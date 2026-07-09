# Search Provider Skill Setup Notes

Use when installing or restoring third-party search skills such as AnySearch or Tavily into Hermes.

## AnySearch pattern

- Quarantine first: clone/download to `/tmp`, inspect `README.md`, `SKILL.md`, scripts, and any install docs before copying into `~/.hermes/skills/`.
- Prefer a class/category location such as `~/.hermes/skills/research/anysearch/` rather than a flat or shared-agent path.
- Run lightweight scans for destructive shell, dynamic execution, secret handling, and network endpoints before install.
- Detect runtimes as the upstream docs recommend. On the user's WSL host, Python 3 is usually the cleanest runtime; Node may also work; Bash can produce locale warnings.
- Write `runtime.conf` after verification so future usage can call the selected command directly, e.g.:

```text
Runtime: Python
Command: python3 ~/.hermes/skills/research/anysearch/scripts/anysearch_cli.py
```

- API keys belong in the skill directory `.env` when the upstream CLI explicitly loads local `.env`. Set restrictive permissions: `chmod 600 .env`.
- Verify with both `skill_view("anysearch")` and a real low-cost search such as `hello world --max_results 1`.
- AnySearch can time out on broader searches with higher result counts. If a `--max_results 3` call times out but the service otherwise works, retry with `--max_results 1` before declaring it unavailable.

## Tavily archived-skill restoration pattern

- Check whether an old Tavily skill exists under `~/.hermes/skills/.archive/tavily-search/` before searching externally.
- Restore by copying it into a category directory, e.g. `~/.hermes/skills/research/tavily-search/`, rather than moving it out of archive without a backup.
- If `skill_view` reports an ambiguous name because another skill has a reference file with the same skill name, rename the restored skill frontmatter to a unique class-level name such as `tavily-search-cli`.
- Some archived Node scripts only read `process.env.TAVILY_API_KEY` and do not load a skill-local `.env`. If the user wants key-in-skill-dir behavior, add a small `.env` loader to the top of `search.mjs` and `extract.mjs`:
  - read `<skill_dir>/.env`
  - parse `KEY=value` lines
  - populate `process.env[key]` only when unset
- Store the key in `<skill_dir>/.env`, `chmod 600`, then verify with a low-cost search.

## Provider comparison routing

When comparing Tavily, AnySearch, and Exa, use identical queries and capture elapsed time, top titles, and URLs. Avoid overclaiming from one query; use at least:

- one agent/documentation query
- one Chinese/current-events query
- one ML/research/product query

Observed routing tendency from a WSL/Hermes setup:

- Tavily: fastest and good for direct AI-style answer + source lists; useful for news/current Q&A.
- AnySearch: strong at official/source-oriented results and URL extraction, but may need lower `max_results` to avoid timeouts.
- Exa MCP: verify connection before comparison; if the MCP server is disconnected, report it as current setup state, not as a durable tool limitation.

Never save or repeat full API keys in user-facing summaries. Report the storage path, permissions, prefix/format check, and verification result instead.