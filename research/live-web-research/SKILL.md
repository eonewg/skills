---
name: live-web-research
description: Unified guidance for live web search, Chinese web research, news/trend lookup, academic search, source routing, and AI-generated search summaries. Use when the task requires current online information, multi-provider web research, search routing, trend/news discovery, or provider-specific search summarization.
---

# Live Web Research

## Overview
This umbrella skill replaces provider-by-provider search skills with one discoverable research entrypoint organized by query type.

## Core workflow
1. Classify the request: general web facts, Chinese web results, academic literature, encyclopedia-style background, news/trends, or summarized multi-source research.
2. Preserve the user's query shape when it is explicit. If the user supplies exact Chinese keywords, abbreviations, school/院系 names, ticker-like terms, or says “直接搜/不用加别的/搜关键词”, run an exact-keyword pass first before adding qualifiers or expansions.
3. Choose a provider or router based on coverage, freshness, and output style.
4. Fetch primary sources when summaries are insufficient.
5. Cross-check high-impact claims across more than one source when possible.

## Consolidated subsections
### General live web search
Use broad web providers for current facts, docs, official sites, and source gathering.

### Chinese web and Baidu ecosystem search
Use Chinese-indexed providers when mainland-web coverage, Chinese news, or Baidu-specific sources matter. For user-facing Chinese social-platform research (知乎、小红书、B站、公众号等), especially exam experience/pain-point mining, prefer opening/searching the platform directly through Kimi WebBridge or an interactive browser path first, because generic search snippets often hide dates, comments, author context, and whether a result is stale or marketing content. If direct platform access is blocked or triggers verification, record that attempt and then use accessible mirrors/Tardis pages, search-engine results, or web_search only as fallback and cross-check; do not imply the original platform page was fully inspected.

### Chinese exam / experience-post search
When searching for考研/考试经验贴、上岸贴、高分贴, do **not** begin with broad school clusters or prestige labels. Start with the user's target taxonomy: department aliases, official department names, project names, subject codes, and intent words. Keep personal experience posts separate from考情分析 and discard institution marketing/noisy homonyms. See `references/exam-experience-search.md`.

### Search routing
Route queries across provider families instead of hard-coding one engine prematurely. For Exa/Tavily/AnySearch setup and routing, prefer Exa as the default docs/technical/official-source search, Tavily for quick answer-style/news overviews, and AnySearch for official/vertical-source cross-checking. See `references/multi-provider-search-routing.md`.

### News, trends, and vertical hot lists
Use trend/news endpoints when the task is explicitly about hot topics, ranked lists, or breaking updates.

### Academic and encyclopedia lookup
Use scholar/baike-style providers for literature discovery or concise background explanations.

### Domain-specific factual verification
When a factual query needs specialized structured sources rather than generic snippets, prefer the relevant vertical workflow. For songwriters, composers, lyricists, arrangers, producers, performers, release dates, and other music-credit trivia, use `references/music-credits-verification.md`; the old worked example is preserved at `references/music-credits-worked-example.md`.

### AI-generated web summaries
Use summary-first providers when the task benefits from synthesized answers, then verify against cited sources.

## Absorbed specialized skills
- `baidu-search`, `byted-web-search`, and `tavily-search` — engine-specific live search coverage.
- `baidu-search-router` — query routing across search providers.
- `qianfan-web-summary` and `qianfan-web-summary-pro` — search-plus-synthesis answer generation.
- `baidu-baike-data` and `baidu-scholar-search-skill` — encyclopedia and academic lookup.
- `music-credits-verification` — structured MusicBrainz-first verification for music credits and related music facts.
- `baidu-trending-hot`, `baidu-vertical-hot`, and `tencent-news` — trend/news/hot-list retrieval.

## Navigation
Absorbed provider-specific notes live under `references/`.

## Common pitfalls
- Using trend endpoints for factual research.
- Accepting AI summaries without opening primary sources.
- Using a China-focused engine for global coverage by default, or vice versa.
- Forgetting to switch to scholar/encyclopedia paths when the request is domain-specific.
- For translated/nicknamed GitHub projects (e.g. a Chinese nickname for an English repo name), run both passes: the user's exact Chinese wording first, then the likely English project name/translation. Search results can contain noisy Chinese homonyms; verify the candidate with `gh repo view` or the repo README before summarizing.
- For exam experience posts, searching broad school names or clusters first instead of the user's department/project aliases; this floods results with generic plans, paid机构文, and unrelated homonyms.

## Verification checklist
- [ ] Query class identified before choosing provider.
- [ ] Freshness and geography requirements matched to the engine.
- [ ] Primary sources opened when the stakes are non-trivial.
- [ ] Summary outputs verified against at least one direct source when needed.
