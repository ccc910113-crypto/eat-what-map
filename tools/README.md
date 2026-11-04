# tools：建置流程

```sh
./build.sh      # 重建整個網站（輸出到 repo 根目錄）
```

| 檔案 | 用途 |
|---|---|
| `template.html` | 網頁樣板（CSS、JS 都在這裡） |
| `shops_src.py` | 最早 9 家店的資料 → `base.json` |
| `extra_*.json` | 後續各輪查證加入的店家 |
| `merge.py` | 合併、ArcGIS 地理編碼（快取在 `geo_cache.json`）、套用 `patches*.py`、`copyfix.json` |
| `patches*.py` | QA 和交叉比對後的修正（價格、營業時間、文案） |
| `xcheck_final.json` | 兩來源交叉比對的結果，顯示在卡片的「交叉比對」 |
| `meta.json` | 頁尾說明＋涵蓋範圍報告（由 `coverage_report.py` 產生） |
| `classify.py`、`reviewed.json`、`coverage_*.json` | 涵蓋率分類：OSM（`pois.json`）＋愛食記（`ifoodie_all.json`） |
| `build.py` | 把資料注入樣板，同時產生離線用的街道 SVG（`roads.json`） |
| `pwa.py` | 加上 manifest、service worker、PWA meta |

新增店家：把查證結果放進新的 `extra_xxx.json`（格式和其他 extra 檔一樣），然後執行 `./build.sh`。
