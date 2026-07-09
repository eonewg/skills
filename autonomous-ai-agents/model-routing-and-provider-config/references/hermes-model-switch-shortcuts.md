# Hermes model-switch shortcuts

Use this reference when a user wants a cheap/default chat model most of the time and a stronger model for complex turns, or when adding a completely new custom provider with quick-command access.

## Pattern: existing provider → alias + quick command

Define model aliases for the concrete model/provider pairs, then optionally expose short slash commands that alias to `/model <alias>`.

```yaml
model_aliases:
  a:
    model: agnes-2.0-flash
    provider: agnes
  g:
    model: gpt-5.5
    provider: openai-codex

quick_commands:
  a:
    type: alias
    target: /model a
  g:
    type: alias
    target: /model g
```

Then in CLI or gateway chats:

```text
/a   # switch current session to Agnes
/g   # switch current session to gpt-5.5
```

`/model <alias>` is session-scoped by default. Add `--global` only when the user explicitly wants to change the persistent default model.

## Full workflow: adding a new custom provider with shortcuts

When the user provides an API key, base URL, and model name for a completely new provider, the setup spans three config layers plus `.env`:

### 1. Define the provider in `custom_providers:`

```yaml
custom_providers:
  - name: longcat
    base_url: https://api.longcat.chat/openai
    key_env: LONGCAT_API_KEY    # arbitrary env-var name
    api_mode: chat_completions
    # Optional: set context_length for non-default window
    context_length: 1048576      # 1M tokens
```

**Important:** Store only the base URL root (e.g. `https://api.longcat.chat/openai`), not the full method path. If the provider docs give `.../v1/chat/completions`, strip to `.../v1`.

### 2. Add the API key to `~/.hermes/.env`

```
LONGCAT_API_KEY=sk-<redacted>
```

The env var name must match `key_env` from step 1 exactly.

### 3. Add a model alias

```yaml
model_aliases:
  longcat:
    model: LongCat-2.0-Preview
    provider: longcat          # bare provider name, NO "custom:" prefix
```

### 4. (Optional) Add a quick command

```yaml
quick_commands:
  longcat:
    type: alias
    target: /model longcat
```

### 5. Verify

```bash
grep -A 5 'name: longcat' ~/.hermes/config.yaml  # provider definition
hermes doctor                     # config check
# In session: /longcat or /model longcat
```

## Critical pitfalls

### 🔴 model_aliases.provider uses the BARE name

This is the most common mistake. The `provider` field in `model_aliases` uses the bare custom provider name (e.g. `longcat`, `agnes`, `sensenova`), **NOT** `custom:longcat`.

The `custom:` prefix is only used in the `/model` slash command's triple syntax:
- `/model custom:longcat:LongCat-2.0-Preview` ← correct for inline switch
- `provider: custom:longcat` ← WRONG in model_aliases
- `provider: longcat` ← CORRECT in model_aliases

### 🔴 `model_routing.quick_switch` does NOT exist

The Hermes feature for user-defined slash commands is called `quick_commands`, not `model_routing.quick_switch`. There is no `model_routing.quick_switch` config key. Use `quick_commands` with `type: alias` pointing to `/model <alias>`.

### 🔴 Full method URLs in base_url

If the provider publishes `https://host/v1/chat/completions`, store only `https://host/v1` (or `https://host/openai` for non-standard paths). Hermes appends `/chat/completions` itself.

### 🔴 Don't forget context_length

For non-standard context windows (1M, 2M, etc.), set `context_length` on the `custom_providers` entry. Without it, Hermes assumes ~128K default and may make wrong compression decisions.

## Verifying a custom provider endpoint

Before wiring into aliases, verify the endpoint works standalone:

```bash
curl -s https://api.longcat.chat/openai/models \
  -H "Authorization: Bearer $LONGCAT_API_KEY" | head -20
```

For a chat-completion smoke test:

```bash
curl -s https://api.longcat.chat/openai/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LONGCAT_API_KEY" \
  -d '{"model":"LongCat-2.0-Preview","messages":[{"role":"user","content":"Reply with exactly: ok"}]}' | python3 -m json.tool
```

## Notes

- Keep secrets in `.env`; aliases should only name model/provider/base_url values.
- Use model aliases for reusable human-facing shortcuts; use fallback chains or provider routing for failure handling and policy routing.
- Do not promise stable automatic task-complexity routing unless a plugin/router is actually configured and tested. For most users, explicit `/a` and `/g`-style switches are lower risk and easier to reason about.
