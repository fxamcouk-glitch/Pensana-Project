"""Fetching and parsing of news feeds and price data.

Sources:
  * Google News RSS search, for press coverage matching a stock's query.
  * Yahoo Finance headline RSS, per ticker; carries RNS notices with direct links.
  * Yahoo Finance chart API, for daily closes.
"""

import email.utils
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone

USER_AGENT = "Mozilla/5.0 (compatible; StockNewsTracker/1.0)"
TIMEOUT = 20

GOOGLE_NEWS_URL = "https://news.google.com/rss/search?q={q}&hl=en-GB&gl=GB&ceid=GB:en"
YAHOO_NEWS_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={s}&region=GB&lang=en-GB"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{s}?range={r}&interval=1d"


@dataclass
class Article:
    title: str
    url: str
    source: str
    feed: str
    summary: str
    published_at: str  # ISO 8601, UTC
    kind: str  # "rns" for regulatory announcements, otherwise "news"

    @property
    def dedupe_key(self):
        return dedupe_key(self.title)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def dedupe_key(title):
    """Normalise a headline so the same story from two feeds compares equal."""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(value):
    if not value:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        dt = email.utils.parsedate_to_datetime(value.strip())
    except (TypeError, ValueError):
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def classify(title, source, company_name):
    """RNS notices are titled '<Company> Plc - <Subject>'."""
    if re.search(r"\b(rns|regulatory news|investegate|london stock exchange)\b", source, re.I):
        return "rns"
    if company_name and re.match(re.escape(company_name) + r"\s+(plc|limited|ltd)\b\s*[-–:]", title, re.I):
        return "rns"
    return "news"


def parse_google_news(xml_bytes, company_name=""):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        source = (item.findtext("source") or "").strip()
        # Google appends " - Source" to every headline.
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)].strip()
        if not title:
            continue
        out.append(Article(
            title=title,
            url=(item.findtext("link") or "").strip(),
            source=source or "Google News",
            feed="google",
            summary="",  # Google's description only repeats the title.
            published_at=parse_date(item.findtext("pubDate")),
            kind=classify(title, source, company_name),
        ))
    return out


KNOWN_HOSTS = {
    "finance.yahoo.com": "Yahoo Finance",
    "advfn.com": "ADVFN",
    "proactiveinvestors.co.uk": "Proactive Investors",
    "proactiveinvestors.com": "Proactive Investors",
    "londonstockexchange.com": "London Stock Exchange",
    "investegate.co.uk": "Investegate",
    "sharecast.com": "Sharecast",
}


def source_from_url(url):
    """Name the publisher from a link, e.g. uk.advfn.com -> ADVFN."""
    host = urllib.parse.urlparse(url).hostname or ""
    for known, name in KNOWN_HOSTS.items():
        if host == known or host.endswith("." + known):
            return name
    return re.sub(r"^(www|uk|m)\.", "", host) or "Unknown"


def parse_yahoo_news(xml_bytes, company_name=""):
    root = ET.fromstring(xml_bytes)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        summary = strip_html(item.findtext("description"))
        url = (item.findtext("link") or "").strip().replace("?.tsrc=rss", "")
        out.append(Article(
            title=title,
            url=url,
            source=source_from_url(url),
            feed="yahoo",
            summary="" if summary == title else summary,
            published_at=parse_date(item.findtext("pubDate")),
            kind=classify(title, "", company_name),
        ))
    return out


def fetch_articles(stock):
    """Fetch all feeds for one stock. Returns (articles, errors)."""
    articles, errors = [], []
    query = stock["query"] or stock["name"] or stock["symbol"]
    sources = [
        ("google", GOOGLE_NEWS_URL.format(q=urllib.parse.quote(query)), parse_google_news),
        ("yahoo", YAHOO_NEWS_URL.format(s=urllib.parse.quote(stock["symbol"])), parse_yahoo_news),
    ]
    for name, url, parser in sources:
        try:
            articles.extend(parser(fetch(url), stock["name"]))
        except Exception as exc:  # one failing feed must not stop the others
            errors.append(f"{name}: {exc}")
    return articles, errors


def parse_chart(json_bytes):
    data = json.loads(json_bytes)
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        raise ValueError("no price data for this symbol")
    res = result[0]
    meta = res.get("meta", {})
    closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    points = [
        {"date": datetime.fromtimestamp(ts, timezone.utc).date().isoformat(), "close": round(c, 4)}
        for ts, c in zip(res.get("timestamp") or [], closes)
        if c is not None
    ]
    price = meta.get("regularMarketPrice")
    prev = meta.get("previousClose") or (points[-2]["close"] if len(points) > 1 else None)
    change = meta.get("regularMarketChangePercent")
    if change is None and price is not None and prev:
        change = (price - prev) / prev * 100
    return {
        "symbol": meta.get("symbol"),
        "name": meta.get("longName") or meta.get("shortName"),
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName"),
        "price": price,
        "change_pct": change,
        "market_time": meta.get("regularMarketTime"),
        "points": points,
    }


def fetch_price(symbol, range_="3mo"):
    return parse_chart(fetch(YAHOO_CHART_URL.format(s=urllib.parse.quote(symbol), r=range_)))
