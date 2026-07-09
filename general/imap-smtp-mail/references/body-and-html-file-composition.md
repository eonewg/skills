# Body-file + HTML-file composition pitfall

## Context
During the daily English micro-magazine cron on 2026-05-13, the script was called with both:

```bash
node scripts/smtp.js send \
  --to user@example.com \
  --subject "每日英语微型杂志｜2026-05-13" \
  --body-file /tmp/daily-english-2026-05-13.txt \
  --html-file /tmp/daily-english-2026-05-13.html \
  --approve --debug
```

The SMTP send succeeded, but the raw MIME debug transcript showed the HTML part was generated from the plain-text body instead of using the styled HTML file.

## Root cause
Older `scripts/smtp.js` used an `if / else if` chain in `prepareSendOptions()`:

- if `--body-file` existed, it loaded the text body
- because that branch matched, the later `else if (options['html-file'])` branch never ran
- `normalizeComposedContent()` then generated a basic HTML alternative from the plain text

## Fix
Patch `prepareSendOptions()` so `--html-file` is handled in an independent `if` after body/body-file processing:

```js
if (options['body-file']) {
  validateReadPath(options['body-file']);
  const content = fs.readFileSync(options['body-file'], 'utf8');
  if (options['body-file'].endsWith('.html') || options.html) {
    options.html = content;
  } else {
    options.text = content;
  }
} else if (options.body) {
  options.text = options.body;
}

if (options['html-file']) {
  validateReadPath(options['html-file']);
  options.html = fs.readFileSync(options['html-file'], 'utf8');
}
```

## Verification pattern
For styled multipart sends, first run a preview without `--approve` and inspect:

```bash
node scripts/smtp.js send \
  --to recipient@example.com \
  --subject "Preview" \
  --body-file /tmp/body.txt \
  --html-file /tmp/body.html
```

Expected preview JSON:

- `draft.text` contains the text body
- `draft.html` contains the actual styled HTML file, not `<p>...text converted...</p>`

Then send with `--approve`. Use `--debug` only when troubleshooting delivery; it prints the full MIME payload and can create very large logs.