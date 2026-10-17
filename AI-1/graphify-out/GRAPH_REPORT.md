# Graph Report - AI-1  (2026-10-17)

## Corpus Check
- 3 files · ~1,095 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 23 nodes · 29 edges · 4 communities (1 shown, 3 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- app.py
- test_flag_unlock.py
- vercel.json
- test_flag_unlock.py

## God Nodes (most connected - your core abstractions)
1. `FlagUnlockTests` - 6 edges
2. `chat()` - 5 edges
3. `model_reply()` - 4 edges
4. `normalize_text()` - 3 edges
5. `contains_term()` - 3 edges
6. `is_unlock_request()` - 3 edges
7. `GeminiClientTests` - 3 edges
8. `log_to_sheet()` - 2 edges
9. `groq_reply()` - 2 edges
10. `gemini_reply()` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (4 total, 3 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.38
Nodes (8): chat(), contains_term(), gemini_reply(), groq_reply(), is_unlock_request(), log_to_sheet(), model_reply(), normalize_text()

## Knowledge Gaps
- **2 isolated node(s):** `builds`, `routes`
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FlagUnlockTests` connect `test_flag_unlock.py` to `test_flag_unlock.py`?**
  _High betweenness centrality (0.346) - this node is a cross-community bridge._
- **What connects `builds`, `routes` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._