"""SQLite storage for the watchlist and articles."""

import sqlite3
import threading
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS stocks (
    symbol      TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    query       TEXT NOT NULL,
    added_at    TEXT NOT NULL,
    last_fetch  TEXT,
    last_error  TEXT
);
CREATE TABLE IF NOT EXISTS articles (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol       TEXT NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
    dedupe_key   TEXT NOT NULL,
    title        TEXT NOT NULL,
    url          TEXT NOT NULL,
    source       TEXT NOT NULL,
    feed         TEXT NOT NULL,
    kind         TEXT NOT NULL,
    summary      TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL,
    first_seen   TEXT NOT NULL,
    read         INTEGER NOT NULL DEFAULT 0,
    starred      INTEGER NOT NULL DEFAULT 0,
    note         TEXT NOT NULL DEFAULT '',
    UNIQUE (symbol, dedupe_key)
);
CREATE INDEX IF NOT EXISTS articles_by_date ON articles (symbol, published_at DESC);
"""

DEFAULT_STOCKS = [("PRE.L", "Pensana", "Pensana")]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        if not self.conn.execute("SELECT 1 FROM stocks LIMIT 1").fetchone():
            for symbol, name, query in DEFAULT_STOCKS:
                self.add_stock(symbol, name, query)

    # --- watchlist -------------------------------------------------------

    def stocks(self):
        with self.lock:
            rows = self.conn.execute(
                """SELECT s.*, (SELECT COUNT(*) FROM articles a
                                WHERE a.symbol = s.symbol AND a.read = 0) AS unread
                   FROM stocks s ORDER BY added_at, symbol"""
            ).fetchall()
        return [dict(r) for r in rows]

    def stock(self, symbol):
        with self.lock:
            row = self.conn.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol,)).fetchone()
        return dict(row) if row else None

    def add_stock(self, symbol, name, query):
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO stocks (symbol, name, query, added_at) VALUES (?, ?, ?, ?)",
                (symbol, name, query, now()),
            )

    def remove_stock(self, symbol):
        with self.lock, self.conn:
            return self.conn.execute("DELETE FROM stocks WHERE symbol = ?", (symbol,)).rowcount

    def record_fetch(self, symbol, errors):
        with self.lock, self.conn:
            self.conn.execute(
                "UPDATE stocks SET last_fetch = ?, last_error = ? WHERE symbol = ?",
                (now(), "; ".join(errors) or None, symbol),
            )

    # --- articles --------------------------------------------------------

    def save_articles(self, symbol, articles):
        """Insert new articles; returns how many were new.

        The same story often arrives from Google News (a redirect link) and
        Yahoo (a direct link); the direct link wins whichever came first.
        """
        added = 0
        seen = now()
        with self.lock, self.conn:
            for a in articles:
                cur = self.conn.execute(
                    """INSERT INTO articles (symbol, dedupe_key, title, url, source, feed,
                                             kind, summary, published_at, first_seen)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT (symbol, dedupe_key) DO NOTHING""",
                    (symbol, a.dedupe_key, a.title, a.url, a.source, a.feed,
                     a.kind, a.summary, a.published_at, seen),
                )
                if cur.rowcount:
                    added += 1
                    continue
                if a.feed != "google":
                    self.conn.execute(
                        """UPDATE articles SET url = ?, feed = ?,
                               summary = CASE WHEN summary = '' THEN ? ELSE summary END
                           WHERE symbol = ? AND dedupe_key = ? AND feed = 'google'""",
                        (a.url, a.feed, a.summary, symbol, a.dedupe_key),
                    )
                if a.kind == "rns":
                    self.conn.execute(
                        "UPDATE articles SET kind = 'rns' WHERE symbol = ? AND dedupe_key = ?",
                        (symbol, a.dedupe_key),
                    )
        return added

    def articles(self, symbol=None, q="", kind="", status="", source="", limit=100, offset=0):
        where, args = [], []
        if symbol:
            where.append("symbol = ?")
            args.append(symbol)
        if q:
            where.append("(title LIKE ? OR summary LIKE ? OR note LIKE ? OR source LIKE ?)")
            args += [f"%{q}%"] * 4
        if kind in ("rns", "news"):
            where.append("kind = ?")
            args.append(kind)
        if source:
            where.append("source = ?")
            args.append(source)
        if status == "unread":
            where.append("read = 0")
        elif status == "starred":
            where.append("starred = 1")
        elif status == "noted":
            where.append("note != ''")
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        with self.lock:
            total = self.conn.execute(f"SELECT COUNT(*) FROM articles {clause}", args).fetchone()[0]
            rows = self.conn.execute(
                f"SELECT * FROM articles {clause} ORDER BY published_at DESC, id DESC LIMIT ? OFFSET ?",
                args + [limit, offset],
            ).fetchall()
        return total, [self._article(r) for r in rows]

    def sources(self, symbol=None):
        sql = "SELECT source, COUNT(*) AS n FROM articles"
        args = []
        if symbol:
            sql += " WHERE symbol = ?"
            args.append(symbol)
        with self.lock:
            rows = self.conn.execute(sql + " GROUP BY source ORDER BY n DESC, source", args).fetchall()
        return [{"source": r["source"], "count": r["n"]} for r in rows]

    def news_days(self, symbol):
        with self.lock:
            rows = self.conn.execute(
                """SELECT substr(published_at, 1, 10) AS day, COUNT(*) AS n,
                          SUM(kind = 'rns') AS rns
                   FROM articles WHERE symbol = ? GROUP BY day""",
                (symbol,),
            ).fetchall()
        return {r["day"]: {"count": r["n"], "rns": r["rns"]} for r in rows}

    def update_article(self, article_id, fields):
        allowed = {"read": int, "starred": int, "note": str}
        sets = {k: allowed[k](v) for k, v in fields.items() if k in allowed}
        if not sets:
            return None
        with self.lock, self.conn:
            self.conn.execute(
                f"UPDATE articles SET {', '.join(f'{k} = ?' for k in sets)} WHERE id = ?",
                list(sets.values()) + [article_id],
            )
            row = self.conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        return self._article(row) if row else None

    def mark_all_read(self, symbol):
        with self.lock, self.conn:
            return self.conn.execute(
                "UPDATE articles SET read = 1 WHERE symbol = ? AND read = 0", (symbol,)
            ).rowcount

    @staticmethod
    def _article(row):
        d = dict(row)
        d["read"] = bool(d["read"])
        d["starred"] = bool(d["starred"])
        del d["dedupe_key"]
        return d
