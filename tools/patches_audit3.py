# -*- coding: utf-8 -*-
def apply(S):
    S=[s for s in S if s["id"]!="mika"]
    by={s["id"]:s for s in S}
    def P(i,**kw):
        if i in by: by[i].update(kw)
    def F(i,**kw):
        if i in by: by[i]["fit"].update(kw)
    def setc(i,o,c):
        for sl in by.get(i,{}).get("slots",[]):
            if sl["o"]==o: sl["c"]=c
    if "getpower" in by: by["getpower"]["note"]+=" Uber Eats 上可能以「米卡蒸烤盒餐 和平店」的名稱上架，價格略有不同。"
    # 福勝亭: official page has no prices
    if "fst" in by:
        for it in by["fst"]["items"]:
            if it["name"]=="和風醬烤雞腿定食": it["price"]=220
            if it["name"]=="鹽烤鯖魚定食": it["price"]=260
        F("fst",price=275,tip="想完全不甜就改點鹽烤鯖魚定食（約 $260），但鯖魚油脂比較高。")
        P("fst",menu_source_label="第三方價目整理（官網沒有公布價格）",note=by["fst"]["note"]+" 官網只有品項，沒有價格；其他品項價格依官網舊價目，可能差 10 元。")
    F("longho",order="鹽味雞湯拉麵（舒肥雞胸）",est=True)
    if "longho" in by: by["longho"]["note"]+=" 點法價格是依均消推估，以現場為準。"
    if "sansi" in by:
        for it in by["sansi"]["items"]:
            if it["name"]=="番茄牛肉刀削麵": it["name"]="番茄牛肉刀削麵（2021 年價格）"
            if it["name"]=="大滷湯（小）": it["name"]="大滷湯（小，2021 年價格）"
        F("sansi",est=True,price=230,order="番茄牛肉刀削麵＋小魚豆干＋干絲")
        by["sansi"]["fit"]["protein"]=32
        by["sansi"]["note"]+=" 番茄牛肉刀削麵的價格是 2021 年的，現在約 160 元（估計）。"
    P("beef13",hours="週一至六 11:30–14:30、17:30–21:30，週日公休"); setc("beef13","17:30","21:30")
    P("qiaoqiao",hours="週一至六 16:00–22:00，週日公休"); setc("qiaoqiao","16:00","22:00")
    if "nanpho" in by:
        P("nanpho",hours="每日 11:00–20:30"); setc("nanpho","11:00","20:30")
        for it in by["nanpho"]["items"]:
            if it["name"] in ("生牛肉粉麵","蘭花干"): it["price"]=None
    P("jbw",hours="11:00–14:00、16:30–19:30，週日公休（2024-12 食記；愛食記寫晚上到 19:15）"); setc("jbw","16:30","19:30")
    if "tibet" in by:
        P("tibet",hours="11:30–14:00、17:00–21:00（2025-06 更新）；週一是否公休未證實；內用另收 10% 服務費")
        for sl in by["tibet"]["slots"]: sl["d"]=[0,1,2,3,4,5,6]
    if "subway" in by:
        for it in by["subway"]["items"]:
            if it["name"]=="鮮嫩雞柳": it["protein_g"]="23"
        F("subway",protein=38)
        by["subway"]["note"]=by["subway"]["note"].replace("蛋白質照抄官網營養表（6 吋含麵包）","蛋白質依官網與 2023 年營養成分整理表（6 吋含麵包），以官網為準")
    if "mos" in by: by["mos"]["note"]="蛋白質依官網各品項營養標示頁（菜單頁本身沒有營養資料）。營業到 22:00。"
    if "luguang" in by:
        P("luguang",menu_source_date="2026-09"); by["luguang"]["note"]+=" 熱炒只在平日晚上和假日供應。"
    F("laoge",avoid="乾拌麵（精緻澱粉）、含糖飲料。")
    if "younghwaru" in by: by["younghwaru"]["hours"]+="（愛食記）"
    return S
