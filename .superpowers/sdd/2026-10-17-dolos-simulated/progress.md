# SDD ledger — plan: docs/superpowers/plans/2026-10-17-dolos-simulated.md

Workspace ruling: the prescribed SDD scripts and isolated worktree cannot run because this workspace has no Git metadata and `.git` is not writable. Proceeding in the user-authorized workspace, with no commits; no existing `Dolos/` files will be edited.

Pre-flight:
- Task 1 -> Task 2: challenge state/tool gate exports are consumed by provider-aware server flow; agreed interfaces align except local prompt-injection handling needs a deterministic simulated tool call, which will stay inside `handle_local_message` via `accept_tool_request`.
- Task 2 -> Task 3: provider adapters return validated `reply`/`tool_request` values consumed by HTTP handler; aligned.
- Task 3 -> Task 4: static routes and JSON payloads are consumed by browser page; aligned.
- Task 4 -> Task 5: all static routes and author-only exclusions are documented; aligned.

Ruling: assigned Dolos Lab port 8100 instead of the draft port 8000 — Prompt Me Maybe already uses 8000, confirmed by the local browser page; cost if wrong: an unexpected port conflict.

Task 1: Ruling: unittest discovery needs `-t Dolos-Lab` plus `tests/__init__.py` for root-level imports; updated all plan commands to use this form — the original command found the test file but failed before exercising it because `challenge` was not importable.
Task 1: complete — `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_challenge.py -v` — 5 tests passed.
Task 2: Ruling: the provider payload test initially prohibited the word “flag” anywhere, which also matched the safe system instruction; narrowed the assertion to prohibit flag-shaped values (`THM{`) — cost if wrong: the test could miss another flag format, addressed separately by provider output filtering.
Task 2: complete — `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_providers.py -v` — 7 tests passed; provider calls were mocked, with no real keys or network use.
Task 3: Ruling: the planned server test checked static files before Task 4 created them, causing expected 500s and making Task 3 non-independent; moved asset assertions to Task 4 and used `/api/session` to establish test sessions — task boundaries now remain independently testable.
Task 3: complete — `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_server.py -v` — 7 tests passed, including session isolation/expiry, body limits, private routes, flag gate, and provider-failure fallback.
Task 4: complete — `python -m unittest discover -s Dolos-Lab/tests -t Dolos-Lab -p test_server.py -v` — 8 tests passed; browser check at 360px showed no horizontal overflow or console errors, keyboard Enter completed the challenge, and refresh restored solved state.
Task 5: complete — standalone run instructions, optional provider configuration, author solution, and launcher are present under `Dolos-Lab/`.
Task 6: independent review found two issues: a failed OpenAI response could commit the local final-stage solution, and abandoned sessions could accumulate. Added regression tests first (both failed), kept live state unchanged on malformed/failed OpenAI output, and added opportunistic expiry cleanup plus a 1000-session LRU cap.
Task 6: complete — `python -m unittest discover -s tests -t . -v` from `Dolos-Lab/` — all 23 tests passed. `graphify update .` refreshed the graph; three JSON source files produced zero graph nodes, as in prior runs. Browser walkthrough had already passed at 360px with no overflow or console errors. No external provider calls or keys were used.
