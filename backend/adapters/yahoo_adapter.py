"""Yahoo News adapter."""

from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urljoin

import feedparser
import httpx
from bs4 import BeautifulSoup

from backend.adapters.base import NewsAdapter
from backend.config import settings
from backend.models import NewsItem


class YahooNewsAdapter(NewsAdapter):
    """Adapter for Yahoo News (RSS + Web Scraping)."""

    def __init__(self):
        """Initialize Yahoo News adapter."""
        super().__init__(source_id="yahoo", source_name="Yahoo News")
        self.rss_url = settings.NEWS_SOURCES["yahoo"]["rss_url"]
        self.scrape_url = settings.NEWS_SOURCES["yahoo"]["scrape_url"]

    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        """Fetch news from Yahoo News using both RSS and scraping.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects merged from RSS and scraping.
        """
        # Fetch from both sources in parallel
        rss_items = await self._fetch_rss(limit)
        scrape_items = await self._fetch_scrape(limit)

        # Merge and deduplicate
        return self._merge_items(rss_items, scrape_items, limit)

    async def fetch_rss_only(self, limit: int = 10) -> List[NewsItem]:
        """Fetch news from RSS feed only.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects from RSS.
        """
        return await self._fetch_rss(limit)

    async def fetch_scrape_only(self, limit: int = 10) -> List[NewsItem]:
        """Fetch news from web scraping only.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects from scraping.
        """
        return await self._fetch_scrape(limit)

    async def _fetch_rss(self, limit: int) -> List[NewsItem]:
        """Fetch news from RSS feed.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects.
        """
        async with httpx.AsyncClient(
            timeout=settings.HTTP_TIMEOUT, headers={"User-Agent": settings.USER_AGENT}
        ) as client:
            response = await client.get(self.rss_url)
            response.raise_for_status()

        feed = feedparser.parse(response.text)
        items: List[NewsItem] = []

        for entry in feed.entries[:limit]:
            # Parse published date
            published_at = None
            published_str = entry.get("published") or entry.get("updated")
            if published_str:
                try:
                    # feedparser usually parses the date into a struct_time
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                except (ValueError, TypeError):
                    pass

            items.append(
                NewsItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    published_at=published_at,
                    source=self.source_id,
                    source_name=self.source_name,
                )
            )

        return items

    async def _fetch_scrape(self, limit: int) -> List[NewsItem]:
        """Fetch news from web scraping.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects.
        """
        async with httpx.AsyncClient(
            timeout=settings.HTTP_TIMEOUT, headers={"User-Agent": settings.USER_AGENT}
        ) as client:
            response = await client.get(self.scrape_url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        items: List[NewsItem] = []
        seen: set[str] = set()

        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue

            # Filter for news article links
            if (
                "news.yahoo.co.jp/articles/" not in href
                and not href.startswith("/articles/")
            ):
                continue

            title = " ".join(anchor.get_text(strip=True).split())
            if not title:
                continue

            url = urljoin(self.scrape_url, href)
            if url in seen:
                continue

            seen.add(url)
            items.append(
                NewsItem(
                    title=title,
                    url=url,
                    published_at=None,
                    source=self.source_id,
                    source_name=self.source_name,
                )
            )

            if len(items) >= limit:
                break

        return items

    def _merge_items(
        self, primary: List[NewsItem], secondary: List[NewsItem], limit: int
    ) -> List[NewsItem]:
        """Merge news items from multiple sources and remove duplicates.

        Args:
            primary: Primary list of news items.
            secondary: Secondary list of news items.
            limit: Maximum number of items to return.

        Returns:
            Merged and deduplicated list of NewsItem objects.
        """
        merged: List[NewsItem] = []
        seen: set[str] = set()

        for item in primary + secondary:
            url = str(item.url)
            if url in seen:
                continue
            seen.add(url)
            merged.append(item)
            if len(merged) >= limit:
                break

        return merged
