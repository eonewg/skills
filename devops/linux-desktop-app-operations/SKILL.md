---
name: linux-desktop-app-operations
description: Install, expose, and verify Linux desktop/Electron apps inside WSL or Linux hosts, especially when a headless/web-kernel mode is more reliable than launching a GUI. Use for AppImage/tarball/deb installs, wrapper commands under ~/.local/bin, workspace initialization, localhost verification, and cleanup.
---

# Linux Desktop App Operations

Use this skill when the user asks to install or run a Linux desktop application in WSL/Linux, especially Electron apps, AppImages, tarball releases, or apps with a separate kernel/server mode.

## Operating principles

1. **Prefer the least invasive install path first.**
   - If a release provides a portable `linux.tar.gz`, install under `~/.local/opt/<app>-<version>` and expose wrappers in `~/.local/bin`.
   - Avoid `sudo dpkg -i` unless the user explicitly wants a system install or the app needs desktop integration.
   - Keep a stable symlink such as `~/.local/opt/<app> -> ~/.local/opt/<app>-<version>` for upgrades/rollbacks.

2. **Check architecture and distro before downloading.**
   - Run `uname -m` and distro detection.
   - Map `x86_64` to generic `linux`/amd64 assets and `aarch64`/`arm64` to ARM assets.

3. **Use release APIs when a GitHub release URL is provided.**
   - Fetch the GitHub release JSON and list assets instead of guessing filenames.
   - Do not pipe remote output directly into an interpreter; save JSON and inspect it with `jq`/safe parsing.

4. **For WSL/Electron apps, verify CLI/server mode separately from GUI mode.**
   - Electron UI may fail if `$DISPLAY`/Wayland/WSLg is unavailable. Treat that as a GUI-environment limitation, not as install failure, if a kernel/server or CLI mode works.
   - If the app has a kernel/server binary, start it on `127.0.0.1:<port>` and verify with `curl`.

5. **Create user-level wrappers.**
   - Wrapper scripts should live in `~/.local/bin` and call the exact installed binary.
   - If the app expects config directories, wrappers can create required config dirs before `exec`.
   - For server-mode apps, create a dedicated `<app>-serve` wrapper with configurable environment variables for workspace, port, language, and auth token when applicable.

6. **Initialize and verify real state.**
   - Create the app workspace/data dir explicitly if needed.
   - Run the app's version/help command.
   - Start the server in background only after install succeeds.
   - Verify with a local HTTP/API call, process check, workspace-info command, or equivalent.
   - Report exact paths, commands, URL, and verification output.

7. **Clean up temporary installers.**
   - Remove `/tmp/<app>-install` or downloaded archives after successful installation unless the user asked to keep them.

## Generic tarball install pattern

```bash
mkdir -p "$HOME/.local/opt" "$HOME/.local/bin" /tmp/<app>-install
cd /tmp/<app>-install
curl -L --fail -o <asset>.tar.gz <release-asset-url>
tar -tzf <asset>.tar.gz | sed -n '1,40p'
tar -xzf <asset>.tar.gz -C "$HOME/.local/opt"
mv "$HOME/.local/opt/<extracted-dir>" "$HOME/.local/opt/<app>-<version>"
ln -sfn "$HOME/.local/opt/<app>-<version>" "$HOME/.local/opt/<app>"
```

Create wrappers with file tools rather than heredoc shell writes when available, then:

```bash
chmod +x "$HOME/.local/bin/<app>" "$HOME/.local/bin/<app>-serve"
command -v <app> <app>-serve
<app> --version || true
```

## WSL GUI fallback

If the desktop command exits with messages like missing `$DISPLAY`, missing X server, or Ozone/X11 initialization failure:

- Do not declare the installation failed if binaries are present and CLI/server mode verifies.
- Tell the user clearly: desktop UI requires WSLg/X server, but web/server mode is usable.
- Prefer giving the localhost URL opened from Windows browser when the app supports it.

## SiYuan-specific note

See `references/siyuan-wsl-v3.7.0.md` for a concrete WSL install and verification pattern for SiYuan v3.7.0, including `siyuan-kernel`, `siyuan-serve`, workspace initialization, and API verification.

## Verification checklist

Before final reply, confirm:

- Installed asset matches host architecture.
- Stable install path and wrapper commands exist.
- Version command reports the requested version.
- Workspace/data directory is valid if applicable.
- Server/API or GUI launch has been exercised.
- Temporary install directory/downloads were cleaned up.
- Final answer includes only durable commands and verified outputs, not speculative claims.