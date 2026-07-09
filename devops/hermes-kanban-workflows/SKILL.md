---
name: hermes-kanban-workflows
description: Operate Hermes Kanban boards, orchestrators, workers, task handoffs, retries, and specialist lanes.
---

# Hermes Kanban Workflows

Use this class-level skill for Hermes Kanban task orchestration, worker execution, board hygiene, or specialist lane setup.

## Roles

### Orchestrator
Use for planning a multi-card workflow, creating tasks, assigning specialists, monitoring progress, and unblocking work. Keep cards scoped, assign to the right profile, and add context in comments rather than overloading titles.

### Worker
Use when spawned on a card. Start by reading the task state and comment thread, work only in the assigned workspace unless instructed otherwise, heartbeat only for meaningful long-running progress, and complete/block with structured metadata.

### Specialist lanes
Use when a board routes a class of work to a specialist agent, such as a Codex lane for code implementation. The lane prompt should define scope, workspace rules, verification requirements, and handoff format.

## Worker completion discipline

- Use `kanban_complete` only when the task is actually terminal.
- For code-changing work that needs human eyes, comment structured handoff metadata and then block with `review-required: ...`.
- Never invent created card IDs; only pass IDs returned by successful task creation calls.
- In headless worker contexts, do not call `clarify`; comment/block instead.

## Retry and state rules

- Always inspect current state first; a task may have been blocked, archived, or reassigned after dispatch.
- Read previous run outcomes before retrying and avoid repeating failed paths.
- Treat shared `dir:` and `worktree` workspaces as potentially stale; reconcile with comments.

## Absorbed narrow skills

This umbrella absorbs `kanban-orchestrator` and `kanban-worker`; specialist lane details may live in references/templates when present.
