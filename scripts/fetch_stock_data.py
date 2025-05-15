#!/usr/bin/env python3.11
import json
import os
import sys
import time

# Add the project root directory to the Python path for data_api module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append("/opt/.manus/.sandbox-runtime") # For data_api module

from data_api import ApiClient

# Define parameters
SYMBOLS = ["AAPL", "MSFT", "GOOGL"] # Example stock symbols
DATA_DIR = os.path.join(project_root, "data", "stock_data")
RANGE = "5y" # Fetch 5 years of historical data
INTERVAL = "1d" # Daily interval

client = ApiClient()

def fetch_stock_history(symbol, range_val, interval_val):
    """Fetches historical stock data using the YahooFinance/get_stock_chart API."""
    print(f"Fetching historical stock data for symbol: {symbol}, range: {range_val}, interval: {interval_val}")
    try:
        response = client.call_api(
            "YahooFinance/get_stock_chart", 
            query={
                "symbol": symbol,
                "range": range_val,
                "interval": interval_val,
                "includeAdjustedClose": True
            }
        )
        print(f"Successfully fetched stock data for symbol: {symbol}")
        return response
    except Exception as e:
        print(f"Error fetching stock data for symbol {symbol}: {e}")
        return None

def save_data_to_json(data, symbol, directory):
    """Saves data to a JSON file in the specified directory."""
    os.makedirs(directory, exist_ok=True)
    filename = f"{symbol}_stock_data.json"
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Stock data for {symbol} successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving stock data for {symbol} to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting historical stock data fetch...")
    
    for stock_symbol in SYMBOLS:
        print(f"Processing symbol: {stock_symbol}")
        stock_data_response = fetch_stock_history(symbol=stock_symbol, range_val=RANGE, interval_val=INTERVAL)
        
        if stock_data_response and stock_data_response.get("chart") and stock_data_response["chart"].get("result"):
            save_data_to_json(stock_data_response, stock_symbol, DATA_DIR)
        elif stock_data_response:
            print(f"Fetched data for symbol {stock_symbol}, but it might be empty or in an unexpected format.")
            # Save raw response for inspection if needed
            save_data_to_json(stock_data_response, f"{stock_symbol}_stock_data_raw_unexpected", DATA_DIR)
            print(f"Raw response for {stock_symbol} saved for inspection.")
        else:
            print(f"Failed to fetch stock data for symbol: {stock_symbol}")
        
        # Add a small delay to avoid hitting API rate limits, if any (though not explicitly stated for this internal API)
        time.sleep(1) 
            
    print("Finished fetching historical stock data.")

