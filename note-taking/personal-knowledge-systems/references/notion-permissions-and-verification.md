# Notion permissions and verification

Useful pattern from session work.

## What a shared integration can actually see

A Notion integration does not gain workspace-wide access. It can only access pages/databases that are shared to it.

The safest structure is:

- one parent page used as an agent workspace
- child pages and databases nested under it
- integration connected to that parent page

This works better than a "navigation page" full of links to unrelated pages elsewhere.

## Critical nuance

A link on a page is not the same as permission.

If page A links to page B, but page B is elsewhere and not shared to the integration, the API may find page A but still fail to read page B.

## Minimal verification flow

### Verify token

```bash
curl -s https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Expected shape: a bot user object.

### Find the shared page

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query":"the assistant"}'
```

### Confirm child content is readable

```bash
curl -s "https://api.notion.com/v1/blocks/<page_id>/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Look for `child_page` and `child_database` blocks to verify the parent page exposes the intended workspace structure.
