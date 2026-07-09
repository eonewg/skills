# Xiaohongshu via Kimi WebBridge

Use this when the user asks to “看看我的小红书”, browse Xiaohongshu/RedNote, inspect his profile, feed, collections, likes, or extract note content. the user corrected the workflow: default to Kimi WebBridge / his real browser login session first, not the xiaohongshu-mcp server.

## Default path

1. Check Kimi WebBridge health if needed:
   - `~/.kimi-webbridge/bin/kimi-webbridge status`
   - Require `running: true` and `extension_connected: true`.
2. Use a named session such as `xhs-look`.
3. Navigate with Kimi WebBridge to `https://www.xiaohongshu.com/explore` or a provided Xiaohongshu URL.
4. If the user wants “my profile”, extract the profile link from the sidebar anchor whose text is `我`, then navigate to that `/user/profile/...` URL.
5. Use `evaluate` to read DOM text and anchors. Useful extraction pattern:
   - `document.body.innerText` for profile stats and tab text.
   - `a[href*="/explore/"]` for feed/note cards.
   - `a[href*="/user/profile/"]` for authors/profile links.
6. Summarize what was actually visible. Do not claim hidden/private tabs are empty if the page may be blocked by privacy, tab state, or lazy loading; say “网页端当前显示…” instead.

## What to report

For a profile snapshot, capture:
- nickname
- Xiaohongshu ID
- IP location
- bio / school line
- following / followers / likes+collects
- visible tabs and whether notes/collections/likes rendered

For a feed snapshot, capture algorithmic signals rather than every card:
- repeated themes in recommended notes
- obvious interest clusters
- useful links only when the user asks for details

## When to use xiaohongshu-mcp instead

Use the MCP client only as fallback or for explicit API-style automation:
- publishing notes
- search/detail API calls when Kimi WebBridge is unavailable
- server-side batch operations the user explicitly asks for

Do not start with MCP just because this skill is named `xiaohongshu-mcp`; for the user, browser-login fidelity is the default.