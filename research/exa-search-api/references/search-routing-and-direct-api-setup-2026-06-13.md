# Search routing and Exa direct API setup — 2026-06-13

## Context

A session compared and configured three live-search paths for Hermes:

- Exa direct Search API through this local skill
- Tavily skill/CLI for quick search/news
- AnySearch skill for official/vertical-source search

The user explicitly preferred removing Exa MCP and keeping Exa as a local direct-API skill.

## Durable lessons

- Prefer Exa direct API over Exa MCP when the goal is predictable search behavior inside an already-running Hermes session. MCP server changes are startup/discovery dependent; direct API calls are immediately testable.
- Keep API keys in local `.env` files with `600` permissions and never echo them in chat. For Exa, both the skill-local `.env` and `~/.hermes/.env` can work.
- When comparing search providers, use identical query strings and comparable parameters. The session used `numResults=3` and highlights/text options consistently.
- Validate a search skill by making a real query against a stable documentation target, not by only checking that files exist.

## Recommended routing

- Exa direct API: default route for technical docs, official pages, semantic/source discovery, and reproducible research.
- Tavily: quick overview, fast Q&A, recent/news-shaped searches.
- AnySearch: official-source, PDF, and vertical-source cross-checking.

## Verification probe

A stable Exa probe is:

```bash
python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py \
  search "Hermes Agent cron jobs documentation NousResearch" \
  --num-results 2 \
  --highlights
```

Expected shape:

- HTTP request succeeds.
- Results include Hermes Agent cron documentation pages.
- Output includes title + URL + highlights.
- Output does not expose `EXA_API_KEY`.

## Pitfall to avoid

Do not encode a negative rule like “Exa MCP is broken.” The durable fix is narrower: use direct API for this workflow because it avoids MCP hot-reload/startup coupling and is easier to verify with explicit parameters.
