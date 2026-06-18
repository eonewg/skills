# Course Lesson Workflow Notes

Use this reference when continuing a course in `your course workspace / <topic>/`.

## Artifact pattern

For each next lesson, default to the lean artifact set:

- `lessons/000X-<topic>.html` — the browser-first teaching page and the only file normally sent as MEDIA.
- `learning-records/000X-<topic>.md` — durable learning state and next direction.

Do **not** create a `reference/<topic>.html` quick-reference sheet by default. Create a reference page only when one of these is true:

1. Explicitly asked for a 速查/参考页.
2. The lesson contains dense formulas, procedures, templates, tables, or checklists that are genuinely useful as a reusable lookup sheet.
3. The main lesson would become too long or cognitively noisy unless the lookup material is split out.

## Back-patching the previous lesson

After creating the new lesson, patch the previous lesson in two places:

1. **Footer navigation** (`<nav class="footer-nav">`): add a "下一课 →" link to the new lesson HTML so sequential navigation works end-to-end.
2. **Review section text**: in the `<section id="review">` paragraph that starts with "下一步" or "下一课", update the text to be a clickable link (`<a href="000X-xxx.html">...</a>`) to the new lesson.

Then re-run make-standalone.py + validate-template.py on the patched previous lesson so the delivered version reflects the new links.

## Forward link in the new lesson

The new lesson's own footer must also include a "下一课 →" link pointing to the next planned filename, even though that file does not exist yet. Follow the naming convention `000X-<kebab-topic>.html`. This keeps the navigation chain continuous end-to-end so the user can always see what comes next.

Feishu/Lark HTML attachments do not carry local relative assets. A page that only links `../../_templates/assets/teach-components.css` and `../../_templates/assets/teach-lesson.js` will render as plain unstyled HTML on the recipient's side.

Before sending any lesson/reference HTML, always inline local CSS/JS:

```bash
python3 path/to/teach-web-lesson/scripts/make-standalone.py path/to/course/lessons/000X-<topic>.html
python3 path/to/teach-web-lesson/scripts/validate-template.py path/to/course/lessons/000X-<topic>.html
```

Verify the delivered file contains:

- `data-standalone="true"`
- inline `/* Teach Web Lesson Components ... */` CSS
- inline `// Teach Web Lesson JS ...` script

Then browser-open the exact standalone file and verify visible colors plus at least one JS interaction before sharing it.

## Source discipline

For exam or authoritative-content courses, gather official or high-trust sources before writing content rather than relying on memory. Embed the source list in a collapsed `details.reveal` block when appropriate.

## Continuing sequence

When asked "下一课 / 继续 / 下一节", continue from the latest `learning-records/*.md` 后续方向 rather than asking what to teach.

## Visual convention

Keep the visual base stable: warm page background, card background, weak borders, coral links/buttons. Use the warm ink scale for text emphasis rather than saturated colors. See `claude-like-warm-editorial.md` and `lightweight-editorial-html-design.md` for detailed design rules.