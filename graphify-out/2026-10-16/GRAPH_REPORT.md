# Graph Report - website  (2026-10-16)

## Corpus Check
- 25 files · ~28,661 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 253 nodes · 313 edges · 25 communities (18 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `ChallengeServerTests` - 32 edges
2. `ChallengeHandler` - 22 edges
3. `Deepfake Help Desk: Adversarial Audio CTF Design` - 14 edges
4. `What You Must Do When Invoked` - 12 edges
5. `Prompt Me Maybe — design spec` - 12 edges
6. `Prompt Me Maybe Token Audit Challenge Design` - 12 edges
7. `/graphify` - 10 edges
8. `Prompt Me Maybe Implementation Plan` - 9 edges
9. `graphify reference: extra exports and benchmark` - 8 edges
10. `File structure` - 7 edges

## Surprising Connections (you probably didn't know these)
- `ChallengeServerTests` --uses--> `ChallengeHandler`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → prompt_me_maybe/server.py
- `ChallengeServerTests` --uses--> `LocalServer`  [INFERRED]
  prompt_me_maybe/tests/test_server.py → prompt_me_maybe/server.py

## Import Cycles
- None detected.

## Communities (25 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (32): `app.py`, Application architecture, Audience and learning outcomes, Audio contract, `audio_features.py`, Audio tests, Browser interface, Challenge mechanics (+24 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (15): addMessage(), completion, currentHelp, feedback, form, guidanceExample, guidanceHint, guidanceLabel (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (12): Audience and learning outcome, Components and data flow, Error behavior, Goal, Hardening, Implementation and validation, Out of scope, Prompt Me Maybe — design spec (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.33
Nodes (3): LocalServer, Local-only server for the Prompt Me Maybe challenge., ThreadingHTTPServer

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
Cohesion: 0.52
Nodes (5): chat(), contains_term(), is_unlock_request(), log_to_sheet(), normalize_text()

### Community 13 - "Review Focus"
Cohesion: 0.29
Nodes (6): Global Constraints, Prompt Me Maybe Token Audit Implementation Plan, Review Focus, Task 1: Add isolated session progress and the ordered challenge flow, Task 2: Update the in-world hint and author walkthrough, Task 3: Final validation and plan review

### Community 14 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 15 - "Prompt Me Maybe"
Cohesion: 0.33
Nodes (5): Challenge walkthrough (author reference), Prompt Me Maybe, Run on Windows, Test on Windows, Ubuntu migration notes

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

## Knowledge Gaps
- **139 isolated node(s):** `builds`, `routes`, `form`, `input`, `sendButton` (+134 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChallengeServerTests` connect `Community 1` to `Community 2`, `Community 6`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `ChallengeHandler` connect `Community 2` to `Community 1`, `Community 6`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `ChallengeServerTests` (e.g. with `ChallengeHandler` and `LocalServer`) actually correct?**
  _`ChallengeServerTests` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ChallengeHandler` (e.g. with `ChallengeServerTests` and `.setUpClass()`) actually correct?**
  _`ChallengeHandler` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `form` to the rest of the system?**
  _140 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._