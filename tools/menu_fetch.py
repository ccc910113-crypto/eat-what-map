# -*- coding: utf-8 -*-
"""Fetch current text menus from delivery platforms through the local Chrome.

Usage: python3 menu_fetch.py out.json URL [URL ...]
- Uber Eats: reads the schema.org Restaurant JSON-LD (hasMenu → sections → items, offers.price).
- foodpanda: reads the visible menu text (name line followed by "$ price").
Results are platform prices (may be higher than in-store).
"""
import json, sys, time, random, os, re
from playwright.sync_api import sync_playwright

out, urls = sys.argv[1], sys.argv[2:]
res = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}

def uber(page):
    raw = page.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)""")
    for t in raw:
        d = json.loads(t)
        if d.get("@type") == "Restaurant":
            items = []
            for sec in (d.get("hasMenu") or {}).get("hasMenuSection", []):
                for it in sec.get("hasMenuItem", []):
                    pr = (it.get("offers") or {}).get("price")
                    items.append({"cat": sec.get("name"), "name": it.get("name"), "price": float(pr) if pr else None,
                                  "desc": (it.get("description") or "")[:120]})
            return {"name": d.get("name"), "items": items, "hours": d.get("openingHoursSpecification"),
                    "rating": d.get("aggregateRating")}
    return {"error": "no Restaurant JSON-LD"}

def panda(page):
    for _ in range(6):
        page.mouse.wheel(0, 2500); time.sleep(0.8)
    t = page.evaluate("() => document.body.innerText")
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    items, seen = [], set()
    for i, l in enumerate(lines):
        m = re.match(r"^\$\s?([\d,]+)(\s*起)?$", l)
        if m and i > 0:
            name = lines[i - 1]
            if name.startswith("$") or name in seen or len(name) > 40: continue
            seen.add(name)
            items.append({"name": name, "price": int(m.group(1).replace(",", "")), "from": bool(m.group(2))})
    title = page.title()
    return {"name": title, "items": items}

with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0]
    page = ctx.new_page()
    for u in urls:
        if u in res and not res[u].get("error"): continue
        try:
            page.goto(u, timeout=40000); time.sleep(7)
            d = uber(page) if "ubereats" in u else panda(page)
            d["fetched"] = time.strftime("%Y-%m-%d")
            res[u] = d
        except Exception as e:
            res[u] = {"error": str(e)[:200]}
        json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(u[:70], "->", res[u].get("name"), len(res[u].get("items", [])), "items", res[u].get("error", ""), flush=True)
        time.sleep(random.uniform(2, 3))
    page.close()
