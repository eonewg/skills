---
name: Kimi WebBridge
description: Browser automation via local Go daemon + Chrome/Edge extension — controls the user's real browser with their login sessions.
read_when:
  - User has a real browser with active login sessions to leverage
  - Need to interact with sites behind SSO/2FA where headless browsers won't work
  - The user asks to use "my browser" or kimi.com/webbridge
---

# Kimi WebBridge

Local daemon + browser extension that gives AI agents real browser control (the user's actual browser, with all their login sessions).

## Installation

```bash
curl -fsSL https://kimi-web-img.moonshot.cn/webbridge/install.sh | bash
```

Binary installed to `~/.kimi-webbridge/bin/kimi-webbridge`.

## Lifecycle

```bash
~/.kimi-webbridge/bin/kimi-webbridge status   # Check running state + extension connection
~/.kimi-webbridge/bin/kimi-webbridge start     # Start daemon
~/.kimi-webbridge/bin/kimi-webbridge stop      # Stop daemon
~/.kimi-webbridge/bin/kimi-webbridge logs -n 100  # View recent logs
~/.kimi-webbridge/bin/kimi-webbridge restart   # Stop + start
```

## Architecture

```
Browser Extension ←WebSocket→ Daemon (:10086) ←HTTP→ AI Agent
```

Two preconditions must be met before tool calls work:
1. **Daemon running** (`running: true`)
2. **Extension connected** (`extension_connected: true`) — user must install the Chrome/Edge extension from https://www.kimi.com/zh-cn/features/webbridge and open their browser

## API

All calls go to `POST http://127.0.0.1:10086/command` with JSON body.

### Request format

```json
{"action": "<action>", "args": {...}, "session": "<optional-session-name>"}
```

### Available actions

| Action | Args | Returns | Notes |
|--------|------|---------|-------|
| `navigate` | `url`, `newTab`(bool), `group_title` | `{success, url, tabId}` | Always use `newTab:true` on first call |
| `find_tab` | `url`, `active`(bool) | `{success, url, tabId}` | Reuse an existing tab; `active:true` for user's current tab |
| `snapshot` | — | `{url, title, tree}` with `@e` refs | Accessibility tree for reading content + locating elements |
| `click` | `selector` (@e ref or CSS) | `{success, tag, text}` | Synthetic `el.click()` |
| `fill` | `selector`, `value` | `{success, tag, mode}` | Works on `<input>`/`<textarea>` AND `[contenteditable]` |
| `evaluate` | `code` (async/await) | `{type, value}` | Run JS in page context |
| `screenshot` | `format`(png\|jpeg), `quality`(0-100), `selector` | `{format, data, dataLength}` | base64 — use helper script to avoid context flooding |
| `network` | `cmd`(start\|stop\|list\|detail), `filter`, `requestId` | request/response data | |
| `upload` | `selector`, `files`(string[]) | `{success, fileCount}` | |
| `save_as_pdf` | `paper_format`, `landscape`, `scale`, `print_background`, `file_name` | `{path, sizeBytes, mimeType}` | Saved under `/tmp/kimi-webbridge-pdfs/` |
| `list_tabs` | — | `{success, tabs:[...]}` | All tabs in current session |
| `close_tab` | — | `{success, closed:bool}` | Close current tab |
| `close_session` | — | `{success, closed:int}` | Close all tabs — call at task end |

### Sessions

Each session maps to a separate tab group in the browser. Use distinct session names for different tasks.

```json
{"action":"navigate","args":{"url":"https://example.com","newTab":true},"session":"my-task"}
```

## Status field reference

```
{
  "running": true,              // daemon listening on :10086
  "extension_connected": true,  // browser extension attached
  "port": 10086,
  "version": "v1.9.7",
  "uptime_seconds": 42
}
```

- `running: false` → daemon not running, start it
- `extension_connected: false` → user needs to open their browser with the extension installed

## Key differences from headless browser tools

| | Kimi WebBridge | agent-browser / Playwright |
|---|---|---|
| Browser | User's real browser | Headless/isolated |
| Login sessions | User's own cookies/sessions | None (need separate auth) |
| `isTrusted` events | `false` (DOM-level synthetic) | Same — both can't pass `isTrusted` checks |
| Cross-origin iframes | Cannot access | Cannot access (same limitation) |

## Pitfalls & notes

- **Stale PID / false start state**: If daemon dies unexpectedly, `status` may report `PID file exists but HTTP probe failed` with an old PID. A subsequent `start` can print `daemon started` while `status` still reads the stale PID. Fix by removing the pid file and starting clean: `rm -f ~/.kimi-webbridge/daemon.pid && ~/.kimi-webbridge/bin/kimi-webbridge start`, then re-check status.
- **Extension connection can lag**: Immediately after a clean start, `running:true` may appear with `extension_connected:false`. Wait a few seconds and run `status` again before asking the user to install/open the extension; the existing browser extension may reconnect automatically.
- **WSL/browser launch preflight**: If the daemon is running but the extension is disconnected, first check `~/.kimi-webbridge/bin/kimi-webbridge status`. If `extension_connected:false`, the blocker is the real browser extension, not the HTTP daemon. In WSL, only use Linux `google-chrome` directly when a GUI display exists (`$DISPLAY` or `$WAYLAND_DISPLAY` is set); otherwise launch the user's Windows Chrome via PowerShell/cmd or ask the user to open it. Then re-check status until it becomes `extension_connected:true`:
  ```bash
  ~/.kimi-webbridge/bin/kimi-webbridge status
  powershell.exe -NoProfile -Command "Start-Process 'chrome.exe' -ArgumentList 'https://www.kimi.com/zh-cn/features/webbridge'"
  sleep 5
  ~/.kimi-webbridge/bin/kimi-webbridge status
  ```
  Verify Chrome actually opened if needed:
  ```bash
  powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Select-Object -First 5 Id,ProcessName,MainWindowTitle | ConvertTo-Json -Compress"
  ```
  If Chrome exists but `extension_connected:false` remains, ask the user to enable/install Kimi WebBridge or grant extension permissions in `chrome://extensions/`, then wait and re-check. Do not declare browser automation ready until `extension_connected:true`.
- **WSL v1.10 focus / stale-window pitfall**: On the user's WSL setup after reinstalling daemon v1.10.0, `status` can be healthy (`running:true`, `extension_connected:true`) while `navigate` with `newTab:true` returns `No current window` or `find_tab active:true` returns `No last-focused window`. This does **not** mean WSL Chrome is unusable; it can mean either (a) the Linux Chrome window is not actually focused from the extension's perspective, (b) daemon/extension has stale current-window state, or (c) the main Chrome profile has extension/runtime conflicts that make Kimi's service worker see no tabs. Evidence pattern for (c): OS/X11 active window is Chrome and Chrome session files show open tabs, but WebBridge `find_tab` with `*://*/*` returns no tab and daemon logs show repeated extension disconnect/reconnect. Official Kimi FAQ says `snapshot`/`evaluate`/`screenshot`/`click` failures are commonly caused by conflicts with scraping tools, website helpers, screen recording extensions, and AI assistant extensions; keep only Kimi enabled to test. For a real isolation test in WSLg, launch the clean-profile Chrome with an explicit display, e.g. `env DISPLAY=:0 google-chrome --user-data-dir=/tmp/kimi-webbridge-clean-profile --disable-extensions-except=~/.config/google-chrome/Default/Extensions/fldmhceldgbpfpkbgopacenieobmligc/1.10.0_0 --load-extension=~/.config/google-chrome/Default/Extensions/fldmhceldgbpfpkbgopacenieobmligc/1.10.0_0 https://example.com`; without explicit `DISPLAY`, Hermes background processes may fail with `Missing X server or $DISPLAY`, invalidating the test. Ask the user to focus the WSL Google Chrome window, then retry. If it still fails after the user says Chrome is foreground, restart the daemon, wait for extension reconnect, then run an `example.com` smoke test before the real task:
  ```bash
  ~/.kimi-webbridge/bin/kimi-webbridge status
  ~/.kimi-webbridge/bin/kimi-webbridge restart
  # extension_connected may be false for ~10-20s immediately after restart
  for i in 1 2 3 4 5 6; do ~/.kimi-webbridge/bin/kimi-webbridge status; sleep 3; done
  curl -sS -X POST http://127.0.0.1:10086/command \
    -H 'Content-Type: application/json' \
    -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true},"session":"smoke"}'
  curl -sS -X POST http://127.0.0.1:10086/command \
    -H 'Content-Type: application/json' \
    -d '{"action":"snapshot","session":"smoke"}'
  ```
  Verified working after daemon restart + reconnect on the user's WSL setup: `navigate(newTab:true)` to `https://example.com`, `snapshot`, Zhihu search navigation, and Zhihu article DOM extraction all succeeded. However, restarting the daemon can also clear the extension's current-window state; if the first post/search works but later calls regress to `No current window`, ask the user to refocus the WSL Chrome window **again after the restart**, then retry the smoke test before continuing. If focus/restart cannot establish a current window, fall back to manually opening the target URL in the browser, then attach with `find_tab` and continue with `snapshot`/`evaluate`. Close the named session afterward.
- **ChatGPT image-generation via real browser**: For ChatGPT behind Cloudflare/login, use Kimi WebBridge with a named session, verify `extension_connected:true`, then navigate to `https://chatgpt.com/` and take a `snapshot`. Do not assume the user is logged in just because the page loads; if the snapshot shows login/free signup, login or ask the user to complete it. For image generation, click the `生成图片` tool/pill first, fill the composer, send, wait for the generated `<img>` (`alt` often begins with `已生成图片` or `src` contains `file_`), then fetch the image bytes in-page via `evaluate` and save them locally. This avoids leaking ChatGPT cookies to shell `curl`.
- **Extension required**: Without it, all tool calls fail silently. User must visit https://www.kimi.com/zh-cn/features/webbridge to install.
- **WeChat/公众号 CAPTCHA boundary**: Kimi WebBridge can verify whether the user's real browser session sees the article body or only `环境异常 / 去验证`. If it only sees the verification page, do not fabricate extraction; ask the user to complete verification or paste/export the article body, then continue ingestion.
- **Screenshots return base64**: Use the helper script at `~/.claude/skills/kimi-webbridge/scripts/screenshot.sh` to save to disk instead.
- **`isTrusted=false`**: Some banking portals and captcha challenges reject synthetic events. This is a fundamental browser automation limitation.
- **Zhihu/Zhuanlan article extraction pattern**: For long logged-in Zhihu articles, use Kimi WebBridge with a named session and `evaluate` to read the DOM rather than screenshots. A reliable selector set is `.Post-RichText, article, .RichText`; extract headings (`h1`-`h4`), paragraphs, lists, blockquotes, code blocks, tables, and image URLs into markdown, write the returned JSON/body to a temp file, then hand it to the wiki ingestion workflow. Close the session after verification. This is especially useful when public fetchers miss content but the user's real browser is logged in.
- **Zhihu own collections vs profile collections**: When the user asks to open “我的收藏夹 / 我收藏的帖子”, start at `https://www.zhihu.com/collections/mine`. Do not rely on `https://www.zhihu.com/people/self/collections` first: in the logged-in browser it can render the public profile collection tab and show stale/limited public collections rather than the private “我创建的收藏夹” view. From `/collections/mine`, extract `a[href*="/collection/"]` and choose the named collection (e.g. `考研经验贴`).
- **Large Kimi batch extraction call budget**: Hermes `execute_code` has a tool-call cap; a loop that calls Kimi via `hermes_tools.terminal()` for many pages can stop mid-batch. For >10-12 browser-command iterations, use a shell/Python script via `terminal()` that calls `curl` with `subprocess.run` directly and writes incremental JSON to `/tmp/...`. This keeps the browser-control loop outside the Hermes tool-call cap while still preserving progress if a page fails.
- **Do not assume one-tab reuse fixes Zhihu navigation**: On the user's WSL Chrome, creating a control tab (`example.com`) can succeed, but reusing that same WebBridge session with `navigate(newTab:false)` to a Zhihu/Zhuanlan URL may hang until the curl timeout and leave the session reporting `tab was closed`, after which later calls can regress to `No current window`. If this happens, stop the batch, report the exact blocker, and ask before taking heavier side effects such as restarting Chrome. Preserve partial search results to `/tmp/...` so the next attempt can resume from selected URLs.
- **Final WSL workaround when Kimi WebBridge tabs/currentWindow stays broken**: On 2026-06-20, after cloning the user's main Chrome profile to `~/.config/google-chrome-cdp`, disabling ordinary extensions in the clone, and confirming Kimi WebBridge v1.10.0 has granted `tabs/debugger/<all_urls>` permissions, WebBridge still returned `find_tab('*://*/*') -> no open tab` and `navigate(newTab:true) -> No current window`. Treat this as a Kimi extension + Chrome 148/WSLg runtime bug, not a user-focus problem. Use the CDP fallback instead: `~/.local/bin/chrome-cdp URL` launches the cloned logged-in profile with `--remote-debugging-address=127.0.0.1 --remote-debugging-port=9222`; `~/.local/bin/cdp-text text URL` navigates and extracts `{title, href, text}` via DevTools Protocol. Verified with `https://example.org/` and logged-in `https://www.zhihu.com/` (title showed `(4 条消息) 首页 - 知乎`, text included 消息/创作中心).
- **Zhihu exact-keyword search batches**: When the user gives short Chinese school/院系 keywords and says to search them directly (e.g. `南软`, `软微`, `浙计`, `科软`), navigate to `https://www.zhihu.com/search?type=content&q=<urlencoded keyword>` exactly. Do not silently add qualifiers like `考研`, `408`, `经验贴`, or full school names before the first pass; those can hide the native high-signal results and violate the intended discovery shape. Batch extraction pattern: for each keyword, open the Zhihu search page, DOM-extract result titles/URLs/snippets, then open selected high-signal posts and extract `.Post-RichText / .RichText / article` bodies into a JSON temp file for downstream wiki ingestion. Close the named session at the end.
- **Sessions**: Always name your session. Different sites → different sessions for isolation.
- **close_session**: Call at task end to clean up browser tabs.

## Agent-side quick path

When a user explicitly asks to use Kimi WebBridge, treat that as a hard routing instruction:

1. Locate/use the binary, normally `~/.kimi-webbridge/bin/kimi-webbridge` (`~/.kimi-webbridge/bin/kimi-webbridge` in the user's WSL profile).
2. Run `~/.kimi-webbridge/bin/kimi-webbridge status`.
3. If status reports `PID file exists but HTTP probe failed`, clear stale state and restart:
   ```bash
   rm -f ~/.kimi-webbridge/daemon.pid
   ~/.kimi-webbridge/bin/kimi-webbridge start
   sleep 3
   ~/.kimi-webbridge/bin/kimi-webbridge status
   ```
4. Proceed only after `running:true` and `extension_connected:true`.
5. Call `POST http://127.0.0.1:10086/command` directly from `terminal()`/a script; do not use Hermes `browser_navigate` as a substitute.
6. Verify with a real extraction (`snapshot` or `evaluate`) from the target site. For Zhihu search, a good smoke test is navigating to `https://www.zhihu.com/search?type=content&q=<urlencoded query>` and evaluating `document.title`, `location.href`, and selected result anchors/snippets.
7. Close the named WebBridge session at the end.

## Verification

```bash
# Check health
~/.kimi-webbridge/bin/kimi-webbridge status

# Navigate to a site
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{"action":"navigate","args":{"url":"https://example.com","newTab":true},"session":"test"}'

# Snapshot to read content
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{"action":"snapshot","session":"test"}'
```
