# Manual English Email Execution

Use this when manually triggering the daily English email outside the cron schedule (e.g., cron failed, user requests immediate resend).

## Quick Path

1. Write HTML email to `~/.hermes/out/daily-english-YYYY-MM-DD.html`
2. Write plaintext fallback to `~/.hermes/out/daily-english-YYYY-MM-DD.txt`
3. Preview: `node scripts/smtp.js send ... > preview.json` (no `--approve`)
4. Verify HTML styling present (not generated from text)
5. Send: add `--approve` to the same command
6. Clean up preview JSON

## Critical Pitfalls

- **Output directory**: Always use `~/.hermes/out/` — NOT `~/.openclaw/workspace/out/`. The ALLOWED_READ_DIRS env points to `~/.openclaw/` but actual Hermes runtime writes to `~/.hermes/out/`. Wrong path = approval-gated failure in cron/no-user context.
- **Use `--body-file` + `--html-file`**, never `--body` + `--html-file` (the latter causes HTML to be ignored)
- **Always preview first** without `--approve`, verify styling, then send with `--approve`
- **From address**: Use `user@example.com` (SMTP_USER), not a display name

## Content Structure (6 sections)

1. 一、今日高级英语表达 (6-8 expressions)
2. 二、今日实用高级句型 (3-4 patterns)
3. 三、写作技巧 (3-4 tips, substantial)
4. 四、常用高级过渡表达 (grouped by function)
5. 五、让英文更自然的替换方式 (weak → strong)
6. 六、今日可背高级段落 (one polished paragraph)

See `references/recurring-study-email-format.md` for full format spec and `references/the user-daily-english-cron-verification.md` for HTML layout guardrails.
