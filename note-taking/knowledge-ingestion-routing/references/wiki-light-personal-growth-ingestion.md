# Light Personal-Growth Article Ingestion

Use this reference for low/mid-signal personal growth, self-regulation, and motivational WeChat articles that are useful to the user's execution system but should not sprawl across the wiki.

## Pattern

1. Extract the full article with the local WeChat extractor and verify the saved Markdown is real article content.
2. Preserve the full article under `raw/articles/<stable-english-slug>-2026.md`.
   - Prepend a concise `the assistant 摘要`.
   - Keep the full body under `## 原文`.
   - Preserve source URL and extracted metadata when available.
3. Create at most one compact concept page if the article contributes a reusable loop or checklist.
   - Prefer a class-level concept like `negative-thought-defusion-loop.md`, not a page named after the article title.
   - Use existing schema tags only, typically `[method, productivity]` for self-regulation/action loops.
4. Patch only 1–2 relevant umbrella pages instead of scattering references widely.
   - Common destinations: `self-worth-and-action.md`, `personal-daily-dashboard.md`, `energy-boundary-maintenance-loop.md`, or `learning-system.md` depending on the concept.
5. Update `index.md`, `hot.md`, `log.md`, `.manifest.json`.
6. Run `scripts/wiki_lint.py`; if a strict raw hash mismatch appears, patch the raw frontmatter and manifest to the linter-reported actual hash, then rerun until `issue_count: 0` and `warning_count: 0`.

## Threshold

Archive lightly when the article provides a reusable move the user can apply later, e.g. a four-step defusion loop, anxiety reset, recovery checklist, or execution reframing. Skip if it is only inspirational prose, quotes, celebrity anecdotes, or newsletter filler with no durable action pattern.

## Output shape

Report concisely:
- article title and classification (`light ingestion`, `skip`, or `full coordinated ingestion`)
- raw file path
- concept/umbrella pages updated
- lint result
