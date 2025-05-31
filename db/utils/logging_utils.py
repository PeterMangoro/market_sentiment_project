"""
Utility functions for logging.

This module provides logging configuration and utility functions.
"""

import logging
import sys
from pathlib import Path

from .. import config

def get_logger(name, log_file=None, level=None):
    """
    Get a configured logger instance.
    
    Args:
        name (str): Logger name, typically __name__ of the calling module.
        log_file (str or Path, optional): Path to log file. Defaults to config.LOG_FILE.
        level (int, optional): Logging level. Defaults to config.LOG_LEVEL.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Set level
    level = level if level is not None else config.LOG_LEVEL
    logger.setLevel(level)
    
    # Avoid adding handlers if they already exist
    if not logger.handlers:
        # Create formatters
        formatter = logging.Formatter(config.LOG_FORMAT)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if log_file is specified
        if log_file or config.LOG_FILE:
            file_path = Path(log_file) if log_file else config.LOG_FILE
            try:
                file_handler = logging.FileHandler(file_path)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except (IOError, PermissionError) as e:
                logger.warning(f"Could not create log file at {file_path}: {e}")
    
    return logger
