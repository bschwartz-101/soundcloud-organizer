"""
Parses a scope string into a start and end datetime.
"""

import re
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta


def parse_scope(scope_str: str) -> tuple[datetime, datetime]:
    """
    Parses a scope string and returns a tuple of (start_date, end_date).

    Args:
        scope_str: The string to parse.
                   Expected formats: 'last-month', 'last-year', 'ytd',
                                     'YYYY', 'YYYY-MM'.

    Returns:
        A tuple containing the start and end datetime objects.

    Raises:
        ValueError: If the scope string is in an invalid format.
    """
    now = datetime.now(timezone.utc)

    if scope_str == "last-month":
        # End of the previous month
        end_date = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(microseconds=1)
        # Start of the previous month
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start_date, end_date

    if scope_str == "last-year":
        # End of the previous year
        end_date = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(microseconds=1)
        # Start of the previous year
        start_date = end_date.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        return start_date, end_date

    if scope_str == "ytd":
        # Start of the current year
        start_date = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        # End of today
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date, end_date

    # YYYY format
    if match := re.fullmatch(r"(\d{4})", scope_str):
        year = int(match.group(1))
        start_date = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(year, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
        return start_date, end_date

    # YYYY-MM format
    if match := re.fullmatch(r"(\d{4})-(\d{2})", scope_str):
        year = int(match.group(1))
        month = int(match.group(2))
        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        # End of the month is start of next month minus one microsecond
        end_date = start_date + relativedelta(months=1) - relativedelta(microseconds=1)
        return start_date, end_date

    raise ValueError(
        f"Invalid scope value: '{scope_str}'. "
        "Allowed values are: 'last-month', 'last-year', 'ytd', 'YYYY', 'YYYY-MM'."
    )
