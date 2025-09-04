"""Houses the core logic for filtering tracks and processing the stream."""

from collections import defaultdict
from enum import Enum

from rich.console import Console

from soundcloud_organizer.client import SoundCloudClient
from soundcloud_organizer.models import Track


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


def process_stream(client: SoundCloudClient, length_filter: TrackLengthFilter, console: Console):
    """
    Fetches the stream, filters tracks, and adds them to monthly playlists.

    Args:
        client: An authenticated SoundCloudClient.
        length_filter: The track length filter to apply.
        console: A rich Console instance for output.
    """
    console.print(f"Fetching stream and filtering for '{length_filter.value}' tracks...", style="yellow")

    tracks_by_playlist = defaultdict(list)

    # 1. Fetch stream, filter, and group tracks by target playlist name
    for item in client.get_stream():
        track = item.origin
        if track and track_matches_filter(track, length_filter):
            playlist_name = track.created_at.strftime("%Y-%m")
            tracks_by_playlist[playlist_name].append(track.id)
            console.log(f"Found matching track: '{track.title}' -> Playlist '{playlist_name}'")

    if not tracks_by_playlist:
        console.print("No new matching tracks found in your stream.", style="bold green")
        return

    console.print("\nProcessing playlists...", style="yellow")

    # 2. Get existing playlists to avoid re-creating them
    existing_playlists = {p.title: p for p in client.get_my_playlists()}

    # 3. Iterate through grouped tracks and add them to playlists
    for playlist_name, track_ids in tracks_by_playlist.items():
        playlist = existing_playlists.get(playlist_name)

        if not playlist:
            console.print(f"Creating new playlist: '{playlist_name}'")
            try:
                playlist = client.create_playlist(playlist_name)
                existing_playlists[playlist_name] = playlist  # Add to our cache
            except Exception as e:
                console.print(f"Error creating playlist {playlist_name}: {e}", style="bold red")
                continue

        console.print(f"Adding {len(track_ids)} track(s) to playlist '{playlist.title}'...")
        client.add_tracks_to_playlist(playlist.id, track_ids)

    console.print("\n✅ Processing complete!", style="bold green")
