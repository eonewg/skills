# Coordinated WeChat → Wiki Ingestion Notes

Use this reference when a WeChat article is high-signal enough to affect multiple wiki pages, especially AI/Agent/model technical reports.

## Pattern

1. Extract with local WeChat extractor and verify the saved markdown is real article content.
2. Preserve full article as `raw/articles/<slug>-2026.md` with concise `the assistant 摘要` plus `## 原文`.
3. Create **one** class-level concept/entity page for the article's durable topic.
   - Model/report article → `entities/<model-or-suite>.md` when it describes a concrete model family/tool suite.
   - Cross-cutting methodology → `concepts/<frame>.md` when it introduces a reusable idea.
4. Patch existing umbrella pages rather than creating many narrow pages.
5. Update `index.md`, `hot.md`, `log.md`, `.manifest.json`.
6. Run `scripts/wiki_lint.py`; fix until `issue_count: 0` and `warning_count: 0`.

## Practical pitfalls

- When computing raw `sha256`, `wiki_lint.py` hashes the body returned by its frontmatter parser, which includes the blank line immediately after the closing `---`. If the linter reports a mismatch, patch the raw frontmatter and `.manifest.json` to the linter's actual hash and re-run.
- For multi-file edits, a short Python script is less error-prone than manual patches because it can update frontmatter `sources`, index count, hot/log, and manifest in one pass.
- If inline script execution is unavailable in the current run context, write a temporary script under the workspace, run it, lint, then remove the script. Capture the retry pattern, not the transient tool state.

## Session examples

- Ling / Ring 2.6 report: created `entities/ling-ring-2-6.md`; patched Agentic RL, attention compression, Agent cost economics, deep learning track.
- Qwen-Robot Suite report: created `entities/qwen-robot-suite.md`; patched world models, state-aware runtime, objective-driven AI, deep learning track.
