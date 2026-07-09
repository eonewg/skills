# Weekly English Digest Cron Collector

Use this when maintaining the user's `weekly-english-digest-to-wiki` cron job.

## Pattern

- Keep the cron as an LLM-driven wiki distillation job (`no_agent: false`), but attach a deterministic pre-run script via the cron `script` field.
- The script should be read-only and output compact Markdown context for the LLM:
  - Asia/Shanghai date range.
  - One canonical `.txt` per date.
  - Same-day version priority: `daily-english-YYYY-MM-DD-resend-latest.txt` → `daily-english-YYYY-MM-DD-resend.txt` → `daily-english-YYYY-MM-DD.txt`.
  - Ignored alternatives, sha256, size, and missing dates.
  - Compact high-signal extracts from sections 04/05/06 plus relevant expressions, sentence patterns, paragraphs, and active-recall prompts.
- Do not let the cron agent rescan every output file unless a listed canonical file is unreadable.
- If the collector prints `[SILENT]`, the agent should final-answer `[SILENT]` and write nothing.

## Live implementation

- Collector path: `~/.hermes/scripts/weekly_english_digest_collect.py`
- Cron job: `weekly-english-digest-to-wiki` / `c9418d75ba09`
- Workdir: `~/wiki`
- Model/provider currently pinned: Ark `glm-5-2-260617`
- Enabled toolsets: `file`, `terminal`, `skills`

## Verification commands

```bash
python3 -m py_compile ~/.hermes/scripts/weekly_english_digest_collect.py
~/.hermes/scripts/weekly_english_digest_collect.py --end-date 2026-07-07 > /tmp/weekly_english_digest_collect_test.md
python3 - <<'PY'
from pathlib import Path
s=Path('/tmp/weekly_english_digest_collect_test.md').read_text()
print('chars', len(s), 'sources', s.count('## SOURCE '))
print('\n'.join(s.splitlines()[:18]))
PY
```

For cron config verification:

```bash
python3 - <<'PY'
import json
from pathlib import Path
j=json.loads(Path('~/.hermes/cron/jobs.json').read_text())
for job in j['jobs']:
    if job['id']=='c9418d75ba09':
        for k in ['script','no_agent','schedule_display','provider','model','enabled_toolsets','workdir']:
            print(k, job.get(k))
PY
```

## Pitfalls

- Do not run the cron immediately just to test it unless the user explicitly wants a backfill; it may archive a partial current week and move selected source files to Trash.
- The script is intentionally read-only. File movement happens only inside the cron agent after wiki build/lint/query/weekly-health all pass.
- Keep `05 今日高级连接词` and `06 自然高级替换` as separate source categories in the final wiki digest.
