#!/usr/bin/env python3
"""Delete a contact by name."""

import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")


def load_contacts():
    """Load contacts from file."""
    if not os.path.exists(CONTACTS_FILE):
        return {"contacts": []}
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_contacts(data):
    """Save contacts to file."""
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_contact(name):
    """Delete contact by name."""
    data = load_contacts()
    contacts = data.get("contacts", [])

    for i, contact in enumerate(contacts):
        if contact["name"].lower() == name.lower():
            deleted = contacts.pop(i)
            save_contacts(data)
            print(f"✅ Deleted contact: {deleted['name']} <{deleted['email']}>")
            return True

    print(f"❌ Contact not found: {name}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 delete_contact.py <name>")
        sys.exit(1)

    name = sys.argv[1]
    success = delete_contact(name)
    sys.exit(0 if success else 1)
