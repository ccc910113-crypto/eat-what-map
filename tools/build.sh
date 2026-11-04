#!/bin/sh
# Rebuild the site: data -> merged shops.json -> page -> PWA (index.html, sw.js, manifest)
set -e
cd "$(dirname "$0")"
python3 shops_src.py >/dev/null        # base 9 shops -> base.json
python3 merge.py | tail -1             # + extra_*.json, geocode, QA/copy patches -> shops.json
python3 build.py | tail -1             # template.html -> ~/Desktop/科技大樓站晚餐地圖.html
python3 pwa.py                         # -> ../index.html, ../sw.js, ../manifest.webmanifest
cp shops.json ../data/shops.json
