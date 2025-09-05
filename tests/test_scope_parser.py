"""
Tests for the scope parser module.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from soundcloud_organizer.scope_parser import parse_scope


@patch("soundcloud_organizer.scope_parser.datetime")
def test_parse_scope_last_month(mock_datetime):
    """Test parsing the 'last-month' keyword."""
    # Mock current date to be Feb 15, 2024
    mock_now = datetime(2024, 2, 15, 10, 30, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    start_date, end_date = parse_scope("last-month")

    # Should cover all of January 2024
    assert start_date == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert end_date == datetime(2024, 1, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


@patch("soundcloud_organizer.scope_parser.datetime")
def test_parse_scope_last_year(mock_datetime):
    """Test parsing the 'last-year' keyword."""
    # Mock current date to be Feb 15, 2024
    mock_now = datetime(2024, 2, 15, 10, 30, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    start_date, end_date = parse_scope("last-year")

    # Should cover all of 2023
    assert start_date == datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert end_date == datetime(2023, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


@patch("soundcloud_organizer.scope_parser.datetime")
def test_parse_scope_ytd(mock_datetime):
    """Test parsing the 'ytd' (year-to-date) keyword."""
    # Mock current date to be Jan 15, 2024
    mock_now = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    start_date, end_date = parse_scope("ytd")

    # Should start on Jan 1, 2024
    assert start_date == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    # End of the day on Jan 15
    assert end_date == datetime(2024, 1, 15, 23, 59, 59, 999999, tzinfo=timezone.utc)


def test_parse_scope_yyyy():
    """Test parsing the 'YYYY' format."""
    start_date, end_date = parse_scope("2023")
    expected_start = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    expected_end = datetime(2023, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
    assert start_date == expected_start
    assert end_date == expected_end


def test_parse_scope_yyyy_mm():
    """Test parsing the 'YYYY-MM' format (including a leap year)."""
    # Test a non-leap year month
    start_date, end_date = parse_scope("2023-11")
    assert start_date == datetime(2023, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert end_date == datetime(2023, 11, 30, 23, 59, 59, 999999, tzinfo=timezone.utc)

    # Test a leap year month
    start_date_leap, end_date_leap = parse_scope("2024-02")
    assert start_date_leap == datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert end_date_leap == datetime(
        2024, 2, 29, 23, 59, 59, 999999, tzinfo=timezone.utc
    )


def test_parse_scope_invalid():
    """Test that an invalid scope string raises a ValueError."""
    with pytest.raises(ValueError) as excinfo:
        parse_scope("invalid-scope")
    assert "Invalid scope value: 'invalid-scope'" in str(excinfo.value)
