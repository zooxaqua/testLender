"""Configuration settings for the news aggregator."""

from typing import Dict, List


class Settings:
    """Application settings."""

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Cache configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    MAX_LIMIT: int = 50

    # User agent for HTTP requests
    USER_AGENT: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

    # HTTP client timeout (seconds)
    HTTP_TIMEOUT: float = 10.0

    # News source configurations
    NEWS_SOURCES: Dict[str, Dict[str, str]] = {
        "yahoo": {
            "name": "Yahoo News",
            "rss_url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
            "scrape_url": "https://news.yahoo.co.jp/",
        },
        "nhk": {
            "name": "NHK News",
            "rss_url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        },
        "google": {
            "name": "Google News",
            "rss_url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
        },
    }

    # Default news source
    DEFAULT_SOURCE: str = "all"

    # Enabled sources (can be configured to enable/disable sources)
    ENABLED_SOURCES: List[str] = ["yahoo", "nhk", "google"]


# Global settings instance
settings = Settings()
