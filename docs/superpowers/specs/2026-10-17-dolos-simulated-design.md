# Dolos: Simulated Prompt Injection Challenge Design

## Goal

Create a standalone, locally runnable Dolos-style prompt-injection challenge. Players investigate a fictional assistant and persuade it to request a protected diagnostic value, revealing a fake CTF flag through a simulated tool. The challenge teaches that prompt instructions and LLM guardrails are not security boundaries without executing model-generated code.

## Audience and learning outcomes

The challenge is for beginner-to-intermediate CTF players learning prompt injection and basic web application inspection. Players should see how an assistant can be manipulated by untrusted input, understand that a prompt filter may reject some inputs but does not provide complete security, and distinguish model-generated text from a server-validated challenge action.

## Scope and placement

- Create the runnable challenge in a standalone `Dolos-Lab/` folder at the project root.
- Keep the app self-contained: Python standard-library server, browser chat page and assets, tests, configuration documentation, Windows launcher, and an author-only walkthrough. Provider HTTP calls use the standard library so local play adds no runtime dependency.
- Use a fictional story, simulated diagnostic tool, and fake flag. Do not execute model-generated code, invoke a shell, or read challenge files in response to player input.
- Support two modes. Local mode works without keys or network access using deterministic responses. Optional live mode uses server-side Rebuff and OpenAI keys to screen messages and generate ordinary conversational replies.
- Do not require API keys, provider availability, or internet access for the core challenge flow. Never put credentials in browser assets, source control, logs, or player-visible responses.

## Player experience

1. The player opens a local chat page for a fictional assistant that claims it cannot reveal protected diagnostic data.
2. They investigate the assistant's behavior and challenge clues, then use prompt injection to persuade the assistant to request the simulated diagnostic action.
3. The server validates that the request is the one fixed challenge action and returns the fake flag. Ordinary text, model output, or a guessed flag cannot unlock it by themselves.
4. Rejected or unrelated messages receive concise, stage-aware guidance. Refreshing preserves progress within the browser session.
5. The page remains usable at mobile sizes and with keyboard navigation; messages are rendered as text, not executable markup.

The author walkthrough documents the intended solution and any provider-mode caveats without serving spoilers through the player routes.

## Application and provider boundaries

- The standalone Python server serves the page and a bounded chat API. It binds to localhost by default and uses per-browser in-memory sessions with expiry.
- A challenge module owns deterministic stage progression, fixed clues, the simulated tool action, and server-side fake-flag release. It does not import a shell, process execution, or filesystem-reading facility. The only simulated tool is a fixed, argument-free diagnostic lookup; the model cannot choose a command or path.
- In live mode, Rebuff screens the current message and OpenAI generates a conversational reply. Provider calls are server-side only. Only when both keys are configured is live mode enabled; if configuration is incomplete or a provider fails, use deterministic local guidance.
- Treat all player messages and model replies as untrusted. Model replies cannot directly advance challenge state or supply the flag. Live mode may return a structured request for the one fixed, argument-free diagnostic action; challenge code checks the current stage and runs only that simulated action before returning the flag. Local mode routes matching challenge actions through the same validator.
- Bound request size and message length, validate JSON shape, escape/render all user and model text safely, and return generic errors without secrets or stack traces.
- Read keys from environment configuration, document how to provide them locally, and ensure diagnostics do not log keys or chat contents.
- No model or guard provider is a security boundary for the simulated tool. The challenge must remain safe if either service is unavailable or returns malformed output.

## Setup and author documentation

`Dolos-Lab/README.md` will explain the learning goal, no-key Windows setup, local URL, optional Rebuff/OpenAI configuration, expected provider costs and network use, troubleshooting, and the safety limits of the simulation. `run.bat` creates a local virtual environment if needed and starts the server; the standard-library implementation has no required package installation. `SOLUTION.md` is marked author-only and gives the intended solve path and fixed tool action; it is never served by the app.

## Testing and acceptance

Checks cover deterministic local play, session separation and expiry, intended progression, early/invalid tool requests, flag secrecy, request limits, safe rendering, static asset routing, live-provider success and failure using mocked HTTP responses, and key redaction. A source-level check confirms the runnable challenge contains no shell execution path. No tests call real providers or need real keys.

Acceptance requires that the challenge launches independently, is playable without keys or network, supports optional server-side Rebuff/OpenAI integration, reveals only a fake flag after the server accepts the fixed simulated action, and never evaluates generated code or executes user-controlled commands.
