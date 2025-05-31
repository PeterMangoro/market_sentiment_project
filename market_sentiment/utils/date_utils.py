"""
Date utility functions.

This module provides date and time utilities for the Market Sentiment Project.
"""

import datetime
from typing import Dict, List, Union, Optional, Tuple

from .logging_utils import get_logger

logger = get_logger(__name__)

def get_date_range(days_back: int = 30) -> Dict[str, str]:
    """
    Get a date range from days_back days ago to today.
    
    Args:
        days_back: Number of days to go back from today. Defaults to 30.
    
    Returns:
        Dictionary with 'start' and 'end' dates in 'YYYY-MM-DD' format.
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    return {
        'start': start_date.strftime('%Y-%m-%d'),
        'end': end_date.strftime('%Y-%m-%d')
    }

def parse_date(date_str: str) -> datetime.datetime:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse.
    
    Returns:
        Datetime object.
    
    Raises:
        ValueError: If the date string cannot be parsed.
    """
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%a %b %d %H:%M:%S %z %Y'  # Twitter format: "Wed Oct 10 20:19:24 +0000 2018"
    ]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.error(f"Could not parse date string: {date_str}")
    raise ValueError(f"Could not parse date string: {date_str}")

def format_date(date: Union[datetime.datetime, str], output_format: str = '%Y-%m-%d') -> str:
    """
    Format a date object or string into a specified format.
    
    Args:
        date: Date to format, either as a datetime object or a string.
        output_format: Output format string. Defaults to 'YYYY-MM-DD'.
    
    Returns:
        Formatted date string.
    
    Raises:
        ValueError: If the date string cannot be parsed.
    """
    if isinstance(date, str):
        date = parse_date(date)
    
    return date.strftime(output_format)

def date_to_unix_timestamp(date: Union[datetime.datetime, str]) -> int:
    """
    Convert a date to a Unix timestamp (seconds since epoch).
    
    Args:
        date: Date to convert, either as a datetime object or a string.
    
    Returns:
        Unix timestamp.
    
    Raises:
        ValueError: If the date string cannot be parsed.
    """
    if isinstance(date, str):
        date = parse_date(date)
    
    return int(date.timestamp())

def unix_timestamp_to_date(timestamp: int) -> datetime.datetime:
    """
    Convert a Unix timestamp to a datetime object.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch).
    
    Returns:
        Datetime object.
    """
    return datetime.datetime.fromtimestamp(timestamp)

def get_trading_days(start_date: Union[datetime.datetime, str], 
                     end_date: Union[datetime.datetime, str]) -> List[datetime.datetime]:
    """
    Get a list of trading days (weekdays) between start_date and end_date.
    
    Args:
        start_date: Start date, either as a datetime object or a string.
        end_date: End date, either as a datetime object or a string.
    
    Returns:
        List of datetime objects representing trading days.
    
    Raises:
        ValueError: If the date strings cannot be parsed.
    """
    if isinstance(start_date, str):
        start_date = parse_date(start_date)
    
    if isinstance(end_date, str):
        end_date = parse_date(end_date)
    
    # Ensure start_date is earlier than end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    trading_days = []
    current_date = start_date
    
    while current_date <= end_date:
        # Weekday is 0-6 (Monday-Sunday), 0-4 are weekdays
        if current_date.weekday() < 5:
            trading_days.append(current_date)
        
        current_date += datetime.timedelta(days=1)
    
    return trading_days
