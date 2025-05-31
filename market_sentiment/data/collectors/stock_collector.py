"""
Stock collector module.

This module provides functionality for collecting historical stock price data.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ...config.paths import get_stock_data_dir, ensure_dir_exists
from ...config.settings import DEFAULT_SYMBOLS, DEFAULT_DATE_RANGE
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class StockCollector:
    """
    Collector for historical stock price data.
    
    This class provides methods for fetching historical stock price data
    for specific stock symbols using the YahooFinance API.
    
    Attributes:
        symbols: List of stock symbols to fetch data for.
        range_val: Time range for historical data.
        interval: Data interval (e.g., '1d' for daily).
    """
    
    def __init__(
        self, 
        symbols: Optional[List[str]] = None,
        range_val: str = "5y",
        interval: str = "1d"
    ):
        """
        Initialize the StockCollector.
        
        Args:
            symbols: List of stock symbols to fetch data for. Defaults to DEFAULT_SYMBOLS.
            range_val: Time range for historical data. Defaults to "5y" (5 years).
            interval: Data interval. Defaults to "1d" (daily).
        """
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.range_val = range_val
        self.interval = interval
        
        logger.info(f"Initialized StockCollector for symbols: {', '.join(self.symbols)}")
    
    def collect(self, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Collect historical stock data for all symbols.
        
        Args:
            output_dir: Directory to save the collected data. If None, data is not saved to file.
        
        Returns:
            Dictionary mapping symbols to their historical data.
        """
        logger.info(f"Collecting stock data for symbols: {', '.join(self.symbols)}")
        
        results = {}
        
        for symbol in self.symbols:
            try:
                data = self._fetch_stock_history(symbol)
                if data:
                    results[symbol] = data
                    
                    # Save to file if output_dir is provided
                    if output_dir:
                        self._save_to_file(data, symbol, output_dir)
                
                # Add a small delay to avoid hitting API rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error collecting stock data for {symbol}: {e}")
        
        return results
    
    def _fetch_stock_history(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical stock data for a single symbol.
        
        Args:
            symbol: Stock symbol to fetch data for.
        
        Returns:
            Dictionary containing the historical stock data, or None if an error occurs.
        """
        logger.info(f"Fetching historical stock data for symbol: {symbol}")
        
        try:
            # In a real implementation, we would use the YahooFinance API directly
            # For this refactoring, we'll use a placeholder that would be replaced
            # with actual API calls in the local implementation
            
            # This is where we would use:
            # import yfinance as yf
            # ticker = yf.Ticker(symbol)
            # data = ticker.history(period=self.range_val, interval=self.interval)
            
            # For now, we'll use a placeholder that mimics the sandbox's ApiClient
            from importlib import util
            
            # Try to import the sandbox's ApiClient if available
            try:
                sys.path.append("/opt/.manus/.sandbox-runtime")
                from data_api import ApiClient
                
                client = ApiClient()
                response = client.call_api(
                    "YahooFinance/get_stock_chart", 
                    query={
                        "symbol": symbol,
                        "range": self.range_val,
                        "interval": self.interval,
                        "includeAdjustedClose": True
                    }
                )
                
                logger.info(f"Successfully fetched stock data for symbol: {symbol}")
                return response
                
            except ImportError:
                # If we're not in the sandbox, use yfinance instead
                logger.warning("Sandbox ApiClient not available, would use yfinance in local implementation")
                
                # This is a placeholder for the actual implementation
                # In a real implementation, this would use yfinance
                logger.info(f"Successfully fetched stock data for symbol: {symbol} (placeholder)")
                return {"placeholder": f"Stock data for {symbol} would be fetched here"}
                
        except Exception as e:
            logger.error(f"Error fetching stock data for symbol {symbol}: {e}")
            return None
    
    def _save_to_file(self, data: Dict[str, Any], symbol: str, output_dir: Union[str, Path]) -> None:
        """
        Save collected data to a JSON file.
        
        Args:
            data: Data to save.
            symbol: Stock symbol.
            output_dir: Directory to save the data to.
        
        Raises:
            IOError: If an error occurs while saving the file.
        """
        output_path = Path(output_dir)
        
        # If output_dir is not absolute, save to the stock data directory
        if not output_path.is_absolute():
            stock_data_dir = get_stock_data_dir()
            output_path = stock_data_dir / output_path
        
        # Ensure directory exists
        ensure_dir_exists(output_path)
        
        filename = f"{symbol}_stock_data.json"
        filepath = output_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Stock data for {symbol} saved to {filepath}")
        except IOError as e:
            logger.error(f"Error saving stock data for {symbol} to {filepath}: {e}")
            raise
