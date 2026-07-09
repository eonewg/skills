---
name: lark-cli-task-management
description: Manage Ethan's Feishu/Lark tasks with lark-cli from the terminal. Use whenever the user asks what tasks remain, to create/update/complete/reschedule tasks, or to adjust study-plan task names and due dates. Triggers on requests like “今天还有什么任务”, “加个任务”, “顺延到明天”, “标完成”, “改成…”, or any Feishu task-list operation.
---

# Lark CLI task management

Use `lark-cli task` for all task CRUD. Do not switch to other task tools.

Check current date first with `date '+%F %T %Z'` so “今天 / 明天 / 后天” maps to the right ISO due date.

List only unfinished tasks:

```bash
lark-cli task +get-my-tasks --complete=false --format json
```

Important: `+get-my-tasks` without `--complete=false` returns completed tasks too.

When scripting against `+get-my-tasks --format json`, current task rows expose the due timestamp as top-level `due_at` (for example `2026-06-12T23:59:00+08:00`), not necessarily under a nested `due` object. Date filters such as “昨天/今天/明天” should parse `item["due_at"]` first, then fall back to legacy/nested due fields if needed. This avoids falsely reporting zero tasks when the CLI response shape uses `due_at`.

Common operations:

```bash
# complete one task; for multiple completions, run one command per task unless the current CLI help explicitly confirms comma support
lark-cli task +complete --task-id '<guid>' --format json

# rename or change due date
lark-cli task +update --task-id '<guid>' --summary '新标题' --due '2026-04-27T23:59:00+08:00' --format json

# move multiple existing tasks to one date
lark-cli task +update --task-id 'id1,id2,id3' --due '2026-04-27T23:59:00+08:00' --format json

# create new task
lark-cli task +create --summary '任务标题' --due '2026-04-27T23:59:00+08:00' --format json

# create new task with explicit start time (preferred when user wants 开始时间)
lark-cli task +create --data '{"summary":"任务标题","start":{"timestamp":"1714181400000","is_all_day":false},"due":{"timestamp":"1714233540000","is_all_day":false}}' --format json

# immediately assign after create
lark-cli task +assign --task-id '<new-guid>' --add 'ou_<open_id>' --format json
```

### Delete tasks (permanent)

There is no `+delete` convenience command. Use the raw `task tasks delete` subcommand. Requires `--yes` flag for high-risk-write confirmation.

```bash
# search for tasks to delete — check both incomplete and completed
lark-cli task +get-my-tasks --complete=false --format json
lark-cli task +get-my-tasks --complete=true --format json

# filter by keyword (e.g. "腰") in summary using python3
lark-cli task +get-my-tasks --complete=false --format json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); items=d.get('data',{}).get('items',[]); \
  [print(t['guid'], t.get('summary','')) for t in items if '腰' in t.get('summary','')]"

# delete a single task by GUID
lark-cli task tasks delete \
  --params '{"task_guid":"<task-guid>"}' \
  --yes \
  --format json

# delete multiple in a loop
for guid in <guid1> <guid2> <guid3>; do
  lark-cli task tasks delete \
    --params '{"task_guid":"'$guid'"}' \
    --yes --format json 2>/dev/null
done
```

Pitfalls:
- The convenience commands (`+complete`, `+update`, `+get-my-tasks`) use `--task-id` but the raw `task tasks delete` uses `--params '{"task_guid":"..."}'`. Different flag path, same GUID value.
- There is no bulk-delete. Iterate per-task.
- Deletion is permanent — there is no undo.
- After deletion, verify by re-running `+get-my-tasks` to confirm the task no longer appears.

Tasklist / grouping operations:

Important terminology: 飞书里“任务清单”对应 `tasklists`，而用户说“任务分组，不是任务清单”时通常指自定义分组 `sections`。Do not answer section questions from `tasklists list` alone.

Use recurring calendar events plus milestone tasks for multi-week plans (rehab, study, training, habit building). The plan itself should not become one giant task: create execution blocks in Calendar, then create a tasklist with review/completion milestones. See `references/lark-cli-multi-week-plan-scheduling.md`.

```bash
# inspect available tasklist commands
lark-cli task --help
lark-cli task tasklists --help
lark-cli task +tasklist-create --help
lark-cli task +tasklist-task-add --help

# list visible tasklists; can return [] even before custom lists exist
lark-cli task tasklists list --format json

# inspect task section commands (custom groups, not tasklists)
lark-cli task sections --help
lark-cli schema task.sections.list

# list custom groups under My Tasks; requires user/app scope task:section:read
lark-cli task sections list --params '{"resource_type":"my_tasks"}' --format json

# list custom groups under a specific tasklist; requires resource_id=<tasklist guid>
lark-cli task sections list --params '{"resource_type":"tasklist","resource_id":"<tasklist-guid>"}' --format json

# create a tasklist/group; add Ethan as member when creating a personal study group
lark-cli task +tasklist-create --name '考研' --member 'ou_<open_id>' --format json
```
# add existing tasks to a tasklist; task ids are comma-separated
lark-cli task +tasklist-task-add --tasklist-id '<tasklist-guid>' --task-id 'id1,id2,id3' --format json

# verify tasks inside a tasklist; parameter key is tasklist_guid
lark-cli task tasklists tasks --params '{"tasklist_guid":"<tasklist-guid>"}' --format json
```

Notes from practice: Feishu's “任务清单” corresponds to tasklists via CLI/API. “任务分组” corresponds to `sections`, not tasklists. Use `lark-cli task sections list --params '{"resource_type":"my_tasks"}' --format json` for the user's “我负责的” custom groups; this requires `task:section:read`. Creating/updating/deleting groups requires `task:section:write` and commands such as `lark-cli task sections create --data '{"resource_type":"my_tasks","name":"考研"}' --format json`. As of the current Feishu Task v2 API/CLI, `my_tasks` sections can be created/listed/read, but there is no exposed CLI/schema field to move existing tasks from the default “我负责的” section into a non-default `my_tasks` section. The only exposed move mechanism with `section_guid` is `+tasklist-task-add --tasklist-id ... --section-guid ...`, which moves/adds tasks inside a **tasklist** section, not a top-level “我负责的” section. If the user asks to convert tasklists to top-level groups, create the `my_tasks` sections if requested, but state clearly that task migration into those groups is blocked by API/CLI support unless done manually in the Feishu UI or via a future API.

`+tasklist-search` with no query/filter fails with validation_error 1470400; use `task tasklists list` to list visible tasklists. However, `tasklists list` and `+tasklist-search --query ...` may not immediately show a newly created tasklist; verify creation by saving the returned `guid` and calling `lark-cli task tasklists get --params '{"tasklist_guid":"<tasklist-guid>"}' --format json`. For adding all current unfinished tasks to a tasklist, first run `+get-my-tasks --complete=false`, collect the `guid` values, then pass them as a comma-separated `--task-id` list to `+tasklist-task-add`, and verify with `tasklists tasks`.

Sections permissions: if `lark-cli task sections list --params '{"resource_type":"my_tasks"}' --format json` fails with `insufficient permissions (required scope: task:section:read)`, report that section count is not currently readable and say exactly that the missing scope is `task:section:read`. Do not imply that the tasklist count is the section count. Bot identity may also fail with `App scope not enabled`; that is an app scope/config issue, not evidence that sections do not exist.

After creating a task, always run `+assign --add ou_<open_id>`. Creation alone does not reliably set Ethan as assignee.

Default study tasklist:学习相关任务默认加入清单「考研」(`d1fff238-f370-4a2b-942d-cd1bbd9de074`)，除非用户特意说明不是考研学习任务。After creating and assigning a study task, also run:

```bash
lark-cli task +tasklist-task-add --tasklist-id 'd1fff238-f370-4a2b-942d-cd1bbd9de074' --task-id '<new-guid>' --format json
```

Interpretation rules:

- If the user asks “今天还有什么任务”, report only unfinished tasks due today.
- If the user asks “今天从哪个任务开始 / 先做哪个 / 怎么排今天任务”, first fetch unfinished tasks and the current time, then make the recommendation fit the actual clock. Do not say “上午做…” if it is already late morning/noon; use the remaining day blocks instead. When math and 408 are both behind, prioritize one math closure loop plus one 408 continuity loop rather than evenly touching every task or opening too many new lectures. If the user just learned a lecture yesterday and today has both “复盘/笔记” and older exercise tasks, put the fresh-review task first: convert yesterday’s input into notes/recall before doing related课后题 or returning to older backlog, but keep the review time-boxed so it does not become a full rewatch. For short remaining windows such as 60–90 minutes, recommend one small closure loop rather than opening multiple tasks; if the user wants to switch subjects (e.g. “可以先听计组吗”), allow it instead of fighting the preference, but give a low-loss structure such as 50 minutes lecture/problem + 20 minutes handwritten framework or error-cause notes. For very short windows such as ~30 minutes, do not force a task that has a known warm-up/review cost longer than the window. If the user says a candidate task needs 40–50 minutes or requires复习 before doing problems, treat that as accurate local context: either pick a smaller independent closure task or explicitly call a clean postponement to tomorrow a rational撤退, not摆烂. Prefer finishing a pending exercise set over starting a new lecture when the time block is short, unless the user is clearly resisting exercises.
- If the user asks “明天什么任务 / 后天什么任务 / 某天有什么任务”, report only unfinished tasks due on that target date instead of dumping the whole backlog.
- If the user says “过期的任务全部挪到今天 / move all overdue tasks to today”, update **all unfinished tasks whose due date is before today** to today 23:59. Do not include already-completed tasks.
- If the user says to postpone yesterday’s tasks to today, update only tasks due yesterday and unfinished, not every overdue task in the system.
- If the user refers to study lectures by Chinese numerals or Arabic numerals (e.g. “第十讲和十一讲”), match both forms (`第10讲`/`第十讲`, `第11讲`/`第十一讲`) and include directly related variants such as 复盘、课后题、1000题.
- If the user says to move **all tasks each by N days** (e.g. “所有的任务都各自往后顺延两天”), treat it as a relative shift: add N days to every referenced task’s current due date individually. Do **not** collapse them onto one common date.
- If the user says “今天完成 A/B，其他全部挪到 X”, interpret A/B as tasks scheduled for today, not as already completed; keep/reopen them as unfinished unless the user explicitly says “标完成/已完成/做完了”.
- If the user says “今天/明天/后天” inside a long-running or late-night session, do not reuse an earlier date from the conversation. Re-run `date '+%F %T %Z'` immediately before writing, and derive the due date from that fresh output. This matters after midnight: a session that started on 5/15 may already be 5/16 when the task is updated.
- If a CLI write involving multiple task IDs fails with `Invalid Param 'task_guid'`, retry as separate per-task calls. In practice, `+complete` may reject comma-separated task IDs even though other operations such as `+update` accept them.
- If the user schedules a bundled study pair like “明天/后天是第X讲复盘和课后题”, treat it as plan-setting, not description. Move the existing matching tasks to that date, and if one half of the pair is missing in Feishu, create the missing counterpart immediately using the same due date, then assign Ethan and add it to the `考研` tasklist.
- If the user adds a study task with an ellipsis-style continuation such as “再加，完成计组5.4习题” immediately after setting a target date for a prior task (e.g. “明天加任务…”), inherit the same target date unless the new message gives a different date. Still re-run `date` first for relative-date resolution, create with due 23:59 by default, assign Ethan, add to `考研`, and verify by reading unfinished tasks back.
- If the user corrects only a subset after a bundled move (e.g. “前4节放周五” after “十四讲放周六”), update only the explicitly named subset and preserve the rest of the bundle. Do not re-collapse related lecture tasks onto one date just because they share the same chapter number.
- Treat “整讲/第X讲” tasks and partial tasks such as “第X讲前4节” as separately schedulable unless the user explicitly says to move them together.

Verification before replying:

- Re-run `lark-cli task +get-my-tasks --complete=false --format json` after create/update/complete.
- Confirm the changed task titles and due dates in the reply.
- When the user used relative language like “今天/明天” but the session is around midnight or the target date matters, state the explicit date in the reply (e.g. `2026-05-17 23:59`) rather than only saying “今天”, to avoid ambiguity.
- Keep the user-facing reply short and chatty; no verbose command dump.
