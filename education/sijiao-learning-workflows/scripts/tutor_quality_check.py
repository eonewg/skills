#!/usr/bin/env python3
"""Structure check for the user private-tutor workspaces.

Usage:
  python3 tutor_quality_check.py ~/teach/<topic>
"""
import json
import sys
from pathlib import Path

REQUIRED = ["MISSION.md", "curriculum.json", "learner-state.example.json"]
OPTIONAL_DIRS = ["lessons", "learning-records", "references"]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 tutor_quality_check.py ~/teach/<topic>")
        return 2
    root = Path(sys.argv[1])
    print(f"Checking: {root}")
    ok = True
    if not root.exists():
        print("FAIL workspace missing")
        return 2
    for name in REQUIRED:
        path = root / name
        exists = path.exists()
        print(("PASS" if exists else "FAIL") + f" {name}")
        ok = ok and exists
    for name in OPTIONAL_DIRS:
        path = root / name
        if path.exists():
            print(f"PASS {name}/")
        else:
            print(f"WARN {name}/ missing")
    cpath = root / "curriculum.json"
    if cpath.exists():
        try:
            data = json.loads(cpath.read_text(encoding="utf-8"))
            modules = data.get("modules", []) if isinstance(data, dict) else []
            print(f"PASS curriculum json parse; modules={len(modules)}")
            if not modules:
                print("WARN curriculum has no modules")
            for i, m in enumerate(modules):
                missing = [k for k in ("id", "title", "practice", "mastery_evidence") if k not in m]
                if missing:
                    print(f"WARN module[{i}] missing {','.join(missing)}")
        except Exception as e:
            print(f"FAIL curriculum json parse: {e}")
            ok = False
    print("Result: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
