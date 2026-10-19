#!/usr/bin/env python3
"""Shared session-backed API and local static server for self-contained challenges."""

from __future__ import annotations

import importlib.util
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


SOURCE_ROOT = Path(__file__).resolve().parent
WEB_ROOT = Path(os.environ.get("CHALLENGE_WEB_ROOT", str(SOURCE_ROOT))).resolve()
STATE_ROOT = Path(os.environ.get("CHALLENGE_STATE_DIR", str(Path.home() / ".jpcs-ctf-challenges"))).resolve()
STATE_ROOT.mkdir(parents=True, exist_ok=True)
DB_PATH = STATE_ROOT / "sessions.sqlite3"
SESSION_TTL = 48 * 60 * 60
SESSION_COOKIE = "jpcs_challenge_session"
MAX_BODY = 4096
SLUGS = (
    "sekur-julius",
    "base64-cascade",
    "sugar-free-candies",
    "lots-of-passwords",
    "redacted-rsa",
    "ghost-binary",
    "tftp-last-block",
    "dns-breadcrumbs",
    "usb-typist",
    "mailbox-in-transit",
    "logbook-0317",
    "metadata-mosaic",
    "git-aftermath",
    "file-carver",
    "browser-cache-reconstruction",
    "firmware-footnote",
    "packet-split",
    "header-hunt",
    "cookie-crumbs",
    "mock-idor-maze",
    "sql-query-room",
    "redirect-relay",
    "api-contract-trap",
    "tiny-vm",
    "elf-gatekeeper",
    "policy-diff",
    "timeline-drift",
)


def load_challenge(slug: str):
    module_path = SOURCE_ROOT / slug / "challenge.py"
    spec = importlib.util.spec_from_file_location(f"challenge_{slug.replace('-', '_')}", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load challenge handler for {slug}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHALLENGES = {slug: load_challenge(slug) for slug in SLUGS}


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 15000")
    return connection


def initialize_db() -> None:
    connection = connect_db()
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS sessions ("
        "session_id TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at REAL NOT NULL)"
    )
    connection.commit()
    connection.close()


def valid_session_id(value: str) -> bool:
    return len(value) <= 80 and re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None


class ChallengeHandler(BaseHTTPRequestHandler):
    server_version = "JPCSChallenge/1.0"

    def _session_id_from_cookie(self) -> str | None:
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except Exception:
            return None
        morsel = cookie.get(SESSION_COOKIE)
        if morsel is None or not valid_session_id(morsel.value):
            return None
        return morsel.value

    def _load_states(self, create: bool) -> tuple[str | None, dict, sqlite3.Connection]:
        session_id = self._session_id_from_cookie()
        connection = connect_db()
        now = time.time()
        connection.execute("DELETE FROM sessions WHERE updated_at < ?", (now - SESSION_TTL,))
        row = connection.execute(
            "SELECT state_json FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone() if session_id else None
        if row is None and create:
            session_id = secrets.token_urlsafe(32)
        states = json.loads(row["state_json"]) if row else {}
        return session_id, states, connection

    def _save_states(self, connection: sqlite3.Connection, session_id: str, states: dict) -> None:
        connection.execute(
            "INSERT INTO sessions(session_id, state_json, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(session_id) DO UPDATE SET state_json=excluded.state_json, updated_at=excluded.updated_at",
            (session_id, json.dumps(states, separators=(",", ":")), time.time()),
        )
        connection.commit()

    def _json(self, status: int, payload: dict, session_id: str | None = None) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if session_id:
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE}={session_id}; Path=/; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Strict",
            )
        self.end_headers()
        self.wfile.write(body)

    def _page(self, file_path: Path) -> None:
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"} else content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def _public_payload(self, slug: str, state: dict, result: dict | None = None) -> dict:
        payload = {
            "challenge": CHALLENGES[slug].public_state(state),
            "solved": bool(state.get("solved")),
        }
        if state.get("solved"):
            payload["flag"] = state["flag"]
        if result is not None:
            payload["result"] = result
        return payload

    def _api_session(self, slug: str) -> None:
        session_id, states, connection = self._load_states(create=True)
        try:
            if slug not in states:
                states[slug] = CHALLENGES[slug].create_state()
            self._save_states(connection, session_id, states)
            self._json(HTTPStatus.OK, self._public_payload(slug, states[slug]), session_id)
        finally:
            connection.close()

    def _origin_is_same_host(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        return urlsplit(origin).netloc.lower() == self.headers.get("Host", "").lower()

    def _api_submit(self, slug: str) -> None:
        if not self._origin_is_same_host():
            self._json(HTTPStatus.FORBIDDEN, {"error": "Cross-origin submissions are not accepted."})
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "Send the answer as JSON."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                raise ValueError
            submitted = json.loads(self.rfile.read(length))
            if not isinstance(submitted, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "Invalid submission."})
            return

        session_id, states, connection = self._load_states(create=True)
        try:
            state = states.get(slug)
            if state is None:
                state = CHALLENGES[slug].create_state()
            if state.get("solved"):
                result = {"correct": True, "message": "Already solved."}
            else:
                is_correct, message = CHALLENGES[slug].check_answer(state, submitted)
                if is_correct:
                    completion_check = getattr(CHALLENGES[slug], "is_solved", None)
                    state["solved"] = bool(completion_check(state)) if completion_check else True
                result = {"correct": bool(is_correct), "message": message}
            states[slug] = state
            self._save_states(connection, session_id, states)
            self._json(HTTPStatus.OK, self._public_payload(slug, state, result), session_id)
        finally:
            connection.close()

    def do_GET(self) -> None:
        path = unquote(urlsplit(self.path).path)
        if path == "/healthz":
            self._json(HTTPStatus.OK, {"ok": True})
            return
        if path == "/" or path == "/index.html":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "http://127.0.0.1:8080/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        api_match = re.fullmatch(r"/api/challenges/([a-z0-9-]+)/session", path)
        if api_match:
            slug = api_match.group(1)
            if slug not in CHALLENGES:
                self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown challenge."})
                return
            self._api_session(slug)
            return

        asset_path = self._static_path(path)
        if asset_path is not None and asset_path.is_file():
            self._page(asset_path)
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

    def _static_path(self, path: str) -> Path | None:
        path = path.rstrip("/") or "/"
        if path == "/challenges/common.js":
            return WEB_ROOT / "common.js"
        match = re.fullmatch(r"/challenges/([a-z0-9-]+)(?:/(index\.html|app\.js|style\.css|capture\.pcap))?", path)
        if not match or match.group(1) not in CHALLENGES:
            return None
        slug, filename = match.groups()
        filename = filename or "index.html"
        return WEB_ROOT / slug / filename

    def do_POST(self) -> None:
        path = unquote(urlsplit(self.path).path)
        match = re.fullmatch(r"/api/challenges/([a-z0-9-]+)/submit", path)
        if not match or match.group(1) not in CHALLENGES:
            self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        self._api_submit(match.group(1))

    def log_message(self, format: str, *args) -> None:
        print(f"[mini-challenges] {self.address_string()} - {format % args}")


def main() -> None:
    host = os.environ.get("CHALLENGE_BIND", "127.0.0.1")
    port = int(os.environ.get("PORT", "8200"))
    initialize_db()
    server = ThreadingHTTPServer((host, port), ChallengeHandler)
    server.daemon_threads = True
    print(f"Self-contained challenge service listening on {host}:{port}")
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
