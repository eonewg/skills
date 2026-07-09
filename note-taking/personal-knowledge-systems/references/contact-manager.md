---
name: contact-manager
description: Manage contacts (name, email, notes) and send emails to saved contacts. Use when user wants to add a contact, view contacts, or send email to a saved contact. Triggers on phrases like "添加联系人", "保存邮箱", "发给XXX", "查看联系人", "contact", "email contact".
---

# Contact Manager

Manage contacts and send emails to saved contacts.

## Features

- Add contacts with name, email, and optional notes
- View all saved contacts
- Send emails to contacts by name
- Data stored in skill's data directory

## Data Storage

Contacts are stored in: `data/contacts.json`

Format:
```json
{
  "contacts": [
    {
      "name": "张三",
      "email": "zhangsan@example.com",
      "notes": "同事，技术部"
    }
  ]
}
```

## Usage

### Add Contact

```bash
python3 scripts/add_contact.py "姓名" "邮箱" "备注(可选)"
```

### List Contacts

```bash
python3 scripts/list_contacts.py
```

### Send Email to Contact

**Using contact name directly (recommended):**
```bash
python3 scripts/send_email.py "联系人姓名" "邮件主题" "邮件内容"
```

**With HTML:**
```bash
python3 scripts/send_email.py "张三" "Newsletter" "<h1>Hello</h1>" --html
```

**With attachment:**
```bash
python3 scripts/send_email.py "张三" "Report" "Please find attached" --attach report.pdf
```

This command automatically:
1. Looks up the contact's email from contacts.json
2. Calls imap-smtp-email skill to send the email
3. Reports success/failure

**Prerequisite:** imap-smtp-email skill must be configured with SMTP credentials.

## Workflow

1. When user wants to add a contact:
   - Run `scripts/add_contact.py` with name, email, optional notes
   - Confirm success to user

2. When user wants to view contacts:
   - Run `scripts/list_contacts.py`
   - Display formatted list

3. When user wants to email a saved contact:
   - Run `scripts/send_email.py <name> <subject> <body>` to auto-lookup and send
   - Or look up contact manually with `scripts/get_contact.py`, then use imap-smtp-email
   - If contact not found, notify user
