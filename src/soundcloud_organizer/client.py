"""SoundCloud API client for interacting with the SoundCloud API."""

from typing import Iterator, List, Optional

from loguru import logger
from requests_oauthlib import OAuth2Session

from soundcloud_organizer.models import Playlist, StreamItem

API_BASE_URL = "https://api.soundcloud.com"


class SoundCloudClient:
    """A client for interacting with the SoundCloud API."""

    def __init__(self, session: OAuth2Session):
        """
        Initializes the SoundCloudClient.

        Args:
            session: An authenticated OAuth2Session instance.
        """
        self.session = session
        self.base_url = API_BASE_URL

    def get_stream(self) -> Iterator[StreamItem]:
        """
        Fetches the user's activity stream and yields stream items.

        This method handles pagination automatically, fetching pages until the
        stream is exhausted.

        Yields:
            StreamItem: An item from the user's activity stream.
        """
        url = f"{self.base_url}/me/activities/tracks"
        params = {"limit": 50}  # Use a reasonable page size

        while url:
            logger.debug(f"Fetching stream page: GET {url}")
            response = self.session.get(url, params=params)
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

            for item_data in data.get("collection", []):
                # Only yield items that are tracks or reposts of tracks and have an origin
                if item_data.get("type") in ["track", "track-repost"] and item_data.get(
                    "origin"
                ):
                    yield StreamItem.model_validate(item_data)

            # Get the next page URL, and clear params as next_href is a full URL
            url = data.get("next_href")
            if url:
                params = {}

    def get_my_playlists(self) -> List[Playlist]:
        """
        Fetches all playlists for the authenticated user.

        Returns:
            A list of Playlist objects.
        """
        url = f"{self.base_url}/me/playlists"
        logger.debug(f"Fetching user playlists: GET {url}")
        response = self.session.get(url)
        logger.debug(f"Response status: {response.status_code}")
        response.raise_for_status()
        playlists_data = response.json()
        return [Playlist.model_validate(p) for p in playlists_data]

    def create_playlist(self, title: str, track_ids: List[int]) -> Playlist:
        """
        Creates a new public playlist with an initial set of tracks.

        Args:
            title: The title of the new playlist.
            track_ids: A list of track IDs to add to the new playlist.

        Returns:
            The newly created Playlist object.
        """
        url = f"{self.base_url}/playlists"
        logger.debug(f"Creating playlist '{title}': POST {url}")
        track_payload = [{"id": track_id} for track_id in track_ids]
        payload = {
            "playlist": {
                "title": title,
                "sharing": "public",
                "tracks": track_payload,
            }
        }
        response = self.session.post(url, json=payload)
        logger.debug(f"Response status: {response.status_code}")
        response.raise_for_status()
        return Playlist.model_validate(response.json())

    def add_tracks_to_playlist(
        self, playlist_id: int, track_ids: List[int]
    ) -> Optional[Playlist]:
        """
        Adds tracks to a playlist, avoiding duplicates.

        Args:
            playlist_id: The ID of the playlist to modify.
            track_ids: A list of track IDs to add.

        Returns:
            The updated Playlist object if changes were made, otherwise None.
        """
        # 1. Get the full playlist object to ensure we have all its current tracks
        playlist_url = f"{self.base_url}/playlists/{playlist_id}"
        logger.debug(f"Fetching playlist details: GET {playlist_url}")
        response = self.session.get(playlist_url)
        logger.debug(f"Response status: {response.status_code}")
        response.raise_for_status()
        playlist = Playlist.model_validate(response.json())

        # 2. Create a set of existing track IDs for efficient lookup
        existing_track_ids = {track.id for track in playlist.tracks}

        # 3. Determine which of the new tracks are not already in the playlist
        new_track_ids = [
            track_id for track_id in track_ids if track_id not in existing_track_ids
        ]

        if not new_track_ids:
            logger.debug(f"No new tracks to add to playlist '{playlist.title}'.")
            return None

        # 4. The SoundCloud API has a limit on how many tracks can be in a playlist
        # (around 500) and how many can be sent in a single PUT request. To avoid
        # a 422 error, we add tracks in batches.
        logger.info(
            f"Adding {len(new_track_ids)} new track(s) to playlist '{playlist.title}' in batches."
        )
        current_track_ids = list(existing_track_ids)

        # Add new tracks in chunks of 50 to stay well within API limits
        for i in range(0, len(new_track_ids), 50):
            batch_ids = new_track_ids[i : i + 50]
            current_track_ids.extend(batch_ids)
            track_payload = [{"id": track_id} for track_id in current_track_ids]

            logger.debug(
                f"Updating playlist '{playlist.title}' with batch of {len(batch_ids)} tracks..."
            )
            response = self.session.put(
                playlist_url, json={"playlist": {"tracks": track_payload}}
            )
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()

        # After the final batch, we can return the updated playlist object
        return Playlist.model_validate(response.json())
