# Custom Provider Context Length Configuration

## Problem
Setting `context_length: 1048576` at the top level of a `custom_providers` entry in `config.yaml` is **ignored**. The model still reports 256K context.

## Root Cause
`get_custom_provider_context_length()` in `hermes_cli/config.py` reads from `entry["models"]["<model_name>"]["context_length"]`, NOT from `entry["context_length"]`.

## Correct Config Structure
```yaml
custom_providers:
  - name: myprovider
    base_url: https://api.example.com/v1
    key_env: MY_API_KEY
    api_mode: chat_completions
    models:
      MyModel-Name:
        context_length: 1048576
        max_completion_tokens: 131072
```

## model_aliases provider field
Use the bare provider name (e.g. `longcat`), NOT `custom:longcat`. Validation auto-prepends `custom:` when comparing.

```yaml
model_aliases:
  longcat:
    model: LongCat-2.0-Preview
    provider: longcat          # correct: bare name
```

## quick_commands
```yaml
quick_commands:
  longcat:
    type: alias
    target: /model longcat
```
Gateway restart required after adding new quick_commands.