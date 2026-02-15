"""News item data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class NewsItem(BaseModel):
    """Represents a single news article from any source."""

    title: str = Field(..., description="The title of the news article")
    url: HttpUrl = Field(..., description="The URL to the full article")
    published_at: Optional[datetime] = Field(
        None, description="The publication date and time"
    )
    source: str = Field(..., description="Source identifier (e.g., 'yahoo', 'nhk')")
    source_name: str = Field(
        ..., description="Human-readable source name (e.g., 'Yahoo News')"
    )
    summary: Optional[str] = Field(None, description="Brief summary of the article")
    image_url: Optional[HttpUrl] = Field(None, description="URL to article thumbnail")
    category: Optional[str] = Field(None, description="Article category")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
