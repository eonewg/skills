# WeChat TAB / large-repo Harness article → existing concept ingestion

Use when a WeChat article about Harness / Agent engineering describes a concrete large-repo, multi-service, product-to-delivery implementation rather than a brand-new concept.

## Decision pattern

- Search for the article URL/title and existing Harness pages first.
- If `concepts/ai-harness-engineering-practice.md`, `concepts/agentic-engineering-operating-loop.md`, and `concepts/agent-knowledge-engineering.md` already cover the class, prefer **raw + patch existing pages** instead of creating another narrow `harness-*` concept page.
- Treat this class as high-signal when it gives reusable operational details: role boundaries, stage gates, human checkpoints, baseline comparison, project memory, MCP/write boundaries, or deletion of over-complex orchestration.

## Recommended patch targets

1. `concepts/ai-harness-engineering-practice.md` — primary page for the overall Harness operating model.
2. `concepts/agentic-engineering-operating-loop.md` — when the article changes workflow sequencing, stage split criteria, handoff rules, human gates, or feedback placement.
3. `concepts/agent-knowledge-engineering.md` — when the article says team-level knowledge must live in repo/wiki/specs rather than personal memory, or describes repo maps/task boards/project memory.
4. `hot.md` — if the article is relevant to current Hermes/the assistant system improvement work.

## Concrete example: TAB large-repo Harness

Article: `https://mp.weixin.qq.com/s/LGo7daiYYRf1r_YY3r-cXw`, title `从Vibe Coding到Harness——一套大仓AI工程化实战`.

Decision: no new concept page. Preserve raw as `raw/articles/tab-large-repo-ai-harness-engineering-2026.md`, then patch the three existing pages above.

Important extracted frame:

- Real bottleneck is not model coding ability but collaboration, process, trust, and delivery closure.
- Keep 4 cognitive agents: requirements, solution/design, development, code review; deterministic work belongs to controller + scripts.
- Split workflow stages by independent failure mode and different rollback target; TAB used 13 stages.
- Move cheap integration/API validation before expensive code review; developer must produce both code and verification artifacts.
- Use 7 gate scripts and baseline diff: block only newly introduced failures, not historical failures.
- Human gates are necessary but must be low-friction; if the user must click more than once per minute, the design is a bug.
- Delete orchestration mechanisms whose complexity mostly solves their own side effects (Team Mode example); prefer simpler synchronous project-level sub-agent calls when no team-specific capability is used.
- Team-level project memory belongs in repo assets such as code navigation maps, workflow definitions, task boards, and evolution logs; personal Memory is only for preferences.
- MCP is the delivery interface layer, not the Harness core: read-heavy, write-light, idempotent, trigger-scoped, and auditable.

## Verification recipe

After raw + patches:

```bash
python3 scripts/wiki_lint.py
WIKI_BUILD_SKIP_SEMANTIC=1 python3 scripts/wiki_v2_build.py
python3 scripts/wiki_v2_source_dependencies.py
python3 scripts/wiki_v2_ingestion_eval.py --case tab-large-repo-ai-harness-engineering-2026-07-09
python3 scripts/wiki_v2_query.py 'TAB 大仓 Vibe Coding Harness 13 阶段 门禁脚本 基线对比 Team Mode' --limit 5 --json --no-log
python3 scripts/wiki_v2_ingestion_eval.py
```

Accept retrieval if the targeted query returns one of the existing Harness pages in top5, especially `ai-harness-engineering-practice`; broad terms may rank older canonical pages above the freshly patched section.

## Pitfalls

- Do not create one concept page per company case if the contribution is an example of an existing Harness class.
- Do not stop at raw preservation; future retrieval should land on the durable Harness concept page.
- Do not treat Team Mode / multi-agent complexity as automatically desirable. Capture the criterion: if a mechanism mainly solves side effects it introduced and no unique capability is used, deletion is a valid Harness improvement.
- Do not put team-wide repository conventions into personal memory; this class of article belongs to repo/wiki/project assets.
