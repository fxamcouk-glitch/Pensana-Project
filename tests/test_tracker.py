import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from tracker import feeds
from tracker.app import Tracker, make_handler
from tracker.db import Store

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name):
    return (FIXTURES / name).read_bytes()


class ParseTests(unittest.TestCase):
    def test_google_strips_source_suffix_and_classifies_rns(self):
        items = feeds.parse_google_news(fixture("google_news.xml"), "Pensana")
        first = items[0]
        self.assertEqual(first.title, "Pensana Plc - Notice of Annual General Meeting and Form of Proxy")
        self.assertEqual(first.source, "Yahoo Finance UK")
        self.assertEqual(first.kind, "rns")
        self.assertEqual(first.published_at, "2026-10-16T06:00:00+00:00")
        self.assertIn("news", {a.kind for a in items})

    def test_yahoo_gives_direct_links_named_by_publisher(self):
        items = feeds.parse_yahoo_news(fixture("yahoo_news.xml"), "Pensana")
        self.assertTrue(items)
        self.assertFalse(any("news.google.com" in a.url or "tsrc=rss" in a.url for a in items))
        self.assertTrue({"Yahoo Finance", "ADVFN", "Proactive Investors"} <= {a.source for a in items})

    def test_source_from_url(self):
        self.assertEqual(feeds.source_from_url("https://uk.finance.yahoo.com/news/x"), "Yahoo Finance")
        self.assertEqual(feeds.source_from_url("https://www.example.co.uk/a"), "example.co.uk")

    def test_same_story_shares_a_dedupe_key(self):
        google = feeds.parse_google_news(fixture("google_news.xml"), "Pensana")
        yahoo = feeds.parse_yahoo_news(fixture("yahoo_news.xml"), "Pensana")
        self.assertTrue({a.dedupe_key for a in google} & {a.dedupe_key for a in yahoo})

    def test_chart(self):
        data = feeds.parse_chart(fixture("chart.json"))
        self.assertEqual(data["symbol"], "PRE.L")
        self.assertEqual(data["currency"], "GBp")
        self.assertGreater(len(data["points"]), 10)
        self.assertRegex(data["points"][0]["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_chart_without_result(self):
        with self.assertRaises(ValueError):
            feeds.parse_chart(b'{"chart": {"result": null, "error": {"code": "Not Found"}}}')

    def test_classify(self):
        self.assertEqual(feeds.classify("Pensana Plc - Holding(s) in Company", "", "Pensana"), "rns")
        self.assertEqual(feeds.classify("Pensana shares jump", "", "Pensana"), "news")
        self.assertEqual(feeds.classify("Anything", "Investegate", "Pensana"), "rns")


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")

    def test_seeds_pensana(self):
        self.assertEqual([s["symbol"] for s in self.store.stocks()], ["PRE.L"])

    def test_dedupes_and_prefers_direct_link(self):
        google = feeds.parse_google_news(fixture("google_news.xml"), "Pensana")
        yahoo = feeds.parse_yahoo_news(fixture("yahoo_news.xml"), "Pensana")
        added = self.store.save_articles("PRE.L", google) + self.store.save_articles("PRE.L", yahoo)
        unique = len({a.dedupe_key for a in google + yahoo})
        self.assertEqual(added, unique)
        self.assertEqual(self.store.save_articles("PRE.L", google + yahoo), 0)

        _, items = self.store.articles("PRE.L", q="Annual General Meeting")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["feed"], "yahoo")
        self.assertTrue(items[0]["url"].startswith("https://uk.finance.yahoo.com/"))

    def test_filters_and_updates(self):
        self.store.save_articles("PRE.L", feeds.parse_yahoo_news(fixture("yahoo_news.xml"), "Pensana"))
        total, items = self.store.articles("PRE.L")
        self.assertEqual(items, sorted(items, key=lambda a: a["published_at"], reverse=True))
        rns_total, _ = self.store.articles("PRE.L", kind="rns")
        self.assertLess(rns_total, total)

        article = self.store.update_article(items[0]["id"], {"starred": True, "note": "check this", "bogus": 1})
        self.assertTrue(article["starred"])
        self.assertEqual(article["note"], "check this")
        self.assertEqual(self.store.articles("PRE.L", status="starred")[0], 1)
        self.assertEqual(self.store.articles("PRE.L", status="noted")[0], 1)
        self.assertIsNone(self.store.update_article(items[0]["id"], {"bogus": 1}))

        self.assertEqual(self.store.mark_all_read("PRE.L"), total)
        self.assertEqual(self.store.articles("PRE.L", status="unread")[0], 0)

    def test_removing_a_stock_removes_its_articles(self):
        self.store.save_articles("PRE.L", feeds.parse_yahoo_news(fixture("yahoo_news.xml"), "Pensana"))
        self.store.remove_stock("PRE.L")
        self.assertEqual(self.store.articles()[0], 0)


class ApiTests(unittest.TestCase):
    def setUp(self):
        def fake_articles(stock):
            if stock["symbol"] == "BAD.L":
                return [], ["google: timed out"]
            return (feeds.parse_google_news(fixture("google_news.xml"), stock["name"])
                    + feeds.parse_yahoo_news(fixture("yahoo_news.xml"), stock["name"])), []

        tracker = Tracker(Store(":memory:"), fake_articles, lambda s, r: feeds.parse_chart(fixture("chart.json")))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tracker))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_page_and_static(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            self.assertIn(b"Stock News Tracker", resp.read())
        with urllib.request.urlopen(self.base + "/app.js") as resp:
            self.assertIn("javascript", resp.headers["Content-Type"])
        status, _ = self.call("GET", "/../tracker/db.py")
        self.assertEqual(status, 404)

    def test_refresh_list_and_patch(self):
        status, data = self.call("POST", "/api/refresh")
        self.assertEqual(status, 200)
        self.assertGreater(data["results"]["PRE.L"]["added"], 0)

        status, data = self.call("GET", "/api/articles?symbol=PRE.L&limit=3")
        self.assertEqual(len(data["articles"]), 3)
        self.assertGreater(data["total"], 3)
        self.assertTrue(data["sources"])

        article_id = data["articles"][0]["id"]
        status, data = self.call("PATCH", f"/api/articles/{article_id}", {"read": True})
        self.assertEqual(status, 200)
        self.assertTrue(data["article"]["read"])
        self.assertEqual(self.call("PATCH", "/api/articles/99999", {"read": True})[0], 404)

    def test_price_includes_news_days(self):
        self.call("POST", "/api/refresh")
        status, data = self.call("GET", "/api/price/PRE.L?range=3mo")
        self.assertEqual(status, 200)
        self.assertIn("2026-10-16", data["news_days"])
        self.assertEqual(self.call("GET", "/api/price/PRE.L?range=5y")[0], 400)

    def test_watchlist(self):
        status, data = self.call("POST", "/api/stocks", {"symbol": "bad.l", "name": "Bad"})
        self.assertEqual(status, 201)
        self.assertEqual(data["stock"]["symbol"], "BAD.L")
        self.assertEqual(data["refresh"]["errors"], ["google: timed out"])
        self.assertEqual(self.call("POST", "/api/stocks", {"symbol": "BAD.L"})[0], 409)
        self.assertEqual(self.call("POST", "/api/stocks", {"symbol": "not a ticker!"})[0], 400)
        self.assertEqual(self.call("DELETE", "/api/stocks/BAD.L")[0], 200)
        self.assertEqual(self.call("DELETE", "/api/stocks/BAD.L")[0], 404)


if __name__ == "__main__":
    unittest.main()
