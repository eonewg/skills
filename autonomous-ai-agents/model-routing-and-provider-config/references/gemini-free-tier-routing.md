# Gemini Developer API free-tier routing for Hermes

Use when adding Google Gemini Developer API keys to Hermes for low-cost/free auxiliary work or subagents without changing the main chat model.

## Credentials

Gemini Developer API is recognized by Hermes through either env var; setting both is safe when different code paths may check one or the other:

```bash
hermes config set GOOGLE_API_KEY <key>
hermes config set GEMINI_API_KEY <key>
```

Do not print the key during verification. Check presence with `hermes config check` or by listing env-key names only.

## Free-tier caveat

The Gemini Developer API free tier may use submitted content to improve Google products. Do **not** route privacy-sensitive material, full private conversation history, secrets, or proprietary code to free-tier Gemini by default. Keep sensitive tasks on the user's chosen private/paid provider unless explicitly approved.

## Good Gemini free-tier placements

Good low-risk placements:

```yaml
auxiliary:
  vision:
    provider: gemini
    model: gemini-3.5-flash
    base_url: ""
    api_key: ""
    timeout: 30
    download_timeout: 30
  approval:
    provider: gemini
    model: gemini-3.1-flash-lite
    base_url: ""
    api_key: ""
    timeout: 30
  monitor:
    provider: gemini
    model: gemini-3.1-flash-lite
    base_url: ""
    api_key: ""
    timeout: 60
```

Avoid by default on free tier:

- `session_search` when it may summarize private conversation history.
- `compression` when it contains the full current conversation unless the user accepts the privacy tradeoff.
- Main model fallback for sensitive work unless the user explicitly asks.

## Subagents / delegation

Hermes subagents are temporary isolated workers spawned by `delegate_task`: they get their own context and terminal session, run short bounded subtasks, and return a summary to the parent. They are useful for parallel research, code review, file inspection, or independent analysis. They are not durable or conversational after completion.

To route subagents to Gemini free tier while keeping the main model unchanged:

```yaml
delegation:
  provider: gemini
  model: gemini-3.1-flash-lite
  base_url: ""
  api_key: ""
  api_mode: ""
```

Use `gemini-3.1-flash-lite` for cheap/light subagents. If tool-use quality is insufficient, upgrade only delegation to `gemini-3.5-flash` rather than changing the main model.

## Verification

Minimal raw Gemini probes after writing the key:

```python
from pathlib import Path
import os, json, urllib.request
for line in (Path.home()/'.hermes/.env').read_text(errors='ignore').splitlines():
    if line.startswith('GOOGLE_API_KEY='):
        os.environ['GOOGLE_API_KEY'] = line.split('=', 1)[1].strip()
key = os.environ['GOOGLE_API_KEY']
model = 'gemini-3.1-flash-lite'
url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=' + key
payload = json.dumps({'contents':[{'parts':[{'text':'只回复 OK'}]}], 'generationConfig': {'maxOutputTokens': 20}}).encode()
req = urllib.request.Request(url, data=payload, headers={'Content-Type':'application/json'}, method='POST')
print(urllib.request.urlopen(req, timeout=45).status)
```

Then run `hermes config check` and, for provider resolution, `resolve_runtime_provider(requested='gemini')`. Note that provider resolution may not echo the target model even when `delegation.model` is set; verify the config value separately.

## Gateway lifecycle

Config changes are written immediately, but a running gateway may not pick up provider/alias/delegation changes until `/restart` or an external `hermes gateway restart`. Do not try to restart the gateway from inside a gateway-handled tool call; Hermes blocks it to avoid killing its own child process.
