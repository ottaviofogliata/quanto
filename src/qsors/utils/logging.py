"""Logging utilities for QSORS."""

from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    """Return configured logger with simple format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
