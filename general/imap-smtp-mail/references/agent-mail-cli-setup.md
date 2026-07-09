# Agent Mail CLI (`agently-cli`) setup notes

Use this when the user asks to install/configure Agent Mail CLI from `https://agent.qq.com/doc/cli-setup.md` or asks about the difference between Agent Mail and the existing 163 IMAP/SMTP mailbox.

## Official setup sequence

1. Install/update CLI:

```bash
npm install -g @tencent-qqmail/agently-cli
```

2. Install/update the Agent Mail skill package for common agents:

```bash
npx skills add https://agent.qq.com --skill -g -y
```

Expected install may report a partial failure for PromptScript global install while still installing/symlinking `agently-mail` for Hermes/OpenClaw/Codex/etc. Treat the relevant Hermes/OpenClaw install lines as the important part; do not claim complete failure just because PromptScript is unsupported.

3. Start OAuth login interactively:

```bash
agently-cli auth login
```

Run it as a background PTY process so the user can authorize in their browser. Extract the exact URL printed by the command and show it as an opaque string: do not edit, decode, re-encode, append punctuation, or rebuild query parameters.

User-facing wording required by the upstream doc:

```text
请点击或复制以下链接在浏览器中完成授权：
```

Then show the URL alone in its own code block.

4. After the user says authorization is complete, wait for the login process to exit and verify:

```bash
agently-cli +me
```

If successful, report:

```text
邮箱地址 xxx 已授权成功，可以用它来收发邮件了。
```

Replace `xxx` with the primary alias returned by `+me`.

## Watch-pattern pitfall

If using `watch_patterns: ["http://", "https://"]`, a PTY login shell may print Ubuntu/MOTD links such as `https://help.ubuntu.com`, causing false watch notifications. Do not treat those as the authorization URL. Poll/log the process output and use the URL in the CLI's own login message, typically under text like `请点击以下链接登录并授权邮箱：` and domain `agent.qq.com/page/oauth`.

## Positioning vs the user's 163 mailbox

- Agent Mail (`@agent.qq.com`) is an Agent-native mailbox identity controlled through `agently-cli` and OAuth. It is good for the assistant/agent workflows, service notifications, automation, and agent-specific inbound/outbound mail.
- Existing 163 (`user@example.com`) remains the ordinary mailbox identity operated through IMAP/SMTP. It is better for formal/long-term external correspondence where a normal mailbox identity is more natural.
- Agent Mail returns structured limits from `+me`, such as send quota, request limits, scopes, and attachment limits. Do not assume those equal 163 provider limits.
- Keep both identities conceptually separate: Agent Mail is the agent-native work inbox; 163 is the stable traditional mailbox.