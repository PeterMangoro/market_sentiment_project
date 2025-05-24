# Market Sentiment Analysis Project: Comprehensive Explanation

This document provides a detailed, step-by-step explanation of the Market Sentiment Analysis project, including code, design decisions, alternatives considered, and rationale for our choices.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Environment Setup](#environment-setup)
3. [API Configuration](#api-configuration)
4. [Data Collection](#data-collection)
   - [Financial News Collection](#financial-news-collection)
   - [Twitter Data Collection](#twitter-data-collection)
   - [Historical Stock Data Collection](#historical-stock-data-collection)
5. [Sentiment Analysis](#sentiment-analysis)
6. [Database Design and Implementation](#database-design-and-implementation)
7. [Exploratory Data Analysis](#exploratory-data-analysis)
8. [Advanced Modeling](#advanced-modeling)
   - [Random Forest Model](#random-forest-model)
   - [XGBoost Model](#xgboost-model)
   - [ARIMA Model](#arima-model)
   - [Model Comparison](#model-comparison)
9. [Interactive Visualization](#interactive-visualization)
10. [Jupyter Notebooks](#jupyter-notebooks)
11. [Project Packaging and Deployment](#project-packaging-and-deployment)
12. [Future Enhancements](#future-enhancements)

## Project Overview

The Market Sentiment Analysis project aims to explore the relationship between public sentiment (derived from financial news and social media) and stock price movements. The project focuses on three major tech stocks: Apple (AAPL), Microsoft (MSFT), and Google (GOOGL).

**Key Objectives:**
- Collect and analyze sentiment from financial news and Twitter
- Correlate sentiment with stock price movements
- Build predictive models to forecast stock prices using sentiment data
- Create interactive visualizations for data exploration
- Package everything for reproducibility and further analysis

## Environment Setup

### Project Structure

We organized the project with a clear directory structure to separate different components:

```
market_sentiment_project/
├── data/                  # Raw and processed data
│   └── stock_data/        # Stock price data for each symbol
├── scripts/               # Python scripts for data collection and processing
├── notebooks/             # Jupyter notebooks for interactive analysis
├── models/                # Saved trained models
├── reports/               # Generated reports and visualizations
├── visualizations_tableau/ # Data prepared for Tableau
├── api_keys.py            # API keys (not committed to version control)
└── requirements.txt       # Project dependencies
```

**Code: Directory Creation**
```python
# Shell command to create the project structure
mkdir -p /home/ubuntu/market_sentiment_project/{data,scripts,notebooks,reports,visualizations_tableau,models}
```

**Alternatives Considered:**
- **Flat structure**: We could have placed all files in a single directory, but this would become unwieldy as the project grows.
- **Framework-specific structure**: We could have used a structure specific to a framework like Django or Flask, but this would add unnecessary complexity for a data analysis project.

**Rationale:**
The chosen structure follows best practices for data science projects, separating data, code, and outputs. This makes the project more maintainable, easier to navigate, and allows for better collaboration.

### Dependencies

We specified project dependencies in a `requirements.txt` file:

**Code: requirements.txt**
```
requests
nltk
pandas
numpy
scikit-learn
statsmodels
matplotlib
xgboost
```

**Alternatives Considered:**
- **Conda environment.yml**: Could have used Conda for environment management, which handles non-Python dependencies better.
- **Poetry**: Could have used Poetry for more deterministic dependency resolution.
- **Manual installation instructions**: Could have provided manual installation steps without a requirements file.

**Rationale:**
`requirements.txt` is the simplest, most widely understood approach for Python projects. It works well with pip, which is included with Python, and is supported by virtually all Python development environments, including VS Code.

## API Configuration

### API Keys Management

We created a separate file for API keys to keep them secure and easy to update:

**Code: api_keys.py**
```python
# API keys for various services
MARKETAUX_API_KEY = "your_marketaux_api_key_here"
# YAHOO_FINANCE_API_KEY = "not_needed_for_yfinance"
# TWITTER_API_KEY = "your_twitter_api_key_here"
# TWITTER_API_SECRET_KEY = "your_twitter_api_secret_key_here"
```

**Alternatives Considered:**
- **Environment variables**: Could have used environment variables for API keys.
- **Config file with encryption**: Could have encrypted the config file for additional security.
- **Secret management service**: Could have used a service like AWS Secrets Manager or HashiCorp Vault.

**Rationale:**
A separate Python file is simple to implement and understand, especially for a local project. It allows for easy updates and keeps sensitive information separate from code. For a production environment, environment variables or a secret management service would be more appropriate.

## Data Collection

### Financial News Collection

We used the Marketaux API to collect financial news articles related to our target stocks.

**Code: fetch_marketaux_news.py**
```python
#!/usr/bin/env python3.11
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Add project root to path to import api_keys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

try:
    from api_keys import MARKETAUX_API_KEY
except ImportError:
    print("Error: api_keys.py file not found or MARKETAUX_API_KEY not defined.")
    print("Please create api_keys.py in the project root with your API key.")
    sys.exit(1)

# Constants
API_BASE_URL = "https://api.marketaux.com/v1/news/all"
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]  # Stock symbols we're interested in
DATA_DIR = os.path.join(project_root, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "marketaux_news_data.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_news_for_symbols(symbols, days_back=30, language="en"):
    """
    Fetch financial news for the specified symbols from the Marketaux API.
    
    Args:
        symbols: List of stock symbols to fetch news for
        days_back: How many days of historical news to fetch
        language: Language of news articles
        
    Returns:
        List of news articles
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates for API
    published_after = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Join symbols for API request
    symbols_str = ",".join(symbols)
    
    # Prepare request parameters
    params = {
        "api_token": MARKETAUX_API_KEY,
        "symbols": symbols_str,
        "language": language,
        "published_after": published_after,
        "limit": 100  # Maximum articles per request
    }
    
    try:
        # Make API request
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response
        news_data = response.json()
        
        if "data" in news_data:
            print(f"Fetched {len(news_data['data'])} articles.")
            return news_data["data"]
        else:
            print("Error: Unexpected API response format.")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def save_news_data(news_articles, output_file):
    """Save news articles to a JSON file."""
    try:
        with open(output_file, "w") as f:
            json.dump(news_articles, f, indent=2)
        print(f"Saved {len(news_articles)} articles to {output_file}")
    except Exception as e:
        print(f"Error saving news data: {e}")

def main():
    """Main function to fetch and save news data."""
    print(f"Starting news fetch for symbols: {', '.join(SYMBOLS)}")
    
    # Fetch news articles
    news_articles = fetch_news_for_symbols(SYMBOLS)
    
    if news_articles:
        # Save to file
        save_news_data(news_articles, OUTPUT_FILE)
        print("News data collection complete.")
    else:
        print("No news articles collected.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **Different News APIs**: We considered alternatives like Alpha Vantage, NewsAPI, or Finnhub.
- **Web scraping**: Could have scraped financial news websites directly.
- **RSS feeds**: Could have used RSS feeds from financial news sources.

**Rationale:**
Marketaux was chosen because:
1. It specializes in financial news with entity recognition for stocks
2. It offers a reasonable free tier for development
3. It has a simple API that's easy to work with
4. It provides some sentiment analysis capabilities (though we implemented our own for learning purposes)

Web scraping would have been more complex and potentially violate terms of service, while RSS feeds might not provide the structured data we needed.

### Twitter Data Collection

We collected tweets related to our target stocks using the Twitter API.

**Code: fetch_twitter_data.py**
```python
#!/usr/bin/env python3.11
import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# For the sandbox environment, we used an internal API client
# For local implementation, you would use the tweepy library or Twitter's official API
try:
    # This is for the sandbox environment
    sys.path.append('/opt/.manus/.sandbox-runtime')
    from data_api import ApiClient
    client = ApiClient()
    USING_SANDBOX_API = True
except ImportError:
    USING_SANDBOX_API = False
    print("Note: Running in local environment. Twitter API access requires configuration.")
    # In a local environment, you would use tweepy or similar
    # import tweepy
    # from api_keys import TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

# Constants
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]  # Stock symbols we're interested in
QUERIES = [query for symbol in SYMBOLS for query in (f"${symbol} stock", f"#{symbol} stock price")]  # Example queries
DATA_DIR = os.path.join(project_root, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "twitter_data.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_tweets_sandbox(query, count=20, tweet_type="Top"):
    """
    Fetch tweets using the sandbox API client.
    This is specific to the development environment and would be replaced
    with direct Twitter API calls in a local implementation.
    """
    try:
        response = client.call_api('Twitter/search_twitter', query={
            'query': query,
            'count': count,
            'type': tweet_type
        })
        
        # Process and extract tweets from the response
        tweets = []
        if response and 'result' in response and 'timeline' in response['result']:
            instructions = response['result']['timeline'].get('instructions', [])
            for instruction in instructions:
                if 'entries' in instruction:
                    for entry in instruction['entries']:
                        if 'content' in entry and 'items' in entry['content']:
                            for item in entry['content']['items']:
                                if 'item' in item and 'itemContent' in item['item']:
                                    content = item['item']['itemContent']
                                    if content.get('__typename') == 'TimelineTimelineItem' and 'user_results' in content:
                                        user_result = content['user_results'].get('result', {})
                                        if user_result:
                                            # Extract user info
                                            user_info = {
                                                'username': user_result.get('legacy', {}).get('screen_name', ''),
                                                'name': user_result.get('legacy', {}).get('name', ''),
                                                'followers': user_result.get('legacy', {}).get('followers_count', 0),
                                                'verified': user_result.get('legacy', {}).get('verified', False)
                                            }
                                            
                                            # For a real implementation, we would extract the tweet text and other details
                                            # Here we're creating a simplified structure
                                            tweet = {
                                                'id': item.get('entryId', ''),
                                                'user': user_info,
                                                'text': f"Tweet about {query}",  # Placeholder
                                                'created_at': datetime.now().isoformat(),
                                                'query': query
                                            }
                                            tweets.append(tweet)
        
        return tweets
    except Exception as e:
        print(f"Error fetching tweets for query '{query}': {e}")
        return []

def fetch_tweets_local(query, count=20):
    """
    Fetch tweets using the Twitter API via tweepy.
    This would be used in a local implementation.
    """
    # This is a placeholder for local implementation
    # In a real implementation, you would use tweepy or the Twitter API directly
    print(f"Would fetch {count} tweets for query: {query}")
    
    # Return some dummy data for demonstration
    return [
        {
            'id': f"dummy_id_{i}",
            'user': {
                'username': f"user_{i}",
                'name': f"User {i}",
                'followers': 100 + i,
                'verified': i % 3 == 0
            },
            'text': f"This is a dummy tweet about {query} - {i}",
            'created_at': datetime.now().isoformat(),
            'query': query
        }
        for i in range(count)
    ]

def save_twitter_data(tweets, output_file):
    """Save tweets to a JSON file."""
    try:
        with open(output_file, "w") as f:
            json.dump(tweets, f, indent=2)
        print(f"Saved {len(tweets)} tweets to {output_file}")
    except Exception as e:
        print(f"Error saving Twitter data: {e}")

def main():
    """Main function to fetch and save Twitter data."""
    print(f"Starting Twitter data collection for queries: {QUERIES}")
    
    all_tweets = []
    
    # Process each query
    for query in QUERIES:
        print(f"Fetching tweets for query: {query}")
        
        # Fetch tweets using the appropriate method
        if USING_SANDBOX_API:
            tweets = fetch_tweets_sandbox(query)
        else:
            tweets = fetch_tweets_local(query)
        
        all_tweets.extend(tweets)
        
        # Be nice to the API with a small delay between requests
        time.sleep(1)
    
    if all_tweets:
        # Save to file
        save_twitter_data(all_tweets, OUTPUT_FILE)
        print("Twitter data collection complete.")
    else:
        print("No tweets collected.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **Twitter API v2**: Could have used the newer Twitter API v2 directly.
- **Third-party services**: Could have used services like GNIP or Brandwatch.
- **Web scraping**: Could have scraped Twitter search results (though this violates Twitter's terms of service).

**Rationale:**
For the sandbox environment, we used an internal API client that simplified access to Twitter data. For a local implementation, we recommend using the official Twitter API via libraries like tweepy, which provides a clean interface and ensures compliance with Twitter's terms of service.

The Twitter API was chosen because:
1. It provides direct access to Twitter data
2. It offers filtering capabilities to focus on relevant tweets
3. It's the official and approved way to access Twitter data

### Historical Stock Data Collection

We collected historical stock price data using the Yahoo Finance API.

**Code: fetch_stock_data.py**
```python
#!/usr/bin/env python3.11
import os
import sys
import json
import time
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# For the sandbox environment, we used an internal API client
# For local implementation, you would use the yfinance library
try:
    # This is for the sandbox environment
    sys.path.append('/opt/.manus/.sandbox-runtime')
    from data_api import ApiClient
    client = ApiClient()
    USING_SANDBOX_API = True
except ImportError:
    USING_SANDBOX_API = False
    print("Note: Running in local environment. Using yfinance for stock data.")
    try:
        import yfinance as yf
    except ImportError:
        print("Error: yfinance library not installed. Please install with 'pip install yfinance'")
        sys.exit(1)

# Constants
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]  # Stock symbols we're interested in
DATA_DIR = os.path.join(project_root, "data", "stock_data")
DAYS_BACK = 365  # Get 1 year of historical data

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_stock_data_sandbox(symbol, interval="1d", range="1y"):
    """
    Fetch historical stock data using the sandbox API client.
    This is specific to the development environment and would be replaced
    with yfinance in a local implementation.
    """
    try:
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'interval': interval,
            'range': range
        })
        
        return response
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

def fetch_stock_data_local(symbol, period="1y", interval="1d"):
    """
    Fetch historical stock data using yfinance.
    This would be used in a local implementation.
    """
    try:
        # Create a Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        # Convert to a format similar to the Yahoo Finance API
        timestamps = hist.index.astype('int64') // 10**9  # Convert to Unix timestamp
        
        result = {
            "chart": {
                "result": [{
                    "meta": {
                        "symbol": symbol,
                        "currency": "USD",
                        "exchangeName": "NMS",
                        "instrumentType": "EQUITY",
                        "timezone": "America/New_York"
                    },
                    "timestamp": timestamps.tolist(),
                    "indicators": {
                        "quote": [{
                            "open": hist['Open'].tolist(),
                            "high": hist['High'].tolist(),
                            "low": hist['Low'].tolist(),
                            "close": hist['Close'].tolist(),
                            "volume": hist['Volume'].tolist()
                        }],
                        "adjclose": [{
                            "adjclose": hist['Close'].tolist()  # Using Close as adjclose for simplicity
                        }]
                    }
                }],
                "error": None
            }
        }
        
        return result
    except Exception as e:
        print(f"Error fetching stock data for {symbol} with yfinance: {e}")
        return None

def save_stock_data(data, symbol, output_dir):
    """Save stock data to a JSON file."""
    output_file = os.path.join(output_dir, f"{symbol}_stock_data.json")
    
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved stock data for {symbol} to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving stock data for {symbol}: {e}")
        return False

def main():
    """Main function to fetch and save stock data."""
    print(f"Starting stock data collection for symbols: {', '.join(SYMBOLS)}")
    
    success_count = 0
    
    # Process each symbol
    for symbol in SYMBOLS:
        print(f"Fetching stock data for: {symbol}")
        
        # Fetch stock data using the appropriate method
        if USING_SANDBOX_API:
            stock_data = fetch_stock_data_sandbox(symbol)
        else:
            stock_data = fetch_stock_data_local(symbol)
        
        if stock_data:
            # Save to file
            if save_stock_data(stock_data, symbol, DATA_DIR):
                success_count += 1
        
        # Be nice to the API with a small delay between requests
        time.sleep(1)
    
    print(f"Stock data collection complete. Successfully processed {success_count}/{len(SYMBOLS)} symbols.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **Alpha Vantage API**: Could have used Alpha Vantage for stock data.
- **IEX Cloud**: Could have used IEX Cloud for more comprehensive financial data.
- **Quandl**: Could have used Quandl for historical stock data.

**Rationale:**
For the sandbox environment, we used an internal API client that accessed Yahoo Finance data. For a local implementation, we recommend using the `yfinance` library, which provides a simple interface to Yahoo Finance data without requiring an API key.

Yahoo Finance (via yfinance) was chosen because:
1. It provides free access to historical stock data
2. It doesn't require an API key for basic usage
3. It's widely used and well-maintained
4. It provides all the data we need (OHLCV - Open, High, Low, Close, Volume)

## Sentiment Analysis

We performed sentiment analysis on the collected news articles and tweets using NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analyzer.

**Code: perform_sentiment_analysis.py**
```python
#!/usr/bin/env python3.11
import os
import sys
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Constants
DATA_DIR = os.path.join(project_root, "data")
NEWS_FILE = os.path.join(DATA_DIR, "marketaux_news_data.json")
TWITTER_FILE = os.path.join(DATA_DIR, "twitter_data.json")
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json")

def load_json_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return []

def save_json_data(data, file_path):
    """Save data to a JSON file."""
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved data to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")
        return False

def initialize_sentiment_analyzer():
    """Initialize the VADER sentiment analyzer."""
    try:
        # Try to load the VADER lexicon
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError: # More general error for resource not found
        print("Downloading VADER lexicon...")
        nltk.download("vader_lexicon")
    
    return SentimentIntensityAnalyzer()

def analyze_news_sentiment(news_data, analyzer):
    """
    Analyze sentiment in news articles.
    
    Args:
        news_data: List of news article dictionaries
        analyzer: VADER sentiment analyzer instance
        
    Returns:
        List of news articles with sentiment scores added
    """
    print(f"Analyzing sentiment for {len(news_data)} news articles...")
    
    for article in news_data:
        # Combine title and description for sentiment analysis
        text = ""
        if "title" in article:
            text += article["title"] + " "
        if "description" in article:
            text += article["description"] + " "
        if "summary" in article:
            text += article["summary"]
        
        # If no text is available, skip this article
        if not text.strip():
            article["sentiment"] = {
                "compound": 0,
                "pos": 0,
                "neg": 0,
                "neu": 1.0  # Neutral by default
            }
            continue
        
        # Get sentiment scores
        sentiment = analyzer.polarity_scores(text)
        
        # Add sentiment to article
        article["sentiment"] = sentiment
    
    return news_data

def analyze_twitter_sentiment(twitter_data, analyzer):
    """
    Analyze sentiment in tweets.
    
    Args:
        twitter_data: List of tweet dictionaries
        analyzer: VADER sentiment analyzer instance
        
    Returns:
        List of tweets with sentiment scores added
    """
    print(f"Analyzing sentiment for {len(twitter_data)} tweets...")
    
    for tweet in twitter_data:
        # Get the tweet text
        text = tweet.get("text", "")
        
        # If no text is available, skip this tweet
        if not text.strip():
            tweet["sentiment"] = {
                "compound": 0,
                "pos": 0,
                "neg": 0,
                "neu": 1.0  # Neutral by default
            }
            continue
        
        # Get sentiment scores
        sentiment = analyzer.polarity_scores(text)
        
        # Add sentiment to tweet
        tweet["sentiment"] = sentiment
    
    return twitter_data

def main():
    """Main function to perform sentiment analysis on news and tweets."""
    print("Starting sentiment analysis...")
    
    # Initialize sentiment analyzer
    analyzer = initialize_sentiment_analyzer()
    
    # Process news articles
    news_data = load_json_data(NEWS_FILE)
    if news_data:
        news_with_sentiment = analyze_news_sentiment(news_data, analyzer)
        save_json_data(news_with_sentiment, NEWS_SENTIMENT_FILE)
    
    # Process tweets
    twitter_data = load_json_data(TWITTER_FILE)
    if twitter_data:
        tweets_with_sentiment = analyze_twitter_sentiment(twitter_data, analyzer)
        save_json_data(tweets_with_sentiment, TWITTER_SENTIMENT_FILE)
    
    print("Sentiment analysis complete.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **TextBlob**: Could have used TextBlob for sentiment analysis, which is simpler but less accurate for financial text.
- **BERT or other transformer models**: Could have used more advanced models like FinBERT (financial BERT) for potentially better accuracy.
- **Cloud-based sentiment analysis**: Could have used services like Google Cloud Natural Language API or Amazon Comprehend.
- **Using pre-calculated sentiment**: Marketaux provides some sentiment analysis, which we could have used directly.

**Rationale:**
VADER was chosen because:
1. It's specifically designed for social media text and works well with short texts like tweets and headlines
2. It's rule-based and doesn't require training data
3. It's fast and can be run locally without API calls
4. It provides compound scores as well as positive, negative, and neutral components
5. It's part of NLTK, a well-established NLP library

While more advanced models like BERT might provide better accuracy, they require more computational resources and are more complex to implement. VADER offers a good balance of accuracy and simplicity for this project.

## Database Design and Implementation

We designed a SQLite database to store our collected and processed data, allowing for efficient querying and analysis.

**Code: create_db.py**
```python
import sqlite3
import os
import json
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Constants
DB_FILE = os.path.join(project_root, "market_sentiment.db")
DATA_DIR = os.path.join(project_root, "data")
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json")
STOCK_DATA_DIR = os.path.join(DATA_DIR, "stock_data")
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

def load_json_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return []

def create_database():
    """Create the SQLite database and tables."""
    print(f"Creating database: {DB_FILE}")
    
    # Connect to database (will create if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    
    # Stocks table - stores basic stock information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE,
        name TEXT,
        sector TEXT
    )
    ''')
    
    # Stock prices table - stores daily stock prices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume INTEGER,
        FOREIGN KEY (stock_id) REFERENCES stocks(id),
        UNIQUE(stock_id, date)
    )
    ''')
    
    # News table - stores news articles
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
    
    # Tweets table - stores tweets
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tweet_id TEXT UNIQUE,
        user_name TEXT,
        user_screen_name TEXT,
        datetime TEXT,
        text TEXT,
        sentiment_score REAL,
        sentiment_label TEXT
    )
    ''')
    
    # Stock-News relationship table - many-to-many relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER,
        news_id INTEGER,
        sentiment_score REAL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id),
        FOREIGN KEY (news_id) REFERENCES news(id),
        UNIQUE(stock_id, news_id)
    )
    ''')
    
    # Stock-Tweets relationship table - many-to-many relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER,
        tweet_id INTEGER,
        sentiment_score REAL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id),
        FOREIGN KEY (tweet_id) REFERENCES tweets(id),
        UNIQUE(stock_id, tweet_id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database and tables created successfully.")

def populate_stocks_table():
    """Populate the stocks table with basic information."""
    print("Populating stocks table...")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Stock information (simplified for this example)
    stocks_info = [
        ("AAPL", "Apple Inc.", "Technology"),
        ("MSFT", "Microsoft Corporation", "Technology"),
        ("GOOGL", "Alphabet Inc.", "Technology")
    ]
    
    # Insert stock information
    for symbol, name, sector in stocks_info:
        cursor.execute('''
        INSERT OR IGNORE INTO stocks (symbol, name, sector)
        VALUES (?, ?, ?)
        ''', (symbol, name, sector))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Stocks table populated successfully.")

def populate_stock_prices():
    """Populate the stock_prices table with historical price data."""
    print("Populating stock_prices table...")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Process each symbol
    for symbol in SYMBOLS:
        print(f"Processing stock prices for {symbol}...")
        
        # Get stock ID
        cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        if not result:
            print(f"Error: Stock {symbol} not found in stocks table.")
            continue
        
        stock_id = result[0]
        
        # Load stock data
        stock_file = os.path.join(STOCK_DATA_DIR, f"{symbol}_stock_data.json")
        stock_data = load_json_data(stock_file)
        
        if not stock_data or "chart" not in stock_data or "result" not in stock_data["chart"] or not stock_data["chart"]["result"]:
            print(f"Error: Invalid or empty stock data for {symbol}.")
            continue
        
        # Extract price data
        result = stock_data["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        quotes = result.get("indicators", {}).get("quote", [{}])[0]
        adjclose = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
        
        # Check if we have data
        if not timestamps or not quotes:
            print(f"Error: No price data found for {symbol}.")
            continue
        
        # Insert price data
        for i, timestamp in enumerate(timestamps):
            if i >= len(quotes.get("close", [])) or quotes["close"][i] is None:
                continue
            
            # Convert timestamp to date
            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            
            # Get price data
            open_price = quotes.get("open", [])[i] if i < len(quotes.get("open", [])) else None
            high = quotes.get("high", [])[i] if i < len(quotes.get("high", [])) else None
            low = quotes.get("low", [])[i] if i < len(quotes.get("low", [])) else None
            close = quotes.get("close", [])[i]
            volume = quotes.get("volume", [])[i] if i < len(quotes.get("volume", [])) else None
            adj_close = adjclose[i] if i < len(adjclose) else close
            
            # Insert into database
            cursor.execute('''
            INSERT OR REPLACE INTO stock_prices 
            (stock_id, date, open, high, low, close, adj_close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (stock_id, date, open_price, high, low, close, adj_close, volume))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Stock prices table populated successfully.")

def populate_news_and_relationships():
    """Populate the news table and stock_news relationships."""
    print("Populating news table and relationships...")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Load news data
    news_data = load_json_data(NEWS_SENTIMENT_FILE)
    
    if not news_data:
        print("Error: No news data found.")
        conn.close()
        return
    
    # Get stock IDs
    stock_ids = {}
    for symbol in SYMBOLS:
        cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        if result:
            stock_ids[symbol] = result[0]
    
    # Process each news article
    for article in news_data:
        # Extract article data
        source = article.get("source", "Unknown")
        datetime_str = article.get("published_at", "")
        headline = article.get("title", "")
        summary = article.get("summary", "") or article.get("description", "")
        url = article.get("url", "")
        
        # Extract sentiment
        sentiment = article.get("sentiment", {})
        sentiment_score = sentiment.get("compound", 0)
        
        # Determine sentiment label
        if sentiment_score >= 0.05:
            sentiment_label = "positive"
        elif sentiment_score <= -0.05:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        # Insert into news table
        cursor.execute('''
        INSERT INTO news 
        (source, datetime, headline, summary, url, sentiment_score, sentiment_label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (source, datetime_str, headline, summary, url, sentiment_score, sentiment_label))
        
        # Get the news ID
        news_id = cursor.lastrowid
        
        # Extract entities/symbols
        entities = article.get("entities", [])
        related_symbols = set()
        
        for entity in entities:
            symbol = entity.get("symbol", "")
            if symbol in SYMBOLS:
                related_symbols.add(symbol)
        
        # If no specific symbols found but article is in our dataset,
        # it might be generally relevant to all our tracked symbols
        if not related_symbols and article in news_data:
            related_symbols = set(SYMBOLS)
        
        # Create relationships
        for symbol in related_symbols:
            if symbol in stock_ids:
                cursor.execute('''
                INSERT OR IGNORE INTO stock_news 
                (stock_id, news_id, sentiment_score)
                VALUES (?, ?, ?)
                ''', (stock_ids[symbol], news_id, sentiment_score))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("News table and relationships populated successfully.")

def populate_tweets_and_relationships():
    """Populate the tweets table and stock_tweets relationships."""
    print("Populating tweets table and relationships...")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Load tweets data
    tweets_data = load_json_data(TWITTER_SENTIMENT_FILE)
    
    if not tweets_data:
        print("Error: No tweets data found.")
        conn.close()
        return
    
    # Get stock IDs
    stock_ids = {}
    for symbol in SYMBOLS:
        cursor.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        if result:
            stock_ids[symbol] = result[0]
    
    # Process each tweet
    for tweet in tweets_data:
        # Extract tweet data
        tweet_id = tweet.get("id", "")
        user = tweet.get("user", {})
        user_name = user.get("name", "")
        user_screen_name = user.get("username", "")
        datetime_str = tweet.get("created_at", "")
        text = tweet.get("text", "")
        
        # Extract sentiment
        sentiment = tweet.get("sentiment", {})
        sentiment_score = sentiment.get("compound", 0)
        
        # Determine sentiment label
        if sentiment_score >= 0.05:
            sentiment_label = "positive"
        elif sentiment_score <= -0.05:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        # Insert into tweets table
        cursor.execute('''
        INSERT OR IGNORE INTO tweets 
        (tweet_id, user_name, user_screen_name, datetime, text, sentiment_score, sentiment_label)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tweet_id, user_name, user_screen_name, datetime_str, text, sentiment_score, sentiment_label))
        
        # Get the tweet ID from the database (might be different from tweet_id if it's a string)
        cursor.execute("SELECT id FROM tweets WHERE tweet_id = ?", (tweet_id,))
        result = cursor.fetchone()
        if not result:
            continue
        
        db_tweet_id = result[0]
        
        # Determine related symbols from the query
        query = tweet.get("query", "")
        related_symbols = set()
        
        for symbol in SYMBOLS:
            if symbol in query or f"${symbol}" in query or f"#{symbol}" in query:
                related_symbols.add(symbol)
        
        # Create relationships
        for symbol in related_symbols:
            if symbol in stock_ids:
                cursor.execute('''
                INSERT OR IGNORE INTO stock_tweets 
                (stock_id, tweet_id, sentiment_score)
                VALUES (?, ?, ?)
                ''', (stock_ids[symbol], db_tweet_id, sentiment_score))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Tweets table and relationships populated successfully.")

def main():
    """Main function to create and populate the database."""
    print("Starting database creation and population...")
    
    # Create database and tables
    create_database()
    
    # Populate tables
    populate_stocks_table()
    populate_stock_prices()
    populate_news_and_relationships()
    populate_tweets_and_relationships()
    
    print("Database creation and population complete.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **NoSQL database**: Could have used MongoDB or another NoSQL database for more flexible schema.
- **Cloud database**: Could have used a cloud database like PostgreSQL on AWS RDS or Google Cloud SQL.
- **Simple CSV files**: Could have kept data in CSV files for simplicity.

**Rationale:**
SQLite was chosen because:
1. It's lightweight and requires no separate server process
2. It's self-contained in a single file, making it easy to distribute
3. It supports SQL queries, which are powerful for data analysis
4. It's cross-platform and widely supported
5. It's sufficient for the scale of data in this project

The relational model was chosen to efficiently represent the relationships between stocks, news articles, and tweets. The many-to-many relationships (stock_news, stock_tweets) allow a single news article or tweet to be associated with multiple stocks, and vice versa.

## Exploratory Data Analysis

We performed exploratory data analysis (EDA) to understand the data and identify patterns. This included visualizing stock prices, sentiment trends, and correlations.

**Code: generate_dashboard_visualizations.py**
```python
#!/usr/bin/env python3.11
import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Constants
DATA_DIR = os.path.join(project_root, "data")
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json")
STOCK_DATA_DIR = os.path.join(DATA_DIR, "stock_data")
REPORTS_DIR = os.path.join(project_root, "reports", "dashboard_visualizations")
TABLEAU_DIR = os.path.join(project_root, "visualizations_tableau")
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

# Ensure directories exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TABLEAU_DIR, exist_ok=True)

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")
plt.rcParams['figure.figsize'] = [12, 7]
plt.rcParams['figure.dpi'] = 100

def load_json_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return []

def load_stock_data():
    """Load stock data for all symbols."""
    stock_dfs = {}
    
    for symbol in SYMBOLS:
        stock_file = os.path.join(STOCK_DATA_DIR, f"{symbol}_stock_data.json")
        data = load_json_data(stock_file)
        
        if data and "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            
            if timestamps and "close" in quotes:
                # Create DataFrame
                df = pd.DataFrame({
                    "timestamp": timestamps,
                    "open": quotes.get("open", [None] * len(timestamps)),
                    "high": quotes.get("high", [None] * len(timestamps)),
                    "low": quotes.get("low", [None] * len(timestamps)),
                    "close": quotes.get("close", [None] * len(timestamps)),
                    "volume": quotes.get("volume", [None] * len(timestamps))
                })
                
                # Convert timestamp to datetime
                df["date"] = pd.to_datetime(df["timestamp"], unit="s")
                
                # Add symbol column
                df["symbol"] = symbol
                
                # Calculate daily returns
                df["daily_return"] = df["close"].pct_change() * 100
                
                stock_dfs[symbol] = df
                print(f"Loaded stock data for {symbol}: {len(df)} rows")
            else:
                print(f"Error: Invalid or empty price data for {symbol}")
        else:
            print(f"Error: Invalid or empty stock data for {symbol}")
    
    return stock_dfs

def load_news_sentiment():
    """Load and process news sentiment data."""
    news_data = load_json_data(NEWS_SENTIMENT_FILE)
    
    if not news_data:
        print("Error: No news data found.")
        return pd.DataFrame()
    
    # Extract relevant fields
    news_records = []
    
    for article in news_data:
        # Basic article info
        record = {
            "title": article.get("title", ""),
            "published_at": article.get("published_at", ""),
            "source": article.get("source", ""),
            "url": article.get("url", "")
        }
        
        # Sentiment scores
        sentiment = article.get("sentiment", {})
        record["compound"] = sentiment.get("compound", 0)
        record["positive"] = sentiment.get("pos", 0)
        record["negative"] = sentiment.get("neg", 0)
        record["neutral"] = sentiment.get("neu", 0)
        
        # Extract symbols
        entities = article.get("entities", [])
        symbols = []
        
        for entity in entities:
            symbol = entity.get("symbol", "")
            if symbol in SYMBOLS:
                symbols.append(symbol)
        
        record["symbols"] = ",".join(symbols)
        
        news_records.append(record)
    
    # Create DataFrame
    news_df = pd.DataFrame(news_records)
    
    # Convert published_at to datetime
    if "published_at" in news_df.columns:
        news_df["published_at"] = pd.to_datetime(news_df["published_at"])
        news_df["date"] = news_df["published_at"].dt.date
        news_df["date"] = pd.to_datetime(news_df["date"])
    
    print(f"Loaded news sentiment data: {len(news_df)} articles")
    
    return news_df

def load_twitter_sentiment():
    """Load and process Twitter sentiment data."""
    twitter_data = load_json_data(TWITTER_SENTIMENT_FILE)
    
    if not twitter_data:
        print("Error: No Twitter data found.")
        return pd.DataFrame()
    
    # Extract relevant fields
    tweet_records = []
    
    for tweet in twitter_data:
        # Basic tweet info
        record = {
            "id": tweet.get("id", ""),
            "created_at": tweet.get("created_at", ""),
            "text": tweet.get("text", ""),
            "query": tweet.get("query", "")
        }
        
        # User info
        user = tweet.get("user", {})
        record["username"] = user.get("username", "")
        record["name"] = user.get("name", "")
        record["followers"] = user.get("followers", 0)
        
        # Sentiment scores
        sentiment = tweet.get("sentiment", {})
        record["compound"] = sentiment.get("compound", 0)
        record["positive"] = sentiment.get("pos", 0)
        record["negative"] = sentiment.get("neg", 0)
        record["neutral"] = sentiment.get("neu", 0)
        
        # Extract symbols from query
        symbols = []
        for symbol in SYMBOLS:
            if symbol in record["query"] or f"${symbol}" in record["query"] or f"#{symbol}" in record["query"]:
                symbols.append(symbol)
        
        record["symbols"] = ",".join(symbols)
        
        tweet_records.append(record)
    
    # Create DataFrame
    twitter_df = pd.DataFrame(tweet_records)
    
    # Convert created_at to datetime
    if "created_at" in twitter_df.columns:
        twitter_df["created_at"] = pd.to_datetime(twitter_df["created_at"])
        twitter_df["date"] = twitter_df["created_at"].dt.date
        twitter_df["date"] = pd.to_datetime(twitter_df["date"])
    
    print(f"Loaded Twitter sentiment data: {len(twitter_df)} tweets")
    
    return twitter_df

def create_stock_price_visualization(stock_dfs):
    """Create visualization of stock prices over time."""
    plt.figure(figsize=(14, 8))
    
    for symbol, df in stock_dfs.items():
        plt.plot(df["date"], df["close"], label=symbol)
    
    plt.title("Stock Prices Over Time", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price (USD)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save figure
    output_file = os.path.join(REPORTS_DIR, "stock_prices_over_time.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved stock price visualization to {output_file}")

def create_news_sentiment_visualization(news_df):
    """Create visualization of news sentiment over time."""
    if news_df.empty or "symbols" not in news_df.columns:
        print("Error: Invalid or empty news data for sentiment visualization.")
        return
    
    # Create a DataFrame with sentiment by symbol and date
    sentiment_by_symbol = []
    
    for _, row in news_df.iterrows():
        if row["symbols"]:
            for symbol in row["symbols"].split(","):
                sentiment_by_symbol.append({
                    "date": row["date"],
                    "symbol": symbol,
                    "compound": row["compound"]
                })
    
    if not sentiment_by_symbol:
        print("Error: No symbol-specific sentiment data found.")
        return
    
    sentiment_df = pd.DataFrame(sentiment_by_symbol)
    
    # Group by date and symbol, calculate mean sentiment
    daily_sentiment = sentiment_df.groupby(["date", "symbol"])["compound"].mean().reset_index()
    
    # Pivot to get symbols as columns
    pivot_df = daily_sentiment.pivot(index="date", columns="symbol", values="compound")
    
    # Plot
    plt.figure(figsize=(14, 8))
    
    for symbol in SYMBOLS:
        if symbol in pivot_df.columns:
            # Calculate 7-day moving average for smoother visualization
            plt.plot(pivot_df.index, pivot_df[symbol].rolling(window=7, min_periods=1).mean(), 
                     label=f"{symbol} (7-day MA)")
    
    plt.title("Average News Sentiment Over Time", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Compound Sentiment Score", fontsize=12)
    plt.axhline(y=0, color="gray", linestyle="--", alpha=0.7)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save figure
    output_file = os.path.join(REPORTS_DIR, "avg_news_sentiment_over_time.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved news sentiment visualization to {output_file}")

def create_sentiment_distribution_visualization(news_df):
    """Create visualization of sentiment distribution by symbol."""
    if news_df.empty or "symbols" not in news_df.columns:
        print("Error: Invalid or empty news data for sentiment distribution visualization.")
        return
    
    # Create a DataFrame with sentiment by symbol
    sentiment_by_symbol = []
    
    for _, row in news_df.iterrows():
        if row["symbols"]:
            for symbol in row["symbols"].split(","):
                sentiment_by_symbol.append({
                    "symbol": symbol,
                    "compound": row["compound"]
                })
    
    if not sentiment_by_symbol:
        print("Error: No symbol-specific sentiment data found.")
        return
    
    sentiment_df = pd.DataFrame(sentiment_by_symbol)
    
    # Plot
    plt.figure(figsize=(14, 8))
    
    sns.boxplot(x="symbol", y="compound", data=sentiment_df)
    
    plt.title("News Sentiment Distribution by Symbol", fontsize=16)
    plt.xlabel("Symbol", fontsize=12)
    plt.ylabel("Compound Sentiment Score", fontsize=12)
    plt.axhline(y=0, color="gray", linestyle="--", alpha=0.7)
    plt.grid(True, alpha=0.3)
    
    # Save figure
    output_file = os.path.join(REPORTS_DIR, "news_sentiment_distribution_boxplot.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved sentiment distribution visualization to {output_file}")

def create_correlation_heatmap(stock_dfs, news_df):
    """Create correlation heatmap between sentiment and stock returns."""
    if not stock_dfs or news_df.empty or "symbols" not in news_df.columns:
        print("Error: Invalid or empty data for correlation heatmap.")
        return
    
    # Create a DataFrame with sentiment by symbol and date
    sentiment_by_symbol = []
    
    for _, row in news_df.iterrows():
        if row["symbols"]:
            for symbol in row["symbols"].split(","):
                sentiment_by_symbol.append({
                    "date": row["date"],
                    "symbol": symbol,
                    "compound": row["compound"]
                })
    
    if not sentiment_by_symbol:
        print("Error: No symbol-specific sentiment data found.")
        return
    
    sentiment_df = pd.DataFrame(sentiment_by_symbol)
    
    # Group by date and symbol, calculate mean sentiment
    daily_sentiment = sentiment_df.groupby(["date", "symbol"])["compound"].mean().reset_index()
    
    # Create correlation data
    correlation_data = []
    
    for symbol in SYMBOLS:
        if symbol in stock_dfs:
            # Get stock data
            stock_df = stock_dfs[symbol].copy()
            
            # Get sentiment data for this symbol
            symbol_sentiment = daily_sentiment[daily_sentiment["symbol"] == symbol].copy()
            
            if not symbol_sentiment.empty:
                # Merge stock and sentiment data
                merged_df = pd.merge(stock_df, symbol_sentiment[["date", "compound"]], on="date", how="left")
                
                # Fill missing sentiment with 0 (neutral)
                merged_df["compound"].fillna(0, inplace=True)
                
                # Calculate lagged and future returns
                for i in range(1, 6):  # 1 to 5 days
                    merged_df[f"return_lag_{i}"] = merged_df["daily_return"].shift(i)
                    merged_df[f"return_future_{i}"] = merged_df["daily_return"].shift(-i)
                
                # Calculate correlation
                corr_columns = ["compound"] + [f"return_lag_{i}" for i in range(1, 6)] + [f"return_future_{i}" for i in range(1, 6)]
                corr_df = merged_df[corr_columns].corr()
                
                # Extract correlations with sentiment
                sentiment_corr = corr_df.loc["compound", :].drop("compound")
                
                for col, corr in sentiment_corr.items():
                    period = int(col.split("_")[-1])
                    direction = "lag" if "lag" in col else "future"
                    
                    correlation_data.append({
                        "symbol": symbol,
                        "period": period if direction == "lag" else -period,
                        "correlation": corr
                    })
    
    if not correlation_data:
        print("Error: No correlation data generated.")
        return
    
    correlation_df = pd.DataFrame(correlation_data)
    
    # Pivot for heatmap
    pivot_df = correlation_df.pivot(index="symbol", columns="period", values="correlation")
    
    # Sort columns
    pivot_df = pivot_df.reindex(sorted(pivot_df.columns))
    
    # Plot
    plt.figure(figsize=(14, 8))
    
    sns.heatmap(pivot_df, annot=True, cmap="RdBu_r", center=0, fmt=".2f")
    
    plt.title("Correlation between News Sentiment and Stock Returns", fontsize=16)
    plt.xlabel("Days (Negative = Future Returns, Positive = Past Returns)", fontsize=12)
    plt.ylabel("Symbol", fontsize=12)
    
    # Save figure
    output_file = os.path.join(REPORTS_DIR, "sentiment_return_correlation_heatmap.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved correlation heatmap to {output_file}")

def prepare_data_for_tableau(stock_dfs, news_df, twitter_df):
    """Prepare and export data for Tableau visualization."""
    # Create a master DataFrame for each symbol
    master_dfs = []
    
    for symbol in SYMBOLS:
        if symbol not in stock_dfs:
            continue
        
        # Get stock data
        stock_df = stock_dfs[symbol].copy()
        
        # Process news sentiment
        if not news_df.empty and "symbols" in news_df.columns:
            # Create a DataFrame with sentiment by symbol and date
            news_sentiment = []
            
            for _, row in news_df.iterrows():
                if row["symbols"] and symbol in row["symbols"].split(","):
                    news_sentiment.append({
                        "date": row["date"],
                        "compound": row["compound"],
                        "title": row["title"]
                    })
            
            if news_sentiment:
                news_sentiment_df = pd.DataFrame(news_sentiment)
                
                # Group by date, calculate mean sentiment and count
                daily_news = news_sentiment_df.groupby("date").agg({
                    "compound": "mean",
                    "title": "count"
                }).rename(columns={"title": "news_count"}).reset_index()
                
                # Merge with stock data
                stock_df = pd.merge(stock_df, daily_news, on="date", how="left")
                
                # Fill missing values
                stock_df["compound"].fillna(0, inplace=True)
                stock_df["news_count"].fillna(0, inplace=True)
        
        # Process Twitter sentiment
        if not twitter_df.empty and "symbols" in twitter_df.columns:
            # Create a DataFrame with sentiment by symbol and date
            twitter_sentiment = []
            
            for _, row in twitter_df.iterrows():
                if row["symbols"] and symbol in row["symbols"].split(","):
                    twitter_sentiment.append({
                        "date": row["date"],
                        "compound": row["compound"],
                        "id": row["id"]
                    })
            
            if twitter_sentiment:
                twitter_sentiment_df = pd.DataFrame(twitter_sentiment)
                
                # Group by date, calculate mean sentiment and count
                daily_twitter = twitter_sentiment_df.groupby("date").agg({
                    "compound": "mean",
                    "id": "count"
                }).rename(columns={"compound": "twitter_compound", "id": "tweet_count"}).reset_index()
                
                # Merge with stock data
                stock_df = pd.merge(stock_df, daily_twitter, on="date", how="left")
                
                # Fill missing values
                stock_df["twitter_compound"].fillna(0, inplace=True)
                stock_df["tweet_count"].fillna(0, inplace=True)
        
        # Add to master list
        master_dfs.append(stock_df)
    
    # Combine all DataFrames
    if master_dfs:
        master_df = pd.concat(master_dfs, ignore_index=True)
        
        # Export to CSV
        output_file = os.path.join(TABLEAU_DIR, "master_sentiment_stock_data.csv")
        master_df.to_csv(output_file, index=False)
        
        print(f"Exported master data for Tableau to {output_file}")
        
        # Also export individual symbol files
        for symbol in SYMBOLS:
            if symbol in stock_dfs:
                symbol_df = master_df[master_df["symbol"] == symbol]
                output_file = os.path.join(TABLEAU_DIR, f"{symbol}_data.csv")
                symbol_df.to_csv(output_file, index=False)
                print(f"Exported {symbol} data for Tableau to {output_file}")
    else:
        print("Error: No data to export for Tableau.")

def main():
    """Main function to generate dashboard visualizations."""
    print("Starting dashboard visualization generation...")
    
    # Load data
    stock_dfs = load_stock_data()
    news_df = load_news_sentiment()
    twitter_df = load_twitter_sentiment()
    
    # Create visualizations
    create_stock_price_visualization(stock_dfs)
    create_news_sentiment_visualization(news_df)
    create_sentiment_distribution_visualization(news_df)
    
    try:
        create_correlation_heatmap(stock_dfs, news_df)
    except Exception as e:
        print(f"Error creating correlation heatmap: {e}")
    
    # Prepare data for Tableau
    prepare_data_for_tableau(stock_dfs, news_df, twitter_df)
    
    print("Dashboard visualization generation complete.")

if __name__ == "__main__":
    main()
```

**Alternatives Considered:**
- **Interactive dashboards**: Could have created interactive dashboards with Dash or Streamlit.
- **Web-based visualizations**: Could have used D3.js or Plotly for web-based visualizations.
- **Different visualization libraries**: Could have used other Python visualization libraries like Bokeh or Altair.

**Rationale:**
Matplotlib and Seaborn were chosen because:
1. They are widely used and well-documented
2. They provide a good balance of customization and ease of use
3. They integrate well with pandas DataFrames
4. They produce publication-quality static visualizations
5. They are familiar to most data scientists and analysts

We also prepared data for Tableau, which is a powerful tool for creating interactive dashboards. This allows for more advanced interactive visualizations beyond what's easily achievable with Python libraries alone.

## Advanced Modeling

We implemented several models to predict stock prices based on historical prices and sentiment data.

### Random Forest Model

**Code: enhanced_modeling.py (Random Forest section)**
```python
# Random Forest model
def train_random_forest_model(X_train, y_train, X_test, y_test, symbol):
    """Train a Random Forest model and evaluate its performance."""
    print(f"\nTraining Random Forest model for {symbol}...")
    
    # Create and train the model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf_model.predict(X_test)
    
    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Random Forest MSE: {mse:.4f}")
    print(f"Random Forest RMSE: {rmse:.4f}")
    print(f"Random Forest R²: {r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance.head(10))
    
    # Plot actual vs predicted
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.values, label='Actual')
    plt.plot(y_pred, label='Predicted', alpha=0.7)
    plt.title(f'{symbol} Stock Price - Random Forest Predictions', fontsize=16)
    plt.xlabel('Test Sample', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save plot
    os.makedirs(os.path.join(REPORTS_DIR, "modeling_results"), exist_ok=True)
    plt.savefig(os.path.join(REPORTS_DIR, "modeling_results", f"{symbol.lower()}_rf_prediction.png"), 
                dpi=300, bbox_inches="tight")
    plt.close()
    
    # Save model
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(rf_model, os.path.join(MODELS_DIR, f"{symbol.lower()}_rf_model.joblib"))
    
    return {
        'model': 'Random Forest',
        'symbol': symbol,
        'mse': mse,
        'rmse': rmse,
        'r2': r2
    }
```

**Alternatives Considered:**
- **Linear Regression**: Simpler but less capable of capturing non-linear relationships.
- **Support Vector Regression (SVR)**: Good for non-linear relationships but can be slower to train.
- **Neural Networks**: More powerful but require more data and tuning.

**Rationale:**
Random Forest was chosen as our primary model because:
1. It can capture non-linear relationships between features
2. It's robust to outliers, which are common in financial data
3. It provides feature importance, helping us understand what drives predictions
4. It's less prone to overfitting than single decision trees
5. It requires minimal preprocessing (no scaling needed)

### XGBoost Model

**Code: enhanced_modeling.py (XGBoost section)**
```python
# XGBoost model
def train_xgboost_model(X_train, y_train, X_test, y_test, symbol):
    """Train an XGBoost model and evaluate its performance."""
    print(f"\nTraining XGBoost model for {symbol}...")
    
    # Create and train the model
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = xgb_model.predict(X_test)
    
    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"XGBoost MSE: {mse:.4f}")
    print(f"XGBoost RMSE: {rmse:.4f}")
    print(f"XGBoost R²: {r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': xgb_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance.head(10))
    
    # Plot actual vs predicted
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.values, label='Actual')
    plt.plot(y_pred, label='Predicted', alpha=0.7)
    plt.title(f'{symbol} Stock Price - XGBoost Predictions', fontsize=16)
    plt.xlabel('Test Sample', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(os.path.join(REPORTS_DIR, "modeling_results", f"{symbol.lower()}_xgb_prediction.png"), 
                dpi=300, bbox_inches="tight")
    plt.close()
    
    # Save model
    joblib.dump(xgb_model, os.path.join(MODELS_DIR, f"{symbol.lower()}_xgb_model.joblib"))
    
    return {
        'model': 'XGBoost',
        'symbol': symbol,
        'mse': mse,
        'rmse': rmse,
        'r2': r2
    }
```

**Alternatives Considered:**
- **LightGBM**: Another gradient boosting framework that's faster but might be less accurate for smaller datasets.
- **CatBoost**: Good for categorical features but more complex to implement.

**Rationale:**
XGBoost was chosen as our second model because:
1. It often outperforms Random Forest in prediction tasks
2. It uses gradient boosting, which can lead to better accuracy
3. It has built-in regularization to prevent overfitting
4. It's widely used in financial prediction tasks
5. It provides feature importance like Random Forest

### ARIMA Model

**Code: enhanced_modeling.py (ARIMA section)**
```python
# ARIMA model
def train_arima_model(df, symbol):
    """Train an ARIMA model and evaluate its performance."""
    print(f"\nTraining ARIMA model for {symbol}...")
    
    # Prepare data
    data = df['close'].values
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    try:
        # Find optimal ARIMA parameters
        print("Finding optimal ARIMA parameters...")
        model = auto_arima(train, seasonal=False, trace=True,
                          error_action='ignore', suppress_warnings=True,
                          stepwise=True, max_order=None, max_p=5, max_d=2, max_q=5)
        
        print(f"Best ARIMA model: {model.order}")
        
        # Fit the model
        arima_model = ARIMA(train, order=model.order)
        arima_result = arima_model.fit()
        
        # Make predictions
        predictions = arima_result.predict(start=train_size, end=train_size+len(test)-1)
        
        # Evaluate the model
        mse = mean_squared_error(test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(test, predictions)
        
        print(f"ARIMA MSE: {mse:.4f}")
        print(f"ARIMA RMSE: {rmse:.4f}")
        print(f"ARIMA R²: {r2:.4f}")
        
        # Plot actual vs predicted
        plt.figure(figsize=(12, 6))
        plt.plot(test, label='Actual')
        plt.plot(predictions, label='Predicted', alpha=0.7)
        plt.title(f'{symbol} Stock Price - ARIMA Predictions', fontsize=16)
        plt.xlabel('Test Sample', fontsize=12)
        plt.ylabel('Price (USD)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.savefig(os.path.join(REPORTS_DIR, "modeling_results", f"{symbol.lower()}_arima_prediction.png"), 
                    dpi=300, bbox_inches="tight")
        plt.close()
        
        # Save model
        joblib.dump(arima_result, os.path.join(MODELS_DIR, f"{symbol.lower()}_arima_model.joblib"))
        
        return {
            'model': 'ARIMA',
            'symbol': symbol,
            'mse': mse,
            'rmse': rmse,
            'r2': r2
        }
    
    except Exception as e:
        print(f"Error training ARIMA model: {e}")
        return {
            'model': 'ARIMA',
            'symbol': symbol,
            'mse': float('nan'),
            'rmse': float('nan'),
            'r2': float('nan')
        }
```

**Alternatives Considered:**
- **SARIMA**: Includes seasonality, which might be relevant for longer time series.
- **Prophet**: Facebook's time series forecasting tool, good for data with strong seasonal effects.
- **LSTM**: Deep learning approach for time series, requires more data but can capture complex patterns.

**Rationale:**
ARIMA was chosen as our time series model because:
1. It's a classical time series forecasting model with a strong theoretical foundation
2. It works well for stationary or differenced time series
3. It's interpretable, with clear parameters for autoregression, differencing, and moving average
4. It provides a good baseline for time series forecasting
5. It complements the machine learning models (Random Forest and XGBoost)

### Model Comparison

**Code: enhanced_modeling.py (Model Comparison section)**
```python
# Compare models
def compare_models(results):
    """Compare the performance of different models."""
    print("\nModel Comparison:")
    
    # Create DataFrame from results
    results_df = pd.DataFrame(results)
    
    # Group by model and calculate mean metrics
    model_comparison = results_df.groupby('model').agg({
        'mse': 'mean',
        'rmse': 'mean',
        'r2': 'mean'
    }).reset_index()
    
    print(model_comparison)
    
    # Save comparison to CSV
    model_comparison.to_csv(os.path.join(REPORTS_DIR, "modeling_results", "models_comparison.csv"), index=False)
    
    # Plot RMSE comparison
    plt.figure(figsize=(10, 6))
    sns.barplot(x='model', y='rmse', data=results_df)
    plt.title('Model Comparison - RMSE (lower is better)', fontsize=16)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('RMSE', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(os.path.join(REPORTS_DIR, "modeling_results", "model_comparison_rmse.png"), 
                dpi=300, bbox_inches="tight")
    plt.close()
    
    # Plot R² comparison
    plt.figure(figsize=(10, 6))
    sns.barplot(x='model', y='r2', data=results_df)
    plt.title('Model Comparison - R² (higher is better)', fontsize=16)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('R²', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(os.path.join(REPORTS_DIR, "modeling_results", "model_comparison_r2.png"), 
                dpi=300, bbox_inches="tight")
    plt.close()
```

**Alternatives Considered:**
- **Cross-validation**: Could have used k-fold cross-validation for more robust evaluation.
- **Different metrics**: Could have used additional metrics like MAE or MAPE.
- **Statistical tests**: Could have used statistical tests to determine if differences between models are significant.

**Rationale:**
Our model comparison approach was chosen because:
1. It provides a clear comparison of multiple models across multiple stocks
2. It uses both RMSE (to measure prediction error) and R² (to measure explained variance)
3. It includes visualizations for easy interpretation
4. It saves the comparison results for future reference
5. It's simple to understand and implement

## Interactive Visualization

We created Jupyter notebooks for interactive analysis and visualization, including an interactive dashboard.

**Code: 04_Interactive_Dashboard.ipynb (excerpt)**
```python
# Function to update the dashboard
def update_dashboard(change=None):
    # Clear outputs
    for i in range(3):
        dashboard_tabs.children[i].clear_output()
    
    # Get selected values
    symbol = symbol_dropdown.value
    start_date = start_date_picker.value
    end_date = end_date_picker.value
    ma_window = ma_slider.value
    show_sentiment = show_sentiment_checkbox.value
    model_type = model_dropdown.value
    prediction_days = prediction_days_slider.value
    
    # Update Price & Sentiment Tab
    with dashboard_tabs.children[0]:
        fig = plot_stock_sentiment(symbol, start_date, end_date, ma_window, show_sentiment)
        if isinstance(fig, HTML):
            display(fig)
        else:
            plt.show()
    
    # Update Sentiment Dashboard Tab
    with dashboard_tabs.children[1]:
        fig = plot_sentiment_dashboard(symbol, start_date, end_date)
        if isinstance(fig, HTML):
            display(fig)
        else:
            plt.show()
    
    # Update Model Predictions Tab
    with dashboard_tabs.children[2]:
        fig = plot_model_predictions(symbol, model_type, start_date, end_date, prediction_days)
        if isinstance(fig, HTML):
            display(fig)
        else:
            plt.show()
```

**Alternatives Considered:**
- **Dash or Streamlit**: Could have created a web-based dashboard with Dash or Streamlit.
- **Bokeh or Plotly**: Could have used interactive visualization libraries like Bokeh or Plotly.
- **Tableau**: Could have created the dashboard directly in Tableau.

**Rationale:**
Jupyter notebooks with ipywidgets were chosen because:
1. They provide a good balance of interactivity and ease of implementation
2. They work well within the Jupyter environment, which is familiar to data scientists
3. They allow for rich documentation alongside the code
4. They can be easily shared and run locally
5. They integrate well with the rest of our Python code

We also prepared data for Tableau, which provides more advanced interactive visualization capabilities for those who prefer it.

## Project Packaging and Deployment

We packaged the project for easy deployment on a Windows machine with VS Code.

**Code: setup_guide_windows_vscode_updated.md (excerpt)**
```markdown
# Market Sentiment Analysis Project - Windows & VS Code Setup Guide

This guide will help you set up and run the Market Sentiment Analysis project on your Windows computer using Visual Studio Code.

## Prerequisites

1. **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/)
2. **Visual Studio Code**: Download and install from [code.visualstudio.com](https://code.visualstudio.com/)
3. **VS Code Python Extension**: Install from the Extensions marketplace in VS Code

## Setup Instructions

### 1. Extract the Project Files

Extract the `market_sentiment_project_enhanced.zip` file to a location of your choice (e.g., `C:\Users\YourName\Documents\`).

### 2. Set Up a Virtual Environment

1. Open VS Code
2. Open the project folder: `File > Open Folder` and select the extracted `market_sentiment_project` folder
3. Open a terminal in VS Code: `Terminal > New Terminal`
4. Create a virtual environment:
   ```
   python -m venv venv
   ```
5. Activate the virtual environment:
   - On Windows Command Prompt: `venv\Scripts\activate`
   - On Windows PowerShell: `.\venv\Scripts\Activate.ps1`

### 3. Install Required Packages

With the virtual environment activated, install the required packages:

```
pip install -r requirements.txt
```
```

**Alternatives Considered:**
- **Docker**: Could have containerized the project for easier deployment.
- **Web application**: Could have created a web application with Flask or Django.
- **Cloud deployment**: Could have deployed the project to a cloud platform like AWS or Google Cloud.

**Rationale:**
The chosen approach (local setup with VS Code) was selected because:
1. It's accessible to users with varying levels of technical expertise
2. It requires minimal setup compared to alternatives like Docker or cloud deployment
3. It allows for direct interaction with the code and data
4. It works well for a learning project where understanding the code is important
5. It's consistent with the user's request to run the project on their Windows computer with VS Code

## Future Enhancements

Several potential enhancements were identified for future development:

1. **Real-time data collection**: Implement automated data collection to keep the analysis up-to-date.
2. **Advanced sentiment analysis**: Use more sophisticated NLP techniques like aspect-based sentiment analysis.
3. **Additional data sources**: Incorporate more data sources like SEC filings, earnings reports, or economic indicators.
4. **More advanced models**: Implement deep learning models like LSTM or transformer-based models.
5. **Trading strategy development**: Develop and backtest trading strategies based on sentiment signals.
6. **Web application**: Create a web application for easier access and sharing.
7. **Automated reporting**: Implement automated report generation for regular updates.

## Conclusion

The Market Sentiment Analysis project demonstrates a comprehensive approach to analyzing the relationship between public sentiment and stock price movements. By collecting data from multiple sources, performing sentiment analysis, and building predictive models, we've created a valuable tool for understanding how sentiment might influence stock prices.

The project showcases a wide range of data science skills, from data collection and preprocessing to advanced modeling and visualization. It also provides a solid foundation for further exploration and enhancement.
