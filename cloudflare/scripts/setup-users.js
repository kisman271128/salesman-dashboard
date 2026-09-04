/**
 * setup-users.js
 * Jalankan SEKALI untuk inisialisasi user di Cloudflare KV
 * 
 * Cara pakai:
 *   node scripts/setup-users.js
 * 
 * Lalu copy output dan jalankan via Wrangler:
 *   wrangler kv:key put --binding=DEPO_KV "user:admin" '<json>'
 */

const crypto = require('crypto');

// ─── Konfigurasi User ──────────────────────────────────────────────────────────
// Edit sesuai data salesman kamu

const USERS = [
  // ── ADMIN PUSAT ──────────────────────────────────────
  {
    username: 'admin',
    password: 'r45t4m4n14',
    name: 'Administrator Pusat',
    role: 'admin',
    depo: null,
    region: null,
    active: true
  },

  // ── DEPO TANJUNG (kode: 0172) ────────────────────────
  {
    username: '017210032876',  // ganti NIK
    password: 'sarabakawatanjung',    // bisa seragam atau beda tiap salesman
    name: 'Asman',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210036369',
    password: 'sarabakawatanjung',
    name: 'Muhammad Tamrin',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210037632',
    password: 'sarabakawatanjung',
    name: 'Robianor',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210037897',
    password: 'sarabakawatanjung',
    name: 'Hindra',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210036576',
    password: 'sarabakawatanjung',
    name: 'Muhammad Yasir',
    role: 'admin',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210042423',
    password: 'sarabakawatanjung',
    name: 'Siti Fatimah Hadijah',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210043127',
    password: 'sarabakawatanjung',
    name: 'Mahrita',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
];

// ─── Hash Password ─────────────────────────────────────────────────────────────

function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

// ─── Generate Output ───────────────────────────────────────────────────────────

console.log('='.repeat(60));
console.log('DEPO TANJUNG - Setup Users');
console.log('Copy perintah di bawah dan jalankan di terminal:');
console.log('='.repeat(60));
console.log();

USERS.forEach(user => {
  const { password, ...userWithoutPassword } = user;
  const userData = {
    ...userWithoutPassword,
    passwordHash: hashPassword(password),
    createdAt: new Date().toISOString(),
    lastLogin: null
  };

  const json = JSON.stringify(userData);
  console.log(`# User: ${user.name} (${user.role})`);
  console.log(`wrangler kv:key put --binding=DEPO_KV "user:${user.username}" '${json}'`);
  console.log();
});

console.log('='.repeat(60));
console.log('KREDENSIAL LOGIN:');
console.log('='.repeat(60));
USERS.forEach(user => {
  console.log(`  ${user.username.padEnd(10)} | ${user.password.padEnd(20)} | ${user.role} | ${user.region || 'semua region'}`);
});
console.log();
console.log('⚠️  SIMPAN KREDENSIAL INI DI TEMPAT AMAN. JANGAN COMMIT KE GIT.');
