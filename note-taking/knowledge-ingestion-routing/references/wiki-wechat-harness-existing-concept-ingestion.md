# WeChat Harness / Agent engineering article → existing concept ingestion

Use when a WeChat article about Harness, Agent engineering, Loop engineering, domain models, or AI Coding adds a concrete case to existing Agent/Harness pages rather than introducing a new durable concept.

## Decision pattern

- Search the wiki for the article title, source URL, author, and distinctive terms such as `Harness`, `domain-mapping`, `领域模型`, `WeTV`, `L0-L4`, `Workspace-first`, etc.
- If pages such as `concepts/ai-harness-engineering-practice.md`, `concepts/agentic-engineering-operating-loop.md`, or `concepts/agent-knowledge-engineering.md` already cover the class, prefer **raw + patch existing pages** over creating another narrow Harness page.
- Create a new concept only when the article introduces a reusable frame not already represented by existing pages.

## Recommended patch targets

For a high-signal Harness / Agent engineering WeChat article, usually patch:

1. `concepts/ai-harness-engineering-practice.md` as the primary formal page.
2. `concepts/agentic-engineering-operating-loop.md` if the article changes workflow sequencing, role boundaries, parallelism, or verification loops.
3. `concepts/agent-knowledge-engineering.md` if the article turns knowledge into machine-readable contracts, mappings, skills, evals, or runtime assets.
4. `hot.md` only when it is current enough to matter in the next few sessions.

## Concrete example: WeTV contractual multi-platform Harness

Article: `https://mp.weixin.qq.com/s/EG8YdPbBUnnyQJzcfGoIGg`, title `契约化多端架构：基于领域模型的Harness实践`.

Decision: no new concept page. Preserve raw, then patch existing pages because `ai-harness-engineering-practice` already covers the class.

Important extracted frame:

- `pages.json`, `ui-modules.json`, `data-layer.json`, `api-layer.json`, and `glossary.json` encode stable business concepts.
- `/project-init` generates `domain-mapping.json`, mapping common contracts to real per-platform code locations.
- `_PLATFORM_SPECIFIC` / `_PLATFORM_PROP_VARIATIONS` make platform differences explicit instead of letting the Agent guess.
- Reader / planner / executor / reviewer roles, main-panel-only user interaction, and L0-L4 gates turn the domain model into an executable control plane.

Good formal-page wording: “通用契约回答是什么；mapping 回答在哪里、怎么接入；平台差异显式标注；门禁验证领域模型、目录结构、API 契约、多端对等性和 E2E。”

## Verification recipe

After writing raw + patches:

```bash
python3 scripts/wiki_lint.py
WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py
python3 scripts/wiki_v2_source_dependencies.py
python3 scripts/wiki_v2_ingestion_eval.py --case <new-case-name>
python3 scripts/wiki_v2_query.py '<distinctive query>' --limit 5 --json --no-log
python3 scripts/wiki_v2_ingestion_eval.py
```

For Harness/Agent articles, add an ingestion eval case when the article materially strengthens an important concept page. The target query should include distinctive source terms, e.g. `WeTV 多端 领域模型 Harness domain-mapping 契约化 多端架构`, and should retrieve `ai-harness-engineering-practice` in the top results.

## Pitfalls

- Do not create one new `harness-*` concept per article when the article is an example of an existing Harness operating model.
- Do not stop after raw preservation; patch the existing formal page so future retrieval lands on the durable concept.
- Do not require a newly patched section to outrank a broad canonical page for a broad query. Use a distinctive query tied to the source’s actual contribution.
- If `WIKI_BUILD_SKIP_SEMANTIC=1` is used and targeted query fails for a new formal page, run a full semantic build before judging retrieval. If only existing pages were patched, the fast build is usually enough.
