# Multi-provider Search Routing: Exa vs Tavily vs AnySearch

Use when the user asks to configure or compare live search providers, or when a research task can benefit from engine routing.

## Provider setup notes

### Exa Search API

- REST endpoint: `POST https://api.exa.ai/search`
- Auth header: `x-api-key: <EXA_API_KEY>`
- Useful body defaults for coding-agent searches:

```json
{
  "query": "...",
  "numResults": 3,
  "contents": { "highlights": true }
}
```

- Useful optional knobs from the Search API reference:
  - `type`: `auto`, `fast`, `instant`, `deep-lite`, `deep`, `deep-reasoning`
  - `category`: `company`, `people`, `research paper`, `news`, `personal site`, `financial report`
  - `includeDomains` / `excludeDomains`
  - `startPublishedDate` / `endPublishedDate`
  - `contents.text`, `contents.highlights`, `contents.summary`

### Exa MCP in Hermes

Configure the remote MCP server under `mcp_servers` with the key in headers:

```yaml
mcp_servers:
  exa:
    url: https://mcp.exa.ai/mcp
    headers:
      x-api-key: ${EXA_API_KEY or literal key from env expansion if supported}
    timeout: 180
    connect_timeout: 60
```

Hermes MCP connections are discovered at startup. If an Exa MCP tool says the server is not connected, write the config/key, verify the key with direct REST, then restart Hermes/Gateway for MCP rediscovery.

### Tavily skill scripts

Tavily search scripts commonly use `TAVILY_API_KEY` and provide `Answer + Sources`. If the key is stored in the skill directory `.env`, verify the script loads local `.env`; if not, add a small loader before reading `process.env`.

### AnySearch skill scripts

AnySearch can run anonymously but should use `ANYSEARCH_API_KEY` for higher rate limits. It returns source-like results and supports vertical search; keep `max_results` modest for reliability.

## Empirical routing from local tests

A small same-query probe across Hermes docs, Chinese CET exam timing, and Qwen3 Embedding sources showed:

- **Exa**: best default. Fast and strong on docs, official pages, technical/model sources, and research-like results.
- **Tavily**: fastest answer-oriented engine. Good for quick current summaries and news/general overview, but may rank secondary sources higher for technical/research queries.
- **AnySearch**: good official-source and vertical-source supplement. Can hit official PDFs and arXiv/GitHub well, but may be slower; start with `max_results` 1–3 and expand if needed.

## Suggested routing

- Default live web/docs/technical lookup: Exa direct API skill first.
- Quick answer/news overview: Tavily first, then Exa if sources or technical precision matter.
- Official documents, Chinese sources, PDFs, vertical lookups, and cross-checking high-impact facts: AnySearch, often paired with Exa.
- Important factual claims: do not rely on a single AI-generated answer; compare Exa + AnySearch or open primary sources.

## Exa prompt-generator choices for agent tooling

When using Exa's prompt/config generator for this setup, choose:

- **What are you building?** `Web search tool` — Exa is being exposed as a search tool used by Hermes/OpenClaw, not as the coding agent itself.
- **Integration:** `cURL` — most transparent for direct REST calls and easiest to convert into Hermes skills, shell probes, or Python wrappers.
- **Coding tool:** `OpenClaw` when asked.
- **Search type:** `Auto` as the default.
- **Content:** `Highlights` as the default token-efficient mode.
- **Search pattern:** raw retrieval (`results` + `contents.highlights`) by default; use `systemPrompt` + `outputSchema` only when Exa should synthesize grounded structured output.

Do **not** choose MCP for the default route in this environment. Exa MCP can be convenient, but direct API is preferred here because it is explicit, reproducible, hot-reload independent, and easier to debug.