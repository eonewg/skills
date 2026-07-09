# TencentDB Memory Embedding Model Selection Notes

## Current known-good configuration

For the user's TencentDB Agent Memory setup, the known-good embedding configuration is:

```text
provider=openai
baseUrl=https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal
model=doubao-embedding-vision-251215
dimensions=2048
```

This uses the Volcengine Ark multimodal embedding endpoint with text payloads shaped as:

```json
{"model":"doubao-embedding-vision-251215","input":[{"type":"text","text":"hello"}]}
```

The setup has been verified to return 2048-dimensional embeddings and to keep TencentDB Memory health at `embeddingService: true`.

## Model/dimension probes from session

The Ark `/models` endpoint listed these embedding-like model IDs:

```text
doubao-embedding-text-240515
doubao-embedding-text-240715
doubao-embedding-large-text-240915
doubao-embedding-vision-241215
doubao-embedding-vision-250328
doubao-embedding-large-text-250515
doubao-embedding-vision-250615
doubao-embedding-vision-251215
```

Practical call results with the current key/region:

- `doubao-embedding-vision-250615`
  - `/embeddings/multimodal`, text object input: works
  - default output: 2048 dims
  - `dimensions=1024`: works
  - `dimensions=2048`: works
  - `dimensions=4096`: HTTP 400
- `doubao-embedding-vision-251215`
  - `/embeddings/multimodal`, text object input: works
  - default output: 2048 dims
  - `dimensions=1024`: works
  - `dimensions=2048`: works
  - `dimensions=4096`: HTTP 400
- `doubao-embedding-text-*` / `doubao-embedding-large-text-*`
  - Listed by `/models`, but direct calls to `/embeddings` and `/embeddings/multimodal` returned HTTP 404 with the current key/endpoint during the probe.
  - Treat these as not directly usable until the exact endpoint/permission/deployment path is verified.

## Recommendation

For this memory workload, prefer `doubao-embedding-vision-251215` at 2048 dimensions unless there is a strong reason to change.

Why:

- The stored memory payloads are mostly text: conversations, preferences, task rules, wiki summaries, and extracted scene/persona records.
- Image inputs are normally captioned/OCR'd first, so TencentDB recall searches text semantics rather than raw pixels.
- 2048 dimensions are sufficient for this scale and cheaper/faster than larger vectors.
- 4096 dimensions are not supported by the currently callable Ark vision embedding models.
- Switching embedding models changes the vector space; plan to rebuild or shadow-test vectors rather than hot-swapping production config.

## Backup candidate: SiliconFlow Qwen3 Embedding

Keep this as a backup candidate, not the production default:

```text
provider=openai
baseUrl=https://api.siliconflow.cn/v1
endpoint=/embeddings
model=Qwen/Qwen3-Embedding-8B
input=["text"]
response=data[0].embedding
dimensions=1024/2048/4096 supported; default observed as 4096
```

Do **not** store the API key in memory or skills. Ask the user for a fresh key or read it from a secret env var when needed.

A shadow benchmark against 100 representative TencentDB memory records and 15 real recall queries found:

```text
ark-vision-251215-2048: Top1 11/15, Top3 12/15, Top5 13/15, MRR 0.788, graded 0.847, wall ~17.0s
qwen3-8b-default/4096: Top1 10/15, Top3 12/15, Top5 13/15, MRR 0.752, graded 0.813, wall ~3.0s
qwen3-8b-2048:        Top1 10/15, Top3 12/15, Top5 12/15, MRR 0.750, graded 0.793, wall ~2.2s
qwen3-8b-4096:        Top1 10/15, Top3 12/15, Top5 13/15, MRR 0.752, graded 0.813, wall ~3.3s
```

Conclusion: keep Ark for recall quality; use Qwen3 as speed-oriented backup or future shadow-index candidate. If switching to Qwen3 4096, recreate the sqlite-vec tables as `float[4096]` and rebuild all vectors. Even Qwen3 2048 requires full re-embedding because the vector space differs.

## Safe migration pattern if changing models

Do not directly switch production embedding config without a quality check. Use this sequence:

1. Keep the known-good `251215 / 2048` setup as the baseline.
2. Create a shadow index/test store or temporary copy of representative memory records.
3. Re-embed the sample with the candidate model/dimension.
4. Run fixed recall queries covering user preferences, task defaults, wiki knowledge, and recent conversation facts.
5. Compare recall quality and latency against the baseline.
6. Only migrate production after the candidate is clearly better; then rebuild all existing vectors so old and new embeddings are not mixed.

## Pitfall

A model appearing in Ark `/models` does not guarantee the current account can call it through the same endpoint used by TencentDB Memory. Always run a minimal embedding probe and verify the actual returned vector length before writing config.