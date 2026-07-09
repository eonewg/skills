# Obsidian + Claudian migration for teach course workspaces

Use when the user asks to move a `~/teach/<topic>/` course (especially `kaoyan-english-1`) to another machine, Obsidian, or Claudian.

## Key distinction

Do **not** confuse this with wiki migration. A teach course is a small stateful course workspace, not the `~/wiki` knowledge backend.

Typical teach course shape:

```text
~/teach/<topic>/
├── MISSION.md
├── RESOURCES.md
├── lessons/*.html
├── learning-records/*.md
└── optional reference/*.html
```

For HTML lesson generation, also carry `~/teach/_templates/`.

## Recommended migration posture

If the user asks about suitability: teach courses are good candidates for Obsidian + Claudian because they are project-style file workspaces. Claudian can read state, continue lessons, patch navigation, and run template/validation commands.

If the user asks to use another machine: do **not** start moving local files unless explicitly asked. Provide a portable prompt/`CLAUDE.md`, install instructions, and optionally package the relevant skills/templates for download.

## What to package

For another Hermes machine, include:

- `teach` skill
- `teach-style-override` skill
- `teach-html-design` skill
- `~/teach/_templates/`

For plain Obsidian + Claudian without Hermes, provide a course-root `CLAUDE.md` that embeds the operational rules.

## Course-root CLAUDE.md essentials

The prompt should tell Claudian to:

1. Treat the directory as a stateful teaching workspace, not a generic notes folder.
2. Read `MISSION.md`, `RESOURCES.md`, latest `learning-records/*.md`, and existing `lessons/` before continuing.
3. Keep sources/search/tool provenance out of learner-facing HTML; put those details in `RESOURCES.md` or learning records.
4. Generate standalone HTML lessons under `lessons/` and matching records under `learning-records/`.
5. Preserve the user's teaching quality gate: real error scene, full example sentence/problem, bad handling vs corrected handling,扣分/错因 consequence, transfer practice, and observable pass evidence.
6. Use `_templates/make-standalone.py` and `_templates/validate-template.py` when available.
7. Patch previous/next footer navigation when adding a new lesson.
8. For continuation, first perform a read-only diagnosis of current course state before writing files.

## Suggested Obsidian layout

```text
ObsidianVault/
└── Learn/
    └── kaoyan-english-1/
        ├── CLAUDE.md
        ├── MISSION.md
        ├── RESOURCES.md
        ├── lessons/
        ├── learning-records/
        └── _templates/
```

Keep HTML as the formal lesson output. Obsidian is the file/workspace front-end; browser remains the best lesson viewer.

## First Claudian test prompt

Ask Claudian to read state without writing:

```text
你现在在一个考研英语一课程工作区。请先读取 CLAUDE.md、MISSION.md、RESOURCES.md、learning-records/ 下最新记录，以及 lessons/ 下已有文件名。先不要写文件。只判断当前课程到哪一课、下一课应该讲什么、工作区是否缺少模板或验证脚本。
```

Only after it identifies the correct next lesson should it be allowed to write files.
