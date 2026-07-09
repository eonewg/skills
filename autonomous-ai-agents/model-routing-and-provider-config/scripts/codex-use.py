#!/usr/bin/env python3
"""Quickly choose the first credential in Hermes' openai-codex credential pool.

Install example:
  cp scripts/codex-use.py ~/.local/bin/codex-use && chmod +x ~/.local/bin/codex-use

Usage:
  codex-use list
  codex-use me
  codex-use friend
  codex-use friend --reset
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

AUTH = Path.home() / ".hermes" / "auth.json"
PROVIDER = "openai-codex"
ALIASES = {
    "me": "device_code",
    "mine": "device_code",
    "main": "device_code",
    "primary": "device_code",
    "1st": "device_code",
    "friend": "friend-codex",
    "backup": "friend-codex",
    "second": "friend-codex",
    "2nd": "friend-codex",
}
STATUS_KEYS = [
    "last_status",
    "last_status_at",
    "last_error_code",
    "last_error_reason",
    "last_error_message",
    "last_error_reset_at",
]


def load() -> dict:
    if not AUTH.exists():
        raise SystemExit(f"auth file not found: {AUTH}")
    return json.loads(AUTH.read_text())


def save(data: dict) -> None:
    AUTH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="auth.", suffix=".json", dir=str(AUTH.parent))
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, AUTH)


def pool(data: dict) -> list[dict]:
    p = data.setdefault("credential_pool", {}).setdefault(PROVIDER, [])
    if not isinstance(p, list) or not p:
        raise SystemExit(f"no {PROVIDER} credentials found; run: hermes auth list {PROVIDER}")
    return p


def show(entries: list[dict]) -> None:
    for i, e in enumerate(entries, 1):
        cur = " ← selected" if i == 1 else ""
        status = e.get("last_status") or "ok"
        print(f"#{i} {e.get('label') or ''} id={e.get('id') or ''} status={status}{cur}")


def find(entries: list[dict], raw: str) -> int:
    q = ALIASES.get(raw.lower(), raw).strip().lower()
    if q.isdigit():
        idx = int(q) - 1
        if 0 <= idx < len(entries):
            return idx
    matches = []
    for idx, e in enumerate(entries):
        vals = [str(e.get("label") or ""), str(e.get("id") or ""), str(e.get("source") or "")]
        if any(v.lower() == q for v in vals):
            matches.append(idx)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise SystemExit(f"ambiguous target: {raw}")
    raise SystemExit(f"no credential matching {raw!r}; run: codex-use list")


def main(argv: list[str]) -> int:
    reset_target = False
    args = []
    for a in argv[1:]:
        if a in {"--reset", "--reset-target"}:
            reset_target = True
        else:
            args.append(a)
    data = load()
    entries = pool(data)
    if not args or args[0] in {"list", "ls", "status"}:
        show(entries)
        return 0
    target = args[0]
    idx = find(entries, target)
    selected = entries.pop(idx)
    if reset_target:
        for k in STATUS_KEYS:
            selected[k] = None
    entries.insert(0, selected)
    for i, e in enumerate(entries):
        e["priority"] = i
    save(data)
    print(f"selected {PROVIDER}: {selected.get('label') or selected.get('id')}")
    show(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
