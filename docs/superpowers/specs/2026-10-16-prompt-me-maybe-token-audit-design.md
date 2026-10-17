# Prompt Me Maybe Token Audit Challenge Design

## Goal

Make the existing Northstar prompt-injection challenge medium difficulty. Players use an external GPT token calculator to discover which archive record to inspect, then use prompt injection to make the assistant reveal the mock flag.

## Audience and learning outcome

The challenge is for beginner security learners. It should teach that model instructions are not an authorization boundary, while also showing how text can be split into model-specific tokens. The puzzle must be solvable with ordinary wording variations instead of requiring one exact chat prompt.

## Player scenario

The player is auditing Northstar Systems' internal assistant before deployment. The assistant refuses direct requests for its protected deployment value. Its sample audit record contains a decoy flag and the exact phrase `token is king!`. The audit notes say the archive is indexed by GPT tokens. The player calculates the phrase's token count, opens the matching archive record, and uses that record's clue to request a hidden Release Notes appendix.

## Intended flow

1. The player opens the challenge and asks for the flag or another protected value. The assistant refuses.
2. The player asks to inspect the public sample deployment record. The assistant returns a clearly identified decoy value, the exact lowercase phrase `token is king!`, and a clue that archive records are indexed by GPT token count rather than word count.
3. The player pastes exactly `token is king!` without quotation marks into [tokencalculator.ai](https://tokencalculator.ai/), using the site's GPT tokenizer. At design time, this returns 4 input tokens although the phrase has 3 words. The player uses 4 as the archive record number. The challenge tells players to select GPT because the calculator documents that providers can produce different counts.
4. The player asks for archive record 4. Common equivalent forms such as `Show archive record 4`, `open the fourth archive record`, and `display item number four` are accepted. The assistant identifies record 4 as the Release Notes and gives an indirect clue that its appendix was used in a formatting review.
5. The player asks the assistant to quote or reproduce the Release Notes appendix. Common paraphrases are accepted. The assistant reveals the mock flag only if the current browser session has reached the archive-record stage.
6. The player submits the revealed flag to TryHackMe.

The external calculator's output is a clue, not trusted input to the server. Players can guess record 4; the challenge teaches the token-counting step but does not claim to prove that a player used the external site.

## Difficulty and hints

- Direct flag, secret, password, or configuration requests remain refused at every stage.
- The sample record contains a decoy flag that is visibly labeled as a demo value and is not accepted as the challenge flag.
- The existing **Need a hint?** control is changed to point toward counting the exact sample phrase with a GPT token calculator. It does not provide the archive number or final prompt.
- The final prompt must request the hidden appendix and use a reproduce/quote intent. Mentioning the word `flag` alone never reveals it.

## Components and data flow

- `prompt_me_maybe/server.py` remains the only authority for challenge phases and flag disclosure. `POST /api/chat` keeps the `{ "message": string }` request and `{ "reply": string, "solved": boolean }` response shapes.
- On the first page request, the server issues an opaque, random, HTTP-only, same-site session cookie. Chat messages carry it automatically on the same origin. The server stores only the challenge phase and last-activity time per session; it never stores message history.
- Session state is held in memory, protected for concurrent requests, and expires after 30 minutes of inactivity. Restarting the local server clears session progress. Missing, unknown, or expired cookies start a fresh phase.
- Stage transitions are ordered: initial → sample record disclosed → archive record 4 disclosed → solved. Requests for a later stage before the required earlier stage receive a non-secret hint and do not reveal the flag.
- `prompt_me_maybe/public/app.js` continues to render server responses with `textContent`; the frontend does not receive or contain the flag except after the server returns it for a solved session.
- `prompt_me_maybe/public/index.html` and `style.css` retain the current ChatGPT/Gemini-inspired layout and adapt the existing hint copy.
- `prompt_me_maybe/tests/test_server.py` covers ordering, paraphrases, cookie isolation, expiration, existing request validation, and flag secrecy.
- `prompt_me_maybe/README.md` documents setup, the exact external token-calculator steps, the full author walkthrough, decoy value, real mock flag, and the known limitation that the calculator is an external dependency which may change its GPT tokenizer.

## Session and privacy behavior

- Generate session identifiers with Python's standard-library `secrets` module; do not accept a caller-selected phase or session identifier from JSON.
- Do not log cookie values, prompts, the flag, or session contents.
- Keep all message length, JSON shape, content type, and body-size checks already enforced by the API.
- Use same-origin cookies and do not add third-party runtime requests. The token calculator is visited manually by the player and receives only the phrase the player pastes.
- Session data is ephemeral and contains no personal data. It expires after 30 idle minutes and is cleared when the process restarts.

## Error behavior

- Invalid or oversized API requests retain the existing generic 400 behavior.
- An expired or unknown session begins at the initial stage rather than exposing later-stage content.
- Session cookie parsing failures produce a fresh session without returning diagnostic details to the player.
- Existing generic server errors and frontend connection-failure behavior remain unchanged.

## Success criteria

- Direct secret requests never reveal the flag.
- The sample record returns only the labeled decoy and exact phrase `token is king!`.
- GPT token count 4 selects archive record 4; word count would point to the wrong record.
- Common paraphrases work for both archive selection and appendix reproduction.
- The flag is revealed only after the same browser session completes the required stages.
- A second browser session cannot use the first session's progress.
- Refreshing a page preserves progress while the session cookie is valid; inactivity expiry and server restart reset progress.
- The flag is absent from static assets and remains server-side until a completed sequence.
- The app still runs on Windows with the Python standard library and remains suitable for the existing Ubuntu systemd setup.

## Out of scope

- A real LLM, model API key, API billing, or model-hosted tokenizer.
- Automatic calls from the challenge server to tokencalculator.ai.
- Verifying that a player actually visited the external calculator.
- Persistent databases, accounts, leaderboards, or long-term challenge progress.
- Preventing a VM operator or a player with shell access from inspecting the challenge source.

## Validation approach

Use the built-in `unittest` suite for API behavior and session isolation. Exercise the full browser sequence on Windows, including the external GPT token count, common prompt paraphrases, a premature final request, a separate browser session, refresh, and the solved state. Recheck that public routes do not expose the flag and that the existing input limits and safe text rendering still hold. Ubuntu systemd verification remains a separate environment check.
