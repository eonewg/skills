# Hermes post-change check

Use after changing Hermes config, source code, cron jobs, scripts, or operational skills.

## Script

`~/.hermes/scripts/hermes_postchange_check.sh`

## What it checks

- `hermes config check`
- whether any `auxiliary.*.provider` remains `auto`
- cron task errors and `last_delivery_error`
- cron delivery watchdog presence
- Python script compilation for known watchdog scripts
- no untracked backup/temp files inside the Hermes repo
- gateway running status
- targeted pytest based on touched source files
- restart-needed reminder when source changes touch runtime areas

## Usage

```bash
~/.hermes/scripts/hermes_postchange_check.sh --tests auto
~/.hermes/scripts/hermes_postchange_check.sh --tests off
~/.hermes/scripts/hermes_postchange_check.sh --tests full
```

Default is `--tests auto`. Current mappings include:

- `tools/delegate_tool.py` -> delegate tool tests
- `cron/*.py` -> cron tests
- config-related `hermes_cli` files -> hermes_cli tests

## Interpretation

- Exit code `0` means no hard failures.
- Warnings are allowed when they reflect known existing state, e.g. an old cron `last_status=error`, a current `last_delivery_error`, or a restart reminder after source changes.
- After source/config/tool changes, restart the gateway or CLI before expecting live sessions to use new code.

## Proven 2026-07-08 run

`hermes_postchange_check.sh --tests auto` exited 0. It passed config check, confirmed auxiliary auto routes are gone, verified the cron delivery watchdog exists, compiled scripts, found no repo-local backup/temp files, confirmed gateway is running, and ran targeted delegate tests successfully. It produced warnings for known cron/delivery state and source-change restart reminder.
