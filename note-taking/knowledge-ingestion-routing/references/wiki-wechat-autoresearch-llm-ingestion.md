# WeChat AutoResearch / Agent-for-ML ingestion pattern

Use this when a WeChat article describes AutoResearch, Agent-for-ML, LLM fine-tuning automation, or skill-driven experiment loops.

## Routing

- Preserve full WeChat extraction as raw under `raw/articles/` with the assistant 摘要 + 原文.
- Prefer one durable concept page when the article introduces a reusable operating model, not merely a news item.
- Patch existing umbrella pages instead of creating many narrow pages. Likely umbrellas:
  - `agentic-engineering-operating-loop`
  - `agent-prompt-skill-runtime-architecture`
  - `skill-authoring-engineering`
  - `llm-training-data-governance`
  - optionally `agent-harness-evaluation-system`, `loop-engineering-practical-manual`, `agentic-rl-infrastructure`

## What to extract

- The reusable loop structure: diagnosis → experiment design → automated validation.
- What belongs in `SKILL.md`: parameter priorities, locked variables, platform APIs, log/metric extraction, Debug table, and human decision gates.
- Machine-verifiable signals: eval loss, BLEU/ROUGE/F1/NDCG, stderr failures, task IDs, experiment ledger rows.
- Platform/runtime gotchas that are durable enough to preserve, e.g. framework checkpoint incompatibilities, model inference modes that contaminate metrics, endpoint/queue contracts.

## Concept-page angle

Frame the page as "skill-driven experiment control plane" rather than generic AutoML. The valuable distinction is that the Agent does not blindly tune; it operates inside a harness with locked parameters, state, automatic metrics, and human gates.

## Verification pattern

After writing raw + concept + umbrella patches:

1. Update `index.md`, `hot.md`, `log.md`, `.manifest.json`.
2. Add a targeted case to `queries/wiki_ingestion_eval_set.json` with:
   - source URL
   - raw path
   - new concept page
   - patched umbrella pages
   - query terms including article title, Agent, Skill, model/runtime gotchas, and metrics
3. Run:
   - `python3 scripts/wiki_lint.py`
   - `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py`
   - `python3 scripts/wiki_v2_query.py '<target query>'`
   - `python3 scripts/wiki_v2_ingestion_eval.py --case <case-name>`
4. Confirm the new concept is top-ranked for its target query and the targeted ingestion eval passes.

## Reporting

Keep final report short: raw path, concept path, patched umbrellas, and verification results. Do not include Markdown tables in Feishu.