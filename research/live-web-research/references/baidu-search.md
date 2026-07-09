---
name: baidu-search
description: Search the web using Baidu AI Search Engine (BDSE). Use when users need live Chinese web information, documentation, recent news, research topics, or filtered Baidu search results.
metadata: { "openclaw": { "emoji": "🔍︎",  "requires": { "bins": ["python3"], "env":["BAIDU_API_KEY"], "python":["requests"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# Baidu Search

Search the web via Baidu AI Search API.

## Usage

```bash
python3 skills/baidu-search/scripts/search.py '<JSON>'
```

## Requirements

- `BAIDU_API_KEY`
- Python package: `requests`

## Request Parameters

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | str | yes | - | Search query |
| edition | str | no | standard | `standard` (full) or `lite` (light) |
| resource_type_filter | list[obj] | no | web:20, others:0 | Resource types: web (max 50), video (max 10), image (max 30), aladdin (max 5) |
| search_filter | obj | no | - | Advanced filters |
| block_websites | list[str] | no | - | Sites to block |
| search_recency_filter | str | no | - | Time filter: `week`, `month`, `semiyear`, `year` |
| safe_search | bool | no | false | Enable strict content filtering |

## Examples

```bash
python3 skills/baidu-search/scripts/search.py '{"query":"人工智能"}'
```

## Current Status

Fully functional.
