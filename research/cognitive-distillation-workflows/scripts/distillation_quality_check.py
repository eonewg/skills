#!/usr/bin/env python3
"""Section sanity check for generated cognitive-distillation skills.

Usage:
  python3 distillation_quality_check.py /path/to/SKILL.md
"""
import re
import sys
from pathlib import Path

REQUIRED = [
    ("frontmatter", r"\A---\n.*?\n---", re.S),
    ("answer/protocol", r"protocol|工作流|回答流程|operating mode|agentic", re.I),
    ("models/playbooks", r"心智模型|mental model|playbook|启发式|heuristic", re.I),
    ("dna/style", r"表达DNA|expression dna|field dna|风格|术语|glossary", re.I),
    ("anti-patterns/quality", r"反模式|anti-pattern|质量|quality|标准", re.I),
    ("boundaries", r"诚实边界|boundary|局限|限制|weak spot|uncertainty", re.I),
    ("sources/research", r"来源|source|references/research|research notes|调研", re.I),
]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 distillation_quality_check.py /path/to/SKILL.md")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL missing file: {path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    passed = 0
    print(f"Checking: {path}")
    for name, pattern, flags in REQUIRED:
        ok = bool(re.search(pattern, text, flags))
        print(("PASS" if ok else "FAIL") + f" {name}")
        passed += int(ok)
    print(f"Result: {passed}/{len(REQUIRED)}")
    return 0 if passed == len(REQUIRED) else 1

if __name__ == "__main__":
    raise SystemExit(main())
