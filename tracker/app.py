"""HTTP server: JSON API, static page and the background poller.

Run with:  python -m tracker.app
"""

import json
import logging
import mimetypes
import os
import re
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import feeds
from .db import Store

STATIC_DIR = Path(__file__).parent / "static"
PRICE_TTL = 300  # seconds a price lookup is cached
PRICE_RANGES = {"1mo", "3mo", "6mo", "1y"}
SYMBOL_RE = re.compile(r"^[A-Za-z0-9.\-^=]{1,20}$")

log = logging.getLogger("tracker")


class Tracker:
    def __init__(self, store, fetch_articles=feeds.fetch_articles, fetch_price=feeds.fetch_price):
        self.store = store
        self.fetch_articles = fetch_articles
        self.fetch_price = fetch_price
        self.refresh_lock = threading.Lock()
        self.price_cache = {}

    def refresh(self, symbol=None):
        """Fetch feeds for one stock or all of them. Returns {symbol: result}."""
        stocks = [self.store.stock(symbol)] if symbol else self.store.stocks()
        results = {}
        with self.refresh_lock:
            for stock in filter(None, stocks):
                articles, errors = self.fetch_articles(stock)
                added = self.store.save_articles(stock["symbol"], articles)
                self.store.record_fetch(stock["symbol"], errors)
                results[stock["symbol"]] = {"fetched": len(articles), "added": added, "errors": errors}
                log.info("%s: %d fetched, %d new, errors=%s", stock["symbol"], len(articles), added, errors)
        return results

    def price(self, symbol, range_):
        key = (symbol, range_)
        hit = self.price_cache.get(key)
        if hit and time.time() - hit[0] < PRICE_TTL:
            data = hit[1]
        else:
            data = self.fetch_price(symbol, range_)
            self.price_cache[key] = (time.time(), data)
        return {**data, "news_days": self.store.news_days(symbol)}

    def poll_forever(self, interval):
        while True:
            try:
                self.refresh()
            except Exception:
                log.exception("scheduled refresh failed")
            time.sleep(interval)


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def make_handler(tracker):
    store = tracker.store

    class Handler(BaseHTTPRequestHandler):
        server_version = "StockNewsTracker/1.0"

        def log_message(self, fmt, *args):
            log.debug("%s - %s", self.address_string(), fmt % args)

        # --- plumbing ----------------------------------------------------

        def _send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, data, status=HTTPStatus.OK):
            self._send(status, json.dumps(data).encode(), "application/json")

        def _body(self):
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            try:
                data = json.loads(self.rfile.read(length))
            except ValueError:
                raise ApiError(HTTPStatus.BAD_REQUEST, "Request body is not valid JSON.")
            if not isinstance(data, dict):
                raise ApiError(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object.")
            return data

        def _dispatch(self, method):
            url = urlparse(self.path)
            parts = [unquote(p) for p in url.path.strip("/").split("/") if p]
            query = {k: v[-1] for k, v in parse_qs(url.query).items()}
            try:
                if parts[:1] == ["api"]:
                    self._api(method, parts[1:], query)
                elif method == "GET":
                    self._static(parts)
                else:
                    raise ApiError(HTTPStatus.METHOD_NOT_ALLOWED, "Method not allowed.")
            except ApiError as err:
                self._json({"error": err.message}, err.status)
            except Exception as exc:
                log.exception("request failed")
                self._json({"error": f"Server error: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

        def do_GET(self):
            self._dispatch("GET")

        def do_POST(self):
            self._dispatch("POST")

        def do_PATCH(self):
            self._dispatch("PATCH")

        def do_DELETE(self):
            self._dispatch("DELETE")

        def _static(self, parts):
            name = "/".join(parts) or "index.html"
            path = (STATIC_DIR / name).resolve()
            if STATIC_DIR.resolve() not in path.parents or not path.is_file():
                raise ApiError(HTTPStatus.NOT_FOUND, "Not found.")
            ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype == "application/javascript":
                ctype += "; charset=utf-8"
            self._send(HTTPStatus.OK, path.read_bytes(), ctype)

        # --- API ---------------------------------------------------------

        def _api(self, method, parts, query):
            route = (method, parts[0] if parts else "", len(parts))

            if route == ("GET", "stocks", 1):
                return self._json({"stocks": store.stocks()})

            if route == ("POST", "stocks", 1):
                body = self._body()
                symbol = str(body.get("symbol", "")).strip().upper()
                if not SYMBOL_RE.match(symbol):
                    raise ApiError(HTTPStatus.BAD_REQUEST, "Enter a ticker such as PRE.L.")
                if store.stock(symbol):
                    raise ApiError(HTTPStatus.CONFLICT, f"{symbol} is already on the watchlist.")
                name = str(body.get("name", "")).strip() or symbol
                query_text = str(body.get("query", "")).strip() or name
                store.add_stock(symbol, name, query_text)
                result = tracker.refresh(symbol)[symbol]
                return self._json({"stock": store.stock(symbol), "refresh": result}, HTTPStatus.CREATED)

            if route == ("DELETE", "stocks", 2):
                if not store.remove_stock(parts[1]):
                    raise ApiError(HTTPStatus.NOT_FOUND, "That stock is not on the watchlist.")
                return self._json({"ok": True})

            if route == ("POST", "stocks", 3) and parts[2] == "read-all":
                return self._json({"updated": store.mark_all_read(parts[1])})

            if route == ("GET", "articles", 1):
                try:
                    limit = max(1, min(int(query.get("limit", 100)), 500))
                    offset = max(0, int(query.get("offset", 0)))
                except ValueError:
                    raise ApiError(HTTPStatus.BAD_REQUEST, "limit and offset must be numbers.")
                symbol = query.get("symbol") or None
                total, items = store.articles(
                    symbol=symbol, q=query.get("q", "").strip(), kind=query.get("kind", ""),
                    status=query.get("status", ""), source=query.get("source", ""),
                    limit=limit, offset=offset,
                )
                return self._json({"total": total, "articles": items, "sources": store.sources(symbol)})

            if route == ("PATCH", "articles", 2):
                try:
                    article_id = int(parts[1])
                except ValueError:
                    raise ApiError(HTTPStatus.NOT_FOUND, "Article not found.")
                article = store.update_article(article_id, self._body())
                if article is None:
                    raise ApiError(HTTPStatus.NOT_FOUND, "Article not found, or nothing to change.")
                return self._json({"article": article})

            if route == ("POST", "refresh", 1):
                symbol = query.get("symbol") or None
                if symbol and not store.stock(symbol):
                    raise ApiError(HTTPStatus.NOT_FOUND, "That stock is not on the watchlist.")
                return self._json({"results": tracker.refresh(symbol)})

            if route == ("GET", "price", 2):
                range_ = query.get("range", "3mo")
                if range_ not in PRICE_RANGES:
                    raise ApiError(HTTPStatus.BAD_REQUEST, "Unknown range.")
                try:
                    return self._json(tracker.price(parts[1], range_))
                except Exception as exc:
                    raise ApiError(HTTPStatus.BAD_GATEWAY, f"Price unavailable: {exc}")

            raise ApiError(HTTPStatus.NOT_FOUND, "Unknown API route.")

    return Handler


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    db_path = os.environ.get("DB_PATH", "tracker.db")
    interval = int(os.environ.get("REFRESH_MINUTES", "15")) * 60

    tracker = Tracker(Store(db_path))
    if interval > 0:
        threading.Thread(target=tracker.poll_forever, args=(interval,), daemon=True).start()

    server = ThreadingHTTPServer((host, port), make_handler(tracker))
    log.info("Serving on http://%s:%d (db=%s, refresh every %ds)", host, port, db_path, interval)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
