"""
Command-line interface for database operations.

This module provides a command-line interface for creating the database
and loading data from various sources.
"""

import argparse
import sys
from pathlib import Path

from . import config
from .schema import create_database
from .loaders import load_stock_data, load_news_data, load_twitter_data
from .utils.logging_utils import get_logger

logger = get_logger(__name__)

def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Market Sentiment Database Setup and Data Loading'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        help='Path to the database file (default: %(default)s)',
        default=str(config.DB_PATH)
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Directory containing data files (default: %(default)s)',
        default=str(config.DATA_DIR)
    )
    
    parser.add_argument(
        '--schema-only',
        action='store_true',
        help='Create database schema only, without loading data'
    )
    
    parser.add_argument(
        '--load-stocks',
        action='store_true',
        help='Load stock data'
    )
    
    parser.add_argument(
        '--load-news',
        action='store_true',
        help='Load news data'
    )
    
    parser.add_argument(
        '--load-tweets',
        action='store_true',
        help='Load Twitter data'
    )
    
    parser.add_argument(
        '--load-all',
        action='store_true',
        help='Load all data types'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='Increase verbosity (can be used multiple times)'
    )
    
    return parser.parse_args()

def configure_logging(verbosity):
    """
    Configure logging based on verbosity level.
    
    Args:
        verbosity (int): Verbosity level (0=INFO, 1=DEBUG).
    """
    import logging
    
    if verbosity >= 1:
        logging.getLogger('db').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

def main():
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    args = parse_args()
    configure_logging(args.verbose)
    
    db_path = Path(args.db_path)
    data_dir = Path(args.data_dir)
    stock_data_dir = data_dir / 'stock_data'
    news_data_path = data_dir / 'news_with_sentiment.json'
    twitter_data_path = data_dir / 'twitter_with_sentiment.json'
    
    logger.info(f"Database path: {db_path}")
    logger.info(f"Data directory: {data_dir}")
    
    # Create database schema
    success = create_database(db_path)
    if not success:
        logger.error("Failed to create database schema")
        return 1
    
    if args.schema_only:
        logger.info("Schema created successfully. Exiting as requested.")
        return 0
    
    # Determine which data to load
    load_all = args.load_all
    load_stocks = args.load_stocks or load_all
    load_news = args.load_news or load_all
    load_tweets = args.load_tweets or load_all
    
    # If no specific load option is selected, load all by default
    if not (load_stocks or load_news or load_tweets):
        logger.info("No specific data load option selected. Loading all data by default.")
        load_stocks = load_news = load_tweets = True
    
    # Load data
    from .schema import get_db_connection
    with get_db_connection(db_path) as conn:
        # Load stock data first (required for relationships)
        if load_stocks:
            logger.info("Loading stock data...")
            result = load_stock_data(conn, stock_data_dir)
            if "error" in result:
                logger.error(f"Error loading stock data: {result['error']}")
            else:
                logger.info(f"Successfully loaded stock data: {result['total']} records")
        
        # Load news data
        if load_news:
            logger.info("Loading news data...")
            result = load_news_data(conn, news_data_path)
            if "error" in result:
                logger.error(f"Error loading news data: {result['error']}")
            else:
                logger.info(f"Successfully loaded news data: {result['total']} articles, {result.get('linked', 0)} links")
        
        # Load Twitter data
        if load_tweets:
            logger.info("Loading Twitter data...")
            result = load_twitter_data(conn, twitter_data_path)
            if "error" in result:
                logger.error(f"Error loading Twitter data: {result['error']}")
            else:
                logger.info(f"Successfully loaded Twitter data: {result['total']} tweets, {result.get('linked', 0)} links")
    
    logger.info("Database setup and data loading complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
