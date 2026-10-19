# Graph Report - website  (2026-10-19)

## Corpus Check
- 142 files · ~63,112 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 804 nodes · 959 edges · 131 communities (75 shown, 56 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1262ce8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- File structure
- Prompt Me Maybe Windows Development and Ubuntu Deployment Plan
- Prompt Me Maybe Implementation Plan
- graphify reference: extra exports and benchmark
- app.py
- Review Focus
- graphify reference: query, path, explain
- Prompt Me Maybe
- Ponytail
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- vercel.json
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- AGENTS.md
- extraction-spec.md
- Prompt Me Maybe — Groq chat design
- FlagUnlockTests
- test_app.py
- Sigma Tech Implementation Plan
- Sigma Tech: Image Classifier Challenge Design
- Sigma Tech
- app.js
- SOLUTION.md
- ChallengeHandler
- Review Focus
- install.sh
- portal.js
- providers.py
- ProviderTests
- challenge.py
- ChallengeServerTests
- Dolos Simulated Challenge Implementation Plan
- app.js
- Dolos: Simulated Prompt Injection Challenge Design
- Dolos Lab
- Dolos Lab Solution — Author Only
- __init__.py
- PortalHandler
- ChallengeHandler
- common.js
- challenge.py
- challenge.py
- build_capture.py
- app.js
- README.md
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- challenge.py
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md
- README.md

## God Nodes (most connected - your core abstractions)
1. `ChallengeServerTests` - 36 edges
2. `ChallengeHandler` - 21 edges
3. `ChallengeServerTests` - 17 edges
4. `ChallengeHandler` - 16 edges
5. `ChallengeHandler` - 15 edges
6. `Deepfake Help Desk: Adversarial Audio CTF Design` - 14 edges
7. `What You Must Do When Invoked` - 12 edges
8. `Dolos Simulated Challenge Implementation Plan` - 12 edges
9. `Prompt Me Maybe — design spec` - 12 edges
10. `Prompt Me Maybe Token Audit Challenge Design` - 12 edges

## Surprising Connections (you probably didn't know these)
- `ChallengeServerTests` --uses--> `LocalServer`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → Dolos-Lab/server.py
- `ChallengeServerTests` --uses--> `ChallengeHandler`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → Dolos-Lab/server.py
- `GroqClientTests` --uses--> `LocalServer`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → Dolos-Lab/server.py
- `ModelFallbackTests` --uses--> `LocalServer`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → Dolos-Lab/server.py
- `GroqClientTests` --uses--> `ChallengeHandler`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → Dolos-Lab/server.py

## Import Cycles
- None detected.

## Communities (131 total, 56 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (32): `app.py`, Application architecture, Audience and learning outcomes, Audio contract, `audio_features.py`, Audio tests, Browser interface, Challenge mechanics (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (12): ChallengeHandler, _connect_prompt_database(), _initialize_prompt_database(), LocalServer, main(), _prompt_status(), BaseHTTPRequestHandler, ThreadingHTTPServer (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 4 - "Community 4"
Cohesion: 0.20
Nodes (13): addMessage(), completion, feedback, form, input, promptMeter, restoreProgress(), sendButton (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (12): Audience and learning outcome, Components and data flow, Error behavior, Goal, Hardening, Implementation and validation, Out of scope, Prompt Me Maybe — design spec (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.20
Nodes (9): File Map, Global Constraints, Implementation Notes, Prompt Me Maybe Groq Chat Implementation Plan, Review Focus, Task 1: Add a bounded Groq client, Task 2: Integrate the model as a non-authoritative chat fallback, Task 3: Make local launch and deployment configuration safe and clear (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (12): Audience and learning outcome, Components and data flow, Difficulty and hints, Error behavior, Goal, Intended flow, Out of scope, Player scenario (+4 more)

### Community 8 - "File structure"
Cohesion: 0.17
Nodes (11): Deepfake Help Desk Adversarial Audio Implementation Plan, Execution notes, File structure, Global Constraints, Review Focus, Task 1: Build the strict audio boundary and feature pipeline, Task 2: Generate and load the transparent detector artifact, Task 3: Build and prove the intended adversarial attack (+3 more)

### Community 9 - "Prompt Me Maybe Windows Development and Ubuntu Deployment Plan"
Cohesion: 0.18
Nodes (10): Approved refinement, File map, Global Constraints, Plan self-review, Prompt Me Maybe Windows Development and Ubuntu Deployment Plan, Review Focus, Scope and acceptance, Task 1: Implement and test the server (+2 more)

### Community 10 - "Prompt Me Maybe Implementation Plan"
Cohesion: 0.20
Nodes (9): File map, Global Constraints, Plan self-review, Prompt Me Maybe Implementation Plan, Review Focus, Scope and acceptance, Task 1: Implement the local challenge server, Task 2: Build the accessible chat interface (+1 more)

### Community 11 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 12 - "app.py"
Cohesion: 0.23
Nodes (16): chat(), cloudflare_reply(), _connect_prompt_database(), contains_term(), gemini_reply(), groq_reply(), _initialize_prompt_database(), is_unlock_request() (+8 more)

### Community 13 - "Review Focus"
Cohesion: 0.29
Nodes (6): Global Constraints, Prompt Me Maybe Token Audit Implementation Plan, Review Focus, Task 1: Add isolated session progress and the ordered challenge flow, Task 2: Update the in-world hint and author walkthrough, Task 3: Final validation and plan review

### Community 14 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 15 - "Prompt Me Maybe"
Cohesion: 0.17
Nodes (10): Install on a fresh Ubuntu VM, Prepare and export an OVA, Service operations, Shared AI provider configuration, Ubuntu CTF VM deployment, Challenge walkthrough (author reference), Prompt Me Maybe, Run on Windows (+2 more)

### Community 16 - "Ponytail"
Cohesion: 0.40
Nodes (4): Before you write, Levels, Ponytail, The smallest complete change

### Community 17 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 18 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 19 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 25 - "Prompt Me Maybe — Groq chat design"
Cohesion: 0.20
Nodes (9): Approaches considered, Components and data flow, Goal, Next step, Out of scope, Prompt Me Maybe — Groq chat design, Security and reliability, Success criteria (+1 more)

### Community 27 - "test_app.py"
Cohesion: 0.10
Nodes (27): create_app(), Local Flask server for the Sigma Tech image-classifier challenge., count_edits(), load_model(), predict_pixels(), Shared image validation and inference for Sigma Tech., validate_pixels(), find_solution() (+19 more)

### Community 28 - "Sigma Tech Implementation Plan"
Cohesion: 0.20
Nodes (9): Completion checks, File Map, Global Constraints, Interfaces, Review Focus, Sigma Tech Implementation Plan, Task 1: Deterministic classifier, generated assets, and solver, Task 2: Guarded Flask API and player interface (+1 more)

### Community 29 - "Sigma Tech: Image Classifier Challenge Design"
Cohesion: 0.20
Nodes (9): Application boundaries and validation, Audience and learning outcomes, Classifier and challenge assets, Goal, Player experience, Scope and placement, Setup and solve documentation, Sigma Tech: Image Classifier Challenge Design (+1 more)

### Community 30 - "Sigma Tech"
Cohesion: 0.40
Nodes (4): Author commands, Player solve outline, Run on Windows, Sigma Tech

### Community 31 - "app.js"
Cohesion: 0.83
Nodes (3): draw(), setResult(), togglePixel()

### Community 33 - "ChallengeHandler"
Cohesion: 0.11
Nodes (14): assistant_prompt(), ChallengeHandler, cloudflare_reply(), _connect_prompt_database(), gemini_reply(), groq_reply(), _initialize_prompt_database(), LocalServer (+6 more)

### Community 34 - "Review Focus"
Cohesion: 0.29
Nodes (6): Global Constraints, Groq to Gemini Chat Fallback Implementation Plan, Review Focus, Task 1: Add the provider chain to Prompt Me Maybe, Task 2: Add the provider chain to AI-1, Task 3: Configure locally, verify both applications, and refresh Graphify

### Community 35 - "install.sh"
Cohesion: 0.70
Nodes (4): create_service_user(), install_tree(), setup_venv(), install.sh script

### Community 37 - "providers.py"
Cohesion: 0.19
Nodes (19): _chat_reply(), cloudflare_reply(), gemini_reply(), groq_reply(), live_mode_configured(), _load_local_env(), model_reply(), openai_reply() (+11 more)

### Community 41 - "challenge.py"
Cohesion: 0.20
Nodes (11): accept_tool_request(), handle_local_message(), _is_prompt_injection(), new_state(), Deterministic Dolos challenge logic and the fixed simulated tool., Execute the single simulated, argument-free diagnostic lookup., Create a fresh per-browser challenge state., Advance known puzzle actions, or simulate an injected tool request. (+3 more)

### Community 43 - "Dolos Simulated Challenge Implementation Plan"
Cohesion: 0.15
Nodes (12): Completion Checks, Dolos Simulated Challenge Implementation Plan, File Map, Global Constraints, Interfaces, Review Focus, Task 1: Challenge state machine and safe simulated tool, Task 2: Optional provider adapters (+4 more)

### Community 44 - "app.js"
Cohesion: 0.18
Nodes (10): count, form, input, promptMeter, restoreSession(), sendButton, setBusy(), status (+2 more)

### Community 45 - "Dolos: Simulated Prompt Injection Challenge Design"
Cohesion: 0.22
Nodes (8): Application and provider boundaries, Audience and learning outcomes, Dolos: Simulated Prompt Injection Challenge Design, Goal, Player experience, Scope and placement, Setup and author documentation, Testing and acceptance

### Community 46 - "Dolos Lab"
Cohesion: 0.33
Nodes (5): Challenge outline, Dolos Lab, Optional AI provider fallback, Run challenge checks, Run locally on Windows

### Community 47 - "Dolos Lab Solution — Author Only"
Cohesion: 0.50
Nodes (3): Dolos Lab Solution — Author Only, Intended path, Security boundary

### Community 59 - "PortalHandler"
Cohesion: 0.17
Nodes (7): ChallengeManager, main(), port_is_open(), PortalHandler, Serve the local challenge index and launch only the selected challenge., Popen, SimpleHTTPRequestHandler

### Community 60 - "ChallengeHandler"
Cohesion: 0.13
Nodes (10): ChallengeHandler, connect_db(), initialize_db(), main(), BaseHTTPRequestHandler, Path, valid_session_id(), is_solved() (+2 more)

### Community 61 - "common.js"
Cohesion: 0.80
Nodes (4): init(), request(), show(), submit()

### Community 68 - "build_capture.py"
Cohesion: 0.48
Nodes (6): ethernet_ipv4_udp(), internet_checksum(), main(), make_capture(), Build the fixed educational TFTP packet capture using Python's stdlib., rot13()

## Knowledge Gaps
- **232 isolated node(s):** `builds`, `routes`, `transcript`, `form`, `input` (+227 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChallengeServerTests` connect `Community 1` to `ChallengeHandler`, `Community 2`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `ChallengeHandler` connect `Community 2` to `Community 1`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `ChallengeServerTests` (e.g. with `ChallengeHandler` and `LocalServer`) actually correct?**
  _`ChallengeServerTests` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ChallengeHandler` (e.g. with `main()` and `ChallengeServerTests`) actually correct?**
  _`ChallengeHandler` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `Deterministic Dolos challenge logic and the fixed simulated tool.` to the rest of the system?**
  _272 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.11397849462365592 - nodes in this community are weakly interconnected._