# Search Provider Skill Installation Notes

Use when installing or restoring third-party search-provider skills such as AnySearch, Tavily, or Exa-backed MCP/API integrations.

## Install / restore pattern

- Quarantine first: clone or copy the skill into `/tmp` or inspect from `.archive/` before placing it under the active `~/.hermes/skills/<category>/...` tree.
- Scan scripts for destructive operations, eval/exec, shell pipes to interpreters, and network endpoints before enabling the skill.
- Prefer a class/category location such as `research/<provider-or-search-skill>` instead of root-level or one-off task folders.
- If restoring an archived provider skill, check for frontmatter name collisions. A local `SKILL.md` can collide with another reference file name; rename the restored skill frontmatter to a unique class/provider name rather than retrying `skill_view` with the same ambiguous name.

## Credential handling

- Store provider keys in the narrowest appropriate place:
  - provider-specific skill `.env` when only that skill's scripts need it;
  - `~/.hermes/.env` when Hermes/MCP/global tools need the key at startup.
- Set secret files to `0600` after writing.
- Do not echo full keys in user-facing output; verify with prefix/length only.

## Script compatibility check

Some third-party scripts only read process environment variables and do not load the skill directory's `.env`. If you store the key in the skill directory, verify the script actually reads it. If not, patch a small local `.env` loader near the top of the script, before it reads `process.env`.

For Node ESM scripts, the durable pattern is:

```js
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

function loadLocalEnv() {
  const envPath = join(dirname(dirname(fileURLToPath(import.meta.url))), ".env");
  if (!existsSync(envPath)) return;
  for (const line of readFileSync(envPath, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const idx = trimmed.indexOf("=");
    const key = trimmed.slice(0, idx).trim();
    const value = trimmed.slice(idx + 1).trim().replace(/^[ '\"]|[ '\"]$/g, "");
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}

loadLocalEnv();
```

## Verification

- Run the provider's local `doc`/help command if present.
- Run a harmless real query such as `hello world` or a known docs query and record only status, latency, result titles/URLs, and sanitized key checks.
- For MCP-backed providers, direct REST verification can prove the key works, but native MCP tools generally require a Hermes/Gateway restart to reconnect and rediscover tools.