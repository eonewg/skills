#!/usr/bin/env python3
"""Lightweight validator for teach HTML pages."""
from __future__ import annotations
import re
import sys
from pathlib import Path

REQUIRED = [
    'katex.min.css',
    'katex.min.js',
    'auto-render.min.js',
]
# Local lesson assets may be linked during authoring or inlined for Feishu attachment delivery.
# Accept both old (Kaoyan Teaching...) and new (Teach...) inline markers for migration.
LOCAL_ASSET_REQUIREMENTS = [
    ('teach-components.css', ['Teach Web Lesson Components', 'Kaoyan Teaching Web Lesson Components']),
    ('teach-lesson.js', ['Teach Web Lesson JS', 'Kaoyan Teaching Web Lesson JS']),
]
BAD_FORMULA_PATTERNS = [
    'e^(-∫',
    '∫Pdx',
    'Qe^(',
]

def validate(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    errors = []
    for item in REQUIRED:
        if item not in text:
            errors.append(f'missing required asset: {item}')
    for linked_name, inline_markers in LOCAL_ASSET_REQUIREMENTS:
        if linked_name not in text and not any(m in text for m in inline_markers):
            errors.append(f'missing required local asset: {linked_name} or inline marker')
    if not re.search(r'<body[^>]+class="[^"]*theme-(math|cs|english|politics)', text):
        errors.append('missing subject theme class on <body>')
    if '\\(' not in text and '\\[' not in text:
        errors.append('no LaTeX delimiters found')
    if 'renderMathInElement' in text and ('left: "\\["' in text or 'left: "\\("' in text):
        errors.append('broken KaTeX JS delimiter escaping: inline script must use "\\\\[" / "\\\\(" so browsers match literal LaTeX delimiters')
    for bad in BAD_FORMULA_PATTERNS:
        if bad in text:
            errors.append(f'ugly raw formula pattern found: {bad}')
    if '<section class="section"' not in text:
        errors.append('missing section components')
    return errors

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('usage: validate-template.py FILE.html [FILE.html ...]')
        return 2
    failed = False
    for arg in argv[1:]:
        path = Path(arg)
        errors = validate(path)
        if errors:
            failed = True
            print(f'FAIL {path}')
            for e in errors:
                print(f'  - {e}')
        else:
            print(f'OK   {path}')
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
