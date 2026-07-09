---
name: model-routing-and-provider-config
description: Unified guidance for configuring multi-model agents, provider fallback chains, and task-based model routing. Use when setting up provider selection, fallback behavior, workload-specific model assignment, or router policies across AI providers.
---

# Model Routing and Provider Config

## Overview
This umbrella skill consolidates model-routing and multi-provider configuration skills into one class-level entry.

## Core workflow
1. Identify the routing problem: fallback, specialization, cost control, provider diversity, adding a reusable named endpoint, or configuring a tool backend such as image generation.
2. Separate default-chat model choices from auxiliary-task routing and from tool-backend routing (`image_gen.provider`, `video_gen.provider`, etc.).
3. For Hermes named OpenAI-compatible endpoints, prefer `providers.<name>` + `key_env` in `~/.hermes/config.yaml` and keep the secret in `~/.hermes/.env`; do not switch the active default model unless the user explicitly asks.
4. For non-chat tool backends that are not built in, add or enable the appropriate backend plugin and configure that tool's provider key (for image generation: `~/.hermes/plugins/image_gen/<name>` + `image_gen.provider`).
5. Encode explicit policies for failures, retries, and model class selection.
6. Test each route with representative workloads or a minimal live probe.

## Consolidated subsections
### Fallback and resilience chains
### Workload-specific model assignment
### Provider mixing and policy routing

### Same-provider credential pools
Use Hermes credential pools when the user wants multiple credentials for the same provider before introducing cross-provider fallback. For OpenAI Codex, multiple ChatGPT/OpenAI OAuth accounts can be added under `openai-codex`; set `credential_pool_strategies.openai-codex` to `fill_first` when the goal is “use one account until quota/usage-limit exhaustion, then switch to the next.” If the user wants fast manual switching between two Codex accounts, reorder the pool so the desired credential has priority 0 (the current selected entry); the helper in `scripts/codex-use.py` implements `codex-use me/friend/list` for this pattern. See `references/hermes-codex-credential-pools.md` for the full device-code flow, friend-account handoff cautions, quick switching, and retry/removal commands.

## Absorbed specialized skills
- `hermes-multi-model-config` — concrete multi-provider/fallback configuration.
- `model-router` — task-aware routing policy across models/providers.

## Linked references
- `hermes-auxiliary-auto-pinning.md` — Hermes auxiliary-task `auto` pinning workflow: audit remaining auto routes, back up config, pin low-risk helpers, and verify with live `agent.auxiliary_client.call_llm` probes.
- `openclaw-provider-config.md` — OpenClaw provider/model config in `openclaw.json`: structure, baseUrl convention, Sensenova setup, fallback/alias cleanup.
- `hermes-named-provider-config.md` — Hermes `providers.<name>` + `key_env` pattern for adding OpenAI-compatible named endpoints without switching the active default model.
- `agnes-ai-provider.md` — Agnes AI `agnes-2.0-flash` endpoint, known-good Hermes config, live probe, and optional thinking-mode notes.
- `hermes-model-switch-shortcuts.md` — Hermes `model_aliases` + `quick_commands` pattern for short `/a` and `/g`-style session model switches.
- `hermes-custom-provider-subcommand-shortcuts.md` — grouped custom-provider shortcuts such as `/provider small` and `/provider large`, using `quick_commands.<name>.target: /model` plus `model_aliases` that point to `custom:<name>`.
- `openai-compatible-proxy-group-probe.md` — diagnosing OpenAI-compatible proxy keys whose `/v1/models` list or live chat probe shows only some upstream groups/models are enabled.
- `ant-ling-provider.md` — Ant Ling / BaLing OpenAI-compatible provider setup, Ling/Ring/Ming model routing notes, context windows, and Ming API-list mismatch pitfall.
- `gemini-free-tier-routing.md` — Gemini Developer API free-tier setup, privacy caveats, auxiliary-task routing, and Gemini-backed subagent/delegation configuration.
- `hermes-codex-credential-pools.md` — OpenAI Codex OAuth credential pools: adding multiple ChatGPT accounts, friend/teammate device-code handoff, fill-first rotation, quick manual account switching, removal/reset, and transient polling failure retry pattern.
- `hermes-image-gen-provider-plugins.md` — Hermes image generation backend plugins, including the Ark Seedream 5.0 Lite pattern, plugin enabling pitfall, config shape, and verification probe.
- `scripts/codex-use.py` — helper script for making `codex-use me/friend/list` switch the selected OpenAI Codex OAuth credential by moving it to priority 0 in `~/.hermes/auth.json`.

## Hermes quick model-switch shortcuts
When the user wants a low-cost/default chat model plus a stronger model for complex work, prefer explicit short aliases over hand-typing long `/model ... --provider ...` commands. Define `model_aliases` for reusable exact model/provider pairs and, if they want true one-token slash commands, add `quick_commands` with `type: alias` pointing at `/model <alias>`. Explain that plain `/model <alias>` is session-scoped; use `--global` only when the user explicitly wants to change the persistent default.

For built-in providers and one-off exact model shortcuts, a `model_aliases` entry is optional: `quick_commands.<name>.target` can point directly at the full switch command, e.g. `hermes config set quick_commands.stepfun.type alias` and `hermes config set quick_commands.stepfun.target '/model step-3.7-flash --provider stepfun'`. This is the right pattern when the user explicitly asks for `/stepfun` to switch to StepFun `step-3.7-flash` and the provider already resolves through Hermes' provider registry / env vars.

For OpenRouter-hosted models that already use the existing `OPENROUTER_API_KEY`, do not create a custom provider block. Add aliases directly with `hermes config set`, e.g. `hermes config set model_aliases.n.model 'vendor/model:free'`, `hermes config set model_aliases.n.provider openrouter`, plus optional `quick_commands.n.type alias` and `quick_commands.n.target '/model n'`. Verify with `hermes config check` and a minimal live probe such as `hermes chat --provider openrouter --model 'vendor/model:free' -q 'Reply with exactly: ok' -Q --toolsets safe`. Preserve the current default model unless the user explicitly asks to switch.

For grouped custom-provider shortcuts such as `/tudou fable` and `/tudou opus`, use a forwarding quick command: `quick_commands.<provider>.target: /model` (no fixed alias after `/model`). Then define each subcommand in `model_aliases` with `provider: custom:<provider>` and the exact model ID. If the custom endpoint exposes a known finite model list, add `custom_providers.<provider>.models` entries too so picker/catalog views can see them. See `references/hermes-custom-provider-subcommand-shortcuts.md` for the full pattern and resolver probe.

## Common pitfalls
- Routing everything through a single heavyweight default.
- When a user asks to add a provider but explicitly wants to decide correct task placement later, only add the provider/aliases first; do not preemptively assign auxiliary routes, fallback chains, or smart-routing policy. Present a workload-placement plan and wait for confirmation.
- Setting fallbacks without testing credentials and quotas.
- Blending chat and background-task policies.
- Treating “provider resolves in Hermes” as a full live-provider test; also probe the endpoint when credentials/compatibility are in doubt.
- Using `model_routing.quick_switch` in config — this key does NOT exist. The correct feature is `quick_commands` with `type: alias` pointing to `/model <alias>`.
- For `model_aliases` entries that target a `custom_providers` entry, use `provider: custom:<name>` (e.g. `provider: custom:longcat`). The alias validator compares against the `custom:` slug; a bare custom-provider name can fail model-switch validation even if runtime provider resolution works elsewhere.
- Changing the default model/provider when the requested scope was only to add a new reusable provider configuration.
- Treating a successful config parse as proof that a proxy key can call the requested model. For OpenAI-compatible proxy panels, run both `/v1/models` and a tiny `/chat/completions` request; if `/models` only shows other groups or the chat probe returns `model_not_found` / “switch to <group>”, the fix is upstream key/group/model access, not Hermes config. See `references/openai-compatible-proxy-group-probe.md`.
- When removing a provider, clean both config and credential surfaces: delete the provider block from `providers:` or `custom_providers:`, remove matching env-key lines from `~/.hermes/.env`, search for provider/name/base-url leftovers, then run `hermes config check`.
- For provider docs that publish the full method endpoint (`.../v1/chat/completions`), store only the base URL root (`.../v1`) in Hermes config; otherwise clients may double-append method paths.
- For high-context models (e.g. deepseek-v4-flash via sensenova: 1M context), set `context_length: 1048576` on the custom provider entry. This lets Hermes make accurate compression/context-management decisions. Add it as a field alongside `base_url`, `key_env`, `api_mode`:
  ```yaml
  custom_providers:
  - name: sensenova
    base_url: https://token.sensenova.cn/v1
    key_env: SENSENOVA_API_KEY
    api_mode: chat_completions
    model: deepseek-v4-flash
    context_length: 1048576    # ← add this for non-default context windows
  ```
  Only set this when the model's actual context window differs from the default (typically 128K). Verify after adding with `grep -A 6 'name: <provider>' ~/.hermes/config.yaml`.
- Hermes image generation uses backend plugins, not the chat-provider registry. When adding a provider such as Ark Seedream, create/enable `~/.hermes/plugins/image_gen/<name>/`, set `image_gen.provider`, and run a real generation probe; a successful chat-provider probe does not prove `image_generate` will route there. User-local plugins require `plugins.enabled` to be a YAML list, not a JSON-looking string. See `references/hermes-image-gen-provider-plugins.md`.
- Volcengine Ark Responses API (`https://ark.cn-beijing.volces.com/api/v3`) can be configured as a named custom provider with `api_mode: codex_responses` and `key_env: ARK_API_KEY`. Ark rejects Hermes' default Responses reasoning payload `reasoning.summary` with `HTTP 400: unknown field "summary"`; add `extra_body: {reasoning: {effort: high}}` so the SDK's `extra_body` overrides the body-level reasoning object. If the provider entry has `default_model`, Hermes' compatibility view treats that as a model filter for `extra_body`; add a second legacy `custom_providers` entry with the same base_url and no model/default_model to apply the override to all Ark models. Verify with `hermes chat --provider ark --model <model> -q '只回复 ok' -Q --toolsets safe` and, for vision, `--image <local-file>`. Cost/quota note from the user: Volcengine Ark allowance refreshes daily with separate per-model pools: `doubao-seed-2-1-pro-260628` ~2,500,000 tokens/day, `doubao-seed-2-1-turbo-260628` ~2,500,000 tokens/day, `doubao-seed-evolving` ~5,500,000 tokens/day, and `glm-5-2-260617` ~2,500,000 tokens/day. Ant Ling/BaLing allowance also refreshes daily but is ~500,000 tokens/day shared across all Ling/Ring/Ming/BaLing models combined. Do not treat these as context-window lengths. Usage visibility: Ark has official management APIs (`GetInferenceUsage` for inference usage and Agent/Coding Plan `GetUsageDetails` for package usage) requiring Volcengine OpenAPI HMAC AK/SK, not the Ark Bearer `ARK_API_KEY`; if no `VOLCENGINE_ACCESS_KEY_ID`/secret is configured, fall back to local Hermes session accounting. Ant Ling public docs mention usage/bills in the Billing Center and free quota reset at 02:00, but no public usage-query API found; local Hermes tracking is the practical in-chat counter. Local helper: `~/.hermes/scripts/llm_daily_usage.py --details` aggregates today's Ark per-model and Ant shared usage from `~/.hermes/state.db` and is a lower bound (only calls through this Hermes profile). Auxiliary routing pitfall: for Ark auxiliary tasks use the named provider (`provider: ark`, `model: doubao-...`/`glm-...`) rather than raw `provider: custom` + `base_url`; a direct custom auxiliary probe can still emit `reasoning.summary` and fail with Ark's `unknown field "summary"`, while named `ark` resolved successfully in `agent.auxiliary_client.call_llm` for `web_extract`, `title_generation`, `skills_hub`, `compression`, `approval`, `mcp`, and `profile_describer`. Full Hermes agent/tool-calling probe: `glm-5-2-260617` successfully called `terminal`; `doubao-seed-evolving` failed a terminal tool-call probe with missing `input.content`, so prefer GLM/pro for cron jobs or full agent sessions that need tools, and use evolving for auxiliary non-tool LLM tasks such as web extraction summaries, title generation, and profile/skill description.

## Verification checklist
- [ ] Routing policy documented.
- [ ] Fallback path tested.
- [ ] Task classes mapped to intended models/providers.
- [ ] Secrets stored in env vars and not printed in summaries/tool output.
- [ ] Live probe run for any newly credentialed provider before assigning production traffic.

## Subagents / delegation routing
- Hermes subagents are temporary isolated workers spawned for short bounded subtasks; they are useful for parallel research, code/file inspection, and independent analysis, then return a summary to the parent.
- Keep delegation routing separate from the main chat model and auxiliary models: changing `delegation.provider/model` should not imply changing `model.provider/default`, fallback chains, or `auxiliary.*` routes.
- For low-cost Gemini-backed subagents, use `delegation.provider: gemini` plus `delegation.model: gemini-3.1-flash-lite`; upgrade to `gemini-3.5-flash` only if tool-use quality is insufficient. See `references/gemini-free-tier-routing.md`.
