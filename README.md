# Pensana-Project

A stock news and article tracker. It starts with **Pensana Plc (LSE: PRE)**, and you can add other tickers to the watchlist.

- Gets articles from **Google News** (press coverage that matches each stock's search) and **Yahoo Finance** (RNS notices and publisher articles, with direct links).
- Stores one copy of each story when it appears in both feeds, and keeps the direct link over Google's redirect.
- Labels each article as **RNS** (regulatory announcement) or **News**.
- Lets you mark articles read or unread, star them, add notes, search, and filter by type, status or source.
- Shows a price chart (1M, 3M, 6M or 1Y) with a dot on each day that had news. Click a dot to jump to that day's articles.
- Checks the feeds every 15 minutes in the background, and also when you press Refresh.

The app uses only the Python standard library, so there's nothing to install. Data is kept in SQLite.

## Run locally

```sh
python3 -m tracker.app
# open http://localhost:8000
```

| Variable          | Default      | Meaning                                       |
|-------------------|--------------|-----------------------------------------------|
| `PORT`            | `8000`       | HTTP port                                     |
| `HOST`            | `0.0.0.0`    | Bind address                                  |
| `DB_PATH`         | `tracker.db` | SQLite file                                   |
| `REFRESH_MINUTES` | `15`         | Background check interval; `0` turns it off   |

## Tests

```sh
python3 -m unittest -v
```

The tests run against saved copies of the real feeds in `tests/fixtures/`. They don't use the network.

## Deploy to Render

`render.yaml` sets up a Python web service. On Render's free plan the disk is wiped at each deploy, so stars, notes and read state are lost on redeploy. Articles come back on the next refresh. To keep everything, attach a persistent disk and set `DB_PATH` to a file on it, e.g. `/var/data/tracker.db`.

## API

| Method | Path                               | Purpose                                                       |
|--------|------------------------------------|---------------------------------------------------------------|
| GET    | `/api/stocks`                      | Watchlist, with unread counts                                 |
| POST   | `/api/stocks`                      | Add `{symbol, name?, query?}` and fetch its news straight away |
| DELETE | `/api/stocks/{symbol}`             | Remove a stock and its articles                               |
| POST   | `/api/stocks/{symbol}/read-all`    | Mark all of a stock's articles read                           |
| GET    | `/api/articles`                    | `symbol, q, kind=rns\|news, status=unread\|starred\|noted, source, limit, offset` |
| PATCH  | `/api/articles/{id}`               | Update `{read?, starred?, note?}`                             |
| POST   | `/api/refresh?symbol=`             | Check the feeds now                                           |
| GET    | `/api/price/{symbol}?range=3mo`    | Daily closes and article counts per day                       |

Prices and feeds come from Yahoo Finance and Google News. Prices may be delayed, and the feeds are for personal use.
