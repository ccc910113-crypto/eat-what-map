# -*- coding: utf-8 -*-
"""Google Maps / Uber Eats verification pipeline.

  python3 gm/run.py places  [--src shops|excluded|FILE.json] [--ids a,b] [--limit N] [--fresh]
  python3 gm/run.py menus   [--ids a,b]
  python3 gm/run.py report
  python3 gm/run.py approve --ids a,b [--fields hours,verified,menu_link,ll]

Run from tools/. Needs the chrome-local browser on 127.0.0.1:9222 for places/menus.
Results go to gm/out/ and resume automatically; nothing is written into the
site data until you `approve` and rebuild (merge.py applies gm/approved.json).
"""
import argparse, json, os, re, sys, time, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib

TOOLS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
STATION = [25.026099, 121.543666]  # BR08, same as build.py
P_PLACES, P_MENUS = os.path.join(OUT, "places.json"), os.path.join(OUT, "menus.json")
LOG = os.path.join(OUT, "run.log")


def jload(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def jsave(p, d):
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    open(LOG, "a", encoding="utf-8").write(line + "\n")


def street(addr):
    m = re.search(r"(?:區)?([^區市]+?(?:路|街|大道)(?:[一二三四五六七八九十]+段)?(?:\d+巷)?)", addr or "")
    return m.group(1) if m else ""


def targets(src):
    if src == "shops":
        S = json.load(open(os.path.join(TOOLS, "shops.json"), encoding="utf-8"))
        return [{"id": s["id"], "name": s["name"], "query": f'{s["name"]} {street(s.get("addr"))}'.strip(),
                 "ll": s.get("ll"), "kind": "shop"} for s in S]
    if src == "excluded":
        R = json.load(open(os.path.join(TOOLS, "reviewed.json"), encoding="utf-8"))
        rx = re.compile(r"找不到 2025|近期紀錄|查無|待確認|找不到 2024|價格")
        return [{"id": "x:" + k, "name": k, "query": f"{k} 台北 大安", "ll": None, "kind": "excluded", "reason": v}
                for k, v in R.items() if rx.search(v)]
    return json.load(open(src, encoding="utf-8"))  # [{id,name,query,ll?}]


def with_browser(fn):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp(CFG["cdp_url"]).contexts[0]
        page = ctx.new_page()
        try:
            fn(page)
        finally:
            page.close()


def cmd_places(a):
    res = jload(P_PLACES, {})
    T = targets(a.src)
    if a.ids:
        want = set(a.ids.split(","))
        T = [t for t in T if t["id"] in want]
    todo = [t for t in T if a.fresh or t["id"] not in res or res[t["id"]].get("error")]
    todo = todo[: a.limit or CFG["max_shops_per_run"]]
    log(f"places: {len(todo)} to do ({len(T)} targets, {len(res)} cached)")

    def go(page):
        for i, t in enumerate(todo, 1):
            try:
                d = lib.google_place(page, t["query"], CFG)
                d["target"] = {k: t.get(k) for k in ("name", "query", "ll", "kind", "reason")}
                if not d.get("error"):
                    d["name_sim"] = lib.name_similarity(t["name"], d.get("place"))
                    d["from_ours_m"] = lib.meters(t.get("ll"), d.get("ll"))
                    d["from_station_m"] = lib.meters(STATION, d.get("ll"))
                res[t["id"]] = d
                log(f'[{i}/{len(todo)}] {t["id"]} -> {d.get("place")} rev={d.get("newest_review_months")}m '
                    f'closed={d.get("closed")} order={len(d.get("order_links", []))} {d.get("error", "")}')
            except lib.Challenge as e:
                log(f"STOP: bot challenge at {e}. A person must open the Chrome window and handle it; then rerun.")
                break
            except Exception as e:
                res[t["id"]] = {"error": str(e)[:300], "target": t}
                log(f'[{i}/{len(todo)}] {t["id"]} ERROR {str(e)[:120]}')
            jsave(P_PLACES, res)
            lib.pause(CFG)
    with_browser(go)


def cmd_menus(a):
    P = jload(P_PLACES, {})
    res = jload(P_MENUS, {})
    want = set(a.ids.split(",")) if a.ids else None
    todo = []
    for sid, d in P.items():
        if want and sid not in want:
            continue
        for u in d.get("order_links", []):
            if "ubereats.com" in u and (u not in res or res[u].get("error")):
                todo.append((sid, u))
    log(f"menus: {len(todo)} Uber Eats pages to fetch (foodpanda is recorded only: it shows a bot check)")

    def go(page):
        for i, (sid, u) in enumerate(todo, 1):
            try:
                m = lib.ubereats_menu(page, u, CFG)
                m["shop"] = sid
                res[u] = m
                log(f'[{i}/{len(todo)}] {sid} -> {len(m.get("items", []))} items {m.get("error", "")}')
            except lib.Challenge as e:
                log(f"STOP: bot challenge at {e}. A person must handle it in the Chrome window; then rerun.")
                break
            except Exception as e:
                res[u] = {"error": str(e)[:300], "shop": sid}
                log(f"[{i}/{len(todo)}] {sid} ERROR {str(e)[:120]}")
            jsave(P_MENUS, res)
            lib.pause(CFG)
    with_browser(go)


def cmd_report(a):
    P = jload(P_PLACES, {})
    M = jload(P_MENUS, {})
    S = {s["id"]: s for s in json.load(open(os.path.join(TOOLS, "shops.json"), encoding="utf-8"))}
    ok_m, far = CFG["recent_months_ok"], CFG["coord_mismatch_m"]
    lines = [f"# Google 地圖查核報告（{time.strftime('%Y-%m-%d %H:%M')}）", "",
             "「最新評論」是未登入時看得到的評論裡最新的一則，代表「至少這麼新」。", ""]
    suggest = {}
    shops = [(k, v) for k, v in P.items() if not k.startswith("x:")]
    exc = [(k, v) for k, v in P.items() if k.startswith("x:")]

    if shops:
        lines += ["## 已收錄店家", "", "| 店 | 狀態 | 最新評論 | 名稱相符 | 座標差 | 營業時間 | 外送價差 | 需要人看 |", "|---|---|---|---|---|---|---|---|"]
    for sid, d in sorted(shops):
        s = S.get(sid)
        if d.get("error") or not s:
            lines.append(f"| {sid} | 查詢失敗：{d.get('error', '不在 shops.json')} | | | | | | ✋ |"); continue
        flags = []
        status = d.get("closed") or "營業中"
        if d.get("closed"): flags.append("停業")
        nm = d.get("newest_review_months")
        if nm is None or nm > ok_m: flags.append("評論太舊")
        if d.get("name_sim", 0) < CFG["name_similarity_min"]: flags.append("店名不符")
        if d.get("from_ours_m") and d["from_ours_m"] > far: flags.append("座標差大")
        same = lib.slots_equal(s.get("slots"), d.get("slots"))
        if not d.get("slots"): hrs = "Google 沒有"
        elif same: hrs = "一致"
        else: hrs = "不同"; flags.append("時間不同")
        menus = [m for m in M.values() if m.get("shop") == sid and m.get("items")]
        diffs = lib.match_items(s.get("items"), menus[0]["items"]) if menus else []
        med = round(statistics.median([x["pct"] for x in diffs])) if diffs else None
        pd = f"{med:+d}%（{len(diffs)} 道）" if diffs else ("有菜單" if menus else "—")
        if diffs and abs(med) >= CFG["price_diff_flag_pct"]: flags.append("價差")
        lines.append(f"| {s['name']} | {status} | {'—' if nm is None else str(nm) + ' 個月'} | {d.get('name_sim')} | "
                     f"{d.get('from_ours_m', '—')} m | {hrs} | {pd} | {'、'.join(flags) or '—'} |")
        sg = {"place": d.get("place"), "flags": flags}
        if d.get("slots") and not same:
            sg["hours"] = {"slots": d["slots"], "text": d["hours_text"] + f"（Google 地圖，{d['fetched'][:7]}）",
                           "was": s.get("hours")}
        if not d.get("closed") and nm is not None and nm <= ok_m:
            sg["verified"] = (f"Google 地圖 {d['fetched'][:7]}：{d.get('rating')} 分、{d.get('reviews')} 則評論，"
                              f"看得到的最新評論約 {nm} 個月前")
        ue = [u for u in d.get("order_links", []) if "ubereats" in u]
        if ue: sg["menu_link"] = {"url": ue[0], "label": "Uber Eats 菜單（外送價）"}
        if d.get("from_ours_m") and d["from_ours_m"] > far: sg["ll"] = d["ll"]
        if diffs: sg["price_diffs"] = diffs
        suggest[sid] = sg

    if exc:
        lines += ["", "## 之前排除的店：重新查", "",
                  "| 店 | 原排除原因 | Google 結果 | 最新評論 | 離車站直線 | 外送菜單 | 判斷 |", "|---|---|---|---|---|---|---|"]
        for k, d in sorted(exc, key=lambda kv: (kv[1].get("newest_review_months") or 999)):
            t = d.get("target", {})
            if d.get("error"):
                lines.append(f"| {t.get('name', k)} | {t.get('reason', '')} | 查詢失敗 | | | | ✋ |"); continue
            nm, dist = d.get("newest_review_months"), d.get("from_station_m")
            ue = [u for u in d.get("order_links", []) if "ubereats" in u]
            menu = next((m for m in M.values() if m.get("url") in ue and m.get("items")), None)
            if d.get("closed"): verdict = "維持排除（" + d["closed"] + "）"
            elif d.get("name_sim", 0) < CFG["name_similarity_min"]: verdict = "✋ 店名不符，人工確認"
            elif lib.item_similarity(t.get("name"), d.get("place")) < 0.8: verdict = "✋ Google 店名不同（可能換店或改名），人工確認"
            elif dist and dist * 1.3 > 800: verdict = "維持排除（超出步行 10 分鐘）"
            elif nm is not None and nm <= ok_m and (menu or ue): verdict = "可重新評估（有營業證據和菜單）"
            elif nm is not None and nm <= ok_m: verdict = "營業中，但沒有菜單來源"
            else: verdict = "維持排除"
            lines.append(f"| {t.get('name')} | {t.get('reason', '')} | {d.get('place')} | {'—' if nm is None else str(nm) + ' 個月'} | "
                         f"{dist or '—'} m | {str(len(menu['items'])) + ' 道' if menu else ('有連結' if ue else '—')} | {verdict} |")
    open(os.path.join(OUT, "report.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    jsave(os.path.join(OUT, "suggest.json"), suggest)
    log(f"report: {len(shops)} shops, {len(exc)} excluded -> gm/out/report.md, gm/out/suggest.json")


def cmd_approve(a):
    sug = jload(os.path.join(OUT, "suggest.json"), {})
    ap_p = os.path.join(HERE, "approved.json")
    ap = jload(ap_p, {})
    fields = a.fields.split(",")
    for sid in a.ids.split(","):
        sg = sug.get(sid)
        if not sg:
            log(f"approve: {sid} has no suggestion"); continue
        e = ap.setdefault(sid, {})
        for f in fields:
            if f in sg and f != "price_diffs":
                e[f] = sg[f]
        log(f"approve: {sid} <- {sorted(k for k in e)}")
    jsave(ap_p, ap)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("places"); p.add_argument("--src", default="shops"); p.add_argument("--ids"); p.add_argument("--limit", type=int); p.add_argument("--fresh", action="store_true")
    p = sp.add_parser("menus"); p.add_argument("--ids")
    sp.add_parser("report")
    p = sp.add_parser("approve"); p.add_argument("--ids", required=True); p.add_argument("--fields", default="hours,verified,menu_link")
    a = ap.parse_args()
    {"places": cmd_places, "menus": cmd_menus, "report": cmd_report, "approve": cmd_approve}[a.cmd](a)
