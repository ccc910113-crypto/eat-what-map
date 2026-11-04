# -*- coding: utf-8 -*-
"""Build the PWA into ~/eat-what-map from the Desktop standalone HTML."""
import os, json, time, shutil
OUT = os.path.expanduser("~/eat-what-map")
SRC = os.path.expanduser("~/Desktop/科技大樓站晚餐地圖.html")
html = open(SRC, encoding="utf-8").read()
ver = time.strftime("%Y%m%d%H%M")

head = """<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#f6f3ee">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#1a1713">
<meta name="description" content="科技大樓站周邊每人 100–300 元的晚餐：文字菜單、豬雞牛魚高蛋白點法、營業狀態與步行路線。">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="晚餐地圖">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
"""
html = html.replace("<title>", head + "<title>", 1)
reg = """<script>
if("serviceWorker" in navigator&&location.protocol==="https:"){addEventListener("load",()=>{navigator.serviceWorker.register("sw.js").catch(()=>{})})}
</script>
"""
html = html.replace("</body>", reg + "</body>", 1)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)

manifest = {
  "name": "科技大樓站晚餐地圖", "short_name": "晚餐地圖",
  "description": "科技大樓站周邊每人 100–300 元的晚餐：文字菜單、豬雞牛魚高蛋白點法、營業狀態與步行路線。",
  "lang": "zh-Hant-TW", "start_url": "./", "scope": "./", "display": "standalone",
  "background_color": "#f6f3ee", "theme_color": "#f6f3ee",
  "id": "./", "categories": ["food","navigation","lifestyle"],
  "shortcuts": [
    {"name": "地圖", "short_name": "地圖", "url": "./#map", "icons": [{"src": "icons/icon-192.png", "sizes": "192x192"}]},
    {"name": "只看營業中", "short_name": "營業中", "url": "./#open", "icons": [{"src": "icons/icon-192.png", "sizes": "192x192"}]}
  ],
  "screenshots": [
    {"src": "screenshots/list-narrow.png", "sizes": "1000x2160", "type": "image/png", "form_factor": "narrow", "label": "店家清單與建議點法"},
    {"src": "screenshots/desktop-wide.png", "sizes": "1440x900", "type": "image/png", "form_factor": "wide", "label": "清單與地圖"}
  ],
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
json.dump(manifest, open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

sw = """// eat-what-map service worker, build %s
const V = "ewm-%s";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"];
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
  if (/wmts\\.nlsc\\.gov\\.tw|arcgisonline\\.com/.test(u.host)) {
    e.respondWith(caches.open(TILE_CACHE).then(c => c.match(r).then(hit => hit || fetch(r).then(res => { if (res.ok || res.type === "opaque") { c.put(r, res.clone()); trim(TILE_CACHE, TILE_MAX); } return res; }))));
    return;
  }
  // libraries & fonts: stale while revalidate
  if (/cdnjs\\.cloudflare\\.com|fonts\\.(googleapis|gstatic)\\.com/.test(u.host) || u.origin === location.origin) {
    e.respondWith(caches.open(V).then(c => c.match(r).then(hit => {
      const net = fetch(r).then(res => { if (res.ok || res.type === "opaque") c.put(r, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    })));
  }
});
""" % (ver, ver)
open(os.path.join(OUT, "sw.js"), "w", encoding="utf-8").write(sw)
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("pwa built", ver)
