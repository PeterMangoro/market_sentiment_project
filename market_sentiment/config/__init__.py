"""
Configuration package initialization.

This package provides configuration settings for the Market Sentiment Project.
"""

from .settings import (
    DEFAULT_SYMBOLS,
    DEFAULT_DATE_RANGE,
    DEFAULT_SENTIMENT_THRESHOLDS
)
from .api_config import load_api_keys
from .paths import get_data_dir, get_output_dir

__all__ = [
    'DEFAULT_SYMBOLS',
    'DEFAULT_DATE_RANGE',
    'DEFAULT_SENTIMENT_THRESHOLDS',
    'load_api_keys',
    'get_data_dir',
    'get_output_dir'
]
