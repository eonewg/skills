---
name: hermes-multi-model-config
title: Configure Multiple AI Models in Hermes
description: Setup fallback models, auxiliary task models, and provider routing for different AI workloads in Hermes Agent
tags: [hermes, configuration, models, providers, fallback, multi-model]
---

# Configuring Multiple AI Models in Hermes Agent

Hermes Agent supports multiple model configuration layers - from automatic failover to task-specific routing.

## The "Modal" Trap

⚠️ **Critical distinction:**
- `modal-backend` = Terminal sandbox backend (Modal Labs cloud compute) - **NOT AI models**
- `fallback_model` = Backup AI LLM when primary fails
- `auxiliary.*` = Task-specific models (vision, compression, etc.)

If you land on the "Modal Backend" configuration page, you're looking at terminal execution backends, not AI model configuration!

## The 4 Configuration Layers

| Layer | When Used | Config Location |
|-------|-----------|-----------------|
| **Primary Model** | Main conversation | `model.provider`, `model.default` |
| **Fallback Model** | Auto-failover on errors | `fallback_model` block |
| **Auxiliary Tasks** | Vision, web extract, compression | `auxiliary.*` blocks |
| **Subagents/Cron** | Delegated work, scheduled jobs | `delegation` block or per-job |

## Layer 1: Primary + Fallback Model

Automatic failover when primary hits rate limits or errors:

```yaml
# ~/.hermes/config.yaml

model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

### Custom Endpoint (Local/Ollama/vLLM)

```yaml
fallback_model:
  provider: custom
  model: llama-3.1-70b
  base_url: http://localhost:8000/v1
  api_key_env: LOCAL_API_KEY  # Name of env var containing key
```

### Fallback Trigger Conditions

Activates on:
- HTTP 429 (rate limits) - after exhausting retries
- HTTP 500/502/503 (server errors) - after retries
- HTTP 401/403 (auth failures) - immediately
- HTTP 404 or malformed responses - immediately

**Limit:** One activation per session. If fallback also fails, normal error handling takes over.

**Does NOT work for:** Subagents, cron jobs, auxiliary tasks

## Layer 2: Auxiliary Task Models

Configure different (usually cheaper) models for side tasks:

```yaml
auxiliary:
  vision:                    # Image analysis, browser screenshots
    provider: openrouter
    model: openai/gpt-4o
    timeout: 30
    download_timeout: 30
  
  web_extract:               # Web page summarization
    provider: openrouter
    model: google/gemini-2.5-flash
    timeout: 360
  
  compression:               # Context compression
    provider: auto
    model: ""
  
  session_search:            # Past conversation search
    provider: auto
  
  skills_hub:                # Skill discovery
    provider: auto
  
  mcp:                       # MCP tool operations
    provider: auto
  
  flush_memories:            # Memory consolidation
    provider: auto
```

### Compression (Alternative Config)

```yaml
compression:
  summary_provider: openrouter
  summary_model: google/gemini-3-flash-preview
  summary_base_url: null
  enabled: true
  threshold: 0.50
```

### Auto-Detection Chain (provider: "auto")

**Text tasks:** OpenRouter → Nous Portal → Custom endpoint → Codex → API-key providers

**Vision tasks:** Main provider (if vision-capable) → OpenRouter → Nous → Codex → Anthropic → Custom endpoint

## Layer 3: Subagent Delegation

Route subagent tasks to a different model:

```yaml
delegation:
  provider: openrouter
  model: google/gemini-3-flash-preview
  # base_url: http://localhost:1234/v1
  # api_key: local-key
```

## Layer 4: Cron Jobs

Per-job model specification:

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

## Provider Reference

| Provider | Config Value | Required Setup |
|----------|--------------|----------------|
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` in `.env` |
| Nous Portal | `nous` | `hermes auth` (OAuth) |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` or Claude Code auth |
| OpenAI Codex | `openai-codex` | ChatGPT OAuth via `hermes model` |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN` or `gh auth token` |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| Custom endpoint | `custom` | `base_url` + env var with API key |

## Environment Variable Alternatives

While `config.yaml` is preferred, you can use env vars:

```bash
# ~/.hermes/.env
AUXILIARY_VISION_PROVIDER=openrouter
AUXILIARY_VISION_MODEL=openai/gpt-4o
AUXILIARY_VISION_BASE_URL=https://custom.api/v1
AUXILIARY_VISION_API_KEY=sk-...
```

## Common Configuration Patterns

### Premium + Budget Fallback
```yaml
model:
  provider: anthropic
  default: claude-opus-4

fallback_model:
  provider: openrouter
  model: google/gemini-3-flash-preview
```

### Task-Optimized Routing
```yaml
model:
  provider: openrouter
  default: anthropic/claude-sonnet-4

auxiliary:
  vision:
    provider: openrouter
    model: openai/gpt-4o
  web_extract:
    provider: openrouter
    model: google/gemini-2.5-flash
  compression:
    provider: openrouter
    model: google/gemini-3-flash-preview

delegation:
  provider: openrouter
  model: google/gemini-3-flash-preview
```

## Verification Commands

```bash
hermes config              # View current config
hermes config check        # Check for missing options
hermes config migrate      # Interactively add missing options
hermes config set model anthropic/claude-opus-4
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Fallback not triggering | Check both `provider` and `model` are set in `fallback_model` |
| Vision not working | Ensure model supports multimodal (e.g., GPT-4o, Gemini) |
| Custom endpoint fails | Verify `base_url` ends with `/v1`, check `api_key_env` points to valid env var |
| Subagent using wrong model | Set `delegation.provider` and `delegation.model` explicitly |

## References

- `/docs/integrations/providers` - Provider setup guide
- `/docs/user-guide/features/fallback-providers` - Fallback behavior
- `/docs/user-guide/configuration` - General configuration
