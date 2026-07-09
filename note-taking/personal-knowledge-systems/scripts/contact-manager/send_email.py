#!/usr/bin/env python3
"""Send email to a saved contact using imap-smtp-email skill."""

import json
import os
import sys
import subprocess

# Contact manager paths
CONTACT_MANAGER_DIR = os.path.dirname(os.path.dirname(__file__))
CONTACTS_FILE = os.path.join(CONTACT_MANAGER_DIR, "data", "contacts.json")

# IMAP/SMTP skill paths (try multiple locations)
SKILLS_DIR = os.path.dirname(CONTACT_MANAGER_DIR)
IMAP_SMTP_DIR = os.path.join(SKILLS_DIR, "imap-smtp-email")

# Fallback to workspace skills
if not os.path.exists(IMAP_SMTP_DIR):
    WORKSPACE_SKILLS = "/root/.openclaw/workspace/skills"
    IMAP_SMTP_DIR = os.path.join(WORKSPACE_SKILLS, "imap-smtp-email")

SMTP_SCRIPT = os.path.join(IMAP_SMTP_DIR, "scripts", "smtp.js")


def load_contacts():
    """Load contacts from file."""
    if not os.path.exists(CONTACTS_FILE):
        return {"contacts": []}
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_contact(name):
    """Find contact by name (case-insensitive partial match)."""
    data = load_contacts()
    contacts = data.get("contacts", [])

    # Exact match first
    for contact in contacts:
        if contact["name"].lower() == name.lower():
            return contact

    # Partial match
    for contact in contacts:
        if name.lower() in contact["name"].lower():
            return contact

    return None


def send_email_to_contact(contact_name, subject, body, html=False, attachments=None):
    """Send email to a contact by name."""
    # Find contact
    contact = find_contact(contact_name)
    if not contact:
        print(f"❌ Contact not found: {contact_name}")
        print("Use 'python3 list_contacts.py' to see saved contacts.")
        sys.exit(1)

    email = contact["email"]
    print(f"📧 Sending email to {contact['name']} <{email}>...")

    # Build SMTP command
    cmd = [
        "node", SMTP_SCRIPT, "send",
        "--to", email,
        "--subject", subject,
        "--body", body
    ]

    if html:
        cmd.append("--html")

    if attachments:
        cmd.extend(["--attach", attachments])

    # Execute command
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=IMAP_SMTP_DIR)
        stdout = result.stdout.decode('utf-8') if result.stdout else ''
        stderr = result.stderr.decode('utf-8') if result.stderr else ''

        if result.returncode == 0:
            print(f"✅ Email sent successfully to {contact['name']}!")
            print(f"   Subject: {subject}")
            return True
        else:
            print(f"❌ Failed to send email:")
            print(stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 send_email.py <contact_name> <subject> <body> [--html] [--attach file]")
        print()
        print("Examples:")
        print('  python3 send_email.py "张三" "Hello" "How are you?"')
        print('  python3 send_email.py "张三" "Report" "See attached" --attach report.pdf')
        print('  python3 send_email.py "张三" "News" "<h1>Hi</h1>" --html')
        sys.exit(1)

    contact_name = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]

    html = "--html" in sys.argv

    attachments = None
    if "--attach" in sys.argv:
        attach_idx = sys.argv.index("--attach")
        if attach_idx + 1 < len(sys.argv):
            attachments = sys.argv[attach_idx + 1]

    success = send_email_to_contact(contact_name, subject, body, html, attachments)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
