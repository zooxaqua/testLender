"""News source adapters."""

from .base import NewsAdapter
from .google_adapter import GoogleNewsAdapter
from .nhk_adapter import NHKNewsAdapter
from .yahoo_adapter import YahooNewsAdapter

__all__ = ["NewsAdapter", "YahooNewsAdapter", "NHKNewsAdapter", "GoogleNewsAdapter"]
