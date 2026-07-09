# Worked Example: Verifying Composer of Leo Ku's 重複犯錯

## Session Context

User asked me to interpret 古巨基《重复犯错》. I answered from memory, saying composer was 雷颂德. User corrected me — it's actually 陈辉阳.

This file documents the verification path that eventually confirmed the correct answer.

## Verification Attempts (in order tried)

### 1. Baidu Baike (FAILED)
- `https://baike.baidu.com/item/重複犯錯/10517713` → 404
- Used browser, blocked by CAPTCHA

### 2. NetEase Music API (FAILED)
- `https://music.163.com/song?id=64280` → couldn't find
- `http://music.163.com/api/song/detail/?id=167608&ids=[167608]` → empty response
- `https://music.163.com/api/search/get/web?s=古巨基+重复犯错&type=1` → found song ID 401538348
- `https://music.163.com/api/song/detail?id=401538348&ids=[401538348]` → song detail returned but no composer/lyricist fields at all

### 3. QQ Music API (PARTIAL)
- `https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?key=古巨基+重复犯错` → found song MID: 003qLQA53VnL4K, song ID: 167608, album: Human 我生
- `https://u.y.qq.com/cgi-bin/musicu.fcg` → GetSongDetail → empty
- Composer info not present in QQ search API results

### 4. iTunes / Apple Music API (PARTIAL)
- `https://itunes.apple.com/search?term=古巨基+重複犯錯&entity=song` → found track, album: 我生, track number: 5, but NO composer field

### 5. Wikipedia (FAILED)
- `https://en.wikipedia.org/wiki/Human_我生` → page doesn't exist
- `https://zh.wikipedia.org/wiki/Human_我生` → page doesn't exist
- `https://zh.wikipedia.org/wiki/古巨基` → page exists but too large, discography sections not easy to navigate by browser tools

### 6. Bing Search (FAILED — completely useless)
- Multiple queries all returned dictionary definitions of the Chinese characters instead of song results
- Even with `cc=hk`, `setlang=zh-HK`, the Chinese query gets interpreted character-by-character

### 7. Discogs (FAILED)
- API returned 0 results for "Leo Ku 重複犯錯"

### 8. MusicBrainz — Work Search (SUCCESS ✅)

```bash
curl -sL "https://musicbrainz.org/ws/2/work?query=%22%E9%87%8D%E5%A4%8D%E7%8A%AF%E9%94%99%22&fmt=json" \
  -H "User-Agent: HermesAgent/1.0 ( user@example.com )"
```

Response contains:
- Work ID: `ac30fa80-b933-46a9-9090-7fe54e1b0543`
- Title: 重複犯錯
- Language: yue (Cantonese)
- Relations:
  - **composer**: 陳輝陽 (Chan, Fai Young Keith)
  - **lyricist**: 林夕 (Lin, Xi)
  - **performance**: tied to multiple recordings

### Key Lessons
1. **MusicBrainz Work search is the canonical source** — starts with work (the abstract song), then follows relations to composer/lyricist
2. Use **traditional characters** for Cantonese song titles (重複犯錯 not 重复犯错)
3. Most other APIs (NetEase, QQ, Apple, Wikipedia, Baidu) don't surface composer info
4. Bing is hopeless for Chinese music queries
5. Always include a proper `User-Agent` with MusicBrainz or it rate-limits