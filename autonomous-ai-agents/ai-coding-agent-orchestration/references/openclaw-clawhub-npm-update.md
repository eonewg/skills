# OpenClaw and ClawHub npm update pattern

Use this when maintaining the user's npm-installed OpenClaw ecosystem tools.

## OpenClaw
Discovery:

```bash
which openclaw || true
readlink -f "$(which openclaw)" 2>/dev/null || true
openclaw --version 2>/dev/null || true
npm list -g openclaw --depth=0 || true
npm view openclaw version
npm view openclaw dist-tags --json
```

Update:

```bash
cd /tmp && npm install -g openclaw@latest
```

Verify:

```bash
which openclaw
readlink -f "$(which openclaw)"
openclaw --version
npm list -g openclaw --depth=0
npm view openclaw version
openclaw --help | sed -n '1,60p'
```

Known-good observed shape after update:

```text
OpenClaw 2026.6.6 (...)
~/.npm-global/lib/node_modules/openclaw/openclaw.mjs
openclaw@2026.6.6
```

## ClawHub
Discovery:

```bash
which clawhub || true
readlink -f "$(which clawhub)" 2>/dev/null || true
clawhub --version 2>/dev/null || true
npm list -g clawhub --depth=0 || true
npm view clawhub version
npm view clawhub dist-tags --json
```

Note: `clawhub --version` may not print a version on some versions; use `npm list -g clawhub --depth=0` and `clawhub --help` / `clawhub --cli-version` as the reliable verification path.

Update:

```bash
cd /tmp && npm install -g clawhub@latest
```

Verify:

```bash
which clawhub
readlink -f "$(which clawhub)"
npm list -g clawhub --depth=0
npm view clawhub version
clawhub --help | sed -n '1,60p'
```

Known-good observed shape after update:

```text
~/.npm-global/lib/node_modules/clawhub/bin/clawdhub.js
clawhub@0.20.0
ClawHub CLI v0.20.0
```

## Reporting style
Keep the user-facing result short: old version → new version, executable path, resolved package file, npm global package version, npm latest, and a single sentence that the help probe passed.
