"""Centralized logging configuration for the application."""

import sys

from loguru import logger


def setup_logging(debug: bool):
    """Sets up the logging configuration for the application."""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level, colorize=True)
