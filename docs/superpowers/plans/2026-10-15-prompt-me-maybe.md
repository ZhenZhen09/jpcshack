# Prompt Me Maybe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a beginner-friendly, Windows-first local web challenge in `prompt_me_maybe` where a scripted chatbot reveals a mock TryHackMe flag through an intended prompt-injection interaction.

**Architecture:** A Python standard-library HTTP server binds to `127.0.0.1`, serves exactly three allowlisted public assets, and handles bounded JSON chat requests at one API route. The chatbot decision and disposable flag remain server-side; the browser renders text only and never receives source/config files.

**Tech Stack:** Python 3 standard library (`http.server`, `json`, `pathlib`), semantic HTML, CSS, and vanilla JavaScript. No packages, external AI, network API, or database.

**Spec:** `docs/superpowers/specs/2026-10-15-prompt-me-maybe-design.md`

## Global Constraints

- Create the app under the project-root folder `prompt_me_maybe`.
- The app starts on Windows with Python and no third-party packages or external API keys.
- Bind the local development server to loopback only.
- The server does not invoke a shell, read arbitrary user-selected files, access a database, or call the internet.
- Keep the flag server-side; it is disposable and is not a real credential or personal data.
- Use an explicit route allowlist; do not expose source files, configuration, directory listings, or arbitrary filesystem paths.
- Bound request body and message lengths, accept only the expected JSON shape, and return generic errors without tracebacks.
- Render all chat content as text, not HTML. Do not persist participant prompts or log the flag.
- The Ubuntu target must use a dedicated unprivileged service account, restrictive file permissions, no SSH unless separately required, and only the challenge web port exposed.
- Use a restrained dark terminal-inspired UI with high contrast, keyboard focus, clear labels, and narrow-screen support; avoid unnecessary motion.

## Review Focus

- Malformed, absent, or non-JSON request bodies must return a generic client error without traceback.
- Oversized bodies and messages must be rejected before chatbot logic runs.
- Unknown paths, encoded traversal attempts, and unsupported methods must not return source or files.
- HTML-like player input and chatbot output must display literally and never execute.
- Direct secret requests must refuse; only the clue-guided intended rephrasing should reveal the mock flag.

---

## File map

- Create `prompt_me_maybe/server.py`: loopback HTTP server, exact route allowlist, bounded request parsing, deterministic chat scenario, and flag response.
- Create `prompt_me_maybe/public/index.html`: challenge intro, chat transcript, labeled form controls, hints, and completion guidance.
- Create `prompt_me_maybe/public/style.css`: responsive dark terminal-inspired visual style, semantic color variables, contrast, and focus styles.
- Create `prompt_me_maybe/public/app.js`: chat request handling, text-only message rendering, busy/error states, and retry behavior.
- Create `prompt_me_maybe/README.md`: Windows startup, player solve path, author notes, and Ubuntu migration/hardening guidance.
- Create `prompt_me_maybe/run.bat`: one-command Windows startup that runs the server from its own directory.

## Task 1: Implement the local challenge server

**Files:**
- Create: `prompt_me_maybe/server.py`

**Interfaces:**
- `GET /` returns `public/index.html`.
- `GET /style.css` returns `public/style.css`.
- `GET /app.js` returns `public/app.js`.
- `POST /api/chat` accepts exactly `{"message": "..."}` and returns `{"reply": "...", "solved": false}` or `{"reply": "...", "solved": true}`.
- Any other method/path returns a generic 404/405 without revealing filesystem paths.

- [ ] Create an HTTP request handler that binds only to `127.0.0.1:8000` and disables directory listing by serving only the three explicit asset routes.
- [ ] Add JSON request validation: require `application/json`, require a valid content length from 1 through 4096 bytes, decode UTF-8 strictly, require one string field named `message`, strip surrounding whitespace, and reject messages over 500 characters with a generic 400 response.
- [ ] Add the deterministic scenario: direct requests for a secret receive a refusal; a request that asks to quote/reproduce the assistant's configuration returns a server-held fake flag `THM{prompt_rules_are_not_security}` and sets `solved` true. Do not log the message or flag.
- [ ] Return JSON with `Content-Type: application/json; charset=utf-8` and `X-Content-Type-Options: nosniff`; serve only the intended HTML/CSS/JS with fixed MIME types and `Cache-Control: no-store`.
- [ ] Add safe generic handling for malformed requests and unexpected internal errors; do not send stack traces or exception text to the browser.

## Task 2: Build the accessible chat interface

**Files:**
- Create: `prompt_me_maybe/public/index.html`
- Create: `prompt_me_maybe/public/style.css`
- Create: `prompt_me_maybe/public/app.js`

**Interfaces:**
- Uses the server contract from Task 1 at `POST /api/chat`.
- The message form has a visible label, a 500-character maximum, and a submit button.
- Transcript announcements use an `aria-live="polite"` region; player input and bot replies are inserted with `textContent`.

- [ ] Create a semantic page with a short fictional scenario, one progressive hint panel, an initially visible bot greeting, a labeled message form, and a polite live transcript.
- [ ] Style it as a restrained dark terminal-inspired interface: charcoal background, readable light text, one green accent for success, red only for errors, visible focus ring, 16px minimum body text, and responsive single-column layout.
- [ ] Implement submit handling that trims and locally rejects empty messages, disables the submit control while waiting, posts JSON to `/api/chat`, and appends both sides of the conversation using text nodes only.
- [ ] Show a clear inline connection or server error with a retry path, re-enable the form after all outcomes, and show the flag submission instruction only when the response says `solved: true`.
- [ ] Keep the interaction keyboard operable and usable at 375px viewport width; do not add animation or external font/image dependencies.

## Task 3: Add launch and author documentation

**Files:**
- Create: `prompt_me_maybe/run.bat`
- Create: `prompt_me_maybe/README.md`

**Interfaces:**
- `run.bat` changes its working directory to its own folder and starts `python server.py`.
- README commands and URLs match Task 1's loopback host and port.

- [ ] Add a Windows launcher that runs the standard-library server from the challenge directory and leaves its console open so startup errors are visible to the author.
- [ ] Document prerequisites (Python 3), launch steps, `http://127.0.0.1:8000`, stop instructions, expected direct-refusal/rephrase/reveal path, and the mock flag for author validation.
- [ ] Document the Ubuntu migration: create a dedicated unprivileged account, install only supported Python 3, use restrictive file permissions, run the service bound to the challenge interface rather than public interfaces, firewall to the required web port, disable SSH if unnecessary, deny outbound network access, and avoid treating source-file concealment as protection after OS compromise.
- [ ] Document that TryHackMe publishing, room metadata, flags, and OVA packaging are separate follow-up work requiring creator access and review.

## Scope and acceptance

The initial deliverable is the Windows-local challenge folder only. It does not publish to TryHackMe, generate an OVA, expose the server to the LAN, persist chats, or call a real AI. The player should be able to solve the fake challenge through the chat UI; the server should refuse direct secret requests and reveal the mock flag only for the intended configuration-reproduction request.

## Plan self-review

- Spec coverage: goal, learning outcome, components, hardening, UI direction, errors, success criteria, and out-of-scope deployment work map to Tasks 1–3 or Scope and acceptance.
- Review focus: malformed body, length limit, route allowlist, safe rendering, and deterministic solve path are explicitly assigned to Tasks 1–2.
- No real project code or automated test files are included in this plan. The user asked for implementation but has not separately asked to add or run tests; verification commands are therefore omitted.
- The workspace is not a Git repository, so this plan has no commit steps.
