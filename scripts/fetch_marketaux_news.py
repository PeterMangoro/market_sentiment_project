#!/usr/bin/env python3.11
import requests
import json
import os
import sys

# Add the project root directory to the Python path to find api_keys.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from api_keys import MARKETAUX_API_KEY
except ImportError:
    print("Error: Could not import MARKETAUX_API_KEY from api_keys.py. Make sure api_keys.py exists in the project root directory (/home/ubuntu/market_sentiment_project/) and MARKETAUX_API_KEY is defined.")
    sys.exit(1)

BASE_URL = "https://api.marketaux.com/v1/news/all"

# Define parameters
SYMBOLS = ["AAPL", "MSFT", "GOOGL"] # Example stock symbols
PARAMS = {
    "api_token": MARKETAUX_API_KEY,
    "symbols": ",".join(SYMBOLS),
    "language": "en",
    "limit": 5 # Start with a small limit for testing, free tier usually has daily limits. Max is 50 for some plans.
}

DATA_DIR = os.path.join(project_root, "data")
OUTPUT_FILENAME = "marketaux_news_data.json"

def fetch_market_news(params):
    """Fetches market news from Marketaux API."""
    print(f"Fetching news from Marketaux with params: {params.get('symbols')}, limit: {params.get('limit')}")
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        print("Successfully fetched data from Marketaux.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Marketaux: {e}")
        if response is not None:
            print(f"Response content: {response.text}")
        return None

def save_data_to_json(data, filename):
    """Saves data to a JSON file in the data directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving data to {filepath}: {e}")

if __name__ == "__main__":
    print(f"Starting news fetch for symbols: {', '.join(SYMBOLS)}")
    news_data = fetch_market_news(PARAMS)
    
    if news_data:
        if news_data.get("data"):
            save_data_to_json(news_data, OUTPUT_FILENAME)
            print(f"Fetched {len(news_data['data'])} articles.")
        else:
            print("Fetched data, but it might be empty or the 'data' key is missing.")
            # Save raw response for inspection if 'data' key is missing but response is not None
            save_data_to_json(news_data, "marketaux_news_data_raw_unexpected.json") 
            print("Raw response saved for inspection.")
    else:
        print("Failed to fetch news data or an error occurred during fetch.")

