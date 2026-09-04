/**
 * shard-catpelanggan.js
 * Split data/d.catpelanggan.json (flat, JSONL) into per-salesman shards,
 * matching the same "d.catpelanggan.<szEmployeeId>" KV key pattern that
 * visit_cat.html requests (mirrors how d.skupelanggan.<szEmployeeId> works).
 *
 * d.catpelanggan.json only has `id_pelanggan` (outlet id) — it has no
 * szEmployeeId of its own — so ownership is resolved via data/d.details.json
 * (id_pelanggan -> szEmployeeId). A "Mix" outlet can map to two employees
 * (e.g. one Arjuna rep + one Bima rep sharing the same outlet); both get
 * the outlet's full category rows, since the `Tim` field is ignored here
 * per instruction (it was only a reference used while building the json).
 *
 * Cara pakai:
 *   node cloudflare/scripts/shard-catpelanggan.js
 *
 * Ini hanya menulis file JSON lokal ke cloudflare/kv-upload/. Upload
 * sebenarnya ke KV dijalankan manual lewat wrangler (lihat output di akhir).
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DETAILS_PATH = path.join(ROOT, 'data', 'd.details.json');
const CATPELANGGAN_PATH = path.join(ROOT, 'data', 'd.catpelanggan.json');
const OUT_DIR = path.join(__dirname, '..', 'kv-upload');

function readJSONL(filePath) {
  return fs.readFileSync(filePath, 'utf8')
    .trim()
    .split('\n')
    .filter(line => line.trim() !== '')
    .map(line => JSON.parse(line));
}

function main() {
  const details = readJSONL(DETAILS_PATH);
  const catpelanggan = readJSONL(CATPELANGGAN_PATH);

  // id_pelanggan -> Set of szEmployeeId
  const ownerMap = new Map();
  for (const d of details) {
    const id = (d.id_pelanggan || '').toString().trim();
    const emp = (d.szEmployeeId || '').toString().trim();
    if (!id || !emp) continue;
    if (!ownerMap.has(id)) ownerMap.set(id, new Set());
    ownerMap.get(id).add(emp);
  }

  const byEmployee = new Map();
  let orphanCount = 0;

  for (const record of catpelanggan) {
    const id = (record.id_pelanggan || '').toString().trim();
    const owners = ownerMap.get(id);
    if (!owners || owners.size === 0) {
      orphanCount++;
      continue;
    }
    for (const emp of owners) {
      if (!byEmployee.has(emp)) byEmployee.set(emp, []);
      byEmployee.get(emp).push(record);
    }
  }

  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  console.log('='.repeat(70));
  console.log('SHARD d.catpelanggan PER SALESMAN');
  console.log('='.repeat(70));
  console.log(`Total records sumber : ${catpelanggan.length}`);
  console.log(`Orphan (outlet tidak ada di d.details.json): ${orphanCount}`);
  console.log(`Jumlah salesman dengan data: ${byEmployee.size}`);
  console.log();

  const commands = [];

  for (const [empId, records] of [...byEmployee.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
    const fileName = `d.catpelanggan.${empId}.json`;
    const filePath = path.join(OUT_DIR, fileName);
    fs.writeFileSync(filePath, JSON.stringify(records));

    const kvKey = `data:d.catpelanggan.${empId}`;
    const relPath = path.relative(process.cwd(), filePath).replace(/\\/g, '/');
    const cmd = `wrangler kv key put "${kvKey}" --binding=DEPO_KV --path "${relPath}" --remote`;
    commands.push(cmd);

    console.log(`  ${empId} -> ${records.length} records -> ${fileName}`);
  }

  console.log();
  console.log('='.repeat(70));
  console.log('JALANKAN PERINTAH BERIKUT DARI FOLDER cloudflare/ (butuh login wrangler):');
  console.log('='.repeat(70));
  console.log();
  commands.forEach(cmd => console.log(cmd));
  console.log();
  console.log('⚠️  --remote menulis ke KV production. Pastikan sudah `wrangler login`');
  console.log('    dan binding DEPO_KV di wrangler.toml menunjuk namespace yang benar.');
}

main();
