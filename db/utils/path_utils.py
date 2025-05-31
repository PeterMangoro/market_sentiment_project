"""
Utility functions for file path operations.

This module provides utility functions for handling file paths,
ensuring they exist, and validating file types.
"""

import os
import json
from pathlib import Path

from .logging_utils import get_logger

logger = get_logger(__name__)

def ensure_dir_exists(directory):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory (str or Path): Directory path to check/create.
    
    Returns:
        Path: Path object of the directory.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.info(f"Creating directory: {dir_path}")
        dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def validate_file_exists(file_path, required=True):
    """
    Validate that a file exists.
    
    Args:
        file_path (str or Path): Path to the file.
        required (bool, optional): Whether the file is required. 
            If True and file doesn't exist, raises FileNotFoundError.
            Defaults to True.
    
    Returns:
        Path or None: Path object if file exists, None otherwise.
    
    Raises:
        FileNotFoundError: If required is True and file doesn't exist.
    """
    path = Path(file_path)
    if path.exists() and path.is_file():
        return path
    
    if required:
        logger.error(f"Required file not found: {path}")
        raise FileNotFoundError(f"Required file not found: {path}")
    
    logger.warning(f"File not found: {path}")
    return None

def load_json_file(file_path):
    """
    Load and parse a JSON file.
    
    Args:
        file_path (str or Path): Path to the JSON file.
    
    Returns:
        dict or list: Parsed JSON data.
    
    Raises:
        FileNotFoundError: If file doesn't exist.
        json.JSONDecodeError: If file contains invalid JSON.
    """
    path = validate_file_exists(file_path)
    
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {path}: {e}")
        raise

def get_files_with_extension(directory, extension):
    """
    Get all files with a specific extension in a directory.
    
    Args:
        directory (str or Path): Directory to search.
        extension (str): File extension to match (e.g., '.json').
    
    Returns:
        list: List of Path objects for matching files.
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.warning(f"Directory not found: {dir_path}")
        return []
    
    return list(dir_path.glob(f"*{extension}"))
