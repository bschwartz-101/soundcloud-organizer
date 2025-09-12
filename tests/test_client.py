"""Tests for the SoundCloud API client."""

import httpx
import pytest
from authlib.integrations.httpx_client import OAuth2Client

from soundcloud_organizer.client import SoundCloudClient

# Sample API responses
STREAM_PAGE_1 = {
    "collection": [
        {
            "type": "track-repost",
            "origin": {
                "id": 1,
                "created_at": "2023-10-01T10:00:00Z",
                "title": "Track 1",
                "duration": 180000,
                "user": {"id": 10, "username": "user10"},
            },
        }
    ],
    "next_href": "https://api.soundcloud.com/me/activities/tracks?cursor=next-page",
}

STREAM_PAGE_2 = {
    "collection": [
        {
            "type": "track",
            "origin": {
                "id": 2,
                "created_at": "2023-10-02T10:00:00Z",
                "title": "Track 2",
                "duration": 240000,
                "user": {"id": 20, "username": "user20"},
            },
        }
    ],
    "next_href": None,
}

PLAYLISTS_RESPONSE = [
    {"id": 101, "title": "My Favs", "track_count": 10, "tracks": []},
    {"id": 102, "title": "2023-10", "track_count": 5, "tracks": []},
]

PLAYLIST_DETAIL_RESPONSE = {
    "id": 102,
    "title": "2023-10",
    "track_count": 1,
    "tracks": [
        {
            "id": 50,
            "created_at": "2023-10-05T10:00:00Z",
            "title": "Existing Track",
            "duration": 300000,
            "user": {"id": 30, "username": "user30"},
        }
    ],
}


@pytest.fixture
def mock_session(mocker):
    """Fixture for a mocked OAuth2Client."""
    return mocker.MagicMock(spec=OAuth2Client)


@pytest.fixture
def client(mock_session):
    """Fixture for a SoundCloudClient with a mocked session."""
    return SoundCloudClient(mock_session)


def test_get_stream_pagination(client, mock_session, mocker):
    """Test that get_stream handles pagination correctly."""
    # Mock the responses for two pages
    request = httpx.Request("GET", "https://api.soundcloud.com/me/activities/tracks")
    mock_session.get.side_effect = [
        httpx.Response(200, json=STREAM_PAGE_1, request=request),
        httpx.Response(200, json=STREAM_PAGE_2, request=request),
    ]

    stream_items = list(client.get_stream())

    assert len(stream_items) == 2
    assert stream_items[0].origin.id == 1
    assert stream_items[1].origin.id == 2

    # Check that GET was called twice with the correct URLs
    assert mock_session.get.call_count == 2
    mock_session.get.assert_any_call(
        "https://api.soundcloud.com/me/activities/tracks", params={"limit": 50}
    )
    mock_session.get.assert_any_call(
        "https://api.soundcloud.com/me/activities/tracks?cursor=next-page", params={}
    )


def test_get_my_playlists(client, mock_session):
    """Test fetching user's playlists."""
    request = httpx.Request("GET", "https://api.soundcloud.com/me/playlists")
    mock_session.get.return_value = httpx.Response(
        200, json=PLAYLISTS_RESPONSE, request=request
    )

    playlists = client.get_my_playlists()

    assert len(playlists) == 2
    assert playlists[0].id == 101
    assert playlists[1].title == "2023-10"
    mock_session.get.assert_called_once_with("https://api.soundcloud.com/me/playlists")


def test_create_playlist(client, mock_session):
    """Test creating a new playlist."""
    new_playlist_title = "New Mixes"
    created_playlist_response = {
        "id": 201,
        "title": new_playlist_title,
        "track_count": 0,
        "tracks": [],
    }
    request = httpx.Request("POST", "https://api.soundcloud.com/playlists")
    mock_session.post.return_value = httpx.Response(
        200, json=created_playlist_response, request=request
    )

    playlist = client.create_playlist(new_playlist_title, [123, 456])

    assert playlist.id == 201
    assert playlist.title == new_playlist_title

    expected_payload = {
        "playlist": {
            "title": new_playlist_title,
            "sharing": "public",
            "tracks": [{"id": 123}, {"id": 456}],
        }
    }
    mock_session.post.assert_called_once_with(
        "https://api.soundcloud.com/playlists", json=expected_payload
    )


def test_add_tracks_to_playlist_with_new_tracks(client, mock_session, mocker):
    """Test adding new tracks to a playlist, avoiding duplicates."""
    playlist_id = 102
    # One existing track (50), one new track (60)
    track_ids_to_add = [50, 60]

    # Mock the GET for the playlist details and the PUT for the update
    request = httpx.Request("GET", f"https://api.soundcloud.com/playlists/{playlist_id}")
    mock_session.get.return_value = httpx.Response(
        200, json=PLAYLIST_DETAIL_RESPONSE, request=request
    )

    # The PUT request returns the updated playlist. We need to mock this response.
    updated_playlist_response = PLAYLIST_DETAIL_RESPONSE.copy()
    updated_playlist_response["track_count"] = 2
    mock_session.put.return_value = httpx.Response(
        200, json=updated_playlist_response, request=request
    )

    client.add_tracks_to_playlist(playlist_id, track_ids_to_add)

    mock_session.get.assert_called_once_with(
        f"https://api.soundcloud.com/playlists/{playlist_id}"
    )

    # Assert PUT was called with the correct combined list of track objects.
    _, kwargs = mock_session.put.call_args
    sent_track_ids = {track["id"] for track in kwargs["json"]["playlist"]["tracks"]}
    assert sent_track_ids == {50, 60}


def test_add_tracks_to_playlist_with_no_new_tracks(client, mock_session, mocker):
    """Test that no update is sent if all tracks already exist in the playlist."""
    playlist_id = 102
    track_ids_to_add = [50]  # This track ID is already in PLAYLIST_DETAIL_RESPONSE

    request = httpx.Request("GET", f"https://api.soundcloud.com/playlists/{playlist_id}")
    mock_session.get.return_value = httpx.Response(
        200, json=PLAYLIST_DETAIL_RESPONSE, request=request
    )

    result = client.add_tracks_to_playlist(playlist_id, track_ids_to_add)

    assert result is None
    mock_session.get.assert_called_once_with(
        f"https://api.soundcloud.com/playlists/{playlist_id}"
    )
    mock_session.put.assert_not_called()
