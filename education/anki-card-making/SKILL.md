---
name: anki-card-making
description: Create high-quality Anki/APKG cards for the user's exam study from PDFs, courseware, notes, exercises, wrong-question reviews, or English intensive reading. Use when the user asks to 制卡 / 生成 Anki / 导出 APKG / 整理为卡片 / 优化卡片 / 继续制卡. Do not trigger for ordinary explanations or review unless the user explicitly wants Anki cards.
tags:
  - anki
  - apkg
  - 考研
  - 制卡
  - 数学
  - 408
  - 英语
---

# Anki Card Making for the user

## Trigger and boundary

Use this skill when the user explicitly asks for Anki card work: 制卡、生成 Anki、导出 APKG、整理为卡片、优化这张卡、继续制卡、错题转卡、PDF 转 APKG.

Do **not** proactively generate Anki cards during normal teaching,复盘, or explanation. If the user only asks “讲一下 / 复盘 / 考我”, answer normally unless they ask for cards.

## Default deliverable

- Default artifact: `.apkg` only, ready to import into Anki.
- If the user only asks “看看怎么制卡 / 优化这张卡”, return improved card content directly; no APKG needed.
- If the user says “继续制卡”, reuse the previous deck path, field schema, and style instead of inventing a new one.

## Deck and note model defaults

Deck names:
- Math: `数学::高数::章节名`
- Data structure: `408::数据结构::章节名`
- COA: `408::计算机组成原理::章节名`
- OS: `408::操作系统::章节名`
- Network: `408::计算机网络::章节名`
- English: `英语::考研英语一::主题名`

Field order for new models:
1. `Question`
2. `Answer`
3. `Notes`
4. `Source`
5. `Tags`

Recommended model names:
- `the user-考研通用问答卡-v1`
- `the user-考研数学-问答卡-v1`
- `the user-408-问答卡-v1`

`Question` must be the first field so Anki duplicate detection works predictably.

## Operating workflow

1. Determine material type: PDF/courseware, user note, exercise/wrong question, review Q&A, or existing cards.
2. Confirm or infer material range and deck path. Ask only if ambiguity changes the artifact.
3. Extract content. For PDFs/courseware, do not rely only on text extraction when formulas, diagrams, tables, blue boxes, or OCR glitches matter; render/check page images as needed.
4. Filter before making cards: keep core mechanisms, formulas with conditions, method signals, easy mistakes, high-value distinctions, and compact recognition points; skip low-value background.
5. Split into card types: concept, mechanism, method, exam-signal, mistake/distinction, formula, image, or low-burden recognition.
6. Generate APKG, preferably with a small Python script using `genanki` in a temporary venv if the environment lacks it.
7. Verify the APKG with `scripts/verify_apkg.py` or an equivalent zip/sqlite read-back before reporting success.
8. Final message: deck name, card count, card types, coverage, exclusions, and `MEDIA:/absolute/path/file.apkg`.

## Card quality rules

- One card = one core point.
- Every card must be self-contained; avoid “this page / above formula / example 3”.
- Do not put whole big problems into cards unless explicitly requested. Extract: signal, method choice, first key step, turning point, mistake, migration rule.
- Prefer “why this concept exists / when this method triggers / what condition blocks misuse” over raw definition recall.
- Long answers should be split.
- Use Anki-compatible MathJax: inline `\(...\)`, block `\[...\]`; do not use `$...$` unless the user asks for Obsidian.
- HTML is allowed inside APKG fields: `<br>`, `<b>`, short `<ul><li>...</li></ul>`, `<img src="...">`.
- Images must be cropped and focused, not full-page screenshots.

## Subject emphasis

Math:
- Prioritize method triggers: symmetry, parity, periodicity, interval recurrence, substitution, parameter differentiation, integration by parts, Taylor order, equivalent infinitesimal conditions.
- Make formulas into forward recall, reverse recognition, condition-limit, and confusion cards.

408:
- First identify module: data structure, COA, OS, network.
- Prioritize mechanisms, state transitions, input/output, boundary conditions, similar-concept distinctions, and calculation templates.
- Common templates: Cache Tag/Index/Offset, memory expansion and chip select, scheduling, semaphores/PV, page replacement, disk scheduling, sliding window, CRC, subnetting, delay calculation.

English intensive reading:
- Prioritize sentence trunk, clause/modifier structure, logical connectors, familiar-word special meanings, transferable expressions, author attitude, and translation logic.

## Minimum tags

Each note should include:
- subject tag: `数学`, `高数`, `408`, `操作系统`, etc.
- chapter/topic tag: e.g. `级数`, `进程同步`, `Cache`.
- type tag: `concept`, `method`, `mistake`, `formula`, `recognition`, `image`.

Useful extra tags: `study-action`, `exam-signal`, `easy-mistake`, `core`, `low-burden`.

## Verification checklist

Before delivery, check:
- APKG exists and is non-empty.
- Zip contains `collection.anki2`.
- SQLite read-back counts notes/cards and confirms field 1 is the question text.
- MathJax uses Anki delimiters.
- Tags are present.
- No accidental full-exam-question dumps unless requested.
- For PDF-derived cards, formulas/diagrams/blue boxes were checked when relevant.

## Reference

The full detailed source spec from the user is stored at `references/the user-anki-card-spec.md`. Use it for detailed card-type examples, PDF handling rules, bad-card rewrites, and final-output template.