"""
Text preprocessor module.

This module provides functionality for preprocessing text data before analysis.
"""

import re
import string
import logging
from typing import List, Optional

from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class TextPreprocessor:
    """
    Preprocessor for text data.
    
    This class provides methods for cleaning and preprocessing text data
    before sentiment analysis or other NLP tasks.
    """
    
    def __init__(self, 
                 remove_urls: bool = True,
                 remove_mentions: bool = True,
                 remove_hashtags: bool = False,
                 remove_punctuation: bool = False,
                 lowercase: bool = True):
        """
        Initialize the TextPreprocessor.
        
        Args:
            remove_urls: Whether to remove URLs from text. Defaults to True.
            remove_mentions: Whether to remove @mentions from text. Defaults to True.
            remove_hashtags: Whether to remove #hashtags from text. Defaults to False.
            remove_punctuation: Whether to remove punctuation from text. Defaults to False.
            lowercase: Whether to convert text to lowercase. Defaults to True.
        """
        self.remove_urls = remove_urls
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_punctuation = remove_punctuation
        self.lowercase = lowercase
        
        logger.info("Initialized TextPreprocessor")
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess a text string.
        
        Args:
            text: Text to preprocess.
        
        Returns:
            Preprocessed text.
        
        Raises:
            ValueError: If text is None or empty.
        """
        if not text or not isinstance(text, str):
            logger.warning("Input text is missing or not a string")
            raise ValueError("Input text is missing or not a string")
        
        processed_text = text
        
        # Remove URLs
        if self.remove_urls:
            processed_text = re.sub(r'http\S+|www\.\S+', '', processed_text)
        
        # Remove @mentions
        if self.remove_mentions:
            processed_text = re.sub(r'@\w+', '', processed_text)
        
        # Remove #hashtags
        if self.remove_hashtags:
            processed_text = re.sub(r'#\w+', '', processed_text)
        
        # Remove punctuation
        if self.remove_punctuation:
            processed_text = processed_text.translate(str.maketrans('', '', string.punctuation))
        
        # Convert to lowercase
        if self.lowercase:
            processed_text = processed_text.lower()
        
        # Remove extra whitespace
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        logger.debug(f"Preprocessed text: '{text[:50]}...' -> '{processed_text[:50]}...'")
        return processed_text
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Preprocess a batch of text strings.
        
        Args:
            texts: List of texts to preprocess.
        
        Returns:
            List of preprocessed texts.
        """
        logger.info(f"Preprocessing batch of {len(texts)} texts")
        processed_texts = []
        
        for text in texts:
            try:
                processed_text = self.preprocess(text)
                processed_texts.append(processed_text)
            except ValueError as e:
                logger.warning(f"Skipping invalid text: {e}")
                processed_texts.append("")
        
        return processed_texts
    
    def clean_financial_text(self, text: str) -> str:
        """
        Clean financial text with specific rules for financial content.
        
        Args:
            text: Financial text to clean.
        
        Returns:
            Cleaned financial text.
        """
        if not text or not isinstance(text, str):
            logger.warning("Input text is missing or not a string")
            raise ValueError("Input text is missing or not a string")
        
        # First apply standard preprocessing
        cleaned_text = self.preprocess(text)
        
        # Replace stock tickers with standardized format
        # e.g., $AAPL, $MSFT, $GOOGL
        cleaned_text = re.sub(r'\$([A-Za-z]{1,5})', r'stock_\1', cleaned_text)
        
        # Replace percentage values with standardized format
        cleaned_text = re.sub(r'(\d+(\.\d+)?)%', r'\1_percent', cleaned_text)
        
        # Replace dollar amounts with standardized format
        cleaned_text = re.sub(r'\$(\d+(\.\d+)?)', r'\1_dollars', cleaned_text)
        
        logger.debug(f"Cleaned financial text: '{text[:50]}...' -> '{cleaned_text[:50]}...'")
        return cleaned_text
