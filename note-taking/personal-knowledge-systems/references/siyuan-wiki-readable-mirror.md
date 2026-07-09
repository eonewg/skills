# SiYuan readable mirror for the user's filesystem wiki

Use this when the user asks to put the existing `~/wiki` into SiYuan for reading / cross-device access.

## Boundary

- Source of truth remains `~/wiki`.
- SiYuan notebook `the assistant Wiki` is a one-way readable mirror only.
- Do **not** implement or encourage bidirectional sync from SiYuan back into `~/wiki`; that risks corrupting frontmatter, raw hashes, `.manifest.json`, and LLM Wiki v2 derived layers.
- the user explicitly accepts this boundary: “wiki本身就是让你来写的”.

## Recommended import shape

Generate a clean mirror directory, then import into the SiYuan notebook.

Include:
- `README.md` landing page explaining it is a readable mirror
- `index.md`
- `hot.md`
- `log.md`
- `concepts/`
- `entities/`
- `comparisons/`
- `queries/`

Exclude machine/source layers:
- `raw/`
- `facts/`
- `graph/`
- `reports/`
- `scripts/`
- `state/`
- `.manifest.json`
- `SCHEMA.md`

Typical mirror path:

```bash
~/.hermes/out/siyuan-wiki-import
```

## Commands / workflow

1. Verify wiki health first:

```bash
cd ~/wiki
python3 scripts/wiki_lint.py
```

2. Create a timestamped SiYuan backup before bulk import:

```bash
tar -czf ~/SiYuan-backup-before-aki-wiki-import-$(date +%Y%m%d%H%M%S).tar.gz -C ~ SiYuan
```

3. Generate the readable mirror:

```bash
OUT=~/.hermes/out/siyuan-wiki-import
SRC=~/wiki
rm -rf "$OUT"
mkdir -p "$OUT"
python3 - <<'PY'
from pathlib import Path
import shutil, datetime
src=Path('~/wiki')
out=Path('~/.hermes/out/siyuan-wiki-import')
include_top=['index.md','hot.md','log.md']
include_dirs=['concepts','entities','comparisons','queries']
(out/'README.md').write_text(f"""# the assistant Wiki 可读镜像

来源：`~/wiki`
生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是给思源阅读/跨设备查看用的单向镜像，不是源仓库。正式写入、归档、lint、v2 build 仍以 `~/wiki` 为准。

包含：`index.md`、`hot.md`、`log.md`、`concepts/`、`entities/`、`comparisons/`、`queries/`。

排除：`raw/`、`facts/`、`graph/`、`reports/`、`scripts/`、`state/`、`.manifest.json`、`SCHEMA.md`。
""", encoding='utf-8')
for name in include_top:
    p=src/name
    if p.exists(): shutil.copy2(p, out/name)
for d in include_dirs:
    sp=src/d
    if not sp.exists(): continue
    for p in sp.rglob('*.md'):
        dest=out/p.relative_to(src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
print('mirror_md_files', sum(1 for _ in out.rglob('*.md')))
PY
```

4. Create or reuse notebook `the assistant Wiki`:

```bash
siyuan-kernel notebook list -w ~/SiYuan -f json
siyuan-kernel notebook create -w ~/SiYuan --name 'the assistant Wiki' -f json
siyuan-kernel notebook open -w ~/SiYuan --id <notebook_id> -f json
```

5. Import top-level files and directories separately. Importing the whole mirror directory can create an unwanted wrapper document; if that happens, remove the wrapper with `siyuan-kernel document remove --id <id>`.

```bash
NB=<the assistant Wiki notebook id>
BASE=~/.hermes/out/siyuan-wiki-import
for f in README.md index.md hot.md log.md; do
  siyuan-kernel import md -w ~/SiYuan --file "$BASE/$f" --notebook "$NB" -f json
done
for d in concepts entities comparisons queries; do
  siyuan-kernel import md -w ~/SiYuan --file "$BASE/$d" --notebook "$NB" -f json
done
```

6. Verify import:

```bash
siyuan-kernel document list -w ~/SiYuan --notebook "$NB" -f json
siyuan-kernel search 'agent' -w ~/SiYuan --notebook "$NB" -f json
siyuan-kernel search '考研' -w ~/SiYuan --notebook "$NB" -f json
find ~/SiYuan/data/$NB -name '*.sy' | wc -l
du -sh ~/SiYuan/data/$NB
```

Expected from the first import session: roughly 205 `.sy` files after removing the accidental wrapper, with top-level documents/folders `README`, `Wiki Index`, `Hot Context`, `log`, `concepts`, `entities`, `comparisons`, `queries`.

7. Sync SiYuan to S3 after verification:

```bash
siyuan-kernel sync push -w ~/SiYuan -f json
siyuan-kernel sync status -w ~/SiYuan -f json
```

## Pitfalls

- Do not import `raw/` unless the user explicitly asks for source archives in SiYuan; it is noisy and unnecessary for reading.
- Do not run bidirectional sync between SiYuan and `~/wiki`.
- Do not trust `siyuan-kernel import md --file <whole mirror dir>` as the final layout; it may create a wrapper folder. Prefer separate imports.
- After importing, use search verification, not just command success.
