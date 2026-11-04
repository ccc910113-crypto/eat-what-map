# QA fixes (data QA agent, 2026-11-03)
def apply(S):
    by={s["id"]:s for s in S}
    def F(i,**kw):
        if i in by: by[i]["fit"].update(kw)
    def P(i,**kw):
        if i in by: by[i].update(kw)
    F("jcz",grade="B")
    F("zhongcheng",price=95)
    F("imbento",price=120); P("imbento",note="直線約 470 m，步行約 6–8 分鐘。舒肥雞胸便當 120 元是 2023 年的店內價。")
    F("niu",protein=35,grade="B"); P("niu",pmax=430)
    F("xinjiye",grade="B",tip="烤肉醬請店家另放或少淋；可以加點一顆滷蛋。")
    F("maesai",grade="C",why="120 元有一整片雞腿排，但椒麻雞是酥炸的。")
    F("eling",grade="C",why="排骨、蛋、豬肉抄手三種蛋白質，但排骨是炸的，炒飯也偏油。")
    F("tst",protein=25)
    for sl in by.get("tst",{}).get("slots",[]):
        if sl["o"]=="17:00": sl["c"]="21:30"
    F("nihao",price=195,est=True)
    F("squid",order="嘴邊肉＋滷肉飯（大）＋滷豆干",price=135,protein=25,why="嘴邊肉是瘦豬肉，搭配豆干補蛋白質，135 元。",tip="店裡的羹湯多半有魷魚，不在你的肉類清單裡；想喝湯就選清湯。")
    F("thai",est=True); P("thai",pmin=188)
    for it in by.get("thai",{}).get("items",[]):
        if it["name"]=="打拋豬肉飯" and it["price"]==188: it["name"]="打拋豬肉飯（店內）"
    F("sushi",protein=27,est=True)
    F("chikopi",protein=22)
    F("penghu",protein=12,est=True)
    F("jiang",est=True); P("jiang",hours="11:30–14:30、17:30–20:30；週六公休，2026 年食記說週五也休（vocus.cc），出發前請打電話確認")
    if "wujiu" in by:
        w=by["wujiu"]; w["slots"]=[{"d":[1,2,3,4,5],"o":"11:00","c":"14:30"},{"d":[1,2,3,4,5],"o":"17:00","c":"20:30"},{"d":[6],"o":"11:30","c":"14:30"},{"d":[6],"o":"17:00","c":"20:30"}]
    for sl in by.get("pie",{}).get("slots",[]): sl["o"]="12:00"
    F("lehe",why="沙朗牛排 260 元在預算內，蛋白質來源單純。")
    F("butcher",est=True)
    F("ameng",est=False)
    # audit round (2026-11-04)
    P("niu",verified="2026-04 PTT 食記提到最新價格；愛食記、OpenRice 沒有歇業標示")
    P("pie",verified="2026-04 食記（mibaoma）")
    P("wujiu",verified="2026-06 食記（goodeat）")
    P("squid",unverified="找不到 2025–2026 年的用餐紀錄，先打電話確認")
    P("zhongcheng",unverified="資料停在 2022 年，可能已經不在，先打電話確認")
    if "linji" in by:
        by["linji"]["fit"]["why"]=by["linji"]["fit"]["why"].replace("補蛋白；","補蛋白質；").replace("補蛋白。","補蛋白質。")
    import json,os
    for i,f,v in json.load(open(os.path.join(os.path.dirname(__file__),"copyfix.json"))):
        if i not in by: continue
        if f.startswith("fit."): by[i]["fit"][f[4:]]=v
        else: by[i][f]=v
    return S
