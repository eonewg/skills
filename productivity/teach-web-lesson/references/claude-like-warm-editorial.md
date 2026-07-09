# Claude-like warm editorial style for teach pages

Use this reference when creating or revising HTML lessons/reference pages in a course workspace.

## Trigger

Apply by default for teach HTML pages, especially when the page is a long-form lesson rather than a dense formula sheet or dashboard.

## Visual target

The page should feel closer to Claude web chat / editorial long-form reading than to a SaaS dashboard or PPT:

- Warm ivory / cream canvas: prefer `#faf9f5` or `#faf8f2`; avoid pure white and cool gray-blue.
- Near-black warm ink: `#141413` / `#1f1e1b`, with muted text around `#6c6a64`.
- Claude app-like typography split: normal UI/body/Chinese-English mixed teaching notes should use Source Sans 3 + Noto Sans SC/CJK; serif is reserved for display moments or longer English reading passages.
- Serif display moments: use Source Serif 4 / Noto Serif SC for hero headings, quoted long passages, or special editorial blocks only. Do not make the whole learning page serif by default.
- Body text: around `17px`, line-height around `1.7`; long English passages may use `17.5px` / `1.75`.
- Generous reading column: around `720–820px` for mixed Chinese-English notes; wider shells are fine for sidebars, but keep the main prose column controlled.
- Sparse coral/orange accent: `#c96442` or Claude-like `#cc785c` for left rules, highlights, tags, and small controls.
- Teaching annotations should use a warm ink scale, not saturated textbook colors. Prefer `#141413`, `#3d3d3a`, `#6c6a64`, `#7a6e60`, `#5f5146`, `#9a8778`; reserve `#cc785c` as the only chromatic anchor for sparse accents or predicate verbs. Avoid bright blue/green/purple/red labels.
- Use font weight, italic, serif/sans contrast, and spacing as the primary emphasis tools; color is secondary.
- Weak borders / no heavy shadows: prefer hairline borders such as `#e6dfd8` / `#e7ded2`; avoid floating card piles.
- Natural content flow: paragraphs should read like a calm tutorial conversation. Do not make every paragraph a card.

## Legibility pitfalls

- Do not use `text-align: justify` for Chinese lesson paragraphs. It can stretch short Chinese lines into awkward spacing. Use `text-align: start`.
- If web fonts stall, keep the font stack resilient with local/system fallbacks.
- Keep cards reserved for high-signal blocks: core conclusion, table, exercise, trap list, worked example, retrieval practice.
- Avoid making short English examples serif; that creates unnecessary visual switching. Save serif for sustained reading blocks.