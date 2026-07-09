#!/usr/bin/env node
// Rebuild TencentDB Memory sqlite-vec tables after changing SiliconFlow Qwen3 embedding model/dimensions.
// Usage:
//   node scripts/reindex-siliconflow-sqlite-vec.mjs \
//     --db ~/.memory-tencentdb/memory-tdai/vectors.db \
//     --config ~/.memory-tencentdb/memory-tdai/tdai-gateway.json \
//     --plugin ~/.memory-tencentdb/tdai-memory-openclaw-plugin \
//     --model Qwen/Qwen3-Embedding-4B \
//     --dimensions 2560
// Stop the memory_tencentdb gateway before running, then restart and verify counts/recall.

import { createRequire } from 'node:module';
import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

function expandHome(p) {
  return p?.startsWith('~/') ? path.join(os.homedir(), p.slice(2)) : p;
}
function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : fallback;
}

const dbPath = expandHome(arg('db', '~/.memory-tencentdb/memory-tdai/vectors.db'));
const cfgPath = expandHome(arg('config', '~/.memory-tencentdb/memory-tdai/tdai-gateway.json'));
const pluginDir = expandHome(arg('plugin', '~/.memory-tencentdb/tdai-memory-openclaw-plugin'));
const expectedModel = arg('model', null);
const expectedDimensions = arg('dimensions', null) ? Number(arg('dimensions')) : null;
const batchSize = Number(arg('batch-size', '32'));

const require = createRequire(import.meta.url);
const sqliteVec = require(path.join(pluginDir, 'node_modules/sqlite-vec'));
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8')).memory.embedding;
const model = cfg.model;
const dimensions = Number(cfg.dimensions);
const baseUrl = cfg.baseUrl.replace(/\/$/, '');
const apiKey = cfg.apiKey;

if (expectedModel && model !== expectedModel) throw new Error(`Unexpected model: config=${model}, expected=${expectedModel}`);
if (expectedDimensions && dimensions !== expectedDimensions) throw new Error(`Unexpected dimensions: config=${dimensions}, expected=${expectedDimensions}`);
if (!apiKey) throw new Error('Missing apiKey in tdai-gateway.json');

function normalize(row) {
  const out = new Float32Array(row.length);
  let sum = 0;
  for (let i = 0; i < row.length; i++) sum += row[i] * row[i];
  const norm = Math.sqrt(sum) || 1;
  for (let i = 0; i < row.length; i++) out[i] = row[i] / norm;
  return out;
}

async function embedBatch(texts, attempt = 1) {
  const res = await fetch(`${baseUrl}/embeddings`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, input: texts, dimensions, encoding_format: 'float' }),
  });
  if (!res.ok) {
    const body = await res.text();
    if (attempt < 4) {
      await new Promise(r => setTimeout(r, 1500 * attempt));
      return embedBatch(texts, attempt + 1);
    }
    throw new Error(`Embedding HTTP ${res.status}: ${body.slice(0, 300)}`);
  }
  const js = await res.json();
  const data = [...(js.data || [])].sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
  if (data.length !== texts.length) throw new Error(`Embedding rows mismatch: got ${data.length}, expected ${texts.length}`);
  return data.map(x => {
    if (!Array.isArray(x.embedding) || x.embedding.length !== dimensions) {
      throw new Error(`Embedding dimension drift: got ${x.embedding?.length}, expected ${dimensions}`);
    }
    return normalize(x.embedding);
  });
}

async function reindexTable(db, kind, rows, textKey, timeKey) {
  const vecTable = kind === 'l1' ? 'l1_vec' : 'l0_vec';
  const insert = db.prepare(`INSERT INTO ${vecTable} (record_id, embedding, ${timeKey}) VALUES (?, ?, ?)`);
  let done = 0;
  for (let i = 0; i < rows.length; i += batchSize) {
    const batch = rows.slice(i, i + batchSize);
    const texts = batch.map(r => (r[textKey] || '').toString().slice(0, 10000));
    const embs = await embedBatch(texts);
    db.exec('BEGIN');
    try {
      for (let j = 0; j < batch.length; j++) {
        insert.run(batch[j].record_id, Buffer.from(embs[j].buffer), batch[j][timeKey] || '');
      }
      db.exec('COMMIT');
    } catch (e) {
      try { db.exec('ROLLBACK'); } catch {}
      throw e;
    }
    done += batch.length;
    console.log(`${kind}: ${done}/${rows.length}`);
  }
}

const db = new DatabaseSync(dbPath, { allowExtension: true });
db.enableLoadExtension(true);
sqliteVec.load(db);
db.exec('PRAGMA busy_timeout = 10000');
db.exec('PRAGMA journal_mode = WAL');

const l1 = db.prepare('SELECT record_id, content, updated_time FROM l1_records ORDER BY record_id ASC').all();
const l0 = db.prepare('SELECT record_id, message_text, recorded_at FROM l0_conversations ORDER BY record_id ASC').all();
console.log(`config: ${model} ${dimensions}D`);
console.log(`source counts: l1=${l1.length} l0=${l0.length}`);

db.exec('DELETE FROM l1_vec');
db.exec('DELETE FROM l0_vec');
await reindexTable(db, 'l1', l1, 'content', 'updated_time');
await reindexTable(db, 'l0', l0, 'message_text', 'recorded_at');

const out = {
  l1_records: db.prepare('SELECT COUNT(*) AS n FROM l1_records').get().n,
  l1_vec_rowids: db.prepare('SELECT COUNT(*) AS n FROM l1_vec_rowids').get().n,
  l0_conversations: db.prepare('SELECT COUNT(*) AS n FROM l0_conversations').get().n,
  l0_vec_rowids: db.prepare('SELECT COUNT(*) AS n FROM l0_vec_rowids').get().n,
  meta: db.prepare("SELECT value FROM embedding_meta WHERE key='embedding_provider_info'").get().value,
};
console.log(JSON.stringify(out, null, 2));
db.close();
