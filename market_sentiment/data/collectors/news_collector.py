"""
News collector module.

This module provides functionality for collecting financial news data from the Marketaux API.
"""

import requests
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ...config.api_config import get_api_key
from ...config.paths import get_data_dir, ensure_dir_exists
from ...config.settings import DEFAULT_SYMBOLS, DEFAULT_COLLECTION_SETTINGS
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class NewsCollector:
    """
    Collector for financial news data from the Marketaux API.
    
    This class provides methods for fetching financial news articles
    related to specific stock symbols from the Marketaux API.
    
    Attributes:
        base_url: Base URL for the Marketaux API.
        api_key: API key for accessing the Marketaux API.
        symbols: List of stock symbols to fetch news for.
        params: Additional parameters for the API request.
    """
    
    def __init__(
        self, 
        symbols: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        language: str = 'en',
        limit: int = 10
    ):
        """
        Initialize the NewsCollector.
        
        Args:
            symbols: List of stock symbols to fetch news for. Defaults to DEFAULT_SYMBOLS.
            api_key: API key for accessing the Marketaux API. If None, attempts to load from config.
            language: Language of news articles. Defaults to 'en'.
            limit: Maximum number of articles to fetch. Defaults to 10.
        
        Raises:
            ValueError: If no API key is provided and none can be loaded from config.
        """
        self.base_url = "https://api.marketaux.com/v1/news/all"
        self.symbols = symbols or DEFAULT_SYMBOLS
        
        # Get API key
        self.api_key = api_key or get_api_key('MARKETAUX_API_KEY')
        if not self.api_key:
            logger.error("No Marketaux API key provided or found in configuration")
            raise ValueError("Marketaux API key is required")
        
        # Set default parameters
        self.params = {
            "api_token": self.api_key,
            "symbols": ",".join(self.symbols),
            "language": language,
            "limit": limit
        }
        
        logger.info(f"Initialized NewsCollector for symbols: {', '.join(self.symbols)}")
    
    def collect(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Collect news data from the Marketaux API.
        
        Args:
            output_file: Path to save the collected data. If None, data is not saved to file.
        
        Returns:
            Dictionary containing the collected news data.
        
        Raises:
            requests.exceptions.RequestException: If an error occurs during the API request.
        """
        logger.info(f"Collecting news for symbols: {', '.join(self.symbols)}")
        
        try:
            response = requests.get(self.base_url, params=self.params)
            response.raise_for_status()
            
            news_data = response.json()
            
            if not news_data.get("data"):
                logger.warning("API response does not contain 'data' key or it's empty")
            else:
                article_count = len(news_data["data"])
                logger.info(f"Successfully collected {article_count} news articles")
            
            # Save to file if output_file is provided
            if output_file:
                self._save_to_file(news_data, output_file)
            
            return news_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error collecting news data: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    def _save_to_file(self, data: Dict[str, Any], output_file: Union[str, Path]) -> None:
        """
        Save collected data to a JSON file.
        
        Args:
            data: Data to save.
            output_file: Path to save the data to.
        
        Raises:
            IOError: If an error occurs while saving the file.
        """
        output_path = Path(output_file)
        
        # If output_file is just a filename, save to the data directory
        if not output_path.is_absolute():
            data_dir = get_data_dir()
            output_path = data_dir / output_path
        
        # Ensure parent directory exists
        ensure_dir_exists(output_path.parent)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Data saved to {output_path}")
        except IOError as e:
            logger.error(f"Error saving data to {output_path}: {e}")
            raise
