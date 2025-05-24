import os
import sys
import json
import requests
from datetime import datetime,timedelta

# Add project root to path to import api_keys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

try:
    from api_keys import MARKETAUX_API_KEY
except ImportError:
    print("Please create a file named 'api_keys.py' in the root directory with your MarketAux API key.")
    sys.exit(1)

# Constants
API_BASE_URL = "https://api.marketaux.com/v1/news/all"
SYMBOLS = ["AAPL", "MSFT", "GOOGL"] #Stock symbols to fetch news for
DATA_DIR =  os.path.join(project_root,"data")
OUTPUT_FILE = os.path.join(DATA_DIR, "marketaux_news_data.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Function to fetch news from MarketAux API
def fetch_marketaux_news(symbols,days_back=30,language="en"):

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    # Format dates for API request
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")

    # Prepare API request parameters
    params = {
        "symbols": ",".join(symbols),
        # "start_date": start_date_str,
        # "end_date": end_date_str,
        "language": language,
        "api_token": MARKETAUX_API_KEY,
        "published_after": start_date_str,
        "limit": 100,  # Limit the number of results
    }

    # Make the API request
    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        news_data = response.json()
        if 'data' in news_data:            
            print(f"Fetched {len(news_data['data'])} articles.")
            return news_data['data']
        else:
            print("No news data found in the response.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news data: {e}")
        return []
    

# Function to save news data to a JSON file
def save_news_to_file(news_data,output_file):
    try:
        with open(output_file,"w") as f:
            json.dump(news_data,f,indent=4)
            print(f"News data saved to {output_file}")
    except Exception as e:
        print(f"Error saving news data to file: {e}")

# Main function
def main():
    # Fetch news data
    news_articles = fetch_marketaux_news(SYMBOLS)
    if news_articles:
        # Save news data to file
        save_news_to_file(news_articles, OUTPUT_FILE)
        
    else:
        print("No news articles fetched.")
        return
    
if __name__ == "__main__":
    main()

    
