import json
def I(c,n,p): return {"cat":c,"name":n,"price":p}
A=[0,1,2,3,4,5,6]
E=[
dict(id="chikopi",name="池先生 Kopitiam 大安店",cuisine="馬來西亞椰漿飯・肉骨茶",type="異國",addr="台北市大安區復興南路二段385號",pmin=220,pmax=250,pest=False,phone="02-2738-9255",
 hours="每日 11:30–20:30（2023-11 食記；2022 年報導寫平日中午到 15:00 後休息，17:00 再開）",slots=[{"d":A,"o":"11:30","c":"20:30"}],verified="2025-08 食記",
 signature=["椰漿飯配紅咖哩雞","大馬肉骨茶飯","沙嗲雞椰漿飯"],
 items=[I("椰漿飯","椰漿飯配紅咖哩雞",220),I("椰漿飯","椰漿飯炸雞配參芭蝦仁",250),I("椰漿飯","沙嗲雞椰漿飯",None),I("飯","大馬肉骨茶飯",240),I("麵","咖哩叻沙湯麵（海鮮）",230),I("炒","炒粿條",240),I("湯","肉骨茶湯",None),I("點心","咖椰麵包",None),I("飲品","馬來式黑咖啡（含糖）",65)],
 menu_source="https://hedonistjun.com/chi-kopitiam/",menu_source_label="食記 hedonistjun",menu_source_date="2023-11（可能已調漲）",menu_link="https://www.facebook.com/274016432761128",menu_link_label="官方 FB",
 note="離站約 500 m。椰漿飯和咖哩都有椰奶，熱量偏高。",
 fit=dict(order="大馬肉骨茶飯（飯吃半碗）",price=240,protein=26,grade="B",why="豬排骨燉湯，不甜、不炸。",avoid="參芭蝦仁、叻沙（海鮮）；椰漿飯（油、熱量高）；含糖的馬來咖啡、咖椰麵包。",tip="沙嗲雞椰漿飯的雞肉多一點，但沙嗲醬含糖，記得醬料另放。")),
dict(id="tst",name="尖沙咀港點",cuisine="港式煲湯・點心",type="飯・粥",addr="台北市大安區復興南路二段286號",pmin=200,pmax=300,pest=False,phone="02-2377-0100",
 hours="11:30–15:00、17:00–21:30，週日公休（2026-09 食記；另一說晚上到 21:00）",slots=[{"d":[1,2,3,4,5,6],"o":"11:30","c":"15:00"},{"d":[1,2,3,4,5,6],"o":"17:00","c":"21:00"}],verified="2026-08～10 有多篇食記",
 signature=["清燉牛腩煲湯","神戶牛肉丸","木桶飯套餐"],
 items=[I("套餐","超值套餐 木桶飯（主菜＋飲料）",238),I("飯","紙包臘味飯",68),I("煲湯","清燉牛腩煲湯",118),I("煲湯","菌菇雞腿煲湯",98),I("煲湯","蓮子排骨煲湯",98),I("點心","神戶牛肉丸",98),I("點心","蜜汁叉燒包",98),I("點心","蠔皇炆鳳爪",98),I("點心","晶瑩鮮蝦餃",98),I("點心","冰火菠蘿包",78)],
 menu_source="https://littlepu.tw/tsim-sha-tsui/",menu_source_label="食記 littlepu",menu_source_date="2026-09（另一篇寫牛腩煲 158 元）",menu_link=None,
 note="內用低消每人 200 元，尖峰時段限時 120 分鐘。",
 fit=dict(order="清燉牛腩煲湯＋菌菇雞腿煲湯",price=216,protein=30,grade="B",why="兩盅清燉肉湯，牛＋雞，不加糖；剛好達到低消。",avoid="叉燒包、菠蘿包（含糖）、臘味飯（加工肉）、蝦餃。",tip="再加一份神戶牛肉丸（$98）可以多補 10 g 左右，但會超過 300 元。")),
dict(id="imbento",name="便當人 I.M BENTO 大安店",cuisine="台式便當・舒肥雞胸",type="飯・粥",addr="台北市大安區和平東路三段48號",pmin=120,pmax=205,pest=False,phone="02-2377-3388",
 hours="每日 11:00–14:00、16:30–19:30（2023 年資料）",slots=[{"d":A,"o":"11:00","c":"14:00"},{"d":A,"o":"16:30","c":"19:30"}],unverified="只有外送平台資料，先打電話確認",
 signature=["五福雞腿王","銷魂烤雞腿","舒肥雞胸肉便當"],
 items=[I("便當（外送價）","銷魂烤雞腿",200),I("便當（外送價）","一哥海南雞",205),I("便當（外送價）","五福雞腿王",190),I("便當（外送價）","三杯杏鮑菇",145),I("便當（店內，2023）","舒肥雞胸肉便當",120),I("便當（店內，2023）","銷魂烤雞腿",145),I("便當（店內，2023）","阿嬤滷排骨",129),I("便當（店內，2023）","升官炸排骨",119),I("沙拉","舒肥雞胸沙拉",None)],
 menu_source="https://www.ubereats.com/tw/store/%E4%BE%BF%E7%95%B6%E4%BA%BA-%E5%A4%A7%E5%AE%89%E5%BA%97/6xAbbl4XUx-aviFjP65OPg",menu_source_label="Uber Eats＋2023 食記",menu_source_date="外送價 2026-11；店內價 2023",menu_link="https://www.ubereats.com/tw/store/%E4%BE%BF%E7%95%B6%E4%BA%BA-%E5%A4%A7%E5%AE%89%E5%BA%97/6xAbbl4XUx-aviFjP65OPg",menu_link_label="Uber Eats 菜單",
 note="離站約 800 m，步行 11–12 分鐘，在範圍邊緣。",
 fit=dict(order="舒肥雞胸肉便當（沒有就點銷魂烤雞腿）",price=150,protein=32,grade="A",why="舒肥雞胸幾乎純蛋白質，不炸、不甜。",avoid="炸排骨、三杯（醬含糖）。",tip="店內價估約 $120–160；19:30 就打烊。")),
]
json.dump(E,open("extra_bento.json","w"),ensure_ascii=False,indent=1)
