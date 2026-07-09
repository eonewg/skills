---
name: ai-coding-agent-orchestration
description: Orchestrate autonomous coding CLIs (Claude Code, Codex, OpenCode) from Hermes for implementation, refactoring, PR review, and parallel work.
---

# AI Coding Agent Orchestration

Use this class-level skill when the task is to delegate software work to an external coding agent CLI instead of doing all edits directly in Hermes.

## Choose the agent

- **Claude Code**: best when Claude Code auth is available, for print-mode automation, tmux-based iterative sessions, structured JSON output, or rich project memory via `CLAUDE.md`.
- **Codex CLI**: best when the user explicitly asks for Codex/OpenAI or when using Codex OAuth in a git repository. It requires PTY for interactive use and refuses to run outside a git repo.
- **OpenCode**: best when the user wants a provider-agnostic open-source coding agent, long-running TUI sessions, or model/provider switching inside OpenCode.

## Shared orchestration workflow

1. Confirm the working directory is the intended repository and check git status before starting.
2. Prefer bounded non-interactive one-shot modes for simple tasks:
   - Claude Code: `claude -p 'task' --max-turns N`
   - Codex: `codex exec 'task'`
   - OpenCode: `opencode run 'task'`
3. Use isolated worktrees or temporary clones for risky PR reviews or parallel implementation.
4. For long interactive sessions, start a tracked background/PTY process or tmux session and monitor with `process(action='poll'|'log')` or `tmux capture-pane`.
5. Require every child/subagent/coding agent to use the parent-facing return contract: `Outcome`, `Evidence / handles`, `Files changed`, `Verification`, `Risks / blockers`, `Needs parent decision`. Forbid raw chronology unless one short excerpt is necessary evidence.
6. Verify results yourself before telling the user the work succeeded.

## Agent-specific quick notes

### Maintenance of external agent CLIs
Use `references/ai-agent-cli-maintenance.md` when the task is to update, verify, or troubleshoot npm-installed autonomous-agent command-line tools outside Hermes itself, including OpenClaw and ClawHub. The tested OpenClaw/ClawHub update commands are preserved at `references/openclaw-clawhub-npm-update.md`. Keep Hermes Agent setup/configuration in the separate `hermes-agent` umbrella.

### Claude Code
- Prefer print mode (`claude -p`) for automation; it avoids TUI dialogs and can emit JSON.
- Use tmux for multi-turn interactive sessions; handle trust and permission dialogs explicitly.
- Set `--max-turns` and optionally `--allowedTools` to cap runaway work.

### Codex CLI
- Must run in a git repository; create a temporary `git init` directory for scratch tasks.
- Use `pty=true` for Codex terminal interactions.
- Use worktrees for parallel issue fixing or isolated PR review.

### OpenCode
- `opencode run` is simplest for bounded tasks and usually does not need PTY.
- Interactive TUI sessions require `pty=true` and should be exited with Ctrl-C or killed, not `/exit`.
- Verify the resolved binary with `which -a opencode` if Hermes and the user's shell behave differently.

## Detailed references

The former narrow skills were demoted intact for provider-specific command details:
- `references/ai-agent-cli-maintenance.md`
- `references/openclaw-clawhub-npm-update.md`
- `references/claude-code.md`
- `references/codex.md`
- `references/opencode.md`

## Subagent return contract

When spawning Hermes subagents or external coding agents, make the final response compact and evidence-bearing. The contract is:

- `Outcome`: answer/result in 1-3 bullets.
- `Evidence / handles`: paths, URLs, IDs, commands, status codes, or other read-back handles the parent can verify.
- `Files changed`: created/modified/deleted files, or `none`.
- `Verification`: checks/tests/probes actually run and result, or `not run` with reason.
- `Risks / blockers`: uncertainty, failures, missing permissions, or `none`.
- `Needs parent decision`: choices/follow-ups the parent must decide, or `none`.

Do not replay tool chronology, raw logs, or reasoning unless one short excerpt is necessary evidence. The parent must verify external side effects via the returned handle before reporting success.

## Token cost discipline

For coding agents, the expensive part is usually not the user's short instruction but the repeated context bundle: system prompt, skills, tool/MCP schemas, session history, file reads, terminal output, and failed retries. Before launching a long agent run:

1. Keep one session focused on one task; start a fresh session/worktree when the topic changes instead of dragging unrelated history.
2. Expose only the tools/MCPs/skills needed for this task. Low-frequency tools should be invoked via CLI or loaded on demand, not carried as permanent schema.
3. Prefer CLI output with filtering/summarization over raw huge terminal logs entering the model context.
4. Route models by task: strong model for planning, architecture, risky review; cheaper/faster model for mechanical edits, formatting, simple classification, and repetitive worker tasks.
5. Make the first instruction complete: goal, files/scope, forbidden actions, tests/checks, and required output format. This prevents expensive retry chains.
6. For large tasks, use orchestrator-worker decomposition: orchestrator plans and writes structured files; workers read only the subset they need; progress is passed through files such as `.agent/plan.json`, `.agent/audit.json`, and `.agent/progress.json` instead of one giant chat history.

## Loop / goal-mode design

Use a loop only when the work is repeated, feedback is machine-checkable, and the cost of unattended iterations is justified. A good loop prompt must include all four layers:

1. **Machine-verifiable completion criteria**: exact commands, tests, metrics, or output files that define done.
2. **Negative guardrails**: what the agent must not do to satisfy the metric, e.g. do not delete failing tests, skip checks, weaken assertions, change public APIs, or touch production data unless explicitly authorized.
3. **Failure fallback**: after N failed iterations, stop, preserve logs/diffs, and report blockers instead of spinning forever.
4. **Layered goals**: separate main objective, intermediate checkpoints, and final acceptance checks so one proxy metric cannot hijack the real goal.

Prefer separating executor and reviewer: the agent that writes code should not be the only judge of success. For high-risk loops, use a second model/agent or manual review before merge/deploy.

## Common pitfalls

- Starting an external coding agent without first checking repo state and scope.
- Sharing one workdir across parallel agents.
- Treating a subagent's self-report as verification; always inspect diffs and run tests or a smoke check.
- Writing loop goals with only positive metrics and no guardrails, causing Goodhart failures such as deleting tests to make checks pass.
- Leaving tmux/background sessions running after completion.
