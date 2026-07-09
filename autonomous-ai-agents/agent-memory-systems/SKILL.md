---
name: agent-memory-systems
description: Unified guidance for agent memory, recall, active-memory plugins, structured knowledge stores, and self-improvement loops. Use when configuring or operating long-term memory, memory recall before replies, knowledge graphs, reflection/evolution workflows, or memory-backed OpenClaw/Hermes plugins.
---

# Agent Memory Systems

## Overview
This umbrella skill replaces narrow memory/plugin/reflection skills with one class-level entry. Use it to choose the right memory layer, wire it up safely, and decide when to use plain memory, retrieval-backed memory, structured ontology storage, or self-improvement/reflection loops.

## Core workflow
1. Identify the job: store facts, retrieve context, run recall before response, or improve the agent from history.
2. Pick the storage layer:
   - lightweight memory notes
   - retrieval/indexed memory plugins
   - structured entity graph / ontology
3. Pick the execution layer:
   - passive recall on demand
   - active memory injected before replies
   - periodic reflection/evolution jobs
4. Verify write/read paths with a tiny end-to-end example before enabling automation.

## Consolidated subsections
### Base memory patterns
Covers durable fact storage, retrieval hygiene, and maintenance conventions formerly split across general memory skills.

### Active memory before reply
Use plugin-based recall when the agent should pull relevant context before answering, not only when manually queried.

### Retrieval-backed memory plugins
Use indexed/vector memory when scale, semantic lookup, or plugin lifecycle management matters.

### Structured ontology / knowledge graph
Use typed entities and relations when projects, people, tasks, and documents must stay linked and queryable.

### Reflection and self-improvement loops
Use reflection/evolution flows when you want lessons from failures, corrections, and session history to feed future behavior.

## Absorbed specialized skills
- `Memory` — baseline long-term memory storage/retrieval guidance.
- `Self-Improving Agent` and `self-improvement` — turning corrections and failures into reusable improvements.
- `self-reflection`, `continuity`, and `capability-evolver` — scheduled or history-driven reflection/evolution loops.
- `memory-lancedb-pro` and `openclaw-active-memory` — plugin-backed retrieval and pre-reply recall.
- `ontology` — typed graph/entity memory for structured relations.

## Navigation
See `references/` for absorbed provider/plugin-specific notes and older specialized skill bodies.

Provider-specific integration notes:
- `references/tencentdb-agent-memory-hermes.md` — safe integration of TencentDB Agent Memory into an existing Hermes install: install without switching provider, sidecar env, health checks, LLM credential requirements, npm/OpenClaw postinstall pitfall, and rollback. For the user's recall workflow, prefer `memory_tencentdb_memory_search` for old projects/skill uploads, then `session_search`, then external/current-state verification; extraction uses `deepseek-v4-flash` when automation is configured for that path.
- `references/graphiti-study-task-sync.md` — Graphiti sidecar pattern for syncing Feishu unfinished tasks, OCR/PDF study materials, chapter priorities, health/study domains, daily model-pinned sync jobs, and graph-backed study briefs into `study`/`personal` graph groups.
- `references/memory-cleanup-and-skill-routing.md` — pattern for cleaning near-full hot memory/user-profile stores: remove stale preferences, compress duplicates, migrate procedures to class-level skills, and report exact changes.
- `references/modular-hot-memory-indexing.md` — pattern for turning `~/.hermes/memories/MEMORY.md` into a hot-start index plus hard rules, with topical cold-memory modules under `~/.hermes/memory-modules/` and a caution not to reactivate the legacy `~/self-improving/memory.md` PCEC file.

## Recurring automation recall

When the user asks whether a previously configured recurring task, scheduled email, digest, reminder, or automation is still present/running, use `references/recurring-automation-recall.md`: recall the semantic target from memory/conversation, then verify live scheduler state before answering.

## Common pitfalls
- Mixing ephemeral session notes with durable memory facts.
- Treating every preference tweak as hot memory. For the user, minor presentation/workflow refinements should usually update the relevant class-level skill instead; keep long-term memory for compact, stable routing facts only. Before adding memory, ask: “Will this still matter next month, and can a skill encode it better?” If yes to skill, patch the skill and keep at most one short pointer in memory.
- Treating a post-session “update the skill library” request as permission to add memory. Default to skill patches/support files only; write memory during these passes only for genuinely stable user facts that cannot live in a class-level skill.
- Writing session progress or completed artifacts to memory. Store progress in learning records/session history/scene blocks; memory should not carry PR numbers, file counts, completed lesson details, or one-off outcomes.
- Enabling automated reflection without a verification pass.
- Using ontology/graph storage for data that only needs plain notes.
- Turning on active recall before confirming memory quality.
- Treating identity/persona corrections as only a memory update. When the user corrects the assistant's role, tone, or workflow expectations during memory cleanup, update the relevant class-level skill too so the procedure survives future memory compaction.

## the user hot-memory cleanup pattern
When the user asks to "change all of these" after a cleanup/optimization proposal, execute the proposed cleanup rather than re-litigating the list: remove stale cron/jobs if explicitly included, migrate procedural rules into class-level skills, compress duplicate hot-memory entries, and keep only compact routing pointers in memory. Preserve the corrected identity wording: the assistant is the user's assistant with digital-partner style collaboration, mentor judgment, and creative problem-solving; the assistant is not a virtual girlfriend.

## Hermes/OpenClaw Graphiti MCP pattern
For a personal agent knowledge graph, prefer a sidecar MCP server over modifying the agent core. Keep Hermes/OpenClaw as the orchestrator and expose graph operations as tools (`graphiti_status`, `add_memory`, `search_facts`, `search_entities`, `recent_episodes`). Use groups such as `study`, `rules`, and `personal` to avoid mixing domains.

If Docker/Neo4j/FalkorDB is unavailable on WSL, Graphiti core can run against embedded Kuzu for a POC, but the official Graphiti MCP server currently focuses on FalkorDB/Neo4j. A custom MCP wrapper may need:
- `graphiti-core[kuzu]`, `mcp`, `uvicorn` installed in an isolated venv.
- A KuzuDriver compatibility shim: set `driver._database = <group_id>` for graphiti-core 0.29.x.
- A provider shim when the LLM endpoint supports only `/chat/completions` and not OpenAI `/responses.parse`; override structured completion to request JSON via chat completions.
- A real embedding provider later; local hash embeddings are acceptable only for first POC verification.

Verification for this pattern: first run a direct MCP client smoke test that lists tools, calls `graphiti_status`, writes one episode, reads `recent_episodes`, and searches facts before adding the server to Hermes `mcp_servers`. Hermes needs a restart/new session before newly configured MCP tools appear in live conversations.

For study/task graph ingestion, keep episodes narrow and domain-specific. Overstuffed mixed-domain episodes (e.g. one long text containing both math and computer-organization tasks) may lead the LLM extractor to preserve the main chain while dropping side facts. Prefer one episode per learning chain or subject slice, then verify with at least two literal queries: one for the core material relation and one for the task/status relation. If Chinese short-token search is weak, supplement Graphiti search with a literal Kuzu fact scan rather than relying only on FTS.

## Verification checklist
- [ ] Chosen memory layer matches the task class.
- [ ] Read path works before automated writes are enabled.
- [ ] Automated reflection/evolution has clear scope and rollback path.
- [ ] Plugin/provider-specific details were checked in `references/` if relevant.
