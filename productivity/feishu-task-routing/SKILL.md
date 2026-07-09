---
name: feishu-task-routing
description: "Use when operating the user's Feishu/Lark task and reminder workflow: checking unfinished tasks, creating tasks with deadlines, assigning tasks to the user, routing study tasks to the exam-prep grouping, handling bulk reschedules, and interpreting task-language edge cases."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [feishu, lark, tasks, reminders, scheduling]
    related_skills: [feishu-lark-workflows, calendar]
---

# Feishu Task Routing

## Overview

This skill is the operating policy for the user's Feishu/Lark task and reminder workflow. It keeps procedural task rules out of hot memory while preserving the exact execution semantics.

## Memory preflight

Before operating Feishu tasks/reminders, route memory with:

```bash
~/.hermes/scripts/memory_route.py 飞书
```

Read the returned modules, normally `memory-modules/process-memory.md`, `user-modules/workflow-profile.md`, and `memory-modules/mistakes-memory.md`. They contain the user-specific defaults and high-priority pitfalls for unfinished-only views, due-time defaults, no default start time, task-language semantics, and Feishu output formatting.

Default channel: Feishu. the user has moved daily chat, reminders, Q&A, tasks, docs, and schedules to Feishu as the primary surface.

## Core Rules

- Daily task lookup means unfinished Feishu tasks only; completed tasks are not listed unless explicitly requested.
- Create tasks as Feishu tasks.
- Create reminders/time-based events as Feishu Calendar events unless the user explicitly asks for a chat/cron reminder.
- New Feishu tasks should not include a start time unless the user explicitly asks for one.
- Every newly created Feishu task must have a due time.
- If the user gives no due time, default to today 23:59.
- If the user says it is a tomorrow task without a concrete time, default to tomorrow 23:59.
- In rapid task-addition turns, context carries forward: if the user says “明天加 A、B、C” and then immediately follows with “再加 D”, treat D as the same due bucket (tomorrow 23:59) unless he says a different date/time. Verify the created task due date before reporting.
- After creating a Feishu task for the user, immediately assign it to `ou_<open_id>`.
- Study/exam-prep tasks default to the 考研 grouping/list unless the user explicitly says the task is not exam-prep related.

## Known IDs

```text
the user Feishu open_id: ou_<open_id>
考研 task grouping/list id: d1fff238-f370-4a2b-942d-cd1bbd9de074
```

Use these IDs for task creation/assignment workflows that require explicit identifiers.

## Lookup Workflow

When the user asks "今天还有什么任务" or equivalent:

```text
Return unfinished tasks only.
Do not list completed tasks.
Prefer live Feishu task state over memory or Graphiti.
```

When the user asks to prioritize today's tasks (e.g. "今天任务排个优先级"):

1. Query live unfinished Feishu tasks first; do not prioritize from memory alone.
2. Filter to tasks due today or already overdue unless the user asks for all unfinished tasks.
3. Rank by: hard deadline/overdue risk -> exam-prep leverage -> dependency unlocks -> energy/time fit.
4. If the user adds new context that a task is the final part of a course/module and unlocks the next subject (e.g. finishing Computer Organization before starting OS), promote that task to P0 even if another task previously looked like the main line. Sequence it as: finish the unlock task -> immediately do the directly related fresh exercises -> clear old residual exercises -> then return to other subjects.
5. If the user says it is a rest day / wants something lighter / asks to “轻松一点先”, let energy fit override the normal old-debt-first ranking. Prefer low-friction forward motion such as listening to a new lecture, and explicitly label older exercises/reviews as tomorrow’s follow-up rather than pushing hard tonight.
6. Return a short ordered list with P0/P1/P2 labels and a realistic execution block, not a long planning essay.
7. If task data is unavailable, say the lookup failed and give only a clearly labeled provisional heuristic.

Known CLI pattern:

```bash
lark-cli task +get-my-tasks --complete=false
```

If the CLI command shape changes, consult `feishu-lark-workflows` and verify with a read-back call before relying on stale syntax.

## Recurring Task vs Cron Automation

When the user refers to a recurring weekly item (e.g. “每周日那个考研周复盘的任务” or “周一这个也删了吧”), do not assume it is a Feishu task. First inspect Hermes cron jobs if the wording points to an automation/reminder rather than a normal unfinished task:

```text
cronjob(action='list') → identify the exact recurring job → cronjob(action='remove', job_id=...) → list again to verify removal
```

If removing the recurring job changes a stable scheduling preference, update user memory compactly after verification. Preserve nearby related jobs unless the user explicitly asks to remove them too.

## Milestone Reminders: Task vs Calendar

When the user asks to “建日程或任务，在几个时间点提醒我进度” for study/exam checkpoints, default to **Feishu tasks**, not calendar events, when the item is a stage node or progress check rather than a fixed time block.

Use this distinction:

```text
Stage checkpoint / progress reminder / launch date → Feishu task
Fixed occupied study block or mock exam time window → Calendar event
Daily concrete learning item → Feishu task
```

For exam-prep milestone reminders, create one task per checkpoint in the 考研 tasklist, assign to the user, set the due datetime to the reminder moment, then set a task reminder at due time and read back unfinished tasks to verify:

```bash
lark-cli task +create \
  --summary "考研英语：7月半程进度检查" \
  --due "2026-07-15T21:30:00+08:00" \
  --description "检查阅读真题主线是否稳定推进。" \
  --assignee "ou_<open_id>" \
  --tasklist-id "d1fff238-f370-4a2b-942d-cd1bbd9de074"

lark-cli task +reminder --task-id <guid> --set 0m
lark-cli task +get-my-tasks --complete=false
```

Do not overuse calendar events for checkpoints; they clutter the calendar because they are not “sit in this meeting/study block from X to Y” commitments.

## Bulk Reschedule with +update

For moving a batch of yesterday-due tasks to today (or any bulk due-date change):

```bash
lark-cli task +update \
  --task-id "guid1,guid2,guid3,guid4,guid5,guid6" \
  --due "2026-06-14T23:59:00+08:00"
```

- `--task-id` accepts comma-separated GUIDs (no spaces after commas)
- `--due` accepts ISO 8601 timestamps with timezone offset (`+08:00`)
- All listed tasks are updated in a single call

## Adding Tasks to a Tasklist

After creating a task, add it to a grouping (e.g. 考研):

```bash
lark-cli task +tasklist-task-add \
  --tasklist-id <grouping-guid> \
  --task-id <task-guid>
```

⚠️ **Flag name**: the flag is `--tasklist-id`, NOT `--tasklist-guid`. The grouping GUID goes into `--tasklist-id`.

## Creation Workflow

For a new task:

1. Parse title, due date/time, and whether it is study/exam-prep related.
2. If no due time is given, apply the default due-time rules.
   - Chinese date-only phrases such as “12号之前 / 12号前 / 截止12号” should be treated as an inclusive deadline on that date at 23:59 unless the user gives a specific time.
   - Do not ask for clarification for ordinary study-task due dates when the date is unambiguous in the current month.
3. Create the task in Feishu without a start time unless explicitly requested.
4. Prefer creating with assignee and tasklist in the same command when the CLI supports it:

```bash
lark-cli task +create \
  --summary "复盘第 15 讲课后题" \
  --due "2026-06-16T23:59:00+08:00" \
  --assignee "ou_<open_id>" \
  --tasklist-id "d1fff238-f370-4a2b-942d-cd1bbd9de074"
```

5. If direct `--assignee` or `--tasklist-id` is unavailable or fails, fall back to creating the task, then assign it:

```bash
+assign --add ou_<open_id>
```

and add it to the 考研 grouping/list when it is study/exam-prep related.
6. Read back or otherwise verify the created task state.

## Bulk Rescheduling Semantics

the user often uses compact natural language for batch task operations:

- "统统挪到后天" means push all remaining unfinished tasks to current date + 2 days; do not adjust one by one via repeated confirmations.
- "顺延昨天的任务" means only yesterday-due unfinished tasks should be moved forward.
- "今天完成 A，其他挪到 X" means A is today's focus task, not that A is already completed.
- "本周完成/听完/听到 A" means create a weekly target task due this Sunday 23:59 unless the user gives a different deadline. Use the 考研 tasklist for study items, assign to the user, and verify by reading back unfinished tasks.
- If a weekly target coexists with daily sub-tasks (e.g. tomorrow finish lecture 17 plus this week reach lecture 18 section 7), keep both: daily tasks are execution slices; weekly tasks are milestone guardrails.

Always preserve the distinction between "planned to complete" and "marked complete".

## Output Expectations

When reporting task changes:

- Lead with what changed.
- Mention failures or tasks skipped due to missing/ambiguous data.
- Do not over-explain CLI internals unless needed for debugging.
- Verify writes before claiming success.
- For task creation, verify the read-back facts you actually report: due time, tasklist membership, unfinished status, and (when needed) assignee/members. If member IDs in a raw `tasks get` response differ from the expected open_id but the task appears in `+get-my-tasks --complete=false`, report it as verified in the user's unfinished tasks rather than overclaiming the exact assignee ID.

## Common Pitfalls

- Forgetting due time on a newly created task.
- Adding a start time by default.
- Treating "今天完成 A" as completion instead of focus/planning.
- Listing completed tasks when the user asks what remains today.
- Forgetting to assign newly created tasks to the user.
- Treating all study tasks as generic daily tasks instead of routing them to 考研.
- Using memory or Graphiti instead of live Feishu state for task truth.

## Verification Checklist

- [ ] Live Feishu task state checked for task-list questions.
- [ ] New task has a due time and no unwanted start time.
- [ ] New task assigned to `ou_<open_id>`.
- [ ] Study task routed to 考研 unless explicitly excluded.
- [ ] Bulk reschedule semantics interpreted correctly.
- [ ] Result read back or otherwise verified.
