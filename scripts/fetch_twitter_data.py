#!/usr/bin/env python3.11
import json
import os
import sys

# Add the project root directory to the Python path to find data_api.py and api_keys.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# sys.path.append("/opt/.manus/.sandbox-runtime") # For data_api module

from data_api import ApiClient

# Define parameters
SYMBOLS = ["AAPL", "MSFT", "GOOGL"] # Example stock symbols
QUERIES = [query for symbol in SYMBOLS for query in (f"${symbol} stock", f"#{symbol} stock price")] # Example queries
COUNT_PER_QUERY = 20 # Number of tweets per query, adjust as needed within API limits
SEARCH_TYPE = "Latest" # Or "Top"

DATA_DIR = os.path.join(project_root, "data")
OUTPUT_FILENAME = "twitter_data.json"

client = ApiClient()

def fetch_twitter_data(query, count, search_type):
    """Fetches twitter data using the Twitter/search_twitter API."""
    print(f"Fetching tweets for query: 	{query}	, count: {count}, type: {search_type}")
    try:
        response = client.call_api(
            "tweets/search/recent", 
            query={
                "query": query,
                "max_results": count,
                # "type": search_type
            }
        )
        # The API call_api already returns a parsed dictionary if the response is JSON
        # No need for response.json() here
        print(f"Successfully fetched tweets for query: {query}")
        return response
    except Exception as e:
        print(f"Error fetching tweets for query 	{query}	: {e}")
        return None

def save_data_to_json(data, filename):
    """Saves data to a JSON file in the data directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    
    all_tweets_data = []
    # Check if file already exists and load its content
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                all_tweets_data = json.load(f)
            if not isinstance(all_tweets_data, list):
                print(f"Warning: Existing file {filepath} does not contain a list. It will be overwritten.")
                all_tweets_data = []
        except json.JSONDecodeError:
            print(f"Warning: Existing file {filepath} is not valid JSON. It will be overwritten.")
            all_tweets_data = []

    # Append new data
    if isinstance(data, list):
        all_tweets_data.extend(data)
    elif isinstance(data, dict):
        all_tweets_data.append(data) # If a single query result is passed
    else:
        print(f"Warning: Data to save is not a list or dict: {type(data)}")
        return

    try:
        with open(filepath, "w") as f:
            json.dump(all_tweets_data, f, indent=4)
        print(f"Data successfully appended/saved to {filepath}")
    except IOError as e:
        print(f"Error saving data to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting Twitter data fetch...")
    collected_tweets_for_all_queries = []

    for query_term in QUERIES:
        print(f"Processing query: {query_term}")
        twitter_data_response = fetch_twitter_data(query=query_term, count=COUNT_PER_QUERY, search_type=SEARCH_TYPE)
        
        if twitter_data_response and twitter_data_response.get("result") and twitter_data_response["result"].get("timeline") and twitter_data_response["result"]["timeline"].get("instructions"):
            # Extract actual tweet entries
            # The structure is nested: result -> timeline -> instructions (list) -> entries (list in one of the instructions)
            entries = []
            for instruction in twitter_data_response["result"]["timeline"]["instructions"]:
                if instruction.get("type") == "TimelineAddEntries" or instruction.get("type") == "TimelineReplaceEntries": # Common instruction types containing entries
                    if instruction.get("entries"):
                        entries.extend(instruction["entries"])
            
            if entries:
                print(f"Found {len(entries)} entries for query 	{query_term}	.")
                # We might want to filter these entries further to get only actual tweets
                # For now, saving the relevant part of the structure
                collected_tweets_for_all_queries.append({"query": query_term, "response": twitter_data_response}) # Store the whole response per query for now
            else:
                print(f"No entries found in the expected structure for query: {query_term}")
                collected_tweets_for_all_queries.append({"query": query_term, "response": twitter_data_response, "error": "No entries found in expected structure"})
        elif twitter_data_response:
            print(f"Fetched data for query 	{query_term}	, but it might be empty or in an unexpected format.")
            collected_tweets_for_all_queries.append({"query": query_term, "response": twitter_data_response, "error": "Unexpected response format"})
        else:
            print(f"Failed to fetch Twitter data for query: {query_term}")
            collected_tweets_for_all_queries.append({"query": query_term, "response": None, "error": "Fetch failed"})
    
    if collected_tweets_for_all_queries:
        save_data_to_json(collected_tweets_for_all_queries, OUTPUT_FILENAME)
        print(f"Finished fetching Twitter data. All responses saved.")
    else:
        print("No Twitter data was collected.")

