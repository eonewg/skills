# Ant Ling / BaLing provider setup for Hermes

Use when adding Ant Ling (`api.ant-ling.com`) as an OpenAI-compatible provider in Hermes, or when planning model routing across Ling, Ring, and Ming model families.

## Endpoint shape

Ant Ling documents an OpenAI-compatible chat-completions endpoint:

```text
POST https://api.ant-ling.com/v1/chat/completions
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

Hermes custom providers should store the **base URL**, not the method URL:

```yaml
custom_providers:
  - name: ant
    base_url: https://api.ant-ling.com/v1
    key_env: ANT_API_KEY
    api_mode: chat_completions
    model: Ling-2.6-flash
    models:
      Ling-2.6-flash:
        context_length: 262144
      Ling-2.6-1T:
        context_length: 262144
      Ling-2.5-1T:
        context_length: 131072
      Ring-2.6-1T:
        context_length: 262144
      Ring-2.5-1T:
        context_length: 131072
      Ming-Flash-Omni: {}
```

Store the secret in `~/.hermes/.env`:

```bash
hermes config set ANT_API_KEY <token>
```

If adding aliases, custom-provider aliases need the `custom:` prefix:

```yaml
model_aliases:
  ling:
    provider: custom:ant
    model: Ling-2.6-flash
  ling-1t:
    provider: custom:ant
    model: Ling-2.6-1T
  ring:
    provider: custom:ant
    model: Ring-2.6-1T
  ring25:
    provider: custom:ant
    model: Ring-2.5-1T
  ming:
    provider: custom:ant
    model: Ming-Flash-Omni
```

## Model-family routing notes

- **Ling-2.6-flash**: 256K context, high cost-performance, supports tool calling. Best first choice for web extraction, session-search synthesis, skill/profile description, light document summarization, text cleanup, and cheap fallback.
- **Ling-2.6-1T**: 256K context, stronger general model for long documents, complex summaries, mid-tier fallback, and tasks that need more stability than flash without using the strongest default model.
- **Ling-2.5-1T**: 128K context, older flagship; useful as a conservative long-document / knowledge-QA fallback if 2.6 models misbehave.
- **Ring-2.6-1T**: 256K context reasoning/Agent model; best for coding-agent workflows, multi-tool tasks, complex research, math, and high-quality fallback. The API supports `reasoning.effort` (`high` default, `xhigh` deeper reasoning) for Ring-2.6-1T, but verify how Hermes passes provider-specific `extra_body` before depending on it.
- **Ring-2.5-1T**: 128K reasoning model; useful for math, code review/generation, paper analysis, and conservative fallback.
- **Ming-Flash-Omni**: full-modal model family according to model docs. The OpenAI-compatible API options page may not list it among chat-completions model IDs, so do not assign it to vision/audio/video production routes until a live probe confirms the endpoint accepts the model and payload shape.

## Workflow guidance

When the user asks to add a provider and then decide usage later, split the work:

1. Add only the structural provider config, env-key reference, and optional manual-switch aliases.
2. Do **not** change auxiliary routes, fallback chains, or smart-routing policy until the user confirms the placement plan.
3. Present a model-to-workload proposal with uncertainty called out, especially for models whose docs and API model list disagree.
4. After confirmation and credentials are available, run a tiny live probe for each model that will receive production traffic.
5. Restart the gateway only when the user wants the running gateway to pick up new aliases/config immediately; otherwise mention that restart is needed later.

## Verification snippets

Runtime provider resolution from the Hermes repo/session environment:

```python
from hermes_cli.runtime_provider import resolve_runtime_provider
r = resolve_runtime_provider(requested="custom:ant")
print(r.get("source"))      # custom_provider:ant
print(r.get("provider"))    # custom
print(r.get("base_url"))    # https://api.ant-ling.com/v1
print(r.get("api_mode"))    # chat_completions
print(r.get("model"))       # default from custom_providers entry
```

Live API smoke test once `ANT_API_KEY` is present:

```bash
curl -sS https://api.ant-ling.com/v1/chat/completions \
  -H "Authorization: Bearer $ANT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"Ling-2.6-flash","messages":[{"role":"user","content":"只回复 OK"}],"max_tokens":10}'
```
