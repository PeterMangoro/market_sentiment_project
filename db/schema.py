"""
Database schema definition and creation functionality.

This module defines the database schema (tables, relationships) and
provides functions to create and initialize the database.
"""

import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path

from . import config
from .utils.logging_utils import get_logger

logger = get_logger(__name__)

@contextmanager
def get_db_connection(db_path=None):
    """
    Context manager for database connections.
    
    Args:
        db_path (str or Path, optional): Path to the database file.
            Defaults to the path specified in config.
    
    Yields:
        sqlite3.Connection: Database connection object.
    """
    db_path = Path(db_path) if db_path else config.DB_PATH
    logger.debug(f"Connecting to database at {db_path}")
    
    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

def create_database(db_path=None):
    """
    Create the SQLite database and tables if they don't exist.
    
    Args:
        db_path (str or Path, optional): Path to the database file.
            Defaults to the path specified in config.
    
    Returns:
        bool: True if database was created successfully, False otherwise.
    """
    db_path = Path(db_path) if db_path else config.DB_PATH
    logger.info(f"Creating database at {db_path}")
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Create stocks table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adj_close REAL,
                volume INTEGER,
                UNIQUE(symbol, date)
            )
            ''')
            
            # Create news table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                datetime TEXT,
                headline TEXT,
                summary TEXT,
                url TEXT,
                sentiment_score REAL,
                sentiment_label TEXT
            )
            ''')
            
            # Create tweets table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE,
                user_name TEXT,
                user_screen_name TEXT,
                datetime TEXT,
                content TEXT,
                sentiment_score REAL,
                sentiment_label TEXT
            )
            ''')
            
            # Create stock_news linking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER,
                news_id INTEGER,
                sentiment_score REAL,
                FOREIGN KEY (stock_id) REFERENCES stocks (id),
                FOREIGN KEY (news_id) REFERENCES news (id)
            )
            ''')
            
            # Create stock_tweets linking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER,
                tweet_id INTEGER,
                sentiment_score REAL,
                FOREIGN KEY (stock_id) REFERENCES stocks (id),
                FOREIGN KEY (tweet_id) REFERENCES tweets (id)
            )
            ''')
            
            conn.commit()
            logger.info("Database and tables created successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error creating database: {e}")
        return False

def get_stock_symbols_map(conn):
    """
    Get a mapping of stock symbols to their IDs in the database.
    
    Args:
        conn (sqlite3.Connection): Database connection.
    
    Returns:
        dict: Mapping of stock symbols to their IDs.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol FROM stocks")
    return {row['symbol']: row['id'] for row in cursor.fetchall()}

def get_sentiment_label(score):
    """
    Determine sentiment label based on score.
    
    Args:
        score (float): Sentiment score.
    
    Returns:
        str: Sentiment label ('positive', 'negative', or 'neutral').
    """
    if score >= config.POSITIVE_THRESHOLD:
        return 'positive'
    elif score <= config.NEGATIVE_THRESHOLD:
        return 'negative'
    else:
        return 'neutral'
