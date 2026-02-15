"""NHK News adapter."""

from datetime import datetime
from typing import List

import feedparser
import httpx

from backend.adapters.base import NewsAdapter
from backend.config import settings
from backend.models import NewsItem


class NHKNewsAdapter(NewsAdapter):
    """Adapter for NHK News RSS feed."""

    def __init__(self):
        """Initialize NHK News adapter."""
        super().__init__(source_id="nhk", source_name="NHK News")
        self.rss_url = settings.NEWS_SOURCES["nhk"]["rss_url"]

    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        """Fetch news from NHK News RSS feed.

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
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except (ValueError, TypeError):
                    pass
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    published_at = datetime(*entry.updated_parsed[:6])
                except (ValueError, TypeError):
                    pass

            # Extract summary/description if available
            summary = None
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description

            items.append(
                NewsItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    published_at=published_at,
                    source=self.source_id,
                    source_name=self.source_name,
                    summary=summary,
                )
            )

        return items
