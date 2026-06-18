# Teach Web Lesson

A research-first, browser-first skill and template kit for creating beautiful standalone HTML lessons.

> Attribution: this teach system was inspired by and evolved from Matt Pocock's `teach` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach). This implementation adds a warm editorial HTML template system, standalone attachment delivery, validation scripts, and stateful course-building conventions.

## What it creates

- Interactive lesson pages with sidebar navigation, progress, KaTeX formulas, examples, quizzes, and review sections.
- Optional reference/cheat-sheet pages.
- Standalone single-file HTML output for sharing.
- Multi-lesson course chains with previous/next footer navigation.

## Quick start

```bash
cp templates/lesson-template.html my-course/lessons/0001-example.html
# edit the lesson content
python3 scripts/make-standalone.py my-course/lessons/0001-example.html
python3 scripts/validate-template.py my-course/lessons/0001-example.html
```

Open the HTML file in a browser and verify the sidebar, KaTeX rendering, quiz interaction, and footer links.

## Agent workflow

1. Research official/high-trust sources first.
2. Sample learner-facing material when misconceptions or practical pain points matter.
3. Write from the template, not from a blank page.
4. Keep the design warm, readable, and low-chroma.
5. Inline assets before sharing.
6. Validate and browser-check before delivery.

## License

MIT.
