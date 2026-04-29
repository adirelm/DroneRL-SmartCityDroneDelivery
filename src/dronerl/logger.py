"""Centralized logging setup for DroneRL project."""

import logging
import sys


def setup_logger(name: str = "DroneRL", level: str = "INFO") -> logging.Logger:
    """Create and configure a logger with console output.

    Args:
        name: Logger name.
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
