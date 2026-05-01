"""
Groq API service — wrapper for LLM inference calls with retry logic.
Uses httpx directly to avoid version conflicts between groq SDK and httpx.
"""

import os
import time
import logging
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

logger = logging.getLogger(__name__)

# Groq API configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds


def call_groq(
    prompt: str,
    system: str = "You are a helpful AI research assistant.",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """
    Send a prompt to the Groq API and return the response text.
    Includes retry logic with exponential backoff for rate limits.
    Uses httpx directly for maximum compatibility.
    
    Args:
        prompt: The user message to send.
        system: The system prompt to set the AI's behavior.
        temperature: Sampling temperature (0.0 - 1.0).
        max_tokens: Maximum tokens in the response.
        
    Returns:
        The LLM's response text.
        
    Raises:
        Exception: If all retries are exhausted.
    """
    last_exception = None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=120.0) as http_client:
                response = http_client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 429:
                    # Rate limited
                    delay = BASE_DELAY * (3 ** attempt)  # 2, 6, 18
                    # Try to get retry-after header
                    retry_after = response.headers.get("retry-after")
                    if retry_after:
                        try:
                            delay = max(delay, float(retry_after))
                        except ValueError:
                            pass
                            
                    last_exception = Exception(f"429 Rate Limit Exceeded. {response.text[:200]}")
                    logger.warning(
                        f"Rate limited on attempt {attempt + 1}/{MAX_RETRIES}. "
                        f"Waiting {delay}s before retry..."
                    )
                    time.sleep(delay)
                    continue

                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            last_exception = e
            logger.error(f"Groq API HTTP error on attempt {attempt + 1}: {e.response.status_code} - {e.response.text[:200]}")
            time.sleep(BASE_DELAY)

        except Exception as e:
            last_exception = e
            logger.error(f"Groq API error on attempt {attempt + 1}: {e}")
            time.sleep(BASE_DELAY)

    raise Exception(f"Groq API failed after {MAX_RETRIES} retries. Last error: {str(last_exception)}")
