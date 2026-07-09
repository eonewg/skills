#!/usr/bin/env python3
"""List all saved contacts."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")


def load_contacts():
    """Load contacts from file."""
    if not os.path.exists(CONTACTS_FILE):
        return {"contacts": []}
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_contacts():
    """Display all contacts."""
    data = load_contacts()
    contacts = data.get("contacts", [])

    if not contacts:
        print("No contacts saved yet.")
        print(f"Add contacts with: python3 scripts/add_contact.py <name> <email> [notes]")
        return

    print(f"📇 Contacts ({len(contacts)} total):\n")

    for i, contact in enumerate(contacts, 1):
        print(f"{i}. {contact['name']}")
        print(f"   Email: {contact['email']}")
        if contact.get("notes"):
            print(f"   Notes: {contact['notes']}")
        print()


if __name__ == "__main__":
    list_contacts()
