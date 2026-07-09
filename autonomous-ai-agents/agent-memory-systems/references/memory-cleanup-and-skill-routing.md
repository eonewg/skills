# Memory Cleanup and Skill-Routing Pattern

## When to use

Use this pattern when Hermes hot memory or user profile is near capacity and the user asks what to do, or when a new durable rule should be saved but memory is full.

## Decision rule

Do not treat memory and skills as interchangeable:

```text
Memory = compact high-frequency defaults and user preferences
Skill  = class-level execution procedure, parameters, pitfalls, verification, fallback logic
Reference file = session-specific rationale, examples, provider quirks, or detailed notes
```

For rules such as search routing, task workflows, or document pipelines, keep only a short trigger/default in memory and put the actual operational detail in a class-level skill.

## Safe cleanup workflow

1. List a proposed cleanup plan before editing if the user has not already authorized changes.
2. Remove stale preferences first, especially explicitly revoked preferences.
3. Consolidate duplicates into one declarative entry.
4. Move procedural details to the relevant class-level skill or `references/` support file.
5. Update both `memory` and `user` stores when the stale rule appears in both places.
6. For TencentDB/active-memory systems, also inspect the injected narrative/persona file (e.g. `~/.memory-tencentdb/memory-tdai/persona.md`). If it has session-specific progress, psychoanalytic prose, or duplicated scene summaries, back it up and compress it into compact routing facts plus pointers to scene blocks. Do not manually delete vector DB rows unless an explicit admin/delete path exists and a backup was made.
7. Report exactly what changed and the before/after capacity when available.

## Pitfalls from this session

- If a memory add/replace fails, do not claim the rule was newly saved. Check the tool result: it may have merely shown an existing compressed entry.
- Morning brief / cron-like preferences can become stale. If the user says a recurring workflow is no longer needed, remove its memory/profile entries and separately offer to inspect cron jobs; do not assume memory cleanup stopped scheduled jobs.
- Channel migration must be reflected in both memory stores when duplicated. In this session, daily chat/reminders/Q&A moved from Telegram to Feishu.
- Preserve high-value compact defaults; do not keep long procedural commands in hot memory if a skill can hold them.

## Compression examples

Verbose style fragments can become one entry:

```text
Style: friend-like chat; direct and opinionated for professional topics; no customer-service tone, excessive apologies, self-reference, or manual-like prose; casual humor allowed; at most one trailing emoji.
```

Search routing can become one memory line plus a skill:

```text
Memory: search defaults to Exa; news/quick overview Tavily; Chinese/official/PDF/fact-check AnySearch.
Skill: search-routing stores the full routing table and fallback policy.
```

Task rules can become one compact default plus a task/Feishu skill:

```text
Memory: Feishu unfinished tasks are the daily source; tasks/reminders/calendar use Feishu; new tasks need deadlines; no-time defaults to 23:59.
Skill: Feishu task workflow stores exact commands, assignee IDs, groups/lists, and verification steps.
```
