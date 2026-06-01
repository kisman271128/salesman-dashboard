/**
 * DEPO TANJUNG - Cloudflare Worker
 * API Layer: Auth + Data Access + KV Storage
 * 
 * Routes:
 *   POST /auth/login          → Login salesman, dapat JWT token
 *   GET  /data/:namespace     → Ambil data JSON (perlu token)
 *   PUT  /data/:namespace     → Upload/update data JSON (perlu ADMIN token)
 *   GET  /health              → Health check
 */

// ─── HELPER: Base64 URL ───────────────────────────────────────────────────────

function base64url(str) {
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

function base64urlDecode(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return atob(str);
}

// ─── JWT HELPERS ──────────────────────────────────────────────────────────────

async function signJWT(payload, secret) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const encodedHeader = base64url(JSON.stringify(header));
  const encodedPayload = base64url(JSON.stringify(payload));
  const signingInput = `${encodedHeader}.${encodedPayload}`;

  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signature = await crypto.subtle.sign(
    'HMAC',
    key,
    new TextEncoder().encode(signingInput)
  );

  const encodedSig = base64url(String.fromCharCode(...new Uint8Array(signature)));
  return `${signingInput}.${encodedSig}`;
}

async function verifyJWT(token, secret) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const [encodedHeader, encodedPayload, encodedSig] = parts;
    const signingInput = `${encodedHeader}.${encodedPayload}`;

    const key = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    const sigBytes = Uint8Array.from(base64urlDecode(encodedSig), c => c.charCodeAt(0));
    const valid = await crypto.subtle.verify(
      'HMAC',
      key,
      sigBytes,
      new TextEncoder().encode(signingInput)
    );

    if (!valid) return null;

    const payload = JSON.parse(base64urlDecode(encodedPayload));
    if (payload.exp && Date.now() / 1000 > payload.exp) return null; // expired

    return payload;
  } catch {
    return null;
  }
}

// ─── AES ENKRIPSI ─────────────────────────────────────────────────────────────

async function encryptData(plaintext, secretKey) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await crypto.subtle.importKey(
    'raw',
    await deriveKey(secretKey),
    { name: 'AES-GCM' },
    false,
    ['encrypt']
  );

  const encoded = new TextEncoder().encode(plaintext);
  const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, encoded);

  // Gabung IV + ciphertext → base64
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return btoa(String.fromCharCode(...combined));
}

async function decryptData(encryptedBase64, secretKey) {
  const combined = Uint8Array.from(atob(encryptedBase64), c => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const ciphertext = combined.slice(12);

  const key = await crypto.subtle.importKey(
    'raw',
    await deriveKey(secretKey),
    { name: 'AES-GCM' },
    false,
    ['decrypt']
  );

  const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);
  return new TextDecoder().decode(decrypted);
}

async function deriveKey(secret) {
  const raw = new TextEncoder().encode(secret.padEnd(32, '0').slice(0, 32));
  return raw;
}

// ─── CORS HEADERS ─────────────────────────────────────────────────────────────

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin || '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
}

function jsonResponse(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders('*'),
      ...extraHeaders
    }
  });
}

// ─── ROUTE HANDLERS ───────────────────────────────────────────────────────────

/**
 * POST /auth/login
 * Body: { username: "S001", password: "xxx" }
 * Response: { token: "jwt...", user: {...} }
 */
async function handleLogin(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON body' }, 400);
  }

  const { username, password } = body;
  if (!username || !password) {
    return jsonResponse({ error: 'Username dan password diperlukan' }, 400);
  }

  // Ambil data user dari KV
  const userRaw = await env.DEPO_KV.get(`user:${username.toLowerCase()}`);
  if (!userRaw) {
    return jsonResponse({ error: 'Username atau password salah' }, 401);
  }

  const user = JSON.parse(userRaw);

  // Verifikasi password (hash SHA-256)
  const passwordHash = await hashPassword(password);
  if (passwordHash !== user.passwordHash) {
    return jsonResponse({ error: 'Username atau password salah' }, 401);
  }

  if (!user.active) {
    return jsonResponse({ error: 'Akun tidak aktif' }, 403);
  }

  // Generate JWT (expire 12 jam)
  const payload = {
    sub: username.toLowerCase(),
    name: user.name,
    role: user.role,         // 'salesman' | 'admin'
    region: user.region,     // filter data per region
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (12 * 60 * 60),
  };

  const token = await signJWT(payload, env.JWT_SECRET);

  // Log last login
  await env.DEPO_KV.put(`user:${username.toLowerCase()}`, JSON.stringify({
    ...user,
    lastLogin: new Date().toISOString()
  }));

  return jsonResponse({
    token,
    user: {
      username: username.toLowerCase(),
      name: user.name,
      role: user.role,
      region: user.region
    }
  });
}

/**
 * GET /data/:namespace
 * Header: Authorization: Bearer <token>
 * Namespace contoh: info-stok, visit-outlet, target-sales
 */
async function handleGetData(namespace, request, env) {
  // Verifikasi token
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: 'Token diperlukan' }, 401);
  }

  const token = authHeader.slice(7);
  const payload = await verifyJWT(token, env.JWT_SECRET);
  if (!payload) {
    return jsonResponse({ error: 'Token tidak valid atau sudah expired' }, 401);
  }

  // Ambil data dari KV
  const encryptedData = await env.DEPO_KV.get(`data:${namespace}`);
  if (!encryptedData) {
    return jsonResponse({ error: `Data '${namespace}' tidak ditemukan` }, 404);
  }

  // Decode data: coba AES-GCM dulu (file kecil via Worker),
  // fallback ke plain JSON (file besar via direct KV API)
  let jsonData;
  try {
    const decrypted = await decryptData(encryptedData, env.ENCRYPT_KEY);
    jsonData = JSON.parse(decrypted);
  } catch {
    try {
      jsonData = JSON.parse(encryptedData);
    } catch {
      return jsonResponse({ error: 'Gagal mendekripsi data' }, 500);
    }
  }

  // Filter per region jika bukan admin
  if (payload.role !== 'admin' && payload.region) {
    if (Array.isArray(jsonData)) {
      jsonData = jsonData.filter(item =>
        !item.region || item.region === payload.region
      );
    }
  }

  return jsonResponse({
    namespace,
    updatedAt: await env.DEPO_KV.get(`meta:${namespace}:updatedAt`),
    count: Array.isArray(jsonData) ? jsonData.length : null,
    data: jsonData
  });
}

/**
 * PUT /data/:namespace
 * Header: Authorization: Bearer <admin-token>
 * Body: JSON array/object — support plain JSON atau gzip (Content-Encoding: gzip)
 */
async function handlePutData(namespace, request, env) {
  // Hanya admin yang bisa upload data
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return jsonResponse({ error: 'Token diperlukan' }, 401);
  }

  const token = authHeader.slice(7);
  const payload = await verifyJWT(token, env.JWT_SECRET);
  if (!payload || payload.role !== 'admin') {
    return jsonResponse({ error: 'Akses ditolak. Hanya admin.' }, 403);
  }

  let body;
  try {
    const encoding = (request.headers.get('Content-Encoding') || '').toLowerCase();
    if (encoding === 'gzip') {
      // Decompress gzip payload
      const compressed = await request.arrayBuffer();
      const ds = new DecompressionStream('gzip');
      const writer = ds.writable.getWriter();
      const reader = ds.readable.getReader();
      writer.write(new Uint8Array(compressed));
      writer.close();
      const chunks = [];
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
      }
      const total = chunks.reduce((acc, c) => acc + c.length, 0);
      const merged = new Uint8Array(total);
      let offset = 0;
      for (const c of chunks) { merged.set(c, offset); offset += c.length; }
      body = JSON.parse(new TextDecoder().decode(merged));
    } else {
      body = await request.json();
    }
  } catch {
    return jsonResponse({ error: 'Invalid JSON body' }, 400);
  }

  // Enkripsi dan simpan ke KV
  const encrypted = await encryptData(JSON.stringify(body), env.ENCRYPT_KEY);
  const now = new Date().toISOString();

  await env.DEPO_KV.put(`data:${namespace}`, encrypted);
  await env.DEPO_KV.put(`meta:${namespace}:updatedAt`, now);
  await env.DEPO_KV.put(`meta:${namespace}:uploadedBy`, payload.sub);
  await env.DEPO_KV.put(`meta:${namespace}:count`, String(Array.isArray(body) ? body.length : 1));

  return jsonResponse({
    success: true,
    namespace,
    count: Array.isArray(body) ? body.length : 1,
    updatedAt: now,
    uploadedBy: payload.sub
  });
}

// ─── UTILS ────────────────────────────────────────────────────────────────────

async function hashPassword(password) {
  const encoded = new TextEncoder().encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
  return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ─── MAIN HANDLER ─────────────────────────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders('*') });
    }

    // Health check
    if (path === '/health' && method === 'GET') {
      return jsonResponse({ status: 'ok', ts: new Date().toISOString() });
    }

    // Auth routes
    if (path === '/auth/login' && method === 'POST') {
      return handleLogin(request, env);
    }

    // Data routes
    const dataMatch = path.match(/^\/data\/([a-zA-Z0-9._-]+)$/);
    if (dataMatch) {
      const namespace = dataMatch[1];
      if (method === 'GET') return handleGetData(namespace, request, env);
      if (method === 'PUT') return handlePutData(namespace, request, env);
    }

    return jsonResponse({ error: 'Route tidak ditemukan' }, 404);
  }
};