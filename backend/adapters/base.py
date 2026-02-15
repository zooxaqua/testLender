"""Base adapter class for news sources."""

from abc import ABC, abstractmethod
from typing import List

from backend.models import NewsItem


class NewsAdapter(ABC):
    """Abstract base class for news source adapters."""

    def __init__(self, source_id: str, source_name: str):
        """Initialize the adapter.

        Args:
            source_id: Unique identifier for the source (e.g., 'yahoo')
            source_name: Human-readable name (e.g., 'Yahoo News')
        """
        self.source_id = source_id
        self.source_name = source_name

    @abstractmethod
    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        """Fetch news articles from the source.

        Args:
            limit: Maximum number of articles to fetch.

        Returns:
            List of NewsItem objects.

        Raises:
            Exception: If fetching fails.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(source_id='{self.source_id}')"
