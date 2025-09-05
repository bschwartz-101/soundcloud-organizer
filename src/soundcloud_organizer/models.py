"""Pydantic models for SoundCloud API objects."""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("created_at", mode="before")
    @classmethod
    def _parse_datetime(cls, v: Any) -> Any:
        """
        Handles multiple datetime formats from the SoundCloud API.

        The API can return ISO format ('YYYY-MM-DDTHH:MM:SSZ') or an older
        format ('YYYY/MM/DD HH:MM:SS +0000').
        """
        if isinstance(v, str):
            # Replace slashes and remove the timezone for consistent parsing
            v_normalized = v.replace("/", "-").split(" +")[0]
            return v_normalized
        return v


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

    model_config = ConfigDict(extra="ignore")
