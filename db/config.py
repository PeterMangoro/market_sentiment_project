"""
Configuration settings for the market sentiment database.

This module centralizes all configuration settings for the database,
including paths, database name, and other constants.
"""

import os
import logging
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = PROJECT_ROOT / 'data'
DB_NAME = 'market_sentiment.db'
DB_PATH = PROJECT_ROOT / DB_NAME

# Data file paths
NEWS_DATA_PATH = DATA_DIR / 'news_with_sentiment.json'
TWITTER_DATA_PATH = DATA_DIR / 'twitter_with_sentiment.json'
STOCK_DATA_DIR = DATA_DIR / 'stock_data'

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = PROJECT_ROOT / 'db_operations.log'

# Stock symbols to track
TRACKED_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']

# Sentiment thresholds
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05
