# WeRead reading analysis report by HTML email

Use this when the user asks for a detailed 微信读书 / WeRead reading analysis report and wants it delivered by email.

## Data collection pattern

Collect enough data to support analysis rather than just restating one endpoint:

- `/readdata/detail` for `weekly`, `monthly`, `annually`, and `overall`. Treat all time fields as seconds. Use `totalReadTime` as the main total and `readStat` for read/finished/note counts.
- `/shelf/sync` for shelf size and composition. Shelf total must be `books.length + albums.length + (mp non-empty ? 1 : 0)`.
- `/user/notebooks` with `count` + `lastSort` pagination until `hasMore` is false. Compute each book's total notes as `reviewCount + noteCount + bookmarkCount`; do not use `noteCount` as total notes.
- For a recent-reading section, sort `shelf.books` by `readUpdateTime` / `updateTime` and call `/book/getprogress` for the top recent books only. Do not fan out over the entire shelf unless the user specifically asks; it is slow and unnecessary for the report.

## Analysis sections that work well

A good report should include:

- Executive judgment: reading archetype, current strength, current risk.
- Time trend: weekly / monthly / annual / overall totals, reading days, natural-day average, and compare trend when available.
- Content preference: `preferCategory`, `preferAuthor`, and shelf category distribution.
- Shelf structure: total visible entries, ebooks, albums, article collection entry, finished count, public/private split.
- Note/deep-processing profile: total notebook books, total notes, top note-heavy books, note density.
- Recent reading field notes: recent books with category, progress, and date.
- Concrete strategy: 2-4 next actions tied to the user's actual pattern, not generic reading advice.

## Email delivery workflow

For an HTML email deliverable:

1. Generate a self-contained HTML file and a plain-text fallback under an allowed read directory such as `/tmp`.
2. Preview with `imap-smtp-mail` before sending:
   `node scripts/smtp.js send --to <recipient> --subject <subject> --body-file /tmp/report.txt --html-file /tmp/report.html`
3. Inspect the preview enough to verify that the HTML part is the styled report, not generated paragraphs from the text body.
4. Send only after the user has already requested email delivery, using `--approve`.
5. Report the recipient, subject, and SMTP `messageId` / accepted response when available.

## HTML report design notes

- Use a wide, readable layout (`max-width` around 900-1000px), flat cards, and responsive CSS.
- Prefer visual hierarchy over huge tables: KPI cards, bar rows for rankings, compact tables for recent books and note-heavy books.
- Include a short口径说明 at the bottom: time fields are seconds; valid reading days follow WeRead's effective-day rule; total notes are `reviewCount + noteCount + bookmarkCount`.
- Keep judgments grounded in data. If weekly reads are zero, say the current week has not formed an effective reading day rather than claiming the user did not open WeRead at all.
