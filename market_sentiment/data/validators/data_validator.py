"""
Data validator module.

This module provides functionality for validating data before processing or analysis.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable

from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataValidator:
    """
    Validator for market sentiment data.
    
    This class provides methods for validating data from various sources
    to ensure it meets the expected format and quality standards.
    """
    
    def __init__(self):
        """Initialize the DataValidator."""
        logger.info("Initialized DataValidator")
    
    def validate_news_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Validate news data.
        
        Args:
            data: News data to validate, either as a dictionary with a 'data' key
                 containing a list of articles, or a direct list of articles.
        
        Returns:
            Dictionary with validation results:
            - valid: Whether the data is valid
            - errors: List of validation errors
            - warnings: List of validation warnings
            - article_count: Number of valid articles
        """
        logger.info("Validating news data")
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "article_count": 0
        }
        
        # Check if data is a dictionary with a 'data' key
        if isinstance(data, dict):
            if "data" not in data:
                result["valid"] = False
                result["errors"].append("Missing 'data' key in news data dictionary")
                return result
            
            articles = data.get("data", [])
        elif isinstance(data, list):
            articles = data
        else:
            result["valid"] = False
            result["errors"].append(f"Invalid news data type: {type(data)}, expected dict or list")
            return result
        
        # Check if articles is a list
        if not isinstance(articles, list):
            result["valid"] = False
            result["errors"].append(f"Invalid articles type: {type(articles)}, expected list")
            return result
        
        # Check if articles list is empty
        if not articles:
            result["warnings"].append("News articles list is empty")
        
        # Validate each article
        valid_articles = 0
        for i, article in enumerate(articles):
            if not isinstance(article, dict):
                result["warnings"].append(f"Article at index {i} is not a dictionary")
                continue
            
            # Check for required fields
            required_fields = ["title", "published_at"]
            missing_fields = [field for field in required_fields if field not in article]
            
            if missing_fields:
                result["warnings"].append(f"Article at index {i} is missing required fields: {', '.join(missing_fields)}")
                continue
            
            valid_articles += 1
        
        result["article_count"] = valid_articles
        
        if valid_articles == 0 and articles:
            result["valid"] = False
            result["errors"].append("No valid articles found")
        
        logger.info(f"News data validation result: valid={result['valid']}, article_count={result['article_count']}")
        return result
    
    def validate_twitter_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate Twitter data.
        
        Args:
            data: Twitter data to validate, as a list of query response dictionaries.
        
        Returns:
            Dictionary with validation results:
            - valid: Whether the data is valid
            - errors: List of validation errors
            - warnings: List of validation warnings
            - query_count: Number of valid queries
            - tweet_count: Number of valid tweets
        """
        logger.info("Validating Twitter data")
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "query_count": 0,
            "tweet_count": 0
        }
        
        # Check if data is a list
        if not isinstance(data, list):
            result["valid"] = False
            result["errors"].append(f"Invalid Twitter data type: {type(data)}, expected list")
            return result
        
        # Check if data list is empty
        if not data:
            result["warnings"].append("Twitter data list is empty")
        
        # Validate each query response
        valid_queries = 0
        total_tweets = 0
        
        for i, query_response in enumerate(data):
            if not isinstance(query_response, dict):
                result["warnings"].append(f"Query response at index {i} is not a dictionary")
                continue
            
            # Check for required fields
            if "query" not in query_response:
                result["warnings"].append(f"Query response at index {i} is missing 'query' field")
                continue
            
            if "response" not in query_response:
                result["warnings"].append(f"Query response at index {i} is missing 'response' field")
                continue
            
            response = query_response.get("response", {})
            
            # Check if response has the expected structure
            if not response or not isinstance(response, dict):
                result["warnings"].append(f"Response for query '{query_response.get('query')}' is empty or invalid")
                continue
            
            # Try to extract tweets from the response
            tweets = self._extract_tweets_from_response(response)
            
            if not tweets:
                result["warnings"].append(f"No tweets found in response for query '{query_response.get('query')}'")
                continue
            
            valid_queries += 1
            total_tweets += len(tweets)
        
        result["query_count"] = valid_queries
        result["tweet_count"] = total_tweets
        
        if valid_queries == 0 and data:
            result["valid"] = False
            result["errors"].append("No valid query responses found")
        
        logger.info(f"Twitter data validation result: valid={result['valid']}, query_count={result['query_count']}, tweet_count={result['tweet_count']}")
        return result
    
    def validate_stock_data(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate stock data.
        
        Args:
            data: Stock data to validate, as a dictionary mapping symbols to their data.
        
        Returns:
            Dictionary with validation results:
            - valid: Whether the data is valid
            - errors: List of validation errors
            - warnings: List of validation warnings
            - symbol_count: Number of valid symbols
            - data_point_count: Number of valid data points
        """
        logger.info("Validating stock data")
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "symbol_count": 0,
            "data_point_count": 0
        }
        
        # Check if data is a dictionary
        if not isinstance(data, dict):
            result["valid"] = False
            result["errors"].append(f"Invalid stock data type: {type(data)}, expected dict")
            return result
        
        # Check if data dictionary is empty
        if not data:
            result["warnings"].append("Stock data dictionary is empty")
        
        # Validate each symbol's data
        valid_symbols = 0
        total_data_points = 0
        
        for symbol, symbol_data in data.items():
            if not isinstance(symbol_data, dict):
                result["warnings"].append(f"Data for symbol '{symbol}' is not a dictionary")
                continue
            
            # Check if symbol data is empty
            if not symbol_data:
                result["warnings"].append(f"Data for symbol '{symbol}' is empty")
                continue
            
            # Check for required fields in each data point
            valid_data_points = 0
            
            for date, point_data in symbol_data.items():
                if not isinstance(point_data, dict):
                    result["warnings"].append(f"Data point for symbol '{symbol}', date '{date}' is not a dictionary")
                    continue
                
                # Check for required fields
                required_fields = ["Open", "High", "Low", "Close", "Volume"]
                missing_fields = [field for field in required_fields if field not in point_data]
                
                if missing_fields:
                    result["warnings"].append(f"Data point for symbol '{symbol}', date '{date}' is missing required fields: {', '.join(missing_fields)}")
                    continue
                
                valid_data_points += 1
            
            if valid_data_points > 0:
                valid_symbols += 1
                total_data_points += valid_data_points
            else:
                result["warnings"].append(f"No valid data points found for symbol '{symbol}'")
        
        result["symbol_count"] = valid_symbols
        result["data_point_count"] = total_data_points
        
        if valid_symbols == 0 and data:
            result["valid"] = False
            result["errors"].append("No valid symbols found")
        
        logger.info(f"Stock data validation result: valid={result['valid']}, symbol_count={result['symbol_count']}, data_point_count={result['data_point_count']}")
        return result
    
    def validate_json_file(self, file_path: Union[str, Path], validator_func: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Validate a JSON file.
        
        Args:
            file_path: Path to the JSON file to validate.
            validator_func: Optional function to validate the loaded data.
                           If None, only basic JSON validation is performed.
        
        Returns:
            Dictionary with validation results:
            - valid: Whether the file is valid
            - errors: List of validation errors
            - warnings: List of validation warnings
            - data: The loaded data if valid, None otherwise
        """
        file_path = Path(file_path)
        logger.info(f"Validating JSON file: {file_path}")
        
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "data": None
        }
        
        # Check if file exists
        if not file_path.exists():
            result["valid"] = False
            result["errors"].append(f"File not found: {file_path}")
            return result
        
        # Try to load JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            result["data"] = data
            
            # Apply custom validator if provided
            if validator_func:
                validation_result = validator_func(data)
                
                # Merge validation results
                result["valid"] = result["valid"] and validation_result.get("valid", True)
                result["errors"].extend(validation_result.get("errors", []))
                result["warnings"].extend(validation_result.get("warnings", []))
            
        except json.JSONDecodeError as e:
            result["valid"] = False
            result["errors"].append(f"Invalid JSON: {e}")
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error loading file: {e}")
        
        logger.info(f"JSON file validation result: valid={result['valid']}")
        return result
    
    def _extract_tweets_from_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tweets from a Twitter API response.
        
        Args:
            response: Twitter API response dictionary.
        
        Returns:
            List of extracted tweets.
        """
        tweets = []
        
        try:
            if (response.get("result") and 
                response["result"].get("timeline") and 
                response["result"]["timeline"].get("instructions")):
                
                entries = []
                for instruction in response["result"]["timeline"]["instructions"]:
                    if instruction.get("type") in ["TimelineAddEntries", "TimelineReplaceEntries"]:
                        if instruction.get("entries"):
                            entries.extend(instruction["entries"])
                
                for entry in entries:
                    # Extract tweet text
                    tweet_text = None
                    
                    # Path for typical tweets
                    if (entry.get("content") and entry["content"].get("itemContent") and 
                        entry["content"]["itemContent"].get("tweet_results") and 
                        entry["content"]["itemContent"]["tweet_results"].get("result") and 
                        entry["content"]["itemContent"]["tweet_results"]["result"].get("legacy") and 
                        entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"].get("full_text")):
                        
                        tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
                        tweets.append(entry)
                    
                    # Fallback for potentially different structures or retweets
                    elif (entry.get("content") and entry["content"].get("itemContent") and 
                          entry["content"]["itemContent"].get("tweet_results") and 
                          entry["content"]["itemContent"]["tweet_results"].get("result") and 
                          entry["content"]["itemContent"]["tweet_results"]["result"].get("tweet") and 
                          entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"].get("legacy") and 
                          entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"].get("full_text")):
                        
                        tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"]["full_text"]
                        tweets.append(entry)
        
        except (KeyError, AttributeError) as e:
            logger.debug(f"Error extracting tweets from response: {e}")
        
        return tweets
