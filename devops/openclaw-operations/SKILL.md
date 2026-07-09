---
name: openclaw-operations
description: "Operate and maintain a local OpenClaw installation: update, back up, verify gateway/systemd health, and handle common post-update warnings."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, wsl]
metadata:
  hermes:
    tags: [OpenClaw, gateway, npm, systemd, update, backup]
---

# OpenClaw Operations

Use this when the user asks to update, repair, verify, or inspect OpenClaw. This is for OpenClaw itself, not Hermes Agent; keep the identity boundary clear.

## Core rules

- Prefer live checks over remembered versions or paths. Memory can hint that OpenClaw exists, but always verify with `which openclaw`, `openclaw --version`, and package/update status.
- Before a write/update, create a real backup and verify it. If state is large, prefer OpenClaw's built-in backup with `--no-include-workspace` unless the user explicitly wants workspaces included.
- After updating, verify the actual running artifact, not just the install command exit code: CLI version, npm global package, systemd service status, listening port, and `openclaw health`/`openclaw status`.
- Preserve operator-owned configuration such as systemd drop-ins/proxy settings. Do not overwrite custom service directives unless update/doctor explicitly requires it or the user asked.
- Keep final reports concise: version before/after, backup path, gateway health, and any non-blocking warnings.

## Standard update workflow

1. Discover current installation:

```bash
which openclaw || true
readlink -f ~/.npm-global/bin/openclaw 2>/dev/null || true
openclaw --version
npm config get prefix 2>/dev/null || true
npm list -g --depth=0 2>/dev/null | grep -i openclaw || true
```

2. Check available channel/version and preview actions:

```bash
npm view openclaw version dist-tags --json
openclaw update status --json
openclaw update --dry-run --json
```

3. Inspect current gateway service when relevant:

```bash
systemctl --user status openclaw-gateway.service --no-pager
```

4. Create and verify a backup before updating:

```bash
mkdir -p ~/.openclaw-backups
openclaw backup create --output ~/.openclaw-backups --no-include-workspace --verify --json
```

Use `--no-include-workspace` by default because OpenClaw workspaces/plugins can be large. If the update is risky or user requests everything, omit it.

5. Run non-interactive update:

```bash
openclaw update --yes --json
```

6. Verify result:

```bash
openclaw --version
npm list -g --depth=0 2>/dev/null | grep -i openclaw || true
systemctl --user is-active openclaw-gateway.service
systemctl --user status openclaw-gateway.service --no-pager
ss -ltnp | grep ':18789' || true
openclaw health --json
openclaw status --json
openclaw update status --json
```

7. If doctor warns that `~/.openclaw` permissions are too open, tightening to owner-only is safe:

```bash
chmod 700 ~/.openclaw
stat -c '%a %n' ~/.openclaw
```

## Post-update service drift

`openclaw update` may report that the gateway service was installed by an older OpenClaw version and suggest `openclaw gateway install --force`. Treat this as a warning first, not an automatic destructive step:

- Check whether the service actually restarted into the new version via `systemctl --user status` and `openclaw status --json`.
- Check any drop-ins under `~/.config/systemd/user/openclaw-gateway.service.d/` before overwriting the unit.
- Only run `openclaw gateway install --force` when the service remains stale/broken or the user accepts replacing OpenClaw-owned service directives.

## Common non-blocking warnings

- Legacy state migration warnings like “SQLite rows already exist; left legacy source in place” usually mean compatibility migration skipped duplicate import. Report as non-blocking unless health/status is failing.
- Plugin install index conflicts can appear after migrations. Verify plugin load errors via `openclaw health --json`; if `plugins.errors` is empty, do not over-fix.
- Weixin `session expired` warnings are channel-login state, not proof the gateway update failed. Report separately and avoid treating it as core update failure.
- Plaintext secret warnings are important but not part of a routine version update unless the user asks for security hardening.

## References

- `references/openclaw-update-2026-06.md` — concrete WSL/npm/systemd update transcript pattern and interpretation notes from a successful version bump.

## Verification checklist for final response

- State exact before/after versions from command output.
- Include backup archive path if one was created.
- Confirm gateway service is `active/running` and health is OK.
- Mention non-blocking warnings separately and briefly.
- Do not include Markdown tables in Feishu replies; use bullets.