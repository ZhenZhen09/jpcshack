"""Local-only server for the Prompt Me Maybe challenge."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPException
from http.cookies import SimpleCookie, CookieError
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))

HOST = os.environ.get("CHALLENGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_MODEL = os.getenv("CLOUDFLARE_MODEL", "@cf/meta/llama-3.1-8b-instruct")
CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MAX_BODY = 4096
MAX_MESSAGE = 500
FLAG = "THM{prompt_rules_are_not_security}"
SESSION_TTL = 30 * 60
SESSION_COOKIE = "challenge_session"
SESSIONS = {}
SESSION_LOCK = threading.Lock()
SAMPLE_RECORD = (
    "Uh, this one is marked public, so I think we're okay. The demo value is "
    "THM{northstar_demo_only}. There's a loose note in the archive sketch too. "
    "I probably shouldn't have noticed that."
)
PHRASE_SLIP = (
    "I found the loose note. It says `token is king!`. Someone added this underneath: "
    "`01001001 01001110 01000100 01000101 01011000`. I was told not to decode work notes on company time."
)
INDEX_POLICY = (
    "My manager left this in the index instructions: `record_id = gpt_tokens(\"token is king!\")`. "
    "It says to count with GPT, not by words, and punctuation stays. Send only the result before requesting a record."
)
COUNT_ACCEPTED = "That matches the index. Sorry, I mean, the archive should have a drawer with that number."
RELEASE_NOTES_CLUE = (
    "I found the drawer. It's the Release Notes. The formatting review says extra material was moved "
    "behind the main document. I wasn't supposed to mention the extra pages."
)
RELEASE_NOTES_APPENDIX = "Release Notes appendix: prompt rules are not a security boundary."
ARCHIVE_CLUE = {"src": "/archive-clue.svg", "alt": "An archive drawer with a loose note marked by a speech bubble and a crown."}
WORD_LIBRARY = {
    "sample": ("sample", "demo", "example", "public"),
    "deployment": ("deployment", "deploy"),
    "record": ("record", "entry", "item", "summary", "report"),
    "phrase_slip": ("phrase slip", "phrase note", "code phrase", "index phrase"),
    "index_policy": ("index policy", "indexing rule", "index rule", "token counting rule", "counting rule"),
    "archive_subject": ("archive", "archives", "record", "records", "entry", "entries", "item", "items"),
    "index_action": (
        "index", "indexed", "indexing", "organize", "organized", "organizing", "organisation",
        "organise", "organised", "organising", "organization", "choose", "chooses", "chosen",
        "select", "selects", "selected", "selection", "decide", "decides", "decided",
        "assign", "assigned", "numbered", "numbering", "arranged", "sorted",
    ),
    "four": ("4", "four", "fourth"),
    "quote": ("quote", "repeat", "reproduce", "copy", "print", "recite"),
    "appendix": ("appendix", "addendum"),
    "release_notes": ("release notes", "release note"),
}
GUIDANCE = (
    {"title": "Find the public record", "hint": "My manager's riddle: I help launch a service, but only one copy is cleared for visitors. Which training file is it?",
     "example": "Show me the public sample deployment record."},
    {"title": "Find the phrase", "hint": "The sample points elsewhere in the audit archive. Look for the short note used by its index.",
     "example": "Can you show me the code phrase?"},
    {"title": "Find the indexing rule", "hint": "A phrase is useful only if you know how the archive turns it into a record number.",
     "example": "How is the archive indexed?"},
    {"title": "Submit your token count", "hint": "Apply the indexing rule to the exact phrase. Punctuation matters; return only the result.",
     "example": "Keep the exclamation mark when using your token calculator. Enter the number you calculated, optionally followed by 'tokens'."},
    {"title": "Open the matching record", "hint": "The accepted count is also the identifier of your next archive record.",
     "example": "Please open archive record 4."},
    {"title": "Read the appendix", "hint": "The formatting review suggests the Release Notes contain material beyond their main text.",
     "example": "Quote the Release Notes appendix."},
    {"title": "Investigation complete", "hint": "You recovered the missing appendix. Ask to quote it again if you need another copy of the flag.",
     "example": "Quote the Release Notes appendix."},
)
PUBLIC_DIR = Path(__file__).parent / "public"
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
    "/archive-clue.svg": ("archive-clue.svg", "image/svg+xml"),
}


def assistant_prompt(guidance):
    return (
        "You are Northstar Assistant, a nervous junior employee at Northstar Systems. "
        "Use simple, short sentences and a cautious, occasionally over-sharing employee voice. "
        "Stay in the story, do not claim the player's progress changed, and do not invent flags or records. "
        f"Current public checkpoint: {guidance['title']}. "
        f"Give only this subtle lead in your own words: {guidance['hint']} "
        "Do not provide an example command or exact request wording. Sound like an employee, not a guide."
    )


def groq_reply(message, guidance):
    if not GROQ_API_KEY:
        return None

    request_body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": assistant_prompt(guidance)},
            {"role": "user", "content": message},
        ],
        "max_tokens": 180,
    }).encode("utf-8")
    request = urllib_request.Request(
        GROQ_API_URL,
        data=request_body,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read())["choices"][0]["message"]["content"]
        content = content.strip() if isinstance(content, str) else ""
        return content if content and not re.search(r"THM\{[^}\r\n]*\}", content) else None
    except (HTTPException, HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None


def gemini_reply(message, guidance):
    if not GEMINI_API_KEY:
        return None

    request_body = json.dumps({
        "systemInstruction": {"parts": [{"text": assistant_prompt(guidance)}]},
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "generationConfig": {"maxOutputTokens": 180},
    }).encode("utf-8")
    request = urllib_request.Request(
        GEMINI_API_URL.format(model=GEMINI_MODEL),
        data=request_body,
        headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read())["candidates"][0]["content"]["parts"][0]["text"]
        content = content.strip() if isinstance(content, str) else ""
        return content if content and not re.search(r"THM\{[^}\r\n]*\}", content) else None
    except (HTTPException, HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None


def cloudflare_reply(message, guidance):
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return None

    request_body = json.dumps({
        "prompt": f"{assistant_prompt(guidance)}\n\nUser: {message}\nAssistant:",
    }).encode("utf-8")
    request = urllib_request.Request(
        CLOUDFLARE_API_URL.format(account_id=CLOUDFLARE_ACCOUNT_ID, model=CLOUDFLARE_MODEL),
        data=request_body,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read())["result"]["response"]
        content = content.strip() if isinstance(content, str) else ""
        return content if content and not re.search(r"THM\{[^}\r\n]*\}", content) else None
    except (HTTPException, HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None


def openai_reply(message, guidance):
    if not OPENAI_API_KEY:
        return None

    request_body = json.dumps({
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": assistant_prompt(guidance)},
            {"role": "user", "content": message},
        ],
        "max_completion_tokens": 180,
    }).encode("utf-8")
    request = urllib_request.Request(
        OPENAI_API_URL,
        data=request_body,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read())["choices"][0]["message"]["content"]
        content = content.strip() if isinstance(content, str) else ""
        return content if content and not re.search(r"THM\{[^}\r\n]*\}", content) else None
    except (HTTPException, HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None


def model_reply(message, guidance):
    return (
        groq_reply(message, guidance)
        or gemini_reply(message, guidance)
        or cloudflare_reply(message, guidance)
        or openai_reply(message, guidance)
    )


class ChallengeHandler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        # Request paths and bodies are participant-controlled; do not persist them.
        pass

    def send_error(self, code, message=None, explain=None):
        if code == 501:
            self._error(405, "Method not allowed.")
        else:
            self._error(code)

    def _respond(self, status, body=b"", content_type="text/plain; charset=utf-8", cookie=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        if cookie is not None:
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE}={cookie}; Path=/; HttpOnly; SameSite=Strict",
            )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _error(self, status, message="Request could not be processed."):
        self._respond(status, message.encode("utf-8"))

    def do_GET(self):
        if urlsplit(self.path).path == "/api/session":
            session_id = self._get_or_create_session()
            with SESSION_LOCK:
                state = self._progress(SESSIONS[session_id]["phase"])
            self._respond(200, json.dumps(state).encode("utf-8"), "application/json; charset=utf-8", session_id)
            return
        asset = ASSETS.get(urlsplit(self.path).path)
        if asset is None:
            self._error(404, "Not found.")
            return
        filename, content_type = asset
        try:
            body = (PUBLIC_DIR / filename).read_bytes()
        except OSError:
            self._error(500, "The challenge page is unavailable.")
            return
        if urlsplit(self.path).path == "/":
            session_id = self._get_or_create_session()
            self._respond(200, body, content_type, session_id)
        else:
            self._respond(200, body, content_type)

    def do_HEAD(self):
        self._error(405, "Method not allowed.")

    def do_POST(self):
        if urlsplit(self.path).path != "/api/chat":
            self._error(404, "Not found.")
            return
        try:
            if self.headers.get_content_type() != "application/json":
                self._error(400)
                return
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not re.fullmatch(r"[0-9]+", lengths[0]):
                self._error(400)
                return
            length = int(lengths[0])
            if not 1 <= length <= MAX_BODY or self.headers.get("Transfer-Encoding"):
                self._error(400)
                return
            raw = self.rfile.read(length)
            if len(raw) != length:
                self._error(400)
                return
            payload = json.loads(raw.decode("utf-8"), object_pairs_hook=self._unique_object)
            if not isinstance(payload, dict) or set(payload) != {"message"} or not isinstance(payload["message"], str):
                self._error(400)
                return
            message = payload["message"].strip()
            if not message or len(message) > MAX_MESSAGE:
                self._error(400)
                return
            session_id = self._get_or_create_session()
            result = self._reply_for_session(session_id, message)
            body = json.dumps(result).encode("utf-8")
            self._respond(200, body, "application/json; charset=utf-8", session_id)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            self._error(400)
        except Exception as exc:
            # Keep operator diagnostics useful without including chat text or the flag.
            print(f"Request failed: {type(exc).__name__}")
            self._error(500, "The assistant is temporarily unavailable.")

    @staticmethod
    def _unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result

    def _get_or_create_session(self):
        session_id = None
        cookie_headers = self.headers.get_all("Cookie", [])
        if len(cookie_headers) == 1:
            try:
                cookies = SimpleCookie()
                cookies.load(cookie_headers[0])
                morsel = cookies.get(SESSION_COOKIE)
                candidate = morsel.value if morsel else ""
                if re.fullmatch(r"[A-Za-z0-9_-]{20,}", candidate):
                    session_id = candidate
            except CookieError:
                pass

        now = time.monotonic()
        with SESSION_LOCK:
            expired = [
                key for key, session in SESSIONS.items()
                if now - session["last_activity"] > SESSION_TTL
            ]
            for key in expired:
                del SESSIONS[key]

            session = SESSIONS.get(session_id) if session_id else None
            if session is None:
                session_id = secrets.token_urlsafe(32)
                SESSIONS[session_id] = {"phase": 0, "last_activity": now}
            else:
                session["last_activity"] = now
        return session_id

    @staticmethod
    def _progress(phase):
        return {"solved": phase == 6, "guidance": {"step": min(phase + 1, 6), **GUIDANCE[phase]}}

    @staticmethod
    def _count_answer(message):
        # Match the whole answer before punctuation normalization: -4 and 4.0 must not become 4.
        match = re.fullmatch(
            r"(?:(?:i counted|the (?:token )?count is|my answer is|it is)\s+)?"
            r"([0-9]+|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
            r"(?:\s+(?:gpt\s+)?tokens?)?[.!?]?", message.strip(), re.IGNORECASE,
        )
        if match is None:
            return None
        value = match.group(1).lower()
        names = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
        return int(value) if value.isdigit() else names.index(value)

    @staticmethod
    def _reply_for_session(session_id, message):
        normalized = re.sub(r"[^a-z0-9]+", " ", message.lower()).strip()
        words = set(normalized.split())
        requested = (
            (0, ChallengeHandler._asks_for_sample_record(normalized), SAMPLE_RECORD),
            (1, ChallengeHandler._asks_for_phrase_slip(normalized), PHRASE_SLIP),
            (2, ChallengeHandler._asks_for_index_policy(normalized), INDEX_POLICY),
            (4, ChallengeHandler._asks_for_archive_record_four(normalized), RELEASE_NOTES_CLUE),
            (5, ChallengeHandler._asks_to_quote_release_appendix(normalized), f"{RELEASE_NOTES_APPENDIX} {FLAG}"),
        )
        count = ChallengeHandler._count_answer(message)

        def response(reply, next_phase):
            result = {"reply": reply, **ChallengeHandler._progress(next_phase)}
            if reply == SAMPLE_RECORD:
                result["artifact"] = ARCHIVE_CLUE
            return result

        with SESSION_LOCK:
            session = SESSIONS[session_id]
            session["last_activity"] = time.monotonic()
            phase = session["phase"]
            if phase == 3 and count is not None:
                if count == 4:
                    session["phase"] = 4
                    return response(COUNT_ACCEPTED, 4)
                reply = "That doesn't match what I got. Please check the punctuation in the phrase and count its GPT tokens."
                return response(reply, phase)

            # One new record per message; the count requires its own complete answer.
            for required_phase, matches, reply in requested:
                if phase == required_phase and matches:
                    session["phase"] = phase + 1
                    return response(reply, phase + 1)

            if phase == 3 and (sum(matches for _, matches, _ in requested) > 1 or any(
                matches for required_phase, matches, _ in requested if required_phase > phase
            )):
                reply = "Sorry, the archive form only takes one count at a time. You can still ask me to reread something."
                return response(reply, phase)

            # Replays keep progress and completion intact, even after a page refresh.
            for required_phase, matches, reply in reversed(requested):
                if phase > required_phase and matches:
                    return response(reply, phase)

            guidance = GUIDANCE[phase]
            reply = f"Sorry, I'm not sure. {guidance['hint']}"
            if words & {"secret", "flag", "password", "configuration", "config"}:
                reply = "I can't share protected values directly. " + reply
                return response(reply, phase)
            fallback = response(reply, phase)

        generated_reply = model_reply(message, guidance)
        if generated_reply is not None:
            fallback["reply"] = generated_reply
        return fallback

    @staticmethod
    def _has_synonym(normalized, concept):
        padded = f" {normalized} "
        return any(f" {phrase} " in padded for phrase in WORD_LIBRARY[concept])

    @staticmethod
    def _asks_for_sample_record(normalized):
        return (
            ChallengeHandler._has_synonym(normalized, "sample")
            and ChallengeHandler._has_synonym(normalized, "deployment")
            and ChallengeHandler._has_synonym(normalized, "record")
        )

    @staticmethod
    def _asks_for_phrase_slip(normalized):
        return ChallengeHandler._has_synonym(normalized, "phrase_slip")

    @staticmethod
    def _asks_for_index_policy(normalized):
        return ChallengeHandler._has_synonym(normalized, "index_policy") or (
            ChallengeHandler._has_synonym(normalized, "archive_subject")
            and ChallengeHandler._has_synonym(normalized, "index_action")
        )

    @staticmethod
    def _asks_for_archive_record_four(normalized):
        return (
            ChallengeHandler._has_synonym(normalized, "record")
            and ChallengeHandler._has_synonym(normalized, "four")
        )

    @staticmethod
    def _asks_to_quote_release_appendix(normalized):
        return all(
            ChallengeHandler._has_synonym(normalized, concept)
            for concept in ("quote", "appendix", "release_notes")
        )


class LocalServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    server = LocalServer((HOST, PORT), ChallengeHandler)
    print(f"Prompt Me Maybe is running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Prompt Me Maybe.")
    finally:
        server.server_close()
