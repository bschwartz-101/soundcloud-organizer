"""Pydantic models for SoundCloud API objects."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents a SoundCloud user."""

    id: int
    username: str


class Track(BaseModel):
    """Represents a SoundCloud track."""

    id: int
    created_at: datetime
    title: str
    duration: int  # in milliseconds
    user: User


class Playlist(BaseModel):
    """Represents a SoundCloud playlist."""

    id: int
    title: str
    track_count: int
    tracks: List[Track] = Field(default_factory=list)


class StreamItem(BaseModel):
    """Represents an item from the user's activity stream (e.g., a track or repost)."""

    type: str  # e.g., 'track', 'track-repost'
    origin: Optional[Track] = None

    class Config:
        # The 'origin' field in the API can sometimes be missing for certain item types
        extra = "ignore"
