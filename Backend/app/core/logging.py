import logging
import sys
from typing import Any, Dict


class ContextFilter(logging.Filter):
    """Logging filter to attach request_id to log records when available."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging() -> logging.Logger:
    """Configure structured console logging for the application."""
    log_format = (
        "%(asctime)s [%(levelname)s] [req_id:%(request_id)s] %(name)s: %(message)s"
    )
    
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    # Quiet external verbose loggers
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.access").addFilter(ContextFilter())

    return root_logger


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive field values before logging."""
    sensitive_keys = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "jwt_secret_key",
        "mongodb_uri",
        "authorization",
        "api_key",
    }
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    return sanitized
