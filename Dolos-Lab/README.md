# Dolos Lab

Dolos Lab is a standalone, local prompt-injection challenge. Investigate a fictional internal assistant, discover its diagnostic policy, and see whether untrusted instructions can make it request a protected record.

The runnable challenge uses one fixed simulated diagnostic tool and a fake flag. It never runs model-generated code, starts a shell, or reads files based on player input.

## Run locally on Windows

1. Install Python 3 and make sure `python` works in Command Prompt or PowerShell.
2. Double-click `run.bat`, or open PowerShell in this directory and run:

   ```powershell
   python server.py
   ```

3. Open <http://127.0.0.1:8100>.
4. Stop the server with Ctrl+C.

The first `run.bat` launch creates a local `.venv`; it installs no packages. Local mode needs no API keys or runtime network access. The server listens on this computer at port 8100 by default, leaving Prompt Me Maybe's port 8000 available. Do not set `CHALLENGE_HOST` to a public interface for an internet-facing deployment.

## Optional Rebuff and OpenAI mode

Live mode is optional. It starts only when both `REBUFF_API_KEY` and `OPENAI_API_KEY` are set in the server process environment. Optional settings are:

- `REBUFF_API_URL`: Rebuff base URL; defaults to `https://playground.rebuff.ai`.
- `OPENAI_MODEL`: OpenAI model; defaults to `gpt-4.1-mini`.

Configure these variables from a private environment or secret manager before launching the server. Do not put keys in browser code, source control, screenshots, or chat messages. In live mode, the current player message is sent to Rebuff; the message and current public clue are sent to OpenAI. The fake flag and later clues are never included. Provider calls may have usage charges and require outbound HTTPS.

Rebuff is optional, and its [upstream repository is archived](https://github.com/protectai/rebuff). If Rebuff or OpenAI is unavailable, the challenge falls back to deterministic local responses. Rebuff is an experimental prompt filter, not a security boundary.

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
