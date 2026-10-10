/* ============================================================
   UniBus - Service Worker
   Version : 1.0.0
   ⚠️  NE JAMAIS CACHER : /admin, /user/login, /user/register,
       /user/logout, /payements, toute requête POST/PUT/DELETE
============================================================ */

const CACHE_VERSION  = 'unibus-v1.0.0';
const STATIC_CACHE   = `${CACHE_VERSION}-static`;   // icônes, CSS, JS, CDN
const PAGES_CACHE    = `${CACHE_VERSION}-pages`;    // pages HTML consultées
const API_CACHE      = `${CACHE_VERSION}-api`;      // positions bus

/* ============================================================
   1. ROUTES À NE JAMAIS CACHER (blocklist)
   ============================================================ */
const NEVER_CACHE_PATTERNS = [
  /^\/admin\//,           // Django admin
  /^\/user\/login/,       // Login
  /^\/user\/register/,    // Register
  /^\/user\/logout/,      // Logout
  /^\/payements\//,       // Paiements (sécurité critique)
  /^\/api\/auth\//,       // API auth (si tu en as)
];

/* ============================================================
   2. ROUTES DE PAGES HTML (Network First + fallback cache)
   ============================================================ */
const PAGES_PATTERNS = [
  /^\/$/,                 // student_list
  /^\/student\/map\//,    // student_map
  /^\/driver\/$/,         // driver_list
  /^\/driver\/dashboard\//, // driver_dashboard
  /^\/user\/dashboard\//, // dashboard
];

/* ============================================================
   3. ROUTES API (Network First avec timeout court)
   ============================================================ */
const API_PATTERNS = [
  /^\/api\//,
  /\/bus\//,
  /\/position\//,
  /\/positions\//,
  /\/gps\//,
];

/* ============================================================
   4. RESSOURCES À PRÉCACHER
   ============================================================ */
const PRECACHE_URLS = [
  '/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/daisyui@4.4.19/dist/full.min.css',
  'https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
];

/* ============================================================
   HELPERS
   ============================================================ */
function matchesAny(url, patterns) {
  return patterns.some((re) => re.test(url.pathname));
}

function isCDN(url) {
  return (
    url.hostname.includes('cdn') ||
    url.hostname.includes('jsdelivr') ||
    url.hostname.includes('cloudflare') ||
    url.hostname.includes('fontawesome') ||
    url.hostname.includes('googleapis')
  );
}

/* ============================================================
   INSTALL
   ============================================================ */
self.addEventListener('install', (event) => {
  console.log('🔧 [SW] Installation...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then(async (cache) => {
      // Précache chaque URL indépendamment pour ne pas tout casser si une échoue
      await Promise.all(
        PRECACHE_URLS.map(async (url) => {
          try {
            await cache.add(new Request(url, { credentials: 'omit' }));
          } catch (err) {
            console.warn('⚠️ [SW] Précache échoué pour :', url, err);
          }
        })
      );
      console.log('📦 [SW] Précache terminé');
    }).then(() => self.skipWaiting())
  );
});

/* ============================================================
   ACTIVATE — nettoyage des vieux caches
   ============================================================ */
self.addEventListener('activate', (event) => {
  console.log('🚀 [SW] Activation...');
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k.startsWith('unibus-') && !k.startsWith(CACHE_VERSION))
          .map((k) => {
            console.log('🗑️ [SW] Suppression cache obsolète :', k);
            return caches.delete(k);
          })
      )
    ).then(() => self.clients.claim())
  );
});

/* ============================================================
   FETCH — Routeur de stratégies
   ============================================================ */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  /* --- Ignorer : non-GET, chrome-extension, devtools --- */
  if (request.method !== 'GET') return;
  if (url.protocol === 'chrome-extension:') return;
  if (url.protocol === 'ws:' || url.protocol === 'wss:') return;

  /* --- Ignorer : requêtes cross-origin non-CDN --- */
  // (laisse le navigateur gérer les autres domaines)
  if (url.origin !== self.location.origin && !isCDN(url)) return;

  /* === 1) BLOCKLIST : NE JAMAIS CACHER === */
  if (matchesAny(url, NEVER_CACHE_PATTERNS)) {
    // On laisse passer au réseau, sans toucher au cache
    return; // ← pas de event.respondWith() → comportement navigateur normal
  }

  /* === 2) RESSOURCES STATIQUES & CDN : Cache First === */
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/') || isCDN(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  /* === 3) API : Network First avec timeout court === */
  if (matchesAny(url, API_PATTERNS)) {
    event.respondWith(networkFirstWithTimeout(request, API_CACHE, 4000));
    return;
  }

  /* === 4) PAGES HTML : Network First + fallback cache === */
  if (matchesAny(url, PAGES_PATTERNS) || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkFirst(request, PAGES_CACHE, true));
    return;
  }

  /* === 5) Par défaut : Network Only (sécurité) === */
  // On ne fait rien → le navigateur gère, rien n'est mis en cache
});

/* ============================================================
   STRATÉGIES
   ============================================================ */

/** Cache First — pour les assets statiques */
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response && response.status === 200 && response.type !== 'opaqueredirect') {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    console.warn('❌ [SW] cacheFirst échec :', request.url);
    return new Response('', { status: 504, statusText: 'Offline' });
  }
}

/** Network First — pour les pages HTML */
async function networkFirst(request, cacheName, htmlFallback = false) {
  try {
    const response = await fetch(request);
    // On ne cache QUE les réponses 200 (pas les redirects 302/401)
    if (response && response.status === 200 && response.type === 'basic') {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) {
      console.log('📦 [SW] Fallback cache :', request.url);
      return cached;
    }

    if (htmlFallback && request.headers.get('accept')?.includes('text/html')) {
      return new Response(
        `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
         <meta name="viewport" content="width=device-width,initial-scale=1">
         <title>Hors-ligne - UniBus</title>
         <style>body{font-family:system-ui;background:#f8fafc;color:#0f172a;
         display:flex;align-items:center;justify-content:center;min-height:100vh;
         margin:0;padding:20px;text-align:center}
         .card{background:#fff;padding:32px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,.08);max-width:360px}
         h1{font-size:22px;margin:16px 0 8px}
         p{color:#64748b;font-size:14px;line-height:1.6}
         button{margin-top:20px;background:#059669;color:#fff;border:none;padding:12px 24px;
         border-radius:10px;font-weight:600;cursor:pointer;font-size:14px}
         </style></head><body>
         <div class="card">
           <div style="font-size:48px">📡</div>
           <h1>Vous êtes hors-ligne</h1>
           <p>Cette page n'est pas encore disponible en cache. Reconnectez-vous pour y accéder.</p>
           <button onclick="location.reload()">Réessayer</button>
         </div></body></html>`,
        { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
      );
    }

    return new Response('', { status: 504, statusText: 'Offline' });
  }
}

/** Network First avec timeout — pour les APIs temps réel */
async function networkFirstWithTimeout(request, cacheName, timeoutMs = 4000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(request, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (response && response.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    clearTimeout(timeoutId);
    const cached = await caches.match(request);
    if (cached) {
      console.log('⚡ [SW] API servie depuis le cache (timeout/offline) :', request.url);
      return cached;
    }
    return new Response(
      JSON.stringify({ error: 'offline', message: 'Données indisponibles hors-ligne' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

/* ============================================================
   MESSAGES
   ============================================================ */
self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
  if (event.data?.type === 'CLEAR_CACHES') {
    caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
  }
});

/* ============================================================
   PUSH NOTIFICATIONS (bonus)
   ============================================================ */
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};
  event.waitUntil(
    self.registration.showNotification(data.title || 'UniBus', {
      body: data.body || 'Nouvelle notification',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-96x96.png',
      vibrate: [100, 50, 100],
      data: { url: data.url || '/' },
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url));
});