# SMTP sent-copy raw message fallback

Use this note when `node scripts/smtp.js send --approve` delivers successfully but the JSON reports that IMAP Sent-copy was not saved because the raw MIME message was unavailable, or when Sent mailbox detection fails unexpectedly.

## Symptom

SMTP succeeds, e.g. `sent: true`, `accepted: [...]`, and a `250 Mail OK ...` response, but the send result includes:

```json
{
  "savedToSent": false,
  "sentCopyError": "raw message unavailable"
}
```

A follow-up IMAP append may also fail with:

```text
(b.flags || []).includes is not a function
```

## Durable fix pattern

1. Do **not** re-send the email just to create a Sent copy. The message has already been delivered.
2. Build the MIME message locally with Nodemailer's stream transport, then append that raw buffer to the detected Sent mailbox through IMAP:

```js
const builder = nodemailer.createTransport({
  streamTransport: true,
  buffer: true,
  newline: 'unix'
});
const built = await builder.sendMail(mail);
const raw = Buffer.isBuffer(built.message)
  ? built.message
  : Buffer.from(String(built.message || ''));
await client.append(sentMailbox, raw, ['\\Seen'], new Date());
```

3. When inspecting IMAP mailbox flags from `imapflow`, normalize flags with `Array.from(...)`; they may be a `Set`, not an Array:

```js
const sent = boxes.find(b => Array.from(b.flags || []).includes('\\Sent'))
  || boxes.find(b => /sent|已发送|寄件|发件/i.test(b.path));
```

## Reporting

If delivery succeeded first and Sent-copy was appended afterwards, report both facts clearly:

- SMTP delivery: successful, with `messageId`, `response`, `accepted`, `rejected`.
- Sent copy: appended via IMAP follow-up, with `sentMailbox`.

Do not overwrite the fact that the first SMTP delivery succeeded; only update local send metadata to reflect the follow-up Sent-copy append.
