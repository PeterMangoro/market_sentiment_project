"""
Market Sentiment Project package initialization.

This package provides functionality for collecting, analyzing, and visualizing
market sentiment data from various sources.
"""

__version__ = '0.1.0'

# Import key components for easy access
from .data.collectors import NewsCollector, StockCollector, TwitterCollector
from .data.processors import SentimentAnalyzer
from .models import RandomForestModel, XGBoostModel, ARIMAModel
from .visualization import SentimentPlotter, StockPlotter

__all__ = [
    'NewsCollector',
    'StockCollector',
    'TwitterCollector',
    'SentimentAnalyzer',
    'RandomForestModel',
    'XGBoostModel',
    'ARIMAModel',
    'SentimentPlotter',
    'StockPlotter',
]
