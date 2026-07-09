# Hermes auxiliary `auto` pinning

Use this when reducing auxiliary-task routing drift/cost in the user's Hermes config.

## Goal

Avoid leaving `auxiliary.<task>.provider: auto` for recurring helper tasks. `auto` can follow the generic fallback chain and may unexpectedly route through OpenRouter or another available provider. Prefer explicit provider/model pins by workload class.

## Proven workflow

1. Inspect the current auxiliary map without exposing secrets:
   ```bash
   python3 - <<'PY'
   from pathlib import Path
   import yaml, json
   cfg=yaml.safe_load((Path.home()/'.hermes/config.yaml').read_text()) or {}
   aux=cfg.get('auxiliary',{})
   print(json.dumps({k:{'provider':v.get('provider'),'model':v.get('model')} for k,v in aux.items() if isinstance(v,dict)}, ensure_ascii=False, indent=2))
   print('auto_remaining:', [k for k,v in aux.items() if isinstance(v,dict) and v.get('provider')=='auto'])
   PY
   ```
2. Back up config before editing:
   ```bash
   cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-aux-routing-$(date +%Y%m%d-%H%M%S)
   ```
3. Pin low-risk helpers to explicit routes.
4. Run `hermes config check`.
5. Verify there are no remaining auto providers.
6. Run real `agent.auxiliary_client.call_llm` probes for every changed task, not just config parsing.

## Example pins from the 2026-07-08 Hermes cost/context cleanup

These matched the user's current cost-quality policy and live credentials at the time:

- `mcp` → Ark `doubao-seed-evolving`
- `tts_audio_tags` → Gemini `gemini-3.1-flash-lite`
- `triage_specifier` → Gemini `gemini-3.1-flash-lite`
- `kanban_decomposer` → Ark `glm-5-2-260617`
- `curator` → Ark `glm-5-2-260617`
- `flush_memories` → Ark `doubao-seed-evolving`

Use these as a precedent, not a permanent rule; re-check quotas, provider health, and task needs before reapplying.

## Config commands pattern

```bash
hermes config set auxiliary.<task>.provider <provider>
hermes config set auxiliary.<task>.model <model>
# For Ark Responses API routes:
hermes config set auxiliary.<task>.api_mode codex_responses
```

## Live auxiliary probe

Use the actual Hermes auxiliary router:

```bash
PYTHONPATH=~/.hermes/hermes-agent ~/.hermes/hermes-agent/venv/bin/python - <<'PY'
from agent.auxiliary_client import call_llm

tasks=['mcp','tts_audio_tags','triage_specifier','kanban_decomposer','curator','flush_memories']
for task in tasks:
    try:
        r=call_llm(
            task=task,
            messages=[{'role':'user','content':'Reply exactly: ok'}],
            temperature=0,
            max_tokens=8,
        )
        content = r.choices[0].message.content if getattr(r,'choices',None) else str(r)[:80]
        print(f'{task}: OK | {content!r}')
    except Exception as e:
        print(f'{task}: ERROR | {type(e).__name__}: {e}')
PY
```

## Verification summary expected

- `hermes config check` exits 0.
- `auto_remaining: []`.
- Every changed auxiliary task returns `OK` from `call_llm`.
- Report the backup path so rollback is easy.

## Pitfalls

- Do not edit the default chat model/provider while pinning auxiliary tasks; these are separate routing layers.
- Do not treat `hermes config check` as a live-provider test. It only validates config shape/known env status.
- For Ark auxiliary tasks, prefer the named `ark` provider with `api_mode: codex_responses`; avoid raw custom config unless specifically testing provider internals.
- Do not encode a one-time provider choice as universally correct. Store the routing rationale and re-probe when quotas or model names change.
