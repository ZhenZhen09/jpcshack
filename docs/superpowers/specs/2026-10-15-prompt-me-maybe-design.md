# Prompt Me Maybe — design spec

## Goal

Create the first TryHackMe-style AI security challenge in a new `prompt_me_maybe` folder at the project root. Develop and run it on Windows first, then document how to move it to an Ubuntu VM. A player finds a local chat website and uses a deliberate prompt-injection weakness to make a scripted assistant reveal a fake `THM{...}` flag.

## Audience and learning outcome

The room is for beginner players who can connect to a Linux target and use a browser. It teaches that instructions given to a chatbot are not an authorization boundary, and that secrets should be protected by application logic rather than a request for the model to keep them hidden.

## Proposed approaches

1. **Scripted local chat app (chosen):** use Python's standard library for a small HTTP server and browser UI. Responses are deterministic, there is no API key or external service, and the same app can later run on Ubuntu.
2. **Real LLM API:** closer to production behavior, but needs credentials, internet access, incurs possible usage charges, and makes a beginner challenge less predictable.
3. **Static browser-only simulation:** simplest to launch, but any flag and challenge logic sent to the browser can be inspected immediately, defeating the intended server-side solve.

## User flow

1. The player discovers the web service on the target and opens the challenge page.
2. A short scenario explains that the fictional assistant protects an internal configuration value.
3. The player asks for the secret directly and receives a refusal.
4. A subtle in-world clue suggests asking the assistant to reproduce or transform its configuration.
5. The player rephrases their request and the scripted server returns the fake flag in the chat.
6. The player submits the flag to TryHackMe. Hints can progressively point toward rephrasing without giving away the exact prompt.

## Components and data flow

- `prompt_me_maybe/server.py`: Python standard-library HTTP server. Serves the chat page and accepts bounded JSON chat requests. Implements only the scripted scenario and intended reveal condition.
- `prompt_me_maybe/public/index.html`, `style.css`, `app.js`: accessible, responsive chat interface. Browser sends user messages to the local server and renders responses as text.
- `prompt_me_maybe/README.md`: Windows run instructions, challenge author notes, intended solve, flag-setting guidance, and later Ubuntu migration notes.
- The flag remains in server-side challenge configuration/code and is never embedded in HTML, CSS, JavaScript, source maps, or public static assets. It is disposable and contains no real credential or personal data.

The server does not invoke a shell, read arbitrary user-selected files, access a database, or call the internet. It only receives chat text and returns a scripted reply.

## Hardening

- Bind the Windows development server to loopback so it is local-only by default.
- Use an explicit route allowlist; do not expose source files, configuration, directory listings, or arbitrary filesystem paths.
- Bound request body and message lengths, accept only the expected JSON shape, and return generic errors without tracebacks.
- Escape/render all chat content as text; do not inject participant input or bot output as HTML.
- Do not persist participant prompts or log the flag.
- For the later Ubuntu target, use a dedicated unprivileged service account, restrictive file permissions, no SSH service unless separately required, and expose only the challenge web port. Disable debug output and restrict outbound traffic.
- Hardening limits accidental exposure through the web app. It cannot make code or secrets inaccessible to a player who gains operating-system access to the VM; the challenge must not rely on that guarantee.

## Visual and interaction direction

Use a restrained, dark terminal-inspired learning interface with high-contrast readable text, clear speaker labels, visible keyboard focus, and an obvious message field and send button. Keep the layout usable on narrow screens. Avoid unnecessary glitch effects or motion; the simulated chatbot content and clue should remain the focus. UI guidance search matched a cyberpunk style, but its neon effects are intentionally toned down for readability and accessibility.

## Error behavior

- Empty or malformed messages receive a clear inline validation message.
- Oversized requests are rejected before scenario processing.
- A server error returns a generic message to the browser and details only to the local operator, excluding chat content and flag values.
- If the server is not running, the page shows a simple connection failure with a retry action.

## Success criteria

- The app starts on Windows with Python and no third-party packages or external API keys.
- The page is reachable through the loopback address only during local development.
- Direct requests refuse; the clue-guided intended rephrasing reveals the mock flag in the chat.
- The flag and challenge implementation are not exposed through static assets or arbitrary web paths.
- Participant messages are safely rendered and bounded.
- README instructions explain local startup and the boundary between local development and the future Ubuntu/TryHackMe machine.

## Out of scope

- Real LLM integrations, accounts, databases, leaderboards, scoring backends, or persistent chat history.
- Publishing a TryHackMe room or uploading an OVA. These require separate account access and packaging/review work.
- Guaranteeing secrecy against a player with shell/root access to the complete VM image.

## Implementation and validation

After this spec is approved, create a separate implementation plan before changing application code. Validate the local start flow, intended solve path, path allowlist, request limits, and safe text rendering. Do not use a real flag or secret in development.
