#!/usr/bin/env python3
"""Inline local Teach Web Lesson CSS/JS into HTML pages for attachment delivery.

Authoring pages may link ../assets/*. When sharing an HTML file as an attachment,
relative assets do not travel with the HTML file, so the delivered file must be standalone.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPT_DIR.parent
CSS_PATH = PACKAGE_DIR / 'assets' / 'teach-components.css'
JS_PATH = PACKAGE_DIR / 'assets' / 'teach-lesson.js'


def inline_one(path: Path) -> bool:
    css = CSS_PATH.read_text(encoding='utf-8')
    js = JS_PATH.read_text(encoding='utf-8')
    css_block = '\n  <style>\n' + css + '\n  </style>'
    js_block = '\n  <script>\n' + js + '\n  </script>'

    html = path.read_text(encoding='utf-8')
    out = html
    out = re.sub(
        r'\s*<link rel="stylesheet" href="\.\./\.\./_templates/assets/teach-components\.css">',
        lambda _m: css_block,
        out,
    )
    out = re.sub(
        r'\s*<style>\s*/\* (Kaoyan )?Teach(ing)? (Web )?Lesson Components.*?</style>',
        lambda _m: css_block,
        out,
        flags=re.S,
    )
    out = re.sub(
        r'\s*<script defer src="\.\./\.\./_templates/assets/teach-lesson\.js"></script>',
        lambda _m: js_block,
        out,
    )
    out = re.sub(
        r'\s*<script>\s*// (Kaoyan )?Teach(ing)? (Web )?Lesson JS.*?</script>',
        lambda _m: js_block,
        out,
        flags=re.S,
    )
    if 'data-standalone="true"' not in out:
        out = out.replace('<html lang="zh-CN"', '<html lang="zh-CN" data-standalone="true"', 1)

    if out != html:
        path.write_text(out, encoding='utf-8')
        return True
    return False


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('usage: make-standalone.py FILE.html [FILE.html ...]')
        return 2
    changed = 0
    for arg in argv[1:]:
        path = Path(arg).expanduser().resolve()
        if inline_one(path):
            changed += 1
            print(f'UPDATED {path}')
        else:
            print(f'OK      {path}')
    print(f'changed {changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
