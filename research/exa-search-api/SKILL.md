---
name: exa-search-api
description: Use when searching the web through Exa's direct APIs instead of MCP. Provides Search API retrieval/synthesis and Contents API extraction with explicit parameters, highlights, text caps, summaries, structured outputs, domain/category/date filters, freshness controls, and verification commands.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, web-search, exa, api]
    related_skills: [live-web-research, anysearch, tavily-search-cli]
credentials:
  - name: EXA_API_KEY
    required: true
    description: Exa API key for https://api.exa.ai/search and https://api.exa.ai/contents
    storage: ".env file in this skill directory, ~/.hermes/.env, or process environment"
---

# Exa Direct API

## Canonical Reference

Before changing this skill or debugging an API mismatch, check the live docs:

```text
https://docs.exa.ai/reference/search-api-guide-for-coding-agents
```

That page is the source of truth for search types, parameters, response shape, and deprecated fields. If this skill disagrees with real API behavior, trust the docs/API, then patch the skill and report the stale section.

## Overview

This skill wraps Exa's **direct APIs** rather than the Exa MCP server.

Endpoints:

```text
POST https://api.exa.ai/search     # find URLs and optionally retrieve/synthesize content
POST https://api.exa.ai/contents   # extract content from known URLs
Header: x-api-key: <EXA_API_KEY>
Header: Content-Type: application/json
```

Local CLI:

```bash
python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py
```

Read `runtime.conf` if the command path ever changes.

## When to Use

Use this skill for:

- Default live web search where Exa should be the primary engine.
- OpenClaw/Hermes search-tool integration generated from Exa docs. In Exa's prompt generator, choose `Web search tool`, `cURL`, `OpenClaw`, `Auto`, and `Highlights`; do not choose MCP for this local direct-API route.
- Documentation lookup, technical research, official-source discovery, and source gathering.
- Raw retrieval for an agent loop: `results` + `contents.highlights`.
- Grounded synthesis: `systemPrompt` + `outputSchema`, with citations in `output.grounding`.
- Known-URL extraction via `/contents`.
- Searches that need highlights, capped full text, per-result summaries, domain filters, category filters, date filters, or freshness controls.
- Cases where MCP is unavailable, not hot-loaded, or too opaque for debugging.

Do not use this skill for private secrets, credentials, or personal data. Queries, URLs, and requested page content are sent to Exa.

## Command Cheatsheet

Set a shell helper when working manually:

```bash
cmd='python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py'
```

Raw retrieval, recommended default:

```bash
$cmd search "Hermes Agent cron jobs documentation NousResearch" --num-results 3 --highlights
```

Search result text, capped to protect context:

```bash
$cmd search "Qwen3 Embedding 8B MTEB benchmark" --num-results 3 --text --text-max 1200 --text-verbosity compact
```

Summaries:

```bash
$cmd search "recent AI agent benchmark reports" --num-results 5 --summary "Summarize why each source is relevant"
```

Known URL extraction through `/contents`:

```bash
$cmd contents "https://hermes-agent.nousresearch.com/docs/user-guide/features/cron" --text --text-max 2000
```

Structured synthesized output:

```bash
$cmd search "articles about GPUs" \
  --type auto \
  --system-prompt "Prefer official sources, collapse duplicate reporting, and keep the output grounded." \
  --output-schema '{"type":"object","required":["companies"],"properties":{"companies":{"type":"array","items":{"type":"object","required":["name"],"properties":{"name":{"type":"string"},"description":{"type":"string"}}}}}}' \
  --highlights
```

For longer schemas, write JSON to a file and pass `--output-schema @schema.json`.

Domain and category filters:

```bash
$cmd search "cron jobs" --include-domain hermes-agent.nousresearch.com --num-results 5 --highlights
$cmd search "Qwen3 Embedding benchmark" --exclude-domain medium.com --exclude-domain ollama.com --num-results 5 --highlights
$cmd search "Qwen3 Embedding" --category "research paper" --num-results 5 --highlights
$cmd search "OpenAI latest" --category news --num-results 5 --highlights
```

Search depth:

```bash
$cmd search "quick factual lookup" --type instant --num-results 3 --highlights
$cmd search "latency-sensitive but relevant search" --type fast --num-results 5 --highlights
$cmd search "hard research comparison" --type deep --additional-query "official documentation" --additional-query "independent benchmark" --num-results 5 --highlights
```

## Search Patterns

### Raw retrieval for your own agent

Use this as the default for agent workflows. Inspect `results` directly and pass highlights into your own reasoning:

```json
{
  "query": "recent product announcements from developer tools companies",
  "type": "auto",
  "numResults": 10,
  "contents": {"highlights": true}
}
```

### Synthesized grounded output

Use this when Exa should produce a grounded structured answer. `systemPrompt` controls source preferences and synthesis rules; `outputSchema` controls `output.content` shape. Citations/confidence are returned separately in `output.grounding`, so do not add citation/confidence fields to the schema.

```json
{
  "query": "recent product announcements from developer tools companies",
  "type": "deep",
  "systemPrompt": "Prefer official sources, collapse duplicate reporting, and keep the output grounded.",
  "outputSchema": {
    "type": "object",
    "properties": {
      "summary": {"type": "string", "description": "Grounded summary"}
    },
    "required": ["summary"]
  },
  "contents": {"highlights": true}
}
```

`outputSchema` works on every search type. Prefer `deep-lite`, `deep`, or `deep-reasoning` when synthesis requires multi-step comparison or many sources.

## Search Type Reference

| Type | Best For | Ballpark Latency | Depth |
|---|---|---:|---|
| `auto` | Most queries; balanced relevance/speed | ~1s | Smart |
| `fast` | Low-latency search with decent relevance | ~450ms | Basic |
| `instant` | Chat, voice, autocomplete, quick lookups | ~250ms | Basic |
| `deep-lite` | Cheaper synthesis when full deep is overkill | ~4s | Deep |
| `deep` | Research, enrichment, thorough results | ~4–15s | Deep |
| `deep-reasoning` | Complex multi-step synthesis | ~12–40s | Deepest |

Latency rises when using `outputSchema`, summaries, more results, or `contents.maxAgeHours: 0` livecrawls.

`additionalQueries` is only for `deep-lite`, `deep`, and `deep-reasoning`; the CLI rejects it on other types.

## API Parameters Used

Core `/search` parameters:

| Parameter | Use |
|---|---|
| `query` | Required natural-language query. Long semantic queries are OK. |
| `type` | `auto`, `fast`, `instant`, `deep-lite`, `deep`, or `deep-reasoning`. CLI default is `auto`. |
| `stream` | SSE streaming mode. CLI prints raw response when `--stream` is used. |
| `numResults` | Number of results, 1–100. CLI default is 5. |
| `category` | `company`, `people`, `research paper`, `news`, `personal site`, `financial report`. |
| `userLocation` | Two-letter ISO country code, e.g. `US`. |
| `includeDomains` / `excludeDomains` | Include/exclude domains. Repeat CLI flags for multiple domains. |
| `startPublishedDate` / `endPublishedDate` | ISO 8601 date filters. |
| `moderation` | Filter unsafe content. |
| `additionalQueries` | Extra query angles for deep variants only. |
| `systemPrompt` | Source preferences, dedupe behavior, synthesis rules. |
| `outputSchema` | JSON schema for synthesized `output.content`; accepts literal JSON or `@file`. |
| `compliance` | Enterprise-only; currently `hipaa`. |

Content options under `/search.contents`, or top-level on `/contents`:

| Option | Use |
|---|---|
| `highlights` | Query-relevant excerpts. Prefer `true` by default. Object supports `query` and `maxCharacters`. |
| `text` | Full page text as markdown. Object supports `maxCharacters`, `includeHtmlTags`, `verbosity`, `includeSections`, `excludeSections`. |
| `summary` | Generic or query-biased per-result summary. Object supports `query` and `schema`. |
| `livecrawlTimeout` | Livecrawl timeout in milliseconds. |
| `maxAgeHours` | Cache freshness: `0` always livecrawl, `-1` never livecrawl, omit for balanced default. |
| `subpages` / `subpageTarget` | Crawl and prioritize subpages. |
| `extras.links` / `extras.imageLinks` | Extract extra page links/image links. |

Text verbosity values are `compact`, `standard`, and `full`. Use `compact` by default. Always set `--text-max` when requesting text.

Case convention: raw JSON and JavaScript SDK use camelCase (`maxCharacters`, `includeHtmlTags`). Python SDK uses snake_case (`max_characters`) inside nested dicts too. This CLI sends raw JSON, so it uses camelCase.

## Freshness Controls

`maxAgeHours` controls cached content freshness:

| Value | Behavior | Use |
|---:|---|---|
| `24` | Use cache if younger than 24h, otherwise livecrawl | Daily-fresh content |
| `1` | Use cache if younger than 1h, otherwise livecrawl | Near-real-time data |
| `0` | Always livecrawl | Real-time where cache is unacceptable |
| `-1` | Never livecrawl; cache only | Maximum speed/static content |
| omit | Default fallback behavior | Recommended default |

Use `--max-age-hours 0` sparingly; it stacks latency on top of search type and content extraction.

## Routing Recommendation

For the user's current search stack:

- **Exa direct API**: default search path; best balance for docs, official sources, technical pages, and reproducible comparisons.
- **Tavily**: fastest quick-answer/news overview path.
- **AnySearch**: official-source/PDF/vertical-source backup and cross-check.
- **Exa MCP**: intentionally not used as the primary path; it depends on startup discovery and hot-reload behavior.

See `references/search-routing-and-direct-api-setup-2026-06-13.md` for routing rationale, verification probe, and MCP-vs-direct-API pitfall.

## Security and Key Handling

Key lookup order in the local CLI:

1. `--api-key` CLI flag
2. `.env` in this skill directory
3. `~/.hermes/.env`
4. process environment variable `EXA_API_KEY`

Do not print full keys in chat or logs. The CLI never prints the key intentionally.

## Common Pitfalls

- Do not confuse Exa MCP with Exa direct APIs. This skill uses direct API calls only.
- On `/search`, content options must be nested under `contents`; on `/contents`, content options are top-level.
- Do not use deprecated `useAutoprompt`, `numSentences`, `highlightsPerUrl`, `tokensNum`, or `livecrawl: "always"`.
- Do not use nonexistent `includeUrls` / `excludeUrls`; use `includeDomains` / `excludeDomains`.
- For cache freshness, use `contents.maxAgeHours: 0` on `/search`, or `maxAgeHours: 0` on `/contents`.
- `category: company` and `category: people` do not support `excludeDomains` or date filters; the CLI blocks those combinations.
- `additionalQueries` is only supported on `deep-lite`, `deep`, and `deep-reasoning`.
- Do not request full text for broad searches unless necessary; cap with `--text-max`.
- If Exa returns 401/403, verify `EXA_API_KEY` in the skill `.env` and `~/.hermes/.env` without echoing the secret.

## Verification Checklist

- [ ] `runtime.conf` points to `scripts/exa_search.py`.
- [ ] `.env` exists or `~/.hermes/.env` contains `EXA_API_KEY`.
- [ ] Search probe returns HTTP 200 results:

```bash
python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py search "hello world" --num-results 1 --highlights
```

- [ ] Contents probe returns HTTP 200 results:

```bash
python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py contents "https://example.com" --text --text-max 500
```

- [ ] Output includes title, URL, and optional highlights/text/summary without exposing the API key.
