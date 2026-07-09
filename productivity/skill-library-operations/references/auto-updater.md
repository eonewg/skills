---
name: auto-updater
description: Automatically check and update OpenClaw and installed skills on a schedule. Use when setting up periodic update checks, modernizing legacy auto-update flows, maintaining skill/runtime versions, or building update-report cron jobs.
---

# Auto-Updater

为 OpenClaw 和已安装 skills 建立定时更新检查与更新流程。

## 何时使用

当用户想：
- 定时检查 OpenClaw 是否有新版本
- 定时更新本地 skills
- 建立“每天/每周自动更新”流程
- 把旧的 `clawdbot` / `clawdhub` 自动更新方案迁到 OpenClaw

## 核心原则

先确认安装形态，再决定更新方式。

OpenClaw 本体优先用：
```bash
openclaw update status
```

如果用户明确要更新，再根据安装方式执行对应更新命令。
不要默认无脑自动升级核心程序，尤其在生产环境。

skills 更新也要先做 dry-run 或差异确认，避免把本地定制覆盖掉。

## 建议流程

先检查：
```bash
openclaw update status
```

再列出已安装 skills / 本地差异。
如果用户确认需要周期任务，再用 `openclaw cron add` 或 `openclaw cron edit` 建立计划任务。

更细的执行细节看：
- `references/agent-guide.md`
- `references/summary-examples.md`

## 注意事项

- 这个 skill 旧版本大量引用了 `clawdbot` / `clawdhub`，当前已过时
- 现在应统一迁移到 OpenClaw 命令体系
- 对本地定制过的 skill，优先做对照再更新，不要一键覆盖
- 自动更新核心程序前，最好先保留回滚路径或至少记录当前版本
- 如果 `openclaw update` 在启动期就因为 `Cannot find module ...` 之类的 bundled plugin 运行时依赖缺失而连 config 都读不出来，可直接绕过 CLI 更新包装层，先在一个稳定目录（如 `/tmp`）执行：
  `OPENCLAW_EAGER_BUNDLED_PLUGIN_DEPS=1 npm update -g openclaw`
  这样会在全局更新时一并预装 bundled plugin 依赖，避免更新后 `openclaw doctor` 因已配置频道插件（如 Feishu / Telegram）缺依赖而失败。
- 如果更新流程里出现 `uv_cwd` / `ENOENT`，通常是因为当前工作目录在更新过程中失效；改到 `/tmp` 或 `$HOME` 再执行更新。
- `openclaw update` 可能在核心和插件已更新成功后，因为 gateway warm-up 超过健康检查窗口而以 exit 1 结束并提示 `Gateway did not become healthy after restart`。不要立刻判定失败；先等几十秒，再执行 `openclaw gateway status --deep`、查看 `journalctl --user -u openclaw-gateway.service -n 200 --no-pager`。如果日志出现 `[gateway] ready` 且 connectivity probe 为 ok，则更新实际成功。
