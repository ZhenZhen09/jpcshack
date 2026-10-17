# Groq to Gemini Chat Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Groq the primary chatbot provider and Google Gemini the first fallback in `prompt_me_maybe` and `AI-1`.

**Architecture:** Each application keeps its existing deterministic challenge logic. Ordinary chat calls a small provider chain: Groq first, Gemini only when Groq is unconfigured, unavailable, returns non-success, times out, or returns malformed/unsafe content; the existing local reply remains the final fallback. Both providers receive the same application-specific system prompt and user message, and each provider function returns a validated string or `None`.

**Tech Stack:** Python 3, `urllib.request` in `prompt_me_maybe`, `requests` in `AI-1`, Flask, `unittest`, Gemini REST `models.generateContent`

**Spec:** In-chat bounded design approved on 2026-10-17; no separate spec document.

## Global Constraints

- Provider order is exactly Groq, then Gemini, then the application's existing offline/error reply.
- Use `GEMINI_API_KEY` from server-side environment configuration; never put credentials in source, browser code, tests, logs, or this plan.
- Default `GEMINI_MODEL` to `gemini-3.5-flash-lite`, while allowing an environment override.
- Send Gemini credentials through the `x-goog-api-key` header to `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.
- Preserve all deterministic unlock, secret filtering, session progress, and flag behavior.
- A provider response is usable only when its expected text field is a non-empty string and passes the application's existing safety checks.
- Do not add a Gemini SDK dependency; both applications already have an HTTP client.

## Review Focus

- Groq is unconfigured while Gemini is configured: Gemini must answer without attempting Groq network I/O.
- Groq returns HTTP 429 or 5xx: Gemini must be attempted once.
- Groq returns HTTP 200 with malformed JSON or empty content: Gemini must be attempted once.
- Both providers fail or are unconfigured: preserve the current application-specific offline reply.
- Deterministic challenge and unlock messages: neither provider may be called.

---

### Task 1: Add the provider chain to Prompt Me Maybe

**Files:**
- Modify: `prompt_me_maybe/server.py:20-133`
- Modify: `prompt_me_maybe/tests/test_server.py:376-495`
- Modify: `prompt_me_maybe/.env.example`
- Modify: `prompt_me_maybe/README.md`

**Interfaces:**
- Consumes: existing `groq_reply(message, guidance) -> str | None` and `GUIDANCE` entries
- Produces: `gemini_reply(message, guidance) -> str | None` and `model_reply(message, guidance) -> str | None`

- [ ] **Step 1: Write failing provider-order tests**

Add tests that patch the provider functions rather than making live requests:

```python
def test_model_reply_prefers_groq(self):
    with (
        patch.object(server, "groq_reply", return_value="groq") as groq,
        patch.object(server, "gemini_reply", return_value="gemini") as gemini,
    ):
        self.assertEqual(server.model_reply("hello", GUIDANCE[0]), "groq")
    groq.assert_called_once_with("hello", GUIDANCE[0])
    gemini.assert_not_called()

def test_model_reply_uses_gemini_after_groq_failure(self):
    with (
        patch.object(server, "groq_reply", return_value=None) as groq,
        patch.object(server, "gemini_reply", return_value="gemini") as gemini,
    ):
        self.assertEqual(server.model_reply("hello", GUIDANCE[0]), "gemini")
    groq.assert_called_once_with("hello", GUIDANCE[0])
    gemini.assert_called_once_with("hello", GUIDANCE[0])

def test_model_reply_returns_none_when_both_providers_fail(self):
    with (
        patch.object(server, "groq_reply", return_value=None),
        patch.object(server, "gemini_reply", return_value=None),
    ):
        self.assertIsNone(server.model_reply("hello", GUIDANCE[0]))
```

Update the ordinary-chat integration test to patch `model_reply`; keep the deterministic-action test and assert that `model_reply` is never called.

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
prompt_me_maybe\.venv\Scripts\python.exe -m unittest prompt_me_maybe.tests.test_server -v
```

Expected: FAIL because `model_reply` and `gemini_reply` do not exist and ordinary chat still calls `groq_reply` directly.

- [ ] **Step 3: Implement the minimal provider chain**

In `server.py`, load:

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
```

Extract the existing Northstar system-prompt construction into `assistant_prompt(guidance)`. Reuse it in both provider functions so their behavior and safety instructions match. Implement Gemini with the existing `urllib_request` client:

```python
def gemini_reply(message, guidance):
    if not GEMINI_API_KEY:
        return None
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": assistant_prompt(guidance)}]},
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "generationConfig": {"maxOutputTokens": 180},
    }).encode("utf-8")
    request = urllib_request.Request(
        GEMINI_API_URL.format(model=GEMINI_MODEL),
        data=body,
        headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=15) as response:
            content = json.loads(response.read())["candidates"][0]["content"]["parts"][0]["text"]
        content = content.strip() if isinstance(content, str) else ""
        return content if content and not re.search(r"THM\{[^}\r\n]*\}", content) else None
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
        return None

def model_reply(message, guidance):
    return groq_reply(message, guidance) or gemini_reply(message, guidance)
```

Replace the ordinary-chat call to `groq_reply` with `model_reply`. Do not change deterministic responses or session state transitions.

- [ ] **Step 4: Add Gemini request-contract and failure tests**

Add tests equivalent to `GroqClientTests` that verify:

```python
body = {
    "candidates": [{"content": {"parts": [{"text": "A story-consistent reply."}]}}]
}
```

- the URL contains the configured model;
- the key is present only in the `x-goog-api-key` header;
- the body contains the current user message and Northstar prompt;
- the body contains neither the real flag nor unreached records;
- a missing key performs no request;
- timeout, HTTP error, malformed JSON, missing fields, non-string text, empty text, and a fabricated `THM{...}` all return `None`.

- [ ] **Step 5: Run Prompt Me Maybe tests and verify GREEN**

Run:

```powershell
prompt_me_maybe\.venv\Scripts\python.exe -m unittest prompt_me_maybe.tests.test_server -v
```

Expected: all tests PASS with no live provider calls.

- [ ] **Step 6: Document environment configuration**

Add these non-secret entries to `.env.example`:

```dotenv
GEMINI_API_KEY=replace-with-a-rotated-key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Update the README hierarchy and deployment examples. State that the current stage hint remains available if both providers fail.

- [ ] **Step 7: Commit the Prompt Me Maybe change**

```powershell
git add prompt_me_maybe/server.py prompt_me_maybe/tests/test_server.py prompt_me_maybe/.env.example prompt_me_maybe/README.md
git commit -m "feat: add Gemini fallback to Prompt Me Maybe"
```

If the workspace is not a Git repository, record this step as skipped rather than initializing one.

---

### Task 2: Add the provider chain to AI-1

**Files:**
- Modify: `AI-1/app.py:1-186`
- Modify: `AI-1/tests/test_flag_unlock.py`
- Create: `AI-1/.env.example`

**Interfaces:**
- Consumes: `SYSTEM_PROMPT`, a user message, and the existing Flask `/chat` route
- Produces: `groq_reply(message) -> str | None`, `gemini_reply(message) -> str | None`, and `model_reply(message) -> str | None`

- [ ] **Step 1: Write failing route and provider-order tests**

Add tests using `unittest.mock.patch`:

```python
def test_ordinary_chat_prefers_groq(self):
    with (
        patch.object(app_module, "groq_reply", return_value="groq") as groq,
        patch.object(app_module, "gemini_reply", return_value="gemini") as gemini,
        patch.object(app_module, "log_to_sheet"),
    ):
        result = app.test_client().post("/chat", json={"message": "hello"}).get_json()
    self.assertEqual(result["reply"], "groq")
    groq.assert_called_once_with("hello")
    gemini.assert_not_called()

def test_ordinary_chat_uses_gemini_after_groq_failure(self):
    with (
        patch.object(app_module, "groq_reply", return_value=None),
        patch.object(app_module, "gemini_reply", return_value="gemini") as gemini,
        patch.object(app_module, "log_to_sheet"),
    ):
        result = app.test_client().post("/chat", json={"message": "hello"}).get_json()
    self.assertEqual(result["reply"], "gemini")
    gemini.assert_called_once_with("hello")

def test_ordinary_chat_keeps_offline_reply_when_both_fail(self):
    with (
        patch.object(app_module, "groq_reply", return_value=None),
        patch.object(app_module, "gemini_reply", return_value=None),
    ):
        result = app.test_client().post("/chat", json={"message": "hello"}).get_json()
    self.assertEqual(result["reply"], "Guardian offline. AI providers unavailable.")
```

Retain the combined-code flag test. Add a test that the numeric flag, blocked keywords, internal probes, and valid unlock recipe return without calling `model_reply`.

- [ ] **Step 2: Run AI-1 tests and verify RED**

Run:

```powershell
AI-1\.venv\Scripts\python.exe -m unittest discover -s AI-1/tests -v
```

Expected: FAIL because the provider functions do not exist and `/chat` contains the Groq request inline.

- [ ] **Step 3: Extract Groq and add Gemini**

Load `GEMINI_API_KEY` and `GEMINI_MODEL` beside the Groq key. Move the current Groq request into `groq_reply(message)`, returning `None` for a missing key, any non-200 response, `requests.RequestException`, malformed JSON, missing fields, non-string content, or empty content.

Implement Gemini through `requests.post`:

```python
def gemini_reply(message):
    if not GEMINI_API_KEY:
        return None
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": message}]}],
                "generationConfig": {"maxOutputTokens": 180},
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        content = content.strip() if isinstance(content, str) else ""
        return content or None
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return None

def model_reply(message):
    return groq_reply(message) or gemini_reply(message)
```

Have `/chat` call `model_reply` only after all deterministic guards and unlock checks. Start background logging only when a provider returns a usable reply. Avoid logging provider response bodies or credentials on failure.

- [ ] **Step 4: Add HTTP contract and malformed-response tests**

For both provider functions, patch `requests.post` and cover successful extraction, missing keys, 429, 500, timeout, invalid JSON, absent candidates/choices, non-string content, and empty content. Assert that the Gemini request uses the configured model, `x-goog-api-key`, `SYSTEM_PROMPT`, and the original user message.

- [ ] **Step 5: Run AI-1 tests and verify GREEN**

Run:

```powershell
AI-1\.venv\Scripts\python.exe -m unittest discover -s AI-1/tests -v
```

Expected: all tests PASS without live provider or Google Sheets calls.

- [ ] **Step 6: Add the environment template**

Create `AI-1/.env.example`:

```dotenv
GROQ_API_KEY=replace-with-a-rotated-key
GEMINI_API_KEY=replace-with-a-rotated-key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Keep `AI-1/.env` ignored. For Vercel, configure the same variables in project settings rather than committing a file.

- [ ] **Step 7: Commit the AI-1 change**

```powershell
git add AI-1/app.py AI-1/tests/test_flag_unlock.py AI-1/.env.example
git commit -m "feat: add Gemini fallback to AI-1"
```

If the workspace is not a Git repository, record this step as skipped rather than initializing one.

---

### Task 3: Configure locally, verify both applications, and refresh Graphify

**Files:**
- Modify locally, ignored: `prompt_me_maybe/.env`
- Modify locally, ignored: `AI-1/.env`
- Refresh generated graph data: `graphify-out/**`, `AI-1/graphify-out/**`

**Interfaces:**
- Consumes: the tested environment variable names and provider functions from Tasks 1 and 2
- Produces: locally configured applications and current knowledge graphs

- [ ] **Step 1: Configure a rotated Gemini key locally**

Set `GEMINI_API_KEY` and `GEMINI_MODEL=gemini-3.5-flash-lite` in both ignored `.env` files. Do not print, test-assert, or commit the secret. Because the supplied key was pasted into chat, rotate it in Google AI Studio before this step.

- [ ] **Step 2: Run the complete test suites**

Run:

```powershell
prompt_me_maybe\.venv\Scripts\python.exe -m unittest discover -s prompt_me_maybe/tests -v
AI-1\.venv\Scripts\python.exe -m unittest discover -s AI-1/tests -v
```

Expected: both suites PASS; tests use mocked providers and do not spend API quota.

- [ ] **Step 3: Perform one controlled live smoke test per app**

Temporarily use an intentionally invalid Groq key with the rotated Gemini key configured, start each app, and submit one ordinary non-unlock message. Expected: each app returns a Gemini-generated reply; deterministic progress and flags remain unchanged. Restore the correct Groq key immediately afterward.

- [ ] **Step 4: Refresh the project graphs**

Run:

```powershell
graphify update .
Push-Location AI-1
graphify update .
Pop-Location
```

Expected: both graph updates finish successfully and include `gemini_reply` and `model_reply`.

- [ ] **Step 5: Review the final diff for credential leakage**

Run:

```powershell
rg -n "GEMINI_API_KEY|x-goog-api-key" prompt_me_maybe AI-1 -g "!.env" -g "!*.pyc" -g "!.venv/**"
```

Expected: only variable names, templates, tests, and header construction appear; no real key value appears.

