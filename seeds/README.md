# seeds/README.md

This directory contains the canonical seed baseline for TruthOS.

Current files:

- `dimensions.seed.jsonl`
- `core_principles.seed.jsonl`
- `truth_puzzles.seed.jsonl`

Rules:

- every seed row must follow `SEED_AUTHORING_GUIDE.md`
- keep rows semantically distinct and structurally complete
- avoid duplicate or semantically redundant rows
- material changes to `embedding_text` or other retrieval-relevant fields require vector reindex

These files are UTF-8 JSONL and should remain easy to inspect, diff, review, and extend.
