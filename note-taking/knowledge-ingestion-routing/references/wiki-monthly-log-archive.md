# Wiki monthly log archive automation

Use this when maintaining the user's `~/wiki/log.md` growth.

## Current operating model

- `log.md` is the current-month / rolling entry point, not the permanent all-history ledger.
- Historical months are archived under `log/YYYY-MM.md`.
- Monthly archival is automated by a no-agent cron job created in the 2026-06-22 session.

## Files

- Deterministic script: `~/wiki/scripts/wiki_log_monthly_archive.py`
- Hermes cron wrapper: `~/.hermes/scripts/wiki_log_monthly_archive.sh`
- Cron job name: `wiki-log-monthly-archive`
- Schedule: `10 0 1 * *` (monthly on day 1 at 00:10 Asia/Shanghai)
- Workdir: `~/wiki`
- Mode: `no_agent=True`, silent on success, alerts only on non-zero exit.

## Behavior

The script:

1. Parses `log.md` lines matching `- \`YYYY-MM-DD\` ...`.
2. Moves entries older than the current month into `log/YYYY-MM.md`.
3. Deduplicates archive entries so reruns are idempotent.
4. Rewrites `log.md` with the historical month index and the current-month section.
5. Runs `scripts/wiki_lint.py` when invoked through the wrapper.

## Verification pattern

Before changing this workflow, verify with:

```bash
cd ~/wiki
python3 scripts/wiki_log_monthly_archive.py --dry-run
python3 scripts/wiki_log_monthly_archive.py --today 2026-07-01 --dry-run
~/.hermes/scripts/wiki_log_monthly_archive.sh
python3 scripts/wiki_lint.py
```

Expected successful behavior from the original test:

- Same-month dry run: `no-op: no months older than 2026-06 in log.md`
- Simulated 2026-07-01 dry run: archives June entries to `log/2026-06.md`
- Wrapper success is silent.
- `wiki_lint.py` should report `issue_count: 0`, `warning_count: 0`.

## Pitfalls

- Do not create daily log files unless the user explicitly asks; monthly granularity is the chosen balance.
- Do not make this LLM-driven; it is deterministic maintenance and should stay `no_agent=True`.
- Do not report success from cron creation alone; run the wrapper once and lint once.
