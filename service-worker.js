// Service Worker untuk Sales Performance Dashboard
const CACHE_NAME = 'sales-dashboard-v1';
const urlsToCache = [
  './',
  './index.html',
  './dashboard.html',
  './performance_all.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

// Install Service Worker
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Service Worker: Caching files');
        // Cache files one by one to handle failures gracefully
        const cachePromises = urlsToCache.map(url => {
          return cache.add(url).catch(err => {
            console.warn(`⚠️ Could not cache ${url}:`, err.message);
            return Promise.resolve(); // Continue even if one file fails
          });
        });
        return Promise.all(cachePromises);
      })
      .then(() => {
        console.log('✅ Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch(err => {
        console.error('❌ Service Worker installation failed:', err);
      })
  );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker: Activation complete');
      return self.clients.claim();
    })
  );
});

// Fetch Strategy: Network First, Fall back to Cache
self.addEventListener('fetch', (event) => {
  // Only handle HTTP/HTTPS requests (ignore chrome-extension, chrome:, about:, etc)
  if (!event.request.url.startsWith('http')) {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Only cache successful responses
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        
        // Clone the response
        const responseToCache = response.clone();
        
        // Cache the fetched response
        caches.open(CACHE_NAME)
          .then((cache) => {
            cache.put(event.request, responseToCache);
          })
          .catch((err) => {
            console.warn('⚠️ Cache put failed:', err);
          });
        
        return response;
      })
      .catch(() => {
        // Network failed, try cache
        return caches.match(event.request)
          .then((response) => {
            if (response) {
              console.log('📦 Serving from cache:', event.request.url);
              return response;
            }
            
            // If not in cache, return a custom offline page (optional)
            if (event.request.destination === 'document') {
              return caches.match('./index.html');
            }
          });
      })
  );
});

// Handle messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('📱 Service Worker loaded successfully');