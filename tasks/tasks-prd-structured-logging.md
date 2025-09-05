## Relevant Files

-   `src/soundcloud_organizer/logging_config.py` - **New File**. This will contain the centralized `loguru` configuration.
-   `src/soundcloud_organizer/main.py` - The CLI entry point. It will be modified to initialize logging and add the `--debug` flag.
-   `pyproject.toml` - The project's dependency file, which will be updated to include `loguru`.
-   `src/soundcloud_organizer/client.py` - The API client. `print` and `log` calls will be replaced with structured logging.
-   `src/soundcloud_organizer/processor.py` - The core processing logic. `print` and `log` calls will be replaced with structured logging.
-   `src/soundcloud_organizer/auth.py` - The authentication module. `print` calls will be replaced with structured logging.
-   `tests/test_main.py` - Will be updated or have a new test file created to verify the `--debug` flag functionality.

### Notes

-   Unit tests should be placed in the `tests/` directory.
-   Use `uv run pytest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the pytest configuration.
-   Dependencies should be managed by `uv`. The `loguru` package will be added.
-   Missing packages should be installed with `uv pip install [package-name]`.

## Tasks

-   [x] **1.0 Add Dependency and Basic Configuration**
    -   [x] 1.1 Add `loguru` to the `dependencies` list in `pyproject.toml`.
    -   [x] 1.2 Create a new file: `src/soundcloud_organizer/logging_config.py`.
    -   [x] 1.3 In `logging_config.py`, create a `setup_logging` function that takes a `debug` boolean flag.
    -   [x] 1.4 In `setup_logging`, remove the default `loguru` handler and add a console sink with level `INFO` (or `DEBUG` if the flag is true) and `colorize=True`.
    -   [x] 1.5 In `main.py`, import and call `setup_logging()` at the start of the `organize` and `login` commands.
-   [x] **2.0 Implement Advanced Logger Configuration**
    -   [x] 2.1 In `logging_config.py`, add a file sink to `setup_logging` that writes to `logs/app.log` with level `DEBUG`.
    -   [x] 2.2 Configure the file sink for rotation (e.g., `rotation="10 MB"`) and retention (e.g., `retention="5 files"`).
    -   [x] 2.3 Configure both sinks to automatically catch unhandled exceptions (`catch=True`).
    -   [x] 2.4 Implement a filter function to redact sensitive data (`client_secret`, `access_token`, `refresh_token`) from log records. Apply this filter to both sinks.
    -   [x] 2.5 In `main.py`, add a `--debug` boolean `typer.Option` to the `organize` command and pass its value to `setup_logging`.
-   [x] **3.0 Integrate Logging into the Application**
    -   [x] 3.1 In `main.py`, replace `rich.console.print` and `rich.console.log` calls with `logger` calls (`logger.info`, `logger.error`, etc.). Keep `rich` for purely presentational output like the initial "dry-run" message.
    -   [x] 3.2 In `auth.py`, import `logger` and replace `print` statements with appropriate `logger` calls (e.g., `logger.info` for browser opening, `logger.debug` for token refresh).
    -   [x] 3.3 In `client.py`, import `logger` and replace `console.log` with `logger.debug`. Add `logger.debug` calls for API requests, including method, URL, and response status. Use `@logger.catch` or `try/except` with `logger.exception` for robustness.
    -   [x] 3.4 In `processor.py`, import `logger` and replace `rich.console.print` and `rich.console.log` with `logger` calls. Use `logger.info` for major steps, and `logger.debug` for detailed per-track information.
-   [ ] **4.0 Add Testing for New Logging Functionality**
    -   [ ] 4.1 In `tests/test_main.py`, add a test to verify that the `--debug` flag is correctly added to the `organize` command's context. (Directly testing log output is complex; we will test the flag's presence).
