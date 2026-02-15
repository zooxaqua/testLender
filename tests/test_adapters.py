"""Tests for news adapters."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.adapters.base import NewsAdapter
from backend.adapters.yahoo_adapter import YahooNewsAdapter
from backend.models import NewsItem


class TestNewsAdapter:
    """Tests for the base NewsAdapter class."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        class TestAdapter(NewsAdapter):
            async def fetch_news(self, limit: int = 10):
                return []
        
        adapter = TestAdapter(source_id="test", source_name="Test Source")
        assert adapter.source_id == "test"
        assert adapter.source_name == "Test Source"
    
    def test_adapter_repr(self):
        """Test adapter string representation."""
        class TestAdapter(NewsAdapter):
            async def fetch_news(self, limit: int = 10):
                return []
        
        adapter = TestAdapter(source_id="test", source_name="Test Source")
        assert "TestAdapter" in repr(adapter)
        assert "test" in repr(adapter)


class TestYahooNewsAdapter:
    """Tests for Yahoo News adapter."""
    
    def test_initialization(self):
        """Test Yahoo adapter initialization."""
        adapter = YahooNewsAdapter()
        assert adapter.source_id == "yahoo"
        assert adapter.source_name == "Yahoo News"
        assert adapter.rss_url is not None
        assert adapter.scrape_url is not None
    
    @pytest.mark.asyncio
    async def test_fetch_rss_mock(self):
        """Test RSS fetching with mocked response."""
        adapter = YahooNewsAdapter()
        
        # Mock RSS response
        mock_rss_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Test Article</title>
      <link>https://news.yahoo.co.jp/articles/test123</link>
      <pubDate>Sat, 15 Feb 2026 12:00:00 +0900</pubDate>
    </item>
  </channel>
</rss>"""
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.text = mock_rss_content
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            items = await adapter._fetch_rss(limit=5)
            
            assert len(items) >= 1
            assert items[0].title == "Test Article"
            assert items[0].source == "yahoo"
    
    def test_merge_items_removes_duplicates(self):
        """Test that merge_items removes duplicate URLs."""
        adapter = YahooNewsAdapter()
        
        item1 = NewsItem(
            title="Article 1",
            url="https://example.com/article",
            source="yahoo",
            source_name="Yahoo News",
        )
        item2 = NewsItem(
            title="Article 1 Duplicate",
            url="https://example.com/article",  # Same URL
            source="yahoo",
            source_name="Yahoo News",
        )
        item3 = NewsItem(
            title="Article 2",
            url="https://example.com/article2",
            source="yahoo",
            source_name="Yahoo News",
        )
        
        merged = adapter._merge_items([item1, item2], [item3], limit=10)
        
        assert len(merged) == 2
        assert merged[0].url == item1.url
        assert merged[1].url == item3.url
