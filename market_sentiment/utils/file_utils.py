"""
Utility functions for file operations.

This module provides file operation utilities for the Market Sentiment Project.
"""

import json
import csv
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

from .logging_utils import get_logger

logger = get_logger(__name__)

def ensure_dir_exists(path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to check/create.
    
    Returns:
        Path object of the directory.
    """
    path = Path(path)
    if not path.exists():
        logger.info(f"Creating directory: {path}")
        path.mkdir(parents=True, exist_ok=True)
    return path

def load_json(file_path: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file.
    
    Returns:
        Loaded data.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    file_path = Path(file_path)
    logger.debug(f"Loading JSON from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise

def save_json(data: Any, file_path: Union[str, Path], indent: int = 4) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save.
        file_path: Path to save the data to.
        indent: Indentation level for the JSON file. Defaults to 4.
    
    Raises:
        IOError: If an error occurs while saving the file.
    """
    file_path = Path(file_path)
    logger.debug(f"Saving JSON to {file_path}")
    
    # Ensure parent directory exists
    ensure_dir_exists(file_path.parent)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        logger.debug(f"Data saved to {file_path}")
    except IOError as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        raise

def load_csv(file_path: Union[str, Path], has_header: bool = True) -> List[Dict[str, str]]:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to the CSV file.
        has_header: Whether the CSV file has a header row. Defaults to True.
    
    Returns:
        List of dictionaries, where each dictionary represents a row.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        csv.Error: If the file is not valid CSV.
    """
    file_path = Path(file_path)
    logger.debug(f"Loading CSV from {file_path}")
    
    try:
        with open(file_path, 'r', newline='') as f:
            if has_header:
                reader = csv.DictReader(f)
                return list(reader)
            else:
                reader = csv.reader(f)
                data = list(reader)
                return [dict(zip([f"col{i}" for i in range(len(row))], row)) for row in data]
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except csv.Error as e:
        logger.error(f"Invalid CSV in {file_path}: {e}")
        raise

def save_csv(data: List[Dict[str, Any]], file_path: Union[str, Path], fieldnames: Optional[List[str]] = None) -> None:
    """
    Save data to a CSV file.
    
    Args:
        data: List of dictionaries to save.
        file_path: Path to save the data to.
        fieldnames: List of field names for the CSV header. If None, uses the keys of the first dictionary.
    
    Raises:
        IOError: If an error occurs while saving the file.
    """
    file_path = Path(file_path)
    logger.debug(f"Saving CSV to {file_path}")
    
    # Ensure parent directory exists
    ensure_dir_exists(file_path.parent)
    
    # Determine fieldnames if not provided
    if fieldnames is None and data:
        fieldnames = list(data[0].keys())
    
    try:
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.debug(f"Data saved to {file_path}")
    except IOError as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        raise

def copy_file(source: Union[str, Path], destination: Union[str, Path], overwrite: bool = False) -> None:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path.
        destination: Destination file path.
        overwrite: Whether to overwrite the destination file if it exists. Defaults to False.
    
    Raises:
        FileNotFoundError: If the source file does not exist.
        FileExistsError: If the destination file exists and overwrite is False.
    """
    source = Path(source)
    destination = Path(destination)
    logger.debug(f"Copying {source} to {destination}")
    
    if not source.exists():
        logger.error(f"Source file not found: {source}")
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if destination.exists() and not overwrite:
        logger.error(f"Destination file already exists: {destination}")
        raise FileExistsError(f"Destination file already exists: {destination}")
    
    # Ensure parent directory exists
    ensure_dir_exists(destination.parent)
    
    try:
        shutil.copy2(source, destination)
        logger.debug(f"File copied from {source} to {destination}")
    except IOError as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        raise
