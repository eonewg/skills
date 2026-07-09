#!/usr/bin/env python3
"""Add a contact to the contact list."""

import json
import sys
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")


def ensure_data_dir():
    """Ensure data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


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


def add_contact(name, email, notes=""):
    """Add a new contact."""
    ensure_data_dir()
    data = load_contacts()

    # Check if contact already exists
    for contact in data["contacts"]:
        if contact["name"] == name:
            print(f"Error: Contact '{name}' already exists with email {contact['email']}")
            print("Use a different name or delete the existing contact first.")
            sys.exit(1)

    # Add new contact
    contact = {
        "name": name,
        "email": email,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    data["contacts"].append(contact)
    save_contacts(data)

    print(f"✅ Added contact: {name} <{email}>")
    if notes:
        print(f"   Notes: {notes}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add_contact.py <name> <email> [notes]")
        sys.exit(1)

    name = sys.argv[1]
    email = sys.argv[2]
    notes = sys.argv[3] if len(sys.argv) > 3 else ""

    add_contact(name, email, notes)
