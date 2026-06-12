import time
import requests
import logging

logger = logging.getLogger(__name__)

# Standard user-agent to bypass basic scrape protection
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_url(url: str, headers: dict = None, retries: int = 3, backoff: float = 1.0, timeout: int = 10) -> str:
    """
    Fetches the raw HTML content of a URL with request retries and exponential backoff.
    
    Args:
        url: The target web page URL.
        headers: Optional custom request headers.
        retries: Number of retry attempts for transient errors.
        backoff: Base sleep time (in seconds) for exponential backoff.
        timeout: Request timeout in seconds.
        
    Returns:
        The raw HTML string of the fetched page.
        
    Raises:
        requests.RequestException: If the fetch fails after all retries or returns a non-200 status code.
    """
    req_headers = headers if headers is not None else DEFAULT_HEADERS
    
    for attempt in range(retries):
        try:
            logger.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{retries})")
            response = requests.get(url, headers=req_headers, timeout=timeout)
            
            # Raise an HTTPError if status code is not 200/OK
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            logger.warning(f"Error fetching {url} on attempt {attempt + 1}: {e}")
            if attempt == retries - 1:
                logger.error(f"Failed to fetch {url} after {retries} attempts.")
                raise e
            
            sleep_time = backoff * (2 ** attempt)
            logger.info(f"Sleeping for {sleep_time} seconds before retrying...")
            time.sleep(sleep_time)
            
    raise requests.RequestException(f"Failed to fetch {url} due to unknown retry failure.")
