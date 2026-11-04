# -*- coding: utf-8 -*-
"""Look up shops on Google Maps through the local Chrome (chrome-local, 127.0.0.1:9222).

Usage: python3 gmaps_check.py out.json "query 1" "query 2" ...
Per shop it records: place name, rating, review count, permanently-closed flag,
structured opening hours, relative date of the newest visible reviews, and
online-ordering links (Uber Eats / foodpanda). One tab, 2-3 s pauses, each
shop in its own try/except, results appended so it can be resumed.
"""
import json, sys, time, random, os, urllib.parse
from playwright.sync_api import sync_playwright

out, queries = sys.argv[1], sys.argv[2:]
res = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}

JS = r"""() => {
  const t = document.body.innerText;
  const h1 = document.querySelector('h1');
  const hours = [...document.querySelectorAll('[aria-label*="複製營業時間"]')].map(e => e.getAttribute('aria-label').replace(/, 複製營業時間$/, ''));
  const rating = (t.match(/\n(\d\.\d)\n\(([\d,]+)\)/) || []);
  const rel = [...t.matchAll(/\n(\d+ (?:天|週|個月|年)前|[一二三四五六七八九十]+ ?(?:天|週|個月|年)前)\n/g)].map(m => m[1]).slice(0, 8);
  return {
    place: h1 ? h1.innerText.trim() : null,
    url: location.href.split('?')[0],
    rating: rating[1] || null, reviews: rating[2] || null,
    closed: /永久停業|暫時停業/.test(t) ? (t.match(/永久停業|暫時停業/)[0]) : null,
    hours, recent_reviews: rel,
    has_order: /線上點餐/.test(t),
  };
}"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    page = ctx.new_page()
    for q in queries:
        if q in res and not res[q].get("error"):
            continue
        try:
            page.goto("https://www.google.com/maps/search/" + urllib.parse.quote(q) + "/?hl=zh-TW", timeout=30000)
            time.sleep(5)
            # if a result list shows instead of a place page, open the first hit
            if not page.query_selector('h1'):
                a = page.query_selector('a[href*="/maps/place/"]')
                if a:
                    a.click(); time.sleep(4)
            # sort reviews by newest when the reviews tab exists
            d = page.evaluate(JS)
            try:
                page.get_by_role("tab", name="評論").first.click(timeout=4000); time.sleep(2.5)
                page.get_by_role("button", name="排序").first.click(timeout=4000); time.sleep(1.5)
                page.get_by_role("menuitemradio", name="最新").first.click(timeout=4000); time.sleep(3)
                d["newest_reviews"] = page.evaluate(JS)["recent_reviews"]
            except Exception as e:
                d["newest_reviews"] = None
            if d["has_order"]:
                try:
                    page.get_by_text("線上點餐").first.click(timeout=4000); time.sleep(4)
                    d["order_links"] = page.evaluate("""() => [...document.querySelectorAll('a[href]')].map(a => a.href)
                        .filter(h => /ubereats\\.com\\/tw\\/store|foodpanda\\.com\\.tw/.test(h)).map(h => h.split('?')[0].replace(/^(https:\\/\\/www\\.foodpanda\\.com\\.tw)\\/food-ordering.*/, '$1'))""")
                    full = page.evaluate("""() => [...document.querySelectorAll('a[href*="foodpanda"]')].map(a => decodeURIComponent((a.href.match(/adj_redirect=([^&]+)/)||[])[1]||'').split('?')[0]).filter(Boolean)""")
                    d["order_links"] = sorted(set([l for l in d["order_links"] if "food-ordering" not in l and l != "https://www.foodpanda.com.tw"] + full))
                except Exception:
                    d["order_links"] = []
            res[q] = d
        except Exception as e:
            res[q] = {"error": str(e)[:200]}
        json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(q, "->", json.dumps(res[q], ensure_ascii=False)[:400], flush=True)
        time.sleep(random.uniform(2, 3))
    page.close()
