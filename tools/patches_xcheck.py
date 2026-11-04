# -*- coding: utf-8 -*-
import json, os
A=[0,1,2,3,4,5,6]
def apply(S):
    by={s["id"]:s for s in S}
    def P(i,**kw):
        if i in by: by[i].update(kw)
    def note(i,t):
        if i in by: by[i]["note"]=(by[i].get("note","")+" "+t).strip()
    P("thai",hours="每日 11:00–21:00（愛食記、OSM；外送可能 20:30 停單）",slots=[{"d":A,"o":"11:00","c":"21:00"}])
    P("wujiu",hours="11:00–14:00、17:00–20:00，週日公休（愛食記；食記寫到 14:30、20:30，取較保守的時間）",slots=[{"d":[1,2,3,4,5],"o":"11:00","c":"14:00"},{"d":[1,2,3,4,5],"o":"17:00","c":"20:00"},{"d":[6],"o":"11:30","c":"14:00"},{"d":[6],"o":"17:00","c":"20:00"}])
    P("pie",hours="週一至六 12:00–19:30，週日公休（愛食記）")
    P("getpower",hours="每日 10:30–14:00、15:30–19:30（OSM 2026-09；foodpanda 寫 15:00 開）",slots=[{"d":A,"o":"10:30","c":"14:00"},{"d":A,"o":"15:30","c":"19:30"}])
    P("proteinbox",hours="週一至六 11:00–14:00、16:00–19:30；週日 11:00–14:00（OSM 2026-09）",slots=[{"d":[1,2,3,4,5,6],"o":"11:00","c":"14:00"},{"d":[1,2,3,4,5,6],"o":"16:00","c":"19:30"},{"d":[0],"o":"11:00","c":"14:00"}])
    note("proteinbox","外送平台價格中英文頁不同（鱸魚 215／220）。")
    note("jcz","店在 275 號 2 樓。Uber Eats 外送價雪花沙朗 7oz 是 320。")
    note("chikopi","愛食記另一筆寫大馬肉骨茶飯 200，價格在 200–240 之間。")
    P("tst",hours="11:30–15:00、17:00–21:00（愛食記；食記寫到 21:30，取較早的時間）；週日公休只有一個來源")
    if "tst" in by:
        for sl in by["tst"]["slots"]:
            if sl["o"]=="17:00": sl["c"]="21:00"
    P("imbento",hours="週一至六 11:00–14:00、16:30–19:30，週日公休（OSM 2026-09）",slots=[{"d":[1,2,3,4,5,6],"o":"11:00","c":"14:00"},{"d":[1,2,3,4,5,6],"o":"16:30","c":"19:30"}])
    P("maesai",hours="每日 11:30–14:00、17:00–20:00（2026-09 食記、OSM 2026-09）")
    if "maesai" in by: by["maesai"].pop("unverified",None)
    P("linji",hours="每日 11:00–21:00（愛食記）",slots=[{"d":A,"o":"11:00","c":"21:00"}])
    P("uosakai",hours="11:30–13:30、17:00–20:00（愛食記；食記寫到 14:00、21:00，取較保守的時間）；週一、二可能只開中午")
    if "uosakai" in by:
        for sl in by["uosakai"]["slots"]:
            if sl["o"]=="11:30": sl["c"]="13:30"
            if sl["o"]=="17:00": sl["c"]="20:00"
    note("guixiang","另一篇 2025 食記寫週一至五 12:00–23:00、週六日 16:00–23:00。")
    P("qiaoqiao",hours="週一至六約 15:50–21:50，週日公休（愛食記）",slots=[{"d":[1,2,3,4,5,6],"o":"15:50","c":"21:50"}])
    P("nanpho",hours="每日 11:00–20:00（愛食記；食記寫到 20:30）",slots=[{"d":A,"o":"11:00","c":"20:00"}])
    P("lemi",hours="週一至五 10:30–14:00、15:30–19:30，週六日公休（OSM 2026-09）",slots=[{"d":[1,2,3,4,5],"o":"10:30","c":"14:00"},{"d":[1,2,3,4,5],"o":"15:30","c":"19:30"}])
    P("laoge",hours="週一至五 11:00–20:30；週六 11:00–14:00、17:00–20:30；週日可能公休（OSM 2026-09）",slots=[{"d":[1,2,3,4,5],"o":"11:00","c":"20:30"},{"d":[6],"o":"11:00","c":"14:00"},{"d":[6],"o":"17:00","c":"20:30"}])
    if "laoge" in by: by["laoge"].pop("unverified",None)
    P("jbw",hours="11:00–14:00、16:30–19:15；公休日來源不一（週日或週一），只收現金")
    if "jbw" in by:
        for sl in by["jbw"]["slots"]:
            if sl["o"]=="16:30": sl["c"]="19:15"
    note("jbw","地址也有寫成 311 巷 17 號。")
    P("tibet",hours="週二至週日 11:30–14:00、17:00–21:00，週一公休（OSM 2026-09）；內用另收 10% 服務費",slots=[{"d":[0,2,3,4,5,6],"o":"11:30","c":"14:00"},{"d":[0,2,3,4,5,6],"o":"17:00","c":"21:00"}])
    note("tibet","內用碳烤雞約 270＋10% 服務費 ≈ 297。")
    P("beef13",hours="週一至六 11:30–14:30、17:30–21:00，週日公休（愛食記）")
    if "beef13" in by:
        for sl in by["beef13"]["slots"]:
            if sl["o"]=="17:30": sl["c"]="21:00"
    if "younghwaru" in by: by["younghwaru"]["hours"]=by["younghwaru"]["hours"].replace("只收現金，","")+"；付款方式各來源不一，建議帶現金"
    P("nihao",hours="每日 11:00–20:50（愛食記、OpenRice）")
    if "nihao" in by: by["nihao"].pop("unverified",None)
    P("eling",hours="週一至五 11:00–14:00、17:00–19:50，週六日公休；只收現金（愛食記）")
    note("xinjiye","地址請以 Google 地圖確認（118 巷 61 之 1 號或 54 弄 33 號）。")
    note("xgypark","2026-10 評論說價格小漲，190 元可能偏低。")
    # attach cross-check summary
    p=os.path.join(os.path.dirname(__file__),"xcheck_final.json")
    try:
        X=json.load(open(p,encoding="utf-8"))
        for r in X.get("results",[]):
            i=r["id"]
            if i not in by: continue
            def lab(v,ok="一致"):
                v=str(v); 
                if v.startswith("一致"): return "一致"
                if v.startswith("衝突"): return "來源不一（已取保守值）"
                return "只有一個來源"
            n=len(r.get("sources",[]))
            by[i]["xcheck"]=f"比對 {n} 個來源：營業 {lab(r['open'])}・時間 {lab(r['hours'])}・價格 {lab(r['price'])}"
    except Exception as e:
        print("xcheck load failed",e)
    return S

_orig_apply=apply
def apply(S):
    S=_orig_apply(S)
    for s in S:
        if s["id"]=="wujiu":
            for it in s["items"]:
                if it["name"]=="怪味蔥醬麵＋去骨雞腿排（小）": it["name"]="怪味蔥醬麵加去骨雞腿排（小）"
            s["fit"]["order"]="怪味蔥醬麵加去骨雞腿排（小）＋青菜豆腐湯"
    return S
