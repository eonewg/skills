# OpenClaw Provider / Model Config (openclaw.json)

## Overview

OpenClaw stores model provider and routing config in `~/.openclaw/openclaw.json`, not `config.yaml`. 
Key sections differ from Hermes Agent — always edit the JSON directly or via `jq`/python, not through a yaml equivalent.

## Config Structure

Four layers to consider when adding or removing a provider:

### 1. Provider registration (`models.providers`)

```json
"models": {
  "mode": "merge",
  "providers": {
    "<provider-name>": {
      "baseUrl": "https://api.example.com/v1",
      "apiKey": "sk-...",
      "api": "openai-completions",
      "models": [
        {
          "id": "model-name",
          "name": "model-name",
          "reasoning": false,
          "input": ["text"],
          "cost": { "input": 0.0025, "output": 0.01, "cacheRead": 0, "cacheWrite": 0 },
          "contextWindow": 65536,
          "maxTokens": 32768,
          "api": "openai-completions"
        }
      ]
    }
  }
}
```

### 2. Primary model + fallback chain (`agents.defaults.model`)

```json
"agents": {
  "defaults": {
    "model": {
      "primary": "<provider>/<model-id>",
      "fallbacks": [
        "<provider2>/<model-id2>",
        "<provider3>/<model-id3>"
      ]
    }
  }
}
```

When removing a provider, ALL references in the fallback chain must be cleaned up.

### 3. Model aliases (`agents.defaults.models`)

```json
"agents": {
  "defaults": {
    "models": {
      "<provider>/<model-id>": {
        "alias": "short-name"
      }
    }
  }
}
```

When removing a provider, remove all its alias entries.

### 4. Auth profile (`auth.profiles`)

Optional — only needed when the provider auth is managed separately from inline `apiKey`:

```json
"auth": {
  "profiles": {
    "<provider>:<name>": {
      "provider": "<provider>",
      "mode": "api_key"
    }
  }
}
```

## CRITICAL: baseUrl Convention

For `api: "openai-completions"`, OpenClaw **automatically appends** `/chat/completions` to the baseUrl.

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| `https://token.sensenova.cn/v1/chat/completions` | `https://token.sensenova.cn/v1` |
| `https://qianfan.baidubce.com/v2/coding/chat/completions` | `https://qianfan.baidubce.com/v2` |

This applies to ALL OpenAI-compatible providers. Always strip the chat completions path from the baseUrl.

## Provider Patterns from This Session

### Sensenova (燧原科技 / token.sensenova.cn)

```json
{
  "baseUrl": "https://token.sensenova.cn/v1",
  "apiKey": "sk-...",
  "api": "openai-completions",
  "models": [{
    "id": "deepseek-v4-flash",
    "name": "deepseek-v4-flash",
    "reasoning": false,
    "input": ["text", "image"],
    "cost": { "input": 0.0025, "output": 0.01, "cacheRead": 0, "cacheWrite": 0 },
    "contextWindow": 65536,
    "maxTokens": 32768,
    "api": "openai-completions"
  }]
}
```

Sensenova's deepseek-v4-flash supports multimodal (text + image).

### OpenRouter

```json
{
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKey": "sk-or-...",
  "api": "openai-completions",
  "models": [...]
}
```

Free models follow the same path pattern: `openrouter/stepfun/step-3.5-flash:free`, `openrouter/qwen/qwen3.6-plus-preview:free`.

## Verification After Changes

```bash
# Validate JSON
python3 -c "import json; json.load(open('~/.openclaw/openclaw.json'))"

# Check no stale references
jq '.agents.defaults.model' ~/.openclaw/openclaw.json
jq '[.models.providers | keys]' ~/.openclaw/openclaw.json

# Restart gateway
openclaw gateway restart

# Confirm status
openclaw status | grep "Gateway"
```

## Common Pitfalls

- **Stale fallback references**: After removing a provider, its models may still exist in `fallbacks` array — OpenClaw will error at runtime.
- **Stale alias entries**: `agents.defaults.models` still referencing a removed provider's models.
- **Double path**: Including `/chat/completions` in baseUrl when using `api: "openai-completions"` — OpenClaw appends it automatically, producing a double path.
- **API key inline vs profile**: For inline keys (embedded in `models.providers.<name>.apiKey`), no auth profile is needed. For profile-managed auth, ensure the profile name matches the provider name used in model references.
- **Changing model ID**: Model reference format is `<provider>/<model-id>`. Changing the model id requires updating primary, fallbacks, and aliases simultaneously.