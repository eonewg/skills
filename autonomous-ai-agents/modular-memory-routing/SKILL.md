---
name: modular-memory-routing
description: Route the user/the assistant tasks to modular cold-memory files under ~/.hermes/memory-modules and ~/.hermes/user-modules before answering or acting. Use when the current task depends on the user-specific study state, user profile, process semantics, style rules, tool paths, long-term projects, or known mistakes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, routing, personalization]
---

# Modular Memory Routing

## Purpose

`~/.hermes/memories/MEMORY.md` is the hot operational index and hard-rule layer. `~/.hermes/memories/USER.md` is the hot user-profile index. Detailed stable memories live under:

- `~/.hermes/memory-modules/` — operational/task/process/style/tool/project/mistake memory.
- `~/.hermes/user-modules/` — the user's detailed user profile modules.

Use this skill to load only the relevant cold-memory module instead of injecting every detail into hot memory.

## Routing table

Operational modules:

- Study / kaoyan / subject planning / learning status → read `memory-modules/study-memory.md` and usually `user-modules/study-profile.md`.
- Wiki ingestion / links / Feishu tasks / email / recall order / recurring workflow semantics → read `memory-modules/process-memory.md`; for user-specific defaults also read `user-modules/workflow-profile.md`.
- Chat tone / Feishu formatting / lesson writing / teaching pages / copy style → read `memory-modules/style-memory.md` and, if user preference matters, `user-modules/preferences.md`.
- WSL / browser CDP / search routes / SSH / servers / local paths / tool quirks → read `memory-modules/tools-memory.md`.
- Wiki/teach/homepage/Wangzhe learning assets/long-lived projects/health and hobbies → read `memory-modules/project-memory.md`; for health/hobbies also read `user-modules/health-and-hobbies.md`.
- Any task involving a known prior error, image recognition, email From, wiki archival truth, Feishu table output, or task-semantics ambiguity → read `memory-modules/mistakes-memory.md`.

User modules:

- Identity / naming / timezone / Feishu ID → read `user-modules/identity.md`.
- Study identity / exam state / subject timings → read `user-modules/study-profile.md`.
- Communication, execution, food/music/content preferences → read `user-modules/preferences.md`.
- Health, exercise, games, running → read `user-modules/health-and-hobbies.md`.
- Task/calendar/email/teaching/server preferences → read `user-modules/workflow-profile.md`.
- Accounts, email, GitHub/homepage handles → read `user-modules/accounts.md`.

Unsure which module applies → read the relevant `index.md` first, then the smallest relevant subset.

## Procedure

1. Classify the user request into one or more memory domains.
2. Read the smallest relevant module(s) with `read_file`.
3. For procedures, also load the proper skill: e.g. `knowledge-ingestion-routing`, `feishu-task-routing`, `teach-html-design`, `static-site-operations`, `search-routing`, or `agent-memory-systems`.
4. For knowledge answers, query wiki/TencentDB/session history as needed; module memory is context, not authoritative proof of current external state.
5. Do not write new module facts unless the user states a stable preference/fact or asks to restructure memory. Procedures belong in skills; durable knowledge belongs in wiki; transient progress belongs in session history.

## Authority hierarchy

- Stable user identity/profile facts → `USER.md` + `user-modules/`.
- Hard operational guardrails and routing pointers → `MEMORY.md`.
- Executable procedures and verification checklists → skills.
- Formal durable knowledge and research synthesis → wiki.
- Conversation history and old project recall → TencentDB memory search, then `session_search`.
- Current external/system facts → live tools; module memory is not proof of current state.

## Mistakes trigger

Always include `memory-modules/mistakes-memory.md` when the task involves: image/screenshot recognition, email sending/From headers, wiki/Bilibili/raw archival truth, Feishu task semantics, or Feishu message formatting.

## Update routing

When a new durable fact appears:

- User identity/account/profile → `user-modules/identity.md` or `accounts.md`.
- Study schedule/state → `user-modules/study-profile.md` and, if operational, `memory-modules/study-memory.md`.
- Communication/content preference → `user-modules/preferences.md` or `memory-modules/style-memory.md`.
- Workflow preference/task semantics → `user-modules/workflow-profile.md` or `memory-modules/process-memory.md`.
- Tool path/environment quirk → `memory-modules/tools-memory.md`.
- Repeated error/prevention rule → `memory-modules/mistakes-memory.md`.
- Procedure → patch/create a skill, not a module.
- Knowledge synthesis → wiki, not memory.

Run `~/.hermes/scripts/memory_lint.py` after structural edits.

## Maintenance rules

- Keep `MEMORY.md` short: index + hard rules only.
- Keep `USER.md` short: identity index + essential stable profile only.
- Keep module files compact and domain-specific.
- Every module should have frontmatter with `type`, `domain`, `priority`, `decay`, `last_reviewed`, and `owner`.
- If a module entry becomes an executable workflow, migrate it into a skill and leave only a pointer in the module.
- If a module entry becomes formal reusable knowledge, archive it in wiki and leave only a pointer.

## Verification

After changing memory modules:

- Read `~/.hermes/memories/MEMORY.md` and the touched modules.
- Confirm `MEMORY.md` remains an index rather than a detail dump.
- Confirm no outdated legacy identity such as OpenClaw/Ethan/PCEC leaked back into current Hermes memory.
