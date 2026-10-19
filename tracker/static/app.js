"use strict";

const PAGE_SIZE = 50;
const SEARCH_DELAY = 250;

const state = {
  stocks: [],
  symbol: null,
  range: "3mo",
  articles: [],
  total: 0,
  filters: { q: "", kind: "", status: "", source: "" },
};

const $ = (id) => document.getElementById(id);

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child != null) node.append(child);
  }
  return node;
}

function svg(tag, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

async function api(path, options = {}) {
  const init = { method: options.method || "GET", headers: {} };
  if (options.body) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(options.body);
  }
  const res = await fetch(path, init);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function showError(message) {
  const banner = $("banner");
  banner.textContent = message;
  banner.hidden = !message;
}

function safeUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? parsed.href : null;
  } catch {
    return null;
  }
}

// --- Formatting -----------------------------------------------------------

const dayFormat = new Intl.DateTimeFormat(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
const timeFormat = new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" });
const shortDate = new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short" });

function relativeTime(iso) {
  const minutes = Math.round((Date.now() - new Date(iso)) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 7) return `${days}d ago`;
  return timeFormat.format(new Date(iso));
}

function localDayKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function dayLabel(date) {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (localDayKey(date) === localDayKey(today)) return "Today";
  if (localDayKey(date) === localDayKey(yesterday)) return "Yesterday";
  return dayFormat.format(date);
}

function formatPrice(value, currency) {
  if (value == null) return "—";
  if (currency === "GBp") return `${value.toFixed(2)}p`;
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(value);
  } catch {
    return value.toFixed(2);
  }
}

// --- Watchlist tabs -------------------------------------------------------

async function loadStocks() {
  const data = await api("/api/stocks");
  state.stocks = data.stocks;
  if (!state.stocks.some((s) => s.symbol === state.symbol)) {
    state.symbol = state.stocks[0] ? state.stocks[0].symbol : null;
  }
  renderTabs();
  renderFootnote();
}

function renderTabs() {
  const tabs = $("tabs");
  tabs.replaceChildren(
    ...state.stocks.map((stock) =>
      el("button", {
        type: "button",
        class: "tab",
        "aria-current": stock.symbol === state.symbol ? "true" : "false",
        title: stock.query,
        "aria-label": `${stock.name} ${stock.symbol}${stock.unread ? `, ${stock.unread} unread` : ""}`,
        onclick: () => selectStock(stock.symbol),
      },
      `${stock.name} · ${stock.symbol}`,
      stock.unread ? el("span", { class: "badge", "aria-hidden": "true" }, String(stock.unread)) : null)
    )
  );
}

function renderFootnote() {
  const stock = state.stocks.find((s) => s.symbol === state.symbol);
  const parts = [];
  if (stock && stock.last_fetch) parts.push(`Feeds checked ${relativeTime(stock.last_fetch)}`);
  if (stock && stock.last_error) parts.push(`Last check had problems: ${stock.last_error}`);
  parts.push("Sources: Google News, Yahoo Finance. Prices may be delayed.");
  $("footnote").replaceChildren(
    document.createTextNode(parts.join(" · ") + " "),
    stock ? el("button", { type: "button", class: "btn-link", onclick: removeStock }, `Remove ${stock.symbol}`) : null
  );
}

function selectStock(symbol) {
  state.symbol = symbol;
  state.filters.source = "";
  $("source").value = "";
  renderTabs();
  renderFootnote();
  loadPrice();
  loadArticles();
}

async function removeStock() {
  const symbol = state.symbol;
  if (!symbol || !confirm(`Remove ${symbol} and all its saved articles?`)) return;
  try {
    await api(`/api/stocks/${encodeURIComponent(symbol)}`, { method: "DELETE" });
    state.symbol = null;
    await loadStocks();
    if (state.symbol) selectStock(state.symbol);
    else renderEmptyWatchlist();
  } catch (err) {
    showError(err.message);
  }
}

function renderEmptyWatchlist() {
  $("price").hidden = true;
  $("list").replaceChildren();
  setListState("Your watchlist is empty. Add a stock to start tracking its news.");
}

// --- Price chart ----------------------------------------------------------

async function loadPrice() {
  const symbol = state.symbol;
  if (!symbol) return;
  $("price").hidden = false;
  for (const btn of $("range").querySelectorAll("button")) {
    btn.setAttribute("aria-pressed", btn.dataset.range === state.range ? "true" : "false");
  }
  const stock = state.stocks.find((s) => s.symbol === symbol);
  $("price-name").textContent = stock ? stock.name : symbol;
  $("price-meta").textContent = symbol;
  try {
    const data = await api(`/api/price/${encodeURIComponent(symbol)}?range=${state.range}`);
    if (symbol !== state.symbol) return;
    $("price-name").textContent = data.name || $("price-name").textContent;
    $("price-meta").textContent = [data.symbol, data.exchange, data.currency].filter(Boolean).join(" · ");
    $("price-value").textContent = formatPrice(data.price, data.currency);
    const change = $("price-change");
    if (data.change_pct != null) {
      change.textContent = `${data.change_pct >= 0 ? "+" : ""}${data.change_pct.toFixed(2)}%`;
      change.className = `change ${data.change_pct >= 0 ? "up" : "down"}`;
    } else {
      change.textContent = "";
    }
    drawChart(data);
  } catch (err) {
    if (symbol !== state.symbol) return;
    $("price-value").textContent = "—";
    $("price-change").textContent = "";
    $("chart").replaceChildren();
    $("price-meta").textContent = `${symbol} · ${err.message}`;
  }
}

function drawChart(data) {
  const chart = $("chart");
  const points = data.points;
  chart.replaceChildren();
  if (points.length < 2) return;

  const width = chart.clientWidth || 600;
  const height = chart.clientHeight || 180;
  const pad = { top: 12, right: 8, bottom: 20, left: 60 };
  chart.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const closes = points.map((p) => p.close);
  let min = Math.min(...closes);
  let max = Math.max(...closes);
  if (min === max) { min -= 1; max += 1; }
  const x = (i) => pad.left + (i / (points.length - 1)) * (width - pad.left - pad.right);
  const y = (v) => pad.top + (1 - (v - min) / (max - min)) * (height - pad.top - pad.bottom);

  for (const v of [min, (min + max) / 2, max]) {
    chart.append(svg("line", { class: "grid", x1: pad.left, x2: width - pad.right, y1: y(v), y2: y(v) }));
    const label = svg("text", { class: "axis", x: pad.left - 6, y: y(v) + 4, "text-anchor": "end" });
    label.textContent = formatPrice(v, data.currency);
    chart.append(label);
  }
  for (const i of [0, Math.floor((points.length - 1) / 2), points.length - 1]) {
    const label = svg("text", { class: "axis", x: x(i), y: height - 4, "text-anchor": i === 0 ? "start" : i === points.length - 1 ? "end" : "middle" });
    label.textContent = shortDate.format(new Date(points[i].date));
    chart.append(label);
  }

  const line = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.close).toFixed(1)}`).join("");
  chart.append(svg("path", { class: "area", d: `${line}L${x(points.length - 1)},${height - pad.bottom}L${x(0)},${height - pad.bottom}Z` }));
  chart.append(svg("path", { class: "line", d: line }));

  // News markers: one dot per trading day, on the price line. News from a
  // weekend or holiday goes on the next trading day.
  const buckets = new Map();
  for (const [day, counts] of Object.entries(data.news_days)) {
    if (day < points[0].date) continue;
    let i = points.findIndex((p) => p.date >= day);
    if (i === -1) i = points.length - 1;
    const bucket = buckets.get(i) || { count: 0, rns: 0, latest: day };
    bucket.count += counts.count;
    bucket.rns += counts.rns;
    if (day > bucket.latest) bucket.latest = day;
    buckets.set(i, bucket);
  }

  const tip = $("chart-tip");
  points.forEach((p, i) => {
    const news = buckets.get(i);
    if (!news) return;
    const kind = news.rns ? "rns" : "news";
    const marker = svg("circle", { class: `marker ${kind}`, cx: x(i), cy: y(p.close), r: 5, tabindex: 0, role: "button" });
    const label = `${shortDate.format(new Date(p.date))}: ${formatPrice(p.close, data.currency)} · ${news.count} article${news.count === 1 ? "" : "s"}${news.rns ? `, ${news.rns} RNS` : ""}`;
    marker.setAttribute("aria-label", label);
    const show = () => {
      tip.textContent = label;
      tip.style.left = `${(x(i) / width) * 100}%`;
      tip.style.top = `${(y(p.close) / height) * 100}%`;
      tip.hidden = false;
    };
    marker.addEventListener("mouseenter", show);
    marker.addEventListener("focus", show);
    marker.addEventListener("mouseleave", () => { tip.hidden = true; });
    marker.addEventListener("blur", () => { tip.hidden = true; });
    marker.addEventListener("click", () => scrollToDay(news.latest));
    marker.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); scrollToDay(news.latest); } });
    chart.append(marker);
  });
}

// Headings are newest first; take the first one on or before the date, so a
// day that is filtered out or not yet loaded lands on the nearest older one.
function scrollToDay(date) {
  const headings = [...document.querySelectorAll(".day[data-day]")];
  const heading = headings.find((h) => h.dataset.day <= date) || headings[headings.length - 1];
  if (heading) heading.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- Articles -------------------------------------------------------------

function setListState(message) {
  $("state").textContent = message || "";
  $("state").hidden = !message;
}

async function loadArticles({ append = false } = {}) {
  const symbol = state.symbol;
  if (!symbol) return;
  const params = new URLSearchParams({ symbol, limit: PAGE_SIZE, offset: append ? state.articles.length : 0 });
  for (const [key, value] of Object.entries(state.filters)) if (value) params.set(key, value);
  if (!append) setListState("Loading articles…");
  $("more").disabled = true;
  try {
    const data = await api(`/api/articles?${params}`);
    if (symbol !== state.symbol) return;
    state.articles = append ? state.articles.concat(data.articles) : data.articles;
    state.total = data.total;
    renderSources(data.sources);
    renderArticles();
  } catch (err) {
    setListState(`Could not load articles: ${err.message}`);
  } finally {
    $("more").disabled = false;
  }
}

function renderSources(sources) {
  const select = $("source");
  const current = state.filters.source;
  select.replaceChildren(
    el("option", { value: "" }, "All sources"),
    ...sources.map((s) => el("option", { value: s.source, selected: s.source === current }, `${s.source} (${s.count})`))
  );
}

function renderArticles() {
  const list = $("list");
  const nodes = [];
  let lastDay = null;
  for (const article of state.articles) {
    const date = new Date(article.published_at);
    const key = localDayKey(date);
    if (key !== lastDay) {
      nodes.push(el("h3", { class: "day", "data-day": key }, dayLabel(date)));
      lastDay = key;
    }
    nodes.push(renderArticle(article));
  }
  list.replaceChildren(...nodes);

  const filtered = Object.values(state.filters).some(Boolean);
  $("count").textContent = state.total ? `(${state.total})` : "";
  $("more").hidden = state.articles.length >= state.total;
  if (state.articles.length) setListState("");
  else setListState(filtered ? "No articles match these filters." : "No articles yet. Press Refresh to check the feeds.");
}

function renderArticle(article) {
  const href = safeUrl(article.url);
  const titleLink = href
    ? el("a", { href, target: "_blank", rel: "noopener noreferrer", onclick: () => { if (!article.read) patch(article, { read: true }); } }, article.title)
    : article.title;

  const body = el("div", { class: "article-body" },
    el("p", { class: "article-title" }, titleLink),
    el("p", { class: "article-meta" },
      el("span", { class: `kind ${article.kind}` }, article.kind === "rns" ? "RNS" : "News"),
      el("span", {}, article.source),
      el("time", { datetime: article.published_at, title: new Date(article.published_at).toLocaleString() }, relativeTime(article.published_at))
    ),
    article.summary ? el("p", { class: "article-summary" }, article.summary) : null,
    article.note ? el("p", { class: "note-text" }, article.note) : null
  );

  const actions = el("div", { class: "article-actions" },
    el("button", {
      type: "button", class: "icon-btn star", "aria-pressed": String(article.starred),
      "aria-label": "Star", title: article.starred ? "Unstar" : "Star",
      onclick: () => patch(article, { starred: !article.starred }),
    }, article.starred ? "★" : "☆"),
    el("button", {
      type: "button", class: "icon-btn", "aria-pressed": String(article.read),
      "aria-label": "Read", title: article.read ? "Mark unread" : "Mark read",
      onclick: () => patch(article, { read: !article.read }),
    }, article.read ? "○" : "✓"),
    el("button", {
      type: "button", class: "icon-btn", "aria-label": article.note ? "Edit note" : "Add note", title: article.note ? "Edit note" : "Add note",
      onclick: () => editNote(article, body),
    }, "✎")
  );

  return el("article", { class: `article${article.read ? " is-read" : ""}`, "data-id": article.id },
    el("span", { class: "unread-dot", "aria-hidden": "true" }), body, actions);
}

function editNote(article, body) {
  if (body.querySelector("textarea")) return;
  const existing = body.querySelector(".note-text");
  if (existing) existing.hidden = true;
  const area = el("textarea", { class: "note", rows: 3, "aria-label": "Note", placeholder: "Your note. Saved when you click away." });
  area.value = article.note;
  area.addEventListener("blur", () => {
    const note = area.value.trim();
    if (note === article.note) {
      area.remove();
      if (existing) existing.hidden = false;
    } else {
      patch(article, { note });
    }
  });
  area.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { area.value = article.note; area.blur(); }
  });
  body.append(area);
  area.focus();
}

async function patch(article, fields) {
  try {
    const data = await api(`/api/articles/${article.id}`, { method: "PATCH", body: fields });
    Object.assign(article, data.article);
    const node = document.querySelector(`.article[data-id="${article.id}"]`);
    if (node) node.replaceWith(renderArticle(article));
    if ("read" in fields) await loadStocks();
  } catch (err) {
    showError(err.message);
  }
}

// --- Actions --------------------------------------------------------------

async function refresh() {
  const button = $("refresh");
  button.disabled = true;
  button.textContent = "Refreshing…";
  showError("");
  try {
    const data = await api("/api/refresh", { method: "POST" });
    const errors = Object.entries(data.results).flatMap(([sym, r]) => r.errors.map((e) => `${sym} ${e}`));
    if (errors.length) showError(`Some feeds failed: ${errors.join("; ")}`);
    await loadStocks();
    await Promise.all([loadArticles(), loadPrice()]);
  } catch (err) {
    showError(err.message);
  } finally {
    button.disabled = false;
    button.textContent = "Refresh";
  }
}

async function markAllRead() {
  if (!state.symbol) return;
  try {
    await api(`/api/stocks/${encodeURIComponent(state.symbol)}/read-all`, { method: "POST" });
    await loadStocks();
    await loadArticles();
  } catch (err) {
    showError(err.message);
  }
}

function openStockDialog() {
  const form = $("stock-form");
  form.reset();
  $("stock-error").hidden = true;
  $("stock-dialog").showModal();
  form.elements.symbol.focus();
}

async function submitStock(event) {
  event.preventDefault();
  const form = event.target;
  const error = $("stock-error");
  const body = {
    symbol: form.elements.symbol.value.trim(),
    name: form.elements.name.value.trim(),
    query: form.elements.query.value.trim(),
  };
  if (!body.symbol) {
    error.textContent = "Enter a ticker such as PRE.L.";
    error.hidden = false;
    form.elements.symbol.focus();
    return;
  }
  const submit = $("stock-submit");
  submit.disabled = true;
  submit.textContent = "Adding…";
  try {
    const data = await api("/api/stocks", { method: "POST", body });
    $("stock-dialog").close();
    await loadStocks();
    selectStock(data.stock.symbol);
    if (data.refresh.errors.length) showError(`Some feeds failed: ${data.refresh.errors.join("; ")}`);
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  } finally {
    submit.disabled = false;
    submit.textContent = "Add stock";
  }
}

// --- Wiring ---------------------------------------------------------------

function init() {
  $("refresh").addEventListener("click", refresh);
  $("add-stock").addEventListener("click", openStockDialog);
  $("stock-cancel").addEventListener("click", () => $("stock-dialog").close());
  $("stock-form").addEventListener("submit", submitStock);
  $("read-all").addEventListener("click", markAllRead);
  $("more").addEventListener("click", () => loadArticles({ append: true }));

  $("range").addEventListener("click", (e) => {
    const range = e.target.dataset && e.target.dataset.range;
    if (range && range !== state.range) {
      state.range = range;
      loadPrice();
    }
  });

  let searchTimer;
  $("search").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.filters.q = e.target.value.trim();
      loadArticles();
    }, SEARCH_DELAY);
  });
  for (const id of ["kind", "status", "source"]) {
    $(id).addEventListener("change", (e) => {
      state.filters[id] = e.target.value;
      loadArticles();
    });
  }

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(loadPrice, 200);
  });

  loadStocks()
    .then(() => (state.symbol ? selectStock(state.symbol) : renderEmptyWatchlist()))
    .catch((err) => showError(err.message));
}

init();
