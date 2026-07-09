# Migrating Hermes Built-in Memory into TencentDB Agent Memory

Session-derived workflow for moving stable facts from Hermes `MEMORY.md` / `USER.md` into TencentDB Agent Memory after the gateway is configured.

## Source files

```text
~/.hermes/memories/MEMORY.md
~/.hermes/memories/USER.md
```

Read both files in a main/direct session only. Distill stable facts and operational preferences; do not migrate temporary task state.

## Preferred path: normal capture first

Use `/capture` to feed curated memory chunks into a dedicated migration session so L0/L1/L2 pipeline behavior is exercised.

```bash
python3 - <<'PY'
import requests, time
base = 'http://127.0.0.1:8420'
session_key = 'builtin-memory-migration-YYYYMMDD'
chunks = [
  ('identity', '请记住：用户姓名是 the user，称呼偏好是 the user。'),
]
for title, content in chunks:
    r = requests.post(base + '/capture', json={
        'session_key': session_key,
        'session_id': session_key,
        'user_content': f'【内置记忆迁移｜{title}】\n{content}',
        'assistant_content': f'已接收并迁移“{title}”相关长期记忆。',
    }, timeout=30)
    print(title, r.status_code, r.text[:200])
    r.raise_for_status()
    time.sleep(0.3)
requests.post(base + '/session/end', json={'session_key': session_key}, timeout=240).raise_for_status()
PY
```

If `requests` unexpectedly connects to a local proxy (for example `127.0.0.1:7897`) instead of the gateway, bypass proxies explicitly:

```python
requests.post(url, json=payload, timeout=30, proxies={'http': None, 'https': None})
```

For curl probes, prefer:

```bash
curl --noproxy '*' -sS --max-time 5 http://127.0.0.1:8420/health
```

## Fallback path: direct L1 import for critical stable preferences

LLM extraction can under-extract curated memory chunks. If important stable facts are missing after waiting for L1, insert distilled records directly into `l1_records` and `l1_fts`.

Database:

```text
~/.memory-tencentdb/memory-tdai/vectors.db
```

Tables:

```text
l1_records(record_id, content, type, priority, scene_name, session_key, session_id,
           timestamp_str, timestamp_start, timestamp_end, created_time, updated_time, metadata_json)
l1_fts(content, content_original, record_id, type, priority, scene_name,
       session_key, session_id, timestamp_str, timestamp_start, timestamp_end, metadata_json)
```

Direct imports should:

- Use deterministic `record_id` prefix, e.g. `import_builtin_YYYYMMDD_001`.
- Use `type='persona'` for user facts and `type='instruction'` for operating rules.
- Use high priority, e.g. `90`, for durable preferences.
- Put raw display text in `content_original`.
- Put `content + keywords` in FTS `content` so Chinese/English key phrases are searchable even without vector hits.
- Store provenance in `metadata_json`, e.g. source path and imported timestamp.

Skeleton:

```python
import sqlite3, json, datetime
path = '~/.memory-tencentdb/memory-tdai/vectors.db'
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
records = [
    ('persona', '用户姓名是 the user（<user>），称呼偏好是 the user。', '身份 用户 姓名 the user <user> 称呼'),
]
con = sqlite3.connect(path, timeout=30)
cur = con.cursor()
cur.execute('BEGIN')
for idx, (typ, content, keywords) in enumerate(records, 1):
    rid = f'import_builtin_YYYYMMDD_{idx:03d}'
    meta = json.dumps({'source': 'Hermes builtin MEMORY.md/USER.md migration', 'keywords': keywords}, ensure_ascii=False)
    cur.execute('''INSERT INTO l1_records
      (record_id,content,type,priority,scene_name,session_key,session_id,timestamp_str,timestamp_start,timestamp_end,created_time,updated_time,metadata_json)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
      ON CONFLICT(record_id) DO UPDATE SET content=excluded.content,type=excluded.type,priority=excluded.priority,scene_name=excluded.scene_name,session_key=excluded.session_key,session_id=excluded.session_id,timestamp_str=excluded.timestamp_str,timestamp_start=excluded.timestamp_start,timestamp_end=excluded.timestamp_end,updated_time=excluded.updated_time,metadata_json=excluded.metadata_json''',
      (rid, content, typ, 90, 'Hermes 内置记忆迁移', 'builtin-memory-direct-import-YYYYMMDD', 'builtin-memory-direct-import-YYYYMMDD', now, now, now, now, now, meta))
    cur.execute('DELETE FROM l1_fts WHERE record_id=?', (rid,))
    cur.execute('''INSERT INTO l1_fts
      (content,content_original,record_id,type,priority,scene_name,session_key,session_id,timestamp_str,timestamp_start,timestamp_end,metadata_json)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
      (content + ' ' + keywords, content, rid, typ, 90, 'Hermes 内置记忆迁移', 'builtin-memory-direct-import-YYYYMMDD', 'builtin-memory-direct-import-YYYYMMDD', now, now, now, meta))
con.commit()
```

## Verification

Use memory search for representative facts:

- `<exam-target> 考研科目 408`
- `飞书任务 截止时间 23:59 assign 考研清单`
- `新会话开场白 🧐 emoji 规则`
- `王者荣耀 打野 镜 露娜 宗师`

Expected: returned L1 records include the migrated `persona` / `instruction` entries from scene `Hermes 内置记忆迁移`.

## Pitfalls

- Do not rely on one LLM extraction pass for full coverage of a curated profile; it may extract only a subset.
- `/session/end` can take longer than 30s while L1/L2 tasks run; use a longer timeout.
- Never echo API keys while printing config or scripts.
