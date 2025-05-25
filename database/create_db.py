import sqlite3
import os
import json
import sys
from datetime import datetime

# add  project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Constants
DB_FILE = os.path.join(project_root, 'database', 'market_sentiment.db')
DATA_DIR = os.path.join(project_root, 'data')
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, 'marketaux_news_sentiment.json')
STOCK_DATA_DR = os.path.join(DATA_DIR, 'stock_data')
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']

# load json file
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    
# Create database and tables
def create_database():
    print(f"Creating database at {DB_FILE}")

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create stock table
    cursor.execute('''
        Create table if not exists stocks(
            id integer primary key autoincrement,
            symbol text not null,
            name text,
            sector text)                                            
                   ''')
    
    # Create stock prices table
    cursor.execute('''
        Create table if not exists stock_prices(
                   id integer primary key autoincrement,
                   stock_id integer not null,
                   date text not null,
                   open real,
                   high real,
                   low real,
                   close real,
                   volume integer,
                   adj_close real,
                   foreign key(stock_id) references stocks(id)
                   unique(stock_id,date)
                   )
               ''')
    
    # Create news table - stores news articles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        date TEXT,
        headline TEXT,
        summary TEXT,
        url TEXT,
        sentiment_score REAL,
        sentiment_label TEXT
    )
''')

    # Stock news table - stores news articles related to stocks
    cursor.execute('''
        create table if not exists stock_news(
                   id integer primary key autoincrement,
                   stock_id integer references stocks(id),
                   news_id integer references news(id),
                   sentiment_score real,
                   unique(stock_id, news_id)
                   )
                   ''')
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

def main():
   

    # Create the database and tables
    create_database()

if __name__ == "__main__":
    main()
   