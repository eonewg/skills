# Recurring study-email formatting pattern

Use this when a user wants a scheduled educational email (for example daily English writing practice) and cares about a very specific presentation format.

## Why save a format explicitly

In-session, a user corrected a generic English-learning email into a much stricter structure:
- write today's date clearly at the very top
- `今日高级表达`
- numbered expressions
- each entry must include meaning, usage note when helpful, `Example:`, one English sentence, and one Chinese translation
- `今日推荐句型`
- `写作技巧一/二/三/四`
- `今日可背段落`

The lesson is broader than this one email: **for recurring study emails, do not rely on a vague 'make it practical' instruction. Encode the exact section structure in the automation prompt or a template file, otherwise the format will drift over time.**

## Recommended cron/prompt pattern

When creating the scheduled job, spell out:
1. required title/section names exactly
2. required order of sections
3. required fields inside each section
4. language split expectations (e.g. Chinese explanations, English examples)
5. freshness requirement (avoid obvious repetition)

## Reusable outline

```text
<Date>

今日高级表达
1. <expression>
含义：<Chinese explanation>
<short usage/register note if needed>
Example:
<English example sentence>
<Chinese translation>

...

今日推荐句型
<pattern>
含义：...
<why it is useful>
Example:
...
可以套用成：
...

写作技巧一：...
写作技巧二：...
写作技巧三：...
写作技巧四：...

今日可背段落
<English paragraph>
<Chinese translation>
```

## Claude-like teach-style refinement for the user's English study mail

A later correction clarified the desired feel again: the recurring English email should inherit the same **Claude-like warm editorial style** as the teach HTML lessons, not the older colorful newsletter/micro-magazine look. Preserve the familiar sections, but design the message with:
- warm editorial palette: cream canvas `#faf9f5`, content surface `#fffdf8`, subtle block background `#efe9de`, near-black text `#141413`, warm gray body `#3d3d3a`, muted support text `#6c6a64`, sparse coral accent `#cc785c`
- column/section feel: headings should feel like recurring lesson columns, not exam-bank labels; use plain coral section numbers like `01 —`, not colored badges
- serif title / display heading, clean sans body, Georgia/serif allowed for polished English paragraph blocks
- visual rhythm and whitespace: fewer visual containers, more typographic hierarchy; do not overfill the screen
- **wide mobile reading area**: do not wrap all content in one big centered card. Keep side whitespace minimal on phone screenshots, roughly 8-12px, so English sentences span most of the screen width
- **flat editorial sections**: use header + independent section blocks/separators; avoid nested cards inside a giant card, because every border/padding layer makes lines too short
- **compact mobile padding**: body margin 0, outer wrapper padding about 8-12px, section padding about 14-18px; max-width only for desktop, around 760-820px
- use left coral rules, subtle borders, transparent tables, warm ink emphasis, and typographic contrast instead of card piles, gradients, heavy shadow, or high-saturation blue/green/purple/red highlights
- English as the main texture, Chinese as concise support; explanations should not drown the English
- practical but polished expressions: exam-usable without sounding like stale templates
- an end product: the final `今日可背段落` should be a compact, finished paragraph that reuses or echoes the day's expression/sentence pattern

Default content depth for this user, after explicit correction on 2026-05-13 and the 2026-06-22 content audit:
- The user does **not** want an over-compressed 2-expression micro card. They want a richer study handout/magazine hybrid like the 2026-05-12 and 2026-05-13 examples they pasted.
- Avoid drifting into generic “complexity / critical thinking / ethical responsibility” themes every day. Rotate exam-relevant topic domains: education/learning, technology and AI, social change, cultural exchange, work/career, environment/cities, information/media literacy, personal growth and resilience.
- Include spaced repetition: at least 2 expressions or patterns from the past 3–7 days should reappear as explicit `复习回扣`, with new examples or a new angle.
- Add one reading-prep component before the July English reading mainline: one 25–40 word long sentence with 主干 / 修饰 / 逻辑关系 / 中文理解 / 可迁移写法.
- Add one active-recall component: 3 short Chinese prompts for the user to translate/rewrite, followed by reference answers.
- Use these sections unless the user changes them again:
  1. `一、今日高级英语表达`: 6–8 expressions; usually 4–6 new + 2 review callbacks. Each item needs 中文解释, Example, 中文理解.
  2. `二、今日高级句型`: 3–4 reusable sentence patterns. Each item needs 中文解释, Example, 中文理解,适用场景.
  3. `三、阅读长难句拆解`: one sentence with syntax and transfer explanation.
  4. `四、实用写作技巧`: 3–4 substantial tips, with ordinary vs advanced expression, structure, examples, and Chinese logic/explanation where useful.
  5. `五、今日高级连接词`: separate section from replacements. Group connectors by function (递进/转折/因果/结论), each group with 2–4 expressions + 1–2 short examples. Use compact text blocks only; do **not** use tables, `.table-wrap`, `.data-table`, `<hr>`, or repeated row borders.
  6. `六、自然高级替换`: separate section from connectors. 4–6 groups of "普通表达 → 高级表达" with example sentences. Use clean before/after text blocks only; do **not** use tables, horizontal separators, or row borders. Do NOT merge with connectors.
  7. `七、今日可背高级段落`: one polished, exam-usable 120–180 word paragraph plus 中文理解; reuse at least 3 expressions/patterns from the day, including one review callback.
  8. `八、3 分钟主动回忆`: 3 short prompts + reference answers.
- Content should feel useful enough to save and review, not a short teaser. Keep the HTML wide and readable, but do not shrink the educational substance.

Avoid: AI-lecture tone, stale templates, content that is too short to be useful, or layouts that reduce the readable line width.

## Operational tip

If the user later says "I want it like this", treat that as a formatting spec update, not casual feedback. Update the scheduled prompt immediately so future runs inherit the exact structure and the visual/legibility intent.

For styled email, verify that the outbound message includes an actual HTML part, not only a plaintext body. A prior bug caused `--html-file` to be ignored when `--body` was also present; this has been fixed in `scripts/smtp.js`, but future automations should still explicitly use `--html-file` for the designed version and a separate fallback for plain text, then report whether HTML styling was sent.
