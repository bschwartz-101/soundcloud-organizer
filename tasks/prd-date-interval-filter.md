# Product Requirements Document: Date Interval Filtering

## 1. Introduction/Overview

This document outlines the requirements for adding a date-based filtering feature to the SoundCloud Organizer. Currently, the application processes all tracks found in the user's activity stream. This feature will introduce a new `--scope` command-line option, allowing users to limit the organization process to a specific time interval. This provides users with more granular control, improves performance by reducing the number of tracks to process, and allows for re-organizing specific historical periods.

## 2. Goals

- **Increase Performance:** Allow the tool to run faster by processing a smaller, user-defined subset of tracks from the stream.
- **Provide Granular Control:** Give users precise control to backfill or re-organize tracks from specific historical periods (e.g., "just last month", "all of 2023").
- **Improve Relevance:** Prevent the tool from processing very old or irrelevant tracks that may appear in the activity stream.

## 3. User Stories

- **As a user**, I want to organize only the tracks from last month so that my playlists are up-to-date without processing my entire feed.
- **As a user**, I want to run the organizer for the entire previous year (`2023`) to backfill my playlists for that period.
- **As a user**, I want to process only tracks from a specific month (e.g., `2024-01`) to fix or re-run the organization for just that period.
- **As a user**, I want to combine a date scope with a length filter (e.g., find all "long" tracks from "last-month") to create highly specific playlists.

## 4. Functional Requirements

1.  **New CLI Option:**
    -   FR1.1: The system must introduce a new command-line option: `--scope`.
    -   FR1.2: The `--scope` option should be optional. If not provided, the application should process all tracks from the stream, maintaining the current behavior.

2.  **Scope Value Parsing:**
    -   FR2.1: The system must parse the value provided to `--scope` and convert it into a start date and an end date for the filtering period.
    -   FR2.2: The system must support the following predefined relative values:
        -   `last-month`: The full previous calendar month (e.g., if run in February, it covers January 1-31).
        -   `last-year`: The full previous calendar year (e.g., if run in 2024, it covers Jan 1, 2023 - Dec 31, 2023).
        -   `ytd`: "Year to date". From January 1st of the current year up to and including the current day.
    -   FR2.3: The system must support specific year and year-month values:
        -   `YYYY` (e.g., `2023`): The entire specified calendar year (Jan 1 - Dec 31).
        -   `YYYY-MM` (e.g., `2024-01`): The entire specified calendar month (Jan 1 - Jan 31).
    -   FR2.4: The system must raise a user-friendly error if the `--scope` value does not match any of the allowed formats.

3.  **Track Filtering Logic:**
    -   FR3.1: The system must fetch all tracks from the user's activity stream.
    -   FR3.2: After fetching, the system must filter the tracks, keeping only those whose `created_at` timestamp falls within the date interval determined by the `--scope` option.
    -   FR3.3: If both `--scope` and the existing `--length-filter` are provided, the system must apply both filters. A track must match both the date interval AND the length criteria to be processed.

4.  **Processing and Playlist Management:**
    -   FR4.1: The tracks that pass the filter(s) should be processed exactly as they are now: grouped by month (`YYYY-MM`) and added to the corresponding playlists.

## 5. Non-Goals (Out of Scope)

- **Arbitrary Date Ranges:** This feature will not support arbitrary start and end dates (e.g., `--start-date 2023-01-15 --end-date 2023-02-15`). The defined `scope` values are sufficient for the initial implementation.
- **Time-of-day Filtering:** Filtering is based on calendar dates only. Time components of the `created_at` field will be used for inclusion within a date, but users cannot specify time-based scopes (e.g., "last 6 hours").
- **API-level Filtering:** The filtering will be performed within the Python application after all stream items have been fetched. We will not attempt to pass date parameters to the stream API endpoint, as its support for this is undocumented and uncertain.

## 6. Design Considerations

- The CLI help text for the `organize` command must be updated to include a clear description of the new `--scope` option and its accepted values.
- A new module or set of helper functions should be created to handle the parsing of the `--scope` string into a `(start_date, end_date)` tuple to keep the main processing logic clean.

## 7. Technical Considerations

- **Date/Time Handling:** The `datetime` module in Python should be used for all date calculations. Careful attention must be paid to timezones to ensure accurate comparisons with the `created_at` field from the API, which is in UTC.
- **Code Location:**
    - The new CLI option will be added in `src/soundcloud_organizer/main.py`.
    - The core filtering logic will be added to `src/soundcloud_organizer/processor.py`. The `process_stream` function will be updated to accept the new scope parameter.
    - A new helper function/module may be needed for parsing the scope argument.
- **Testing:** New unit tests must be created to validate:
    - The correct parsing of all supported `--scope` values into date ranges.
    - The filtering logic correctly includes/excludes tracks based on their `created_at` date.
    - The interaction between `--scope` and `--length-filter`.

## 8. Success Metrics

- Successful execution of the `organize` command with various valid `--scope` values.
- User feedback confirming the feature's utility and correctness.
- Reduction in processing time when a narrow scope is used compared to no scope.

## 9. Open Questions

- None at this time. The requirements are considered clear enough for implementation.