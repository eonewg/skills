---
name: search-routing
description: Use when choosing between Exa, Tavily, and AnySearch for live web research, technical documentation lookup, news/current information, Chinese/official/PDF searches, and multi-source fact verification. Encodes the user's default search-tool routing policy and fallback rules.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, web-search, routing, exa, tavily, anysearch]
    related_skills: [exa-search-api, tavily-search-cli, anysearch, live-web-research]
---

# Search Routing

## Overview

This skill is the routing layer for the user's current search stack. It decides **which search provider to use first**, when to combine providers, and how to fall back when a result is incomplete or unreliable.

## Memory preflight

Before Chinese-platform, browser-login, CDP, or source-verification tasks, route memory with:

```bash
~/.hermes/scripts/memory_route.py tools
```

Read the returned module, normally `memory-modules/tools-memory.md`, for the user's current WSL/CDP/browser/search setup. If the task involves screenshot/image recognition or source-truth pitfalls, also read `memory-modules/mistakes-memory.md` via `memory_route.py mistakes`.

Current provider roles:

```text
Exa direct API  = default primary search engine
Tavily          = fast overview, quick answers, news/current events
AnySearch       = Chinese sources, official/PDF/vertical search, cross-checking
```

Use this skill before provider-specific skills when a task says "search", "查一下", "核实", "找资料", "看最新", "找官方文档", or otherwise needs online information and the provider choice is not explicit.

## Default Priority

Default route:

```text
1. Exa direct API
2. Tavily
3. AnySearch
```

This is not a rigid ranking. It is a routing policy:

- Use **Exa first** for normal web search, technical documentation, official-source discovery, AI/tooling research, GitHub/project lookups, papers/benchmarks, and reproducible source gathering.
- Use **Tavily first** when the user wants speed, a quick answer, breaking/current news, trend overviews, or a first-pass news radar.
- Use **AnySearch first** for Chinese-language web, official-source/PDF/vertical-source precision, and when the task explicitly asks for reliable cross-checking.

## Routing Table

Session-specific rationale and durable provider notes live in `references/exa-tavily-anysearch-routing-2026-06.md`.

| User intent | First provider | Follow-up / fallback |
|---|---|---|
| Normal web search | Exa | Tavily if quick overview needed; AnySearch for verification |
| Technical docs / API docs | Exa | AnySearch for official-source/PDF backup |
| GitHub / open-source project lookup | Exa | AnySearch if official source not found |
| AI/model/tooling research | Exa | AnySearch for papers/PDFs; Tavily for news angle |
| Current news / hot topics | Tavily | Exa for deeper sources; AnySearch for Chinese/official confirmation |
| Quick factual overview | Tavily | Exa if the answer needs citations or docs |
| Chinese sources | AnySearch | Exa for English/global sources |
| Zhihu/Xiaohongshu/Bilibili/community experience posts | CDP (chrome-cdp + cdp-text, port 9222) with cloned logged-in profile — use `cdp-text text URL` for page content | Kimi WebBridge as fallback if explicitly requested (known currentWindow bug on WSLg+Chrome 148); Exa/Tavily/AnySearch for cross-checking |
| Official notices / government / institutional source | AnySearch | Exa if AnySearch misses broader context |
| PDF / vertical source / source-specific search | AnySearch | Exa for semantic expansion |
| Important factual claim / high-stakes answer | Exa + AnySearch | Add Tavily if recency/news matters |
| User explicitly names a provider | That provider | Only fallback if it fails or result quality is poor |

## Provider-Specific Execution

### Exa direct API

Use `exa-search-api` for direct API calls. Prefer raw retrieval by default:

```bash
python3 ~/.hermes/skills/research/exa-search-api/scripts/exa_search.py \
  search "QUERY" \
  --num-results 3 \
  --highlights
```

Use Exa when you need semantic search, technical pages, official docs, structured output, or controlled reproducibility. For deeper synthesis, use `--type deep` plus `--system-prompt` and `--output-schema` only when needed.

### Tavily

Use `tavily-search-cli` for speed-oriented search, especially:

- current events
- breaking news
- quick overviews
- broad "what is happening" questions
- first pass before deeper research

Do not rely on Tavily alone for important factual claims when official/PDF/primary-source verification is possible.

### Chinese community / platform-native posts

For Zhihu, Xiaohongshu, Bilibili, and similar Chinese community experience posts, prefer native-context reading when available instead of relying on search-engine snippets.

### Chinese community / platform-native posts

For Zhihu, Xiaohongshu, Bilibili, and similar Chinese community experience posts, prefer native-context reading when available instead of relying on search-engine snippets.

**Zhihu route discipline:** use `zhihu-search` first for site-native discovery and structured search results. If the user asks to “看某人的知乎帖子 / read this specific Zhihu post” or the answer depends on a paragraph that may be missing from search summaries, then use CDP to read the full logged-in page. Do not skip straight to CDP for ordinary discovery; CDP is the full-text verification path.

the user's WSL setup has a **CDP-based logged-in browser** as the primary full-text path:

- Launch Chrome with the cloned profile: `chrome-cdp [URL]`
- Extract page content: `cdp-text text [URL]` (returns `{title, href, text}`)
- CDP port: 9222, profile at `~/.config/google-chrome-cdp`

When reporting the result, keep the tool explanation minimal. If asked why CDP was used, say: “先用知乎 skill 定位/摘要；CDP 是为了读原帖全文确认细节。”

The Kimi WebBridge extension (v1.10.0 + Chrome 148) has a known `currentWindow`/`tabs` runtime bug on WSLg. If Kimi WebBridge is explicitly requested, start the daemon and check `extension_connected:true`, but be prepared to fall back to CDP when `No current window` appears.

If all browser-based approaches are unavailable, fall back to ordinary search tools and explicitly treat results as fallback snippets rather than original-post context.

### AnySearch

Use `anysearch` for:

- Chinese-language sources
- official-source discovery
- PDF/document-heavy searches
- vertical/targeted search
- second-source verification

AnySearch is usually slower, but it is valuable as a precision and verification engine.

## Fact-Checking Policy

For important factual claims, do not use a single search engine unless the source is already authoritative and directly retrieved.

Recommended high-confidence pattern:

```text
Exa + AnySearch
```

Use this when:

- the answer could affect a decision, purchase, configuration, schedule, or public claim
- sources disagree
- the claim is new, surprising, or easy to hallucinate
- the user asks "核实", "确认", "靠谱吗", "官方有没有", "找出处"

Add Tavily when the fact is time-sensitive or news-driven:

```text
Tavily -> Exa -> AnySearch
```

## Fallback Rules

If the first provider fails:

- Exa timeout/API error → use Tavily for overview, AnySearch for verification.
- Tavily weak or generic results → use Exa for semantic/docs search.
- AnySearch sparse/slow → use Exa for expansion, then return to AnySearch with narrower terms if official/PDF proof is required.

If results are low quality:

- Remove over-tight filters.
- Rewrite the query in English for global technical sources, Chinese for domestic sources.
- For docs, include product/company/domain names.
- For papers, try title keywords + author/model name + `research paper` route.
- For official sources, use AnySearch with domain/source hints, then Exa for surrounding context.

## Output Expectations

When reporting search results:

- Say which route was used only when it matters for trust or debugging; do not over-explain tooling in casual answers.
- Prefer concise conclusions first, then sources/evidence.
- For cross-checking, explicitly distinguish confirmed facts from unresolved/conflicting evidence.
- Never expose API keys. Keys live in skill-local `.env` files or global `~/.hermes/.env`.

## Common Pitfalls

- Do not treat Exa as the only search engine. It is the default, not a monopoly.
- Do not use MCP for Exa unless the user explicitly asks. The current preferred route is Exa direct API skill.
- Do not use Tavily alone for high-stakes verification.
- Do not skip AnySearch when the user asks for Chinese, official, PDF, or vertical sources.
- Do not request full text from Exa for broad queries unless needed; use highlights first and cap text with `--text-max`.
- Do not repeat or reveal API keys in chat, logs, or summaries.

## Verification Checklist

Before finalizing a search-heavy answer:

- [ ] Provider route matched the user's intent.
- [ ] Important claims were checked with Exa + AnySearch, or a reason is stated for single-source reliance.
- [ ] Time-sensitive/current topics used Tavily or another current-source path.
- [ ] Chinese/official/PDF tasks considered AnySearch.
- [ ] Sources are recent enough for the question.
- [ ] API keys were not exposed.
