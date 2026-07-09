# TencentDB Agent Memory for existing Hermes installs

Use this when integrating Tencent/TencentDB-Agent-Memory with an already-running Hermes Agent deployment. Prefer this over the README's Docker-first path when the user already has a configured Hermes gateway, messaging platforms, sessions, skills, and another memory provider such as `hindsight`.

## Recommended sequence

1. Keep the current Hermes memory provider active during installation.
   - Example current state: `memory.provider: hindsight`.
   - Do **not** switch to `memory_tencentdb` until provider discovery and sidecar health both pass.
2. Verify prerequisites:
   ```bash
   node -v        # must be >= 22.16
   npm -v
   hermes --version
   hermes memory status
   hermes gateway status
   ```
3. Install package under a separate root, not inside `~/.hermes`:
   ```bash
   ROOT="$HOME/.memory-tencentdb"
   INSTALL="$ROOT/tdai-memory-openclaw-plugin"
   DATA="$ROOT/memory-tdai"
   mkdir -p "$ROOT" "$DATA"

   TMP=$(mktemp -d)
   cd "$TMP"
   npm pack @tencentdb-agent-memory/memory-tencentdb@latest --silent > pkgname
   tar -xzf "$(cat pkgname)"
   mv package "$INSTALL"
   cd "$INSTALL"
   npm install --omit=dev
   npm install tsx   # if npx tsx --version fails
   ```
4. Link the Hermes provider. The directory name must be underscore form:
   ```bash
   ln -s \
     ~/.memory-tencentdb/tdai-memory-openclaw-plugin/hermes-plugin/memory/memory_tencentdb \
     ~/.hermes/hermes-agent/plugins/memory/memory_tencentdb
   ```
   `memory-tencentdb` is an alias in config, but the plugin directory must be `memory_tencentdb`.
5. Add sidecar env to `~/.hermes/.env` but do not switch provider yet:
   ```bash
   MEMORY_TENCENTDB_GATEWAY_CMD="sh -c 'cd ~/.memory-tencentdb/tdai-memory-openclaw-plugin && exec npx tsx src/gateway/server.ts'"
   MEMORY_TENCENTDB_GATEWAY_HOST="127.0.0.1"
   MEMORY_TENCENTDB_GATEWAY_PORT="8420"
   TDAI_DATA_DIR="~/.memory-tencentdb/memory-tdai"
   MEMORY_TENCENTDB_ROOT="~/.memory-tencentdb"
   ```
6. Add LLM extraction credentials before enabling as primary memory:
   ```bash
   MEMORY_TENCENTDB_LLM_API_KEY="..."
   MEMORY_TENCENTDB_LLM_BASE_URL="https://.../v1"
   MEMORY_TENCENTDB_LLM_MODEL="..."
   ```
   Important: Hermes `openai-codex` OAuth is not necessarily usable by the Node sidecar. The sidecar expects an OpenAI-compatible HTTP API key.
7. Test provider discovery:
   ```bash
   cd ~/.hermes/hermes-agent
   python3 - <<'PY'
   from plugins.memory import discover_memory_providers
   for n, cls, available in discover_memory_providers():
       if n in {'memory_tencentdb','hindsight'}:
           print(n, available, cls)
   PY
   hermes memory status
   ```
8. Test sidecar manually before switching:
   ```bash
   set -a; . ~/.hermes/.env; set +a
   cd ~/.memory-tencentdb/tdai-memory-openclaw-plugin
   npx tsx src/gateway/server.ts
   # separate shell
   curl http://127.0.0.1:8420/health
   ```
   Healthy without embedding may look like:
   ```json
   {"status":"ok","version":"0.1.0","stores":{"vectorStore":true,"embeddingService":false}}
   ```
9. Only after discovery + health + LLM credentials are ready:
   ```bash
   hermes config set memory.provider memory_tencentdb
   hermes gateway restart
   ```

## Conservative defaults

- Treat TencentDB Agent Memory first as long-term memory, not context offload.
- Keep `offload.enabled: false` initially; Hermes already has compression/session_search/wiki workflows, and offload adds a second context-management layer.
- Start without remote embedding if no reliable embedding API is available; use keyword/BM25 first, then add hybrid retrieval later.

## Pitfalls

- The npm package `postinstall` can run `scripts/openclaw-after-tool-call-messages.patch.sh` and patch a globally installed OpenClaw package. This does not directly affect Hermes, but note any `*.pre-offload-patch.bak` files and mention the side effect to the user.
- The README Docker path starts a separate Hermes deployment. Avoid it for users who already have a configured Hermes gateway unless they explicitly want a second containerized instance.
- Do not overwrite `memory.provider` during installation. Keep rollback simple by leaving the current provider in place until tests pass.
- If port `8420` is occupied, either stop the old sidecar or set `MEMORY_TENCENTDB_GATEWAY_PORT` consistently in `.env` and health checks.

## Rollback

```bash
hermes config set memory.provider hindsight
hermes gateway restart
pkill -f "src/gateway/server.ts" || true
rm ~/.hermes/hermes-agent/plugins/memory/memory_tencentdb
```

Keep `~/.memory-tencentdb/memory-tdai/` unless the user explicitly wants the data removed.
