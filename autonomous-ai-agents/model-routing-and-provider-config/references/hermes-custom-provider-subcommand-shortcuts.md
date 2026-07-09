# Hermes custom-provider subcommand shortcuts

Use this when a user wants a short slash command for model switching, including:
- a single OpenAI-compatible custom provider exposing multiple upstream models, with grouped commands such as `/provider small` and `/provider large`;
- a built-in provider shortcut such as `/gemini`, `/gpt`, or `/sense` that should map to a deterministic model alias.

## Config pattern

```yaml
custom_providers:
  - name: provider_name
    base_url: https://proxy.example.com/v1
    key_env: PROVIDER_API_KEY
    api_mode: chat_completions
    model: default-model-id
    models:
      default-model-id: {}
      stronger-model-id: {}

model_aliases:
  small:
    model: default-model-id
    provider: custom:provider_name
  large:
    model: stronger-model-id
    provider: custom:provider_name

quick_commands:
  provider_name:
    type: alias
    target: /model
```

Why `target: /model`? Quick-command aliases append the user's trailing arguments. Therefore `/provider_name large` rewrites to `/model large`, and model-switch resolution uses `model_aliases.large` to select the exact `custom:provider_name` model.

For a fixed shortcut to one alias, set the quick-command target to the full model command:

```yaml
model_aliases:
  gemini:
    model: gemini-3.5-flash
    provider: gemini

quick_commands:
  gemini:
    type: alias
    target: /model gemini
```

Prefer `hermes config set` over direct file edits when changing `~/.hermes/config.yaml` from an agent session, because security guards may refuse direct writes to Hermes config files:

```bash
hermes config set model_aliases.gemini.model gemini-3.5-flash
hermes config set model_aliases.gemini.provider gemini
hermes config set quick_commands.gemini.type alias
hermes config set quick_commands.gemini.target '/model gemini'
```

## Verification pattern

1. Parse config and assert the quick command, aliases, and custom provider model list exist.
2. Exercise Hermes' actual model-switch resolver, not just YAML parsing:

```bash
PYTHONPATH=/path/to/hermes-agent /path/to/hermes-agent/venv/bin/python - <<'PY'
from hermes_cli.config import load_config
from hermes_cli.model_switch import switch_model, parse_model_flags, resolve_alias
cfg = load_config()
for raw in ['small', 'large']:
    print(raw, parse_model_flags(raw), resolve_alias(raw, cfg['model']['provider']))
    res = switch_model(raw, cfg['model']['provider'], cfg['model']['default'], custom_providers=cfg.get('custom_providers'))
    print(res.success, res.new_model, res.target_provider, res.base_url, res.api_mode, res.error_message)
PY
```

3. For proxy-backed providers, run a lightweight provider probe too:
   - `GET /v1/models` to confirm the target model IDs are visible for the configured key.
   - A tiny `POST /v1/chat/completions` with the new model to confirm the upstream group/model is callable.
4. For built-in providers, a minimal `hermes chat --provider <provider> --model <model> -q '...'` is enough to distinguish routing/config success from account-state failures. For example, Gemini returning `HTTP 429: prepayment credits are depleted` after the model resolver succeeds means the shortcut/key path is wired correctly but the Google AI Studio project needs billing/credits.
5. In gateway sessions, tell the user to run `/restart` if a newly added quick command is not recognized immediately; the gateway reads config at startup.

## Pitfalls

- A `quick_commands.<name>.target` of `/model <default-alias>` creates a fixed shortcut; it will not make `/name other-alias` a grouped subcommand. Use `target: /model` when arguments should be forwarded.
- For `model_aliases` targeting a named custom provider, use `provider: custom:<name>`, not the bare provider name.
- Adding `custom_providers.<name>.models` improves picker/catalog visibility, but `model_aliases` are what make short `/model <alias>` switches deterministic.
- A successful `hermes config check` or YAML parse does not prove the proxy key can call the model; verify `/v1/models` and a minimal chat request when access is uncertain.
