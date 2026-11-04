# Google 地圖與外送平台查核工具

用本機 Chrome（chrome-local skill，除錯埠只綁 127.0.0.1）讀 Google 地圖和 Uber Eats 的公開頁面，查店家是否還在營業、營業時間、目前的菜單價格。不登入、不送出任何東西，遇到真人驗證就停。

## 前置

```sh
python3 ~/.claude/skills/chrome-local/scripts/start.py --port 9222   # 開本機 Chrome
cd ~/eat-what-map/tools
python3 -m unittest gm/test_parse.py                                  # 解析器測試，應全部 OK
```

## 流程

| 步驟 | 指令 | 產出 |
|---|---|---|
| 1. 查 Google 地圖 | `python3 gm/run.py places`（已收錄店）<br>`python3 gm/run.py places --src excluded`（之前排除、理由是「找不到近期紀錄或價格」的店）<br>可加 `--ids a,b`、`--limit 20`、`--fresh` | `gm/out/places.json` |
| 2. 抓外送菜單 | `python3 gm/run.py menus` | `gm/out/menus.json` |
| 3. 產生報告 | `python3 gm/run.py report` | `gm/out/report.md`、`gm/out/suggest.json` |
| 4. 人工看報告後核准 | `python3 gm/run.py approve --ids niu,jiang --fields hours,verified,menu_link` | `gm/approved.json` |
| 5. 重建網站 | `./build.sh`（merge.py 會套用 `patches_gm.py`） | `index.html`、`data/shops.json` |

- 每家店之間停 2–3.5 秒，只開一個分頁，中斷後重跑會從沒做完的店繼續，log 在 `gm/out/run.log`。
- 參數（停頓秒數、評論多舊算「太舊」、座標差多少要人看、價差多少要標記）都在 `gm/config.json`。

## 會自動寫回的，和不會的

- **會寫回**（核准後）：營業時間、「已查證」說明、菜單連結、座標。
- **不會自動寫回**：價格。外送平台價常比店內貴（I'm Pasta 同一道麵，店內 125 元、foodpanda 185 元），報告只列價差，由人決定要不要改。新店也不會自動加入，要照 `extra_*.json` 的格式手寫。

## 已知限制

| 狀況 | 原因 | 處理 |
|---|---|---|
| 「最新評論」只是下限 | 未登入時 Google 是「有限檢視」，評論不能改成依最新排序 | 報告寫「看得到的最新評論」；超過 12 個月的標「評論太舊」，人工確認 |
| 相片沒有「菜單」分類 | 同上，有限檢視 | 菜單改從外送平台拿 |
| foodpanda 抓不到菜單 | 會跳 PerimeterX 真人驗證；菜單由 API 載入，頁面的 JSON-LD 和 `__PRELOADED_STATE__` 裡都沒有 | 只記錄連結；菜單以 Uber Eats 為主 |
| 「線上點餐」按鈕點了沒反應 | 這是一個 `searchviewer` 連結 | 直接開那個連結，再從 `adj_redirect` 參數取出平台網址 |
| 搜尋結果是清單而不是店家頁 | 店名太常見 | 取第一筆，記錄 `picked_from_list`，再用店名相似度和座標差檢查 |
| 菜名相似但不同道 | 「紅燒莊園牛肉麵」和「紅燒牛肉麵」 | 菜名比對不用子字串、相似度至少 0.9，有測試保護 |
