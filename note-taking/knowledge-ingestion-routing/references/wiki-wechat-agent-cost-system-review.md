# WeChat Agent-cost article + system-improvement review pattern

Use when the user sends a high-signal WeChat article about Agent cost, token efficiency, context management, model routing, or Harness engineering, then asks what it implies for the current the assistant/Hermes/wiki system.

## Pattern

1. Extract with the local WeChat extractor and preserve full raw under `~/wiki/raw/articles/<stable-slug>-2026.md`.
2. Prefer patching existing umbrella concepts over creating a duplicate narrow concept page. Typical targets:
   - `concepts/ai-coding-agent-token-cost-control.md`
   - `concepts/agent-cost-economics.md`
   - `concepts/agent-context-management.md`
   - `concepts/agentic-engineering-operating-loop.md`
   - optionally `concepts/agent-memory-context-offloading.md` or `concepts/agent-context-compaction-strategies.md` when the source changes compaction/offload mechanics.
3. If the user also asks “what can our system improve?”, create a separate `queries/<topic>-review-YYYY-MM-DD.md` page rather than burying operational recommendations only in chat. Treat it as an episodic review with `sources: [raw/articles/...]`, and patch `index.md`, `hot.md`, and `log.md`.
4. Ground recommendations in current system evidence where available, but do not turn transient failures into permanent rules. Capture durable fixes or patterns, such as:
   - use deterministic pre-collection scripts for recurring cron jobs with stable input selection;
   - keep main-agent context as decision state, not raw tool noise;
   - make subagents return conclusions, evidence paths, risks, and next-decision needs, not full process dumps;
   - pin auxiliary routes after probing instead of relying on broad `auto` defaults;
   - split broad default tool surfaces only after confirming user-facing capability tradeoffs.
5. Verification sequence:
   - `python3 scripts/wiki_lint.py`
   - `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py`
   - targeted ingestion eval for the raw + patched concepts, if a case was added
   - targeted `wiki_v2_query.py` for the article concepts
   - targeted `wiki_v2_query.py` for the new operational review page if one was created
6. If a brand-new formal query/review page under-ranks after a skip-semantic build, run a full `python3 scripts/wiki_v2_build.py`; new pages may need fresh semantic embeddings before query verification is meaningful.
7. Delete temporary deterministic ingest/review scripts from the workspace after verification.

## Reporting

Keep the user-facing report short:
- raw path;
- patched concept pages;
- new review/query page if created;
- verification result (`lint issue_count/warning_count`, build, eval/query);
- 2–5 prioritized improvements, with clear “do now / confirm before changing” boundaries.

## Pitfalls

- Do not create a new narrow concept for every token-cost article when existing cost/context/Harness pages already cover the class.
- Do not change Feishu/default toolsets or model defaults while merely evaluating. Tool-surface slimming affects daily capability and needs explicit user confirmation.
- Do not save transient provider errors as durable facts. If a known provider quirk has a stable fix, patch the provider/model-routing skill instead.
