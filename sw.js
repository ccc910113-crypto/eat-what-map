// eat-what-map service worker, build 202611041924
const V = "ewm-202611041924";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];
const TILE_CACHE = "ewm-tiles", TILE_MAX = 800;
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V && k !== TILE_CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
async function trim(name, max) { const c = await caches.open(name); const ks = await c.keys(); for (let i = 0; i < ks.length - max; i++) await c.delete(ks[i]); }
self.addEventListener("fetch", e => {
  const r = e.request; if (r.method !== "GET") return;
  const u = new URL(r.url);
  // pages: network first so new data shows up, cache as offline fallback
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(V).then(c => c.put("index.html", cp)); return res; })
      .catch(() => caches.match("index.html")));
    return;
  }
  // map tiles: cache first, capped
  if (/wmts\.nlsc\.gov\.tw|arcgisonline\.com/.test(u.host)) {
    e.respondWith(caches.open(TILE_CACHE).then(c => c.match(r).then(hit => hit || fetch(r).then(res => { if (res.ok || res.type === "opaque") { c.put(r, res.clone()); trim(TILE_CACHE, TILE_MAX); } return res; }))));
    return;
  }
  // libraries & fonts: stale while revalidate
  if (/cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com/.test(u.host) || u.origin === location.origin) {
    e.respondWith(caches.open(V).then(c => c.match(r).then(hit => {
      const net = fetch(r).then(res => { if (res.ok || res.type === "opaque") c.put(r, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    })));
  }
});
