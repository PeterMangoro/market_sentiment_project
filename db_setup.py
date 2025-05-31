#!/usr/bin/env python3
"""
Main entry point for database setup and data loading.

This script provides a convenient way to create the database and load data
from the command line or by importing into other scripts.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from db.schema import create_database
from db.loaders import load_stock_data, load_news_data, load_twitter_data
from db.utils.logging_utils import get_logger

logger = get_logger(__name__)

def setup_database(db_path=None, load_all=True, load_stocks=False, 
                  load_news=False, load_tweets=False, data_dir=None):
    """
    Set up the database and optionally load data.
    
    Args:
        db_path (str or Path, optional): Path to the database file.
        load_all (bool, optional): Whether to load all data types. Defaults to True.
        load_stocks (bool, optional): Whether to load stock data. Defaults to False.
        load_news (bool, optional): Whether to load news data. Defaults to False.
        load_tweets (bool, optional): Whether to load Twitter data. Defaults to False.
        data_dir (str or Path, optional): Directory containing data files.
    
    Returns:
        dict: Summary of operations performed.
    """
    from db import config
    from db.schema import get_db_connection
    
    # Set up paths
    db_path = Path(db_path) if db_path else config.DB_PATH
    data_dir = Path(data_dir) if data_dir else config.DATA_DIR
    stock_data_dir = data_dir / 'stock_data'
    news_data_path = data_dir / 'news_with_sentiment.json'
    twitter_data_path = data_dir / 'twitter_with_sentiment.json'
    
    logger.info(f"Setting up database at {db_path}")
    logger.info(f"Using data directory: {data_dir}")
    
    # Create database schema
    success = create_database(db_path)
    if not success:
        logger.error("Failed to create database schema")
        return {"error": "Failed to create database schema"}
    
    summary = {"schema_created": True}
    
    # Determine which data to load
    if load_all:
        load_stocks = load_news = load_tweets = True
    
    # Load data
    with get_db_connection(db_path) as conn:
        # Load stock data first (required for relationships)
        if load_stocks:
            logger.info("Loading stock data...")
            result = load_stock_data(conn, stock_data_dir)
            summary["stock_data"] = result
        
        # Load news data
        if load_news:
            logger.info("Loading news data...")
            result = load_news_data(conn, news_data_path)
            summary["news_data"] = result
        
        # Load Twitter data
        if load_tweets:
            logger.info("Loading Twitter data...")
            result = load_twitter_data(conn, twitter_data_path)
            summary["twitter_data"] = result
    
    logger.info("Database setup complete")
    return summary

def main():
    """
    Main function when script is run directly.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    # Import here to avoid circular imports
    from db.cli import main as cli_main
    return cli_main()

if __name__ == "__main__":
    sys.exit(main())
