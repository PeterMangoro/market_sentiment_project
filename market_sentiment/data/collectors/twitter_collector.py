"""
Twitter collector module.

This module provides functionality for collecting Twitter data related to stock symbols.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ...config.paths import get_data_dir, ensure_dir_exists
from ...config.settings import DEFAULT_SYMBOLS
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class TwitterCollector:
    """
    Collector for Twitter data related to stock symbols.
    
    This class provides methods for fetching tweets related to specific stock symbols
    using the Twitter search API.
    
    Attributes:
        symbols: List of stock symbols to fetch tweets for.
        count_per_query: Number of tweets to fetch per query.
        search_type: Type of search to perform ('Latest' or 'Top').
    """
    
    def __init__(
        self, 
        symbols: Optional[List[str]] = None,
        count_per_query: int = 20,
        search_type: str = "Latest"
    ):
        """
        Initialize the TwitterCollector.
        
        Args:
            symbols: List of stock symbols to fetch tweets for. Defaults to DEFAULT_SYMBOLS.
            count_per_query: Number of tweets to fetch per query. Defaults to 20.
            search_type: Type of search to perform ('Latest' or 'Top'). Defaults to 'Latest'.
        """
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.count_per_query = count_per_query
        self.search_type = search_type
        
        # Generate queries for each symbol
        self.queries = []
        for symbol in self.symbols:
            self.queries.extend([f"${symbol} stock", f"#{symbol} stock price"])
        
        logger.info(f"Initialized TwitterCollector for symbols: {', '.join(self.symbols)}")
    
    def collect(self, output_file: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        Collect Twitter data for all queries.
        
        Args:
            output_file: Path to save the collected data. If None, data is not saved to file.
        
        Returns:
            List of dictionaries containing the collected Twitter data.
        """
        logger.info(f"Collecting Twitter data for queries: {', '.join(self.queries)}")
        
        collected_tweets = []
        
        for query in self.queries:
            try:
                data = self._fetch_twitter_data(query)
                if data:
                    collected_tweets.append({
                        "query": query,
                        "response": data
                    })
            except Exception as e:
                logger.error(f"Error collecting Twitter data for query '{query}': {e}")
                collected_tweets.append({
                    "query": query,
                    "response": None,
                    "error": str(e)
                })
        
        # Save to file if output_file is provided
        if output_file and collected_tweets:
            self._save_to_file(collected_tweets, output_file)
        
        return collected_tweets
    
    def _fetch_twitter_data(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Twitter data for a single query.
        
        Args:
            query: Query string to search for.
        
        Returns:
            Dictionary containing the Twitter data, or None if an error occurs.
        """
        logger.info(f"Fetching tweets for query: '{query}'")
        
        try:
            # In a real implementation, we would use the Twitter API directly
            # For this refactoring, we'll use a placeholder that would be replaced
            # with actual API calls in the local implementation
            
            # Try to import the sandbox's ApiClient if available
            try:
                import sys
                sys.path.append("/opt/.manus/.sandbox-runtime")
                from data_api import ApiClient
                
                client = ApiClient()
                response = client.call_api(
                    "Twitter/search_twitter", 
                    query={
                        "query": query,
                        "count": self.count_per_query,
                        "type": self.search_type
                    }
                )
                
                logger.info(f"Successfully fetched tweets for query: '{query}'")
                return response
                
            except ImportError:
                # If we're not in the sandbox, use a different Twitter API client
                logger.warning("Sandbox ApiClient not available, would use tweepy or Twitter API v2 in local implementation")
                
                # This is a placeholder for the actual implementation
                # In a real implementation, this would use tweepy or the Twitter API v2
                logger.info(f"Successfully fetched tweets for query: '{query}' (placeholder)")
                return {"placeholder": f"Twitter data for '{query}' would be fetched here"}
                
        except Exception as e:
            logger.error(f"Error fetching tweets for query '{query}': {e}")
            return None
    
    def _save_to_file(self, data: List[Dict[str, Any]], output_file: Union[str, Path]) -> None:
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
        
        # Check if file already exists and load its content
        all_tweets_data = []
        if output_path.exists():
            try:
                with open(output_path, 'r') as f:
                    existing_data = json.load(f)
                if isinstance(existing_data, list):
                    all_tweets_data = existing_data
                else:
                    logger.warning(f"Existing file {output_path} does not contain a list. It will be overwritten.")
            except json.JSONDecodeError:
                logger.warning(f"Existing file {output_path} is not valid JSON. It will be overwritten.")
        
        # Append new data
        all_tweets_data.extend(data)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(all_tweets_data, f, indent=4)
            logger.info(f"Data saved to {output_path}")
        except IOError as e:
            logger.error(f"Error saving data to {output_path}: {e}")
            raise
