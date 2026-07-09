# WeChat article → existing concept light ingestion

Use this when a WeChat article is valuable but does not deserve a new narrow concept page because an existing umbrella/concept already covers the class.

## Pattern

1. Extract with the local WeChat extractor first:
   - `~/.hermes/scripts/wechat_article_to_md.sh '<URL>'`
   - Treat `Skipping (already exists)` as successful extraction; read the saved Markdown under `~/.hermes/data/wechat-articles/`.
2. Search the wiki for title, author, core terms, and likely slug. If an existing concept is the right home, choose **raw + patch existing concept**, not a duplicate narrow page.
3. Preserve full raw article under `raw/articles/<stable-english-slug>-2026.md`:
   - Include source URL, title, author, published date, ingested date.
   - Add a short `the assistant 摘要` before `## 原文`.
   - Keep the full extracted article body under `## 原文`.
   - Compute `sha256` over the final body after frontmatter, using the same policy as `wiki_lint.py`; add `hash_policy: final-body-excluding-wiki-frontmatter` for strict new raws.
4. Patch the existing concept deliberately:
   - Add the raw path to `sources:`.
   - Update `updated` and `last_confirmed`.
   - Add 1–3 reusable sections or bullets, anchored with `^[raw/articles/...md]`.
   - If you expand a checklist/template, update surrounding prose so counts stay true (e.g. do not leave “先写三行” after turning it into six lines).
5. Update `hot.md`, `log.md`, and `.manifest.json`.
6. Rebuild and verify:
   - `python3 scripts/wiki_lint.py` must report `issue_count: 0` and `warning_count: 0`.
   - `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py` for routine derived-layer refresh.
   - Query with terms that appear in the formal page, not only an exact quote from raw. Exact-quote queries may rank lower when the phrase lives only in raw/full text; a concept-term query should surface the patched concept at or near #1.
   - Run ingestion regression if this ingest touches shared machinery or recent eval cases: `python3 scripts/wiki_v2_ingestion_eval.py`.
7. Clean temporary deterministic scripts after successful verification; leave only durable wiki files and backups.

## When to create a new concept instead

Create a new concept when the article introduces a reusable frame that is not already covered, will be queried independently later, or would overload the existing concept. Otherwise, prefer this light ingestion pattern.
