"""
Sentiment analyzer module.

This module provides functionality for analyzing sentiment in text data.
"""

import logging
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict, List, Any, Optional, Union

from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer:
    """
    Analyzer for sentiment in text data.
    
    This class provides methods for analyzing sentiment in text data
    using the VADER sentiment analysis tool from NLTK.
    
    Attributes:
        analyzer: VADER sentiment intensity analyzer.
    """
    
    def __init__(self):
        """
        Initialize the SentimentAnalyzer.
        
        Downloads the VADER lexicon if not already present.
        """
        # Download VADER lexicon if not already present
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
            logger.debug("VADER lexicon already downloaded")
        except LookupError:
            logger.info("Downloading VADER lexicon...")
            nltk.download("vader_lexicon", quiet=True)
        
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info("Initialized SentimentAnalyzer with VADER")
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a given text.
        
        Args:
            text: Text to analyze.
        
        Returns:
            Dictionary containing sentiment scores:
            - compound: Compound score (-1 to 1)
            - neg: Negative score (0 to 1)
            - neu: Neutral score (0 to 1)
            - pos: Positive score (0 to 1)
        
        Raises:
            ValueError: If text is None or empty.
        """
        if not text or not isinstance(text, str):
            logger.warning("Input text is missing or not a string")
            return {"compound": 0, "neg": 0, "neu": 1, "pos": 0, "error": "Input text is missing or not a string"}
        
        try:
            scores = self.analyzer.polarity_scores(text)
            logger.debug(f"Analyzed sentiment for text: '{text[:50]}...' - Compound score: {scores['compound']}")
            return scores
        except Exception as e:
            logger.error(f"Error during sentiment analysis for text '{text[:50]}...': {e}")
            return {"compound": 0, "neg": 0, "neu": 1, "pos": 0, "error": str(e)}
    
    def analyze_news_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for a list of news articles.
        
        Args:
            articles: List of news article dictionaries.
        
        Returns:
            List of news article dictionaries with sentiment scores added.
        """
        logger.info(f"Analyzing sentiment for {len(articles)} news articles")
        processed_articles = []
        
        for article in articles:
            # Combine title, snippet, and description for a more comprehensive sentiment analysis
            text_to_analyze = " ".join(filter(None, [
                article.get("title", ""), 
                article.get("snippet", ""), 
                article.get("description", "")
            ]))
            
            if not text_to_analyze.strip():
                text_to_analyze = "N/A"  # Handle cases where all fields might be empty
            
            article["sentiment"] = self.analyze_text(text_to_analyze)
            processed_articles.append(article)
        
        logger.info(f"Finished analyzing sentiment for {len(processed_articles)} news articles")
        return processed_articles
    
    def analyze_tweets(self, tweets_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for Twitter data.
        
        Args:
            tweets_data: List of Twitter data dictionaries, each containing a query and response.
        
        Returns:
            List of Twitter data dictionaries with sentiment scores added.
        """
        logger.info(f"Analyzing sentiment for Twitter data from {len(tweets_data)} queries")
        processed_tweets_data = []
        
        for query_response in tweets_data:
            query = query_response.get("query", "")
            response_content = query_response.get("response", {})
            processed_query_tweets = {"query": query, "tweets_with_sentiment": []}
            
            if (response_content and response_content.get("result") and 
                response_content["result"].get("timeline") and 
                response_content["result"]["timeline"].get("instructions")):
                
                entries = []
                for instruction in response_content["result"]["timeline"]["instructions"]:
                    if instruction.get("type") in ["TimelineAddEntries", "TimelineReplaceEntries"]:
                        if instruction.get("entries"):
                            entries.extend(instruction["entries"])
                
                for entry in entries:
                    tweet_text = self._extract_tweet_text(entry)
                    
                    if tweet_text:
                        sentiment_scores = self.analyze_text(tweet_text)
                        tweet_info = self._extract_tweet_info(entry)
                        tweet_info["text"] = tweet_text
                        tweet_info["sentiment"] = sentiment_scores
                        
                        processed_query_tweets["tweets_with_sentiment"].append(tweet_info)
            
            processed_tweets_data.append(processed_query_tweets)
        
        logger.info(f"Finished analyzing sentiment for Twitter data from {len(processed_tweets_data)} queries")
        return processed_tweets_data
    
    def _extract_tweet_text(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Extract tweet text from a Twitter API entry.
        
        Args:
            entry: Twitter API entry dictionary.
        
        Returns:
            Tweet text, or None if not found.
        """
        tweet_text = None
        try:
            # Path for typical tweets
            if (entry.get("content") and entry["content"].get("itemContent") and 
                entry["content"]["itemContent"].get("tweet_results") and 
                entry["content"]["itemContent"]["tweet_results"].get("result") and 
                entry["content"]["itemContent"]["tweet_results"]["result"].get("legacy") and 
                entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"].get("full_text")):
                
                tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
            
            # Fallback for potentially different structures or retweets
            elif (entry.get("content") and entry["content"].get("itemContent") and 
                  entry["content"]["itemContent"].get("tweet_results") and 
                  entry["content"]["itemContent"]["tweet_results"].get("result") and 
                  entry["content"]["itemContent"]["tweet_results"]["result"].get("tweet") and 
                  entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"].get("legacy") and 
                  entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"].get("full_text")):
                
                tweet_text = entry["content"]["itemContent"]["tweet_results"]["result"]["tweet"]["legacy"]["full_text"]
        
        except (AttributeError, KeyError) as e:
            logger.debug(f"Error extracting tweet text: {e}")
        
        return tweet_text
    
    def _extract_tweet_info(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tweet information from a Twitter API entry.
        
        Args:
            entry: Twitter API entry dictionary.
        
        Returns:
            Dictionary containing tweet information.
        """
        tweet_id_str = entry.get("entryId", "").split("-")[-1]
        
        user_info = (entry.get("content", {})
                    .get("itemContent", {})
                    .get("tweet_results", {})
                    .get("result", {})
                    .get("core", {})
                    .get("user_results", {})
                    .get("result", {})
                    .get("legacy", {}))
        
        screen_name = user_info.get("screen_name", "")
        user_name = user_info.get("name", "")
        
        created_at = (entry.get("content", {})
                     .get("itemContent", {})
                     .get("tweet_results", {})
                     .get("result", {})
                     .get("legacy", {})
                     .get("created_at", ""))
        
        return {
            "tweet_id": tweet_id_str,
            "user_screen_name": screen_name,
            "user_name": user_name,
            "created_at": created_at,
            "original_entry_data": entry  # Optionally include for full context if needed later
        }
