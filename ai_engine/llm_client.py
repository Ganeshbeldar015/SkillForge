"""
llm_client.py
-------------
A secure, centralized wrapper for the OpenAI API.
Automatically falls back gracefully if the API key is missing or invalid.
"""

import os
import logging
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Check if OpenAI is strictly available
_OPENAI_AVAILABLE = False
try:
    import openai
    from openai import OpenAI
    # Check if key is actually provided and not empty
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        _OPENAI_AVAILABLE = True
except ImportError:
    pass

# Singleton client instance
_client = None

def get_llm_client() -> Optional[any]:
    """Returns the initialized OpenAI client, or None if unavailable/no key."""
    global _client
    if not _OPENAI_AVAILABLE:
        return None
        
    if _client is None:
        try:
            api_key = os.environ.get("OPENAI_API_KEY", "").strip()
            # Explicitly pass the key so it works seamlessly
            _client = OpenAI(api_key=api_key)
            logger.info("OpenAI API client successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
            
    return _client

def is_llm_active() -> bool:
    """Returns True if the OpenAI client is loaded and ready to use."""
    return get_llm_client() is not None
