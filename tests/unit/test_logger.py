"""Tests for ``dronerl.logger.setup_logger``."""

import logging

from dronerl.logger import setup_logger


def test_setup_logger_returns_named_logger():
    logger = setup_logger("test_logger_unit", "INFO")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger_unit"


def test_setup_logger_default_name_and_level():
    logger = setup_logger()
    assert logger.name == "DroneRL"
    assert logger.level == logging.INFO


def test_setup_logger_respects_level_string():
    logger = setup_logger("test_logger_debug", "DEBUG")
    assert logger.level == logging.DEBUG


def test_setup_logger_invalid_level_falls_back_to_info():
    """An unknown level string defaults to INFO rather than raising."""
    logger = setup_logger("test_logger_invalid", "NOT_A_REAL_LEVEL")
    assert logger.level == logging.INFO


def test_setup_logger_idempotent_when_called_twice():
    """Calling setup_logger with the same name doesn't pile up duplicate handlers."""
    a = setup_logger("test_logger_dup")
    b = setup_logger("test_logger_dup")
    # Same logger object, handler list unchanged
    assert a is b
    assert len(a.handlers) == 1
