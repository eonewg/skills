# Lark CLI multi-week plan scheduling

Use this when the user gives a multi-stage plan (rehab, study, training, habit building) and asks to “安排一下这个计划”. The durable workflow is to combine recurring calendar blocks for execution with milestone tasks for review/completion.

## Pattern

1. Run `date '+%F %A %T %z'` before interpreting relative dates or starting today.
2. Split the plan into phases with explicit date ranges and weekly frequency.
3. Create recurring Feishu Calendar events for the actual practice blocks. Keep each event description compact but actionable: exercises/checklist, duration, stop conditions, and phase progression criteria.
4. Create a Feishu tasklist for the overall plan when it has multiple phases.
5. Create milestone/review tasks with due dates at phase boundaries. For the user, every created task needs a due time and immediate assignment:

```bash
lark-cli task +create --summary '<title>' --description '<desc>' --due '<YYYY-MM-DDT23:59:00+08:00>' --tasklist-id '<tasklist-guid>' --assignee 'ou_<open_id>' --format json
lark-cli task +assign --task-id '<new-guid>' --add 'ou_<open_id>' --format json
```

6. Add a reminder to milestone tasks if appropriate:

```bash
lark-cli task +reminder --task-id '<new-guid>' --set '1d' --format json
```

7. Verify both surfaces before replying:

```bash
lark-cli calendar +agenda --format table
lark-cli task +search --query '<plan keyword>' --format table
```

## Recurring calendar example

```bash
lark-cli calendar +create \
  --calendar-id primary \
  --summary '腰椎康复训练｜第1-2周：稳住腰' \
  --start '2026-05-21T21:30:00+08:00' \
  --end '2026-05-21T21:50:00+08:00' \
  --rrule 'FREQ=WEEKLY;COUNT=10;BYDAY=MO,TU,WE,TH,FR' \
  --description '15-20分钟：腹式呼吸+腹部轻收紧；骨盆后倾；腹部支撑；低幅度臀桥；轻松步行。原则：腰椎中立位；腿麻/放射痛立刻停止。' \
  --format json
```

## Domain-sensitive notes

For medical/rehab plans, do not improvise beyond the user-provided clinician guidance. Preserve red flags and stop conditions in descriptions: worsening pain, leg numbness/pain, radiating pain, weakness, gait changes, bowel/bladder symptoms, or saddle numbness. Avoid turning the reply into medical certainty; present it as scheduling the provided plan.

## User-facing reply

Keep it short: say it is arranged, list the start time/frequency, tasklist name, and milestone count. Do not dump commands or long exercise detail unless asked; the details live in the calendar/task descriptions.
