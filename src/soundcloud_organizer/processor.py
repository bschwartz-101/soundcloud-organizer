"""Houses the core logic for filtering tracks and processing the stream."""

from collections import defaultdict
from datetime import datetime
from enum import Enum

from loguru import logger
from rich.console import Console

from soundcloud_organizer.client import SoundCloudClient
from soundcloud_organizer.models import Track
from soundcloud_organizer.scope_parser import parse_scope

# Number of consecutive tracks older than the scope to see before stopping.
CONSECUTIVE_OUT_OF_SCOPE_LIMIT = 25


class TrackLengthFilter(str, Enum):
    """Enum for track length filtering options."""

    SHORT = "short"  # < 5 minutes
    MEDIUM = "medium"  # 5-20 minutes
    LONG = "long"  # > 20 minutes
    ALL = "all"


def track_matches_filter(track: Track, length_filter: TrackLengthFilter) -> bool:
    """
    Checks if a track's duration matches the specified length filter.

    Args:
        track: The Track object to check.
        length_filter: The filter to apply.

    Returns:
        True if the track matches the filter, False otherwise.
    """
    duration_minutes = track.duration / 1000 / 60
    if length_filter == TrackLengthFilter.SHORT:
        return duration_minutes < 5
    if length_filter == TrackLengthFilter.MEDIUM:
        return 5 <= duration_minutes <= 20
    if length_filter == TrackLengthFilter.LONG:
        return duration_minutes > 20
    if length_filter == TrackLengthFilter.ALL:
        return True
    return False


def track_matches_scope(
    track: Track, date_range: tuple[datetime, datetime] | None
) -> bool:
    """
    Checks if a track's creation date falls within the specified date range.

    Args:
        track: The Track object to check.
        date_range: A tuple of (start_date, end_date) or None.

    Returns:
        True if the track is within the scope, False otherwise.
    """
    if date_range is None:
        return True  # No scope provided, so all tracks match
    return date_range[0] <= track.created_at <= date_range[1]


def process_stream(
    client: SoundCloudClient,
    length_filter: TrackLengthFilter,
    console: Console,
    dry_run: bool = False,
    scope: str | None = None,
):
    """
    Fetches the stream, filters tracks, and adds them to monthly playlists.

    Args:
        client: An authenticated SoundCloudClient.
        length_filter: The track length filter to apply.
        console: A rich Console instance for output.
        dry_run: If True, only print actions without performing them.
        scope: Optional time interval to filter tracks by.
    """
    logger.info(f"Fetching stream and filtering for '{length_filter.value}' tracks...")

    date_range = None
    if scope:
        logger.info(f"Filtering for time interval: '{scope}'")
        # ValueError is handled upstream in main.py
        date_range = parse_scope(scope)

    tracks_by_playlist = defaultdict(list)
    consecutive_out_of_scope_count = 0

    # 1. Fetch stream, filter, and group tracks by target playlist name
    for item in client.get_stream():
        track = item.origin
        if not track:
            continue

        is_in_scope = track_matches_scope(track, date_range)
        is_length_match = track_matches_filter(track, length_filter)

        if is_in_scope and is_length_match:
            playlist_name = track.created_at.strftime("%Y-%m")
            tracks_by_playlist[playlist_name].append(track)
            logger.debug(
                f"Found matching track: '{track.title}' -> Playlist '{playlist_name}'"
            )
            # Reset counter on a successful match
            consecutive_out_of_scope_count = 0
        else:
            # If a scope is defined and the track is older than the start date
            if date_range and track.created_at < date_range[0]:
                consecutive_out_of_scope_count += 1
                logger.debug(
                    f"Skipping older track: '{track.title}' ({track.created_at.date()}) "
                    f"({consecutive_out_of_scope_count}/{CONSECUTIVE_OUT_OF_SCOPE_LIMIT})[/dim]"
                )

        # If we hit the limit, stop processing the stream.
        if (
            date_range
            and consecutive_out_of_scope_count >= CONSECUTIVE_OUT_OF_SCOPE_LIMIT
        ):
            logger.info("Stopping early: Found enough consecutive older tracks.")
            break

    if not tracks_by_playlist:
        logger.info("No new matching tracks found in your stream.")
        return

    if dry_run:
        console.print("\n[bold yellow]-- DRY RUN --[/bold yellow]")
        console.print("The following actions would be taken:")
        for playlist_name, tracks in tracks_by_playlist.items():
            track_titles = "\n".join([f"  - '{t.title}'" for t in tracks])
            console.print(f"\n[bold cyan]Playlist '{playlist_name}':[/bold cyan]")
            console.print(f"Would add {len(tracks)} track(s):\n{track_titles}")
        return

    logger.info("Processing playlists...")

    # 2. Get existing playlists to avoid re-creating them
    existing_playlists = {p.title: p for p in client.get_my_playlists()}

    # 3. Iterate through grouped tracks and add them to playlists
    for playlist_name, tracks in tracks_by_playlist.items():
        track_ids = [track.id for track in tracks]
        playlist = existing_playlists.get(playlist_name)

        if not playlist:
            logger.info(f"Creating new playlist: '{playlist_name}'")
            logger.info(
                f"Adding {len(track_ids)} track(s) to new playlist '{playlist_name}'..."
            )
            try:
                # Create the playlist and add tracks in one API call
                playlist = client.create_playlist(playlist_name, track_ids)
                existing_playlists[playlist_name] = playlist  # Add to our cache
            except Exception as e:
                logger.exception(f"Error creating playlist {playlist_name}: {e}")
        else:
            # If the playlist exists, add only the new tracks
            logger.info(
                f"Adding {len(track_ids)} track(s) to existing playlist '{playlist_name}'..."
            )
            client.add_tracks_to_playlist(playlist.id, track_ids)

    logger.info("✅ Processing complete!")
