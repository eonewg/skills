---
name: feishu-lark-workflows
description: "Unified guidance for Feishu/Lark workspace operations: docs, interactive cards, CLI setup, and task workflows. Use when the user needs to configure or operate Feishu/Lark documents, tasks, messaging UX, or the official CLI."
---

# Feishu / Lark Workflows

## Overview
This umbrella skill replaces narrowly scoped Lark/Feishu skills with one class-level entry organized by workspace job type.

## Core workflow
1. Identify the surface area: CLI setup, tasks, docs/content publishing, or interactive message UX.
2. Verify the active account/app identity before writes.
3. Prefer the platform-native workflow for the target object instead of mixing unrelated tools.
4. Read back results or inspect the resulting document/task/card state after writes.

## Consolidated subsections
### CLI installation and identity
Install, verify, update, and inspect the official `lark-cli` setup.

### Task management
Create, update, assign, complete, **delete**, regroup, and verify Feishu/Lark tasks. For the user-specific task routing rules — due-time defaults, assignment ID, study grouping, and batch-reschedule semantics — load `feishu-task-routing` first. Task deletion uses the raw `task tasks delete` subcommand (not `+delete`) with `--yes` flag — see `references/lark-cli-task-management.md`.

### Calendar reminders and events
Create, update, search, patch, delete, and verify Feishu Calendar events for time-based reminders. For the user, reminder-like requests default to Feishu Calendar unless he explicitly asks for a chat/cron reminder. See `references/lark-cli-calendar-reminders.md` for the exact lark-cli create/get/reschedule/delete workflow and duplicate-cron cleanup rule.

### Multi-week plan scheduling
When the user asks to arrange a structured plan, combine recurring Feishu Calendar blocks for execution with phase-boundary tasks/tasklists for progress tracking. See `references/lark-cli-multi-week-plan-scheduling.md` for the tested pattern.

### Feishu docs and document publishing
Create or update docs, publish Markdown, manage permissions, and handle long-content quirks. For the user's exam-prep cockpit, use `templates/the user-weekly-exam-review.md` for weekly review docs and `references/the user-feishu-execution-cockpit.md` for the Docs/Base pattern.

### the user weekly exam plan/review loop
the user's preferred weekly rhythm is: every Monday morning create a new Feishu cloud doc for the current week, fill the plan section from live unfinished Feishu tasks + the `考研进度表` Base; every Sunday night append/fill a review draft from live unfinished tasks + Base status. Do not create calendar events for this loop unless the user asks. Store weekly doc links in `~/.hermes/data/feishu-weekly-exam-docs.json`; active cron jobs are named `每周一创建考研周计划云文档` and `每周日填写考研周复盘草稿`.

### Feishu Base execution dashboards
Use Base as a lightweight progress/status layer, not as a replacement for local wiki. For the user, the default exam-prep Base pattern is one `考研进度表` Base with a `主线进度` table tracking module, subject, stage, status, priority, progress, next action, blocker, due time, link, and notes. Keep initial schemas small and seed only high-signal records from current tasks.

### Interactive cards and confirmation UX
Use buttons/forms/cards when Feishu interactions need structured user choices.

## Absorbed specialized skills
- `lark-cli-install-update`
- `lark-cli-task-management`
- `feishu-doc-manager`
- `feishu-interactive-cards`

## Navigation
Absorbed skill bodies and provider-specific details live under `references/` and `scripts/`.

## Feishu messaging style
- **Do not use Markdown tables in Feishu channel messages.** Use plain bullet lists or numbered lists instead. Tables render poorly in Feishu chat bubbles and break the conversational flow.

## Common pitfalls
- Confusing CLI account identity with app/bot identity.
- Mixing document workflows with message-card workflows.
- Updating tasks without re-reading the resulting task state.
- Using cron/chat reminders when the user expects a Feishu Calendar reminder; if corrected, remove the cron job and create/read back the Feishu event.
- Using plain-text confirmation when an interactive card is more reliable.
- Using `+complete` as a workaround for deletion — Feishu completed tasks are still visible; use `task tasks delete` for permanent removal.
- Attempting to delete a recurring calendar event by its base event_id (without `_timestamp` suffix) fails. Delete each `_timestamp`-suffixed instance individually.

## Verification checklist
- [ ] Correct Feishu/Lark surface identified.
- [ ] Identity/account checked before writes.
- [ ] Platform-native workflow used for docs/tasks/cards.
- [ ] Result verified after write or action.