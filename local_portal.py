"""Serve the local challenge index and launch only the selected challenge."""

from __future__ import annotations

import html
import os
import socket
import subprocess
import tempfile
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
PORTAL_ROOT = ROOT / "deploy" / "ubuntu"
PORTAL_URL = "http://127.0.0.1:8080/"
STARTUP_TIMEOUT_SECONDS = 180
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

SERVER_CHALLENGES = {
    "ancient-bedrock": (ROOT / "AI-1", 5000),
    "sigma-tech": (ROOT / "Sigma-Tech", 5001),
    "prompt-me-maybe": (ROOT / "prompt_me_maybe", 8000),
    "dolos-lab": (ROOT / "Dolos-Lab", 8100),
    "self-contained-challenges": (ROOT / "challenges", 8200),
}
STATIC_CHALLENGES = {
    slug: ROOT / "challenges" / slug
    for slug in (
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
}
LOG_ROOT = Path(tempfile.gettempdir()) / "jpcs-ctf-portal-logs"


def port_is_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


class ChallengeManager:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._shutdown_requested = threading.Event()
        self._active_slug: str | None = None
        self._active_process: subprocess.Popen | None = None

    def _stop_active_locked(self) -> None:
        process = self._active_process
        self._active_process = None
        self._active_slug = None
        if process is not None:
            self._terminate_process(process)

    def stop_active(self) -> None:
        with self._lock:
            self._stop_active_locked()

    def shutdown(self) -> None:
        self._shutdown_requested.set()
        # Kill without taking the launch lock first, so Ctrl+C interrupts a
        # slow first-time setup instead of waiting for its startup timeout.
        self._stop_active_locked()
        with self._lock:
            self._stop_active_locked()

    def start(self, slug: str) -> int:
        if os.name != "nt":
            raise RuntimeError("The on-demand .bat launcher is for Windows.")

        challenge_dir, port = SERVER_CHALLENGES[slug]
        batch_file = challenge_dir / "run.bat"

        with self._lock:
            if self._shutdown_requested.is_set():
                raise RuntimeError("The local launcher is stopping.")

            if self._active_slug == slug and self._active_process is not None:
                if self._active_process.poll() is None and port_is_open(port):
                    return port
                self._stop_active_locked()
            else:
                self._stop_active_locked()

            if port_is_open(port):
                raise RuntimeError(
                    f"Port {port} is already in use. Stop the older challenge launcher, then retry."
                )

            LOG_ROOT.mkdir(parents=True, exist_ok=True)
            log_path = LOG_ROOT / f"{slug}.log"
            environment = os.environ.copy()
            environment["CTF_LAUNCHED_BY_PORTAL"] = "1"

            with log_path.open("ab") as log_file:
                process = subprocess.Popen(
                    ["cmd.exe", "/d", "/c", "call", str(batch_file)],
                    cwd=challenge_dir,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=NO_WINDOW,
                )

            if self._shutdown_requested.is_set():
                self._terminate_process(process)
                raise RuntimeError("The local launcher is stopping.")

            self._active_slug = slug
            self._active_process = process
            deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS

            while time.monotonic() < deadline:
                if self._shutdown_requested.is_set():
                    self._stop_active_locked()
                    raise RuntimeError("The local launcher is stopping.")
                if process.poll() is not None:
                    self._stop_active_locked()
                    raise RuntimeError(f"The server stopped during startup. See {log_path}")
                if port_is_open(port):
                    return port
                time.sleep(0.25)

            self._stop_active_locked()
            raise RuntimeError(f"The server did not start in time. See {log_path}")

    @staticmethod
    def _terminate_process(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return

        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=6,
                    check=False,
                    creationflags=NO_WINDOW,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
        else:
            process.terminate()

        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)


manager = ChallengeManager()


class PortalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PORTAL_ROOT), **kwargs)

    def translate_path(self, path: str) -> str:
        url_path = urlsplit(path).path
        parts = [unquote(part) for part in url_path.split("/") if part]
        if parts == ["challenges", "common.js"]:
            return str((ROOT / "challenges" / "common.js").resolve())
        if len(parts) >= 2 and parts[0] == "challenges":
            challenge_dir = STATIC_CHALLENGES.get(parts[1])
            if challenge_dir is not None:
                relative_parts = parts[2:]
                if relative_parts not in ([], ["index.html"], ["app.js"], ["style.css"], ["capture.pcap"]):
                    return str(challenge_dir / "__not_found__")
                if any(
                    part in {".", ".."} or any(char in part for char in ("/", "\\", "\x00", ":"))
                    for part in relative_parts
                ):
                    return str(challenge_dir / "__not_found__")
                challenge_root = challenge_dir.resolve()
                target = challenge_root.joinpath(*relative_parts).resolve()
                if not target.is_relative_to(challenge_root):
                    return str(challenge_root / "__not_found__")
                return str(target)
        return super().translate_path(path)

    def _send_message(self, status: int, message: str) -> None:
        body = (
            "<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Challenge launcher</title><body style='font:16px sans-serif;max-width:42rem;margin:4rem auto;padding:0 1rem'>"
            f"<h1>Could not open challenge</h1><p>{html.escape(message)}</p>"
            "<p><a href='/'>Return to the Challenge Index</a></p></body></html>"
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:
        path = unquote(urlsplit(self.path).path).strip("/")

        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "challenges" and parts[1] in STATIC_CHALLENGES:
            self._redirect(f"/open/{parts[1]}")
            return

        if path.startswith("launch/"):
            slug = path.removeprefix("launch/")
            if slug not in SERVER_CHALLENGES:
                self._send_message(404, "Unknown challenge.")
                return
            try:
                port = manager.start(slug)
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                self._send_message(503, str(error))
                return
            self._redirect(f"http://127.0.0.1:{port}/")
            return

        if path.startswith("open/"):
            slug = path.removeprefix("open/")
            target = STATIC_CHALLENGES.get(slug)
            if target is None or not (target / "index.html").is_file():
                self._send_message(404, "Unknown challenge.")
                return
            try:
                port = manager.start("self-contained-challenges")
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                self._send_message(503, str(error))
                return
            self._redirect(f"http://127.0.0.1:{port}/challenges/{slug}/")
            return

        super().do_GET()

    def log_message(self, format: str, *args) -> None:
        print(f"[portal] {self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8080), PortalHandler)
    server.daemon_threads = True
    print(f"Challenge Index: {PORTAL_URL}")
    print("Only the selected server challenge will run. Press Ctrl+C to stop everything.")
    threading.Timer(0.8, webbrowser.open, args=(PORTAL_URL,)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nStopping the active challenge server...")
    finally:
        server.server_close()
        manager.shutdown()
        print("All challenge servers stopped.")


if __name__ == "__main__":
    main()
