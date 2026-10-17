# Graph Report - AI-1  (2026-10-16)

## Corpus Check
- 3 files · ~869 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 13 nodes · 16 edges · 3 communities (1 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- app.py
- test_flag_unlock.py
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `chat()` - 4 edges
2. `normalize_text()` - 3 edges
3. `contains_term()` - 3 edges
4. `is_unlock_request()` - 3 edges
5. `log_to_sheet()` - 2 edges
6. `FlagUnlockTests` - 2 edges
7. `builds` - 1 edges
8. `routes` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (3 total, 2 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.52
Nodes (5): chat(), contains_term(), is_unlock_request(), log_to_sheet(), normalize_text()

## Knowledge Gaps
- **2 isolated node(s):** `builds`, `routes`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `builds`, `routes` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._