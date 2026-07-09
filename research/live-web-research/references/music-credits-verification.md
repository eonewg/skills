---
name: music-credits-verification
description: Verify composer, lyricist, arranger, producer, and other music credits using structured APIs. Use when the user asks about who wrote/created/performed a song, or any factual music trivia that you're not 100% certain of.
---

# Music Credits Verification

## Trigger

The user asks about composer, lyricist, arranger, producer, band members, release date, or any other factual music detail — especially for Cantopop, Mandopop, or any music you haven't personally verified in this session.

**FIRST RULE: Do not answer from memory alone.** If you're not looking at a verified source right now, you're guessing. Stop and research.

## Primary Method: MusicBrainz API

MusicBrainz is a free, open music database. No API key needed. Works well for Cantopop and Chinese music credits.

### Workflow

**Step 1: Search for the song's Work entry**

```bash
curl -sL "https://musicbrainz.org/ws/2/work?query=%22SONG_TITLE%22&fmt=json" \
  -H "User-Agent: YourAgent/1.0 ( user@example.com )"
```

URL-encode the song title in quotes for exact match. Note: use the traditional/full-form characters for Cantonese songs (e.g. `重複犯錯` not `重复犯错`).

The response contains `works[].relations[]` where:
- `type: "composer"` → composer name in `artist.name`
- `type: "lyricist"` → lyricist name in `artist.name`
- `type: "performance"` → performer (though performance relations point to recordings, not always artist)
- `language: "yue"` → Cantonese

**Step 2: Extract credits from relations**

The `relations` array has entries like:
```json
{
  "type": "composer",
  "artist": { "name": "陳輝陽" }
}
```

Report all relevant relations to the user.

**Step 3: Fallback — Search recording instead**

If `work` search fails, try the recording endpoint:

```bash
curl -sL "https://musicbrainz.org/ws/2/recording?query=recording:%22SONG_TITLE%22%20AND%20artist:%22ARTIST_NAME%22&fmt=json" \
  -H "User-Agent: YourAgent/1.0 ( user@example.com )"
```

### Dead ends to skip

- **Bing search** — completely useless for Chinese music queries; returns dictionary definitions of the characters instead of song info
- **Baidu Baike** — CAPTCHA blocks browser; API returns empty
- **NetEase Music API** — song detail response has no composer/lyricist fields
- **QQ Music search API** — composer info not present in search results
- **iTunes/Apple Music API** — no composer/lyricist in track results
- **Wikipedia** — Cantonese album/song pages often don't exist

### User-agent requirement

MusicBrainz requires a custom `User-Agent` header containing app name and contact info, or it returns 503/rate-limit errors. Use:
`-H "User-Agent: HermesAgent/1.0 ( user@example.com )"`

## Pitfalls

- **Do NOT guess from training data.** This is exactly what the user is frustrated by. If you haven't looked at a verified source in this session, you don't know.
- Cantonese song titles may use traditional characters (重複犯錯 vs 重复犯错). Try both variants if one fails.
- MusicBrainz rate-limits aggressively; if you get "busy" errors, wait 2-3 seconds and retry once.
- The `type` field in `works[].relations[]` distinguishes composer vs lyricist — check both.
- Some songs may appear in multiple releases; the Work entry aggregates all credits across releases.

## Reference

See `references/worked-example.md` for the complete session transcript that led to this skill.
