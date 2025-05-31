"""
Path configuration module.

This module provides functions for managing file paths in the Market Sentiment Project.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_DATA_DIR = DEFAULT_PROJECT_ROOT / 'data'
DEFAULT_OUTPUT_DIR = DEFAULT_PROJECT_ROOT / 'output'

def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root directory.
    """
    return DEFAULT_PROJECT_ROOT

def get_data_dir(create: bool = True) -> Path:
    """
    Get the data directory path.
    
    Args:
        create: If True, create the directory if it doesn't exist.
    
    Returns:
        Path to the data directory.
    """
    data_dir = os.environ.get('MARKET_SENTIMENT_DATA_DIR')
    if data_dir:
        data_dir = Path(data_dir)
    else:
        data_dir = DEFAULT_DATA_DIR
    
    if create and not data_dir.exists():
        logger.info(f"Creating data directory: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir

def get_output_dir(create: bool = True) -> Path:
    """
    Get the output directory path.
    
    Args:
        create: If True, create the directory if it doesn't exist.
    
    Returns:
        Path to the output directory.
    """
    output_dir = os.environ.get('MARKET_SENTIMENT_OUTPUT_DIR')
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = DEFAULT_OUTPUT_DIR
    
    if create and not output_dir.exists():
        logger.info(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir

def ensure_dir_exists(path: Path) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to check/create.
    
    Returns:
        Path object of the directory.
    """
    if not path.exists():
        logger.info(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path

def get_stock_data_dir(create: bool = True) -> Path:
    """
    Get the stock data directory path.
    
    Args:
        create: If True, create the directory if it doesn't exist.
    
    Returns:
        Path to the stock data directory.
    """
    stock_data_dir = get_data_dir() / 'stock_data'
    if create and not stock_data_dir.exists():
        logger.info(f"Creating stock data directory: {stock_data_dir}")
        stock_data_dir.mkdir(parents=True, exist_ok=True)
    return stock_data_dir
