---
name: cangjie-content-skill-distillation
description: Distill high-value source content—books, long videos, podcasts, interviews, courses, long essays, or document corpora—into a staged pack of executable Hermes skills. Use when the user asks “仓颉”, “cangjie”, “把这本书/长视频/播客蒸馏成 skills”, “把内容里的方法论做成可调用 skill”, or wants reusable methods rather than a summary. Not for simple summaries, one-book reference skills, persona/colleague/master distillation, or learning-session scheduling.
version: 1.0.0
author: Hermes Agent, adapted from kangarooking/cangjie-skill
license: MIT
metadata:
  hermes:
    tags: [content-distillation, book-to-skill, video-to-skill, methodology, agent-skills]
    homepage: https://github.com/kangarooking/cangjie-skill
    related_skills: [book-to-skill, cognitive-distillation-workflows, media-ingestion-and-transcription, bili-note, douyin-note, skill-library-operations]
---

# Cangjie Content Skill Distillation

Hermes-native adaptation of `kangarooking/cangjie-skill`: turn high-value content into a **set of atomic, executable, testable skills**, not a summary or a single giant reference file.

## Mission

Use this skill when the user wants to extract reusable methods from source material so future agents can **call the methods in real tasks**.

The output is a staged skill pack:

```text
~/skill-lab/cangjie/<source-slug>/
├── BOOK_OVERVIEW.md
├── INDEX.md
├── candidates/
├── rejected/
├── verified.md
├── <atomic-skill-1>/
│   ├── SKILL.md
│   └── test-prompts.json
└── <atomic-skill-2>/
    ├── SKILL.md
    └── test-prompts.json
```

Only after user approval / quality verification should individual atomic skills be promoted to:

```text
~/.hermes/skills/content-derived/<skill-name>/
```

## Boundaries and Routing

Use this skill for:
- books, long videos, podcasts, interviews, courses, long essays, or document sets with reusable methodology;
- requests to “蒸馏成一组 skills”, “结构化复用”, “以后让 agent 调用这些方法”; 
- extracting frameworks, principles, checklists, failure modes, terms, and execution procedures.

Do **not** use this skill for:
- simple summary / highlights / notes → use `knowledge-ingestion-routing`, `bili-note`, `douyin-note`, or media extraction skills;
- one book as a compact reference skill → use `book-to-skill`;
- person / colleague / master / industry OS distillation → use `cognitive-distillation-workflows`;
- long-term learning schedule / state / curriculum → use `sijiao-learning-workflows` and `teach`;
- persona imitation or roleplay as the author.

## Core Method: RIA-TV++

Pipeline:

```text
Stage 0: Adler whole-source understanding → BOOK_OVERVIEW.md
Stage 1: extractor passes → candidates/
Stage 1.5: triple verification → verified.md + rejected/
Stage 2: RIA++ atomic skill construction → */SKILL.md
Stage 3: Zettelkasten links → INDEX.md
Stage 4: pressure tests → test-prompts.json + test-results.md
```

Read details on demand:
- `references/methodology/00-overview.md`
- `references/methodology/01-stage0-adler.md`
- `references/methodology/02-stage1-parallel-extract.md`
- `references/methodology/03-stage1.5-triple-verify.md`
- `references/methodology/04-stage2-ria-plus.md`
- `references/methodology/05-stage3-zettelkasten.md`
- `references/methodology/06-stage4-pressure-test.md`

## Input Requirements

Before starting a full distillation, obtain or resolve:

1. **Source text path or extracted transcript**: PDF/EPUB/TXT/MD/HTML, video subtitles, ASR transcript, podcast transcript, article corpus, etc. Do not “distill from memory”.
2. **Source identity**: title, author/speaker/channel, year/date if known.
3. **Scope**: full source, selected chapters, selected video, playlist, podcast episode, or corpus.
4. **Mode**:
   - `scan`: assess whether the source is worth skill distillation;
   - `pilot`: produce BOOK_OVERVIEW + 1–3 atomic skills;
   - `full`: produce a full staged pack;
   - `promote`: move verified atomic skills into `~/.hermes/skills/content-derived/`.

If the source is a video/podcast without transcript, first route through `media-ingestion-and-transcription`, `bili-note`, `douyin-note`, or `yt-dlp-downloader`.

## Hermes Adaptations

1. **Staging first**: build under `~/skill-lab/cangjie/<source-slug>/`; do not immediately pollute live `~/.hermes/skills/`.
2. **Support files**: put long methodology/templates in `references/` and `templates/` so Hermes can load them progressively.
3. **Delegation limit**: if using subagents, this environment may cap batch delegation at 3. Run extractor waves:
   - Wave 1: framework, principle, case;
   - Wave 2: counter-example, glossary.
   If delegation is unavailable or overkill, run extractor passes sequentially but keep their outputs separate.
4. **Copyright discipline**: short quotes only when needed for audit. Prefer paraphrased methods, steps, boundaries, and source location references. Do not copy long book/video passages into skills.
5. **Promotion rule**: only promote atomic skills that have trigger clarity, boundaries, and pressure tests. Do not promote candidates or half-tested skills.

## Stage 0 — Whole-Source Understanding

1. Inspect the source structure with bounded reads/searches. For large sources, do not dump all text into context.
2. Use `references/methodology/01-stage0-adler.md` and `templates/BOOK_OVERVIEW.md.template`.
3. Write:

```text
~/skill-lab/cangjie/<source-slug>/BOOK_OVERVIEW.md
```

4. Show the user the skeleton and ask whether the understanding/scope is right before full extraction unless the user explicitly asked for autonomous full processing.

BOOK_OVERVIEW must include:
- source type and thesis;
- 3–7 major arguments/parts;
- key terms;
- core claims and argument chain;
- author/speaker blind spots and limits;
- what is and is not worth turning into skills.

## Stage 1 — Extractor Passes

Use the extractor prompts under `references/extractors/`:

| Extractor | Output |
|---|---|
| framework-extractor | `candidates/frameworks.md` |
| principle-extractor | `candidates/principles.md` |
| case-extractor | `candidates/cases.md` |
| counter-example-extractor | `candidates/counter-examples.md` |
| glossary-extractor | `candidates/glossary.md` |

Every candidate should include:

```yaml
id: f01
title: <short title>
type: framework | principle | case | counter-example | term
source_location: <chapter/timestamp/section>
source_quote_or_pointer: <short quote or pointer, keep concise>
summary: <5-10 lines in own words>
tags: [..]
```

Do not filter too aggressively in Stage 1. Filtering happens in Stage 1.5.

## Stage 1.5 — Triple Verification

Use `references/methodology/03-stage1.5-triple-verify.md`.

A candidate becomes an atomic skill only if it passes all three tests:

1. **V1 Cross-domain / repeated support**: appears in at least 2 independent contexts in the source or corpus.
2. **V2 Predictive power**: can answer a new, non-explicit scenario in a non-trivial way.
3. **V3 Exclusivity**: not generic common sense the base model already knows.

Write:

```text
verified.md
rejected/<candidate-id>.md
```

Rejected items are still useful as examples, glossary entries, or background, but should not become standalone skills.

## Stage 2 — RIA++ Atomic Skill Construction

For each verified method, use `templates/SKILL.md.template` and `references/methodology/04-stage2-ria-plus.md`.

Each atomic skill must include:

- **R — Reading**: short source quote or precise source pointer;
- **I — Interpretation**: method in your own words;
- **A1 — Past Application**: source example(s);
- **A2 — Future Trigger**: when a future user would need this skill;
- **E — Execution**: step-by-step procedure with completion criteria;
- **B — Boundary**: when not to use it, failure modes, blind spots;
- Related skills and audit information.

The `description` field must come from A2 and should be specific enough to prevent noisy activation.

## Stage 3 — Zettelkasten Links

Use `templates/INDEX.md.template` and `references/methodology/05-stage3-zettelkasten.md`.

Map relationships:

- `depends-on`: skill A needs skill B first;
- `contrasts-with`: similar-looking but different method;
- `composes-with`: useful combination.

Generate `INDEX.md` with skill groups, recommended order, and a lightweight graph.

## Stage 4 — Pressure Testing

Use `templates/test-prompts.json.template` and `references/methodology/06-stage4-pressure-test.md`.

Each atomic skill needs tests:

- 3–5 `should_trigger` prompts;
- 2–3 `should_not_trigger` decoys;
- 1–3 `edge_case` prompts.

Prefer blind subagent tests when worthwhile. Otherwise run a documented fallback self-test and write `test-results.md`.

If tests fail, return to Stage 2 and fix A2/E/B; do not just patch the description superficially.

## Promotion to Live Hermes Skills

Only after tests pass and the user approves:

1. Choose a concise `content-derived/<skill-name>` target.
2. Use `skill_manage(action="create", category="content-derived", ...)` or direct Hermes skill tooling.
3. Move long evidence/examples into `references/`.
4. Run `skill_view(name)` to verify the promoted skill loads.
5. Report real paths and test status.

## Quality Gates

Block or warn if:

- No source text/transcript is available.
- The source has no method/framework content and only supports summary/notes.
- A candidate fails any of V1/V2/V3 but is still being promoted.
- An atomic skill lacks trigger, execution steps, or boundaries.
- The generated skill is too broad, e.g. “long-term thinking skill” without precise activation.
- No negative/decoy pressure tests exist.

## Relationship to Existing the user Skills

- `book-to-skill`: one source → one reference skill. Use for searchable technical/reference knowledge.
- `cangjie-content-skill-distillation`: one source/corpus → many executable atomic skills. Use for reusable methodology.
- `cognitive-distillation-workflows`: person/teammate/industry → cognitive/work/master OS.
- `teach` / `sijiao-learning-workflows`: learning delivery and state. Cangjie outputs can become teaching material, but Cangjie does not schedule learning.

## Attribution

Adapted from `kangarooking/cangjie-skill` (MIT). Original concepts include RIA-TV++, extractor passes, triple verification, RIA++ construction, Zettelkasten linking, and pressure-test workflow. This Hermes adaptation changes paths, staging, delegation assumptions, copyright discipline, and promotion workflow for the user’s Hermes skill system.
