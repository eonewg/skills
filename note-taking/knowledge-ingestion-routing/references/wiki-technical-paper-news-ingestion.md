# Technical paper + news report wiki ingestion

Use this when the user explicitly asks to archive a newly released AI/model/infra item and the available sources include a primary paper/repo/model card plus one or more news reports.

## Pattern

1. Search exact title/keyword and identify the primary source first: paper PDF, official GitHub repo, model card/API docs, release note.
2. Preserve at least two raw layers when available:
   - primary source raw: extracted paper text / repo README / official release
   - readable article raw: news/report summary with publication metadata
3. Create one durable concept/entity page rather than many narrow pages.
4. Patch existing umbrella/entity pages that the item changes, such as model entity, inference engine, cost economics, research track, or agent infra pages.
5. Update `index.md`, `hot.md`, `log.md`, and `.manifest.json` consistently.
6. Run verification:
   - `python3 scripts/wiki_lint.py`
   - `python3 scripts/wiki_v2_build.py`
   - `python3 scripts/wiki_v2_query.py '<topic query>' --limit 5`
   - optional ingestion eval if the repo has a relevant eval set
7. If lint reports raw hash mismatch for newly written raw files, trust the linter's actual hash and patch both raw frontmatter and `.manifest.json`, then rerun lint.
8. Clean temporary extraction files after verification.

## PDF extraction notes

- If `pdftotext` is missing but Python has `pdfminer`, use `pdfminer.high_level.extract_text` to extract PDF text locally.
- Do not record the missing binary as a durable failure; the reusable lesson is the fallback extraction path.

## Interpretation guardrails

- Distinguish “new model capability” from “serving/inference optimization.” Many releases attach a decoding module or runtime layer to an existing model.
- Treat dramatic high-SLA throughput ratios cautiously: they may mean the baseline is near an operational cliff, not that every workload gets that multiplier.
- For third-party news claims such as “deployed to Qwen/Gemma,” verify against the paper/repo. Often the precise claim is offline evaluation or released checkpoints, while production deployment only applies to the vendor's own service.

## Worked example summary: DSpark, 2026-06-28

For DeepSeek / PKU DSpark:
- raw paper: `raw/articles/dspark-paper-2026.md`
- raw report: `raw/articles/dspark-cls-report-2026-06-28.md`
- concept: `concepts/dspark-speculative-decoding.md`
- patched: `deepseek-v4`, `llm-inference-engine-vllm`, `agent-cost-economics`, `deep-learning-research-track`, `hot`, `index`, `log`, `.manifest.json`
- verified with lint (`issue_count: 0`, `warning_count: 0`), v2 build, and v2 query returning the new concept as top result.
