#!/usr/bin/env python3.11
import json
import os
import sys
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

DATA_DIR = os.path.join(project_root, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "marketaux_news_data.json")
TWITTER_DATA_FILE = os.path.join(DATA_DIR, "twitter_data.json")

OUTPUT_NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
OUTPUT_TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json")

# Download VADER lexicon if not already present
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError: # More general error for resource not found
    print("Downloading VADER lexicon...")
    nltk.download("vader_lexicon")

sid = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """Analyzes sentiment of a given text using VADER."""
    if not text or not isinstance(text, str):
        return {"compound": 0, "neg": 0, "neu": 1, "pos": 0, "error": "Input text is missing or not a string"}
    try:
        return sid.polarity_scores(text)
    except Exception as e:
        print(f"Error during sentiment analysis for text 	{text[:50]}...	: {e}")
        return {"compound": 0, "neg": 0, "neu": 1, "pos": 0, "error": str(e)}

def process_news_data(filepath):
    """Loads news data, performs sentiment analysis, and returns data with sentiment."""
    print(f"Processing news data from: {filepath}")
    try:
        with open(filepath, "r") as f:
            news_data_collection = json.load(f)
    except FileNotFoundError:
        print(f"Error: News data file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return []

    processed_articles = []
    if isinstance(news_data_collection, dict) and "data" in news_data_collection:
        articles = news_data_collection.get("data", [])
        if not isinstance(articles, list):
            print(f"Warning: Expected a list of articles in news_data_collection[	data	], got {type(articles)}")
            articles = [] # Treat as empty if not a list
    elif isinstance(news_data_collection, list): # If the file directly contains a list of articles
        articles = news_data_collection
    else:
        print(f"Warning: News data file {filepath} is not in the expected dict format with a 	data	 key or a direct list of articles.")
        return []

    for article in articles:
        # Combine title, snippet, and description for a more comprehensive sentiment analysis
        text_to_analyze = " ".join(filter(None, [article.get("title"), article.get("snippet"), article.get("description")]))
        if not text_to_analyze.strip():
            text_to_analyze = "N/A" # Handle cases where all fields might be empty
        
        article["sentiment"] = analyze_sentiment(text_to_analyze)
        processed_articles.append(article)
    print(f"Finished processing {len(processed_articles)} news articles.")
    return processed_articles

def process_twitter_data(filepath):
    """Loads Twitter data, performs sentiment analysis, and returns data with sentiment."""
    print(f"Processing Twitter data from: {filepath}")
    try:
        with open(filepath, "r") as f:
            twitter_responses = json.load(f) # This is a list of responses, one per query
    except FileNotFoundError:
        print(f"Error: Twitter data file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return []

    processed_tweets_data = []
    for query_response in twitter_responses:
        query = query_response.get("query")
        response_content = query_response.get("response")
        processed_query_tweets = {"query": query, "tweets_with_sentiment": []}

        if response_content and response_content.get("result") and response_content["result"].get("timeline") and response_content["result"]["timeline"].get("instructions"):
            entries = []
            for instruction in response_content["result"]["timeline"]["instructions"]:
                if instruction.get("type") == "TimelineAddEntries" or instruction.get("type") == "TimelineReplaceEntries":
                    if instruction.get("entries"):
                        entries.extend(instruction["entries"])
            
            for entry in entries:
                # Traversing the complex structure to find tweet text
                # This structure can vary, so robust parsing is key. This is a common path.
                tweet_text = None
                try:
                    # Path for typical tweets
                    if entry.get("content") and entry["content"].get("itemContent") and entry["content"]["itemContent"].get("tweet_results") and entry["content"]["itemContent"]["tweet_results"].get("result") and entry["content"]["itemContent"]["tweet_results"]["result"].get("legacy") and entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"].get("full_text"):
                        tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
                    # Fallback for potentially different structures or retweets
                    elif entry.get("content") and entry["content"].get("itemContent") and entry["content"]["itemContent"].get("tweet_results") and entry["content"]["itemContent"]["tweet_results"].get("result") and entry["content"]["itemContent"]["tweet_results"]["result"].get("tweet") and entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"].get("legacy") and entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"].get("full_text"):
                         tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"]["full_text"]
                except AttributeError:
                    pass # Handle cases where path doesn't exist
                
                if tweet_text:
                    sentiment_scores = analyze_sentiment(tweet_text)
                    # Store the original entry data along with sentiment
                    # Or just the relevant parts of the tweet for brevity
                    tweet_id_str = entry.get("entryId", "").split("-")[-1]
                    user_info = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
                    screen_name = user_info.get("screen_name")
                    created_at = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {}).get("legacy", {}).get("created_at")

                    processed_query_tweets["tweets_with_sentiment"].append({
                        "tweet_id": tweet_id_str,
                        "text": tweet_text,
                        "user_screen_name": screen_name,
                        "created_at": created_at,
                        "sentiment": sentiment_scores,
                        "original_entry_data": entry # Optionally include for full context if needed later
                    })
        processed_tweets_data.append(processed_query_tweets)
    print(f"Finished processing Twitter data for {len(processed_tweets_data)} queries.")
    return processed_tweets_data

def save_processed_data(data, filepath):
    """Saves the processed data (with sentiment) to a JSON file."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Processed data successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving processed data to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting sentiment analysis process...")
    
    # Process News Data
    news_with_sentiment = process_news_data(NEWS_DATA_FILE)
    if news_with_sentiment:
        save_processed_data(news_with_sentiment, OUTPUT_NEWS_SENTIMENT_FILE)
    else:
        print("No news data was processed or news data file was empty/invalid.")

    # Process Twitter Data
    twitter_with_sentiment = process_twitter_data(TWITTER_DATA_FILE)
    if twitter_with_sentiment:
        save_processed_data(twitter_with_sentiment, OUTPUT_TWITTER_SENTIMENT_FILE)
    else:
        print("No Twitter data was processed or Twitter data file was empty/invalid.")
        
    print("Sentiment analysis process completed.")

