# SiYuan v3.7.0 on WSL — session reference

This reference captures a verified install pattern for SiYuan inside Ubuntu WSL where the Electron UI may not have a display, but the kernel/web UI works.

## Context

- Host: WSL Ubuntu 24.04, `x86_64`.
- Release: `siyuan-note/siyuan` tag `v3.7.0`.
- Correct asset for x86_64 Linux portable install: `siyuan-3.7.0-linux.tar.gz`.
- Installed size observed: about 489 MB.

## Release asset discovery

Use the GitHub API and inspect assets safely:

```bash
curl -sL https://api.github.com/repos/siyuan-note/siyuan/releases/tags/v3.7.0 \
  -o /tmp/siyuan-release-v3.7.0.json
jq -r '.tag_name + " " + .name, (.assets[] | [.name,.browser_download_url] | @tsv)' \
  /tmp/siyuan-release-v3.7.0.json
```

Do not pipe the GitHub JSON directly into Python or another interpreter.

## Install layout

```bash
mkdir -p "$HOME/.local/opt" "$HOME/.local/bin" /tmp/siyuan-install
cd /tmp/siyuan-install
curl -L --fail -o siyuan-3.7.0-linux.tar.gz \
  https://github.com/siyuan-note/siyuan/releases/download/v3.7.0/siyuan-3.7.0-linux.tar.gz

tar -tzf siyuan-3.7.0-linux.tar.gz | sed -n '1,40p'
tar -xzf siyuan-3.7.0-linux.tar.gz -C "$HOME/.local/opt"
mv "$HOME/.local/opt/siyuan-3.7.0-linux" "$HOME/.local/opt/siyuan-3.7.0"
ln -sfn "$HOME/.local/opt/siyuan-3.7.0" "$HOME/.local/opt/siyuan"
```

Key binaries:

- Desktop app: `~/.local/opt/siyuan/siyuan`
- Kernel CLI: `~/.local/opt/siyuan/resources/kernel/SiYuan-Kernel`

## Wrappers

`~/.local/bin/siyuan-kernel`:

```bash
#!/usr/bin/env bash
set -euo pipefail
exec ~/.local/opt/siyuan/resources/kernel/SiYuan-Kernel "$@"
```

`~/.local/bin/siyuan`:

```bash
#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.config/siyuan"
exec ~/.local/opt/siyuan/siyuan "$@"
```

`~/.local/bin/siyuan-serve`:

```bash
#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${SIYUAN_WORKSPACE:-$HOME/SiYuan}"
PORT="${SIYUAN_PORT:-6806}"
LANG="${SIYUAN_LANG:-zh-CN}"
mkdir -p "$WORKSPACE" "$HOME/.config/siyuan"
exec ~/.local/opt/siyuan/resources/kernel/SiYuan-Kernel serve \
  -w "$WORKSPACE" \
  --port "$PORT" \
  --lang "$LANG" \
  --accessAuthCode "${SIYUAN_ACCESS_AUTH_CODE:-}"
```

Then:

```bash
chmod +x ~/.local/bin/siyuan ~/.local/bin/siyuan-kernel ~/.local/bin/siyuan-serve
```

## Workspace initialization

Use a normal user workspace path such as:

```bash
mkdir -p "$HOME/SiYuan" "$HOME/.config/siyuan"
siyuan-kernel serve -w "$HOME/SiYuan" --port 6806 --lang zh-CN --accessAuthCode ''
```

Starting the server once initializes:

- `~/SiYuan/conf/`
- `~/SiYuan/temp/`
- `~/.config/siyuan/workspace.json`
- `~/.config/siyuan/port.json`

## Verification commands

```bash
siyuan-kernel --version
# SiYuan-Kernel version 3.7.0

siyuan-kernel workspace list -f json
# [{"name":"SiYuan","path":"~/SiYuan"}]

siyuan-kernel workspace info -w "$HOME/SiYuan" -f json
# {"path":"~/SiYuan","valid":true,"version":"3.7.0"}

curl -sS -m 5 http://127.0.0.1:6806/api/system/version
# {"code":0,"msg":"","data":"3.7.0"}
```

The web UI / API is reachable at:

```text
http://127.0.0.1:6806
```

## WSL Electron caveat

Running `siyuan --help` or the desktop app in headless WSL may log errors like:

```text
Missing X server or $DISPLAY
The platform failed to initialize. Exiting.
```

If the kernel version, workspace, and HTTP endpoint verify, the install is still good. Report that the Electron desktop UI needs WSLg/X display support, while the kernel/web UI is usable via localhost.

## Upgrade pattern

For a patch release such as `v3.7.1`, keep the same portable layout and switch only the stable symlink after checksum verification:

```bash
TAG=v3.7.1
VER=3.7.1
TMP=/tmp/siyuan-update-$TAG
ASSET=siyuan-$VER-linux.tar.gz
mkdir -p "$TMP" "$HOME/.local/opt"
cd "$TMP"
curl -L --fail --retry 3 --retry-delay 2 -o "$ASSET" \
  "https://github.com/siyuan-note/siyuan/releases/download/$TAG/$ASSET"
curl -L --fail --retry 3 --retry-delay 2 -o SHA256SUMS.txt \
  "https://github.com/siyuan-note/siyuan/releases/download/$TAG/SHA256SUMS.txt"
sha256sum -c <(grep " $ASSET$" SHA256SUMS.txt)
tar -tzf "$ASSET" | sed -n '1,20p'
tar -xzf "$ASSET" -C "$HOME/.local/opt"
mv "$HOME/.local/opt/siyuan-$VER-linux" "$HOME/.local/opt/siyuan-$VER"
ln -sfn "$HOME/.local/opt/siyuan-$VER" "$HOME/.local/opt/siyuan"
siyuan-kernel --version
siyuan-kernel workspace info -w "$HOME/SiYuan" -f json
rm -rf "$TMP"
```

Keep the previous `~/.local/opt/siyuan-<old-version>` directory for rollback unless disk pressure is a concern.

Before deleting the old install directory, check whether the workspace export config still points Pandoc at versioned resources:

```bash
grep -n 'siyuan-[0-9]' "$HOME/SiYuan/conf/conf.json" || true
```

If `export.pandocParams` references the old version, update it through the running kernel API (not by editing `conf.json` while the kernel is running, because shutdown can rewrite the old in-memory config):

```bash
python3 - <<'PY'
import json, os, urllib.request
conf_path=os.path.expanduser('~/SiYuan/conf/conf.json')
with open(conf_path, encoding='utf-8') as f:
    conf=json.load(f)
export=conf['export']
export['pandocParams']='--reference-doc "~/.local/opt/siyuan/resources/pandoc-resources/pandoc-template.docx"'
req=urllib.request.Request(
    'http://127.0.0.1:6806/api/setting/setExport',
    data=json.dumps(export).encode(),
    headers={'Content-Type':'application/json'},
    method='POST')
print(urllib.request.urlopen(req, timeout=10).read().decode())
PY
```

Restart and verify the new log line says `pandoc params set to [.../.local/opt/siyuan/resources/...]` and no longer references the deleted version directory.

## Cleanup

After successful verification:

```bash
rm -rf /tmp/siyuan-install
```
