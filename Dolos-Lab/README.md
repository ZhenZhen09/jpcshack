# Dolos Lab

Dolos Lab is a standalone, local prompt-injection challenge. Investigate a fictional internal assistant, discover its diagnostic policy, and see whether untrusted instructions can make it request a protected record.

The runnable challenge uses one fixed simulated diagnostic tool and a fake flag. It never runs model-generated code, starts a shell, or reads files based on player input.

## Run locally on Windows

1. Install Python 3 and make sure `python` works in Command Prompt or PowerShell.
2. For AI replies, copy the project-root `ai-providers.env.example` to `ai-providers.env` and set the provider keys there. That one ignored file is shared by AI-1, Prompt Me Maybe, and Dolos Lab. Optional Rebuff screening settings can stay in this folder's `.env`. Without provider keys, the challenge runs in deterministic local mode.
3. Double-click `run.bat`, or open PowerShell in this directory and run:

   ```powershell
   python server.py
   ```

4. Open <http://127.0.0.1:8100>.
5. Stop the server with Ctrl+C.

The first `run.bat` launch creates a local `.venv`; it installs no packages. Deterministic local mode needs no API keys or runtime network access. The server listens on this computer at port 8100 by default, leaving Prompt Me Maybe's port 8000 available. Do not set `CHALLENGE_HOST` to a public interface for an internet-facing deployment.

## Optional AI provider fallback

Live model replies are optional. Configure one or more provider credentials in the project-root `ai-providers.env` or the server process environment; ordinary conversation tries providers in this order: Groq, Gemini, Cloudflare Workers AI, then OpenAI. The first valid reply is used. At the final tool checkpoint, Dolos uses OpenAI directly because it is the only configured provider that can request the simulated diagnostic tool. If a provider is unavailable, deterministic local guidance keeps the challenge usable. Optional prompt screening uses Rebuff when `REBUFF_API_KEY` is configured; Rebuff is not part of the model fallback chain.

Provider settings are:

- `GROQ_API_KEY`, `GROQ_MODEL`: Groq credentials and model; model defaults to `openai/gpt-oss-20b`.
- `GEMINI_API_KEY`, `GEMINI_MODEL`: Gemini credentials and model; model defaults to `gemini-3.5-flash-lite`.
- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_MODEL`: Workers AI credentials and model; model defaults to `@cf/meta/llama-3.1-8b-instruct`.
- `OPENAI_API_KEY`, `OPENAI_MODEL`: OpenAI credentials and model; model defaults to `gpt-4.1-mini`.
- `REBUFF_API_URL`: Rebuff base URL; defaults to `https://playground.rebuff.ai`.

Configure credentials from a private environment or secret manager before launching the server. Do not put keys in browser code, source control, screenshots, or chat messages. Provider requests contain the current player message and current public clue; the fake flag and later clues are never included. Provider calls may have usage charges and require outbound HTTPS.

If no model provider is configured or all providers fail, the challenge uses deterministic local responses. Rebuff is optional, and its [upstream repository is archived](https://github.com/protectai/rebuff); it is an experimental prompt filter, not a security boundary.

OpenAI integration uses the [Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create). The optional Rebuff call follows the [upstream Python client request format](https://github.com/protectai/rebuff/blob/main/python-sdk/rebuff/rebuff.py).

## Challenge outline

1. Ask for the public deployment summary.
2. Follow its lead to the archive index and diagnostic policy.
3. Test whether the assistant follows a written refusal when a message tries to override it.
4. The server releases the mock flag only when the single argument-free simulated diagnostic action is requested at the final checkpoint.

The challenge tracks progress in an in-memory session tied to an HTTP-only browser cookie. Progress survives a page refresh and expires after 30 minutes without activity; restarting the server clears sessions.

The author-only solution is in `SOLUTION.md`. The server does not serve that file.

## Run challenge checks

From the project root:

```powershell
python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -v
```

Provider tests use mocked responses. They do not call Rebuff or OpenAI and require no real keys.
