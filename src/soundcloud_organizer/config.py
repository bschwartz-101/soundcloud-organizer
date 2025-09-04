"""Manages loading and saving of configuration data."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

APP_NAME = "soundcloud-organizer"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"


class Token(BaseModel):
    """Pydantic model for storing OAuth2 token data."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: float
    scope: str


class Settings(BaseModel):
    """Pydantic model for app settings."""

    client_id: Optional[str] = Field(None, description="SoundCloud API Client ID")
    client_secret: Optional[str] = Field(None, description="SoundCloud API Client Secret")
    token: Optional[Token] = Field(None, description="Stored OAuth2 token")


def load_settings() -> Settings:
    """Loads settings from the config file."""
    if not CONFIG_FILE.exists():
        return Settings()
    return Settings.model_validate_json(CONFIG_FILE.read_text())


def save_settings(settings: Settings) -> None:
    """Saves settings to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(settings.model_dump_json(indent=4))