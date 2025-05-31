"""
API configuration module.

This module provides API keys and endpoints for external data sources.
"""

import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Default API keys (replace with your own)
# Alpha Vantage API (Stock Data)
ALPHA_VANTAGE_API_KEY = "3CKQLFX71Z2NHLB5"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Marketaux API (News Data)
MARKETAUX_API_KEY = "MHoeIY9l1Rr8OGxD53i286Gnk8N8QhNrvAbkz5Ui"
MARKETAUX_BASE_URL = "https://api.marketaux.com/v1"

# Twitter API (Twitter Data)
TWITTER_API_KEY = "YOUR_TWITTER_API_KEY"
TWITTER_API_SECRET = "YOUR_TWITTER_API_SECRET"
TWITTER_ACCESS_TOKEN = "YOUR_TWITTER_ACCESS_TOKEN"
TWITTER_ACCESS_SECRET = "YOUR_TWITTER_ACCESS_SECRET"
TWITTER_BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"

# Path to API keys file
API_KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.json")

def load_api_keys():
    """
    Load API keys from api_keys.json file if it exists.
    
    Returns:
        dict: Dictionary containing API keys.
    """
    global ALPHA_VANTAGE_API_KEY, MARKETAUX_API_KEY
    global TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_BEARER_TOKEN
    
    try:
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r') as f:
                keys = json.load(f)
                
                # Update global variables with loaded keys
                ALPHA_VANTAGE_API_KEY = keys.get('alpha_vantage_api_key', ALPHA_VANTAGE_API_KEY)
                MARKETAUX_API_KEY = keys.get('marketaux_api_key', MARKETAUX_API_KEY)
                TWITTER_API_KEY = keys.get('twitter_api_key', TWITTER_API_KEY)
                TWITTER_API_SECRET = keys.get('twitter_api_secret', TWITTER_API_SECRET)
                TWITTER_ACCESS_TOKEN = keys.get('twitter_access_token', TWITTER_ACCESS_TOKEN)
                TWITTER_ACCESS_SECRET = keys.get('twitter_access_secret', TWITTER_ACCESS_SECRET)
                TWITTER_BEARER_TOKEN = keys.get('twitter_bearer_token', TWITTER_BEARER_TOKEN)
                
                logger.info("API keys loaded successfully from api_keys.json")
                return keys
        else:
            logger.warning(f"API keys file not found at {API_KEYS_FILE}")
            return {}
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return {}

def save_api_keys(keys):
    """
    Save API keys to api_keys.json file.
    
    Args:
        keys (dict): Dictionary containing API keys.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=4)
        logger.info("API keys saved successfully to api_keys.json")
        return True
    except Exception as e:
        logger.error(f"Error saving API keys: {e}")
        return False

def get_api_key(service):
    """
    Get API key for the specified service.
    
    Args:
        service (str): Service name ('alpha_vantage', 'marketaux', 'twitter').
    
    Returns:
        str: API key for the specified service.
    """
    # Load keys if not already loaded
    if not os.path.exists(API_KEYS_FILE):
        load_api_keys()
    
    if service == 'alpha_vantage':
        return ALPHA_VANTAGE_API_KEY
    elif service in ['marketaux', 'MARKETAUX_API_KEY']:
        return MARKETAUX_API_KEY
    elif service == 'twitter':
        return {
            'api_key': TWITTER_API_KEY,
            'api_secret': TWITTER_API_SECRET,
            'access_token': TWITTER_ACCESS_TOKEN,
            'access_secret': TWITTER_ACCESS_SECRET,
            'bearer_token': TWITTER_BEARER_TOKEN
        }
    else:
        logger.error(f"Unknown service: {service}")
        return None

def get_api_url(service):
    """
    Get API base URL for the specified service.
    
    Args:
        service (str): Service name ('alpha_vantage', 'marketaux').
    
    Returns:
        str: API base URL for the specified service.
    """
    if service == 'alpha_vantage':
        return ALPHA_VANTAGE_BASE_URL
    elif service == 'marketaux':
        return MARKETAUX_BASE_URL
    else:
        logger.error(f"Unknown service: {service}")
        return None

# Create a sample api_keys.json file if it doesn't exist
def create_sample_api_keys_file():
    """
    Create a sample api_keys.json file if it doesn't exist.
    """
    if not os.path.exists(API_KEYS_FILE):
        sample_keys = {
            'alpha_vantage_api_key': '3CKQLFX71Z2NHLB5',
            'marketaux_api_key': 'MHoeIY9l1Rr8OGxD53i286Gnk8N8QhNrvAbkz5Ui',
            'twitter_api_key': 'YOUR_TWITTER_API_KEY',
            'twitter_api_secret': 'YOUR_TWITTER_API_SECRET',
            'twitter_access_token': 'YOUR_TWITTER_ACCESS_TOKEN',
            'twitter_access_secret': 'YOUR_TWITTER_ACCESS_SECRET',
            'twitter_bearer_token': 'YOUR_TWITTER_BEARER_TOKEN'
        }
        save_api_keys(sample_keys)
        logger.info("Created sample api_keys.json file")

# Initialize API keys
create_sample_api_keys_file()
load_api_keys()
