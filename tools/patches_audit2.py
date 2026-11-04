# -*- coding: utf-8 -*-
def apply(S):
    by={s["id"]:s for s in S}
    def P(i,**kw):
        if i in by: by[i].update(kw)
    P("sushi",unverified="官網門市頁讀不到，找不到 2025–2026 年的紀錄；先用官網門市查詢或打電話確認")
    P("imbento",unverified="只有外送平台資料，找不到 2025–2026 年的用餐紀錄，先打電話確認")
    P("butcher",verified="2026-04 食記確認地址和營業時間")
    P("longho",verified="2026-04 食記；愛食記最新評論 2026-04")
    if "squid" in by: by["squid"]["hours"]="各來源不一：10:30–21:00（2023 食記）、12:00–20:00（Uber Eats）、11:00–22:00 週日休；以 Google 地圖為準"
    if "chikopi" in by: by["chikopi"]["hours"]="每日 11:30–20:30（2023 食記）；2022 年報導寫平日 15:00–17:00 休息"
    return S
