# Recurring automation recall

Use this when the user asks whether a previously configured recurring task, scheduled email, digest, reminder, or automation is "还在吗 / 在不在 / 之前那个还跑吗".

## Procedure

1. **Recall the semantic target first**
   - Search durable memory for the user's phrasing and domain, e.g. `英语 邮件 每天 20:00`, before answering from memory.
   - Search prior conversations if the exact automation wording, output structure, or recipient matters.

2. **Verify live scheduler state**
   - List cron jobs and match by name, prompt preview, schedule, or destination.
   - Report `enabled/state`, schedule, next run, last run, and last status.
   - Do not rely on remembered job IDs alone; recurring automations can be renamed or replaced.

3. **Answer in status-first form**
   - Start with whether it exists and is enabled.
   - Then give the key operational details: schedule, destination, last success/failure, next run.
   - Avoid dumping the full prompt unless the user asks; summarize the durable shape.

4. **For the user's English-learning automation**
   - The durable semantic shape is daily 20:00 English reading/writing email to `user@example.com`.
   - Core sections: advanced expressions, sentence patterns, writing techniques, connectors, natural upgrades, memorisable paragraph.
   - HTML preference: white wide layout, colored vertical accents, pale-yellow paragraph cards, magazine-like spacing, flat non-nested sections.
   - A separate weekly digest may summarize recent daily emails into the local wiki as distilled knowledge, not copied raw text.

## Pitfalls

- Do not answer "yes" from memory only; live scheduler state is the source of truth for whether it is currently enabled.
- Do not expose secrets or full credential paths when reporting email automation status.
- Do not treat the last successful run as proof of future delivery if the job is disabled; always include current enabled/state and next run.