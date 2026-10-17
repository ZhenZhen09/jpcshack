# Prompt Me Maybe — Groq chat design

## Goal

Give the Prompt Me Maybe assistant natural, story-consistent chat responses using Groq, while keeping the existing investigation stages, answer validation, and flag reveal deterministic and server-controlled.

## User experience

- The player continues the existing archive investigation in the same chat interface.
- Requests that match a challenge action are handled by the current deterministic progression and return its fixed clue or flag response.
- Other valid chat messages are sent from the Python server to Groq. The model replies as the fictional archive assistant, using only the current stage's public context and the player's message.
- The browser never receives the Groq credential. If no key is configured or Groq fails/times out, the existing stage-aware guidance remains available so the challenge can still be played.

## Approaches considered

1. **Groq as conversational fallback (chosen):** retain the current deterministic state machine as the authority for progression; call Groq only for messages that do not trigger a challenge action. This improves conversational feel without making the solve path dependent on model behavior.
2. **Groq controls every response and progression:** more open-ended, but makes checkpoints, flag handling, and repeatability model-dependent. Not chosen because it risks skipping or fabricating challenge steps.
3. **Keep deterministic replies only:** no credentials, billing, or outbound dependency, but does not meet the request for Groq-powered chat.

## Components and data flow

- `prompt_me_maybe/server.py` keeps request validation and challenge progression. It evaluates the existing deterministic actions first. For unmatched valid messages only, it sends a bounded request to Groq's chat-completions API using Python's standard-library HTTP support; no new package is required.
- The Groq model name is configurable through `GROQ_MODEL`, defaulting to `openai/gpt-oss-20b` to match the currently configured AI-1 challenge. The key is read from `GROQ_API_KEY` at server startup.
- The model receives a short system instruction for the archive-assistant persona, the current public guidance/stage, and the current player message. It does not receive the flag, future clues, server source, or credentials. Chat history is not sent; the existing session stage supplies the needed story context.
- Model requests have a finite timeout and bounded output. API errors and malformed responses are not exposed verbatim to players and must not log the key or full prompt. On failure, the server returns its existing stage-aware guidance.
- `prompt_me_maybe/public/app.js` and the page layout remain unchanged unless implementation reveals a necessary loading/error-state adjustment; all API calls remain browser-to-local-server, never browser-to-Groq.
- Add `.env` to the challenge folder's ignore rules and provide a non-secret `.env.example`. Local setup documentation explains configuration without embedding a real key.
- Update `README.md` and `prompt-me-maybe.service` deployment guidance: the service now needs narrowly scoped outbound HTTPS/DNS access to Groq, and a deployment secret must be readable by the service account but not exposed to players. Remove claims that the application never calls the internet or requires no API credentials.

## Security and reliability

- A Groq key is an operator secret, not a challenge clue. Never place it in HTML, JavaScript, responses, or logs. Any key pasted into chat or otherwise exposed should be rotated before use.
- Keep message/request size validation, session isolation, HTTP-only cookies, and safe text rendering intact.
- The deterministic challenge state and flag reveal remain authoritative even if the model attempts to skip steps or produce convincing but incorrect answers.
- The external API adds availability, quota, latency, and possible usage-cost dependencies. Local development remains possible without a key by using deterministic guidance; production operators must configure and monitor a valid key and outbound access.
- The current app is intended for a controlled CTF environment. Before exposing it publicly, review abuse/rate limiting and the provider's current usage/pricing limits separately.

## Success criteria

- Existing challenge tests and author walkthrough continue to pass unchanged.
- An unmatched message with a mocked successful Groq response returns the model's reply, without changing the player's stage.
- Recognized challenge actions still return their deterministic clue/flag without calling Groq.
- Missing credentials, timeout, API error, or malformed provider response return stage-aware guidance without exposing secrets or provider diagnostics.
- The browser bundle and HTTP responses never expose `GROQ_API_KEY`; `.env` is ignored.
- README and systemd instructions accurately describe the optional local configuration and required outbound provider access.

## Out of scope

- Letting the model choose or mutate challenge stages, validate the token count, or reveal the flag.
- Conversation history/memory, streaming responses, model selection UI, chat analytics, or provider failover.
- Adding Groq credentials to source control or copying credentials from chat into files.
- Publishing a TryHackMe room or changing its hosted flag.

## Next step

After this spec is reviewed and approved, create a separate implementation plan. Do not modify application code before that plan is reviewed and an execution method is selected.
