# WeChat personal-growth / low-valley advantage light ingestion

Use this pattern for WeChat personal-growth articles that are motivational in tone but contain a reusable execution/review loop worth preserving.

## Trigger

- Source is a WeChat article, often CCTV 夜读 / 人民日报夜读 / similar public-account essay.
- User explicitly says “归档” after the initial summary.
- Article is not dense enough for a standalone concept page, but contributes a reusable lens for the user's exam/execution/self-worth system.
- Common motifs: low谷, failure, self-worth, slow growth, action evidence, advantage perspective, reflection after setbacks.

## Pattern

1. Preserve the full extracted article as raw Markdown under `raw/articles/<english-slug>-2026.md`.
   - Frontmatter: `source_url`, `source_title`, `source_author`, `published`, `ingested`, `sha256`.
   - Body: `## the assistant 摘要`, then `## 原文` with the full article body.
2. Prefer patching existing operational concept pages over creating a narrow new concept page.
   - Failure / self-judgment / low energy → patch `concepts/self-worth-and-action.md`.
   - Advantage perspective / strengths after setbacks → patch `concepts/advantage-based-growth.md`.
   - Daily action / exam execution → patch `concepts/personal-daily-dashboard.md` or `concepts/kaoyan-daily-execution-system.md` only if the article changes a concrete daily action.
3. Extract the operational loop, not the motivational prose.
   - Example from “低谷不是用来熬的，是用来向内看清自己”: convert the article to “表层结果 → 中层行为 → 底层认知” plus “避坑指南 + 优势清单”.
   - Tie the model to the user's current context: a failed task, wrong problem, or low-energy day should not become a personality verdict; it should leave one rule and one advantage clue.
4. Update working/navigation layers.
   - Patch `hot.md` with a short “近期摄入” entry.
   - Update `index.md` date only if no new formal page is created.
   - Append one compact `log.md` entry.
   - Add `.manifest.json` entry: `raw_files[path] = {sha256,last_seen,status}` plus one operation.
5. Verify.
   - Run `python3 scripts/wiki_lint.py` and require `issue_count: 0`, `warning_count: 0`.
   - Run `WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py` for routine derived-layer refresh.
   - Run a targeted `wiki_v2_query.py` using article terms and expect the patched operational concept(s) to rank at the top.

## Pitfalls

- Do not create one concept page per motivational essay. If the durable value is a small review/action loop, patch the umbrella pages.
- Do not keep the article's inspirational framing as-is. Translate it into the user's actionable language: “one rule, one evidence, one next action”.
- If writing a deterministic temporary script for multi-file edits, delete it after successful lint/build/query verification.
