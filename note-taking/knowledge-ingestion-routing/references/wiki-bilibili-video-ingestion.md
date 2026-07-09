# Wiki Bilibili video ingestion pattern

Use this when the user is sharing a sequence of Bilibili learning videos and the conversation context indicates archiving/continuation (e.g. “这个也是”, “这几个归档了吗”, “只放在 raw 里了？”).

## Expected destination shape

Do not leave valuable Bilibili learning videos only as chat summaries or only as `raw/` transcripts.

Use a two-layer wiki shape:

1. `raw/transcripts/<topic>-<bvid>-<year>.md`
   - Preserve extracted note, metadata, comments, subtitle evidence index, full transcript, note budget, and score.
   - Include source URL, title, author, BVID, ingested date, and final-body sha256.
2. `concepts/<class-topic>.md`
   - Create or patch a reusable concept page that distills the durable knowledge.
   - For a sequence of related videos, prefer one class-level concept page over one formal page per video unless the new video introduces a distinct method.
   - Add new raw paths to `sources:` deliberately.
   - Cross-link adjacent pages when the new concept is a general framework for an existing tactical page.

## Conversation behavior

If the active thread is already an archive/continuation thread, do not pause on every Bilibili link to ask whether to archive. Treat “这个也是” as “process this into the same archive flow.”

When reporting back, explicitly distinguish:

- raw evidence layer: transcript/comments/metadata preserved for traceability
- formal concept layer: the page the user will query/use later

This avoids the recurring ambiguity behind “只放在 raw 里了？”.

## Verification checklist

After writes:

- Run wiki lint and require `issue_count: 0`; warnings should be understood and non-blocking only if unrelated legacy warnings.
- Verify raw sha256 matches the stored final body.
- Verify the concept page lists the raw file in `sources:`.
- Verify the concept page appears in `index.md` exactly once.
- Rebuild/query the wiki v2 layer when available; a query containing the video’s core terms should return the concept page as the first hit.

## Practical note

For long Bilibili videos with only AI subtitles, it is acceptable to use the WSL Chrome CDP login flow to fetch `/x/player/wbi/v2` subtitle URLs, then rerun the archive material step so the archive contains the same normalized subtitle/index layout as ordinary runs.