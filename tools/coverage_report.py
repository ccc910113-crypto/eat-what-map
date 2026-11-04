# -*- coding: utf-8 -*-
"""Build a de-duplicated coverage report (OSM + iFoodie) and store it in meta.json."""
import json, re
from classify import norm
o = json.load(open('coverage_osm.json', encoding='utf-8'))
f = json.load(open('coverage_ifoodie.json', encoding='utf-8'))
S = json.load(open('shops.json', encoding='utf-8'))
INC_ALIAS = {"貴香鹹酥雞", "便當人台北大安店 I`M BENTO"}

uni = {}
for src, rows in (("osm", o), ("ifoodie", f)):
    for name, cat, why in rows:
        if name in INC_ALIAS: cat, why = "已收錄", ""
        if why.startswith("已收錄") or "（已收錄）" in why or "已收錄" in why: continue
        k = norm(name)
        if k in uni:
            # keep the more informative classification
            if uni[k][1] != "已收錄" and cat == "已收錄": uni[k] = (name, cat, why)
            continue
        uni[k] = (name, cat, why)

GROUPS = [
    ("已歇業或搬走", r"歇業|搬|停止營業|危老|同址已改"),
    ("還在營業，但找不到 2024 年以後的價格", r"還在營業|找不到 2024|價格"),
    ("找不到 2025–2026 年仍營業的紀錄", r"找不到 2025|近期紀錄|查無|待確認"),
    ("查不到這家店（地圖資料過時）", r"查不到"),
    ("超出步行 10 分鐘", r"超出步行|附近沒有分店|沒有分店"),
    ("每人超過 300 元或合菜", r"超過|300|高價|合菜|每人約|居酒屋|私廚|飯店"),
    ("沒有晚餐時段", r"只開|沒有晚餐|白天|中午"),
    ("不是豬雞牛魚為主", r"豬雞牛魚|素食|鵝|海鮮|甜品|果汁"),
    ("酒吧、門市或不是餐館", r"酒吧|餐酒館|門市|超市|外帶|生麵|早餐"),
    ("精緻澱粉、點心或油炸攤", r"澱粉|點心|煎包|水煎|餅|炸|熱狗|披薩|義大利|切麵|不到 100"),
]
def group(why):
    for g, rx in GROUPS:
        if re.search(rx, why): return g
    return "其他"

inc = [v for v in uni.values() if v[1] == "已收錄"]
exc = [v for v in uni.values() if v[1] in ("已查核排除", "已歇業（愛食記標示）")]
unfit = [v for v in uni.values() if v[1] == "不適合晚餐"]
todo = [v for v in uni.values() if v[1] == "待查"]
grouped = {}
for n, c, w in exc:
    grouped.setdefault(group(w), []).append(n)
unfit_g = {}
for n, c, w in unfit:
    unfit_g.setdefault(w.split("：")[0] if w else "其他", []).append(n)

total = len(uni)
html = ("<b>涵蓋範圍</b>：比對了 OpenStreetMap（車站 800 公尺內 346 筆）和愛食記「捷運科技大樓站」列表（259 筆），去除重複後共"
        f"約 {total} 家（兩邊店名寫法不同，少數可能重複計算）。其中 <b>{len(S)} 家收錄</b>；"
        f"{len(exc)} 家逐一查核後沒有收錄；{len(unfit)} 家是早餐、咖啡甜點、素食、酒吧或高價餐廳，不屬於晚餐清單；"
        f"尚未查核 {len(todo)} 家。")
det = "<details><summary>查核後沒有收錄的店（依原因）</summary>" + "".join(
    f"<p><b>{g}（{len(v)}）</b>：{'、'.join(sorted(v))}</p>" for g, v in sorted(grouped.items(), key=lambda x: -len(x[1]))) + "</details>"
det2 = "<details><summary>不屬於晚餐清單的店</summary>" + "".join(
    f"<p><b>{g}（{len(v)}）</b>：{'、'.join(sorted(v))}</p>" for g, v in sorted(unfit_g.items(), key=lambda x: -len(x[1]))) + "</details>"
m = json.load(open('meta.json', encoding='utf-8'))
m["coverage"] = html + det + det2
json.dump(m, open('meta.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(total, len(inc), len(exc), len(unfit), len(todo))
for g, v in grouped.items(): print(g, len(v))
