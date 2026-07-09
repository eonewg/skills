# Adapting Third-Party Claude Code Skills into Hermes

Use when a user shares a GitHub repo containing Claude Code skills and asks to install or adapt it for Hermes.

## Workflow

1. **Clone and inspect in quarantine**
   - Clone to `/tmp` or another temp directory, not directly under `~/.hermes/skills`.
   - Inspect `README.md`, `install.sh`, `skills/*/SKILL.md`, `templates/`, and `scripts/`.
   - Run a security scan for shell/network/secret/destructive patterns before installing anything.

2. **Do not blindly run upstream install scripts**
   - Claude Code repos often install into `~/.claude/skills/`, which Hermes will not load.
   - If you test an installer, run it with a temporary `HOME` and explicit data directory first.
   - Preserve the useful content, but adapt paths and assumptions to Hermes.

3. **Prefer a class-level Hermes umbrella**
   - Collapse narrow command skills such as `lc-go`, `lc-done`, `lc-review` into one umbrella when they are one workflow class.
   - Put the high-level operating loop in `SKILL.md`.
   - Put reusable starter files under `templates/` and provenance/session details under `references/`.

4. **Adapt to the user's environment**
   - Replace author-specific paths with this user's stable data roots, e.g. `~/.hermes/data/study/...`.
   - Do not assume Obsidian unless the user explicitly asks.
   - Make OS-specific commands explicit. On the user's WSL/Linux host, prefer `date -d` over macOS `date -v`.
   - Avoid model guessing where a template can carry exact values; e.g. add known URL slugs to a checklist rather than asking the model to infer them later.

5. **Initialize data safely**
   - Create parent directories and copy templates only if the destination file is missing.
   - Never overwrite user progress files without explicitly saying what would be overwritten.

6. **Verify after adaptation**
   - `skill_view(<new-skill>)` succeeds.
   - Linked `templates/` and `references/` show up.
   - Initialized data files exist and basic invariants hold, such as expected item counts and required frontmatter fields.

## Common pitfalls

- Treating a Claude Code `SKILL.md` repo as directly installable in Hermes.
- Creating three narrow Hermes skills when one class-level umbrella is clearer.
- Keeping upstream Obsidian defaults when the user prefers local non-Obsidian study data.
- Copying macOS date commands into WSL/Linux workflows.
- Losing provenance: always note source repo, inspected commit, and local changes.
