# WeChat Harness self-improvement / Lilian Weng article ingestion

Use when ingesting WeChat articles that compile, translate, or summarize a primary Harness / recursive self-improvement / Agent self-improvement source, especially Lilian Weng-style technical essays.

## Decision pattern

- Treat these as high-signal Agent systems material.
- Preserve both layers when available:
  1. the WeChat compilation/translation/raw article, because it is the source the user shared and may contain Chinese framing;
  2. the primary source linked inside the article, because it is the authoritative technical reference.
- Prefer patching existing Harness/Agent pages rather than creating a narrow one-article concept page when pages already exist, such as:
  - `concepts/ai-harness-engineering-practice.md`
  - `concepts/agentic-engineering-operating-loop.md`
  - `concepts/agent-knowledge-engineering.md`
  - `concepts/agent-harness-evaluation-system.md`
  - `concepts/agent-context-management.md`
- If the user explicitly asks whether it is useful for “our system / the assistant / Hermes”, create a durable `queries/` page with the system applicability judgment, not just a chat answer.

## What to extract

For Harness self-improvement sources, extract at least:

- Harness as deployment/runtime system around the base model: workflow, tools, context, state, artifacts, evals, permissions.
- File system as persistent memory: long-horizon state, logs, diffs, raw evidence, recovery paths should be files/records, not chat-only context.
- Sub-agent and backend jobs: parallelism must be explicit, inspectable, and merged back through evidence paths.
- Context engineering: do not rewrite a giant prompt every time; maintain structured context manuals/skills with deterministic merge, dedupe, and read-back.
- Self-Harness / self-improvement boundary: failure traces → weakness clusters → candidate harness changes → held-in and held-out regression validation → accept/reject record.
- Safety boundary: permission controls, verifiers, user preferences, and high-impact side effects must stay outside the unconstrained self-modification loop.

## Good the user/Hermes synthesis

A useful query-page conclusion usually looks like:

> This is useful not because we should swap to a stronger model, but because the system should move from model-layering to harness-layering. Existing pieces such as toolsets, skills, memory modules, wiki raw/concept/manifest/log, cron, delegation, lint/build/query, and read-back verification are harness parts; the missing loop is failure mode → candidate change → regression validation → accept/reject record.

Recommended priorities:

1. Add mini harness cases to high-frequency workflows first: WeChat/wiki ingest, weekly English digest, Feishu task updates, skill updates.
2. Add a rejected-change buffer or query-page record for rejected/over-designed harness changes.
3. Keep high-impact permissions, verifier scripts, hot memory/user profile, and cron automation frequency behind user confirmation or external validation.
4. Do not create self-improvement cron jobs until there is a grader, held-out validation, and review path.

## Verification recipe

After raw + patches + query page:

```bash
python3 scripts/wiki_lint.py
WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py
python3 scripts/wiki_v2_source_dependencies.py
python3 scripts/wiki_v2_ingestion_eval.py --case <case-name> --json
python3 scripts/wiki_v2_query.py '<distinctive source + concept terms>' --limit 5 --json --no-log
```

Add an ingestion eval case when the article materially strengthens Harness pages. The expected top results may include broad canonical Harness pages above the new query page; that is acceptable if the patched pages and query page appear in top results and the eval case passes.

## Pitfalls

- Do not archive only the Chinese WeChat compilation when it links to a primary technical source; preserve the primary source too when accessible.
- Do not turn a “对我们系统有没有用” answer into chat-only advice. Preserve it as a `queries/` page if it contains durable operating decisions.
- Do not recommend direct Hermes core/toolset changes just because a Harness source advocates self-improvement. Keep small reversible steps and verifier boundaries first.
- Do not encode transient setup/tool failures as durable rules. Capture the reliable workflow and verification pattern instead.