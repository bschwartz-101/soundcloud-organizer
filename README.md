0,0 +1,87 @@
# SoundCloud Organizer

A CLI tool to automatically organize your SoundCloud stream into monthly playlists.

This tool helps you automatically discover, filter, and organize music from your SoundCloud stream. It connects to your account, fetches tracks from your main activity stream, filters them based on track length, and sorts them into monthly playlists (e.g., `2023-10`).

## Features

- **Secure OAuth2 Login:** Authorize the application with your SoundCloud account without sharing your password.
- **Automated Curation:** Fetches tracks from your main activity stream.
- **Track Filtering:** Filter tracks by length: "short" (<5 min), "medium" (5-20 min), or "long" (>20 min).
- **Date Scoping:** Filter tracks by time interval (e.g., `last-month`, `ytd`, `2023`, `2023-01`).
- **Automatic Playlist Creation:** Creates monthly playlists (e.g., `YYYY-MM`) if they don't already exist.
- **Idempotent:** Running the tool multiple times won't create duplicate playlists or add duplicate tracks.

## Installation

This project uses `uv` for environment and dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/soundcloud-organizer.git
    cd soundcloud-organizer
    ```

2.  **Create a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install the package:**
    ```bash
    uv pip install -e .
    ```

## Setup

Before you can use the tool, you need to get a **Client ID** and **Client Secret** from SoundCloud.

1.  **Create a SoundCloud App:**
    - Go to the SoundCloud for Developers page: https://soundcloud.com/you/apps
    - Click "Register a new application".
    - Fill out the form for your new app.

2.  **Configure the Redirect URI:**
    - In your app's settings on the SoundCloud developer page, find the "Redirect for authorization" field.
    - You **must** set this value to: `http://127.0.0.1:8080/`
    - Save your changes.

3.  **Copy Your Credentials:**
    - On your app's page, you will see your **Client ID** and **Client Secret**. You will need these for the `login` command.

## Usage

The application provides two main commands: `login` and `organize`.

### 1. Login

First, you need to authorize the application with your SoundCloud account. This is a one-time process.

```bash
soundcloud-organizer login
```

You will be prompted to enter the **Client ID** and **Client Secret** you obtained during setup. After entering them, your web browser will open to a SoundCloud authorization page. Log in and approve the application.

Your credentials will be securely stored in `~/.config/soundcloud-organizer/config.json` for future use.

### 2. Organize

Once you are logged in, you can run the `organize` command to fetch, filter, and sort tracks.

```bash
soundcloud-organizer organize
```

By default, this will process all tracks. You can use the `--length-filter` (or `-f`) option to specify which tracks to organize.

**Examples:**

- Organize only long tracks (over 20 minutes):
  ```bash
  soundcloud-organizer organize --length-filter long
  ```

- Organize only short tracks (under 5 minutes):
  ```bash
  soundcloud-organizer organize -f short
  ```

## Development

To install development dependencies (like `pytest`), run:
```bash
uv pip install -e .[dev]
```

To run the test suite:
```bash
pytest
```