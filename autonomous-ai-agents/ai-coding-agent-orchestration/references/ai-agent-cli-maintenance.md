---
name: ai-agent-cli-maintenance
description: Maintain and update npm-installed AI agent CLIs and companion package tools such as OpenClaw and ClawHub. Use when the user asks to update, verify, or troubleshoot agent command-line tools outside Hermes itself.
---

# AI Agent CLI Maintenance

## When to use
Use this skill when the user asks to update, check, or verify command-line tools for autonomous/agentic workflows, especially npm-installed CLIs such as `openclaw` and companion tools like `clawhub`.

Do not use this for Hermes Agent itself; load `hermes-agent` for Hermes CLI/config/provider/plugin work.

## Core workflow
1. Identify the exact executable and package owner before updating.
2. Check the current binary path and version.
3. Check the package-manager source of truth, usually `npm list -g <package> --depth=0` and `npm view <package> version` for npm tools.
4. Update the explicit package name from a neutral directory such as `/tmp`:
   ```bash
   cd /tmp && npm install -g <package>@latest
   ```
5. Verify after update:
   - `which <binary>`
   - `readlink -f "$(which <binary>)"`
   - `<binary> --version` or the tool's version flag
   - `npm list -g <package> --depth=0`
   - `npm view <package> version`
   - a lightweight help probe, e.g. `<binary> --help | sed -n '1,60p'`
6. Report only the old version, new version, path, package version, latest version, and whether the help probe succeeded.

## OpenClaw / ClawHub notes
See `references/openclaw-clawhub-npm-update.md` for the tested update and verification commands.

## Pitfalls
- Do not assume the executable name and npm package name differ or match; verify ownership first.
- Do not update adjacent companion tools unless the user explicitly asks or confirms. If you discover one is outdated while updating another, mention it separately.
- Avoid turning transient local setup state into a durable rule. Capture stable package-name/version-check patterns, not one-off environment failures.

## Verification checklist
- [ ] Binary path and resolved target checked before or after update.
- [ ] Package manager source of truth checked.
- [ ] Update installed the intended package.
- [ ] Post-update binary version matches npm global package version and npm latest.
- [ ] Help or equivalent non-destructive probe succeeds.
