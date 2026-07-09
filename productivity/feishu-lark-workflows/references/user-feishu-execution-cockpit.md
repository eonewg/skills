# the user Feishu execution cockpit patterns

Use this when the user asks to make Feishu more useful beyond tasks, especially for exam prep operations.

## Positioning

Feishu should be the execution/display/collaboration layer, not the full source-of-truth knowledge base.

- Local wiki: durable raw/concept knowledge, lintable and agent-friendly.
- Feishu Docs: readable weekly reviews, stage reports, operating manuals.
- Feishu Base: lightweight progress/status tracking.
- Feishu Tasks: concrete daily actions.
- Feishu Wiki: optional portal/index layer, not a replacement for local wiki.

## Weekly exam review doc

Create a Feishu cloud doc from `templates/the user-weekly-exam-review.md` when the user asks for a weekly review or review-template doc.

Recommended command shape:

```bash
cd ~/.hermes/skills/productivity/feishu-lark-workflows
lark-cli docs +create \
  --api-version v2 \
  --doc-format markdown \
  --parent-position my_library \
  --content @templates/the user-weekly-exam-review.md
```

Use Markdown here because the template is simple, stable, and meant to be edited by the user. Keep the document natural and airy; do not turn every section into a visual card.

## Exam progress Base schema

For a minimal useful 考研进度表, create one Base named `考研进度表` with one table `主线进度`.

Recommended fields:

```json
[
  {"name":"模块","type":"text","description":"章节/模块名，作为主字段"},
  {"name":"科目","type":"select","multiple":false,"options":[{"name":"数学","hue":"Blue"},{"name":"408","hue":"Purple"},{"name":"英语","hue":"Green"},{"name":"政治","hue":"Orange"}]},
  {"name":"阶段","type":"select","multiple":false,"options":[{"name":"听课","hue":"Blue"},{"name":"做题","hue":"Orange"},{"name":"复盘","hue":"Purple"},{"name":"错题","hue":"Red"},{"name":"模拟","hue":"Green"}]},
  {"name":"状态","type":"select","multiple":false,"options":[{"name":"未开始","hue":"Gray"},{"name":"进行中","hue":"Blue"},{"name":"完成","hue":"Green"},{"name":"返工","hue":"Red"},{"name":"滚动","hue":"Orange"}]},
  {"name":"优先级","type":"select","multiple":false,"options":[{"name":"P0","hue":"Red"},{"name":"P1","hue":"Orange"},{"name":"P2","hue":"Blue"},{"name":"P3","hue":"Gray"}]},
  {"name":"完成度","type":"number","style":{"type":"progress","percentage":true,"color":"Blue"}},
  {"name":"当前动作","type":"text","description":"下一步具体动作，不写空泛目标"},
  {"name":"卡点","type":"text","description":"当前阻塞点/薄弱点"},
  {"name":"截止时间","type":"datetime","style":{"format":"yyyy-MM-dd HH:mm"}},
  {"name":"关联链接","type":"text","style":{"type":"url"}},
  {"name":"备注","type":"text"}
]
```

Recommended command shape:

```bash
lark-cli base +base-create \
  --as user \
  --name "考研进度表" \
  --time-zone Asia/Shanghai \
  --table-name "主线进度" \
  --fields @base_fields.json
```

After creation:

1. Read `+table-list` to capture the real table ID.
2. Read `+field-list` before writing records.
3. Seed only a few high-signal records from current tasks; avoid turning progress tracking into填表地狱.
4. Create simple grid view entry points if useful, e.g. `按优先级推进` and `数学与408主线`; do not over-engineer filters/sorts before the user has used the table.

## Pitfalls

- Do not create a second full knowledge base in Feishu. Keep Feishu as the cockpit layer.
- Do not use Calendar if the user explicitly says “日历先不用”.
- Do not make the review doc over-designed; the user prefers natural sections with breathing room, not every section as a card.
- When verifying Base writes, `record-list --format json` may return rows under `data.data` with `data.record_id_list`, not `data.items`.
