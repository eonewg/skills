# WeChat product-review / office-Agent case ingestion

Use this pattern when the user sends a WeChat article that is a product review or productized-Agent case study, and then asks to archive it plus identify how it fits his own workflows.

## When to use

- The source is a WeChat article reviewing a tool/product rather than a primary technical paper.
- The durable value is not every benchmark claim, but the product pattern and implications for the user's system.
- The article intersects existing AI/Agent/productivity concepts such as office Agent, OpenClaw, connector ecosystem, skills, memory, scheduling, sandboxing, or task execution.

## Preferred archive shape

1. Preserve the full extracted WeChat Markdown as raw article, including source URL, title, author/date, images, and an the assistant summary at the top.
2. Create one entity page for the product only when it is a named tool likely to recur (e.g. WorkBuddy).
3. Patch 2–4 existing concept/comparison pages instead of creating many narrow pages. Good targets include:
   - `agent-era-work-paradigm`
   - `codex-office-agent-accessibility`
   - OpenClaw/Hermes comparisons when the article discusses OpenClaw lineage or adoption barriers
   - security/cost/knowledge-engineering pages when the article adds concrete product evidence
4. Update `hot.md`, `index.md`, `log.md`, `.manifest.json`.
5. Run `scripts/wiki_lint.py`, then `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py`, then query verification.

## User-facing synthesis after archive

After reporting paths and verification, add a short “what is suitable for the user” section. Prioritize practical workflow fit over product hype:

- Feishu task/study-status watching: reminders + drafts, not automatic commitments.
- Link/article/video ingestion: send link → summarize → user says archive → raw + formal + lint/query.
- Exam-prep material organization: agent organizes materials and wrong-reason categories, the user still does problems and verification.
- AI/Agent content idea pool: collect candidates, classify signal level, then archive only the useful ones.
- HTML/demo artifact prototyping: turn fuzzy workflow ideas into visible artifacts.

## Boundaries to preserve

- Do not present a product review as proof of model capability; distinguish author claims from verified system evidence.
- Do not recommend high-side-effect uses such as automatic posting, automatic relationship replies, trading decisions, deletion, or unsupervised multi-file long tasks without Plan/approval/read-back verification.
- Do not create a new concept page for every product feature. The durable knowledge is usually the productization pattern: low-friction entry, explicit modes, connectors, skill ecosystem, memory, scheduling, sandboxing, and verification boundaries.
