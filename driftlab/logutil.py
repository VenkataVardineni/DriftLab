"""Structured logging helpers for DriftLab."""

import logging
import os
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """
    Configure root logging once. Level from argument, DRIFTLAB_LOG_LEVEL, or INFO.
    """
    name = (level or os.environ.get("DRIFTLAB_LOG_LEVEL") or "INFO").upper()
    numeric = getattr(logging, name, logging.INFO)
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
