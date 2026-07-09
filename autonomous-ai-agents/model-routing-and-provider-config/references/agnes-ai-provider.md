# Agnes AI OpenAI-compatible provider notes

Use when adding or verifying Agnes AI models in Hermes.

## Agnes 2.0 Flash

Authoritative docs: `https://agnes-ai.com/doc/agnes-20-flash`

Known-good Hermes named-provider shape:

```yaml
providers:
  agnes:
    name: agnes
    base_url: https://apihub.agnes-ai.com/v1
    key_env: AGNES_API_KEY
    default_model: agnes-2.0-flash
    api_mode: chat_completions
```

```bash
# ~/.hermes/.env
AGNES_API_KEY=sk-...
```

Important: the documented endpoint is `https://apihub.agnes-ai.com/v1/chat/completions`, but Hermes/OpenAI clients should be configured with the base URL root `https://apihub.agnes-ai.com/v1`; the client appends `/chat/completions`.

## Minimal live probe

Use the stored env key and redact it from output:

```bash
API_KEY=$(python3 - <<'PY'
from pathlib import Path
for line in Path('~/.hermes/.env').expanduser().read_text().splitlines():
    if line.startswith('AGNES_API_KEY='):
        print(line.split('=',1)[1].strip())
        break
PY
)
curl -sS https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"agnes-2.0-flash","messages":[{"role":"user","content":"Hello!"}]}'
```

Expected successful shape: HTTP 200 with `model: agnes-2.0-flash` and an assistant message.

Hermes smoke test:

```bash
hermes chat --provider agnes --model agnes-2.0-flash -q 'Reply with exactly: ok' --toolsets safe -Q
```

## Optional thinking mode

Docs recommend enabling thinking for coding/debugging/agent workflows via OpenAI-compatible `chat_template_kwargs`:

```yaml
providers:
  agnes:
    extra_body:
      chat_template_kwargs:
        enable_thinking: true
```

Do not enable this globally unless the user asks or the intended workload is coding/agent execution; it changes every Agnes request.

## Capabilities from docs

- Chat completions, multi-turn conversation, system prompt
- Streaming output
- Tool calling / agent workflows
- Coding and reasoning tasks
- Image URL input / image understanding via publicly accessible image URLs
- Context: 256K; max output: 65.5K
