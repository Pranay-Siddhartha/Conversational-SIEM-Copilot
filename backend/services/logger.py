import logging
import sys
import traceback
from typing import Any

# Configure structured logging for Vercel/Production
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: [%(name)s] %(message)s",
    stream=sys.stdout,
)

def get_logger(name: str):
    """Get a named logger instance."""
    return logging.getLogger(name)

def log_error(logger: logging.Logger, message: str, exc: Exception = None):
    """Log an error with message and optional traceback."""
    if exc:
        err_detail = f"{message} | Error: {str(exc)}"
        logger.error(err_detail)
        # On Vercel, print_exc helps seeing the full stack trace in logs
        traceback.print_exc()
    else:
        logger.error(message)

def log_debug(logger: logging.Logger, message: str, data: Any = None):
    """Log a debug message (visible if log level is DEBUG)."""
    if data:
        logger.debug(f"{message} | Data: {data}")
    else:
        logger.debug(message)
