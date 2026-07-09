# Exa / Tavily / AnySearch Routing Notes

## Durable decision

For the user's current research stack, default to a three-engine route rather than a single search tool:

```text
Exa direct API  = primary/default search engine
Tavily          = quick overview, quick Q&A, current/news radar
AnySearch       = Chinese sources, official/PDF/vertical-source precision, cross-checking
```

## Why this route

- Exa direct API is preferred over Exa MCP for operational control: explicit HTTP parameters, easier verification, no MCP hot-load/connection ambiguity, and straightforward wrapping as a local skill.
- Tavily is useful when the user's intent is speed or a high-level current overview rather than exhaustive source control.
- AnySearch is the verification and source-quality layer, especially for Chinese, official, PDF, and vertical searches.

## Default execution patterns

Normal search:

```text
Exa
```

News / current event overview:

```text
Tavily -> Exa
```

Important fact verification:

```text
Exa + AnySearch
```

Chinese / official / PDF / vertical source:

```text
AnySearch -> Exa
```

Technical docs / API docs / GitHub / AI tooling:

```text
Exa -> AnySearch if primary-source confirmation is needed
```

## User-facing behavior

Do not over-explain the routing in normal answers. Mention the route only when it improves trust, debugging, or source interpretation. Keep API keys out of chat and logs.
