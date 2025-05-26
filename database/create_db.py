import sqlite3
import os
import json
import pandas as pd
from datetime import datetime

# Define paths
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'market_sentiment.db')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NEWS_DATA_PATH = os.path.join(DATA_DIR, 'news_with_sentiment.json')
TWITTER_DATA_PATH = os.path.join(DATA_DIR, 'twitter_with_sentiment.json')
STOCK_DATA_DIR = os.path.join(DATA_DIR, 'stock_data')

def create_database():
    """Create the SQLite database and tables if they don't exist."""
    print(f"Creating database at {DB_PATH}...")
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
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
    print("Database and tables created successfully.")
    return conn

def load_news_data(conn):
    """Load news data from JSON file into the database."""
    if not os.path.exists(NEWS_DATA_PATH):
        print(f"News data file not found at {NEWS_DATA_PATH}")
        return
    
    print(f"Loading news data from {NEWS_DATA_PATH}...")
    
    try:
        with open(NEWS_DATA_PATH, 'r') as f:
            news_data = json.load(f)
        
        cursor = conn.cursor()
        
        # Get existing stock symbols
        cursor.execute("SELECT id, symbol FROM stocks")
        stock_map = {row[1]: row[0] for row in cursor.fetchall()}
        
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
            
            # Determine sentiment label
            if sentiment_score >= 0.05:
                sentiment_label = 'positive'
            elif sentiment_score <= -0.05:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
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
                news_id = cursor.fetchone()[0]
            
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
        
        conn.commit()
        print(f"Loaded {len(news_data)} news articles into the database.")
    
    except Exception as e:
        print(f"Error loading news data: {e}")

def load_twitter_data(conn):
    """Load Twitter data from JSON file into the database."""
    if not os.path.exists(TWITTER_DATA_PATH):
        print(f"Twitter data file not found at {TWITTER_DATA_PATH}")
        return
    
    print(f"Loading Twitter data from {TWITTER_DATA_PATH}...")
    
    try:
        with open(TWITTER_DATA_PATH, 'r') as f:
            twitter_data = json.load(f)
        
        cursor = conn.cursor()
        
        # Get existing stock symbols
        cursor.execute("SELECT id, symbol FROM stocks")
        stock_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Insert tweets
        for tweet in twitter_data:
            # Extract tweet data
            tweet_id = tweet.get('id_str', '')
            user_name = tweet.get('user', {}).get('name', '')
            user_screen_name = tweet.get('user', {}).get('screen_name', '')
            created_at = tweet.get('created_at', '')
            text = tweet.get('text', '')
            
            # Extract sentiment data
            sentiment = tweet.get('sentiment', {})
            sentiment_score = sentiment.get('compound', 0)
            
            # Determine sentiment label
            if sentiment_score >= 0.05:
                sentiment_label = 'positive'
            elif sentiment_score <= -0.05:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
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
                db_tweet_id = cursor.fetchone()[0]
            
            # Link to relevant stocks
            # Extract stock symbols from tweet text (simplified approach)
            # In a real implementation, you might use a more sophisticated method
            symbols = []
            for symbol in ['AAPL', 'MSFT', 'GOOGL']:  # Our tracked symbols
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
        
        conn.commit()
        print(f"Loaded {len(twitter_data)} tweets into the database.")
    
    except Exception as e:
        print(f"Error loading Twitter data: {e}")

def load_stock_data(conn):
    """Load stock data from JSON files into the database."""
    if not os.path.exists(STOCK_DATA_DIR):
        print(f"Stock data directory not found at {STOCK_DATA_DIR}")
        return
    
    print(f"Loading stock data from {STOCK_DATA_DIR}...")
    
    try:
        cursor = conn.cursor()
        
        # Process each stock data file
        for filename in os.listdir(STOCK_DATA_DIR):
            if filename.endswith('_stock_data.json'):
                symbol = filename.split('_')[0]
                file_path = os.path.join(STOCK_DATA_DIR, filename)
                
                with open(file_path, 'r') as f:
                    stock_data = json.load(f)
                
                # Insert stock data
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
                
                print(f"Loaded {len(stock_data)} days of data for {symbol}.")
        
        conn.commit()
        print("Stock data loaded successfully.")
    
    except Exception as e:
        print(f"Error loading stock data: {e}")

def main():
    """Main function to create the database and load all data."""
    # Create database and tables
    conn = create_database()
    
    # Load stock data first (to establish stock IDs)
    load_stock_data(conn)
    
    # Load news and Twitter data
    load_news_data(conn)
    load_twitter_data(conn)
    
    # Close connection
    conn.close()
    
    print("Database creation and data loading complete.")

if __name__ == "__main__":
    main()
