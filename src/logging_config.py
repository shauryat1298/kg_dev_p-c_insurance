"""
Structured logging configuration using structlog.

This module provides a centralized logging setup with JSON formatting
for production use and human-readable console output for development.
"""
import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

import structlog
from structlog.types import Processor


def setup_logging(
    log_level: Optional[str] = None,
    log_dir: Optional[Path] = None,
    log_file: Optional[str] = None,
    json_logs: bool = True
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_file: Name of the log file
        json_logs: Whether to use JSON formatting (True) or human-readable (False)
    """
    # Import config here to avoid circular imports
    from config import BASE_PATH, LOG_LEVEL, LOG_DIR, LOG_FILE
    
    # Use config values if not provided
    log_level = log_level or LOG_LEVEL
    log_dir = log_dir or Path(LOG_DIR)
    log_file = log_file or LOG_FILE
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Shared processors for structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Choose formatter based on json_logs flag
    if json_logs:
        # JSON output for production/log aggregation
        processors: list[Processor] = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Human-readable output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set up file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    
    # Use JSON formatter for file handler
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Set console handler for human-readable output (if json_logs is False)
    if not json_logs:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


# Initialize logging on module import (lazy to avoid circular imports)
_logging_initialized = False

def _init_logging():
    """Initialize logging if not already done."""
    global _logging_initialized
    if not _logging_initialized:
        setup_logging(json_logs=True)
        _logging_initialized = True

# Initialize on first import
_init_logging()

