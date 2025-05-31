"""
Twitter data loader module.

This module provides functionality for loading Twitter data into the database.
"""

import os
import json
from pathlib import Path

from .. import config
from ..schema import get_db_connection, get_stock_symbols_map, get_sentiment_label
from ..utils.logging_utils import get_logger
from ..utils.path_utils import validate_file_exists, load_json_file

logger = get_logger(__name__)

def load_twitter_data(conn=None, twitter_data_path=None):
    """
    Load Twitter data from JSON file into the database.
    
    Args:
        conn (sqlite3.Connection, optional): Database connection.
            If None, a new connection will be created.
        twitter_data_path (str or Path, optional): Path to the Twitter data JSON file.
            Defaults to the path specified in config.
    
    Returns:
        dict: Summary of loaded data with counts.
    """
    twitter_data_path = Path(twitter_data_path) if twitter_data_path else config.TWITTER_DATA_PATH
    
    try:
        validate_file_exists(twitter_data_path)
    except FileNotFoundError:
        logger.error(f"Twitter data file not found: {twitter_data_path}")
        return {"error": f"Twitter data file not found: {twitter_data_path}", "loaded_count": 0}
    
    logger.info(f"Loading Twitter data from {twitter_data_path}")
    
    # Use provided connection or create a new one
    close_conn = False
    if conn is None:
        conn = get_db_connection().__enter__()
        close_conn = True
    
    cursor = conn.cursor()
    summary = {"total": 0, "linked": 0}
    
    try:
        # Load Twitter data
        twitter_data = load_json_file(twitter_data_path)
        
        # Get existing stock symbols
        stock_map = get_stock_symbols_map(conn)
        
        if not stock_map:
            logger.warning("No stocks found in database. Load stock data first.")
            summary["warning"] = "No stocks found in database. Load stock data first."
        
        # Insert tweets
        for tweet in twitter_data:
            # Extract tweet data
            tweet_id = tweet.get('id_str', '')
            user = tweet.get('user', {})
            user_name = user.get('name', '')
            user_screen_name = user.get('screen_name', '')
            created_at = tweet.get('created_at', '')
            text = tweet.get('text', '')
            
            # Extract sentiment data
            sentiment = tweet.get('sentiment', {})
            sentiment_score = sentiment.get('compound', 0)
            sentiment_label = get_sentiment_label(sentiment_score)
            
            # Insert into tweets table
            cursor.execute('''
            INSERT OR IGNORE INTO tweets 
            (tweet_id, user_name, user_screen_name, datetime, content, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tweet_id, user_name, user_screen_name, created_at, text, sentiment_score, sentiment_label))
            
            # Get the tweet_id (either the one just inserted or the existing one)
            db_tweet_id = cursor.lastrowid
            if not db_tweet_id:
                cursor.execute('''
                SELECT id FROM tweets 
                WHERE tweet_id = ?
                ''', (tweet_id,))
                result = cursor.fetchone()
                if result:
                    db_tweet_id = result[0]
                else:
                    logger.warning(f"Could not retrieve ID for tweet: {tweet_id}")
                    continue
            
            summary["total"] += 1
            
            # Link to relevant stocks
            # Extract stock symbols from tweet text (simplified approach)
            symbols = []
            for symbol in config.TRACKED_SYMBOLS:
                if f"${symbol}" in text or f"#{symbol}" in text or symbol in text:
                    symbols.append(symbol)
            
            for symbol in symbols:
                if symbol in stock_map:
                    stock_id = stock_map[symbol]
                    cursor.execute('''
                    INSERT OR IGNORE INTO stock_tweets 
                    (stock_id, tweet_id, sentiment_score)
                    VALUES (?, ?, ?)
                    ''', (stock_id, db_tweet_id, sentiment_score))
                    summary["linked"] += 1
        
        conn.commit()
        logger.info(f"Loaded {summary['total']} tweets into the database.")
        logger.info(f"Linked {summary['linked']} tweet-stock relationships.")
        return summary
    
    except Exception as e:
        logger.error(f"Error loading Twitter data: {e}")
        conn.rollback()
        return {"error": str(e), "loaded_count": 0}
    
    finally:
        if close_conn:
            conn.close()
