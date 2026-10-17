# Prompt Me Maybe Groq Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Groq-powered, story-consistent replies to Prompt Me Maybe without letting the model control puzzle progression or the flag.

**Architecture:** Keep `ChallengeHandler`'s deterministic state machine authoritative. For valid messages that do not trigger a fixed challenge action, ask Groq from the server using only the player's current message and current public stage guidance; use the existing guidance reply when Groq is not configured or fails. Load local configuration from an ignored `.env`; use systemd's environment-file mechanism on Ubuntu.

**Tech Stack:** Python standard-library `urllib` HTTP client; `python-dotenv` only for local `.env` loading; existing `unittest` suite; Groq Chat Completions API.

**Spec:** `docs/superpowers/specs/2026-10-16-prompt-me-maybe-groq-chat-design.md`

## Global Constraints

- Keep the challenge stage transitions, token-count check, and flag reveal deterministic and server-controlled.
- Do not send the flag, future clues, server source, credentials, or chat history to Groq.
- Never expose the Groq key in browser code, HTTP responses, or logs.
- Keep message/request bounds, session isolation, HTTP-only cookies, and text-only chat rendering.
- Do not add conversation history, streaming, a model-selection UI, analytics, or provider failover.
- Groq is optional for local development; missing credentials and provider failure must fall back to stage-aware guidance.

## Review Focus

- Missing `GROQ_API_KEY`: ordinary chat must return deterministic guidance and never call the provider.
- Timeout, non-200 response, malformed JSON, or missing reply field: return guidance without a traceback or secret-bearing diagnostic.
- Prompt-injection text: may be sent only as the current user message; must not alter session phase or disclose future challenge data.
- Correct challenge action: return the fixed clue/flag and skip Groq entirely.
- Tests run on a machine with an operator key in `.env`: the suite must not make live, billable provider calls.

## File Map

- `prompt_me_maybe/server.py` — load local environment settings, call Groq for unmatched messages, retain deterministic state transitions and fallback behavior.
- `prompt_me_maybe/tests/test_server.py` — pin provider and route behavior with mocked HTTP; prevent test traffic from reaching Groq.
- `prompt_me_maybe/requirements.txt` — declare `python-dotenv` for local `.env` loading; HTTP remains standard-library.
- `prompt_me_maybe/.gitignore` — ignore `.env` and the local virtual environment.
- `prompt_me_maybe/.env.example` — safe names/default model and placeholder only; no usable credentials.
- `prompt_me_maybe/run.bat` — create/use a local venv and install requirements on first launch, then start the server.
- `prompt_me_maybe/README.md` — explain local setup, API key rotation/configuration, optional no-key behavior, costs/quota, and revised egress requirements.
- `prompt_me_maybe/prompt-me-maybe.service` — load an operator-managed environment file for the systemd deployment.

### Task 1: Add a bounded Groq client

**Files:**
- Modify: `prompt_me_maybe/server.py`
- Modify: `prompt_me_maybe/tests/test_server.py`
- Create: `prompt_me_maybe/requirements.txt`
- Create: `prompt_me_maybe/.gitignore`
- Create: `prompt_me_maybe/.env.example`

**Interfaces:**
- Add `groq_reply(message, guidance) -> str | None`. It returns model text on a valid provider response, otherwise `None`; it must not mutate session state.
- Read `GROQ_API_KEY` and `GROQ_MODEL` from the environment, defaulting the model to `openai/gpt-oss-20b`.
- Use `urllib.request.Request` and `urllib.request.urlopen` with JSON, bearer auth, a finite timeout, and a bounded completion-token limit.

- [ ] **Step 1: Write failing provider tests**

Add tests that patch `server.GROQ_API_KEY`, `server.GROQ_MODEL`, and `server.urllib.request.urlopen`. Use a context-manager response backed by `io.BytesIO` containing the provider's normal shape:

```python
{"choices": [{"message": {"content": "A story-consistent reply."}}]}
```

Assert that a valid response returns the text and that the outgoing request uses the Groq endpoint, bearer token, configured model, current user message, and current public guidance. Decode the request body and assert it does not contain `FLAG`, future-stage clue text, or the API key. Add separate tests that a missing key skips `urlopen`, and that timeout/`URLError`, HTTP error, invalid JSON, and a missing `choices` reply return `None` without raising.

- [ ] **Step 2: Run provider tests and verify expected failures**

Run: `python -m unittest tests.test_server.GroqClientTests -v` from `prompt_me_maybe`.
Expected: FAIL because `groq_reply` does not exist yet.

- [ ] **Step 3: Implement the minimal provider helper and local config**

Load `.env` with `python-dotenv` near startup. Add `groq_reply` that returns `None` when the key is empty or any provider/parse failure occurs; otherwise construct the chat-completions request with only the assistant persona, current public stage guidance, and the current user message. Use `GROQ_MODEL` or the specified default and a finite timeout. Catch provider and JSON-shape errors without printing request bodies, prompts, keys, or provider response bodies. Add:

```text
# requirements.txt
python-dotenv
```

Add `.env` and `.venv/` to `.gitignore`. Add `.env.example` containing `GROQ_API_KEY=replace-with-a-rotated-key` and `GROQ_MODEL=openai/gpt-oss-20b` only.

- [ ] **Step 4: Run provider tests and verify they pass**

Run: `python -m unittest tests.test_server.GroqClientTests -v`.
Expected: PASS; all HTTP calls are mocked and no real credentials are used.

### Task 2: Integrate the model as a non-authoritative chat fallback

**Files:**
- Modify: `prompt_me_maybe/server.py`
- Modify: `prompt_me_maybe/tests/test_server.py`

**Interfaces:**
- `_reply_for_session(session_id, message)` keeps its current response shape and deterministic checkpoint behavior.
- `groq_reply(message, guidance)` from Task 1 is called only after no deterministic action/replay/checkpoint response applies and only after releasing `SESSION_LOCK`.

- [ ] **Step 1: Write failing route integration tests**

Add tests proving that (a) an unmatched message with a mocked Groq reply returns that reply and leaves `guidance.step` unchanged; (b) recognized sample-record, phrase-slip, policy, count, archive, appendix, and replay requests return their fixed responses without calling Groq; (c) a provider failure falls back to the exact existing stage-aware hint/example; and (d) model text containing an injection attempt does not change phase. Set the module's API key to empty for the legacy suite and only enable it inside tests that mock the provider, so a developer's `.env` can never cause live test traffic.

- [ ] **Step 2: Run integration tests and verify expected failures**

Run: `python -m unittest tests.test_server.GroqFallbackTests -v` from `prompt_me_maybe`.
Expected: FAIL because unmatched requests currently always return deterministic guidance.

- [ ] **Step 3: Integrate Groq outside the session lock**

Preserve every existing deterministic branch and its response unchanged. In the unmatched path, capture the current stage guidance and fallback result while holding `SESSION_LOCK`, release the lock, call `groq_reply`, and replace only the reply text when it returns a string. If it returns `None`, return the original fallback. Do not pass session phase forward based on model output and do not include stored future clue constants or the flag in provider messages.

- [ ] **Step 4: Run integration tests and verify they pass**

Run: `python -m unittest tests.test_server.GroqFallbackTests -v`.
Expected: PASS; fixed challenge actions bypass the provider, unmatched replies use the mocked provider, and failures preserve existing guidance.

### Task 3: Make local launch and deployment configuration safe and clear

**Files:**
- Modify: `prompt_me_maybe/run.bat`
- Modify: `prompt_me_maybe/README.md`
- Modify: `prompt_me_maybe/prompt-me-maybe.service`

- [ ] **Step 1: Add setup checks to the launch instructions**

Update the README with the local sequence: copy `.env.example` to `.env`, replace the placeholder with a newly rotated key (or leave it unset for deterministic-only operation), run `run.bat`, and open the existing local URL. Explain that Groq is called only for unmatched chat turns, the key stays on the server, API quota/latency/cost may apply, and provider failure falls back to local guidance. Add a clear note never to commit `.env` or paste credentials into chat.

- [ ] **Step 2: Configure the Windows launcher and systemd secret source**

Change `run.bat` to create `.venv` and install `requirements.txt` only when the environment is first created, then run `server.py` with that interpreter. Add an optional `EnvironmentFile=-/etc/prompt-me-maybe.env` to the systemd unit. Document creation of that root-owned file with restrictive permissions and group readability for `promptme`; do not copy the local `.env` or any chat-provided key into deployment instructions. Revise the Ubuntu guidance to permit outbound DNS and HTTPS to Groq while retaining the existing inbound-port restrictions and service hardening.

- [ ] **Step 3: Check setup documentation for contradictions**

Search `prompt_me_maybe/README.md` and the service for claims that the app never accesses the internet, needs no API key, or blocks all outbound traffic. Keep only accurate statements: no key is required for deterministic fallback, but Groq chat requires a valid key and outbound access.

### Task 4: Verify full challenge behavior and graph

**Files:**
- Test: `prompt_me_maybe/tests/test_server.py`
- Check: all files listed above

- [ ] **Step 1: Run the full test suite**

Run: `python -m unittest discover -s tests -v` from `prompt_me_maybe`.
Expected: all existing progression/session/security tests and new Groq tests pass; no test makes a live provider request.

- [ ] **Step 2: Smoke-test the local launcher without a key**

Run `run.bat`, GET `/` and `/api/session`, and POST an unmatched chat message. Expected: page and session load, the message returns existing deterministic guidance, and the server remains available. Stop with Ctrl+C.

- [ ] **Step 3: Refresh the project knowledge graph**

Run: `graphify update .` from the website workspace. Expected: graph update completes without errors.

## Implementation Notes

- The workspace currently has no Git repository metadata, so do not include `git add` or commit steps unless the project is later placed in a repository.
- Never copy either key previously pasted into chat into `.env`, tests, examples, shell history, logs, or the spec. The operator must rotate the exposed key and enter a replacement locally.
- The model response is conversational only. The deterministic checkpoint outputs and flag remain the only authoritative solve results.
