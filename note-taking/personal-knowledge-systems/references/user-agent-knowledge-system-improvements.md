# the user agent knowledge-system improvement notes

Derived from reviewing the WeChat article `深度解析LLM Wiki / Obsidian-Wiki / GBrain：Agent时代知识的“自组织”与“自进化”` and mapping it onto the user's existing filesystem wiki.

## Key interpretation

The useful pattern is not "add another knowledge base". It is: convert valuable sources, questions, task outcomes, and decisions into a maintained Markdown wiki so knowledge compounds instead of being rediscovered via chat/RAG each time.

## Immediate improvements for `~/wiki`

- Add `hot.md`: a short active-context cache, ~500-800 Chinese characters, covering current learning focus, today's/near-term tasks, recent sources, active weak points, and next priorities.
- Add `.manifest.json`: track raw source URL/path, sha256, ingestion time, generated/updated formal pages, and status (`new`, `modified`, `unchanged`, `deleted`). Use it before ingesting sources to avoid duplication.
- Preserve high-value answers as `queries/` pages, especially strategy/system-improvement discussions. Example target: `queries/improving-the user-agent-knowledge-system-with-llm-wiki.md`.
- Run wiki lint periodically: missing index entries, raw sources without formal pages, orphan pages, duplicate concepts, stale short-term plans in long-term pages, pages needing split, and missing source markings.
- Treat Feishu learning-task completion as a possible wiki update trigger: update course/track pages, record weak points if supplied, and derive next tasks.

## Current state after 2026-06-19 LLM Wiki v2 migration

the user explicitly approved a full upgrade from the earlier pure LLM-Wiki style to an LLM Wiki v2 layer on top of `~/wiki`.

Current architecture:
- Markdown pages remain the human-readable source of truth under `concepts/`, `entities/`, `comparisons/`, `queries/`, and `raw/`.
- `SCHEMA.md` now defines v2 fields: `status`, `lifecycle`, `confidence_score`, `last_confirmed`, `decay`, `supersedes`, `superseded_by`.
- Derived machine layers live under `facts/facts.jsonl`, `graph/entities.jsonl`, `graph/relations.jsonl`, and `state/layers.json`.
- Scripts: `scripts/wiki_v2_build.py` rebuilds derived indexes; `scripts/wiki_v2_query.py` does hybrid lexical/alias/graph/confidence search; `scripts/wiki_v2_lifecycle.py` reports stale/contested/low-confidence candidates; `scripts/wiki_query.py` is a compatibility wrapper to v2 query.
- `scripts/wiki_v2_semantic_embed.py` uses TencentDB-aligned SiliconFlow `Qwen/Qwen3-Embedding-4B` / 2560D true semantic embeddings, reading config from `~/.memory-tencentdb/memory-tdai/tdai-gateway.json` unless overridden.
- Key pages: `queries/llm-wiki-v2-operating-model.md`, `queries/wiki-v2-maintenance-playbook.md`, and `queries/wiki-v2-migration-report-2026-06-19.md`.

Operational rule: after any wiki write, run `python3 scripts/wiki_v2_build.py` then `python3 scripts/wiki_lint.py`; for search, prefer `python3 scripts/wiki_v2_query.py "<query>" --limit N` before reading pages.

## Task/knowledge loop

Preferred future loop:

1. Feishu task says what to do.
2. User completes or reports friction.
3. Update Feishu status if needed.
4. Update the relevant wiki page if the report changes learning state.
5. If weak points appear, create or adjust the next Feishu task.

This makes tasks an input to the knowledge system, not just a todo endpoint.
