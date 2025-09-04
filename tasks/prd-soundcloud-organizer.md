# Product Requirements Document: SoundCloud Organizer

## 1. Introduction/Overview

This document outlines the requirements for a SoundCloud Organizer application. The primary goal of this application is to help users automatically discover, filter, and organize music from their SoundCloud stream. The application will function as a command-line tool that can be run manually or on a schedule. It will connect to a user's SoundCloud account, fetch tracks from their main activity stream, filter them based on track length, and sort them into monthly playlists.

## 2. Goals

- **Automate Music Curation:** Automatically process a user's SoundCloud stream to find and save relevant tracks, reducing manual effort.
- **Organize Discoveries:** Create a structured library of music by sorting tracks into monthly playlists.
- **Improve Listening Experience:** Allow users to easily find tracks of a specific length (e.g., long mixes, short tracks) that are otherwise hard to filter for on SoundCloud.

## 3. User Stories

- **As a user**, I want to securely authorize the application with my SoundCloud account via an OAuth login flow so that it can access my stream and manage my playlists on my behalf.
- **As a user**, I want the application to fetch all new tracks from my main activity stream so that I don't miss any recommendations.
- **As a user**, I want to filter these tracks by preset length categories ("Short", "Medium", "Long") so I can easily find music that fits my listening habits.
- **As a user**, I want the application to automatically create new public playlists for each month and year (e.g., `2023-10`) to store the filtered tracks.
- **As a user**, I want the application to add new tracks to an existing monthly playlist if one already exists, so I don't have duplicate playlists.
- **As a user**, I want the application to be a command-line tool that I can run whenever I want or set up on a schedule (e.g., daily) for a "set it and forget it" experience.

## 4. Functional Requirements

1.  **Authentication:**
    -   FR1.1: The system must guide the user through a one-time SoundCloud OAuth 2.0 authorization flow to grant the application access.
    -   FR1.2: The application must securely store the obtained OAuth token (e.g., in a local configuration file) for subsequent runs.
    -   FR1.3: The application must use the stored token to authenticate with the SoundCloud API on startup.

2.  **Track Fetching:**
    -   FR2.1: The system must fetch tracks from the user's main activity stream (homepage feed).

3.  **Filtering:**
    -   FR3.1: The system must filter the fetched tracks based on their duration.
    -   FR3.2: The user must be able to select from three preset filter ranges:
        -   "Short": Tracks less than 5 minutes long.
        -   "Medium": Tracks between 5 and 20 minutes long.
        -   "Long": Tracks longer than 20 minutes.

4.  **Playlist Management:**
    -   FR4.1: For each filtered track, the system must determine the target playlist name based on the track's creation date using the format `YYYY-MM` (e.g., `2023-10`).
    -   FR4.2: The system must check if a playlist with the target name already exists in the user's account.
    -   FR4.3: If the playlist does not exist, the system must create a new **public** playlist with that name.
    -   FR4.4: The system must add the filtered track to the corresponding monthly playlist.

5.  **Duplicate Handling:**
    -   FR5.1: Before adding a track to a playlist, the system must check if that track is already in the target playlist.
    -   FR5.2: If the track already exists in the playlist, the system must skip it and not add it again.

6.  **Execution:**
    -   FR6.1: The application must be a Command-Line Interface (CLI) tool.
    -   FR6.2: The application must be executable from a terminal and suitable for being run by a scheduler (e.g., cron job).

## 5. Non-Goals (Out of Scope)

- **User Interface (UI):** This is a CLI-only tool. There will be no graphical user interface (GUI).
- **Advanced Filtering:** Filtering will be limited to the three preset duration ranges. There will be no support for custom ranges, genre, or other metadata filtering in this version.
- **Multiple Account Support:** The application will only support connecting to one SoundCloud account at a time.
- **Username/Password Login:** The application will not ask for or handle user passwords directly.
- **Editing or Deleting Playlists:** The application will only create playlists and add tracks. It will not modify playlist details or delete playlists/tracks.
- **Backfilling Old Tracks:** The tool will only process tracks currently available in the activity stream at the time of running. It will not go through the user's entire SoundCloud history.

## 6. Technical Considerations

- **Technology Stack:** The application will be built using **Python**. Dependency and environment management will be handled by **uv**.
- **SoundCloud API:** The application will need a library to interact with the SoundCloud API. This will require obtaining API credentials (client ID, client secret) from SoundCloud for the OAuth flow.
- **OAuth Flow in CLI:** Implementing an OAuth flow in a CLI application typically requires temporarily running a local web server to handle the redirect callback from SoundCloud. The application must be able to capture the authorization code from the redirect.
- The application should be designed to be idempotent, meaning running it multiple times will not create duplicate entries or playlists.

## 7. Success Metrics

- **Successful Runs:** The number of times the script runs to completion without errors.
- **Playlists Created:** The total number of new monthly playlists created across all users.
- **Tracks Sorted:** The total number of tracks successfully added to playlists.

## 8. Open Questions

- How many tracks should the application attempt to fetch from the activity stream in a single run? Is there a limit?
- Where should the OAuth token and other configuration be stored? (e.g., a config file in `~/.config/soundcloud-organizer/`).

---