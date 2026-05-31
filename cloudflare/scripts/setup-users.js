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
    password: 'rastamania271128',
    name: 'Administrator Pusat',
    role: 'admin',
    depo: null,
    region: null,
    active: true
  },

  // ── DEPO TANJUNG (kode: 0172) ────────────────────────
  {
    username: '017210032876',  // ganti NIK
    password: 'sarabakawa2026',    // bisa seragam atau beda tiap salesman
    name: 'Asman',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210036369',
    password: 'sarabakawa2026',
    name: 'Muhammad Tamrin',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210037632',
    password: 'sarabakawa2026',
    name: 'Robianor',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210037897',
    password: 'sarabakawa2026',
    name: 'Hindra',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210041467',
    password: 'sarabakawa2026',
    name: 'Doli Purnama Sari',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210042412',
    password: 'sarabakawa2026',
    name: 'Muhammad Rizky Algifari',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017210042423',
    password: 'sarabakawa2026',
    name: 'Siti Fatimah Hadijah',
    role: 'salesman',
    depo: '0172',
    region: 'KALIMANTAN',
    active: true
  },
  {
    username: '017212345678',
    password: 'sarabakawa2026',
    name: 'Muhammad Syech',
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
