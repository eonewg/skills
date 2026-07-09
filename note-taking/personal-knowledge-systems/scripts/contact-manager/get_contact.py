#!/usr/bin/env python3
"""Get contact info by name."""

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


def get_contact(name):
    """Get contact by name (case-insensitive partial match)."""
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_contact.py <name>")
        sys.exit(1)

    name = sys.argv[1]
    contact = get_contact(name)

    if contact:
        print(json.dumps(contact, ensure_ascii=False))
    else:
        print(f"Contact not found: {name}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
