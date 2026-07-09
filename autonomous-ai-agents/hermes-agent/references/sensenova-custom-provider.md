# SenseNova custom provider for Hermes

Use this when the user wants to add SenseNova / TokenHub as a selectable Hermes model provider while keeping the existing default model/provider unchanged.

## Endpoint shape

User-facing docs may provide the full chat completions URL:

```text
https://token.sensenova.cn/v1/chat/completions
```

Hermes custom providers should store the OpenAI-compatible **base URL** instead:

```text
https://token.sensenova.cn/v1
```

Hermes/OpenAI clients append `/chat/completions` automatically when `api_mode: chat_completions` is used.

## Recommended config shape

Store the secret in `~/.hermes/.env` and reference it from config. Do not store or repeat the actual API key in skills, memory, or final summaries.

```env
SENSENOVA_API_KEY=<secret>
```

```yaml
custom_providers:
  - name: sensenova
    base_url: https://token.sensenova.cn/v1
    key_env: SENSENOVA_API_KEY
    api_mode: chat_completions
    model: deepseek-v4-flash
```

This creates a named provider addressable as `sensenova` or `custom:sensenova` without changing:

```yaml
model:
  default: gpt-5.5
  provider: openai-codex
```

## Safe update workflow

1. Backup `~/.hermes/config.yaml` before editing.
2. Upsert `SENSENOVA_API_KEY` in `~/.hermes/.env` without printing the value.
3. Upsert the `custom_providers` entry above. Preserve the existing `model.default` and `model.provider` unless the user explicitly asks to switch defaults.
4. Run `hermes config check`.
5. Verify the raw endpoint with a tiny `只回复 OK` request against `https://token.sensenova.cn/v1/chat/completions`.
6. Verify Hermes runtime resolution from the repo/workdir:

```python
from hermes_cli.runtime_provider import resolve_runtime_provider
r = resolve_runtime_provider(requested="sensenova")
print(r.get("provider"))       # custom
print(r.get("source"))         # custom_provider:sensenova
print(r.get("base_url"))       # https://token.sensenova.cn/v1
print(r.get("model"))          # deepseek-v4-flash
print(r.get("api_mode"))       # chat_completions
```

## Pitfalls

- Do not put `/chat/completions` in `custom_providers[].base_url`; it will double-append or route incorrectly in OpenAI-compatible clients.
- Do not set `model.provider: sensenova` or `model.default: deepseek-v4-flash` unless the user wants SenseNova to become the default model. Adding a provider and switching defaults are separate operations.
- Do not print the API key during verification. Mask outputs and avoid storing the secret inline in skill or memory content.
- A running gateway may need restart before menus or runtime sessions pick up the new provider, but avoid restarting mid-conversation unless the user explicitly wants immediate gateway refresh.
- GLM-family SenseNova models may spend the first completion tokens on `reasoning_content`. Tiny probes with `max_tokens`/`max_completion_tokens` around 8-64 can return HTTP 200 with empty `message.content` and `finish_reason: length`; use a larger probe budget (e.g. 512) before concluding the model failed.

### model_aliases provider field needs `custom:` prefix

When a `model_aliases` entry points at a `custom_providers` entry, the `provider` field **must** use the `custom:<name>` form (e.g. `custom:longcat`), not just the bare name. The validation path in `model_switch.py` builds `entry_slug = f"custom:{entry_name}"` and compares it against `target_provider`. If the alias uses the bare name, validation fails with "Model was not found in this provider's model listing."

```yaml
model_aliases:
  longcat:
    model: LongCat-2.0-Preview
    provider: custom:longcat   # ✅ correct — matches entry_slug
    # provider: longcat        # ❌ wrong — validation mismatch
```

### Always set context_length on custom_providers

If `context_length` is omitted from a `custom_providers` entry, Hermes falls back to the endpoint's `/models` API or a small default (~128K). For models with large context windows (1M+), always set it explicitly:

```yaml
custom_providers:
  - name: longcat
    base_url: https://api.longcat.chat/openai
    key_env: LONGCAT_API_KEY
    api_mode: chat_completions
    context_length: 1048576        # 1M — required for correct window sizing
    max_completion_tokens: 131072   # 128K — set if model supports large output
    model: LongCat-2.0-Preview
```

### /model <alias> requires gateway restart after config changes

`DIRECT_ALIASES` (populated from `model_aliases`) is lazy-loaded on first call but cached in the gateway process. If you add or change a `model_aliases` entry, the running gateway won't see it until restart. Use `/restart` (gateway) or restart the CLI.
