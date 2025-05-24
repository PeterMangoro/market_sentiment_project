import os
import sys
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Add project root to path to import api_keys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Constants
DATA_DIR = os.path.join(project_root,"data")
NEWS_FILE = os.path.join(DATA_DIR,"marketaux_news_data.json")
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR,"marketaux_news_sentiment.json")

def load_json_data(file_path):
    try:
        with open(file_path,"r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return []
    
def save_json_data(file_path, data):
    try:
        with open(file_path, "w") as file:
            json.dump(data,file, indent=4)
            print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

def initialize_sentiment_analyzer():
    try:
        # Check if VADER lexicon is already downloaded
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        # If not, download it
        print("Downloading VADER lexicon...")
        nltk.download('vader_lexicon')

    return SentimentIntensityAnalyzer()

def analyze_news_sentiment(news_data, analyzer):

    print(f"Analyzing sentiment for {len(news_data)} news articles...")

    for article in news_data:
        # Check if 'title' and 'description' exist in the article and combine them
        text = ""
        if 'title' in article:
            text += article['title'] + " "
        if 'description' in article:
            text += article['description'] + " "
        if 'summary' in article:
            text += article['summary'] + " "

        # If no text is found, skip the article
        if not text.strip():
            print("No text found for article, skipping...")
            article['sentiment'] = {
                'compound': 0,
                'pos': 0,
                'neu': 0,
                'neg': 1.0
            }
            continue

        # Analyze sentiment
        sentiment = analyzer.polarity_scores(text)
        article['sentiment'] = sentiment

    return news_data

def main():
    print("Starting sentiment analysis...")
    # Load news data
    news_data = load_json_data(NEWS_FILE)
    if not news_data:
        print("No news data found, exiting...")
        return
    # Initialize sentiment analyzer
    analyzer = initialize_sentiment_analyzer()

    # Analyze sentiment
    analyzed_news_data = analyze_news_sentiment(news_data, analyzer)
    # Save analyzed data
    save_json_data(NEWS_SENTIMENT_FILE, analyzed_news_data)
    print("Sentiment analysis completed and saved to file.")

if __name__ == "__main__":
    main()
