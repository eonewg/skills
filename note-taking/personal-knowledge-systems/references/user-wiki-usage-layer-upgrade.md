# the user wiki usage-layer upgrade pattern

Use this when the user asks to make the local filesystem wiki more directly usable, operational, queryable, or agent-friendly rather than merely ingesting another source.

## Trigger examples

- “一次性把有必要的都搞定” after discussing wiki/system improvements.
- “让这个知识库以后能用起来 / 能回答我今天该干啥”.
- “把任务和 wiki 接起来”.
- A prior roadmap/query page says the wiki needs an entry layer, routing layer, or verification layer.

## Target outcome

Upgrade the wiki from page storage to a daily operating backend:

1. Natural-question entry page under `queries/`, e.g. `queries/ask-wiki-playbook.md`.
   - Map common user questions to default wiki pages and output shapes.
   - Prefer Chinese natural-language route tables over abstract taxonomy.
2. Task-to-wiki routing page under `queries/`, e.g. `queries/task-wiki-routing.md`.
   - Map Feishu task keywords to study pages, execution loops, and optional completion-time wiki updates.
   - Keep the rule: task completion alone is not wiki-worthy; reusable learning feedback is.
3. Add usage sections to high-traffic core pages:
   - `## 什么时候用这页`
   - `## 最小动作`
   This makes pages callable by future agents and prevents rereading long theory when a small action is enough.
4. Add lightweight scripts under the wiki `scripts/` directory when useful:
   - `wiki_query.py`: keyword search across `concepts/`, `entities/`, `comparisons/`, `queries/`, plus `index.md`/`hot.md`; include alias expansion for Chinese task keywords like 张宇、408、拖延、英语、wiki.
   - `wiki_lint.py`: check frontmatter, tags, source paths, wikilinks, index inclusion, and raw hash warnings.
5. Update `index.md`, `hot.md`, `.manifest.json`, and `log.md`.
6. Run smoke tests and a full lint before reporting.

## Verification standard

Before final response, verify all of the following programmatically where possible:

- New `queries/` pages exist and have frontmatter.
- New scripts exist and run.
- `index.md` declares the same formal-page count as the actual count.
- New pages appear in `index.md` exactly once.
- Core pages contain both `## 什么时候用这页` and `## 最小动作`.
- `wiki_lint.py` reports `issue_count = 0`.
- Query smoke tests route correctly, e.g.:
  - `拖延` returns `personal-daily-dashboard` or `self-worth-and-action`.
  - `张宇第十一讲课后题` returns `zhangyu-math-learning-track`.
  - `408 计组` returns `cs408-prep` or `wangdao-computer-organization`.
- `log.md` and `.manifest.json` contain the upgrade operation.

## Pitfalls

- Do not create a new narrow skill for a single wiki upgrade; this belongs under the personal knowledge systems umbrella.
- Do not only add pages. If the wiki needs to be used by agents, add routing, minimal-action cues, and verification.
- Do not treat legacy raw hash mismatches as hard failures if they come from older hash policies. Report them as warnings unless the file opts into a strict current hash policy.
- Do not write task completions into wiki as a diary. Only write reusable learning state, weak points, route changes, or operating-model decisions.
