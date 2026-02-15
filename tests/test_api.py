"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_sources_endpoint(self):
        """Test sources listing endpoint."""
        response = client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "default" in data
        assert len(data["sources"]) > 0
    
    def test_news_endpoint_default(self):
        """Test news endpoint with default parameters."""
        response = client.get("/api/news")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_news_endpoint_with_limit(self):
        """Test news endpoint with limit parameter."""
        response = client.get("/api/news?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_news_endpoint_with_specific_source(self):
        """Test news endpoint with specific source."""
        response = client.get("/api/news?sources=yahoo&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All items should be from yahoo
        for item in data:
            assert item["source"] == "yahoo"
    
    def test_news_endpoint_with_sort(self):
        """Test news endpoint with sorting."""
        response = client.get("/api/news?sort_by=published_at&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_news_endpoint_with_keyword(self):
        """Test news endpoint with keyword filter."""
        response = client.get("/api/news?keyword=news&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_news_endpoint_invalid_limit(self):
        """Test news endpoint with invalid limit."""
        # Limit too high should be clamped
        response = client.get("/api/news?limit=1000")
        assert response.status_code == 422  # Validation error
    
    def test_root_endpoint(self):
        """Test root endpoint serves HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "News Aggregator" in response.text
