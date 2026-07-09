# Graphiti study task sync pattern

Use this when building or maintaining a Hermes/OpenClaw personal knowledge graph that connects study tasks, PDFs/OCR outputs, chapters, priorities, and task status.

## Pattern

- Keep Graphiti as a sidecar MCP server; do not change Hermes core.
- Use `study` for exam/study entities and `personal` for health/life tasks.
- Pull Feishu tasks with:

```bash
lark-cli task +get-my-tasks --complete=false --format json
```

- Split task-sync episodes by domain before writing:
  - 考研数学 → `study`
  - 408/计组 → `study`
  - 腰椎康复/health → `personal`
- Keep each episode narrow. Numeric section facts like `5.6` / `5.7` may be dropped from mixed episodes, so add a separate focused episode for tiny corrections or current-focus facts.
- Store Feishu task `summary`, `guid`, `due_at`, `url`, incomplete status, and simple scheduling relation.

## Useful script shape

A sync script should:

1. Run `date '+%F %T %Z'` for an explicit snapshot time.
2. Fetch unfinished Feishu tasks only.
3. Classify tasks by title keywords.
4. Build one episode per domain.
5. Call MCP tools over stdio: `graphiti_status`, `add_memory`, then `search_facts` for verification.
6. Print `SUMMARY {"ok": true, "episodes_written": N, "task_count": M}`.

A read/brief script should consume the graph after sync and stay read-only:

1. Call `graphiti_status`.
2. Query `study` facts by sections such as 数学主线, 408计组, and 资料状态.
3. Deduplicate facts before printing.
4. Produce a concise decision brief: main closure loop, continuity loop, downgraded tasks, and linked materials.
5. Keep recommendations grounded in returned facts; if a fact is missing, either query more literally or omit the recommendation.

For the user’s setup, the daily sync cron can be model-pinned to SenseNova instead of the current chat model:

```yaml
provider: custom:sensenova
model: deepseek-v4-flash
workdir: ~/.hermes/graphiti-mcp
deliver: local
```

Use `deliver: local` for quiet background sync jobs unless the user explicitly wants a chat notification.

## Verification queries

After writing, verify with literal queries, not only broad semantic queries:

- `张宇 第十四讲 第十一讲1000题 飞书任务` in `study`
- `计组5.6 5.7 5.3 未完成任务` in `study`
- `腰椎 康复 未完成任务` in `personal`

Expected useful facts include:

- `张宇第十四讲前4节优先级高于第十一讲1000题`
- `第十一讲1000题属于考研数学领域`
- `计组5.3习题优先级低于数学主线，属于可降级处理的任务`
- `任务「听完计组第五章」当前实际含义是继续听计组第五章中的5.6/5.7小节`

## Pitfalls

- Do not write all unfinished tasks as one huge episode; Graphiti extraction may keep the dominant chain and lose side facts.
- Do not sync every few minutes. For the user’s workflow, sync before the morning brief and after manual/bulk task changes; otherwise repeated snapshots can pollute the graph.
- Feishu is still the source of truth for task completion/due dates; Graphiti is context for reasoning and recall.
- If a short Chinese/numeric query returns too little, supplement Graphiti search with direct Kuzu literal fact scanning.
