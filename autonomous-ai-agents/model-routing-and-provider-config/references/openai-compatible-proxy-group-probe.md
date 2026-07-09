# OpenAI-compatible proxy key/group/model probe

Use this when adding a Hermes custom provider that points at a New API / One API / TokenHub-style OpenAI-compatible proxy and a requested model fails even though the base URL and key are syntactically correct.

## Durable lesson

For proxy panels, the API key may be bound to a limited upstream group or model set. Hermes can parse and resolve the provider correctly while live calls still fail with `model_not_found`, quota, or a message such as `暂无default可用分组，请切换至gemini或claude分组`. Treat that as an upstream key/group/model-access issue unless a raw endpoint probe contradicts it.

## Safe config pattern

- Store only the base URL root in Hermes, e.g. `http://host:3000/v1`, not `/chat/completions`.
- Store the secret in `~/.hermes/.env`, referenced by `key_env`.
- Preserve the existing default `model.provider` and `model.default` unless the user explicitly asks to switch.
- For a `model_aliases` shortcut to a `custom_providers` entry, use `provider: custom:<name>`.

Example:

```yaml
custom_providers:
- name: tudou
  base_url: http://43.133.165.104:3000/v1
  key_env: TUDOU_API_KEY
  api_mode: chat_completions
  model: "[25额度aws]claude-opus-4-7"

model_aliases:
  tudou:
    model: "[25额度aws]claude-opus-4-7"
    provider: custom:tudou
```

## Verification sequence

1. Backup `config.yaml` and `.env` before editing.
2. Upsert the key in `.env` without printing it in final replies.
3. Run `hermes config check`.
4. Verify Hermes resolution, e.g. `resolve_runtime_provider(requested='<name>')` should show `provider: custom`, `source: custom_provider:<name>`, expected base URL/model/api mode.
5. Probe `/v1/models` with the same key. If the requested model is absent and only unrelated models are listed, note that the key likely lacks access to the requested upstream group/model.
6. Send a tiny raw chat request (`只回复 OK`, `max_tokens: 10`) to `/v1/chat/completions` using the exact configured model.

## Interpreting results

- `hermes config check` passes + runtime provider resolves + raw chat succeeds: configuration is live.
- `hermes config check` passes + runtime provider resolves + raw chat returns `model_not_found` or “switch to gemini/claude group”: Hermes is configured, but the proxy key/group/model access is wrong upstream.
- `/v1/models` returns only Gemini models while a Claude/Opus alias is configured: either change the alias/model to one of the visible models for temporary use, or ask the user to enable/switch the key to the Claude group upstream and retest.
- A second key that returns the same `/v1/models` list and same `model_not_found` confirms the issue is key/group scope, not local key writing.

## Reporting style

Be concise: state that provider setup succeeded separately from model access failure. Include the visible model IDs and the upstream error, but do not reprint API keys.
