"""
Structured logging configuration for Smart Dev Dashboard
"""
import sys
import json
from datetime import datetime
from loguru import logger
from pathlib import Path

# Global filter to remove problematic keys from loguru extra
PROBLEMATIC_KEYS = {"size", "filename", "log_analysis_status", "log_count"}

def safe_log_filter(record):
    for key in list(PROBLEMATIC_KEYS):
        if key in record["extra"]:
            del record["extra"][key]
    return True

# Remove default logger
logger.remove()

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Console logger with colors
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    filter=safe_log_filter
)

# File logger for structured logging
logger.add(
    logs_dir / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    filter=safe_log_filter
)

# Custom logger for API requests
api_logger = logger.bind(module="api")
analysis_logger = logger.bind(module="analysis")
performance_logger = logger.bind(module="performance")

# Reserved keys that must not be passed to loguru's extra (loguru/SQLAlchemy internals)
RESERVED_LOG_KEYS = {
    "filename", "file", "module", "name", "message", "level", "time",
    "function", "line", "thread", "process", "exception", "record", "extra"
}

def _filter_log_kwargs(kwargs):
    """Remove reserved or problematic keys from kwargs for logger.extra."""
    return {k: v for k, v in kwargs.items() if k not in RESERVED_LOG_KEYS and v is not None}

def log_api_request(endpoint: str, method: str, status_code: int, duration: float, **kwargs):
    """Log API request with performance metrics, robust to missing/reserved keys"""
    api_logger.info(
        f"API Request: {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s"
    )

def log_analysis_request(log_length: int, analysis_duration: float, **kwargs):
    """Log analysis request with metrics, robust to missing/reserved keys"""
    analysis_logger.info(
        f"Analysis completed - Log length: {log_length} chars - Duration: {analysis_duration:.3f}s"
    )

def log_error(error: Exception, context: str = "", **kwargs):
    """Log errors with context, safely handle missing or reserved keys"""
    logger.error(
        f"Error in {context}: {str(error)}"
    ) 