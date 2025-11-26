"""Logging Configuration Module.

This module provides centralized logging configuration for the Color Correction System.
It supports both console and file logging with rotation, and different log levels per module.

Usage:
    from logging_config import setup_logging
    setup_logging()
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Application started")
"""

import logging
import logging.handlers
import os
from pathlib import Path
from config import settings


def setup_logging() -> None:
    """Configure application-wide logging.
    
    Sets up logging with:
    - Console handler for real-time output
    - File handler with rotation for persistent logging
    - Different levels for different modules
    - Formatted output with timestamp, level, and message
    
    Raises:
        OSError: If unable to create log directory
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File Handler with Rotation
    if settings.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Keep 5 backup files
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    # Database logger
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Celery logger
    logging.getLogger("celery").setLevel(logging.INFO)
    
    # Uvicorn logger
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # FastAPI logger
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Application logger
    app_logger = logging.getLogger("color_correction")
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> from logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello, world!")
    """
    return logging.getLogger(name)


# Configure logging on module import
if not logging.root.handlers:
    setup_logging()
