#!/usr/bin/env python3
"""Verify one `~/wiki` raw→formal ingestion.

Usage:
  python3 scripts/verify_user_wiki_ingest.py \
    --wiki ~/wiki \
    --raw raw/articles/example-2026.md \
    --page concepts/example.md \
    --link '[[example]]'

This complements `scripts/wiki_lint.py`: lint checks global schema/link health;
this script checks the newly ingested raw file's hash, manifest entry, index link,
formal-page existence, and whether updated pages have dangling raw sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, body


def raw_sources_in_frontmatter(text: str) -> list[str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    sm = re.search(r"sources:\s*\[(.*?)\]", m.group(1), re.S)
    if not sm:
        return []
    return [x.strip() for x in sm.group(1).split(",") if x.strip().startswith("raw/")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="~/wiki")
    ap.add_argument("--raw", required=True, help="Raw path relative to wiki root")
    ap.add_argument("--page", required=True, help="Formal page path relative to wiki root")
    ap.add_argument("--link", required=True, help="Expected wikilink, e.g. [[my-page]]")
    ap.add_argument("--updated", nargs="*", default=[], help="Additional updated page paths to check for dangling raw sources")
    args = ap.parse_args()

    root = Path(args.wiki)
    raw_path = root / args.raw
    page_path = root / args.page
    manifest_path = root / ".manifest.json"
    index_path = root / "index.md"

    failures: list[str] = []
    report: dict[str, object] = {}

    if not raw_path.exists():
        failures.append(f"missing raw: {args.raw}")
    else:
        fm, body = parse_frontmatter(raw_path.read_text(encoding="utf-8"))
        calc = hashlib.sha256(body.encode("utf-8")).hexdigest()
        stored = fm.get("sha256")
        report["raw_sha_stored"] = stored
        report["raw_sha_calc"] = calc
        report["raw_sha_matches"] = stored == calc
        if stored != calc:
            failures.append("raw frontmatter sha256 does not match body hash")
        if fm.get("source_author") in {None, "", "***", "unknown", "未知"}:
            failures.append("source_author is missing/placeholder; preserve extractor author/account when known")

    report["page_exists"] = page_path.exists()
    if not page_path.exists():
        failures.append(f"missing formal page: {args.page}")

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = manifest.get("raw_files", {}).get(args.raw)
        report["manifest_has_raw"] = bool(entry)
        if not entry:
            failures.append("manifest missing raw entry")
        elif raw_path.exists():
            report["manifest_sha_matches"] = entry.get("sha256") == report.get("raw_sha_calc")
            if entry.get("sha256") != report.get("raw_sha_calc"):
                failures.append("manifest sha does not match recomputed raw body hash")
    else:
        failures.append("missing .manifest.json")

    if index_path.exists():
        count = index_path.read_text(encoding="utf-8").count(args.link)
        report["index_link_count"] = count
        if count != 1:
            failures.append(f"expected exactly one index link {args.link}, found {count}")
    else:
        failures.append("missing index.md")

    dangling: list[tuple[str, str]] = []
    for rel in [args.page, *args.updated, "hot.md"]:
        p = root / rel
        if not p.exists():
            continue
        for src in raw_sources_in_frontmatter(p.read_text(encoding="utf-8")):
            if not (root / src).exists():
                dangling.append((rel, src))
    report["dangling_raw_sources"] = dangling
    if dangling:
        failures.append("one or more updated pages cite missing raw sources")

    report["ok"] = not failures
    report["failures"] = failures
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
