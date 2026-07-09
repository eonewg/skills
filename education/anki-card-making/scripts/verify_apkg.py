#!/usr/bin/env python3
"""Verify a generated Anki .apkg by reading zip + collection.anki2.

Usage:
  python scripts/verify_apkg.py /path/to/deck.apkg

Checks:
- file exists and is a valid zip
- contains collection.anki2
- SQLite can read notes/cards
- prints model names, note/card counts, sample Question fields, and media count
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

SEP = "\x1f"


def fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("expected exactly one .apkg path")

    apkg = Path(argv[1]).expanduser().resolve()
    if not apkg.exists():
        return fail(f"not found: {apkg}")
    if apkg.stat().st_size == 0:
        return fail(f"empty file: {apkg}")

    try:
        with zipfile.ZipFile(apkg) as zf:
            names = set(zf.namelist())
            if "collection.anki2" not in names:
                return fail("collection.anki2 missing")
            media_count = 0
            if "media" in names:
                try:
                    media = json.loads(zf.read("media").decode("utf-8"))
                    media_count = len(media)
                except Exception as exc:  # noqa: BLE001
                    return fail(f"media manifest unreadable: {exc}")
            with tempfile.TemporaryDirectory() as td:
                zf.extract("collection.anki2", td)
                db_path = Path(td) / "collection.anki2"
                con = sqlite3.connect(db_path)
                cur = con.cursor()
                note_count = cur.execute("select count(*) from notes").fetchone()[0]
                card_count = cur.execute("select count(*) from cards").fetchone()[0]
                models_json = cur.execute("select models from col").fetchone()[0]
                models = json.loads(models_json)
                model_names = [m.get("name", "<unnamed>") for m in models.values()]
                samples = cur.execute("select flds from notes limit 5").fetchall()
                con.close()
    except zipfile.BadZipFile:
        return fail("not a valid zip/apkg")
    except sqlite3.Error as exc:
        return fail(f"sqlite read failed: {exc}")
    except Exception as exc:  # noqa: BLE001
        return fail(f"verification failed: {exc}")

    print(f"APKG: {apkg}")
    print(f"Size: {apkg.stat().st_size} bytes")
    print(f"Models: {', '.join(model_names) if model_names else '<none>'}")
    print(f"Notes: {note_count}")
    print(f"Cards: {card_count}")
    print(f"Media files: {media_count}")
    print("Sample Question fields:")
    for i, (flds,) in enumerate(samples, 1):
        question = flds.split(SEP, 1)[0]
        question = question.replace("\n", " ").strip()
        print(f"  {i}. {question[:160]}")

    if note_count <= 0 or card_count <= 0:
        return fail("deck has no notes/cards")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
