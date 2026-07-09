# OpenClaw update session note: 2026-06-24

This reference captures the reusable pattern from updating a WSL OpenClaw install from `2026.6.8` to `2026.6.9`. Do not treat the exact versions as durable defaults; they are examples of the workflow.

## Observed install shape

- CLI entrypoint: `~/.npm-global/bin/openclaw`
- Package root: `~/.npm-global/lib/node_modules/openclaw`
- Global package manager: npm with prefix `~/.npm-global`
- Gateway service: user systemd unit `~/.config/systemd/user/openclaw-gateway.service`
- Gateway port: `18789` on loopback
- Backup directory used: `~/.openclaw-backups`

## Commands that worked

Discovery:

```bash
which openclaw || true
readlink -f ~/.npm-global/bin/openclaw 2>/dev/null || true
openclaw --version
npm config get prefix 2>/dev/null || true
npm list -g --depth=0 2>/dev/null | grep -i openclaw || true
npm view openclaw version dist-tags --json
openclaw update status --json
openclaw update --dry-run --json
```

Backup:

```bash
mkdir -p ~/.openclaw-backups
openclaw backup create --output ~/.openclaw-backups --no-include-workspace --verify --json
```

Update:

```bash
openclaw update --yes --json
```

Verification:

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

Permission hardening if doctor warns:

```bash
chmod 700 ~/.openclaw
stat -c '%a %n' ~/.openclaw
```

## Interpretation notes

- `openclaw update --dry-run --json` can trigger state-migration messages even though it is a dry run; distinguish noisy migration warnings from update failure.
- `openclaw update --yes --json` updated npm global package and synchronized bundled/npm plugins; plugin outcomes were embedded under `postUpdate.plugins`.
- Doctor may say service drift exists because the service file was installed by an older version. Verify actual service runtime before forcing reinstall.
- A healthy post-update state showed `openclaw health --json` with `ok: true`, no plugin errors, gateway reachable, and systemd runtime `active/running`.
- Weixin `session expired` appeared after restart and was unrelated to the core update. Report it as channel-login state only.
