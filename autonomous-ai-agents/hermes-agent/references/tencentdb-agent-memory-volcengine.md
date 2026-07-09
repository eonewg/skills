# TencentDB Agent Memory + Volcengine Ark notes

Session-derived notes for configuring Hermes `memory_tencentdb` with Volcengine Ark LLM extraction and Doubao multimodal embeddings.

## LLM extraction config

Hermes reads `memory.memory_tencentdb.llm_base_url` / `llm_model` from `~/.hermes/config.yaml` and the API key from env / `~/.hermes/.env`:

```env
MEMORY_TENCENTDB_LLM_API_KEY=ark-...
MEMORY_TENCENTDB_LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MEMORY_TENCENTDB_LLM_MODEL=doubao-seed-2-0-pro-260215
```

For the sidecar in Hermes mode, prefer the package control script so it also writes `$HERMES_HOME/env.d/memory-tencentdb-llm.sh` and `$TDAI_DATA_DIR/tdai-gateway.json`:

```bash
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes config llm \
  --api-key "$ARK_API_KEY" \
  --base-url 'https://ark.cn-beijing.volces.com/api/v3' \
  --model 'doubao-seed-2-0-pro-260215' \
  --restart
```

Verify:

```bash
hermes memory status
bash "$SCRIPT" --hermes status
curl -sS --max-time 5 http://127.0.0.1:8420/health
```

## Doubao embedding-vision is not OpenAI-compatible

`doubao-embedding-vision-251215` uses the Ark multimodal embeddings endpoint, not standard `/embeddings`.

Observed behavior:

- `POST /api/v3/embeddings/multimodal` with OpenAI-style `input: ["hello"]` returns HTTP 400.
- The working text format is:

```json
{
  "model": "doubao-embedding-vision-251215",
  "input": [{ "type": "text", "text": "hello" }]
}
```

Response shape is also different from OpenAI embeddings: it returns `data.embedding` as an object field, not `data[]`.

## Local patch used

The installed plugin path was:

```text
~/.memory-tencentdb/tdai-memory-openclaw-plugin/src/core/store/embedding.ts
```

Patch behavior added:

- Detect `baseUrl.endsWith('/embeddings/multimodal')` or model containing `embedding-vision`.
- Route to `/embeddings/multimodal` without appending `/embeddings` again.
- Convert each text to `[{ type: 'text', text }]`.
- Parse `json.data.embedding` and normalize as usual.

This patch may be overwritten by package upgrades; re-check after upgrading TencentDB-Agent-Memory.

Configure embedding after patch:

```bash
bash "$SCRIPT" --hermes config embedding \
  --provider openai \
  --api-key "$ARK_API_KEY" \
  --base-url 'https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal' \
  --model 'doubao-embedding-vision-251215' \
  --dimensions 2048 \
  --restart
```

Expected health:

```json
{"stores":{"vectorStore":true,"embeddingService":true}}
```

Expected logs during recall:

```text
embeddingService=available
Search strategy: hybrid
Embedding OK, dims=2048
```

## Pitfalls

- `hermes gateway restart` can interrupt the current gateway conversation; after interruption, verify service state with `systemctl --user is-active hermes-gateway` and `hermes memory status`.
- `memory-tencentdb-ctl --hermes config show` may reveal whether `tdai-gateway.json` exists; `hermes memory status` alone can look good while the sidecar JSON is still missing.
- If `embeddingService=false`, hybrid recall silently falls back to keyword/BM25; check stdout logs for `EmbeddingService not available`.
- Avoid printing API keys in final replies or logs. Use script output that redacts secrets.
