# Headless Chrome HTML → PDF fallback

Use this when the user asks for a polished PDF deliverable and common Python PDF libraries or converters are unavailable (`reportlab`, `weasyprint`, `pandoc`, `wkhtmltopdf`, LibreOffice, etc.).

## Pattern

1. Author a self-contained HTML file with print CSS:
   - `@page { size: A4; margin: ... }`
   - readable fonts, explicit layout, page breaks where needed
   - for Chinese text, prefer installed CJK fonts such as `WenQuanYi Zen Hei` when available
2. Render with Google Chrome / Chromium headless:

```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --print-to-pdf=/absolute/path/output.pdf \
  file:///absolute/path/input.html
```

3. Verify the PDF:

```bash
file /absolute/path/output.pdf
du -h /absolute/path/output.pdf
```

Optionally check page count with `pdfinfo` if installed.

## Notes from a real run

- In WSL/headless environments, Chrome may print DBus/UPower/shared-memory warnings but still successfully write the PDF. Treat success as the presence of the output file and `file` reporting `PDF document`.
- This works well for bilingual annotated handouts because HTML/CSS makes two-column layouts, callouts, and typography much easier than hand-built PDF APIs.
- If the PDF will be emailed through `imap-smtp-mail`, remember the attachment must live under that skill's runtime `ALLOWED_READ_DIRS`; copy the final PDF to `/tmp` when needed.
