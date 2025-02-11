from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class URLModel(BaseModel):
    """Schema for storing URLs in MongoDB"""
    short_url: str = Field(..., alias="_id")
    long_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    click_count: int = 0

    model_config = ConfigDict(populate_by_name=True)  # Ensure alias `_id` works


class URLCreate(BaseModel):
    """Schema for creating a short URL"""
    long_url: str


class URLResponse(BaseModel):
    """Schema for returning a short URL"""
    short_url: str
    long_url: str
    created_at: datetime
    click_count: int
