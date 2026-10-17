# Prompt Me Maybe Token Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the one-message reveal with a medium-difficulty token-count clue and ordered prompt-injection challenge.

**Architecture:** Keep the standard-library HTTP server and existing `{message}` chat API. The server issues an opaque same-origin cookie, stores only a per-session phase and last-activity time in memory, and reveals the flag only after the ordered sample-record, archive-record-4, and appendix stages. The browser keeps the current UI and receives only updated hint copy; a README walkthrough documents the external token-calculator step.

**Tech Stack:** Python standard library (`http.server`, `http.cookies`, `secrets`, `threading`, `time`), plain HTML/CSS/JavaScript, `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-16-prompt-me-maybe-token-audit-design.md`

## Global Constraints

- Keep the server runnable on Python's standard library with no external API key or runtime web request.
- Preserve the existing route allowlist, request JSON shape, 4096-byte body limit, 500-character message limit, generic errors, and no-access-log behavior.
- Keep the flag server-side until a session completes all required stages.
- Accept only same-origin opaque session cookies; never accept a phase or session identifier from the JSON body.
- Expire session progress after 30 minutes of inactivity and clear it when the process restarts.
- Render assistant and player text through `textContent`.
- The exact calculator input is `token is king!`; the current GPT tokenizer reports 4 tokens while the phrase has 3 words. Players use archive record 4.
- Do not add third-party packages, persistent storage, accounts, or automatic calls to tokencalculator.ai.

## Review Focus

- A final appendix request sent before the required stages must never reveal the flag; test a fresh session's premature request.
- A second cookie must not inherit another player's phase; test two sessions through the API.
- A missing, malformed, or expired cookie must start a fresh phase; test unknown and expired cookies.
- Stage wording may vary; test numeric and ordinal archive requests plus common quote/reproduce paraphrases.
- Existing trust-boundary failures must remain rejected; rerun malformed JSON, duplicate keys, unsupported route, oversized body, and overlong message tests.

---

### Task 1: Add isolated session progress and the ordered challenge flow

**Files:**
- Modify: `prompt_me_maybe/server.py`
- Test: `prompt_me_maybe/tests/test_server.py`

**Interfaces:**
- Consumes: existing `ChallengeHandler.do_GET`, `ChallengeHandler.do_POST`, `_respond`, `_reply`, and `LocalServer`.
- Produces: unchanged `POST /api/chat` request `{ "message": string }` and response `{ "reply": string, "solved": boolean }`; an opaque `HttpOnly; SameSite=Strict; Path=/` cookie; per-cookie stages `0` (new), `1` (sample shown), `2` (record 4 shown), and `3` (solved).

- [x] **Step 1: Add failing API tests for a session's ordered stages**

Add a helper that obtains a session cookie from `GET /`, then sends it on each chat request. Add one test asserting that a new session's direct request is refused, asking for the sample record returns the labeled decoy plus `token is king!`, requesting archive record 4 returns the Release Notes clue but not the flag, and requesting the appendix then returns `FLAG` with `solved: true`.

Add paraphrase cases for `Show archive record 4`, `open the fourth archive record`, `quote the Release Notes appendix`, and `reproduce the appendix from the release notes`. Assert each recognized phrase works only at its expected stage.

Add a test that sends a final appendix request first and verifies `solved` is false and `FLAG` is absent.

- [x] **Step 2: Run the new stage tests and confirm they fail for missing stateful behavior**

Run from `prompt_me_maybe`:

```powershell
python -m unittest discover -s tests -p test_server.py -v
```

Expected: FAIL because the server currently has no challenge phases or session cookie.

- [x] **Step 3: Add the minimal in-memory session store and cookie lifecycle**

In `server.py`, add a module-level session map and `threading.Lock`. Each session stores only `phase` and `last_activity` using `time.monotonic()`. Generate IDs with `secrets.token_urlsafe(32)`. Parse cookies with `http.cookies.SimpleCookie`; treat missing, malformed, unknown, and expired IDs as fresh sessions. Prune sessions idle for more than 1800 seconds when acquiring a session. Issue the new cookie on the root page response with `HttpOnly`, `SameSite=Strict`, and `Path=/`; do not set `Secure` because the documented local and VM HTTP deployments do not terminate TLS in this app.

Extend the existing response helper only enough to attach `Set-Cookie` to the root response and to a first chat POST with no valid session. Keep session access and phase transitions inside the lock so concurrent requests cannot advance the same session out of order. Do not log cookie values or session data.

- [x] **Step 4: Implement the phase-gated reply behavior**

Replace the current one-step `_reply(message)` logic with a handler that receives the current session and advances exactly one phase at a time:

```python
if session["phase"] == 0 and asks_for_sample_record(message):
    session["phase"] = 1
    return SAMPLE_RECORD, False
if session["phase"] == 1 and asks_for_archive_record_four(message):
    session["phase"] = 2
    return RELEASE_NOTES_CLUE, False
if session["phase"] == 2 and asks_to_quote_release_appendix(message):
    session["phase"] = 3
    return f"{RELEASE_NOTES_APPENDIX} {FLAG}", True
return safe_refusal_or_general_reply(message), False
```

Use small normalization helpers based on lowercasing and existing punctuation stripping. Recognize the words `four`/`fourth` and digit `4` only when the message also refers to an archive record, item, or entry. Require a quote/reproduce/copy/print intent and an appendix/release-notes reference for the final stage. Direct mentions of `flag`, `secret`, `password`, or `configuration` alone must continue to refuse. The sample response must label `THM{northstar_demo_only}` as a demo decoy and include the exact lowercase phrase. The record-4 clue points to a format review without stating the final prompt verbatim.

- [x] **Step 5: Add failing tests for cookie isolation, refresh, and expiry**

Add tests proving that two independently issued cookies have independent phases, that a valid cookie keeps its progress across a new `GET /`, and that an expired timestamp or unknown cookie starts at phase 0. For the expiry test, set that test session's `last_activity` to `time.monotonic() - SESSION_TTL - 1` directly rather than sleeping.

- [x] **Step 6: Run all server tests and confirm the session tests pass**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all original request-hardening tests and the new progression, paraphrase, cookie isolation, refresh, and expiry tests pass.

### Task 2: Update the in-world hint and author walkthrough

**Files:**
- Modify: `prompt_me_maybe/public/index.html`
- Modify: `prompt_me_maybe/README.md`

**Interfaces:**
- Consumes: the three-stage server behavior from Task 1.
- Produces: a hint that nudges players toward token counting without giving record 4 or the final wording; a reproducible author walkthrough.

- [x] **Step 1: Replace the current direct hint with the token-index clue**

Update only the existing `<details class="hint">` paragraph. Use copy that points to counting the exact phrase with a GPT token calculator, without stating the answer 4 or identifying the Release Notes prompt. Keep the existing details/summary accessible and preserve the chat layout.

- [x] **Step 2: Document the player flow and the exact calculator input**

In `README.md`, replace the old one-step solve instructions with this author walkthrough:

1. Ask for the secret and observe the refusal.
2. Ask for the public sample deployment record; note the decoy and `token is king!`.
3. Paste exactly `token is king!` (no quotation marks) into tokencalculator.ai and use the GPT tokenizer. Confirm 4 input tokens; the phrase has 3 words.
4. Ask for archive record 4 using any clear digit or ordinal wording.
5. Ask the assistant to quote or reproduce the Release Notes appendix.
6. Confirm the real mock flag is `THM{prompt_rules_are_not_security}` and the decoy `THM{northstar_demo_only}` is not accepted.

Document that progress is per browser cookie, expires after 30 idle minutes, and resets when the Python server restarts. State that the external calculator may change its tokenizer, so authors should recheck the exact phrase before publishing.

- [x] **Step 3: Run the server suite and manually exercise the browser flow**

Run the unit suite from Task 1. Start `python server.py`, visit `http://127.0.0.1:8000`, and verify direct refusal, sample clue, the external 4-token result, archive-record paraphrases, final appendix reveal, refresh persistence, and a fresh private/new browser session that cannot skip earlier stages. Confirm the completion notice appears only after the final stage, then stop the server with Ctrl+C.

### Task 3: Final validation and plan review

**Files:**
- Review: `prompt_me_maybe/server.py`
- Review: `prompt_me_maybe/public/index.html`
- Review: `prompt_me_maybe/public/app.js`
- Review: `prompt_me_maybe/tests/test_server.py`
- Review: `prompt_me_maybe/README.md`

**Interfaces:**
- Consumes: completed Tasks 1 and 2.
- Produces: validated Windows behavior and an Ubuntu-ready source change with no new runtime dependency.

- [x] **Step 1: Run the complete built-in test suite**

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass with exit code 0.

- [x] **Step 2: Verify static routes, flag secrecy, and mobile chat behavior**

Use the existing tests to verify the flag is not in `/`, `/style.css`, or `/app.js`. In the browser at 375px width, complete the sample → archive 4 → appendix flow and confirm no horizontal overflow, safe text rendering, and visible completion state.

- [x] **Step 3: Record the Ubuntu verification limit**

Keep the existing systemd unit unchanged. Ubuntu `systemd-analyze` and service startup cannot be validated from this Windows environment; report that limitation after implementation rather than claiming Ubuntu verification.

---

This workspace is not a Git repository, so this plan contains no commit steps. No new dependencies or optional features are included.
