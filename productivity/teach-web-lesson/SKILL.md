---
name: teach-web-lesson
description: Use when creating or revising browser-first standalone HTML lessons, reference pages, and stateful course workspaces. Defines a research-first teaching workflow, warm editorial page design, KaTeX/quiz/sidebar components, validation, and shareable single-file delivery.
version: 1.0.0
author: Eone Wang
license: MIT
metadata:
  hermes:
    tags: [teaching, html, lessons, course-design, templates, katex]
    related_skills: []
---

# Teach Web Lesson

## Overview

Teach Web Lesson is a research-first, browser-first system for turning teaching material into beautiful standalone HTML lessons. It is meant for AI agents that build real learning artifacts rather than plain Markdown notes: each page has a readable warm editorial layout, a sidebar table of contents, progress feedback, KaTeX rendering, quiet quiz interactions, review sections, and footer navigation for course continuity.

**Attribution:** this teaching skill was inspired by and evolved from Matt Pocock's `teach` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach). This implementation adds a standalone HTML template kit, warm editorial visual system, validation scripts, and stateful course-building conventions.

## When to Use

Use this skill when:

- Creating a new HTML lesson page for a topic, course, tutorial, exam unit, or internal training module.
- Continuing a multi-lesson course where previous/next navigation and learning records matter.
- Converting researched teaching material into a self-contained page that can be opened in a browser or sent as a single HTML attachment.
- Building math, CS, language-learning, writing, or technical lessons that benefit from formulas, examples, quizzes, and review prompts.
- Revising an existing lesson for layout, readability, navigation, or validation quality.

Do not use this when the user only needs a short answer, a plain Markdown note, or a print-first PDF handout.

## Package Layout

```text
teach-web-lesson/
├── SKILL.md
├── skill-card.md
├── templates/
│   ├── lesson-template.html
│   └── reference-template.html
├── assets/
│   ├── teach-components.css
│   └── teach-lesson.js
├── scripts/
│   ├── make-standalone.py
│   └── validate-template.py
├── examples/
└── references/
```

## Core Workflow

1. **Research first.** Before teaching or writing, gather source material. Use official/high-trust references for correctness, then sample learner-facing discussions when the topic benefits from real confusion points. Treat community material as misconception mining, not as unchecked fact.
2. **Create or continue a course workspace.** A typical workspace has `lessons/`, optional `reference/`, and `learning-records/`.
3. **Start from a template.** Copy `templates/lesson-template.html` into `lessons/000X-topic.html` or `templates/reference-template.html` into `reference/topic.html`.
4. **Author the lesson.** Use the warm editorial style: clear hero, concise sections, left-rule callouts, examples, quiet quizzes, and review prompts. Avoid over-carded dashboard pages.
5. **Maintain navigation.** Each lesson should link to previous and next lessons via `.footer-nav`. If the next lesson is planned but not written yet, link to its intended filename rather than a `#review` placeholder.
6. **Make it standalone before sharing.** Inline local CSS/JS so the HTML file can travel alone:
   ```bash
   python3 scripts/make-standalone.py path/to/lesson.html
   ```
7. **Validate.** Run:
   ```bash
   python3 scripts/validate-template.py path/to/lesson.html
   ```
8. **Browser-check.** Open the file and verify the title, sidebar toggle, table of contents, KaTeX rendering, footer links, and at least one quiz interaction.

## Design Rules

- Use a warm editorial canvas, not a SaaS dashboard: cream background, weak borders, little/no shadow, sparse coral accent.
- Keep the main reading column around 720px on desktop.
- Use section rhythm and typography before adding cards.
- Prefer left-rule examples/callouts over heavy rounded containers.
- Use high-contrast near-black/brown text and low-saturation accents; avoid bright grammar-marker colors.
- Use KaTeX delimiters `\(...\)` and `\[...\]`; avoid `$...$` in HTML pages.
- Quiz feedback must include visible text markers such as `✓` and `✗`, not color alone.

## Course Continuity Rules

For a continuing course:

- Read the latest learning record and existing filenames before deciding the next lesson.
- Patch the previous lesson so its footer right link points to the new lesson.
- In the new lesson, include a next-link placeholder pointing to the next planned filename.
- If a review paragraph mentions the next lesson, make the link well-formed and close the `<a>` tag before the paragraph ends.
- After editing, inspect the rendered footer: it should show exactly two nav links and no empty swallowed link.

## Common Pitfalls

1. **Teaching from memory only.** Always do a source pass before generating a serious lesson.
2. **Sending linked HTML.** If the page links local CSS/JS, attachments will render unstyled. Run `make-standalone.py` before sharing.
3. **Broken footer layout from malformed links.** A missing `</a>` in a review paragraph can swallow footer nodes and shift buttons. Validate and browser-check.
4. **Over-designing.** Too many cards, badges, gradients, or saturated colors make the page harder to read.
5. **Ignoring mobile.** The sidebar should collapse into a compact navigation row on narrow screens.

## Verification Checklist

- [ ] Sources checked before teaching/writing.
- [ ] Lesson starts from the template and uses package assets.
- [ ] KaTeX imports and delimiters are present when formulas are used.
- [ ] Previous/next footer links are real filenames, not placeholders like `#review`.
- [ ] `python3 scripts/make-standalone.py ...` run before sharing.
- [ ] `python3 scripts/validate-template.py ...` passes.
- [ ] Browser opened and sidebar/footer/quiz visually checked.
