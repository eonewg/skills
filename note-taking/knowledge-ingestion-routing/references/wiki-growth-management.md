# Wiki Growth Management

## Problem

Wiki files grow unboundedly as content is ingested. Without compaction:
- `log.md` becomes thousands of lines of repetitive entries
- `.manifest.json` accumulates redundant fields (`impacted_pages`, `source_url`, etc.) and mixed-type structures
- Both files become harder to maintain and slower to lint

## Log Compaction Protocol

### Format (compact)
```markdown
- `2026-06-17` **ingest** | GLM-5.2: Built for Long-Horizon Tasks — Z.ai 旗舰模型，1M context + IndexShare DSA + MTP speculative decoding，MIT 开源。
```

### Rules
1. One line per entry. No multi-line entries.
2. Fields: `date` | `action` | `subject` | one-line note.
3. Drop: Source URL, Raw captured, Created/Updated pages lists.
4. Archive trigger: When file exceeds 200 lines, move entries older than 30 days to `log/<YYYY-MM>.md`.
5. The `log.md` rolling window always contains the most recent 30 days + month index pointers.

### Example month index at bottom of log.md
```markdown
## History
- [2026-05](log/2026-05.md) — 42 entries
- [2026-04](log/2026-04.md) — 38 entries
```

## Manifest Compaction Protocol

### raw_files entry (canonical)
```json
{
  "sha256": "abc123...",
  "last_seen": "2026-06-17",
  "status": "unchanged"
}
```

Only three fields. No exceptions.

### operations entry (canonical)
```json
{
  "date": "2026-06-17",
  "action": "ingest",
  "subject": "GLM-5.2: Built for Long-Horizon Tasks",
  "note": "Z.ai 旗舰模型技术博客"
}
```

### Compaction script pattern
```python
import json

with open('~/wiki/.manifest.json', 'r') as f:
    data = json.load(f)

# Strip raw_files to 3 fields
new_raw = {}
for path, meta in data['raw_files'].items():
    new_raw[path] = {
        "sha256": meta["sha256"],
        "last_seen": meta.get("last_seen", ""),
        "status": meta.get("status", "unchanged")
    }

# Normalize operations
new_ops = []
for key, meta in data.get('operations', {}).items():
    if isinstance(meta, list):
        for item in meta:
            if isinstance(item, dict):
                new_ops.append({
                    "date": item.get("date", key[:10]),
                    "action": item.get("action", ""),
                    "subject": item.get("subject", key),
                    **({"note": item["note"]} if item.get("note") else {})
                })
    elif isinstance(meta, dict):
        new_ops.append({
            "date": meta.get("ingested", meta.get("date", "")),
            "action": meta.get("action", "ingest"),
            "subject": key,
            **({"note": meta["note"]} if meta.get("note") else {})
        })

new_ops.sort(key=lambda x: x.get("date", ""))

data["raw_files"] = new_raw
data["operations"] = new_ops

with open('~/wiki/.manifest.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

## When to compact
- Log: Every 15-20 ingests, check line count. If > 200, archive old entries.
- Manifest: Every 10-15 ingests, run compaction script.
- After any session that modifies wiki files, run `scripts/wiki_lint.py` and fix issues before claiming done.
