# WeChat literary / expression article light ingestion

Use this pattern for WeChat articles that are valuable as writing/literary素材 but do not justify a new standalone concept page.

## Trigger

- Source is a WeChat article, often CCTV 夜读 / literary essay / quotation-with-life-experience style.
- User explicitly says “归档” after the summary.
- Article adds reusable expression素材, not a new durable theory/framework.

## Pattern

1. Preserve the full extracted article as raw Markdown under `raw/articles/<english-slug>-2026.md`.
   - Include `source_url`, `source_title`, `source_author`, `published`, `ingested`, `sha256` frontmatter.
   - Add a short `## the assistant 摘要`, then `## 原文` containing the full article body.
2. Prefer patching an existing umbrella concept over creating a narrow page.
   - For literary/expression material, usually patch `concepts/literary-expression-life-experience.md`.
   - If the article is literary/expression素材 **and** clearly strengthens an existing relationship/communication/self-care concept, patch that second existing concept too rather than creating a new narrow page. Example: an article about “接住情绪 / 情绪价值” should preserve raw, patch `literary-expression-life-experience.md` for expression素材, and patch `intimate-relationship-model.md` for the operational relationship-response model.
   - Add the raw path to each formal page `sources:` list, not to `tags:`.
   - Add one compact section extracting the reusable writing principle / life-experience motif; for a second operational page, add a concise action model or response script, not a duplicate summary.
3. Update working/navigation layers.
   - Patch `hot.md` with a short “近期摄入” entry and add the raw path to its `sources:`.
   - Update `index.md` date only if no new formal page is created; do not add a duplicate index entry.
   - Append one compact `log.md` entry.
   - Add compact `.manifest.json` entry: `raw_files[path] = {sha256,last_seen,status}` and a short operation record.
4. Verify.
   - Run `python3 scripts/wiki_lint.py` and require `issue_count: 0`, `warning_count: 0`.
   - Run `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py` for routine derived-layer refresh.
   - Run a targeted `wiki_v2_query.py` using article keywords and expect the patched umbrella page to rank first.

## Example mapping

CCTV 夜读 “当古诗文照进现实，才发现李白是写实派” was better handled as:

- raw: `raw/articles/ancient-poetry-reality-realism-2026.md`
- formal patch: `concepts/literary-expression-life-experience.md`
- extracted principle: ancient poetry’s romance often comes from precise observation; life experience later reactivates classic lines.

## Pitfalls

- Do not create a new concept page for every literary WeChat article. If the value is素材/语感/母题, patch the umbrella.
- Search tools may miss Chinese terms in recently patched files, and may also miss newly inserted source paths even when the text is present. If verification search looks empty but the edit should exist, read the target file around the intended insertion before assuming the patch failed. Treat `read_file` evidence plus `wiki_lint.py` + `wiki_v2_query.py` as stronger verification than content search alone.
- Keep the user report short and explicitly name both layers: raw evidence path + patched formal page.