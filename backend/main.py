from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from backend.adapters import YahooNewsAdapter, NHKNewsAdapter, GoogleNewsAdapter
from backend.config import settings
from backend.models import NewsItem
from backend.services import NewsAggregator

# このファイルの場所を基準にテンプレートディレクトリを解決
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(title="News Aggregator API", version="2.0.0")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Initialize adapters
yahoo_adapter = YahooNewsAdapter()
nhk_adapter = NHKNewsAdapter()
google_adapter = GoogleNewsAdapter()

# Initialize aggregator with all adapters
aggregator = NewsAggregator(
    adapters={
        "yahoo": yahoo_adapter,
        "nhk": nhk_adapter,
        "google": google_adapter,
    }
)

# Cache configuration
CACHE_TTL_SECONDS = settings.CACHE_TTL_SECONDS
MAX_LIMIT = settings.MAX_LIMIT

_cache: dict[str, dict[str, Any]] = {}
_cache_lock = asyncio.Lock()


def _now() -> float:
    return time.time()


def _is_cache_fresh(cache_key: str, limit: int) -> bool:
    """Check if cache is fresh for a given key.

    Args:
        cache_key: Cache key.
        limit: Required limit.

    Returns:
        True if cache is fresh and sufficient.
    """
    entry = _cache.get(cache_key)
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


def _news_items_to_dict(items: List[NewsItem]) -> List[Dict[str, Any]]:
    """Convert NewsItem objects to dictionary format for API response.

    Args:
        items: List of NewsItem objects.

    Returns:
        List of dictionaries compatible with existing frontend.
    """
    result = []
    for item in items:
        result.append(
            {
                "title": item.title,
                "url": str(item.url),
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "source": item.source,
                "source_name": item.source_name,
                "summary": item.summary,
            }
        )
    return result


async def _fetch_news(
    sources: List[str],
    limit: int,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch news using the aggregator or specific adapter.

    Args:
        sources: List of source identifiers.
        limit: Maximum number of items to return.
        sort_by: Sort field ('published_at' or 'source').
        sort_order: Sort order ('asc' or 'desc').
        keyword: Optional keyword to filter by title.

    Returns:
        List of news items as dictionaries.
    """
    # Handle legacy Yahoo-specific modes
    if "rss" in sources:
        items = await yahoo_adapter.fetch_rss_only(limit)
        return _news_items_to_dict(items)
    elif "scrape" in sources:
        items = await yahoo_adapter.fetch_scrape_only(limit)
        return _news_items_to_dict(items)
    elif "mixed" in sources:
        items = await yahoo_adapter.fetch_news(limit)
        return _news_items_to_dict(items)

    # Handle new multi-source aggregation
    if "all" in sources:
        # Fetch from all sources
        items = await aggregator.fetch_and_aggregate(
            limit=limit, sort_by=sort_by, sort_order=sort_order, keyword=keyword
        )
    else:
        # Validate and filter sources
        valid_sources = [s for s in sources if s in aggregator.adapters]
        if not valid_sources:
            valid_sources = ["yahoo"]  # Default fallback
        items = await aggregator.fetch_and_aggregate(
            sources=valid_sources,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    return _news_items_to_dict(items)


async def _refresh_cache(
    cache_key: str,
    sources: List[str],
    limit: int,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Refresh the cache for given sources.

    Args:
        cache_key: Cache key.
        sources: List of source identifiers.
        limit: Number of items to fetch.
        sort_by: Sort field.
        sort_order: Sort order.
        keyword: Optional keyword filter.

    Returns:
        List of news items.
    """
    async with _cache_lock:
        if _is_cache_fresh(cache_key, limit):
            return _cache[cache_key]["items"]

        items = await _fetch_news(sources, limit, sort_by, sort_order, keyword)
        _cache[cache_key] = {
            "items": items,
            "fetched_at": _now(),
            "limit": limit,
        }
        return items


def _get_cached_items(cache_key: str) -> List[Dict[str, Any]] | None:
    """Get cached items for a cache key.

    Args:
        cache_key: Cache key.

    Returns:
        Cached items or None if not available.
    """
    entry = _cache.get(cache_key)
    if not entry:
        return None
    return entry.get("items")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/news")
async def get_news(
    background_tasks: BackgroundTasks,
    sources: Optional[str] = Query(
        default="all",
        description="Comma-separated list of sources (yahoo,nhk,google) or 'all'",
    ),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    sort_by: str = Query(
        default="published_at",
        description="Sort field: 'published_at' or 'source'",
    ),
    sort_order: str = Query(
        default="desc", description="Sort order: 'asc' or 'desc'"
    ),
    keyword: Optional[str] = Query(
        default=None, description="Filter by keyword in title"
    ),
) -> JSONResponse:
    """Get news from specified sources with filtering and sorting.

    Args:
        background_tasks: FastAPI background tasks.
        sources: Comma-separated source list or special values.
        limit: Maximum number of items to return.
        sort_by: Sort field ('published_at' or 'source').
        sort_order: Sort order ('asc' or 'desc').
        keyword: Optional keyword to filter by title.

    Returns:
        JSON response with news items.
    """
    # Validate sort parameters
    if sort_by not in ["published_at", "source"]:
        sort_by = "published_at"
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    # Parse sources
    source_list = [s.strip().lower() for s in sources.split(",") if s.strip()]
    if not source_list:
        source_list = ["all"]

    # Create cache key from parameters
    cache_key = (
        f"{','.join(sorted(source_list))}:{limit}:{sort_by}:{sort_order}"
        f":{keyword or ''}"
    )

    # Check cache
    cached_items = _get_cached_items(cache_key)

    if cached_items and _is_cache_fresh(cache_key, limit):
        return JSONResponse(cached_items[:limit])

    if cached_items and len(cached_items) >= limit:
        # Return cached data and refresh in background
        background_tasks.add_task(
            _refresh_cache, cache_key, source_list, limit, sort_by, sort_order, keyword
        )
        return JSONResponse(cached_items[:limit])

    # Fetch new data
    items = await _refresh_cache(
        cache_key, source_list, limit, sort_by, sort_order, keyword
    )
    return JSONResponse(items[:limit])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sources")
def get_sources() -> JSONResponse:
    """Get available news sources.

    Returns:
        JSON response with list of available sources.
    """
    sources = []
    for source_id, adapter in aggregator.adapters.items():
        sources.append(
            {
                "id": source_id,
                "name": adapter.source_name,
                "enabled": source_id in settings.ENABLED_SOURCES,
            }
        )
    return JSONResponse(
        {
            "sources": sources,
            "default": settings.DEFAULT_SOURCE,
        }
    )
