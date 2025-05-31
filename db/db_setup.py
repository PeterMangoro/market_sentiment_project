"""
Database configuration and setup module for the Market Sentiment Analysis project.
This module handles database connection and table creation.
"""
import sqlite3
import os

def get_db_path():
    """Return the path to the SQLite database file."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'market_sentiment.db')

def create_connection(db_path=None):
    """Create a database connection to the SQLite database."""
    if db_path is None:
        db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables(conn):
    """Create the necessary tables in the database if they don't exist."""
    try:
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
        return True
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        return False

def setup_database():
    """Set up the database and create tables."""
    db_path = get_db_path()
    print(f"Setting up database at {db_path}...")
    
    conn = create_connection(db_path)
    if conn is None:
        return None
    
    if create_tables(conn):
        print("Database and tables created successfully.")
        return conn
    else:
        conn.close()
        return None
