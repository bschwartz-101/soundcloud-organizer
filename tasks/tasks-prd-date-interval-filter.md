## Relevant Files

-   `src/soundcloud_organizer/main.py` - The entry point for the CLI. The new `--scope` option will be added here.
-   `src/soundcloud_organizer/processor.py` - Contains the core logic for fetching and filtering tracks. This will be modified to apply the date filter.
-   `tests/test_processor.py` - Unit tests for the processor. Will need updates to test the new filtering logic.
-   `src/soundcloud_organizer/scope_parser.py` - **New File**. A new helper module to parse the `--scope` string into a date range.
-   `tests/test_scope_parser.py` - **New File**. Unit tests for the new `scope_parser.py` module.
-   `README.md` - The main documentation for the project, which will need to be updated to explain the new feature.

### Notes

-   Unit tests should be placed in the `tests/` directory.
-   Use `uv run pytest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the pytest configuration.
-   Dependencies should be managed by `uv`. The `python-dateutil` package will be useful for date calculations and should be added.
-   Missing packages should be installed with `uv pip install [package-name]`.

## Tasks

-   [x] **1.0 Add `--scope` CLI Option to the `organize` Command**
    -   [x] 1.1 In `src/soundcloud_organizer/main.py`, modify the `organize` function to accept a new optional argument: `scope: str | None`.
    -   [x] 1.2 Use `typer.Option` to define the argument with a default value of `None`.
    -   [x] 1.3 Add a short name `-s` for the option, e.g., `typer.Option(None, "--scope", "-s", ...)`.
    -   [x] 1.4 Add a `help` message explaining the purpose of the filter and listing the accepted values (e.g., `last-month`, `ytd`, `2023`, `2023-01`).
    -   [x] 1.5 Update the call to `process_stream` to pass the new `scope` argument.

-   [ ] **2.0 Create a New Module for Parsing the `--scope` Argument**
    -   [x] 2.1 Create a new file: `src/soundcloud_organizer/scope_parser.py`.
    -   [x] 2.2 Add `python-dateutil` as a dependency for easier date calculations: `uv pip install python-dateutil`.
    -   [x] 2.3 In `scope_parser.py`, create a main function `parse_scope(scope_str: str) -> tuple[datetime, datetime]`. This function will act as a router.
    -   [x] 2.4 Implement the logic to parse the `last-month`, `last-year`, and `ytd` keywords.
    -   [x] 2.5 Implement the logic to parse the `YYYY` and `YYYY-MM` formats. Regular expressions can be useful here.
    -   [x] 2.6 If the `scope_str` is invalid, the function should raise a `ValueError` with a user-friendly message.
    -   [x] 2.7 Create the corresponding test file: `tests/test_scope_parser.py`.
    -   [x] 2.8 Write unit tests for each valid scope keyword and format to ensure they return the correct start and end datetimes.
    -   [x] 2.9 Write a unit test to verify that an invalid scope string correctly raises a `ValueError`.

-   [ ] **3.0 Integrate Date Filtering into the Core Processing Logic**
    -   [x] 3.1 In `src/soundcloud_organizer/processor.py`, update the `process_stream` function signature to accept the new `scope: str | None` parameter.
    -   [x] 3.2 At the beginning of `process_stream`, if `scope` is not `None`, call the `scope_parser.parse_scope` function to get the date range. Handle the potential `ValueError` and print it to the console, then exit gracefully.
    -   [x] 3.3 Create a new filter function `track_matches_scope(track: Track, date_range: tuple[datetime, datetime] | None) -> bool`.
    -   [x] 3.4 This function should return `True` if `date_range` is `None`, or if the `track.created_at` falls within the range. Remember to handle timezones correctly (the API provides UTC dates).
    -   [x] 3.5 In the main loop of `process_stream`, modify the `if` condition to check both `track_matches_filter` (for length) and the new `track_matches_scope`.
    -   [x] 3.6 In `src/soundcloud_organizer/main.py`, wrap the call to `process_stream` in a `try...except ValueError` block to catch parsing errors and display them cleanly.
    -   [x] 3.7 Update `tests/test_processor.py` to test the combined filtering. Add tests that provide a scope and ensure only tracks within that date range are processed.

-   [x] **4.0 Update Documentation**
    -   [x] 4.1 In `README.md`, update the "Features" and "Usage" sections to document the new `--scope` option.
    -   [ ] 4.2 Provide examples of how to use the new option, similar to the existing examples for `--length-filter`.