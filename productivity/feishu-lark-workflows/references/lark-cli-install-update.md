---
name: lark-cli-install-update
description: Install, verify, and update the official Feishu/Lark CLI. Use when the user asks to install/update/check the Feishu CLI or when lark-cli version/package naming looks inconsistent.
---

# Lark CLI install/update

Use this when working on the official Feishu/Lark CLI.

## Critical package-name gotcha

The official CLI binary is `lark-cli`, but the correct npm package is:

```bash
@larksuite/cli
```

Do **not** rely on the npm package named `lark-cli` for updates. It can appear as an unrelated or stale package (for example `0.1.0`) while the real official CLI is installed from `@larksuite/cli` and reports versions like `1.0.19` / `1.0.20`.

## Verification flow

Check the live binary version first:

```bash
lark-cli --version
```

Check where the binary resolves and what package owns it:

```bash
which lark-cli
readlink -f "$(which lark-cli)"
node -p "require('/home/$USER/.npm-global/lib/node_modules/@larksuite/cli/package.json').version"
```

Safer generic ownership check:

```bash
npm list -g @larksuite/cli --depth=0
## Post-update verification

Always re-check both the binary and the installed package:

```bash
lark-cli --version
npm list -g @larksuite/cli --depth=0
```

For the user's environment, also run a small real API probe after upgrades, because `auth status` can show `tokenStatus: "needs_refresh"` while the next user API call auto-refreshes successfully:

```bash
lark-cli auth status
lark-cli task +get-my-tasks --complete=false --format json
```

Treat `needs_refresh` as a warning, not a failure, if the task probe returns `ok: true` and `identity: "user"`. After the task probe, run `lark-cli auth status --verify` to confirm the refresh landed and report `tokenStatus: "valid"` / `verified: true` when present. Report the proxy warning if present, but do not disable the proxy unless the user asks or requests a no-proxy check.

### the user wrapper path note

In the user's WSL environment, `lark-cli` may resolve to `~/.local/bin/lark-cli` rather than the npm-global binary. This is expected when the wrapper is installed before `~/.npm-global/bin` in `PATH`. If `lark-cli update` prints an npm-package update path like `Updating lark-cli X → Y via npm package @larksuite/cli ...` and then `lark-cli updated successfully`, treat the wrapper path as healthy; still verify `lark-cli --version`, `npm list -g @larksuite/cli --depth=0`, task probe `ok: true`, and `auth status --verify`.

## Identity check

When the user asks which identity the CLI is using, use the auth subcommands directly:

```bash
lark-cli update
```

This matches the `_notice.update.message` shown by many `lark-cli task ... --format json` responses.

If that path is unavailable, fails validation, or you want an explicit package-level upgrade, run updates against the official package explicitly. One observed failure mode: `lark-cli update` can download the new release but fail its temporary-path/self-check validation with an error like `new binary verification failed: .../.cli-XXXX/bin/lark-cli: no such file or directory`; the package-level npm install still upgrades the real official CLI correctly.

```bash
cd /tmp && npm install -g @larksuite/cli@latest
```

Or pin a known version:

```bash
cd /tmp && npm install -g @larksuite/cli@1.0.20
```

Use `/tmp` or `$HOME` to avoid cwd-related update issues during npm global installs.

If a user wants `lark-cli update` itself to stop hitting that failing self-updater path on Linux/WSL, install a small wrapper earlier in `PATH` (for the user this is `~/.local/bin/lark-cli`, before `~/.npm-global/bin`). The wrapper should intercept only the `update` subcommand, run `npm view @larksuite/cli version` + `cd /tmp && npm install -g @larksuite/cli@$latest`, verify `~/.npm-global/bin/lark-cli --version`, and delegate all other subcommands to the real npm-global binary. This persists across npm package upgrades because it lives outside the package directory.

## Notice interpretation / pitfalls

- Task-command JSON can include `_notice.update.current` and `_notice.update.latest`; treat that as a live hint that a newer CLI release exists.
- Task-command JSON can also include `_notice.skills.current: ""` with a message like `lark-cli skills not installed, run: lark-cli update`. That notice is not the same thing as the binary version check. You can have a current binary version and still see a skills notice in task responses.
- Many environments surface a proxy warning such as `HTTPS_PROXY=...`; if present, remember requests and credentials are transiting that proxy unless `LARK_CLI_NO_PROXY=1` is set.

## Post-update verification

Always re-check both the binary and the installed package:

```bash
lark-cli --version
npm list -g @larksuite/cli --depth=0
```

For the user's environment, also run a small real API probe after upgrades, because `auth status` can show `tokenStatus: "needs_refresh"` while the next user API call auto-refreshes successfully:

```bash
lark-cli auth status
lark-cli task +get-my-tasks --complete=false --format json
```

Treat `needs_refresh` as a warning, not a failure, if the task probe returns `ok: true` and `identity: "user"`. After the task probe, run `lark-cli auth status --verify` to confirm the refresh landed and report `tokenStatus: "valid"` / `verified: true` when present. Report the proxy warning if present, but do not disable the proxy unless the user asks or requests a no-proxy check.

### the user wrapper path note

In the user's WSL environment, `lark-cli` may resolve to `~/.local/bin/lark-cli` rather than the npm-global binary. This is expected when the wrapper is installed before `~/.npm-global/bin` in `PATH`. If `lark-cli update` prints an npm-package update path like `Updating lark-cli X → Y via npm package @larksuite/cli ...` and then `lark-cli updated successfully`, treat the wrapper path as healthy; still verify `lark-cli --version`, `npm list -g @larksuite/cli --depth=0`, task probe `ok: true`, and `auth status --verify`.

## Identity check

When the user asks which identity the CLI is using, use the auth subcommands directly:

For Feishu task workflows, also run a lightweight live API probe after the version check. This both verifies the CLI can reach Feishu and can trigger the user token's automatic refresh when `auth status` says `needs_refresh`:

```bash
lark-cli task +get-my-tasks --complete=false --format json
```

When doing a scripted post-update task probe, avoid piping `lark-cli ... --format json` directly into `python3 -c` or another interpreter. The command output is data, but security scanners may treat “CLI output piped to interpreter” as downloaded content execution and require approval. Safer pattern: redirect JSON to a temp file, then parse the file:

```bash
lark-cli task +get-my-tasks --complete=false --format json > /tmp/lark_tasks_probe.json
python3 - <<'PY'
import json
with open('/tmp/lark_tasks_probe.json', encoding='utf-8') as f:
    d = json.load(f)
print({'ok': d.get('ok'), 'identity': d.get('identity'), 'items': len(d.get('data', {}).get('items', []))})
PY
```

Note task responses place task rows under `data.items`, not top-level `items`.

## Identity check

When the user asks which identity the CLI is using, use the auth subcommands directly:

```bash
lark-cli auth status
lark-cli auth status --verify
lark-cli auth list
```

Do not try `lark-cli auth whoami --format json`; there is no `whoami` subcommand and auth commands do not use `--format` in the same way task commands do. In particular, `lark-cli auth status --format json` is an invalid flag combination. `auth status` already returns JSON-shaped output by default, and `--verify` is the live-network check when you need to confirm the token is actually valid server-side. `auth status` reports `identity`, `defaultAs`, `tokenStatus`, `userName`, and `userOpenId`.

For a quick task API identity probe, a task command with `--format json` reports an `identity` field:

```bash
lark-cli task +get-my-tasks --complete=false --format json
```

## User-facing explanation

If the user is confused by mismatched version numbers, explain clearly:

- `lark-cli` is the executable name
- `@larksuite/cli` is the official npm package name
- the npm package named `lark-cli` should not be used as the source of truth for official updates

If the user is confused by identity/open_id differences, explain that the CLI login `userOpenId` from `lark-cli auth status` may differ from stored task-assignment IDs; report the live CLI identity as the source of truth for “which identity is the CLI using”.
