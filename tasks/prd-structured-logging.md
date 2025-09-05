# Product Requirements Document: Structured Logging

## 1. Introduction/Overview

This document outlines the requirements for integrating a structured logging system into the SoundCloud Organizer using the `loguru` library. The current application uses basic `print` statements for output, which makes debugging difficult and provides no persistent record of operations or errors. The goal of this feature is to introduce comprehensive, configurable, and structured logging to improve debuggability, provide detailed traceability for application flow, and capture errors effectively for both development and production use.

## 2. Goals

-   **Improve Debuggability:** Provide detailed, leveled logs that allow developers to easily trace the application's execution flow and inspect the state of important variables during development.
-   **Structured Error Reporting:** Automatically capture unhandled exceptions and errors with full stack traces in a structured format, making it easier to diagnose failures.
-   **Persistent Auditing:** Maintain a persistent log file of all application activities, which can be reviewed later to understand what the application did, which API calls were made, and where failures occurred.
-   **Enhance User Experience:** Provide clear, user-configurable control over log verbosity, allowing users to switch between standard operational output and detailed debugging information.

## 3. User Stories

-   **As a developer**, I want to see detailed `DEBUG` level logs on my console when I run the app with a `--debug` flag, so I can trace the execution flow and inspect variable values without adding temporary print statements.
-   **As a user**, I want all application logs to be automatically saved to a file in a `logs/` directory so I can review them later if an unexpected error occurs.
-   **As a maintainer**, I want unhandled exceptions to be automatically logged with a full stack trace to a file, so I can diagnose production failures without needing to reproduce them.
-   **As a security-conscious developer**, I want to ensure that sensitive information like API tokens and client secrets are automatically redacted from all logs to prevent accidental exposure.

## 4. Functional Requirements

1.  **Library Integration:**
    -   FR1.1: The system must add `loguru` as a project dependency.

2.  **Logger Configuration:**
    -   FR2.1: The system must configure `loguru` to output logs to two destinations (sinks): the console and a file.
    -   FR2.2: Console logs must be colorized for readability (e.g., `INFO` is one color, `ERROR` another).
    -   FR2.3: File logs must be written to a `logs/` directory at the root of the project. The log file should be named `app.log`.
    -   FR2.4: The log file must be configured to rotate, creating a new file when it reaches a certain size (e.g., 10 MB) and keeping a limited number of old files (e.g., 5 backups).
    -   FR2.5: The system must ensure that sensitive data (e.g., `client_secret`, `access_token`, `refresh_token`) is automatically filtered or redacted from all log messages and records.

3.  **Log Level Control:**
    -   FR3.1: The default log level for the **console** must be `INFO`. This will show major application steps but hide detailed debug messages.
    -   FR3.2: The default log level for the **log file** must be `DEBUG` to ensure all details are always captured for later analysis.
    -   FR3.3: The `organize` command must include a new optional boolean flag: `--debug`.
    -   FR3.4: When the `--debug` flag is used, the console log level must be changed from `INFO` to `DEBUG`.

4.  **Logging Implementation:**
    -   FR4.1: The application must replace all existing `rich.console.print()` and `rich.console.log()` calls used for operational feedback with `loguru` logger calls at the appropriate level (`INFO`, `DEBUG`, `WARNING`, `ERROR`). `rich` should still be used for user-facing tables or purely presentational output.
    -   FR4.2: The system must log the entry and exit points of key functions (e.g., `process_stream`, `SoundCloudClient.get_stream`, `SoundCloudClient.add_tracks_to_playlist`) at the `DEBUG` level.
    -   FR4.3: The system must log all external API requests made by `SoundCloudClient`. The log message should include the HTTP method, URL, and the status of the response (e.g., success or failure code). This should be at the `DEBUG` level.
    -   FR4.4: The system must log the values of important variables at different stages, such as the number of tracks found, the playlists being created or updated, and the results of filtering decisions.
    -   FR4.5: The system must be configured to automatically catch and log any unhandled exceptions that would otherwise cause the application to crash.

## 5. Non-Goals (Out of Scope)

-   **Remote Log Shipping:** Logs will only be stored locally. Integration with external logging services (e.g., Sentry, Logstash, Datadog) is not part of this feature.
-   **Complex Log Formatting:** A standard, readable log format will be used. Users will not be given the ability to customize the log message format via the CLI.
-   **GUI for Logs:** There will be no graphical interface for viewing logs; they will be accessible via the console and text files.

## 6. Technical Considerations

-   **Centralized Configuration:** A new module (e.g., `src/soundcloud_organizer/logging_config.py`) should be created to handle all `loguru` setup. This configuration should be imported and applied once at the application's entry point in `main.py`.
-   **Dependency Management:** `loguru` will be added to the `dependencies` in `pyproject.toml`.
-   **Exception Handling:** `loguru`'s `@logger.catch` decorator or `logger.add(..., catch=True)` sink configuration should be used to handle uncaught exceptions gracefully.
-   **Testing:** While it can be difficult to test logging output directly, new tests can be added to verify that the `--debug` flag is correctly parsed. Existing tests should be reviewed to ensure they don't break due to changes in console output.

## 7. Success Metrics

-   The application successfully generates a `logs/app.log` file upon first run.
-   When run with `--debug`, the console output is visibly more verbose than when run without it.
-   When an intentional or unintentional error is triggered, a full stack trace is recorded in the log file.
-   A manual review of the log files confirms that no sensitive credentials appear in plain text.

## 8. Open Questions

-   None at this time. The requirements are clear for implementation.
