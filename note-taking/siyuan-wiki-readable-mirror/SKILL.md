---
name: siyuan-wiki-readable-mirror
description: Generate a clean one-way readable mirror of the user's filesystem wiki and import it into SiYuan as the `the assistant Wiki` notebook for cross-device reading via SiYuan S3 sync. Use when the user asks to sync/export/mirror `~/wiki` into SiYuan, update the SiYuan the assistant Wiki copy, or make wiki pages available in SiYuan.
---

# SiYuan Wiki Readable Mirror

## Purpose

Create a **one-way readable mirror** from the user's canonical filesystem wiki into SiYuan.

Canonical source of truth stays:

```text
~/wiki
```

SiYuan notebook `the assistant Wiki` is only a reading / cross-device copy. Do **not** treat it as bidirectional sync. Edits in SiYuan are not authoritative and should not be merged back into `~/wiki` unless the user explicitly asks for a manual migration.

## When to use

Use this skill when the user asks to:

- 同步 wiki 到思源
- 更新思源里的 the assistant Wiki
- 把现有 wiki 放进思源
- 让另一台电脑/手机通过思源看 wiki
- 刷新 SiYuan wiki mirror

## Boundary rules

- `~/wiki` remains the only source of truth for the assistant-written knowledge.
- SiYuan `the assistant Wiki` is a generated reading mirror.
- Do not include machine/build layers in SiYuan by default.
- Do not import raw evidence by default; raw files stay in filesystem wiki.
- Do not enable bidirectional sync between SiYuan and `~/wiki`.
- Before mutating SiYuan, create a backup tarball of `~/SiYuan`.

## Included content

Generate a clean mirror containing:

```text
00 the assistant Wiki 首页.md
01 考研驾驶舱.md
02 Agent 工程入口.md
05 最近更新.md
README.md
index.md
hot.md
log.md
concepts/
entities/
comparisons/
queries/
```

The generated `00 the assistant Wiki 首页` homepage is the human-first SiYuan entry. The refresh also generates `01 考研驾驶舱`, `02 Agent 工程入口`, and `05 最近更新` as focused entry pages. All generated entry-page links must be real SiYuan block links (`[title](siyuan://blocks/<id>)`), not raw wiki `[[slug]]`, because imported `[[...]]` can remain plain text when targets are not available during import. The refresh installs/updates the `the assistant Wiki 阅读增强` CSS snippet through `/api/snippet/setSnippet` for lightweight reading polish.

## Excluded content

Do not include these in the readable mirror unless the user explicitly asks:

```text
raw/
facts/
graph/
reports/
scripts/
state/
.manifest.json
SCHEMA.md
archive/
```

## Standard workflow

### Preferred: one-command refresh

A verified wrapper exists in PATH:

```bash
siyuan-wiki-refresh
```

It performs the full flow: wiki lint → rebuild readable mirror → volatile-safe SiYuan backup → replace the existing `the assistant Wiki` notebook → import mirror → smoke-test search → S3 sync push → prune old the assistant Wiki refresh backups. Use this by default.

Backup retention: keep the latest `SiYuan-backup-before-aki-wiki-refresh-*.tar.gz` only, moving older refresh backups to Trash. Do not automatically delete the separate S3-import baseline backup unless the user explicitly asks.

Useful options:

```bash
siyuan-wiki-refresh --no-sync
siyuan-wiki-refresh --no-backup
```

Implementation lives at:

```text
~/.hermes/skills/note-taking/siyuan-wiki-readable-mirror/scripts/refresh_siyuan_wiki_mirror.py
~/.local/bin/siyuan-wiki-refresh
```

### Manual fallback

Use the steps below only when debugging the wrapper.

### 1. Verify wiki health first

```bash
cd ~/wiki
python3 scripts/wiki_lint.py
```

Proceed if `issue_count` is `0`. Existing warnings may be reported, but do not hide them.

### 2. Build the mirror directory

Use this deterministic script:

```bash
set -euo pipefail
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
landing=out/'README.md'
landing.write_text(f"""# the assistant Wiki 可读镜像

来源：`~/wiki`
生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是给思源阅读/跨设备查看用的单向镜像，不是源仓库。正式写入、归档、lint、v2 build 仍以 `~/wiki` 为准。

包含：`index.md`、`hot.md`、`log.md`、`concepts/`、`entities/`、`comparisons/`、`queries/`。

排除：`raw/`、`facts/`、`graph/`、`reports/`、`scripts/`、`state/`、`.manifest.json`、`SCHEMA.md`。
""", encoding='utf-8')
count=1
for name in include_top:
    p=src/name
    if p.exists():
        shutil.copy2(p, out/name)
        count+=1
for d in include_dirs:
    sp=src/d
    if not sp.exists():
        continue
    for p in sp.rglob('*.md'):
        rel=p.relative_to(src)
        dest=out/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,dest)
        count+=1
print('mirror_files', count)
PY
find "$OUT" -type f -name '*.md' | wc -l
du -sh "$OUT"
```

Known successful baseline on 2026-06-30:

```text
201 Markdown files
2.1M mirror directory
```

### 3. Create or reuse SiYuan notebook

List notebooks:

```bash
siyuan-kernel notebook list -w ~/SiYuan -f json
```

If `the assistant Wiki` does not exist:

```bash
siyuan-kernel notebook create -w ~/SiYuan --name 'the assistant Wiki' -f json
```

Open the notebook if it is closed:

```bash
siyuan-kernel notebook open -w ~/SiYuan --id <notebook_id> -f json
```

### 4. Back up SiYuan before import

When the kernel is running, `repo/` and `temp/` can change during `tar` and cause `file changed as we read it`. Prefer a volatile-safe backup that preserves durable data/config and excludes sync/cache layers:

```bash
backup=~/SiYuan-backup-before-aki-wiki-refresh-$(date +%Y%m%d%H%M%S).tar.gz
tar -czf "$backup" \
  --exclude=SiYuan/temp \
  --exclude=SiYuan/repo \
  -C ~ SiYuan
echo "$backup"
```

### 5. Import into SiYuan

Important pitfall: importing the whole mirror directory in one call can create an extra wrapper document such as `siyuan-wiki-import`. Prefer importing top-level files and directories individually.

```bash
NB=<notebook_id>
BASE=~/.hermes/out/siyuan-wiki-import

for f in index.md hot.md log.md; do
  siyuan-kernel import md -w ~/SiYuan --file "$BASE/$f" --notebook "$NB" -f json
done

for d in concepts entities comparisons queries; do
  siyuan-kernel import md -w ~/SiYuan --file "$BASE/$d" --notebook "$NB" -f json
done
```

If testing with `README.md`, import it separately:

```bash
siyuan-kernel import md -w ~/SiYuan --file "$BASE/README.md" --notebook "$NB" -f json
```

If a mistaken wrapper document is created, remove it by document ID:

```bash
siyuan-kernel document remove -w ~/SiYuan --id <wrapper_doc_id> -f json
```

### 6. Verify the import

List top-level documents:

```bash
siyuan-kernel document list -w ~/SiYuan --notebook "$NB" -f json
```

Expected top-level structure:

```text
00 the assistant Wiki 首页
README
Wiki Index
Hot Context
log
concepts
entities
comparisons
queries
```

Expected child counts from the 2026-06-30 baseline:

```text
concepts: 161
entities: 13
comparisons: 2
queries: 21
```

Count local `.sy` files:

```bash
find ~/SiYuan/data/$NB -name '*.sy' | wc -l
du -sh ~/SiYuan/data/$NB ~/.hermes/out/siyuan-wiki-import
```

Known successful baseline after removing the accidental wrapper:

```text
205 .sy files
5.6M ~/SiYuan/data/<the assistant-Wiki-notebook-id>
```

Smoke-test search:

```bash
siyuan-kernel search 'agent' -w ~/SiYuan --notebook "$NB" -f json
siyuan-kernel search '考研' -w ~/SiYuan --notebook "$NB" -f json
```

Known successful baseline:

```text
agent: matchedBlockCount 3858
考研: matchedBlockCount 816
```

### 7. Sync to SiYuan S3

After successful import and verification:

```bash
siyuan-kernel sync push -w ~/SiYuan -f json
siyuan-kernel sync status -w ~/SiYuan -f json
```

Check logs if needed:

```bash
grep -n "repository.go:1865\|uploaded index\|uploaded cloud ref" ~/SiYuan/temp/siyuan.log | tail -80
```

Known successful baseline after the assistant Wiki import:

```text
uploaded cloud ref
files=4324
size=244.56 MB
ufc=210
ucc=207
```

### 8. Clean temporary test files

```bash
rm -rf ~/SiYuan/temp/aki-wiki-import-test \
  /tmp/akiwiki_docs.json \
  /tmp/akiwiki_search_agent.json \
  /tmp/akiwiki_search_kaoyan.json \
  /tmp/siyuan_notebooks.json \
  /tmp/siyuan_create_akiwiki.json 2>/dev/null || true
```

## Pitfalls

- Do not pipe `siyuan-kernel ... | python3` in approval-gated contexts; save JSON to `/tmp/*.json` first, then parse it.
- `siyuan-kernel notebook open` uses `--id`, not `--notebook`.
- Importing the whole directory can create a wrapper document; import files/dirs individually instead.
- Search indexing may need a short delay after import.
- `[[slug]]` is not a reliable clickable format in this mirror. The homepage must be imported last after target docs exist, and `write_linked_homepage_for_notebook()` should rewrite important homepage links to `[title](siyuan://blocks/<id>)`; verification requires `homepage_links_ok: true`.
- SiYuan sync may report a small download during push because it merges repo metadata; verify log lines rather than assuming failure.
- Do not delete backup tarballs unless the user confirms the UI looks normal and wants cleanup.

## User-facing report style

Keep it short. Mention:

- Notebook name: `the assistant Wiki`
- Mirror path: `~/.hermes/out/siyuan-wiki-import`
- Source path remains `~/wiki`
- Counts imported and smoke-test results
- Backup tarball path
- S3 sync status

Avoid Markdown tables in Feishu messages.
