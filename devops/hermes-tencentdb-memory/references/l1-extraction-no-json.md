# L1 Extraction `NO_JSON` Troubleshooting

## Symptom

Gateway stderr shows fresh logs like:

```text
[l1-debug] NO_JSON taskId=l1-extraction
[l1-extractor] No JSON array found in extraction response
```

Hybrid search and embeddings can still be healthy: `/health` reports `vectorStore: true` and `embeddingService: true`, `l1_records` contains rows, and recall/search works. This symptom is specifically about the L1 summarization/extraction LLM returning non-JSON text for some sessions, causing that batch to be dropped.

## Root Cause Pattern

In the TencentDB memory plugin, L1 extraction uses a clean/standalone LLM runner and then `parseExtractionResult` expects a JSON array (`[...]`). A strong prompt alone is not enough if the runner provides tools to the model or constrains the run to a single tool/assistant step.

Problematic pattern in `src/adapters/standalone/llm-runner.ts`:

```ts
const tools = this.enableTools
  ? createSandboxedTools(workspaceDir, this.logger)
  : createReadOnlyTools(workspaceDir, this.logger);

stopWhen: stepCountIs(this.enableTools ? MAX_TOOL_ITERATIONS : 1)
```

For extraction tasks with `enableTools=false`, read-only tools can still prime the model to say things like “I will inspect/analyze...” instead of emitting a raw JSON array. With `stepCountIs(1)`, the run can end before a compliant final JSON answer appears.

## Durable Fix

For non-tool extraction tasks, pass no tools and do not set a one-step tool stop condition. Also use deterministic temperature.

Patch target:

```text
~/.memory-tencentdb/tdai-memory-openclaw-plugin/src/adapters/standalone/llm-runner.ts
```

Desired shape:

```ts
const tools = this.enableTools
  ? createSandboxedTools(workspaceDir, this.logger)
  : undefined;

const result = await generateText({
  model: provider.chat(this.model),
  system: params.systemPrompt,
  prompt: params.prompt,
  ...(tools ? { tools } : {}),
  stopWhen: this.enableTools ? stepCountIs(MAX_TOOL_ITERATIONS) : undefined,
  maxOutputTokens: maxTokens,
  temperature: 0,
  abortSignal: AbortSignal.timeout(timeoutMs),
});
```

The important invariant: `enableTools=false` means no `tools` field and no `stepCountIs(1)`.

## Prompt Hardening

Also harden `src/core/prompts/l1-extraction.ts` so the final instruction is explicit:

```text
Final output MUST be a valid JSON array.
The first character MUST be [ and the last character MUST be ].
Do not include explanations, markdown fences, headings, apologies, or analysis text.
Do not describe tool use.
If there are no memories to extract, return a valid empty-scene JSON array in the required schema.
```

This is secondary to the runner fix: prompt-only fixes are brittle when tools are still exposed.

## Validation

After patching:

```bash
cd ~/.memory-tencentdb/tdai-memory-openclaw-plugin
npm run build
SCRIPT=~/.openclaw/npm/node_modules/@tencentdb-agent-memory/memory-tencentdb/scripts/memory-tencentdb-ctl.sh
bash "$SCRIPT" --hermes restart
curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:8420/health
```

If `npm run build` fails because this installed plugin tree has no tsdown entry (`No input files, try "tsdown <your-file>"`) or dev deps are missing, do not loop on the same build command. The Hermes sidecar runs the gateway with `npm exec -- tsx src/gateway/server.ts`, so validate the touched modules with a direct tsx import instead:

```bash
cd ~/.memory-tencentdb/tdai-memory-openclaw-plugin
npm ci  # only if node_modules/.bin/tsx is missing
npm exec -- tsx -e "Promise.all([import('./src/adapters/standalone/llm-runner.ts'), import('./src/core/prompts/l1-extraction.ts')]).then(()=>console.log('tsx import ok'))"
```

Note: `npm ci` runs the package postinstall hook and may patch the local OpenClaw install; this is expected for this plugin but should be mentioned in the report.

Then inspect fresh logs, not stale historical lines:

```bash
tail -100 ~/.hermes/logs/memory_tencentdb/gateway.stderr.log
tail -100 ~/.hermes/logs/memory_tencentdb/gateway.stdout.log
```

Good state: no new `NO_JSON` lines after new captures/session-end extraction jobs.

## If It Still Fails

If fresh `NO_JSON` continues after the runner fix:

- Add one repair retry in `parseExtractionResult`: when no array is found, re-ask the LLM to convert the previous answer into the exact JSON array schema, with tools disabled.
- Prefer a model with reliable JSON obedience for extraction. Fast/cheap models such as `deepseek-v4-flash` may be acceptable for general chat but can be flaky for schema-only extraction unless runner constraints are clean.
- If the provider supports JSON mode or structured output through the AI SDK, use it for this extraction path only; keep generic chat/tool runs unchanged.
