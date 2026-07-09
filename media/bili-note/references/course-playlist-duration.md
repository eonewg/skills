# Bilibili course playlist duration reconnaissance

Use this when the user asks how long a course/playlist is, or how long each chapter/part takes.

## Durable workflow

1. If the user explicitly asks to search Zhihu, run the Zhihu search skill first for qualitative opinions and planning advice, but do not use Zhihu snippets as the source of truth for exact durations.
2. Find the closest original course/playlist source, usually Bilibili. Prefer official uploads, but mirrored playlists can still provide useful metadata when clearly labeled as mirrors.
3. Use `scripts/extract_bilibili.py <BVID> --out <tmpdir> --parts all --force` to fetch Bilibili metadata. The returned `metadata.json` includes `data.pages[].duration` in seconds and `data.pages[].part` titles.
4. Compute total time from `pages[].duration`, not from search snippets. If the source only exposes generic part names such as `基础精讲-1~12`, say that chapter mapping is inferred rather than directly titled.
5. Cross-check with web/Bilibili page snapshots or search result snippets when possible. Be wary of partial mirrors: a playlist title may say “完整版” while metadata exposes only some parts, or some parts may be mislabeled/duplicated.
6. For study planning, report both raw duration and realistic study time:
   - pure 1.5x listening = total / 1.5
   - pure 2x listening = total / 2
   - with notes/pauses/exercises, use a higher practical estimate and label it as planning estimate.

## Output shape

- Lead with the total duration.
- Then list per-part or per-chapter durations in bullets, not Markdown tables for Feishu chat.
- Separate verified facts from inferred chapter grouping.
- Cite source type briefly, e.g. “B站 metadata says 12 parts totaling …; chapter split below is inferred from the six probability modules.”

## Example calculation pattern

```python
import json
meta = json.load(open('/tmp/course/metadata.json'))['data']
secs = [p['duration'] for p in meta['pages']]
print(sum(secs))
for p in meta['pages']:
    print(p['page'], p['duration'], p['part'])
```
