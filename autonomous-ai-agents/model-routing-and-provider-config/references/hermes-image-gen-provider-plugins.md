# Hermes image-generation provider plugins

Use this note when the user asks to configure a non-built-in image generation backend for Hermes' `image_generate` tool.

## When a provider is not built into Hermes

Hermes image generation is routed through backend plugins under `plugins/image_gen/<name>/`. A user-local provider can live at:

```text
~/.hermes/plugins/image_gen/<provider-name>/
├── __init__.py
└── plugin.yaml
```

`plugin.yaml` should use `kind: backend`, and the Python module must expose `register(ctx)` that calls `ctx.register_image_gen_provider(<ImageGenProvider instance>)`.

User-local plugins are opt-in. Enable with a real YAML list under `plugins.enabled`, e.g.:

```yaml
plugins:
  enabled:
    - image_gen/ark-seedream
```

Pitfall: `hermes config set plugins.enabled '["image_gen/ark-seedream"]'` may persist a string instead of a YAML list. If `hermes plugins list` says the plugin is not enabled, inspect the raw config and rewrite `plugins.enabled` as a list (prefer using Hermes' config helpers/atomic YAML writer, not ad-hoc text replacement).

## Ark Seedream 5.0 Lite example

Official endpoint:

```text
POST https://ark.cn-beijing.volces.com/api/v3/images/generations
```

Use the same `ARK_API_KEY` already used by the Volcengine Ark LLM provider unless the user wants a separate image key. A minimal config:

```yaml
image_gen:
  provider: ark-seedream
  model: doubao-seedream-5-0-260128
  ark_seedream:
    base_url: https://ark.cn-beijing.volces.com/api/v3
    model: doubao-seedream-5-0-260128
    response_format: url
    output_format: png
    watermark: false
    sequential_image_generation: disabled
```

Provider implementation notes:

- Subclass `agent.image_gen_provider.ImageGenProvider`.
- Return `name = "ark-seedream"` and implement `generate(prompt, aspect_ratio, image_url=None, reference_image_urls=None, **kwargs)`.
- POST JSON to `<base_url>/images/generations` with `Authorization: Bearer $ARK_API_KEY`.
- Map Hermes aspect ratios to Ark-supported 2K exact sizes, e.g. square `2048x2048`, landscape `2848x1600`, portrait `1600x2848`, or let config override `size` / per-aspect `sizes`.
- For text-to-image, omit `image`.
- For image-to-image / reference images, set `image` to a string for one source or an array for multiple sources. Ark Seedream supports URL and `data:image/<format>;base64,...`; local paths should be read only after `agent.file_safety.raise_if_read_blocked` and converted to data URIs.
- Prefer `response_format: url`; because Ark URLs expire, cache the result immediately with `save_url_image`. If using `b64_json`, write it with `save_b64_image`.
- Include `watermark: false` when the user expects clean generated images.
- Keep `stream: false` for the Hermes `image_generate` tool unless implementing SSE parsing.
- Seedream 5.0 Lite supports `tools: [{type: "web_search"}]` and `output_format: png|jpeg`; expose these as config flags if needed rather than hardcoding them on every call.

## Verification sequence

1. Confirm `ARK_API_KEY` exists without printing it.
2. Force plugin discovery and inspect the registry:

```python
from hermes_cli.plugins import _ensure_plugins_discovered
from agent import image_gen_registry
_ensure_plugins_discovered(force=True)
print([(p.name, p.display_name, p.is_available()) for p in image_gen_registry.list_providers()])
print(image_gen_registry.get_active_provider().name)
```

3. Run one real minimal generation through the provider object, not just config parsing. Confirm `success: true`, expected provider/model, a cached local image path or valid URL, and returned size.
4. Tell the user that an already-running chat/gateway may have stale tool-description schema until `/reset` or gateway restart, even though runtime config is already changed.
