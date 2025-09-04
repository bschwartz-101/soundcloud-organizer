"""Tests for the processor module."""

from datetime import datetime

import pytest
from rich.console import Console

from soundcloud_organizer.models import Playlist, StreamItem, Track, User
from soundcloud_organizer.processor import (
    TrackLengthFilter,
    process_stream,
    track_matches_filter,
)


# Helper to create a mock track
def create_mock_track(id: int, duration_ms: int, created_at: str) -> Track:
    return Track(
        id=id,
        created_at=datetime.fromisoformat(created_at),
        title=f"Track {id}",
        duration=duration_ms,
        user=User(id=1, username="testuser"),
    )


@pytest.mark.parametrize(
    "duration_ms, length_filter, expected",
    [
        # Short filter (< 5 mins)
        (299_999, TrackLengthFilter.SHORT, True),  # Just under 5 mins
        (300_000, TrackLengthFilter.SHORT, False),  # Exactly 5 mins
        (600_000, TrackLengthFilter.SHORT, False),  # 10 mins
        # Medium filter (5-20 mins)
        (299_999, TrackLengthFilter.MEDIUM, False),  # Just under 5 mins
        (300_000, TrackLengthFilter.MEDIUM, True),  # Exactly 5 mins
        (1_200_000, TrackLengthFilter.MEDIUM, True),  # Exactly 20 mins
        (1_200_001, TrackLengthFilter.MEDIUM, False),  # Just over 20 mins
        # Long filter (> 20 mins)
        (1_200_000, TrackLengthFilter.LONG, False),  # Exactly 20 mins
        (1_200_001, TrackLengthFilter.LONG, True),  # Just over 20 mins
        (3_600_000, TrackLengthFilter.LONG, True),  # 60 mins
        # All filter
        (10_000, TrackLengthFilter.ALL, True),
        (600_000, TrackLengthFilter.ALL, True),
        (3_600_000, TrackLengthFilter.ALL, True),
    ],
)
def test_track_matches_filter(duration_ms, length_filter, expected):
    """Test the track_matches_filter function with various durations."""
    track = create_mock_track(1, duration_ms, "2023-10-10T10:00:00Z")
    assert track_matches_filter(track, length_filter) == expected


def test_process_stream_creates_new_playlist(mocker):
    """Test that a new playlist is created when one doesn't exist."""
    mock_client = mocker.MagicMock()
    mock_console = mocker.MagicMock(spec=Console)

    # Stream has one short track from Oct 2023
    track1 = create_mock_track(101, 180_000, "2023-10-15T12:00:00Z")
    mock_client.get_stream.return_value = [StreamItem(type="track", origin=track1)]

    # No existing playlists
    mock_client.get_my_playlists.return_value = []

    # Mock the create_playlist call
    created_playlist = Playlist(id=1, title="2023-10", track_count=0, tracks=[])
    mock_client.create_playlist.return_value = created_playlist

    process_stream(mock_client, TrackLengthFilter.SHORT, mock_console)

    # Assertions
    mock_client.get_stream.assert_called_once()
    mock_client.get_my_playlists.assert_called_once()
    mock_client.create_playlist.assert_called_once_with("2023-10")
    mock_client.add_tracks_to_playlist.assert_called_once_with(
        created_playlist.id, [track1.id]
    )


def test_process_stream_uses_existing_playlist(mocker):
    """Test that an existing playlist is used if found."""
    mock_client = mocker.MagicMock()
    mock_console = mocker.MagicMock(spec=Console)

    # Stream has one long track from Nov 2023
    track1 = create_mock_track(202, 1_800_000, "2023-11-20T12:00:00Z")
    mock_client.get_stream.return_value = [StreamItem(type="track", origin=track1)]

    # An existing playlist for Nov 2023
    existing_playlist = Playlist(id=2, title="2023-11", track_count=5, tracks=[])
    mock_client.get_my_playlists.return_value = [existing_playlist]

    process_stream(mock_client, TrackLengthFilter.LONG, mock_console)

    # Assertions
    mock_client.create_playlist.assert_not_called()
    mock_client.add_tracks_to_playlist.assert_called_once_with(
        existing_playlist.id, [track1.id]
    )


def test_process_stream_groups_tracks_by_month(mocker):
    """Test that tracks are correctly grouped into different monthly playlists."""
    mock_client = mocker.MagicMock()
    mock_console = mocker.MagicMock(spec=Console)

    # Stream has tracks from two different months
    track_oct = create_mock_track(101, 180_000, "2023-10-15T12:00:00Z")
    track_nov = create_mock_track(202, 180_000, "2023-11-20T12:00:00Z")
    mock_client.get_stream.return_value = [
        StreamItem(type="track", origin=track_oct),
        StreamItem(type="track", origin=track_nov),
    ]

    # No existing playlists
    mock_client.get_my_playlists.return_value = []
    mock_client.create_playlist.side_effect = [
        Playlist(id=1, title="2023-10", track_count=0, tracks=[]),
        Playlist(id=2, title="2023-11", track_count=0, tracks=[]),
    ]

    process_stream(mock_client, TrackLengthFilter.ALL, mock_console)

    assert mock_client.create_playlist.call_count == 2
    mock_client.add_tracks_to_playlist.assert_any_call(1, [track_oct.id])
    mock_client.add_tracks_to_playlist.assert_any_call(2, [track_nov.id])
