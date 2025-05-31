"""
Stock data loader module.

This module provides functionality for loading stock price data into the database.
"""

import os
import json
from pathlib import Path

from .. import config
from ..schema import get_db_connection
from ..utils.logging_utils import get_logger
from ..utils.path_utils import validate_file_exists, get_files_with_extension, load_json_file

logger = get_logger(__name__)

def load_stock_data(conn=None, stock_data_dir=None):
    """
    Load stock data from JSON files into the database.
    
    Args:
        conn (sqlite3.Connection, optional): Database connection.
            If None, a new connection will be created.
        stock_data_dir (str or Path, optional): Directory containing stock data files.
            Defaults to the directory specified in config.
    
    Returns:
        dict: Summary of loaded data with counts per symbol.
    """
    stock_data_dir = Path(stock_data_dir) if stock_data_dir else config.STOCK_DATA_DIR
    
    if not stock_data_dir.exists() or not stock_data_dir.is_dir():
        logger.error(f"Stock data directory not found: {stock_data_dir}")
        return {"error": f"Stock data directory not found: {stock_data_dir}", "loaded_count": 0}
    
    logger.info(f"Loading stock data from {stock_data_dir}")
    
    # Use provided connection or create a new one
    close_conn = False
    if conn is None:
        conn = get_db_connection().__enter__()
        close_conn = True
    
    cursor = conn.cursor()
    summary = {"total": 0}
    
    try:
        # Process each stock data file
        stock_files = get_files_with_extension(stock_data_dir, '_stock_data.json')
        
        if not stock_files:
            logger.warning(f"No stock data files found in {stock_data_dir}")
            return {"warning": "No stock data files found", "loaded_count": 0}
        
        for file_path in stock_files:
            symbol = file_path.stem.split('_')[0]
            logger.info(f"Processing stock data for {symbol} from {file_path}")
            
            try:
                stock_data = load_json_file(file_path)
                
                # Insert stock data
                records_count = 0
                for date, data in stock_data.items():
                    cursor.execute('''
                    INSERT OR REPLACE INTO stocks 
                    (symbol, date, open, high, low, close, adj_close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol,
                        date,
                        data.get('Open', 0),
                        data.get('High', 0),
                        data.get('Low', 0),
                        data.get('Close', 0),
                        data.get('Adj Close', 0),
                        data.get('Volume', 0)
                    ))
                    records_count += 1
                
                conn.commit()
                summary[symbol] = records_count
                summary["total"] += records_count
                logger.info(f"Loaded {records_count} days of data for {symbol}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                conn.rollback()
                summary[f"{symbol}_error"] = str(e)
        
        logger.info(f"Stock data loading complete. Total records: {summary['total']}")
        return summary
        
    except Exception as e:
        logger.error(f"Error loading stock data: {e}")
        conn.rollback()
        return {"error": str(e), "loaded_count": 0}
        
    finally:
        if close_conn:
            conn.close()
