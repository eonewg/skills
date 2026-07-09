---
title: OpenClaw Active Memory Configuration
name: openclaw-active-memory
version: 1.0
description: Configure the Active Memory plugin for OpenClaw to enable automatic memory recall before replies.
triggers:
  - configure active memory
  - setup openclaw memory
  - enable active memory
  - openclaw active memory
prerequisites:
  - OpenClaw installed and configured
  - ~/.openclaw/openclaw.json exists
---

# OpenClaw Active Memory Configuration

## Overview

Active Memory is an optional plugin that runs a memory sub-agent before the main reply, automatically surfacing relevant memories without requiring the user to say "remember this" or "search memory".

## Configuration Steps

### 1. Check Documentation

Review the official docs at:
```
https://docs.openclaw.ai/concepts/active-memory
```

Key concepts:
- Runs before main reply (blocking)
- Only works in interactive persistent chat sessions
- Three query modes: `message`, `recent`, `full`
- Multiple prompt styles: `balanced`, `strict`, `contextual`, `preference-only`, etc.

### 2. Read Existing Configuration

```bash
cat ~/.openclaw/openclaw.json | jq '.plugins'
```

Identify:
- Current `plugins.allow` list
- Existing `plugins.entries` structure

### 3. Add to Allow List

Add `"active-memory"` to `plugins.allow` array:

```json
"plugins": {
  "allow": [
    "telegram",
    "discord",
    "tavily",
    "openrouter",
    "openai",
    "memory-tencentdb",
    "memory-wiki",
    "openclaw-weixin",
    "openclaw-lark",
    "memory-core",
    "active-memory"
  ],
```

### 4. Add Plugin Configuration

Add entry to `plugins.entries`:

```json
"active-memory": {
  "enabled": true,
  "config": {
    "enabled": true,
    "agents": ["main"],
    "allowedChatTypes": ["direct"],
    "modelFallbackPolicy": "default-remote",
    "queryMode": "recent",
    "promptStyle": "balanced",
    "timeoutMs": 15000,
    "maxSummaryChars": 220,
    "persistTranscripts": false,
    "logging": true
  }
}
```

### 5. Configuration Options Reference

| Key | Type | Description | Recommended |
|-----|------|-------------|-------------|
| `agents` | string[] | Agent IDs to enable | `["main"]` |
| `allowedChatTypes` | string[] | Session types | `["direct"]` for DM only |
| `queryMode` | string | Context sent to sub-agent | `"recent"` (balanced) |
| `promptStyle` | string | Recall aggressiveness | `"balanced"` or `"preference-only"` |
| `timeoutMs` | number | Sub-agent timeout | `15000` |
| `maxSummaryChars` | number | Max memory chars | `220` |
| `modelFallbackPolicy` | string | Fallback behavior | `"default-remote"` |
| `persistTranscripts` | boolean | Keep debug logs | `false` (true for debugging) |
| `logging` | boolean | Enable logging | `true` initially |

### 6. Restart Gateway

```bash
openclaw gateway
```

### 7. Verify in Session

Enable verbose mode:
```
/verbose on
```

Expected output when active memory runs:
```
🧩 Active Memory: ok 842ms recent 34 chars
🔎 Active Memory Debug: <memory summary>
```

### 8. Session Commands

Control active memory per session:
```
/active-memory status    # Check status
/active-memory off       # Disable for this session
/active-memory on        # Re-enable
/active-memory off --global  # Disable globally
```

## Query Modes Explained

- **message**: Only latest user message (fastest, ~3-5s timeout)
- **recent**: Latest message + recent conversation tail (~15s timeout)
- **full**: Full conversation history (slowest, most context)

## Prompt Styles

- **balanced**: General purpose default
- **strict**: Minimal recall, very conservative
- **contextual**: Continuity-friendly
- **recall-heavy**: More willing to surface memory
- **precision-heavy**: Only obvious matches
- **preference-only**: Optimized for habits, taste, favorites

## Troubleshooting

If not working:
1. Confirm plugin enabled: `plugins.entries.active-memory.enabled: true`
2. Check agent ID in `config.agents`
3. Verify interactive persistent session (not headless/heartbeat)
4. Turn on `logging: true` and check gateway logs
5. Test memory search: `openclaw memory status --deep`

If too slow:
- Lower `queryMode` to `message`
- Reduce `timeoutMs`
- Reduce `recentUserTurns` / `recentAssistantTurns`

## Pitfalls

- Only works in interactive persistent sessions (not cron/heartbeat)
- Increases latency (blocking sub-agent call)
- Can be disabled per session with `/active-memory off`
- Requires restart after config changes
