# Cron delivery-error watchdog

Use when a Hermes cron job shows `last_status: ok` but has `last_delivery_error` set, meaning the task body likely completed but delivery back to a chat platform failed.

## Proven workflow

1. Inspect cron state with `cronjob(action="list")` or read `~/.hermes/cron/jobs.json`.
2. Confirm the error in logs:
   ```bash
   grep -R "last_delivery_error\|delivery error\|cannot schedule new futures" -n ~/.hermes/logs ~/.hermes/cron 2>/dev/null | tail -80
   ```
3. Add or maintain a no-agent watchdog script under `~/.hermes/scripts/` that:
   - reads `~/.hermes/cron/jobs.json`,
   - prints nothing when no job has `last_delivery_error`,
   - prints a compact alert when one or more jobs have delivery errors,
   - fingerprints `(job_id, last_run_at, last_delivery_error)` to suppress duplicate alerts,
   - clears the reported fingerprint state when all delivery errors disappear.
4. Schedule it as a script-only cron job, e.g.:
   ```python
   cronjob(action="create", name="cron-delivery-error-watchdog", schedule="15 20 * * *", script="cron_delivery_watchdog.py", no_agent=True, deliver="origin", workdir="~/.hermes")
   ```
5. Verify:
   - `python3 -m py_compile ~/.hermes/scripts/cron_delivery_watchdog.py`
   - `~/.hermes/scripts/cron_delivery_watchdog.py --dry-run --no-dedupe` prints the active alert when one exists.
   - `cronjob(action="run", job_id="...")` records `last_status: ok` and `last_delivery_error: null` for the watchdog itself.
   - A second normal script run is silent for the same fingerprint.

## Notes

- Do not treat `last_status: ok` as sufficient cron health; `last_delivery_error` is a separate failure channel.
- `mark_job_run(..., delivery_error=...)` clears `last_delivery_error` on the next successful delivery for that job.
- A delivery error like `cannot schedule new futures after interpreter shutdown` points to gateway/platform adapter shutdown timing rather than the job body itself.
