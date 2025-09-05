"""Centralized logging configuration for the application."""

import re
import sys
from typing import Any

from loguru import logger

SENSITIVE_KEYS = ["client_secret", "access_token", "refresh_token"]
REDACTION_STRING = "[REDACTED]"


def sensitive_data_filter(record: dict[str, Any]) -> bool:
    """Filter function to redact sensitive data from log records."""
    # Redact from the formatted message string using regex
    for key in SENSITIVE_KEYS:
        # This pattern looks for 'key="value"' or 'key': 'value' and redacts the value
        pattern = re.compile(
            rf"(['\"]?{key}['\"]?\s*[:=]\s*['\"]?)([^,'\"&\s]+)(['\"]?)"
        )
        record["message"] = pattern.sub(rf"\1{REDACTION_STRING}\3", record["message"])

    # Also check the 'extra' dict for structured data
    for key in SENSITIVE_KEYS:
        if key in record["extra"]:
            record["extra"][key] = REDACTION_STRING

    return True


def setup_logging(debug: bool):
    """Sets up the logging configuration for the application."""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stderr, level=level, colorize=True, catch=True, filter=sensitive_data_filter
    )
    logger.add(
        "logs/app.log",
        level="DEBUG",
        rotation="10 MB",
        retention=5,
        catch=True,
        filter=sensitive_data_filter,
    )
