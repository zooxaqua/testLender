"""News aggregator service."""

import asyncio
from typing import Dict, List, Optional

from backend.adapters.base import NewsAdapter
from backend.models import NewsItem


class NewsAggregator:
    """Service for aggregating news from multiple sources."""

    def __init__(self, adapters: Dict[str, NewsAdapter]):
        """Initialize the news aggregator.

        Args:
            adapters: Dictionary mapping source IDs to their adapters.
        """
        self.adapters = adapters

    async def fetch_from_sources(
        self, sources: List[str], limit_per_source: int = 10
    ) -> List[NewsItem]:
        """Fetch news from multiple sources in parallel.

        Args:
            sources: List of source IDs to fetch from.
            limit_per_source: Maximum number of items to fetch per source.

        Returns:
            Combined list of NewsItem objects from all sources.
        """
        tasks = []
        for source_id in sources:
            adapter = self.adapters.get(source_id)
            if adapter:
                tasks.append(self._fetch_with_error_handling(adapter, limit_per_source))

        # Fetch from all sources in parallel
        results = await asyncio.gather(*tasks)

        # Flatten the results
        all_items: List[NewsItem] = []
        for items in results:
            if items:
                all_items.extend(items)

        return all_items

    async def fetch_all_sources(self, limit_per_source: int = 10) -> List[NewsItem]:
        """Fetch news from all available sources.

        Args:
            limit_per_source: Maximum number of items to fetch per source.

        Returns:
            Combined list of NewsItem objects from all sources.
        """
        return await self.fetch_from_sources(
            list(self.adapters.keys()), limit_per_source
        )

    def merge_and_sort(
        self,
        items: List[NewsItem],
        limit: Optional[int] = None,
        sort_by: str = "published_at",
        sort_order: str = "desc",
    ) -> List[NewsItem]:
        """Merge news items, remove duplicates, and sort.

        Args:
            items: List of NewsItem objects to merge.
            limit: Optional maximum number of items to return.
            sort_by: Sort field ('published_at' or 'source').
            sort_order: Sort order ('asc' or 'desc').

        Returns:
            Sorted and deduplicated list of NewsItem objects.
        """
        # Remove duplicates based on URL
        seen_urls: set[str] = set()
        unique_items: List[NewsItem] = []

        for item in items:
            url = str(item.url)
            if url not in seen_urls:
                seen_urls.add(url)
                unique_items.append(item)

        # Sort items
        if sort_by == "source":
            sorted_items = sorted(
                unique_items,
                key=lambda x: x.source,
                reverse=(sort_order == "desc"),
            )
        else:  # published_at
            # Items without published_at go to the end
            sorted_items = sorted(
                unique_items,
                key=lambda x: x.published_at if x.published_at else datetime.min,
                reverse=(sort_order == "desc"),
            )

        # Apply limit if specified
        if limit is not None:
            return sorted_items[:limit]

        return sorted_items

    def filter_by_keyword(
        self, items: List[NewsItem], keyword: str
    ) -> List[NewsItem]:
        """Filter news items by keyword in title.

        Args:
            items: List of NewsItem objects.
            keyword: Keyword to search for (case-insensitive).

        Returns:
            Filtered list of NewsItem objects.
        """
        if not keyword:
            return items

        keyword_lower = keyword.lower()
        return [item for item in items if keyword_lower in item.title.lower()]

    async def fetch_and_aggregate(
        self,
        sources: Optional[List[str]] = None,
        limit: int = 20,
        limit_per_source: int = 15,
        sort_by: str = "published_at",
        sort_order: str = "desc",
        keyword: Optional[str] = None,
    ) -> List[NewsItem]:
        """Fetch news from sources, merge, deduplicate, filter, and sort.

        Args:
            sources: List of source IDs to fetch from. If None, fetch from all.
            limit: Maximum number of items to return.
            limit_per_source: Maximum number of items to fetch per source.
            sort_by: Sort field ('published_at' or 'source').
            sort_order: Sort order ('asc' or 'desc').
            keyword: Optional keyword to filter by title.

        Returns:
            Sorted and deduplicated list of NewsItem objects.
        """
        if sources is None:
            items = await self.fetch_all_sources(limit_per_source)
        else:
            items = await self.fetch_from_sources(sources, limit_per_source)

        # Filter by keyword if specified
        if keyword:
            items = self.filter_by_keyword(items, keyword)

        return self.merge_and_sort(items, limit, sort_by, sort_order)

    async def _fetch_with_error_handling(
        self, adapter: NewsAdapter, limit: int
    ) -> List[NewsItem]:
        """Fetch news with error handling.

        Args:
            adapter: The news adapter to fetch from.
            limit: Maximum number of items to fetch.

        Returns:
            List of NewsItem objects, or empty list if error occurs.
        """
        try:
            return await adapter.fetch_news(limit)
        except Exception as e:
            # Log the error but don't fail the entire aggregation
            print(f"Error fetching from {adapter.source_id}: {e}")
            return []


# Import datetime for sorting
from datetime import datetime
