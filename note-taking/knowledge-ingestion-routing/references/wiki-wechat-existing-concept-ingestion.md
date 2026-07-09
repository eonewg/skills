# WeChat article ingestion into an existing concept page

Use when a WeChat article adds evidence or an organizational example for a concept that already exists in the wiki, rather than creating a new standalone concept page.

## Pattern

1. Extract the article. For `mp.weixin.qq.com`, try the local extractor first; if it downloads/installs Camoufox and times out or stalls, switch to the mobile User-Agent fallback and save both `.html` and `.txt` under `~/.hermes/data/wechat-articles/_raw-html/`.
2. Search the wiki for the article title, URL slug, and likely concept terms. If an existing concept already covers the class, prefer `raw + patch existing pages` over creating a duplicate narrow page.
3. Preserve the full article as `raw/articles/<stable-slug>-2026.md` with source URL/title/author/published/ingested/sha256 frontmatter. It is fine to prepend an `the assistant 摘要`, but keep a full `## 原文` section.
4. Patch the main existing concept page with a short section that states what the article adds. Add the raw path to `sources:` deliberately; do not put sources in `tags:`.
5. Patch 1–2 related umbrella pages only when the article changes their operating model or adds a concrete example. Avoid over-linking every adjacent page.
6. Update `hot.md`, `log.md`, `.manifest.json`, and, if the page is important for future ingestion reliability, add a case to `queries/wiki_ingestion_eval_set.json`.
7. Run verification: `scripts/wiki_lint.py`, `scripts/wiki_v2_build.py`, `scripts/wiki_v2_source_dependencies.py`, `scripts/wiki_v2_ingestion_eval.py`, and a targeted `scripts/wiki_v2_query.py '<distinctive query>'`. The targeted query should retrieve the patched concept in top results.
8. Delete temporary deterministic ingestion scripts from the workspace after successful verification.

## Example from 2026-06-29

Article: WeChat `https://mp.weixin.qq.com/s/uhc7_-0Vm_cw9p17b9VyJA`, title repaired as `开启 Harness Engineering 探索之旅`.

Decision: do not create a new `harness-engineering-exploration` concept page because `concepts/ai-harness-engineering-practice.md` already existed and covered the class. Preserve raw, then patch:

- `concepts/ai-harness-engineering-practice.md` as the main page
- `concepts/agentic-engineering-operating-loop.md` for the P1–P6 organizational loop
- `concepts/agent-knowledge-engineering.md` for the knowledge-base-as-runtime layer
- `hot.md`, `log.md`, `.manifest.json`, and ingestion eval set

Target query used for verification: `Harness Engineering 研发全链路 工作环境 P1 P6`, expected top result `ai-harness-engineering-practice`.

## Example from 2026-07-09

Article: WeChat `https://mp.weixin.qq.com/s/VKiTUsqiVxHA70IyptVG6g`, title `一文读懂 Harness Engineering！`.

Decision: do not create a new `harness-engineering-compensation-surface` concept page because `concepts/ai-harness-engineering-practice.md`, `concepts/agentic-engineering-operating-loop.md`, and `concepts/agent-harness-evaluation-system.md` already covered the class. Preserve full raw as `raw/articles/harness-engineering-compensation-surface-2026.md`, then patch those three pages plus `hot.md`, `log.md`, `.manifest.json`, and `queries/wiki_ingestion_eval_set.json`.

Distinctive value extracted: “补偿面迁移” — each harness component encodes a hypothesis about what the current model cannot do; future runs should track what risk a layer reduces, what fixed tax it adds, and what evidence would justify removing it.

Target query used for verification: `Harness Engineering 补偿面迁移 Claude Code Team Mode KAIROS YOLO Hooks`. In this case the query correctly ranked multiple patched existing pages (`agent-harness-evaluation-system`, `agentic-engineering-operating-loop`, `ai-harness-engineering-practice`) in top results. For existing-concept ingests, the eval should allow any intended patched concept page in top results rather than requiring the main page to be rank 1 when the query spans several related concepts.

## Pitfalls

- Do not mistake garbled JavaScript metadata from the mobile-UA fallback for the real title/author. Repair title/author from the readable body when needed.
- Do not make a new concept page just because the source is high-signal. If the article is a new example of an existing concept, patch the existing concept and related umbrella pages.
- Source dependency scripts may print huge JSON. Verification can still be valid if exit code is 0, but user-facing report should summarize only counts and failures.
- For existing-concept ingests, targeted query verification should prove retrievability of the updated cluster, not force one specific patched page to outrank other canonical pages that legitimately match the distinctive query.
