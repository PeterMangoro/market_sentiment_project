import os
import sys
import json
import time
from datetime import datetime,timedelta

# Add project root to path to import api_keys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    import yfinance as yf
except ImportError:
    print("Please install yfinance using 'pip install yfinance'")
    sys.exit(1)

# Constants
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]  # Stock symbols to fetch data for
DATA_DIR = os.path.join(project_root,"data","stock_data")
DAYS_BACK = 365 # 1 year of historical data

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Function to fetch stock data using yfinance
def fetch_stock_data(symbol,period="1y",interval="1d"):
    
    try:
        #Create a ticker object for each symbol
        ticker = yf.Ticker(symbol)

        # Fetch historical data
        data = ticker.history(period=period, interval=interval)

        # Convert to format similar to Yahoo Finance
        timestamps = data.index.astype('int64') // 10**9

        result = {
            "chart": {
                "result":[{
                    "meta":{
                        "symbol": symbol,
                        "currency": "USD",
                        "exchangeName": "NMS",
                        "instrumentType": "EQUITY",
                        "timezone": "America/New_York",
                    },
                    "timestamp": timestamps.tolist(),
                    "indicators": {
                        "quote": [{
                            "open": data['Open'].tolist(),
                            "close": data['Close'].tolist(),
                            "high": data['High'].tolist(),
                            "low": data['Low'].tolist(),
                            "volume": data['Volume'].tolist()
                        }],
                        "adjclose": [{
                            "adjclose": data['Close'].tolist()
                        }]
                    }
                }],
                "error": None
            }
        }

        return result
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    
# Function to save stock data to a JSON file
def save_stock_data_to_file(stock_data, symbol, output_dir):
    try:
        output_file = os.path.join(output_dir, f"{symbol}_stock_data.json")
        with open(output_file, "w") as f:
            json.dump(stock_data, f, indent=4)
            print(f"Stock data for {symbol} saved to {output_file}")
            return True
    except Exception as e:
        print(f"Error saving stock data for {symbol} to file: {e}")
        return False
    
# Main function
def main():
    print(f"Fetching stock data for symbols: {', '.join(SYMBOLS)}")

    success_count = 0
    for symbol in SYMBOLS:
        # Fetch stock data
        stock_data = fetch_stock_data(symbol)

        if stock_data:
            # Save stock data to file
            if save_stock_data_to_file(stock_data, symbol, DATA_DIR):
                success_count += 1

        time.sleep(1) # Sleep to avoid hitting API rate limits
    print(f"Successfully fetched and saved data for {success_count} out of {len(SYMBOLS)} symbols.")

if __name__ == "__main__":
    main()

