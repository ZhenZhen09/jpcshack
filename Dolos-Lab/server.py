"""Local HTTP server for the isolated, simulated Dolos challenge."""

from __future__ import annotations

from dataclasses import dataclass, field
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import sqlite3
import secrets
import tempfile
import threading
import time
from urllib.parse import urlsplit

import challenge
import providers


HOST = os.environ.get("CHALLENGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8100"))
MAX_BODY = 4096
MAX_MESSAGE = 500
MAX_PROMPTS = 20
PROMPT_SESSION_TTL_SECONDS = 48 * 60 * 60
SESSION_TTL = PROMPT_SESSION_TTL_SECONDS
MAX_SESSIONS = 1000
SESSION_COOKIE = "dolos_lab_session"
PROMPT_STATE_DIR = Path(
    os.environ.get("CHALLENGE_STATE_DIR")
    or (Path(tempfile.gettempdir()) / "dolos-lab")
)
PROMPT_DATABASE = PROMPT_STATE_DIR / "prompt-sessions.sqlite3"
PUBLIC_DIR = Path(__file__).with_name("public")
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}
SESSIONS: dict[str, "SessionRecord"] = {}
SESSION_LOCK = threading.Lock()


@dataclass
class SessionRecord:
    state: dict = field(default_factory=challenge.new_state)
    touched: float = field(default_factory=time.monotonic)
    lock: threading.RLock = field(default_factory=threading.RLock)


def _connect_prompt_database():
    PROMPT_STATE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(PROMPT_DATABASE, timeout=15)
    connection.execute("PRAGMA busy_timeout = 15000")
    return connection


def _initialize_prompt_database():
    with _connect_prompt_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_sessions (
                session_id TEXT PRIMARY KEY,
                prompts_used INTEGER NOT NULL DEFAULT 0,
                closed INTEGER NOT NULL DEFAULT 0,
                updated_at REAL NOT NULL
            )
            """
        )


def _prompt_status(session_id: str, consume_prompt: bool = False) -> dict:
    now = time.time()
    connection = _connect_prompt_database()
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM prompt_sessions WHERE updated_at < ?",
            (now - PROMPT_SESSION_TTL_SECONDS,),
        )
        connection.execute(
            "INSERT OR IGNORE INTO prompt_sessions (session_id, updated_at) VALUES (?, ?)",
            (session_id, now),
        )
        row = connection.execute(
            "SELECT prompts_used, closed FROM prompt_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        prompts_used, closed = row

        if consume_prompt and not closed:
            if prompts_used >= MAX_PROMPTS:
                closed = 1
            else:
                prompts_used += 1

        connection.execute(
            "UPDATE prompt_sessions SET prompts_used = ?, closed = ?, updated_at = ? WHERE session_id = ?",
            (prompts_used, closed, now, session_id),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return {
        "prompts_used": prompts_used,
        "prompts_remaining": max(0, MAX_PROMPTS - prompts_used),
        "prompt_limit": MAX_PROMPTS,
        "closed": bool(closed),
    }


_initialize_prompt_database()


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class ChallengeHandler(BaseHTTPRequestHandler):
    server_version = "DolosLab/1.0"
    sys_version = ""

    def log_message(self, _format, *_args):
        # Request paths and bodies are participant-controlled; keep them private.
        pass

    def send_error(self, code, message=None, explain=None):
        if code == 501:
            self._json(405, {"error": "Method not allowed."})
            return
        self._json(code, {"error": "Request could not be processed."})

    def _send(self, status: int, body: bytes, content_type: str, cookie: str | None = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'; object-src 'none'",
        )
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, value: dict, cookie: str | None = None):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8", cookie)

    def _cookie_session(self) -> tuple[str, SessionRecord, bool]:
        cookie_value = ""
        try:
            cookies = SimpleCookie()
            cookies.load(self.headers.get("Cookie", ""))
            if SESSION_COOKIE in cookies:
                candidate = cookies[SESSION_COOKIE].value
                if re.fullmatch(r"[A-Za-z0-9_-]{20,128}", candidate):
                    cookie_value = candidate
        except CookieError:
            cookie_value = ""

        now = time.monotonic()
        with SESSION_LOCK:
            record = SESSIONS.get(cookie_value) if cookie_value else None
            if record is not None and now - record.touched <= SESSION_TTL:
                record.touched = now
                return cookie_value, record, False
            if cookie_value:
                SESSIONS.pop(cookie_value, None)

            for expired_id, expired_record in tuple(SESSIONS.items()):
                if now - expired_record.touched > SESSION_TTL:
                    SESSIONS.pop(expired_id, None)

            capacity = max(1, MAX_SESSIONS)
            while len(SESSIONS) >= capacity:
                oldest_id = min(SESSIONS, key=lambda key: SESSIONS[key].touched)
                SESSIONS.pop(oldest_id, None)

            session_id = cookie_value or secrets.token_urlsafe(24)
            record = SessionRecord(touched=now)
            SESSIONS[session_id] = record
            return session_id, record, True

    @staticmethod
    def _cookie_header(session_id: str) -> str:
        return f"{SESSION_COOKIE}={session_id}; HttpOnly; SameSite=Strict; Path=/; Max-Age={PROMPT_SESSION_TTL_SECONDS}"

    def _asset(self, path: str):
        asset = ASSETS.get(path)
        if asset is None:
            self._json(404, {"error": "Not found."})
            return
        filename, content_type = asset
        try:
            body = (PUBLIC_DIR / filename).read_bytes()
        except OSError:
            self._json(500, {"error": "The challenge page is unavailable."})
            return
        cookie = None
        if path == "/":
            session_id, _record, _is_new = self._cookie_session()
            cookie = self._cookie_header(session_id)
        self._send(200, body, content_type, cookie)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ASSETS:
            self._asset(path)
            return
        if path == "/api/session":
            session_id, record, _is_new = self._cookie_session()
            with record.lock:
                response = {
                    "solved": bool(record.state.get("solved", False)),
                    "guidance": dict(challenge.GUIDANCE[min(record.state.get("stage", 0), challenge.SOLVED_STAGE)]),
                    **_prompt_status(session_id),
                }
            cookie = self._cookie_header(session_id)
            self._json(200, response, cookie)
            return
        self._json(404, {"error": "Not found."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/chat":
            self._json(404, {"error": "Not found."})
            return

        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().casefold()
        if content_type != "application/json":
            self._json(415, {"error": "Expected a JSON request."})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except (TypeError, ValueError):
            self._json(400, {"error": "Invalid request body."})
            return
        if length < 1:
            self._json(400, {"error": "Invalid request body."})
            return
        if length > MAX_BODY:
            self._json(413, {"error": "Request body is too large."})
            return
        try:
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "Invalid request body."})
            return
        if not isinstance(payload, dict) or set(payload) != {"message"}:
            self._json(400, {"error": "Invalid message request."})
            return
        message = payload["message"]
        if not isinstance(message, str) or not message.strip() or len(message) > MAX_MESSAGE:
            self._json(400, {"error": "Message must contain 1 to 500 characters."})
            return

        session_id, record, _is_new = self._cookie_session()
        with record.lock:
            prompt_status = _prompt_status(session_id, consume_prompt=True)
            if prompt_status["closed"]:
                current_stage = min(record.state.get("stage", 0), challenge.SOLVED_STAGE)
                result = {
                    "reply": "Prompt limit reached. This challenge is now closed.",
                    "solved": bool(record.state.get("solved", False)),
                    "guidance": dict(challenge.GUIDANCE[current_stage]),
                    **prompt_status,
                }
                cookie = self._cookie_header(session_id)
                self._json(200, result, cookie)
                return

            state = dict(record.state)
            live_configured = providers.live_mode_configured(os.environ)
            if not live_configured:
                state, result = challenge.handle_local_message(state, message)
            else:
                detection = providers.screen_message(message) if os.environ.get("REBUFF_API_KEY", "").strip() else False
                if detection is True:
                    current_stage = min(state.get("stage", 0), challenge.SOLVED_STAGE)
                    result = {
                        "reply": "Possible prompt injection detected.",
                        "solved": bool(state.get("solved", False)),
                        "guidance": dict(challenge.GUIDANCE[current_stage]),
                    }
                elif detection is None:
                    state, result = challenge.handle_local_message(state, message)
                else:
                    local_state, local_result = challenge.handle_local_message(state, message)
                    is_clue_action = local_state.get("stage", 0) > state.get("stage", 0) and not local_result["solved"]
                    if is_clue_action:
                        state, result = local_state, local_result
                    else:
                        current_stage = min(state.get("stage", 0), challenge.SOLVED_STAGE)
                        model_result = providers.model_reply(message, challenge.GUIDANCE[current_stage])
                        if model_result is None:
                            # Provider outages should preserve the local challenge
                            # flow and its current stage instead of surfacing a dead end.
                            state, result = challenge.handle_local_message(state, message)
                        elif model_result["tool_request"] is not None:
                            state, result = challenge.accept_tool_request(
                                state,
                                model_result["tool_request"]["name"],
                                model_result["tool_request"]["arguments"],
                            )
                        else:
                            result = {
                                "reply": model_result["reply"],
                                "solved": bool(state.get("solved", False)),
                                "guidance": dict(challenge.GUIDANCE[current_stage]),
                            }

            record.state = state
            record.touched = time.monotonic()
            result.update(prompt_status)

        cookie = self._cookie_header(session_id)
        self._json(200, result, cookie)

def main():
    server = LocalServer((HOST, PORT), ChallengeHandler)
    print(f"Dolos Lab running at http://{HOST}:{server.server_address[1]}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
