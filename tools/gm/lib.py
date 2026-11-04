# -*- coding: utf-8 -*-
"""Google Maps + delivery-platform lookups through the local Chrome (chrome-local).

Pure parsers (tested in test_parse.py) are kept separate from browser code.
Everything here only reads public pages; nothing is submitted, no login,
no CAPTCHA solving. A bot challenge stops the run.
"""
import json, math, re, time, random, difflib, urllib.parse

# ---------------------------------------------------------------- parsers
WD = {"星期日": 0, "星期一": 1, "星期二": 2, "星期三": 3, "星期四": 4, "星期五": 5, "星期六": 6}
EN_WD = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
CN_NUM = {"一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}


def _hm(s):
    h, m = s.split(":")
    return int(h), int(m)


def parse_hours_labels(labels):
    """Google Maps aria-labels like '星期三、11:00 到 14:30、17:00 到 20:30' / '星期四、休息'
    -> {weekday: [(open, close), ...]} ; overnight closes are capped at 23:59."""
    days = {}
    for lab in labels:
        lab = lab.replace(", 複製營業時間", "").strip()
        parts = [p.strip() for p in lab.split("、")]
        if not parts or parts[0] not in WD:
            continue
        d = WD[parts[0]]
        days.setdefault(d, [])
        rest = parts[1:]
        if not rest or rest[0] in ("休息", "休業", "公休"):
            continue
        if rest[0].startswith("24 小時"):
            days[d].append(("00:00", "23:59")); continue
        for seg in rest:
            m = re.match(r"(\d{1,2}:\d{2})\s*到\s*(?:次日\s*)?(\d{1,2}:\d{2})", seg)
            if not m:
                continue
            o, c = m.group(1), m.group(2)
            if _hm(c) <= _hm(o):
                c = "23:59"
            days[d].append((o.zfill(5), c.zfill(5)))
    return days


def days_to_slots(days):
    """{wd: [(o,c)]} -> site format [{"d":[...], "o":..., "c":...}], grouping identical intervals."""
    by = {}
    for d, segs in days.items():
        for o, c in segs:
            by.setdefault((o, c), []).append(d)
    return [{"d": sorted(ds), "o": o, "c": c} for (o, c), ds in sorted(by.items())]


def slots_equal(a, b):
    norm = lambda s: sorted((tuple(sorted(x["d"])), x.get("o"), x.get("c")) for x in (s or []))
    return norm(a) == norm(b)


def hours_text(days):
    if not days:
        return ""
    groups = {}
    for d in range(7):
        segs = days.get(d)
        key = "休息" if segs == [] else ("、".join(f"{o}–{c}" for o, c in segs) if segs else "未知")
        groups.setdefault(key, []).append(d)
    names = "日一二三四五六"
    out = []
    for key, ds in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lab = "每天" if len(ds) == 7 else "週" + "、".join(names[d] for d in ds)
        out.append(f"{lab} {key}" if key != "休息" else f"{lab}公休")
    return "；".join(out)


def ld_hours_to_days(spec):
    """schema.org openingHoursSpecification -> {wd: [(o,c)]}"""
    days = {}
    for s in spec or []:
        dws = s.get("dayOfWeek") or []
        if isinstance(dws, str):
            dws = [dws]
        for dw in dws:
            d = EN_WD.get(dw.split("/")[-1])
            if d is None:
                continue
            o, c = s.get("opens", "")[:5], s.get("closes", "")[:5]
            if o and c:
                if _hm(c) <= _hm(o):
                    c = "23:59"
                days.setdefault(d, []).append((o, c))
    return {d: sorted(v) for d, v in days.items()}


def rel_to_months(s):
    """'3 週前' / '2 個月前' / '1 年前' / '一個月前' / '5 天前' -> months (float) or None."""
    s = s.strip().replace(" ", "")
    m = re.match(r"^(\d+|[一二兩三四五六七八九十]+)(?:個)?(分鐘|小時|天|週|星期|月|年)前$", s)
    if not m:
        return None
    n = m.group(1)
    n = int(n) if n.isdigit() else CN_NUM.get(n)
    if n is None:
        return None
    unit = m.group(2)
    return {"分鐘": 0, "小時": 0, "天": n / 30, "週": n / 4.35, "星期": n / 4.35, "月": n, "年": n * 12}[unit]


REL_RX = re.compile(r"(?:^|\n)((?:\d+|[一二兩三四五六七八九十]+) ?(?:個)?(?:分鐘|小時|天|週|星期|個月|月|年)前)(?:\n|$| ·)")


def find_rel_dates(text):
    return [m.group(1) for m in REL_RX.finditer(text)]


def coords_from_url(url):
    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if m:
        return [round(float(m.group(1)), 6), round(float(m.group(2)), 6)]
    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    return [round(float(m.group(1)), 6), round(float(m.group(2)), 6)] if m else None


def meters(a, b):
    if not a or not b:
        return None
    dy = (a[0] - b[0]) * 111195
    dx = (a[1] - b[1]) * 111195 * math.cos(math.radians((a[0] + b[0]) / 2))
    return round(math.hypot(dx, dy))


def norm_name(n):
    n = re.sub(r"[\s　・·\-–_()（）\[\]【】「」『』,，.。!！&＆’'`]", "", n or "")
    n = re.sub(r"台北|臺北|大安|分店|門市|科技大樓|店$", "", n)
    return n.lower()


def name_similarity(a, b):
    a, b = norm_name(a), norm_name(b)
    if not a or not b:
        return 0.0
    if a in b or b in a:
        return 1.0
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 2)


def parse_ubereats_ld(ld_list):
    """list of JSON-LD dicts from an Uber Eats store page -> menu dict."""
    for d in ld_list:
        if d.get("@type") != "Restaurant":
            continue
        items = []
        for sec in (d.get("hasMenu") or {}).get("hasMenuSection", []) or []:
            for it in sec.get("hasMenuItem", []) or []:
                pr = (it.get("offers") or {}).get("price")
                try:
                    pr = round(float(pr))
                except (TypeError, ValueError):
                    pr = None
                items.append({"cat": sec.get("name"), "name": (it.get("name") or "").strip(), "price": pr})
        rating = d.get("aggregateRating") or {}
        return {"name": d.get("name"), "items": [i for i in items if i["name"]],
                "days": ld_hours_to_days(d.get("openingHoursSpecification")),
                "rating": rating.get("ratingValue"), "rating_count": rating.get("reviewCount") or rating.get("ratingCount"),
                "geo": [(d.get("geo") or {}).get("latitude"), (d.get("geo") or {}).get("longitude")]}
    return None


def platform_from_google_link(href):
    """Google's ordering links -> clean platform store URL (or None)."""
    m = re.search(r"adj_redirect=([^&]+)", href)
    if m:
        href = urllib.parse.unquote(m.group(1))
    href = href.split("?")[0]
    if re.match(r"https://(www\.)?ubereats\.com/tw/store/", href):
        return href
    if re.match(r"https://(www\.)?foodpanda\.com\.tw/restaurant/[a-z0-9]+/", href):
        return href.replace("https://foodpanda", "https://www.foodpanda")
    return None


def item_similarity(a, b):
    """Strict dish-name match: no substring shortcut ('牛肉麵' must not match '清燉牛肉麵')."""
    a, b = norm_name(a), norm_name(b)
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 2) if a and b else 0.0


def match_items(old_items, new_items, min_sim=0.9):
    """Pair our menu items with platform items by name -> list of diffs."""
    out = []
    for o in old_items or []:
        on = re.sub(r"（.*?）|\(.*?\)", "", o.get("name", ""))
        best, score = None, 0
        for n in new_items:
            s = item_similarity(on, re.sub(r"（.*?）|\(.*?\)", "", n["name"]))
            if s > score:
                best, score = n, s
        if best and score >= min_sim and o.get("price") and best.get("price"):
            out.append({"ours": o["name"], "ours_price": o["price"], "platform": best["name"],
                        "platform_price": best["price"], "pct": round((best["price"] - o["price"]) * 100 / o["price"]), "sim": score})
    return out


# ---------------------------------------------------------------- browser
class Challenge(Exception):
    """A site asked to prove we are human. Stop; a person must handle it."""


CHALLENGE_RX = re.compile(r"confirm you are a human|not a bot|unusual traffic|我們的系統偵測到|驗證您是真人|請確認您不是機器人")

PLACE_JS = r"""() => {
  const t = document.body.innerText;
  const h1 = document.querySelector('h1');
  const lab = [...document.querySelectorAll('[aria-label*="複製營業時間"]')].map(e => e.getAttribute('aria-label'));
  const r = t.match(/\n(\d\.\d)\n\(([\d,]+)\)/) || [];
  const sv = [...document.querySelectorAll('a[href*="searchviewer"]')].map(a => a.href);
  const phone = [...document.querySelectorAll('a[href^="tel:"]')].map(a => a.getAttribute('href').slice(4))[0] || null;
  const addr = (document.querySelector('button[data-item-id="address"]') || {}).innerText || null;
  return { place: h1 ? h1.innerText.trim() : null, url: location.href, rating: r[1] || null, reviews: r[2] || null,
           closed: (t.match(/永久停業|暫時停業/) || [null])[0], hours_labels: lab, text: t.slice(0, 20000),
           searchviewer: sv[0] || null, phone, addr: addr && addr.trim() };
}"""


def pause(cfg):
    time.sleep(random.uniform(*cfg["pause_seconds"]))


def check_challenge(page):
    try:
        t = page.evaluate("() => document.body.innerText.slice(0, 3000)")
    except Exception:
        return
    if CHALLENGE_RX.search(t) or "/sorry/" in page.url:
        raise Challenge(page.url)


def google_place(page, query, cfg):
    url = "https://www.google.com/maps/search/" + urllib.parse.quote(query) + "/?hl=" + cfg["hl"]
    page.goto(url, timeout=40000)
    time.sleep(cfg["page_wait_seconds"])
    check_challenge(page)
    picked_from_list = False
    if not page.query_selector("h1"):
        a = page.query_selector('a[href*="/maps/place/"]')
        if not a:
            return {"error": "not found"}
        a.click()
        picked_from_list = True
        time.sleep(cfg["page_wait_seconds"])
    # close the "sign in" nudge if it pops up
    page.keyboard.press("Escape")
    d = page.evaluate(PLACE_JS)
    days = parse_hours_labels(d.pop("hours_labels"))
    text = d.pop("text")
    rel = find_rel_dates(text)
    months = [m for m in (rel_to_months(x) for x in rel) if m is not None]
    d.update({
        "ll": coords_from_url(d["url"]), "url": d["url"].split("?")[0],
        "picked_from_list": picked_from_list,
        "days": {str(k): v for k, v in days.items()},
        "slots": days_to_slots(days), "hours_text": hours_text(days),
        "review_dates_visible": rel[:10],
        "newest_review_months": round(min(months), 1) if months else None,
        "has_online_order": "線上點餐" in text,
        "fetched": time.strftime("%Y-%m-%d %H:%M"),
    })
    d["order_links"] = []
    if d.get("searchviewer") and d["has_online_order"]:
        pause(cfg)
        page.goto(d["searchviewer"], timeout=40000)
        time.sleep(cfg["page_wait_seconds"])
        hrefs = page.evaluate("() => [...document.querySelectorAll('a[href]')].map(a => a.href)")
        d["order_links"] = sorted({u for u in (platform_from_google_link(h) for h in hrefs) if u})
    d.pop("searchviewer", None)
    return d


def ubereats_menu(page, url, cfg):
    page.goto(url, timeout=40000)
    time.sleep(cfg["page_wait_seconds"] + 2)
    check_challenge(page)
    raw = page.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent)""")
    lds = []
    for t in raw:
        try:
            lds.append(json.loads(t))
        except ValueError:
            pass
    m = parse_ubereats_ld(lds)
    if not m:
        return {"error": "no Restaurant JSON-LD"}
    m["days"] = {str(k): v for k, v in m["days"].items()}
    m["url"] = url
    m["fetched"] = time.strftime("%Y-%m-%d %H:%M")
    return m
