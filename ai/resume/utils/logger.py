"""Centralized logging module for the AI Resume Analyzer."""

import logging
import sys
import time
from functools import wraps
from typing import Callable, Any
from config import settings


def get_logger(name: str) -> logging.Logger:
    """Configures and returns a standardized logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL.upper())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = get_logger("resume_analyzer")


def log_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log function execution time in milliseconds."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"{func.__qualname__} completed in {elapsed_ms:.2f} ms")
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"{func.__qualname__} failed after {elapsed_ms:.2f} ms with error: {str(e)}")
            raise e

    return wrapper
