import os
import sys
import sqlite3


# add  project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from utils.file_loader import load_json_data

# Constants
DATA_DIR = os.path.join(project_root, 'data')
STOCK_DATA_DR = os.path.join(DATA_DIR, 'stock_data')

conn = sqlite3.connect(os.path.join(project_root, 'database', 'market_sentiment.db'))

def insert_stock_data(conn = conn):
    try:
        print(f"Inserting stock data from {STOCK_DATA_DR}")
        # Connect to SQLite database
        cursor = conn.cursor()

        # Get all stock files in the directory
        for filename in os.listdir(STOCK_DATA_DR):
            if filename.endswith('_stock_data.json'):
                filename = os.path.join(STOCK_DATA_DR, filename)
                stock_data = load_json_data(filename)
                symbol = filename.split('_')[0]
                if not stock_data:
                    print(f"No data found in {filename}")
                    continue
                # Insert stock data into the database
                for date, data in stock_data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO stocks (
                                   symbol, date, open, high, low, close, adj_close, volume)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                   ''',(
                                       symbol,
                                       date,
                                       data.get('Open',0),
                                       data.get('High',0),
                                       data.get('Low',0),
                                       data.get('Close',0),
                                       data.get('Adj Close',0),
                                       data.get('Volume',0)
                                   ))
                print(f"Inserted data for {symbol} from {filename} with {len(stock_data)} records")
        # Commit the changes
            conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        print("Stock data insertion completed.")

# Main function to insert stock data
def main():
    # Connect to SQLite database
    
    
    # Insert stock data
    insert_stock_data()
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
            

