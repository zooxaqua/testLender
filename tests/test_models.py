"""Tests for data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.models import NewsItem


def test_news_item_valid():
    """Test creating a valid NewsItem."""
    item = NewsItem(
        title="Test Article",
        url="https://example.com/article",
        published_at=datetime(2026, 2, 15, 12, 0, 0),
        source="test",
        source_name="Test Source",
        summary="This is a test article",
    )
    
    assert item.title == "Test Article"
    assert str(item.url) == "https://example.com/article"
    assert item.source == "test"
    assert item.source_name == "Test Source"
    assert item.summary == "This is a test article"


def test_news_item_minimal():
    """Test creating a NewsItem with minimal fields."""
    item = NewsItem(
        title="Minimal Article",
        url="https://example.com/minimal",
        source="test",
        source_name="Test Source",
    )
    
    assert item.title == "Minimal Article"
    assert item.published_at is None
    assert item.summary is None
    assert item.image_url is None
    assert item.category is None


def test_news_item_invalid_url():
    """Test that invalid URLs are rejected."""
    with pytest.raises(ValidationError):
        NewsItem(
            title="Invalid URL",
            url="not-a-valid-url",
            source="test",
            source_name="Test Source",
        )


def test_news_item_missing_required():
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError):
        NewsItem(
            title="Missing Source",
            url="https://example.com",
        )
