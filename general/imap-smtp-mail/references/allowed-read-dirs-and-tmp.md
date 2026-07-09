# Allowed read dirs / tmp pitfall

## What happened

A real send run failed with:

```text
Error: Access denied: '~/.openclaw/workspace/tmp/daily-english-2026-05-11.txt' is outside allowed read directories
```

The configured runtime allowlist was:

```text
ALLOWED_READ_DIRS=~/.hermes,~/.hermes/data,~/Downloads,/tmp
ALLOWED_WRITE_DIRS=~/.hermes,~/.hermes/data,~/Downloads,/tmp
```

So the sample path from the skill doc (`~/.openclaw/workspace/tmp`) was **not** actually permitted on that machine.

## Reusable lesson

Before using:
- `--body-file`
- `--html-file`
- `--subject-file`
- `--attach`
- IMAP download output directories

check the live values in `~/.openclaw/credentials/imap-smtp-mail.env` instead of assuming the sample config from the README is what the machine uses.

## Fast recovery pattern

1. Inspect `ALLOWED_READ_DIRS` / `ALLOWED_WRITE_DIRS` in the env file.
2. If your chosen path is outside the allowlist, rewrite the temporary files into an approved directory.
3. Retry the exact same `smtp.js send` command using the approved path.

In observed cases, moving generated `.txt` / `.html` body files and final PDF attachments to `/tmp/` fixed the send immediately.

## Why this matters

This failure happens late — the email content may already be generated, so the practical fix is to relocate files, not to rework the whole message. Encode this as a first-pass check whenever a send command depends on local files.
