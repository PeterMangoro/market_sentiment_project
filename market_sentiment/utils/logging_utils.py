"""
Utility functions for logging.

This module provides logging utilities for the Market Sentiment Project.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Configure logging format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_LEVEL = logging.INFO

def setup_logging(log_file: Optional[Path] = None, 
                  log_level: int = DEFAULT_LOG_LEVEL,
                  log_format: str = DEFAULT_LOG_FORMAT) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Path to the log file. If None, logs only to console.
        log_level: Logging level. Defaults to INFO.
        log_format: Logging format string. Defaults to a standard format.
    """
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        log_file = Path(log_file)
        
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log setup completion
    root_logger.info(f"Logging configured with level {logging.getLevelName(log_level)}")
    if log_file:
        root_logger.info(f"Logging to file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name, typically the module name.
    
    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
