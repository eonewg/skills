# WeChat 人生周报 / quote-curation issue → cognitive-frame light ingestion

Use this when a recurring WeChat quote/newsletter issue (especially 李继刚「人生周报」) is mixed-signal overall, but contains one reusable cognitive frame worth future retrieval.

## Pattern

1. Treat the issue as **light ingestion**, not a full coordinated ingest.
2. Preserve the complete extracted article under `raw/articles/<life-weekly-topic>-2026.md` with:
   - source URL, title, author, published/extracted date
   - concise `the assistant 摘要`
   - full article body under `## 原文`
   - strict `hash_policy: final-body-excluding-wiki-frontmatter` when adding a new raw file
3. Before creating anything, search for title, issue number, topic terms, and likely existing umbrella pages.
4. If the issue introduces a reusable frame that users will search directly, create **one compact class-level concept page**, not a page that merely mirrors the newsletter title.
   - Example: `人生周报v080: Bayes` should become `bayesian-thinking-frame.md`, not `life-weekly-v080-bayes.md` as the formal page.
   - Keep the raw filename issue-specific; keep the formal page concept-specific.
5. Patch 1–2 existing umbrellas where the frame changes an existing model.
   - A Bayes/update frame can patch `reference-frame-cognition.md`.
   - A prompt/skill assumption-refresh idea can patch `skill-self-evolution-engineering.md`.
6. Update `index.md`, `hot.md`, `log.md`, `.manifest.json`.
7. Verify with:
   - `python3 scripts/wiki_lint.py` → expect `issue_count: 0`, `warning_count: 0`
   - `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py`
   - `python3 scripts/wiki_v2_query.py '<distinctive concept terms>'`

## Query verification nuance

For a new narrow concept patched into a broader umbrella, it is acceptable if the umbrella ranks above the new page, as long as both appear high and the new page is directly retrievable with distinctive terms. Example query: `贝叶斯思维取景框 类别 先验 似然比 后验 日常判断` may rank `reference-frame-cognition` above `bayesian-thinking-frame` because the umbrella was patched; this still proves the retrieval chain is healthy.

## Decision threshold

Create a compact concept only when the issue contains a reusable operational frame, such as:
- a decision/update model (`先验 → 新信息 → 似然比 → 后验`)
- a durable learning/knowledge-system frame
- a skill/prompt/harness maintenance frame

If the issue is only good sentences, literary flavor, or loose inspiration, preserve raw and patch an existing literary/expression or personal-growth umbrella instead of creating a new concept.
