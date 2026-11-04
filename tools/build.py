import json, math, sys, os
D = os.path.dirname(os.path.abspath(__file__))
roads = json.load(open(os.path.join(D, "roads.json")))["elements"]
shops = json.load(open(os.path.join(D, "shops.json")))
meta = json.load(open(os.path.join(D, "meta.json")))
STATION = [25.026099, 121.543666]

lats = [s["ll"][0] for s in shops] + [STATION[0]]
lons = [s["ll"][1] for s in shops] + [STATION[1]]
m_lat = 0.0013; m_lon = 0.0016
lat0 = max(lats) + m_lat; lat1 = min(lats) - m_lat
lon0 = min(lons) - m_lon; lon1 = max(lons) + m_lon
W = 1000.0
kx = W / (lon1 - lon0)
ky = kx / math.cos(math.radians(STATION[0]))
H = round((lat0 - lat1) * ky)

def P(lat, lon):
    return ((lon - lon0) * kx, (lat0 - lat) * ky)

def path(geom, close=False):
    pts = [P(g["lat"], g["lon"]) for g in geom]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + ("Z" if close else ""), pts

parks, edges, fills, labels = [], [], [], []
width = {"trunk": 16, "secondary": 14, "tertiary": 10, "unclassified": 6, "residential": 6}
best = {}
for e in roads:
    t = e["tags"]
    if "geometry" not in e: continue
    if t.get("leisure") == "park":
        d, _ = path(e["geometry"], True); parks.append(f'<path class="park" d="{d}"/>'); continue
    hw = t.get("highway")
    if t.get("tunnel") == "yes" or t.get("bridge") == "yes" and hw == "trunk": continue
    d, pts = path(e["geometry"])
    w = width.get(hw, 6); major = hw in ("trunk", "secondary", "tertiary")
    edges.append((w, f'<path class="rd-edge" stroke-width="{w+2.5}" d="{d}"/>'))
    fills.append((w, f'<path class="rd{" major" if major else ""}" stroke-width="{w}" d="{d}"/>'))
    name = t.get("name", "")
    if name and hw in ("secondary", "tertiary", "residential") and "地下道" not in name and "高架" not in name:
        # longest in-view segment
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if not (60 < mx < W - 60 and 30 < my < H - 30): continue
            L = math.hypot(x2 - x1, y2 - y1)
            key = name
            if key not in best or L > best[key][0]:
                best[key] = (L, mx, my, math.degrees(math.atan2(y2 - y1, x2 - x1)), hw)
for name, (L, mx, my, ang, hw) in best.items():
    if "巷" in name or (hw == "residential" and L < 120): continue
    if L < 60: continue
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    labels.append(f'<text class="rlabel" x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" dominant-baseline="central" transform="rotate({ang:.1f} {mx:.0f} {my:.0f})">{name}</text>')
edges.sort(key=lambda a: a[0]); fills.sort(key=lambda a: a[0])
svg = "\n".join(parks + [e for _, e in edges] + [f for _, f in fills] + labels)

for i, s in enumerate(shops): s["n"] = i + 1
html = open(os.path.join(D, "template.html")).read()
html = (html.replace("/*VBW*/", str(int(W))).replace("/*VBH*/", str(H)).replace("/*ROADS*/", svg)
        .replace("/*PROJ*/", json.dumps({"lat0": lat0, "lon0": lon0, "kx": kx, "ky": ky}))
        .replace("/*STATION*/", json.dumps(STATION))
        .replace("/*DATA*/", json.dumps(shops, ensure_ascii=False))
        .replace("/*META*/", json.dumps(meta, ensure_ascii=False)))
open(os.path.join(D, "br08-dinner.html"), "w").write(html)
print("ok", W, H, len(shops), "labels", len(labels), "size", len(html))
full = ('<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + html.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '').replace('</style>', 'body{margin:0}\n[hidden]{display:none!important}\n</style>\n</head>\n<body>', 1)
        + '\n</body>\n</html>\n')
out = os.path.expanduser("~/Desktop/科技大樓站晚餐地圖.html")
open(out, "w").write(full)
print("local", out)
