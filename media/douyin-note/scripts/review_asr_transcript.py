#!/usr/bin/env python3
"""Review and lightly correct ASR transcripts for media-note workflows.

This is a deterministic post-ASR pass: it does not invent missing content. It uses
source metadata (title/chapters) plus a conservative glossary to normalize common
ASR mistakes in AI/engineering videos, then writes corrected transcript artifacts
and a correction report for human/agent review.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_GLOSSARY: list[tuple[str, str, str]] = [
    (r"\bCore\s+Engine\b", "Query Engine", "AI Agent module list / query engine"),
    (r"\bqueryengine\b", "Query Engine", "normalize casing"),
    (r"\bAI\s*agent\b", "AI Agent", "normalize casing"),
    (r"\bagent\b", "Agent", "normalize casing when standalone"),
    (r"\breact\b", "ReAct", "Agent loop term"),
    (r"\breasoning\b", "Reasoning", "ReAct term"),
    (r"\baction\b", "Action", "ReAct term"),
    (r"\btools\b", "Tools", "module name"),
    (r"\bTOS\b", "Tools", "ASR misrecognition of Tools"),
    (r"\bSkills\b", "Skills", "module name"),
    (r"\bskills\b", "Skills", "module name"),
    (r"\bmemory\b", "Memory", "module name"),
    (r"\bcontext\b", "Context", "module name"),
    (r"\bpermission\b", "Permission", "module name"),
    (r"\bsubagent\b", "Subagent", "module name"),
    (r"\bsessions\b", "Sessions", "module name"),
    (r"\bcommand\b", "Command", "module name"),
    (r"\bhook\b", "Hook", "module name"),
    (r"\bHulk\b", "Hook", "ASR misrecognition of Hook"),
    (r"\bClaude\s*code\b", "Claude Code", "product name"),
    (r"\bnode\s*js\b", "Node.js", "tech stack"),
    (r"\btouch\s*script\b", "TypeScript", "tech stack"),
    (r"\bluncheon\b", "LangChain", "tech stack"),
    (r"\blang\s*chain\b", "LangChain", "tech stack"),
    (r"\blong\s*graph\b", "LangGraph", "tech stack"),
    (r"\blang\s*graph\b", "LangGraph", "tech stack"),
    (r"\bcyclize\b", "SQLite", "storage engine"),
    (r"\bsql\s*lite\b", "SQLite", "storage engine"),
    (r"知\s*talk", "智 Talk", "project name"),
    (r"知语", "智语", "project name"),
    (r"\bslash\s*command\b", "Slash Command", "command type"),
    (r"\bsystem\s*command\b", "System Command", "command type"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path | None) -> Any:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def apply_glossary(text: str, glossary: list[tuple[str, str, str]]) -> tuple[str, list[dict[str, Any]]]:
    changes: list[dict[str, Any]] = []
    corrected = text
    for pattern, replacement, reason in glossary:
        flags = re.IGNORECASE if pattern.startswith("\\b") else 0
        changed = 0

        def repl(match: re.Match[str]) -> str:
            nonlocal changed
            original = match.group(0)
            if original == replacement:
                return original
            changed += 1
            return replacement

        corrected = re.sub(pattern, repl, corrected, flags=flags)
        if changed:
            changes.append({"pattern": pattern, "replacement": replacement, "count": changed, "reason": reason})
    # Clean repeated filler spacing but preserve Chinese punctuation.
    before = corrected
    corrected = re.sub(r"[ \t]{2,}", " ", corrected)
    corrected = re.sub(r"\s+([，。！？；：])", r"\1", corrected)
    corrected = re.sub(r"([，。！？；：])\s+", r"\1", corrected)
    if corrected != before:
        changes.append({"pattern": "spacing", "replacement": "normalized spaces around punctuation", "count": 1, "reason": "readability"})
    return corrected, changes


def glossary_from_metadata(metadata: Any) -> list[tuple[str, str, str]]:
    glossary = list(DEFAULT_GLOSSARY)
    if not isinstance(metadata, dict):
        return glossary
    title = metadata.get("title") or metadata.get("desc") or ""
    if "AI Agent" in title or "Agent" in title:
        glossary.extend([
            (r"\bAI\s*Agent\b", "AI Agent", "source title keyword"),
        ])
    chapters = metadata.get("chapters")
    if isinstance(chapters, list):
        for ch in chapters:
            if not isinstance(ch, dict):
                continue
            title = str(ch.get("title", ""))
            detail = str(ch.get("detail", ""))
            if "查询引擎" in title or "query" in detail.lower():
                glossary.append((r"\bCore\s+Engine\b", "Query Engine", "chapter says 查询引擎 / query engine"))
            if "技术栈" in title or "lang" in detail.lower():
                glossary.extend([
                    (r"\btouch\s*script\b", "TypeScript", "chapter tech stack"),
                    (r"\bluncheon\b", "LangChain", "chapter tech stack"),
                    (r"\blong\s*graph\b", "LangGraph", "chapter tech stack"),
                ])
    return glossary


def correct_utterances(utterances: Any, glossary: list[tuple[str, str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(utterances, list):
        return [], []
    corrected: list[dict[str, Any]] = []
    all_changes: list[dict[str, Any]] = []
    for idx, utt in enumerate(utterances):
        if not isinstance(utt, dict):
            continue
        new_utt = json.loads(json.dumps(utt, ensure_ascii=False))
        text = str(new_utt.get("text", ""))
        new_text, changes = apply_glossary(text, glossary)
        new_utt["text"] = new_text
        corrected.append(new_utt)
        for ch in changes:
            all_changes.append({"utterance_index": idx, **ch})
    return corrected, all_changes


def ms_to_stamp(ms: Any) -> str:
    if not isinstance(ms, (int, float)) or ms < 0:
        return "--:--"
    total = int(ms // 1000)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def write_outputs(
    out_dir: Path,
    corrected_text: str,
    corrected_utterances: list[dict[str, Any]],
    report: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "transcript_corrected.txt").write_text(corrected_text.rstrip() + "\n", encoding="utf-8")
    if corrected_utterances:
        (out_dir / "utterances_corrected.json").write_text(json.dumps(corrected_utterances, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "correction_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md: list[str] = [
        "# ASR 核对与纠正文稿",
        "",
        "## Correction Summary",
        "",
        f"- original_chars: {report.get('original_chars')}",
        f"- corrected_chars: {report.get('corrected_chars')}",
        f"- correction_rules_hit: {report.get('correction_rules_hit')}",
        f"- utterance_count: {report.get('utterance_count')}",
        "",
        "## Correction Rules Hit",
        "",
    ]
    for item in report.get("rule_counts", []):
        md.append(f"- `{item['replacement']}` × {item['count']} — {item['reason']}")
    if corrected_utterances:
        md.extend(["", "## Corrected Utterances", ""])
        for utt in corrected_utterances:
            md.append(f"- [{ms_to_stamp(utt.get('start_time'))}] {utt.get('text', '')}")
    md.extend(["", "## Corrected Transcript", "", corrected_text.rstrip(), ""])
    (out_dir / "transcript_corrected.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review/correct ASR transcript with conservative glossary and metadata hints.")
    parser.add_argument("--transcript", required=True, help="Raw transcript.txt path")
    parser.add_argument("--utterances", default="", help="Optional utterances.json path")
    parser.add_argument("--metadata", default="", help="Optional source metadata JSON path")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--extra-glossary", default="", help="Optional JSON list of {pattern,replacement,reason}")
    args = parser.parse_args()

    transcript_path = Path(args.transcript).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    original = read_text(transcript_path)
    metadata = load_json(Path(args.metadata).expanduser().resolve()) if args.metadata else None
    glossary = glossary_from_metadata(metadata)
    if args.extra_glossary:
        extra = load_json(Path(args.extra_glossary).expanduser().resolve())
        if isinstance(extra, list):
            for item in extra:
                if isinstance(item, dict) and item.get("pattern") and item.get("replacement"):
                    glossary.append((str(item["pattern"]), str(item["replacement"]), str(item.get("reason", "extra glossary"))))
    corrected_text, text_changes = apply_glossary(original, glossary)
    utterances = load_json(Path(args.utterances).expanduser().resolve()) if args.utterances else None
    corrected_utterances, utt_changes = correct_utterances(utterances, glossary)

    counter: Counter[tuple[str, str]] = Counter()
    reason_map: dict[tuple[str, str], str] = {}
    for ch in text_changes:
        key = (ch["pattern"], ch["replacement"])
        counter[key] += int(ch.get("count", 0))
        reason_map[key] = ch.get("reason", "")
    rule_counts = [
        {"pattern": pat, "replacement": repl, "count": count, "reason": reason_map.get((pat, repl), "")}
        for (pat, repl), count in counter.most_common()
    ]
    report = {
        "source_transcript": str(transcript_path),
        "source_utterances": str(Path(args.utterances).expanduser().resolve()) if args.utterances else None,
        "source_metadata": str(Path(args.metadata).expanduser().resolve()) if args.metadata else None,
        "original_chars": len(original),
        "corrected_chars": len(corrected_text),
        "correction_rules_hit": len(rule_counts),
        "utterance_count": len(corrected_utterances),
        "rule_counts": rule_counts,
        "note": "Conservative glossary pass only; final notes should still be checked against video metadata/chapters and visible context.",
    }
    write_outputs(out_dir, corrected_text, corrected_utterances, report)
    print(json.dumps({"ok": True, "out_dir": str(out_dir), "correction_rules_hit": len(rule_counts), "utterance_count": len(corrected_utterances)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
