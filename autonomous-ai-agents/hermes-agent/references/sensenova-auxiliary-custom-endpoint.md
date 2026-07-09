# SenseNova Token endpoint for Hermes auxiliary tasks

Use this when configuring Hermes auxiliary helpers (for example `compression` and `title_generation`) to use SenseNova TokenHub / SenseNova OpenAI-compatible chat completions.

## Proven endpoint shape

The user-provided chat-completions URL may be:

```text
https://token.sensenova.cn/v1/chat/completions
```

Hermes auxiliary config expects the OpenAI client `base_url`, not the full chat-completions path. Store it as:

```yaml
base_url: https://token.sensenova.cn/v1
api_mode: chat_completions
```

The OpenAI SDK appends `/chat/completions` itself.

## Example config block

```yaml
auxiliary:
  compression:
    provider: custom
    model: deepseek-v4-flash
    base_url: https://token.sensenova.cn/v1
    api_key: <secret or ${ENV_VAR} if the running process loads it>
    api_mode: chat_completions
    timeout: 120
  title_generation:
    provider: custom
    model: deepseek-v4-flash
    base_url: https://token.sensenova.cn/v1
    api_key: <secret or ${ENV_VAR} if the running process loads it>
    api_mode: chat_completions
    timeout: 30
```

## Verification probe

After editing, verify through Hermes' auxiliary router rather than a raw curl, so config parsing, base-url normalization, and task routing are tested together:

```python
from agent.auxiliary_client import call_llm, extract_content_or_reasoning, shutdown_cached_clients
try:
    resp = call_llm(
        task="title_generation",
        messages=[{"role":"user","content":"只回复 OK"}],
        max_tokens=8,
        temperature=0,
    )
    print((extract_content_or_reasoning(resp) or "").strip())
finally:
    shutdown_cached_clients()
```

Expected output contains `OK`.

## Pitfalls

- Do not put `/chat/completions` in `auxiliary.*.base_url`; the OpenAI client will append it.
- If using `${ENV_VAR}` in `config.yaml`, verify the running Hermes process actually loads that env var. For immediate current-process reliability, a direct `api_key` in config works but is less ideal than a properly loaded env reference.
- Do not record actual API keys in skills, memory, or chat summaries.
