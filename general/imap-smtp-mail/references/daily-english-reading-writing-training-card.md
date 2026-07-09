# Daily English email: reading-writing training-card refinement

Session-derived refinement for the user's recurring daily English email.

## Trigger

Use this when composing, manually backfilling, resending, or revising the user's daily English study email.

## Core positioning

Do **not** turn the email into a full `teach` course system. Keep it as a lightweight email handout / daily training card.

The email should support future systematic study, but it should remain readable in email:

- small daily input
- spaced repetition callbacks
- one long-sentence reading drill
- one reading-writing micro-skill
- reusable expressions and sentence patterns
- short active recall

The user explicitly preferred not to build a separate teach-like system for this workflow after discussion.

## Updated section logic

Keep the fixed 8-section structure, but make it more reading-to-writing oriented:

1. `一、今日高级英语表达`
   - 6-8 expressions, including 2 review callbacks.
   - Each item should include 中文解释, English example, 中文理解, and `适用场景`.

2. `二、今日高级句型`
   - 3-4 reusable patterns.
   - Add `句型功能` such as 开头点题, 因果, 让步, 评价, 段末收束.

3. `三、阅读长难句拆解`
   - Include 主干 / 修饰 / 逻辑关系 / 中文理解 / 可迁移写法.
   - Add `可能考点/命题陷阱`: e.g. 作者态度, 转折后重点, 例子支撑观点, 熟词僻义, 同义改写.

4. `四、阅读与写作微技能`
   - Replace the old `实用写作技巧` section.
   - Keep it compact: 2-3 techniques connecting 真题阅读 and writing output.
   - Good topics: 定位句→同义改写, 例证题看观点不看例子, 态度词识别, 错因分类, 把阅读句改成作文功能句.

5. `五、今日高级连接词`
   - Group by function.
   - Add `适用位置` for each group.
   - No tables, horizontal rules, row borders, or `.data-table` / `.table-wrap`.

6. `六、自然高级替换`
   - Use `普通表达 → 高级表达` plus `适用位置` and example.
   - Prefer replacements useful for reading-to-writing transfer: 同义改写, 态度评价, 原因机制, 主旨概括.
   - Keep separate from section 05.

7. `七、今日可背高级段落`
   - 120-180 words.
   - Reuse at least 3 expressions/patterns including at least one review callback.
   - Add 2-3 `可拆用句` with where each can be reused in作文.

8. `八、3 分钟主动回忆`
   - Do not make all three tasks simple translation.
   - Use: one 中译英, one 阅读逻辑判断, one 同义改写/普通句升级.

## Visual rule learned from user correction

The user said sections 05 and 06 had too many horizontal lines and looked messy. This is a first-class formatting preference.

For sections 05/06 and repeated list items:

- no tables
- no row-by-row border lines
- no `<hr>`
- no `border-bottom`
- no `.table-wrap` / `.data-table`
- no repeated left vertical rules

Use typography and whitespace only: bold labels, warm gray explanatory text, serif italic examples, and compact spacing.

## Manual resend/backfill notes

When the user asks to resend today or backfill yesterday:

- Do not rerun the recurring cron blindly.
- Determine the fixed Asia/Shanghai target date first.
- If artifacts exist, patch or regenerate `*-resend.*` files rather than overwriting the original cron artifacts.
- If no target-date artifacts exist, create a fixed-date manual email from scratch under `~/.hermes/out/daily-english-YYYY-MM-DD-resend.{txt,html}` using the current spec.
- Preview without `--approve`, run the verifier, then send with `--approve` and save `*-resend-send.json`.

## Verification expectations

Before sending, verify at least:

- styled HTML present, not generated plaintext paragraphs
- warm palette and `max-width` around 760-820px
- `class="section"` and `class="hero"` present
- no `.data-table` / `.table-wrap`
- no `border-bottom` / `<hr>` separators
- no `border-left` repeated list styling

Use `scripts/verify_daily_english_html.py` for the deterministic checks and add manual grep/search checks if changing layout rules.
