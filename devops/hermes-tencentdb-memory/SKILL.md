---
name: hermes-tencentdb-memory
version: 1.1.0
description: Configure, migrate, re-embed, and troubleshoot Hermes TencentDB Agent Memory, including SiliconFlow Qwen3 embeddings, SenseNova extraction, and legacy Volcengine Ark compatibility.
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, memory, tencentdb, embedding, siliconflow, qwen3, volcengine]
    related_skills: [hermes-agent]
---

# Hermes TencentDB Memory

## Overview

TencentDB Agent Memory can run as a Hermes memory provider via a sidecar gateway on `127.0.0.1:8420`. Use this skill to configure the sidecar, switch embedding providers, rebuild vector tables, migrate existing memory, and debug recall/extraction failures.

For the user's current setup, LLM extraction uses SenseNova's OpenAI-compatible chat endpoint. The user-facing endpoint may be given as `https://token.sensenova.cn/v1/chat/completions`, but the TencentDB sidecar uses AI SDK `createOpenAI({ baseURL })`, so configure the base URL without the final `/chat/completions` suffix:

```text
base_url=https://token.sensenova.cn/v1
model=deepseek-v4-flash
```

Current embedding uses SiliconFlow's OpenAI-compatible endpoint:

```text
baseUrl=https://api.siliconflow.cn/v1
model=Qwen/Qwen3-Embedding-4B
dimensions=2560
```

Legacy Volcengine Ark `doubao-embedding-vision-*` multimodal embeddings are still documented below as a compatibility/migration path. The key Ark issue: the plugin's stock `OpenAIEmbeddingService` sends `input: string[]` to `${baseUrl}/embeddings` and expects `data: []`, while Ark multimodal expects `input: [{type:"text", text:"..."}]` at `/embeddings/multimodal` and returns `data.embedding`.

## When to Use

Use this when:

- Hermes `hermes memory status` shows provider `memory_tencentdb` but `embeddingService: false`.
- User wants to configure or migrate TencentDB Agent Memory embeddings, especially SiliconFlow Qwen3 or legacy Volcengine Ark / 豆包.
- The embedding model or dimensions changed and existing `l0_vec` / `l1_vec` tables need a full re-embed.
- `doubao-embedding-vision-*` returns 400 for OpenAI-style `input: ["text"]`.
- A package upgrade overwrote the local patch in `~/.memory-tencentdb/tdai-memory-openclaw-plugin/src/core/store/embedding.ts`.

Do not use this for generic Hermes memory providers like Honcho/Mem0, unless the specific issue is the TencentDB sidecar's embedding route.

## Key Paths

```text
Hermes config:        ~/.hermes/config.yaml
Hermes env:           ~/.hermes/.env
TDAI root:            ~/.memory-tencentdb/
TDAI install dir:     ~/.memory-tencentdb/tdai-memory-openclaw-plugin
TDAI data dir:        ~/.memory-tencentdb/memory-tdai
Gateway config:       ~/.memory-tencentdb/memory-tdai/tdai-gateway.json
Hermes-mode env file: ~/.hermes/env.d/memory-tencentdb-llm.sh
Gateway logs:         ~/.hermes/logs/memory_tencentdb/
Ctl script:           ~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
Patch target:         ~/.memory-tencentdb/tdai-memory-openclaw-plugin/src/core/store/embedding.ts
```

## Check Current Status

```bash
hermes memory status
curl -sS --max-time 5 http://127.0.0.1:8420/health
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes status
bash "$SCRIPT" --hermes config show
```

Expected after success:

```json
{"status":"ok","stores":{"vectorStore":true,"embeddingService":true}}
```

## Configure LLM Extraction

Use the ctl script in Hermes mode so it writes both `tdai-gateway.json` and `~/.hermes/env.d/memory-tencentdb-llm.sh`.

```bash
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes config llm \
  --api-key "$SENSENOVA_API_KEY" \
  --base-url "https://token.sensenova.cn/v1" \
  --model "deepseek-v4-flash" \
  --restart
```

Also ensure Hermes provider is active:

```bash
hermes config set memory.provider memory_tencentdb
hermes memory status
```

## Verify Ark Multimodal Embedding Format

Before patching, test the endpoint shape. Do not print secrets.

```bash
python3 - <<'PY'
import os, requests
key = os.environ['ARK_API_KEY']
url = 'https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key}
body = {'model': 'doubao-embedding-vision-251215', 'input': [{'type': 'text', 'text': 'hello'}]}
r = requests.post(url, headers=headers, json=body, timeout=15)
print('status', r.status_code)
js = r.json()
emb = js.get('data', {}).get('embedding')
print('dim', len(emb) if isinstance(emb, list) else None)
PY
```

Expected: `status 200`, `dim 2048`.

OpenAI-style `input: ["hello"]` to `/embeddings/multimodal` is expected to fail with HTTP 400. That confirms this is a format mismatch, not a bad API key.

## Patch TencentDB Plugin for Ark Multimodal Embedding

Patch `src/core/store/embedding.ts` in the local plugin install. The essence:

- Add a `VolcengineMultimodalEmbeddingResponse` type with `data.embedding`.
- In `OpenAIEmbeddingService._callApi`, detect `baseUrl.endsWith('/embeddings/multimodal') || model.includes('embedding-vision')`.
- For that path, call the exact `baseUrl` if it already ends in `/embeddings/multimodal`, otherwise append `/embeddings/multimodal`.
- Send one request per text with body:

```json
{"model":"doubao-embedding-vision-251215","input":[{"type":"text","text":"..."}]}
```

- Parse `json.data.embedding` and pass through `sanitizeAndNormalize`.
- Leave the normal OpenAI path untouched for other providers.

Minimal behavior to preserve:

```ts
const useVolcengineMultimodal =
  this.baseUrl.endsWith("/embeddings/multimodal") || this.model.includes("embedding-vision");

if (useVolcengineMultimodal) {
  const fetchUrl = this.baseUrl.endsWith("/embeddings/multimodal")
    ? this.baseUrl
    : `${this.baseUrl}/embeddings/multimodal`;
  const results: Float32Array[] = [];
  for (const text of texts) {
    const json = (await callOnce(fetchUrl, {
      model: this.model,
      input: [{ type: "text", text }],
    })) as VolcengineMultimodalEmbeddingResponse;
    if (!json.data || !Array.isArray(json.data.embedding)) {
      throw new Error("Embedding API returned unexpected Volcengine multimodal format: missing 'data.embedding'");
    }
    results.push(sanitizeAndNormalize(json.data.embedding));
  }
  return results;
}
```

After editing, restart the gateway.

## Configure Embedding

```bash
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes config embedding \
  --provider openai \
  --api-key "$ARK_API_KEY" \
  --base-url "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal" \
  --model "doubao-embedding-vision-251215" \
  --dimensions 2048 \
  --restart
```

Why `--provider openai` even though it is not OpenAI-compatible: the TencentDB plugin treats any non-local remote provider as the `OpenAIEmbeddingService`; the local patch adds the Volcengine multimodal branch inside that service.

### Embedding Model Selection

For the user's memory workload, keep `doubao-embedding-vision-251215` at `2048` dimensions unless there is a clear measured reason to change. The current memory records are primarily text; images/screenshots are normally OCR'd or captioned before memory capture, so a plain text embedding would be sufficient in principle. The current vision embedding model is acceptable because it is already verified with text input, but switching models/dimensions should be treated as a vector-space migration, not a harmless config tweak.

Before changing models, run a minimal endpoint probe and confirm the returned vector length. In-session probes found `doubao-embedding-vision-250615` and `doubao-embedding-vision-251215` callable at `1024`/`2048`, but not `4096`; Ark-listed `doubao-embedding-text-*` and `doubao-embedding-large-text-*` returned 404 through the tested endpoints/key. See `references/embedding-model-selection.md` for the probe details, recommendation, and safe shadow-index migration pattern.

the user's current default is SiliconFlow `Qwen/Qwen3-Embedding-4B` at `2560` dimensions. Use the normal OpenAI-compatible path (`https://api.siliconflow.cn/v1`, model `Qwen/Qwen3-Embedding-4B`) rather than the Ark multimodal adapter. Treat any provider/model/dimension change as a vector-space migration: the SQLite VectorStore can detect drift, drop and recreate `l0_vec`/`l1_vec`, and expose `needsReindex`, but verify that vectors are actually repopulated. In the 2026-06-23 migration, the gateway recreated 2560D tables but did not auto-repopulate vectors; a manual Node `node:sqlite` + `sqlite-vec` batch reindex was required. See `references/siliconflow-qwen3-embedding-migration.md` for the exact safe migration and verification flow.

## Migrate Existing Hermes Built-in Memory

After TencentDB Memory is healthy, migrate critical stable facts from Hermes built-in `~/.hermes/memories/MEMORY.md` and `~/.hermes/memories/USER.md` when the goal is replacing or augmenting the old memory layer. First try the normal `/capture` + `/session/end` pipeline so L0/L1/L2 behavior is exercised. If LLM extraction under-extracts curated profile facts, import distilled `persona` / `instruction` records directly into `l1_records` and `l1_fts` with deterministic IDs and keyword-enriched FTS content.

See `references/migrating-hermes-builtin-memory.md` for the tested migration script pattern, direct L1 fallback schema, proxy-bypass notes, and representative verification searches.

## Troubleshoot L1 Extraction `NO_JSON`

If embeddings and hybrid search are healthy but gateway logs show fresh `NO_JSON` / `No JSON array found in extraction response`, treat it as an L1 extraction-runner issue rather than an embedding issue. The durable fix is to ensure extraction runs with `enableTools=false` pass **no tools**, do **not** use `stepCountIs(1)`, and set `temperature: 0`; then harden the L1 prompt to require the first character `[` and last character `]`.

See `references/l1-extraction-no-json.md` for the root cause pattern, patch shape, validation steps, and fallback retry/model options.

## Switch Embedding to SiliconFlow Qwen3

Use this when migrating TencentDB Memory to SiliconFlow Qwen3 embeddings. SiliconFlow text embeddings are OpenAI-compatible and work through the stock `OpenAIEmbeddingService` path.

**First-response guard:** if the user says they “plan to” or asks whether they “can” do a full re-embedding, answer the current request directly before touching any stale prior task context. State: “可以，按全量迁移处理；先备份、探测 Qwen3 维度、切配置、重建向量、验 counts/recall。” Do not perform destructive steps such as stopping the gateway, changing embedding config, dropping/rebuilding vec tables, or running a long batch reindex until the user explicitly confirms to proceed.

配置目标：

```text
baseUrl=https://api.siliconflow.cn/v1
model=Qwen/Qwen3-Embedding-4B
dimensions=2560
```

Qwen3-Embedding-4B supports selectable dimensions up to `2560`; the user chose `2560` as the cost/quality compromise. If the user later switches to 8B, `4096` is available but costs more.

Probe before switching, without printing secrets:

```bash
python3 - <<'PY'
import json, os, urllib.request
key = os.environ['SILICONFLOW_API_KEY']
body = {
  'model': 'Qwen/Qwen3-Embedding-4B',
  'input': ['hello', '考研任务记忆检索测试'],
  'dimensions': 2560,
  'encoding_format': 'float',
}
req = urllib.request.Request(
  'https://api.siliconflow.cn/v1/embeddings',
  data=json.dumps(body).encode(),
  headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
)
with urllib.request.urlopen(req, timeout=30) as r:
  js = json.loads(r.read().decode())
  print('status', r.status)
  print('dims', [len(x['embedding']) for x in js['data']])
PY
```

Configure with the TencentDB ctl script in Hermes mode:

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

Important migration behavior observed in this setup: the plugin detects provider/model/dimension drift, drops `l0_vec` / `l1_vec`, recreates them with `float[2560]`, and updates `embedding_meta`, but the gateway may not automatically call `reindexAll()`. Verify row counts immediately:

```bash
python3 - <<'PY'
import sqlite3, re
p='~/.memory-tencentdb/memory-tdai/vectors.db'
con=sqlite3.connect(p); cur=con.cursor()
print(cur.execute("select value from embedding_meta where key='embedding_provider_info'").fetchone()[0])
for name in ['l1_vec','l0_vec']:
  sql=cur.execute('select sql from sqlite_master where name=?',(name,)).fetchone()[0]
  print(name, re.search(r'float\\[(\\d+)\\]', sql).group(1))
for t in ['l1_records','l1_vec_rowids','l0_conversations','l0_vec_rowids']:
  print(t, cur.execute(f'select count(*) from {t}').fetchone()[0])
PY
```

If vec row counts are zero or lower than metadata row counts, stop the sidecar and run a manual batch reindex. Use batches of 32 for SiliconFlow. Load `sqlite-vec` through Node's `node:sqlite` with `new DatabaseSync(dbPath, { allowExtension: true })`; otherwise `enableLoadExtension(true)` fails with `ERR_INVALID_STATE`. Insert normalized `Float32Array` buffers into `l1_vec` and `l0_vec`, then restart the gateway. A reusable script is packaged at `scripts/reindex-siliconflow-sqlite-vec.mjs`; the verified 2026-06-23 4B/2560D migration details are in `references/qwen3-4b-2560-migration-2026-06-23.md`.

After migration, expected verification:

```text
embedding_meta: {"provider":"openai","model":"Qwen/Qwen3-Embedding-4B","dimensions":2560}
l1_vec: float[2560]
l0_vec: float[2560]
l1_vec_rowids == l1_records
l0_vec_rowids == l0_conversations
recall logs: [hybrid-embedding] Embedding OK, dims=2560
```

## Verify End-to-End

```bash
curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:8420/health
```

Expected:

```json
"embeddingService": true
```

Then trigger recall to force a query embedding:

```bash
curl -sS --max-time 20 \
  -X POST http://127.0.0.1:8420/recall \
  -H 'Content-Type: application/json' \
  -d '{"query":"测试 embedding 是否可用 hello","session_key":"embedding-test"}'
```

Check logs:

```bash
tail -80 ~/.hermes/logs/memory_tencentdb/gateway.stdout.log
tail -80 ~/.hermes/logs/memory_tencentdb/gateway.stderr.log
```

Good signs for the user's current SiliconFlow setup:

```text
[memory-tdai][embedding] Using remote embedding (provider=openai, model=Qwen/Qwen3-Embedding-4B)
Stores initialized: backend=sqlite, embedding=openai
Search strategy: hybrid (configured: hybrid)
[hybrid-embedding] Embedding OK, dims=2560
embeddingService=available
```

For legacy Volcengine Ark setups, `doubao-embedding-vision-251215` with `dims=2048` is still acceptable when explicitly configured.

Bad signs:

```text
Strategy "hybrid" requested but EmbeddingService not available, falling back to keyword
Embedding API returned unexpected format: missing 'data' array
HTTP 400 ... could not parse the JSON body
```

The first means embedding is not configured or gateway was not restarted. The latter two mean the Volcengine multimodal patch is missing or broken.

## Common Pitfalls

1. **Using base URL without the multimodal suffix.** Stock OpenAI-style code appends `/embeddings`; for Ark vision embeddings use `https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal` with the patch.

2. **Expecting OpenAI text array format to work.** `input: ["hello"]` fails on the multimodal endpoint. Use `[{type:"text",text:"hello"}]`.

3. **Misreading the response.** Ark multimodal returns `data.embedding`, not `data[0].embedding`.

4. **Forgetting Hermes mode.** `memory-tencentdb-ctl config llm` in standalone mode will not write `~/.hermes/env.d/memory-tencentdb-llm.sh`. Use `--hermes`.

5. **Patch can be overwritten by upgrades.** If TencentDB-Agent-Memory is upgraded or reinstalled, re-check `embedding.ts` and reapply the patch if `embeddingService` drops back to false or recall logs show OpenAI-format failures.

6. **Stale logs contain earlier failures.** Look at timestamps or current PID. Historical errors like `Cannot connect to api.openai.com` may be from before LLM env was written.

7. **TypeScript compiler may be absent.** `npm exec -- tsc` can print “This is not the tsc command you are looking for” if `typescript` is not installed in the plugin tree. Validate via gateway restart + health + recall logs instead.

8. **Local gateway requests may be hijacked by proxy env.** If Python `requests` or curl goes to a local proxy such as `127.0.0.1:7897`, use `curl --noproxy '*' ...` or disable proxies in `requests`. This matters for `/health`, `/capture`, `/session/end`, and verification probes.

9. **LLM extraction may under-extract curated migrations.** When migrating dense built-in profile/preferences, a normal `/capture` pass may only store a subset. Verify representative facts; for critical stable rules, use the direct L1 import fallback in `references/migrating-hermes-builtin-memory.md`.

## Verification Checklist

- [ ] `hermes memory status` shows provider `memory_tencentdb`.
- [ ] `memory-tencentdb-ctl --hermes status` shows gateway `RUNNING` and `health OK`.
- [ ] `tdai-gateway.json` has `llm.baseUrl`, `llm.model`, and `memory.embedding` configured.
- [ ] `~/.hermes/env.d/memory-tencentdb-llm.sh` exists with `MEMORY_TENCENTDB_LLM_*` aliases.
- [ ] `/health` reports `vectorStore: true` and `embeddingService: true`.
- [ ] Recall logs show `Search strategy: hybrid` and `Embedding OK, dims=2560` for the user's current Qwen3-Embedding-4B setup; legacy Ark vision setups may show `dims=2048`.
- [ ] No fresh stderr contains `missing 'data' array`, HTTP 400 parse errors, or fallback to keyword.
