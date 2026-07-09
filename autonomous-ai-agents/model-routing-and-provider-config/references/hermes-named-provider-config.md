# Hermes named provider configuration

Use this when adding an OpenAI-compatible endpoint as a reusable named provider in Hermes without changing the current default model.

## Pattern

Store secrets in `~/.hermes/.env`, and reference them from `~/.hermes/config.yaml` with `key_env`:

```yaml
providers:
  provider_name:
    name: provider_name
    base_url: https://example.com/v1
    key_env: PROVIDER_NAME_API_KEY
    default_model: vendor-model-id
    api_mode: chat_completions
```

```bash
# ~/.hermes/.env
PROVIDER_NAME_API_KEY=sk-...
```

This lets `hermes chat --provider provider_name --model vendor-model-id` resolve as a custom OpenAI-chat runtime while keeping the API key out of config.

## Verification workflow

After writing config/env:

1. Confirm `hermes config check` passes.
2. Verify runtime resolution with `hermes_cli.runtime_provider.resolve_runtime_provider(requested='<provider_name>')` after loading `~/.hermes/.env` into `os.environ`. Check only non-secret fields: provider/custom, requested_provider, api_mode, base_url, model/default_model, source, and whether an API key is present.
3. Optionally make a minimal `/chat/completions` request against `<base_url>/chat/completions` with the target model and tiny `max_tokens` to catch bad credentials or non-OpenAI-compatible behavior. Never print the secret; only report status and sanitized error text.

## Pitfalls

- Do not hardcode API keys in `config.yaml` when `key_env` is available.
- Do not silently change `model.provider` / `model.default` when the user only asked to “add” a provider; preserve the current default unless they explicitly ask to switch.
- Use the base URL root such as `https://host/v1`, not the full method path (`/chat/completions`), because the OpenAI-compatible client appends method paths itself.
- A successful Hermes runtime resolution only proves the config is wired; a live probe can still return auth or provider-specific errors that need to be reported separately.
- If the user asks to remove/delete a provider, clean up both config and credentials: remove the provider block, remove its env-key line(s), search for provider/base-url/name leftovers, and finish with `hermes config check`.

## Agnes AI example

For Agnes 2.0 Flash, use `base_url: https://apihub.agnes-ai.com/v1` and `model/default_model: agnes-2.0-flash`. The docs publish the full request URL `https://apihub.agnes-ai.com/v1/chat/completions`; do not put that full method path in Hermes config. See `references/agnes-ai-provider.md` for the known-good config and smoke tests.
