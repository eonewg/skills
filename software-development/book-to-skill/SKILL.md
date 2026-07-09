---
name: book-to-skill
description: Use when converting a technical book/document PDF, EPUB, DOCX, HTML, Markdown, TXT, RTF, MOBI/AZW into a Hermes Agent skill. Extracts frameworks, concepts, chapter summaries, glossary, patterns, and cheatsheet into a reusable skill under ~/.hermes/skills/.
version: 1.0.0
author: Hermes Agent, adapted from virgiliojr94/book-to-skill
license: MIT
metadata:
  hermes:
    tags: [books, skills, knowledge-base, pdf, epub, technical-documents]
    homepage: https://github.com/virgiliojr94/book-to-skill
    related_skills: [ocr-and-documents, hermes-agent-skill-authoring, personal-knowledge-systems]
---

# Book-to-Skill for Hermes

Convert a technical book or substantial document into a Hermes skill that can be loaded later and used as a grounded reference while studying, coding, planning, or reviewing.

This is adapted from `virgiliojr94/book-to-skill`, but the output is Hermes-native:

- Generated skills live under `~/.hermes/skills/<category>/<slug>/`.
- Use `skill_manage(action="create")` for the generated `SKILL.md`.
- Put chapter/support files under `references/`, because Hermes skill support files are loaded with `skill_view(name, file_path="references/...")`.
- Do **not** create Claude Code slash-command skills under `~/.claude/skills` unless the user explicitly asks for Claude Code output.

## When to Use

Use this skill when the user says things like:

- “把这本 PDF 转成 skill”
- “把这本书做成 Hermes skill”
- “以后能随时查这本书里的概念”
- “把这份技术文档沉淀成技能”
- “从这本书提炼框架 / 模型 / 术语 / 速查表”

Good sources:

- Programming, systems, ML, architecture, product, research, or engineering books
- Technical whitepapers and long-form docs
- Internal manuals / operational playbooks
- Dense courses where the value is reusable conceptual structure

Usually **do not** use this for:

- Ordinary daily notes
- Pure problem sets without explanatory structure
- Short articles better suited to the filesystem wiki
- Exam material where the user only needs task scheduling or OCR

## Output Shape

Generate one Hermes skill with this structure:

```text
~/.hermes/skills/book-derived/<slug>/
├── SKILL.md
└── references/
    ├── chapters/
    │   ├── ch01-<slug>.md
    │   └── ...
    ├── glossary.md
    ├── patterns.md
    ├── cheatsheet.md
    └── source-metadata.json
```

The top-level `SKILL.md` should be compact and front-loaded because Hermes loads it into the prompt. Put detailed chapter material in `references/chapters/*.md` and instruct future agents to load those files on demand.

## Source Extraction

A helper script is bundled at:

```text
scripts/extract.py
```

Use it like this:

```bash
BOOK_PATH="/path/to/book.pdf"
BOOK_SKILL_WORKDIR="/tmp/book_skill_work" \
python3 ~/.hermes/skills/software-development/book-to-skill/scripts/extract.py "$BOOK_PATH" --mode text --install-missing no
```

Modes:

- `--mode text`: fast path; uses `pdftotext`, PyPDF2, pdfminer, plain readers, EPUB fallbacks, etc.
- `--mode technical`: for code/tables/formulas; tries Docling first, then falls back.

Recommended dependencies on WSL:

```bash
sudo apt install poppler-utils
```

For heavier extraction, use a venv instead of system Python:

```bash
uv venv ~/.venvs/book-to-skill
source ~/.venvs/book-to-skill/bin/activate
uv pip install docling PyPDF2 pdfminer.six ebooklib beautifulsoup4 python-docx striprtf
```

The script writes:

```text
/tmp/book_skill_work/full_text.txt
/tmp/book_skill_work/metadata.json
```

Read `metadata.json` first, then inspect `full_text.txt` with bounded reads/searches. Do not dump huge books into context at once.

## Workflow

### 1. Validate request and source

Resolve the document path. If the user gives a Windows path, translate it to `/mnt/c/...` or the correct WSL mount.

Check:

```bash
test -f "$BOOK_PATH" && echo FILE_OK
```

Supported formats: `.pdf`, `.epub`, `.docx`, `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.asciidoc`, `.html`, `.htm`, `.rtf`, `.mobi`, `.azw`, `.azw3`.

### 2. Choose extraction mode

If obvious, choose without asking:

- Code, formulas, tables, academic/engineering PDF → `technical`
- Prose-heavy book or EPUB → `text`
- Scanned/image PDF → use OCR/document skills first; this extractor is primarily text extraction, not full OCR.

If unclear and extraction quality matters, ask one concise question: technical vs text-heavy.

### 3. Extract text

Run the bundled script. Prefer `--install-missing no` unless the user explicitly allowed installs or the current task clearly requires the missing dependency. If a dependency is missing, report the exact package and use available fallbacks first.

### 4. Inspect structure without flooding context

Use tool-based searches and bounded reads:

```bash
wc -w /tmp/book_skill_work/full_text.txt
grep -n -E "^(Chapter|CHAPTER|第[一二三四五六七八九十0-9]+章|[0-9]+\.)" /tmp/book_skill_work/full_text.txt | head -80
```

Use `read_file(..., offset=..., limit=...)` for specific ranges.

Identify:

- Title and author
- Domain and intended use
- Table of contents / chapters
- Core frameworks and repeated vocabulary
- Techniques, algorithms, anti-patterns, decision rules

### 5. Name the generated skill

If the user supplied a slug, use it. Otherwise create a short lowercase hyphenated slug:

- Title-based: `designing-data-intensive-applications`
- Author-concept: `kleppmann-data-systems`
- Chinese title: use concise pinyin or English domain phrase if clearer

Use category `book-derived` unless the user asks otherwise.

### 6. Generate references first

Create these files under a temporary staging directory, then write them into the skill with `skill_manage(action="write_file")` after creating the skill.

Chapter file template:

```markdown
# Chapter N: <Title>

## Core Idea
<1-2 sentences>

## Frameworks / Models
- **Name**: What it is; when to use it; how to apply it.

## Key Concepts
- **Term**: precise definition.

## Techniques / Procedures
- **Technique**: steps, constraints, trade-offs.

## Anti-patterns
- **Avoid X**: why it fails.

## Examples / Tables
Preserve exact code, commands, equations, or decision tables when useful.

## Takeaways
- 3-7 actionable bullets.

## Connects To
- Related chapters or external concepts.
```

Supporting files:

- `references/glossary.md`: important terms alphabetically or by chapter.
- `references/patterns.md`: concrete methods, algorithms, frameworks, playbooks.
- `references/cheatsheet.md`: quick decisions, formulas, command summaries, comparison tables.
- `references/source-metadata.json`: source file path, extraction mode, date, title, author, chapter list, notes about extraction quality.

### 7. Create the Hermes skill

Use `skill_manage(action="create", category="book-derived", name=<slug>, content=<SKILL.md>)`.

Generated `SKILL.md` should include:

```markdown
---
name: <slug>
description: Knowledge skill from "<Title>" by <Author>. Use when applying or studying <3-6 core topics>.
version: 1.0.0
author: Hermes Agent
license: Derived from user-provided source; respect source copyright
metadata:
  hermes:
    tags: [book, <domain tags>]
    related_skills: []
---

# <Title>

## How to Use This Skill
Load this skill when the user asks about <book/domain>. For specific chapters, load `references/chapters/chNN-...md` with `skill_view`.

## Core Mental Models
<the most important frameworks first>

## Chapter Index
- Ch 1 — <title>: `references/chapters/ch01-...md`

## Quick Reference
- Glossary: `references/glossary.md`
- Patterns: `references/patterns.md`
- Cheatsheet: `references/cheatsheet.md`

## Common Pitfalls
<misreadings, overapplications, context limitations>

## Verification
When answering, cite the relevant chapter/reference file and avoid inventing claims not present in the extracted notes.
```

Then write references:

```python
skill_manage(action="write_file", name=<slug>, file_path="references/glossary.md", file_content=...)
skill_manage(action="write_file", name=<slug>, file_path="references/chapters/ch01-title.md", file_content=...)
```

### 8. Verify

Run:

```python
skill_view(name=<slug>)
skill_view(name=<slug>, file_path="references/glossary.md")
```

Also inspect at least one chapter file. If generated files are large, verify the linked file list and sample content rather than reading everything.

## Quality Rules

- Extract structure, not a book report.
- Preserve named frameworks exactly.
- Prefer “Use X when Y” and “Avoid X because Y” phrasing.
- Do not quote huge copyrighted passages. Use concise derived notes; preserve only small necessary code/commands/tables.
- Keep `SKILL.md` compact; put detail in `references/`.
- If extraction quality is poor, state the limitation in `source-metadata.json` and the final reply.
- For the user, do not write to Obsidian unless he explicitly asks.

## Cost / Scope Control

For large books, do not repeatedly read the whole extracted text. Use grep/search and bounded `read_file` ranges.

If a full conversion would require many long model passes, offer a staged path:

- “analysis only” first: identify chapters/frameworks and produce a conversion plan.
- “core skill only”: SKILL.md + glossary + cheatsheet.
- “full skill”: all chapters + references.

If the user explicitly asks to convert and the document is available, proceed with the most reasonable path and verify the generated skill.

## Common Pitfalls

- Writing Claude Code skills to `~/.claude/skills` instead of Hermes skills to `~/.hermes/skills`.
- Putting chapter files under `chapters/`; Hermes supporting files should be under `references/chapters/`.
- Loading entire books into context instead of using bounded reads.
- Creating a massive `SKILL.md` that bloats every future session.
- Treating OCR errors as facts; mark uncertain extraction.
- Creating skills from copyrighted books with long verbatim excerpts.

## Verification Checklist

- [ ] Source file exists and format is supported.
- [ ] Extraction mode chosen and run successfully.
- [ ] `metadata.json` and `full_text.txt` inspected.
- [ ] Generated skill uses Hermes frontmatter and lives under `~/.hermes/skills/`.
- [ ] Chapters/support files are under `references/`.
- [ ] `skill_view(name)` succeeds.
- [ ] At least one linked reference file opens successfully.
- [ ] Final reply gives the skill name, location, and any extraction caveats.
