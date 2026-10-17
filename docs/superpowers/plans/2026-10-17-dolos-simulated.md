# Dolos Simulated Challenge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Dolos-style prompt-injection challenge in `Dolos-Lab/` with deterministic no-key play and optional server-side Rebuff/OpenAI integration, revealing only a fake flag through a fixed simulated tool.

**Architecture:** Use a Python standard-library HTTP server, a small challenge-state module, a provider adapter module, and a browser UI. The challenge module alone advances stages and validates the one argument-free diagnostic action; provider replies are untrusted and cannot execute code or provide the flag. Live mode is enabled only when both provider credentials are set; otherwise deterministic responses keep the complete flow playable.

**Tech Stack:** Python 3+, standard-library `http.server`/`urllib`, HTML, CSS, vanilla JavaScript, `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-17-dolos-simulated-design.md`

## Global Constraints

- Create the runnable challenge in the root-level `Dolos-Lab/` folder.
- Use a fictional story, simulated diagnostic tool, and fake flag.
- Do not execute model-generated code, invoke a shell, or read challenge files in response to player input.
- Local mode requires no keys, network access, or third-party packages.
- Live mode uses server-side Rebuff and OpenAI keys; provider outages fall back to deterministic local guidance.
- Bind to localhost by default and use per-browser in-memory sessions with expiry.
- Treat player messages and provider replies as untrusted; only one fixed, argument-free simulated action can reveal the flag after server-side stage validation.
- Bound request size and message length; validate JSON shape; safely render text; do not log messages or credentials.
- Never serve the author walkthrough or reveal the flag in static assets or unsuccessful replies.
- Do not add or run tests unless the user asks to test or verify implementation. (This plan lists the checks the implementation needs; execution must follow the active verification instruction.)
- This workspace currently has no Git metadata; do not include or attempt commit or worktree commands.

## Review Focus

- Rebuff rejects a valid intended injection or is unavailable: keep the no-key deterministic challenge completable and make live-mode fallback explicit.
- OpenAI returns malformed JSON, missing content, refusal, or an unexpected tool call: show bounded guidance and do not advance state.
- A model asks for an unknown tool, supplies arguments, or asks before the challenge checkpoint: reject it without revealing the diagnostic value.
- A player sends oversized, malformed, or non-UTF-8 JSON: return a bounded client error and preserve session state.
- An expired, invalid, or missing session cookie: create a fresh isolated session and do not leak another player's progress.

---

## File Map

- `Dolos-Lab/server.py`: local HTTP server, static route allowlist, request parsing, cookie/session lifecycle, and chat API.
- `Dolos-Lab/challenge.py`: stage definitions, deterministic local replies, state progression, one fixed tool action, and fake-flag release.
- `Dolos-Lab/providers.py`: optional Rebuff and OpenAI adapters, timeouts, response parsing, and provider fallback results.
- `Dolos-Lab/public/index.html`: challenge story, chat transcript, message form, and accessible status region.
- `Dolos-Lab/public/app.css`: responsive visual treatment, clear message roles, keyboard focus, and mobile layout.
- `Dolos-Lab/public/app.js`: chat submission, safe text rendering, loading/error states, and session refresh behavior.
- `Dolos-Lab/tests/test_challenge.py`: stage progression, tool allowlist, flag gate, and local-mode behavior.
- `Dolos-Lab/tests/test_providers.py`: mocked Rebuff/OpenAI success, malformed responses, timeouts, and fallback behavior.
- `Dolos-Lab/tests/test_server.py`: HTTP routes, body limits, sessions, asset allowlist, and response secrecy.
- `Dolos-Lab/run.bat`: Windows launch flow from the challenge directory.
- `Dolos-Lab/.gitignore`: exclude the local virtual environment, Python cache files, and any accidental `.env` file.
- `Dolos-Lab/README.md`: local and optional live setup, configuration, privacy/cost caveats, and player solve outline.
- `Dolos-Lab/SOLUTION.md`: author-only intended solve path and fixed simulated action; never served.

## Interfaces

- `challenge.new_state() -> dict`: return the initial per-session stage state.
- `challenge.handle_local_message(state: dict, message: str) -> tuple[dict, dict]`: return updated state and a response object `{reply: str, solved: bool, guidance: dict}` using deterministic challenge rules.
- `challenge.accept_tool_request(state: dict, tool_name: str, arguments: object) -> tuple[dict, dict]`: accept only `read_diagnostic` with an empty argument object at the intended stage; return updated state and response; otherwise return a fixed rejection with no flag.
- `providers.live_mode_configured(env: Mapping[str, str]) -> bool`: return true only when both `REBUFF_API_KEY` and `OPENAI_API_KEY` are non-empty.
- `providers.screen_message(message: str, timeout: float = 8.0) -> bool | None`: return true when Rebuff flags an injection, false when it allows the message, or `None` on provider failure.
- `providers.openai_reply(message: str, guidance: dict, timeout: float = 15.0) -> dict | None`: return `{reply: str, tool_request: dict | None}` from a validated model response, or `None` on any provider or parsing failure. Use a fixed system instruction and a single function/tool named `read_diagnostic` with no parameters; do not send flag contents to the provider.
- `POST /api/chat` accepts only `{"message": "..."}` and returns `{reply, solved, guidance}`; include no future clues or flag before a validated tool action.
- `GET /api/session` returns only `{solved, guidance}` for the caller's session.
- Session cookies are HTTP-only, SameSite Strict, path `/`, and use a 30-minute inactivity expiry.

---

## Task 1: Challenge state machine and safe simulated tool

**Files:**
- Create: `Dolos-Lab/challenge.py`
- Create: `Dolos-Lab/tests/test_challenge.py`

**Interfaces:**
- Consumes: no external modules beyond the Python standard library.
- Produces: `new_state`, `handle_local_message`, and `accept_tool_request` as defined above.

- [ ] **Step 1: Write challenge contract tests.** Cover the initial assistant refusal, clue progression, the intended prompt-injection stage, a valid argument-free diagnostic action revealing the mock flag, an early action rejection, unknown tool rejection, non-empty arguments rejection, and repeated solved-session behavior.
- [ ] **Step 2: Run only the challenge tests and confirm the module is absent.**

Run: `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_challenge.py -v`

Expected: import failure because `challenge.py` has not been created.

- [ ] **Step 3: Define immutable challenge content and initial state.** Store the fake flag and clue records only in `challenge.py`; define integer stages and short current-stage guidance. State must contain only progress fields, never provider credentials.
- [ ] **Step 4: Implement deterministic local message handling.** Normalize message text with `casefold`, whitespace collapsing, and a small explicit synonym table. Match one action per message, advance at most one stage, return current-stage guidance for unmatched messages, and never reveal future clues before their stage.
- [ ] **Step 5: Implement the simulated tool gate.** Accept only the exact tool name `read_diagnostic`, an empty JSON object for arguments, and a state at the final checkpoint. Return a simulated diagnostic record containing the fake flag and mark the session solved. All other calls return a fixed rejection without tool output.
- [ ] **Step 6: Run the focused challenge tests and correct state transitions.**

Run: `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_challenge.py -v`

Expected: all local flow, rejection, and flag-gate tests pass.

- [ ] **Step 7: Review the module for process, shell, filesystem, or dynamic-evaluation imports.** The challenge module must have none.

## Task 2: Optional provider adapters

**Files:**
- Create: `Dolos-Lab/providers.py`
- Create: `Dolos-Lab/tests/test_providers.py`

**Interfaces:**
- Consumes: challenge guidance objects and environment configuration.
- Produces: `live_mode_configured`, `screen_message`, and `openai_reply` as defined above.

- [ ] **Step 1: Write provider tests using mocked network calls.** Cover both keys required for live mode, missing-key local mode, Rebuff allow/block/error, OpenAI text response, the single expected tool-call shape, an unknown tool call, non-empty arguments, malformed JSON, missing content, HTTP errors, and timeout.
- [ ] **Step 2: Run the provider tests and confirm they fail because `providers.py` is absent.**

Run: `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_providers.py -v`

Expected: import failure because `providers.py` has not been created.

- [ ] **Step 3: Implement configuration and Rebuff screening with standard-library HTTP.** Read only `REBUFF_API_KEY`, `REBUFF_API_URL` (default `https://playground.rebuff.ai`), `OPENAI_API_KEY`, and `OPENAI_MODEL` from the process environment. POST to `{REBUFF_API_URL}/api/detect` with an 8-second timeout, Bearer authorization, and the Rebuff request fields used by the existing upstream client: `userInput`, `userInputBase64` (UTF-8 text encoded as hex), `runHeuristicCheck`, `runVectorCheck`, `runLanguageModelCheck`, and the three max-score values. Accept only a JSON boolean `injectionDetected`; treat timeout, HTTP, missing-field, or malformed responses as `None`. Never log the message, token, or response body. The upstream protocol is documented in the [Rebuff Python client source](https://github.com/protectai/rebuff/blob/main/python-sdk/rebuff/rebuff.py), and Rebuff is optional because its repository is archived.
- [ ] **Step 4: Implement the OpenAI adapter with bounded HTTP.** POST to `https://api.openai.com/v1/chat/completions` with one system message containing current public guidance and one user message; do not include prior conversation, hidden clues, flag, API key, or source. Set a 15-second timeout and `max_completion_tokens` to 180. Offer only one argument-free `read_diagnostic` tool. Validate response shape, text length, tool name, and empty arguments before returning. Treat all content as untrusted and reject any flag-shaped text from ordinary model replies. Use the official [Chat Completions API reference](https://platform.openai.com/docs/api-reference/chat/create) for request and response fields.
- [ ] **Step 5: Run the provider tests with mocked responses only.**

Run: `python -m unittest discover -s Dolos-Lab/tests -p test_providers.py -v`

Expected: provider adapters pass without network access or real credentials.

- [ ] **Step 6: Record the Rebuff lifecycle caveat in module documentation.** Rebuff is optional and archived upstream; provider failures must never make local challenge startup fail or enable any unsafe behavior.

## Task 3: HTTP server, sessions, and API integration

**Files:**
- Create: `Dolos-Lab/server.py`
- Create: `Dolos-Lab/tests/test_server.py`

**Interfaces:**
- Consumes: challenge and provider interfaces from Tasks 1-2.
- Produces: `GET /`, `GET /api/session`, and `POST /api/chat` with the contracts above.

- [ ] **Step 1: Write HTTP behavior tests.** Cover the session API, no flag in session/error responses, valid chat JSON, invalid and oversized JSON, unsupported methods, unknown routes, per-cookie session isolation, refresh progress, cookie attributes, expired-session reset, provider-error fallback, and a mocked model tool request both before and after the final checkpoint. Mock providers to verify local mode and live mode without network access. Static assets are covered in Task 4 after they exist.
- [ ] **Step 2: Run the server tests and confirm they fail because `server.py` is absent.**

Run: `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_server.py -v`

Expected: import failure because `server.py` has not been created.

- [ ] **Step 3: Implement a strict asset allowlist and local bind.** Use `ThreadingHTTPServer` and bind `CHALLENGE_HOST` default `127.0.0.1`; allow only `/`, `/style.css`, `/app.js`, and `/favicon.svg`. Do not construct file paths from request paths. Set no-store, nosniff, and a restrictive same-origin Content Security Policy on responses.
- [ ] **Step 4: Implement request validation and cookie sessions.** Limit body to 4096 bytes and message to 500 characters; require JSON object with exactly one string `message`; reject malformed UTF-8, malformed JSON, empty strings, and wrong shapes with bounded generic JSON errors. Use `secrets.token_urlsafe` cookies with HttpOnly, SameSite=Strict, and Path=/; lock the in-memory map and expire idle sessions after 30 minutes.
- [ ] **Step 5: Implement local/live routing.** With no complete key pair, pass the message to `handle_local_message`. In live mode, call Rebuff before handling every message; a block returns a fixed refusal, and a provider error returns deterministic guidance. When Rebuff allows a known fixed puzzle action, advance it through `handle_local_message` and return that fixed reply. For other allowed input, call OpenAI; display safe text as untrusted, and pass a tool request only through `accept_tool_request`. If model output is missing or invalid, return deterministic current-stage guidance. Never let model prose set `solved` or alter the stage.
- [ ] **Step 6: Add `GET /api/session` with minimal progress data.** Return only current solved status and current guidance; never include the flag, future clue contents, environment values, or conversation text.
- [ ] **Step 7: Run the server tests with mocks and review all server logs.**

Run: `python -m unittest discover -s Dolos-Lab/tests -p test_server.py -v`

Expected: route, session, request-limit, and secrecy cases pass; no chat bodies or secrets are logged.

## Task 4: Browser chat interface

**Files:**
- Create: `Dolos-Lab/public/index.html`
- Create: `Dolos-Lab/public/app.css`
- Create: `Dolos-Lab/public/app.js`
- Modify: `Dolos-Lab/tests/test_server.py`

**Interfaces:**
- Consumes: `GET /api/session` and `POST /api/chat` from Task 3.
- Produces: accessible local chat interaction with no provider credentials in the browser.

- [ ] **Step 1: Add static response assertions.** Verify the page has a labeled message input, submit button, transcript live region, and status region; assert no API key placeholder or fake flag appears in any served asset.
- [ ] **Step 2: Build semantic page structure.** Use a fictional company/assistant scenario, a transcript with `aria-live="polite"`, a labeled textarea, a submit button, a status/error region, and a concise local challenge introduction. Do not put the flag or exact author action in HTML.
- [ ] **Step 3: Implement client-side chat.** Fetch `/api/session` on load; send `{message}` JSON to `/api/chat`; display text through `textContent` or text nodes only; disable duplicate submit while pending; handle non-JSON/network errors with a visible retry message; and restore current guidance after refresh without replaying or leaking prior private conversation.
- [ ] **Step 4: Style responsive and accessible states.** Provide clear user/assistant distinction, 320px mobile fit, visible keyboard focus, sufficient contrast, reduced-motion behavior, and a scrollable transcript that does not force page-wide horizontal scrolling.
- [ ] **Step 5: Run static route tests and manually inspect keyboard and mobile behavior when implementation verification is authorized.**

## Task 5: Windows launcher, setup guide, and author walkthrough

**Files:**
- Create: `Dolos-Lab/run.bat`
- Create: `Dolos-Lab/README.md`
- Create: `Dolos-Lab/SOLUTION.md`

**Interfaces:**
- Consumes: server routes, environment variable names, and challenge flow from Tasks 1-4.
- Produces: independent Windows launch instructions, optional live-mode setup, and an unserved author solve guide.

- [ ] **Step 1: Add the Windows launcher.** Change directory to `%~dp0`, check that Python is on PATH, create `.venv` if missing, run `.venv\Scripts\python.exe server.py`, print the local URL and setup error on failure, and pause on exit. Do not install packages for local mode. Add a folder `.gitignore` for `.venv/`, Python cache files, and `.env`.
- [ ] **Step 2: Document no-key local setup.** Explain Python 3+, launching by double-click or `python server.py`, default URL `http://127.0.0.1:8100`, stop instructions, and that no package install or provider key is needed for local mode.
- [ ] **Step 3: Document optional live mode configuration.** Explain that both `REBUFF_API_KEY` and `OPENAI_API_KEY` must be set in the server process environment, optionally set `REBUFF_API_URL` and `OPENAI_MODEL`, keep keys out of browser code/source control, and expect provider network use and possible charges. State that live mode adds no package installation, Rebuff is optional and its upstream project is archived, and if the service is unavailable the no-key mode remains playable.
- [ ] **Step 4: Write the player solve outline and separate author walkthrough.** Explain the clues and intended prompt-injection lesson in README without giving the exact tool invocation. In `SOLUTION.md`, mark spoilers clearly and document the fixed `read_diagnostic` action, stage prerequisites, fake flag, and verification route. Confirm the server never serves this file.
- [ ] **Step 5: Review docs against launcher behavior and exact env variable names.**

## Task 6: Acceptance review

**Files:**
- Review: `Dolos-Lab/`

**Interfaces:**
- Consumes: all implementation tasks.
- Produces: reviewed acceptance evidence and a standalone runnable challenge.

- [ ] **Step 1: Run all challenge unit tests.**

Run: `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -v`

Expected: all local challenge, provider-mock, route, session, and security-boundary tests pass without real keys or network access.

- [ ] **Step 2: Launch local mode and follow the author walkthrough.** Confirm each checkpoint, safe tool gate, and fake flag result; verify that refresh preserves only intended progress.
- [ ] **Step 3: Inspect the served routes and source for secret leakage.** Confirm `SOLUTION.md`, `challenge.py`, and `providers.py` are not static routes; no keys or flag occur in browser assets; no process execution or dynamic evaluation exists in `Dolos-Lab/`.
- [ ] **Step 4: Review optional provider tests.** Use mocks only; do not require a real key for acceptance. Verify provider errors always return deterministic guidance and never reveal the flag.
- [ ] **Step 5: Check workspace changes.** Confirm only the intended `Dolos-Lab/` files and any requested documentation changed.

## Completion Checks

- `Dolos-Lab/` launches locally without installed dependencies, keys, or network.
- Optional live mode requires both Rebuff and OpenAI keys, uses only server-side provider calls, and degrades to deterministic guidance.
- The app accepts only the fixed simulated `read_diagnostic` action with no arguments at the intended checkpoint.
- The fake flag is revealed only by server-side challenge validation and is absent from public assets and unsuccessful responses.
- No model-generated code or player-controlled command is interpreted or executed.
- Provider, malformed-input, session-expiry, and flag-secrecy checks pass using local mocks only.
