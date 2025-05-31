"""
News data loader module.

This module provides functionality for loading news article data into the database.
"""

import os
import json
from pathlib import Path

from .. import config
from ..schema import get_db_connection, get_stock_symbols_map, get_sentiment_label
from ..utils.logging_utils import get_logger
from ..utils.path_utils import validate_file_exists, load_json_file

logger = get_logger(__name__)

def load_news_data(conn=None, news_data_path=None):
    """
    Load news data from JSON file into the database.
    
    Args:
        conn (sqlite3.Connection, optional): Database connection.
            If None, a new connection will be created.
        news_data_path (str or Path, optional): Path to the news data JSON file.
            Defaults to the path specified in config.
    
    Returns:
        dict: Summary of loaded data with counts.
    """
    news_data_path = Path(news_data_path) if news_data_path else config.NEWS_DATA_PATH
    
    try:
        validate_file_exists(news_data_path)
    except FileNotFoundError:
        logger.error(f"News data file not found: {news_data_path}")
        return {"error": f"News data file not found: {news_data_path}", "loaded_count": 0}
    
    logger.info(f"Loading news data from {news_data_path}")
    
    # Use provided connection or create a new one
    close_conn = False
    if conn is None:
        conn = get_db_connection().__enter__()
        close_conn = True
    
    cursor = conn.cursor()
    summary = {"total": 0, "linked": 0}
    
    try:
        # Load news data
        news_data = load_json_file(news_data_path)
        
        # Get existing stock symbols
        stock_map = get_stock_symbols_map(conn)
        
        if not stock_map:
            logger.warning("No stocks found in database. Load stock data first.")
            summary["warning"] = "No stocks found in database. Load stock data first."
        
        # Insert news articles
        for article in news_data:
            # Extract article data
            source = article.get('source', 'Unknown')
            published_at = article.get('published_at', '')
            title = article.get('title', '')
            description = article.get('description', '')
            url = article.get('url', '')
            
            # Extract sentiment data
            sentiment = article.get('sentiment', {})
            sentiment_score = sentiment.get('compound', 0)
            sentiment_label = get_sentiment_label(sentiment_score)
            
            # Insert into news table
            cursor.execute('''
            INSERT OR IGNORE INTO news 
            (source, datetime, headline, summary, url, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (source, published_at, title, description, url, sentiment_score, sentiment_label))
            
            # Get the news_id (either the one just inserted or the existing one)
            news_id = cursor.lastrowid
            if not news_id:
                cursor.execute('''
                SELECT id FROM news 
                WHERE headline = ? AND datetime = ?
                ''', (title, published_at))
                result = cursor.fetchone()
                if result:
                    news_id = result[0]
                else:
                    logger.warning(f"Could not retrieve ID for news article: {title}")
                    continue
            
            summary["total"] += 1
            
            # Link to relevant stocks
            symbols = article.get('symbols', [])
            for symbol in symbols:
                if symbol in stock_map:
                    stock_id = stock_map[symbol]
                    cursor.execute('''
                    INSERT OR IGNORE INTO stock_news 
                    (stock_id, news_id, sentiment_score)
                    VALUES (?, ?, ?)
                    ''', (stock_id, news_id, sentiment_score))
                    summary["linked"] += 1
        
        conn.commit()
        logger.info(f"Loaded {summary['total']} news articles into the database.")
        logger.info(f"Linked {summary['linked']} news-stock relationships.")
        return summary
    
    except Exception as e:
        logger.error(f"Error loading news data: {e}")
        conn.rollback()
        return {"error": str(e), "loaded_count": 0}
    
    finally:
        if close_conn:
            conn.close()
