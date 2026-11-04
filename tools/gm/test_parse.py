# -*- coding: utf-8 -*-
"""Unit tests for the pure parsers. Run: python3 -m unittest gm/test_parse.py (from tools/)."""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class Hours(unittest.TestCase):
    LABELS = ["星期三、11:00 到 14:30、17:00 到 20:30, 複製營業時間", "星期四、休息, 複製營業時間",
              "星期五、11:00 到 14:30、17:00 到 20:30", "星期六、18:00 到 次日 02:00", "星期日、24 小時營業"]

    def test_parse(self):
        d = lib.parse_hours_labels(self.LABELS)
        self.assertEqual(d[3], [("11:00", "14:30"), ("17:00", "20:30")])
        self.assertEqual(d[4], [])                       # closed day is present but empty
        self.assertEqual(d[6], [("18:00", "23:59")])     # overnight capped
        self.assertEqual(d[0], [("00:00", "23:59")])
        self.assertNotIn(1, d)                           # unknown day stays unknown

    def test_slots_and_text(self):
        d = lib.parse_hours_labels(["星期一、11:00 到 21:00", "星期二、休息"] +
                                   [f"{w}、11:00 到 21:00" for w in ("星期三", "星期四", "星期五", "星期六", "星期日")])
        self.assertEqual(lib.days_to_slots(d), [{"d": [0, 1, 3, 4, 5, 6], "o": "11:00", "c": "21:00"}])
        self.assertEqual(lib.hours_text(d), "週日、一、三、四、五、六 11:00–21:00；週二公休")
        self.assertTrue(lib.slots_equal([{"d": [6, 0, 1, 3, 4, 5], "o": "11:00", "c": "21:00"}], lib.days_to_slots(d)))

    def test_ld_hours(self):
        spec = [{"dayOfWeek": ["Monday", "Tuesday"], "opens": "11:30", "closes": "14:00"},
                {"dayOfWeek": "https://schema.org/Monday", "opens": "17:30", "closes": "20:20"}]
        self.assertEqual(lib.ld_hours_to_days(spec), {1: [("11:30", "14:00"), ("17:30", "20:20")], 2: [("11:30", "14:00")]})


class Dates(unittest.TestCase):
    def test_rel(self):
        self.assertEqual(lib.rel_to_months("2 個月前"), 2)
        self.assertEqual(lib.rel_to_months("1 年前"), 12)
        self.assertEqual(lib.rel_to_months("一個月前"), 1)
        self.assertAlmostEqual(lib.rel_to_months("3 週前"), 3 / 4.35)
        self.assertEqual(lib.rel_to_months("5 小時前"), 0)
        self.assertIsNone(lib.rel_to_months("2025年4月"))

    def test_find(self):
        t = "Julia\n在地嚮導 · 96 則評論\n7 個月前\n超熱門\n宗哲\n4 個月前\n常常來\n價格 3 個月前沒有換行"
        self.assertEqual(lib.find_rel_dates(t), ["7 個月前", "4 個月前"])


class Geo(unittest.TestCase):
    def test_coords(self):
        u = "https://www.google.com/maps/place/x/@25.02,121.54,17z/data=!3m1!4b1!8m2!3d25.0283199!4d121.5468478!16s"
        self.assertEqual(lib.coords_from_url(u), [25.02832, 121.546848])
        self.assertEqual(lib.coords_from_url("https://www.google.com/maps/@25.1,121.5,15z"), [25.1, 121.5])

    def test_meters(self):
        self.assertAlmostEqual(lib.meters([25.026099, 121.543666], [25.0224973, 121.542779]), 410, delta=5)


class Names(unittest.TestCase):
    def test_sim(self):
        self.assertEqual(lib.name_similarity("I'm Pasta 和平店", "I’m Pasta 和平店"), 1.0)
        self.assertEqual(lib.name_similarity("29號館 義大利麵", "29號館義大利麵"), 1.0)
        self.assertLess(lib.name_similarity("Eat foodie Pasta 好好吃餐房", "Eatfoodie udon 好好吃餐房(烏龍麵 鍋燒意麵)"), 1.0)

    def test_match_items(self):
        ours = [{"name": "清燉雪花牛肉麵", "price": 215}, {"name": "紅燒半筋半肉麵（小）", "price": 260}, {"name": "滷海帶", "price": 30}]
        theirs = [{"name": "清燉雪花牛肉麵", "price": 240}, {"name": "紅燒半筋半肉麵", "price": 280}]
        d = lib.match_items(ours, theirs)
        self.assertEqual([(x["ours"], x["pct"]) for x in d], [("清燉雪花牛肉麵", 12), ("紅燒半筋半肉麵（小）", 8)])
        # a different dish with a similar name must not be paired
        self.assertEqual(lib.match_items([{"name": "紅燒莊園牛肉麵", "price": 430}], [{"name": "紅燒牛肉麵", "price": 240}]), [])
        self.assertEqual(lib.match_items([{"name": "牛肉麵", "price": 200}], [{"name": "清燉牛肉麵", "price": 240}]), [])


class Links(unittest.TestCase):
    def test_platform(self):
        g = ("https://www.foodpanda.com.tw/food-ordering?c=tw&adj_redirect=https%3A%2F%2Ffoodpanda.com.tw%2Frestaurant%2Fcyu8"
             "%2Fniu-zhuang-yuan-niu-rou-mian-cyu8%3Futm_campaign%3Dx")
        self.assertEqual(lib.platform_from_google_link(g), "https://www.foodpanda.com.tw/restaurant/cyu8/niu-zhuang-yuan-niu-rou-mian-cyu8")
        u = "https://www.ubereats.com/tw/store/abc/0Fg4Mgp_SJqi8dj0FeIbOg?diningMode=PICKUP&utm_source=google"
        self.assertEqual(lib.platform_from_google_link(u), "https://www.ubereats.com/tw/store/abc/0Fg4Mgp_SJqi8dj0FeIbOg")
        self.assertIsNone(lib.platform_from_google_link("https://support.google.com/foodordering"))


class UberLD(unittest.TestCase):
    def test_fixture(self):
        with open(os.path.join(FIX, "ubereats_ld.json"), encoding="utf-8") as f:
            lds = json.load(f)
        m = lib.parse_ubereats_ld(lds)
        self.assertEqual(m["name"], "測試牛肉麵")
        self.assertEqual(m["items"][0], {"cat": "牛肉麵", "name": "清燉牛肉麵", "price": 240})
        self.assertIsNone(m["items"][2]["price"])
        self.assertEqual(m["days"][1], [("11:30", "14:00"), ("17:30", "20:20")])


class Challenge(unittest.TestCase):
    def test_rx(self):
        self.assertTrue(lib.CHALLENGE_RX.search("Before we continue...\nPlease confirm you are a human (and not a bot)."))
        self.assertFalse(lib.CHALLENGE_RX.search("牛莊園牛肉麵 4.5 (1,550)"))


if __name__ == "__main__":
    unittest.main()
