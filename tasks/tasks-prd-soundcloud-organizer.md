## Relevant Files

- `src/soundcloud_organizer/main.py` - Main entry point for the CLI application.
- `src/soundcloud_organizer/auth.py` - Handles the SoundCloud OAuth2 authentication flow.
- `src/soundcloud_organizer/client.py` - Contains the logic for interacting with the SoundCloud API (fetching stream, managing playlists).
- `src/soundcloud_organizer/config.py` - Manages loading and saving of configuration (API keys, user tokens).
- `src/soundcloud_organizer/models.py` - Data models for tracks, playlists, etc.
- `tests/` - Directory for all unit and integration tests.

### Notes

- The project will use `uv` for environment and dependency management.
- A `pyproject.toml` file will define project metadata and dependencies.

## Tasks

- [x] 1.0 Project Setup and Configuration
  - [x] 1.1 Initialize the project structure with `src/soundcloud_organizer` and `tests` directories.
  - [x] 1.2 Update `pyproject.toml` with project metadata and add initial dependencies (`typer`, `rich`, `requests`, `requests-oauthlib`, `pydantic`).
  - [x] 1.3 Create placeholder Python files (`auth.py`, `client.py`, `config.py`, `models.py`) within the `src` directory.
  - [x] 1.4 Create an initial test file `tests/test_main.py` to ensure the test runner is configured correctly.
- [x] 2.0 Implement SoundCloud OAuth2 Authentication
  - [x] 2.1 Define Pydantic models in `config.py` for storing configuration data (client ID, secret, tokens) and implement load/save functions.
  - [x] 2.2 Implement the core OAuth2 authorization flow in `auth.py` to get a token from SoundCloud.
  - [x] 2.3 Create a function to retrieve an authenticated `OAuth2Session`, refreshing the token if necessary.
  - [x] 2.4 Add a `login` command to the CLI to initiate the authentication process.
- [x] 3.0 Develop SoundCloud API Client
  - [x] 3.1 Define Pydantic models in `models.py` for API objects like `Track`, `User`, and `Playlist`.
  - [x] 3.2 Create a `SoundCloudClient` class in `client.py` that is initialized with an authenticated session.
  - [x] 3.3 Implement a method in the client to fetch the user's activity stream.
  - [x] 3.4 Implement methods for playlist management (get, create, add tracks).
- [x] 4.0 Implement Track Filtering and Processing Logic
  - [x] 4.1 Create a new file `src/soundcloud_organizer/processor.py` to house the filtering and processing logic.
  - [x] 4.2 In `processor.py`, define an `Enum` for track length filters and a function to check if a track matches a filter.
  - [x] 4.3 Implement the main `process_stream` function to orchestrate fetching, filtering, and adding tracks to monthly playlists.
- [x] 5.0 Build the CLI and Main Execution Flow
  - [x] 5.1 Add an `organize` command to `main.py` that accepts a `length-filter` argument.
  - [x] 5.2 Implement the main execution logic within the `organize` command: load settings, get an authenticated client, and call the `process_stream` function.
- [x] 6.0 Add Testing and Documentation
  - [x] 6.1 Add `pytest` and `pytest-mock` as development dependencies in `pyproject.toml`.
  - [x] 6.2 Create `tests/test_processor.py` and write unit tests for the track filtering and stream processing logic.
  - [x] 6.3 Create `tests/test_client.py` and write unit tests for the `SoundCloudClient`, mocking API responses.
  - [x] 6.4 Create a `README.md` with installation, setup, and usage instructions.