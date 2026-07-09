# Modular hot-memory indexing

Use this when the user discusses restructuring Hermes memory, asks what `MEMORY.md` should contain, or proposes splitting memory into topical files.

## Principle

Treat Hermes hot memory as a **navigation layer**, not as the long-term warehouse.

Recommended layering:

- `~/.hermes/memories/MEMORY.md` — hot-start index, hard rules, routing triggers.
- `~/.hermes/memories/USER.md` — hot user-profile index with only essential identity/profile facts.
- `~/.hermes/memory-modules/*.md` — optional operational cold-memory files loaded on demand.
- `~/.hermes/user-modules/*.md` — optional detailed user-profile modules loaded on demand.
- Skills — procedural workflows and task-class rules.
- Wiki — durable concept/entity/raw-source knowledge.
- TencentDB / Graphiti — semantic recall and relationship graph.
- Session search — raw historical transcript fallback.

## Proposed module layout

If implemented, use directories such as:

```text
~/.hermes/memory-modules/
  index.md
  study-memory.md
  process-memory.md
  style-memory.md
  tools-memory.md
  project-memory.md
  mistakes-memory.md
  changelog.md

~/.hermes/user-modules/
  index.md
  identity.md
  study-profile.md
  preferences.md
  health-and-hobbies.md
  workflow-profile.md
  accounts.md
```

Typical operational responsibilities:

- `study-memory.md`: exam target, subject cadence, study constraints, durable learning state.
- `process-memory.md`: Feishu task semantics, archive workflow, wiki routing, recurring process rules.
- `style-memory.md`: chat tone, Feishu format rules, teaching/lesson writing preferences.
- `tools-memory.md`: WSL paths, CDP browser setup, email/tool quirks, SSH aliases.
- `project-memory.md`: durable project routing pointers, not transient progress.
- `mistakes-memory.md`: compact “do not repeat” lessons that should be high-priority but not flood `MEMORY.md`.

## Hot MEMORY.md shape

Keep only:

1. Pointers to the module directory.
2. A short trigger map: “study → read study-memory.md”, “archive/process → read process-memory.md”, etc.
3. A few truly global hard rules, such as Feishu no-Markdown-table formatting and identity/tone boundaries.
4. Recall order: TencentDB memory search → session_search → external/current-state verification.

Do not keep long procedures, session outcomes, source summaries, PR numbers, task progress, or copied article knowledge in hot memory.

## Implementation requirement

A module file is not useful merely because it exists. Add or maintain a routing skill/pattern so the agent knows when to read the relevant file. The practical target is:

```text
Hot MEMORY.md = index + hard rules
modular-memory-routing skill/pattern = load the right module on demand
memory-modules/*.md = topical cold memory
wiki/TencentDB/Graphiti = broader knowledge and recall
```

## Legacy root memory.md caution

The file `~/self-improving/memory.md` is a legacy self-improving/PCEC HOT Tier file from 2026-03-26, not the active Hermes profile memory. It contains stale cues such as `PCEC`, `Ethan`, and old Exa MCP/Feishu-task wording. Do not treat it as the current memory index or merge it blindly into current Hermes memory. If touched, archive it as legacy rather than reactivating old rules.

Current active Hermes memory files are under:

```text
~/.hermes/memories/MEMORY.md
~/.hermes/memories/USER.md
```

## Good migration sequence

1. Create `~/.hermes/memory-modules/` and draft module files.
2. Move procedural details from hot memory into the appropriate module or skill.
3. Compress hot `MEMORY.md` into a short index and hard-rule set.
4. Add/update the routing skill so future sessions know when to read modules.
5. Verify by asking a study/process/style/tool question and confirming the correct module is loaded before answering.
