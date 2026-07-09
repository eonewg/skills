# Manual dated study-email backfill

Use this when the user asks to “补一个昨天的 / 重发昨天的 / 昨晚测试发成今天了” for the daily English study email.

## Core lesson

Do **not** rerun the recurring cron job when the requested email date is not today. The cron prompt intentionally derives the date from the live Asia/Shanghai system clock, so rerunning it will produce/send today’s email again.

Instead, create a manual fixed-date resend using the intended date in filenames, subject, body, and HTML.

## Workflow

1. Parse the requested target date explicitly.
   - “昨天” means Asia/Shanghai yesterday relative to the current live date.
   - Confirm with `TZ=Asia/Shanghai date` when tools are available.

2. Inspect existing artifacts for that target date under `~/.hermes/out/`:
   - `daily-english-YYYY-MM-DD.txt`
   - `daily-english-YYYY-MM-DD.html`
   - `daily-english-YYYY-MM-DD-send.json`
   - If the content was structurally wrong but useful, patch it into `daily-english-YYYY-MM-DD-resend.txt/html` rather than overwriting the original.
   - If no artifacts exist for the fixed date, create a manual `daily-english-YYYY-MM-DD-resend.txt/html` from scratch using the current daily-English spec. Do not change the date to today and do not rerun the live-date cron.

3. For the 2026-06-22 correction pattern, split the old merged section:
   - replace `五、自然高级替换与连接` with `五、今日高级连接词`
   - add `六、自然高级替换`
   - renumber later sections to `七、今日可背高级段落` and `八、3 分钟主动回忆`
   - keep connectors grouped by function; keep replacements as `普通表达 → 高级表达 + Example`.

4. Preview without approval:

```bash
cd ~/.hermes/skills/imap-smtp-mail
node scripts/smtp.js send \
  --to user@example.com \
  --subject '每日英语学习｜YYYY年M月D日 星期X（补发）' \
  --body-file ~/.hermes/out/daily-english-YYYY-MM-DD-resend.txt \
  --html-file ~/.hermes/out/daily-english-YYYY-MM-DD-resend.html \
  > ~/.hermes/out/daily-english-YYYY-MM-DD-resend-preview.json
```

5. Verify the preview:

```bash
python3 ~/.hermes/skills/imap-smtp-mail/scripts/verify_daily_english_html.py \
  ~/.hermes/out/daily-english-YYYY-MM-DD-resend-preview.json
```

6. Send with approval only after verification:

```bash
cd ~/.hermes/skills/imap-smtp-mail
node scripts/smtp.js send \
  --to user@example.com \
  --subject '每日英语学习｜YYYY年M月D日 星期X（补发）' \
  --body-file ~/.hermes/out/daily-english-YYYY-MM-DD-resend.txt \
  --html-file ~/.hermes/out/daily-english-YYYY-MM-DD-resend.html \
  --approve \
  > ~/.hermes/out/daily-english-YYYY-MM-DD-resend-send.json
```

7. Read back the send JSON and verify:
   - `sent: true`
   - recipient accepted
   - `savedToSent: true`
   - four local files exist: `resend.txt`, `resend.html`, `resend-preview.json`, `resend-send.json`

## Reporting

Keep the Feishu reply short:
- state the target date and that it was manually backfilled, not today’s cron rerun
- mention the split sections if that was the correction
- include messageId and Sent-copy status
- list local artifact paths only if useful

Do not paste the full email body into Feishu.
