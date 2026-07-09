# the user Wiki compiler-ops upgrade pattern

Use when the user asks to improve `~/wiki` itself after ingesting a high-signal knowledge-engineering / LLM Wiki / RAG article, or when an answer should become a more verifiable wiki operating-system capability rather than only a concept page.

## Trigger

Signals:
- the user asks “看看我们现有架构有没有优化的地方 / 可以” after a wiki/LLM Wiki article.
- The source argues for compiler-style knowledge management: source material -> structured pages -> relation graph -> retrieval -> lint/eval.
- A previous answer identified architectural gaps such as domain routing, source dependency tracking, answer-path explanations, or ingestion regression tests.

## Pattern

1. Preserve the source normally first: raw article + concept/query page + index/hot/log/manifest + build/lint/query verification.
2. If the user confirms the optimization, implement small deterministic scripts under `~/wiki/scripts/` rather than leaving the recommendation in prose.
3. Keep `.manifest.json` compact. Do not bloat each raw entry with impacted pages. Instead generate a rebuildable dependency artifact from formal-page `sources:`:
   - `scripts/wiki_v2_source_dependencies.py`
   - `state/source_dependencies.json`
   - `reports/source_dependencies.json`
4. For query usability, add a wrapper that explains the route instead of replacing the ranker:
   - `scripts/wiki_v2_answer_path.py`
   - Output shape: domain inference -> candidate pages -> why to read them -> read-detail rule.
   - Keep the original user query clean. Domain entries are explanatory routing hints; injecting all entry-page slugs into the query can swamp the actual intent and over-rank broad hub pages.
5. For ingestion reliability, add a small regression grader:
   - `scripts/wiki_v2_ingestion_eval.py`
   - cases in `queries/wiki_ingestion_eval_set.json`
   - verify raw exists, raw hash matches, source_url preserved, formal pages cite raw, index slugs appear exactly once, manifest raw exists, log mentions the slug, query top5 includes expected page.
6. Wire durable checks into the existing health chain:
   - `wiki_v2_build.py` should run source dependency generation.
   - `wiki_v2_weekly_health.py` should report source dependency missing count and ingestion eval failure count.
7. Update documentation pages after scripts land:
   - `SCHEMA.md`
   - `queries/llm-wiki-v2-operating-model.md`
   - the specific architecture-optimization query page if one exists
   - `hot.md`, `index.md`, `log.md`, `.manifest.json`
8. Run verification before reporting:
   - `python3 scripts/wiki_v2_build.py`
   - `python3 scripts/wiki_lint.py`
   - `python3 scripts/wiki_v2_source_dependencies.py --json`
   - `python3 scripts/wiki_v2_ingestion_eval.py --json`
   - one answer-path smoke query
   - one normal query smoke test
   - `python3 scripts/wiki_v2_weekly_health.py`

## Good final state

Healthy output should include:
- lint issue_count 0 and warning_count 0
- source dependency missing count 0
- ingestion eval failed 0
- weekly health query_eval_failures 0
- answer path routes the target architecture question to the intended domain and returns the new/updated concept/query pages near the top

## Pitfalls

- Do not turn every architecture suggestion into a new permanent daemon or cron. Prefer deterministic scripts and reports first.
- Do not duplicate dependency data inside `.manifest.json`; generate it from page frontmatter.
- Do not treat top-slug retrieval as enough for strategic questions. Use answer-path output to force “which domain, which pages, why these pages.”
- Do not capture transient extractor/browser failures as durable claims. Capture the successful fallback/verification pattern only when it generalizes.
