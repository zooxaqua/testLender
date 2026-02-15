"""Tests for news aggregator service."""

import pytest
from datetime import datetime

from backend.models import NewsItem
from backend.services.aggregator import NewsAggregator
from backend.adapters.base import NewsAdapter


class MockAdapter(NewsAdapter):
    """Mock adapter for testing."""
    
    def __init__(self, source_id: str, source_name: str, items: list):
        super().__init__(source_id, source_name)
        self.items = items
    
    async def fetch_news(self, limit: int = 10):
        return self.items[:limit]


class TestNewsAggregator:
    """Tests for NewsAggregator service."""
    
    def test_initialization(self):
        """Test aggregator initialization."""
        adapters = {
            "test1": MockAdapter("test1", "Test 1", []),
            "test2": MockAdapter("test2", "Test 2", []),
        }
        aggregator = NewsAggregator(adapters)
        assert len(aggregator.adapters) == 2
    
    @pytest.mark.asyncio
    async def test_fetch_from_single_source(self):
        """Test fetching from a single source."""
        items = [
            NewsItem(
                title="Article 1",
                url="https://example.com/1",
                source="test",
                source_name="Test Source",
            ),
            NewsItem(
                title="Article 2",
                url="https://example.com/2",
                source="test",
                source_name="Test Source",
            ),
        ]
        
        adapters = {"test": MockAdapter("test", "Test Source", items)}
        aggregator = NewsAggregator(adapters)
        
        result = await aggregator.fetch_from_sources(["test"], limit_per_source=10)
        
        assert len(result) == 2
        assert result[0].title == "Article 1"
    
    @pytest.mark.asyncio
    async def test_fetch_from_multiple_sources(self):
        """Test fetching from multiple sources."""
        items1 = [
            NewsItem(
                title="Source 1 Article",
                url="https://example.com/s1",
                source="test1",
                source_name="Test Source 1",
            ),
        ]
        items2 = [
            NewsItem(
                title="Source 2 Article",
                url="https://example.com/s2",
                source="test2",
                source_name="Test Source 2",
            ),
        ]
        
        adapters = {
            "test1": MockAdapter("test1", "Test Source 1", items1),
            "test2": MockAdapter("test2", "Test Source 2", items2),
        }
        aggregator = NewsAggregator(adapters)
        
        result = await aggregator.fetch_from_sources(["test1", "test2"])
        
        assert len(result) == 2
    
    def test_merge_and_sort_by_date(self):
        """Test merging and sorting by published date."""
        items = [
            NewsItem(
                title="Older",
                url="https://example.com/1",
                published_at=datetime(2026, 2, 14, 10, 0),
                source="test",
                source_name="Test",
            ),
            NewsItem(
                title="Newer",
                url="https://example.com/2",
                published_at=datetime(2026, 2, 15, 10, 0),
                source="test",
                source_name="Test",
            ),
        ]
        
        aggregator = NewsAggregator({})
        sorted_items = aggregator.merge_and_sort(
            items, sort_by="published_at", sort_order="desc"
        )
        
        assert sorted_items[0].title == "Newer"
        assert sorted_items[1].title == "Older"
    
    def test_merge_and_sort_by_source(self):
        """Test merging and sorting by source."""
        items = [
            NewsItem(
                title="Yahoo Article",
                url="https://example.com/1",
                source="yahoo",
                source_name="Yahoo News",
            ),
            NewsItem(
                title="Google Article",
                url="https://example.com/2",
                source="google",
                source_name="Google News",
            ),
        ]
        
        aggregator = NewsAggregator({})
        sorted_items = aggregator.merge_and_sort(
            items, sort_by="source", sort_order="asc"
        )
        
        assert sorted_items[0].source == "google"
        assert sorted_items[1].source == "yahoo"
    
    def test_filter_by_keyword(self):
        """Test keyword filtering."""
        items = [
            NewsItem(
                title="Technology News Article",
                url="https://example.com/1",
                source="test",
                source_name="Test",
            ),
            NewsItem(
                title="Sports Update",
                url="https://example.com/2",
                source="test",
                source_name="Test",
            ),
            NewsItem(
                title="Technology Innovation",
                url="https://example.com/3",
                source="test",
                source_name="Test",
            ),
        ]
        
        aggregator = NewsAggregator({})
        filtered = aggregator.filter_by_keyword(items, "technology")
        
        assert len(filtered) == 2
        assert all("technology" in item.title.lower() for item in filtered)
    
    def test_filter_by_keyword_case_insensitive(self):
        """Test that keyword filtering is case-insensitive."""
        items = [
            NewsItem(
                title="TECHNOLOGY News",
                url="https://example.com/1",
                source="test",
                source_name="Test",
            ),
        ]
        
        aggregator = NewsAggregator({})
        filtered = aggregator.filter_by_keyword(items, "technology")
        
        assert len(filtered) == 1
    
    def test_remove_duplicates(self):
        """Test that duplicate URLs are removed."""
        items = [
            NewsItem(
                title="Article 1",
                url="https://example.com/article",
                source="test",
                source_name="Test",
            ),
            NewsItem(
                title="Article 1 Duplicate",
                url="https://example.com/article",  # Same URL
                source="test",
                source_name="Test",
            ),
            NewsItem(
                title="Article 2",
                url="https://example.com/article2",
                source="test",
                source_name="Test",
            ),
        ]
        
        aggregator = NewsAggregator({})
        unique = aggregator.merge_and_sort(items)
        
        assert len(unique) == 2
