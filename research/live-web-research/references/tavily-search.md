---
name: tavily-search
description: Search the web via Tavily API and extract article content. Use when users ask for live web research, current information, source gathering, news lookup, or URL content extraction through Tavily.
homepage: https://tavily.com
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Tavily Search

AI-optimized web search using Tavily API. Designed for AI agents and source gathering.

## Search

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 10
node {baseDir}/scripts/search.mjs "query" --deep
node {baseDir}/scripts/search.mjs "query" --topic news
```

## Options

- `-n <count>`: Number of results (default: 5, max: 20)
- `--deep`: Use advanced search for deeper research
- `--topic <topic>`: `general` or `news`
- `--days <n>`: For news topic, limit to last n days

## Extract content from URL

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
```

## Notes

- Needs `TAVILY_API_KEY`
- Use `--deep` for more involved research
- Use `--topic news` for current events
- Use extraction when the user already has a URL and wants the page content
