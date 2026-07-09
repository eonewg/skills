# 163.com validation notes

Validated in-session against a real `@163.com` mailbox using an authorization code.

## Known-good credential file shape

```bash
IMAP_HOST=imap.163.com
IMAP_PORT=993
IMAP_USER=user@example.com
IMAP_PASS=<authorization-code>
IMAP_TLS=true
IMAP_REJECT_UNAUTHORIZED=true
IMAP_MAILBOX=INBOX
IMAP_SAVE_SENT=true

SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=user@example.com
SMTP_PASS=<authorization-code>
SMTP_FROM=user@example.com
SMTP_FROM_NAME=the assistant
SMTP_REPLY_TO=user@example.com
SMTP_CLIENT_NAME=163.com
SMTP_REJECT_UNAUTHORIZED=true
```

Credential file path used by the skill:
`~/.openclaw/credentials/imap-smtp-mail.env`

## Verified commands

```bash
cd ~/.hermes/skills/imap-smtp-mail
node scripts/imap.js list-mailboxes
node scripts/imap.js check --limit 5
node scripts/smtp.js test
```

Observed result:
- mailbox listing succeeded
- inbox reads succeeded (recent onboarding/security emails were returned)
- SMTP self-test succeeded and returned a messageId

## Why this matters

In the same session, Himalaya authenticated and listed folders for the same mailbox but failed on inbox selection with:

`unexpected NO response: SELECT Unsafe Login. Please contact user@example.com for help`

So when `@163.com` works at the auth layer but fails at mailbox selection in Himalaya, `imap-smtp-mail` is a strong fallback candidate.

## Caution

`node scripts/smtp.js test` sends a real email to `SMTP_USER`.
