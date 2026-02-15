from __future__ import annotations

import asyncio
import time
from typing import Any

import feedparser
import httpx
from bs4 import BeautifulSoup
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import urljoin

app = FastAPI()
templates = Jinja2Templates(directory="templates")

RSS_URL = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
SCRAPE_URL = "https://news.yahoo.co.jp/"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

CACHE_TTL_SECONDS = 300
MAX_LIMIT = 50

_cache: dict[str, dict[str, Any]] = {}
_cache_lock = asyncio.Lock()


def _now() -> float:
    return time.time()


def _is_cache_fresh(source: str, limit: int) -> bool:
    entry = _cache.get(source)
    if not entry:
        return False
    if _now() - entry["fetched_at"] >= CACHE_TTL_SECONDS:
        return False
    items = entry.get("items", [])
    return len(items) >= limit


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    return min(limit, MAX_LIMIT)


async def _fetch_rss(limit: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(RSS_URL)
        response.raise_for_status()

    feed = feedparser.parse(response.text)
    items: list[dict[str, Any]] = []
    for entry in feed.entries[:limit]:
        items.append(
            {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_at": entry.get("published") or entry.get("updated"),
                "source": "rss",
            }
        )
    return items


async def _fetch_scrape(limit: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(SCRAPE_URL)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not href:
            continue
        if "news.yahoo.co.jp/articles/" not in href and not href.startswith("/articles/"):
            continue

        title = " ".join(anchor.get_text(strip=True).split())
        if not title:
            continue

        url = urljoin(SCRAPE_URL, href)
        if url in seen:
            continue

        seen.add(url)
        items.append(
            {
                "title": title,
                "url": url,
                "published_at": None,
                "source": "scrape",
            }
        )
        if len(items) >= limit:
            break

    return items


def _merge_items(primary: list[dict[str, Any]], secondary: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in primary + secondary:
        url = item.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        merged.append(item)
        if len(merged) >= limit:
            break
    return merged


async def _fetch_news(source: str, limit: int) -> list[dict[str, Any]]:
    if source == "rss":
        return await _fetch_rss(limit)
    if source == "scrape":
        return await _fetch_scrape(limit)

    rss_items = await _fetch_rss(limit)
    scrape_items = await _fetch_scrape(limit)
    return _merge_items(rss_items, scrape_items, limit)


async def _refresh_cache(source: str, limit: int) -> list[dict[str, Any]]:
    async with _cache_lock:
        if _is_cache_fresh(source, limit):
            return _cache[source]["items"]

        items = await _fetch_news(source, limit)
        _cache[source] = {
            "items": items,
            "fetched_at": _now(),
            "limit": limit,
        }
        return items


def _get_cached_items(source: str) -> list[dict[str, Any]] | None:
    entry = _cache.get(source)
    if not entry:
        return None
    return entry.get("items")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/news")
async def get_news(
    background_tasks: BackgroundTasks,
    source: str = "mixed",
    limit: int = 10,
) -> JSONResponse:
    source = source.lower().strip()
    if source not in {"rss", "scrape", "mixed"}:
        source = "mixed"

    limit = _clamp_limit(limit)
    cached_items = _get_cached_items(source)

    if cached_items and _is_cache_fresh(source, limit):
        return JSONResponse(cached_items[:limit])

    if cached_items and len(cached_items) >= limit:
        background_tasks.add_task(_refresh_cache, source, limit)
        return JSONResponse(cached_items[:limit])

    items = await _refresh_cache(source, limit)
    return JSONResponse(items[:limit])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
