# TencentDB Memory: SiliconFlow Qwen3 Embedding Migration Notes

Use this when moving the user's TencentDB Agent Memory embedding provider to SiliconFlow Qwen3 embeddings. the user's current cost-optimized target is `Qwen/Qwen3-Embedding-4B` at `2560` dimensions.

## Endpoint Shape

SiliconFlow embeddings are OpenAI-compatible for text embeddings:

```text
base_url=https://api.siliconflow.cn/v1
endpoint=${base_url}/embeddings
model=Qwen/Qwen3-Embedding-4B
```

Request body shape accepted by the plugin's normal `OpenAIEmbeddingService` path:

```json
{
  "input": ["hello"],
  "model": "Qwen/Qwen3-Embedding-4B",
  "dimensions": 2560
}
```

The stock OpenAI-compatible response shape is expected: `data[]` with `index` and `embedding`.

## Dimensions

SiliconFlow docs list `Qwen/Qwen3-Embedding-4B` as supporting custom dimensions:

```text
64, 128, 256, 512, 768, 1024, 1536, 2048, 2560
```

Migration choice:

- Use `2048` only if you intentionally want to minimize schema churn and keep the old vec0 dimension.
- Prefer `2560` when the user explicitly wants a full re-embedding / vector-space migration; this uses the model's full embedding dimension and the local store can rebuild vec0 tables.

Always run a one-text endpoint probe before changing config, and confirm returned vector length matches the chosen `dimensions`.

## Existing Local Store Behavior

The SQLite VectorStore records embedding metadata in `embedding_meta.embedding_provider_info`. On provider/model/dimension drift:

1. `VectorStore.init(providerInfo)` detects the change.
2. It drops `l1_vec` and `l0_vec`.
3. It recreates vec0 tables with the configured dimension.
4. It returns `needsReindex: true`.
5. The caller is expected to invoke `reindexAll(embedFn)` to repopulate vectors from existing `l1_records` and `l0_conversations`.

Important: current code has `reindexAll()` support, but verify the running gateway path actually calls it or run a controlled reindex path. Do not assume merely changing config populated vectors unless logs/counts prove it.

## Safe Migration Procedure

0. Confirm intent and scope in the current user message. Treat “整体重新嵌入 / full re-embedding” as a destructive vector-space migration: it is acceptable, but requires explicit go-ahead before changing config, stopping the sidecar, rebuilding vec tables, or launching a long reindex. Do not let stale context after compaction/model-switch distract into unrelated deliverables.

1. Confirm current state:

```bash
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes config show
curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:8420/health
```

2. Ensure `SILICONFLOW_API_KEY` is available in the environment that runs the gateway. Do not print it.

3. Probe SiliconFlow dimensions:

```bash
python3 - <<'PY'
import os, requests
key = os.environ['SILICONFLOW_API_KEY']
body = {
  'model': 'Qwen/Qwen3-Embedding-4B',
  'input': ['hello'],
  'dimensions': 2560,
}
r = requests.post(
  'https://api.siliconflow.cn/v1/embeddings',
  headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
  json=body,
  timeout=20,
)
print('status', r.status_code)
js = r.json()
emb = js.get('data', [{}])[0].get('embedding')
print('dim', len(emb) if isinstance(emb, list) else None)
PY
```

Expected for the full migration choice: `status 200`, `dim 2560`.

4. Backup the database before changing dimensions:

```bash
cp ~/.memory-tencentdb/memory-tdai/vectors.db \
  ~/.memory-tencentdb/memory-tdai/vectors.db.before-siliconflow-$(date +%Y%m%d-%H%M%S)
```

5. Configure embedding through the Hermes-mode control script:

```bash
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes config embedding \
  --provider openai \
  --api-key "$SILICONFLOW_API_KEY" \
  --base-url "https://api.siliconflow.cn/v1" \
  --model "Qwen/Qwen3-Embedding-4B" \
  --dimensions 2560 \
  --restart
```

6. Verify reindex and recall:

```bash
curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:8420/health
curl --noproxy '*' -sS --max-time 20 \
  -X POST http://127.0.0.1:8420/recall \
  -H 'Content-Type: application/json' \
  -d '{"query":"测试 Qwen3 embedding 是否可用","session_key":"embedding-migration-test"}'
```

Inspect logs for provider/model drift, table rebuild, `reindexAll`, and successful embedding dimensions. Also inspect `embedding_meta` and vec table schema/counts if sqlite-vec is loadable from Node.

## Pitfalls

- Do not use the Volcengine multimodal endpoint adapter for SiliconFlow text embeddings. SiliconFlow Qwen3 uses the normal OpenAI-compatible `/v1/embeddings` path.
- Do not forget `dimensions`; the plugin sends it in the OpenAI-compatible request body and vec0 schema must match it.
- Changing from 2048 to 2560 is a vector-space migration. Backup first and verify all vectors are repopulated.
- Missing `SILICONFLOW_API_KEY` is setup state, not a durable failure. Ask the user to provide/configure it, then rerun the probe.
