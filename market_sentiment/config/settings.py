"""
General settings module.

This module provides general configuration settings for the Market Sentiment Project.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta

# Default stock symbols to track
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']

# Default date range for historical data (5 years)
DEFAULT_DATE_RANGE = {
    'start': (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d'),
    'end': datetime.now().strftime('%Y-%m-%d')
}

# Default sentiment thresholds
DEFAULT_SENTIMENT_THRESHOLDS = {
    'positive': 0.05,
    'negative': -0.05
}

# Default data collection settings
DEFAULT_COLLECTION_SETTINGS = {
    'news': {
        'limit': 100,
        'language': 'en'
    },
    'twitter': {
        'limit': 100,
        'language': 'en'
    },
    'stock': {
        'interval': '1d'  # daily data
    }
}

# Default model parameters
DEFAULT_MODEL_PARAMS = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'xgboost': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 5,
        'random_state': 42
    },
    'arima': {
        'order': (5, 1, 0)
    }
}

# Default visualization settings
DEFAULT_VISUALIZATION_SETTINGS = {
    'figsize': (12, 8),
    'style': 'seaborn-v0_8-darkgrid',
    'palette': 'viridis',
    'dpi': 100
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'market_sentiment.log',
            'mode': 'a'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
