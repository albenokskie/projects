import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
from typing import Optional, Dict, Any, Union, List, Callable
from datetime import datetime
import warnings
import time
from functools import wraps

from config import ConfluenceConfig, ConfluenceConfigError
from confluence_types import (
    ConfluencePage, 
    ConfluenceSearchResult, 
    ConfluenceContentResult, 
    ConfluenceSpaceResult
)


class ConfluenceAPIError(Exception):
    """Base exception for Confluence API errors."""
    pass


class ConfluenceAuthenticationError(ConfluenceAPIError):
    """Raised when authentication fails."""
    pass


class ConfluenceNotFoundError(ConfluenceAPIError):
    """Raised when a resource is not found."""
    pass


class ConfluenceRateLimitError(ConfluenceAPIError):
    """Raised when rate limit is exceeded."""
    pass


class ConfluenceServerError(ConfluenceAPIError):
    """Raised when server returns 5xx error."""
    pass


class RetryConfig:
    """Configuration for retry mechanism."""
    
    def __init__(
        self,
        total_retries: int = 3,
        backoff_factor: float = 1.0,
        status_forcelist: Optional[List[int]] = None,
        allowed_methods: Optional[List[str]] = None
    ):
        self.total_retries = total_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist or [429, 500, 502, 503, 504]
        self.allowed_methods = allowed_methods or ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]


class RateLimiter:
    """Rate limiter to control API request frequency."""
    
    def __init__(self, calls_per_second: float = 2.0):
        self.calls_per_second = calls_per_second
        self.last_called = 0.0
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator to rate limit function calls."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Calculate time since last call
            current_time = time.time()
            elapsed = current_time - self.last_called
            
            # Calculate minimum time between calls
            min_interval = 1.0 / self.calls_per_second
            
            # Wait if necessary
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
            
            # Update last called time
            self.last_called = time.time()
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper

class ConfluenceAPI:
    def __init__(
        self, 
        config: Optional[ConfluenceConfig] = None,
        base_url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None, 
        log_level: str = 'INFO'
    ):
        """
        Initialize Confluence API client
        
        Args:
            config: ConfluenceConfig object (recommended)
            base_url: Your Confluence base URL (deprecated, use config)
            username: Your email address (deprecated, use config)
            api_token: Your API token (deprecated, use config)
            log_level: Logging level (deprecated, use config)
        """
        # Handle backward compatibility
        if config is None:
            if base_url and username and api_token:
                warnings.warn(
                    "Passing credentials directly is deprecated and insecure. "
                    "Use ConfluenceConfig or environment variables instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                config = ConfluenceConfig(
                    base_url=base_url,
                    username=username,
                    api_token=api_token,
                    log_level=log_level,
                    load_from_env=False
                )
            else:
                # Load from environment
                config = ConfluenceConfig.from_env()
        
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.auth = HTTPBasicAuth(config.username, config.api_token)
        
        # Setup logging first (needed by other setup methods)
        self.logger = self._setup_logging(config.log_level)
        
        # Setup session with retry mechanism
        self.session = self._setup_session_with_retry()
        
        # Setup rate limiter
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.logger.info(f"Confluence API client initialized for {self.base_url}")
        self.logger.debug(f"Using username: {self._mask_username(config.username)}")
        self.logger.debug(f"Configuration: {config.mask_sensitive_data()}")
        self.logger.debug(f"Rate limiting: {config.rate_limit} requests per second")
    
    def _mask_username(self, username: str) -> str:
        """Mask username for logging (show first 3 chars and domain)."""
        if '@' in username:
            local, domain = username.split('@', 1)
            if len(local) > 3:
                return f"{local[:3]}***@{domain}"
        return f"{username[:3]}***" if len(username) > 3 else "***"
    
    def _setup_session_with_retry(self) -> requests.Session:
        """Set up requests session with retry mechanism."""
        session = requests.Session()
        session.auth = self.auth
        
        # Configure retry strategy
        retry_config = RetryConfig()
        retry_strategy = Retry(
            total=retry_config.total_retries,
            backoff_factor=retry_config.backoff_factor,
            status_forcelist=retry_config.status_forcelist,
            allowed_methods=retry_config.allowed_methods,
            raise_on_status=False  # We'll handle status codes manually
        )
        
        # Create HTTP adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set reasonable timeouts
        session.timeout = (10, 30)  # (connect_timeout, read_timeout)
        
        self.logger.debug(f"Session configured with retry strategy: {retry_config.total_retries} retries, "
                         f"backoff factor: {retry_config.backoff_factor}")
        
        return session
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a rate-limited request with proper error handling."""
        @self.rate_limiter
        def _request():
            return self.session.request(method, url, **kwargs)
        
        try:
            response = _request()
            
            # Handle rate limiting (429) specifically
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                        self.logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry.")
                        time.sleep(wait_time)
                        # Retry once after waiting
                        response = _request()
                    except ValueError:
                        self.logger.warning("Invalid Retry-After header, using default backoff")
            
            # Log response details for debugging
            self.logger.debug(f"{method} {url} -> {response.status_code}")
            if response.headers.get('X-RateLimit-Remaining'):
                self.logger.debug(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
            
            return response
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout for {method} {url}: {e}")
            raise ConfluenceAPIError(f"Request timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error for {method} {url}: {e}")
            raise ConfluenceAPIError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {method} {url}: {e}")
            raise ConfluenceAPIError(f"Request failed: {e}")
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """Handle HTTP error responses with specific exceptions."""
        if response.status_code == 401:
            self.logger.error("Authentication failed - check your credentials")
            raise ConfluenceAuthenticationError("Authentication failed - check your credentials")
        elif response.status_code == 403:
            self.logger.error("Access forbidden - insufficient permissions")
            raise ConfluenceAuthenticationError("Access forbidden - insufficient permissions")
        elif response.status_code == 404:
            self.logger.error("Resource not found")
            raise ConfluenceNotFoundError("Resource not found")
        elif response.status_code == 429:
            self.logger.error("Rate limit exceeded")
            raise ConfluenceRateLimitError("Rate limit exceeded")
        elif 500 <= response.status_code < 600:
            self.logger.error(f"Server error: {response.status_code}")
            raise ConfluenceServerError(f"Server error: {response.status_code}")
        elif not response.ok:
            self.logger.error(f"HTTP error: {response.status_code} - {response.text}")
            raise ConfluenceAPIError(f"HTTP error: {response.status_code} - {response.text}")
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ConfluenceAPI')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create file handler
        file_handler = logging.FileHandler('confluence_api.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_page_by_id(self, page_id: str, expand: Optional[str] = None) -> Optional[ConfluencePage]:
        """
        Fetch a page by its ID
        
        Args:
            page_id: The ID of the page to fetch
            expand: Additional properties to expand (e.g., 'body.storage,version,space')
        
        Returns:
            Page data as dictionary or None if failed
        """
        self.logger.info(f"Fetching page with ID: {page_id}")
        self.logger.debug(f"Expand parameters: {expand}")
        
        url = f'{self.base_url}/rest/api/content/{page_id}'
        params = {}
        if expand:
            params['expand'] = expand
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            start_time = datetime.now()
            response = self._make_request('GET', url, params=params)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Request duration: {duration:.3f} seconds")
            
            self._handle_response_errors(response)
            data = response.json()
            
            self.logger.info(f"Successfully fetched page '{data.get('title', 'Unknown')}' (ID: {page_id})")
            self.logger.debug(f"Page space: {data.get('space', {}).get('name', 'Unknown')}")
            self.logger.debug(f"Page version: {data.get('version', {}).get('number', 'Unknown')}")
            
            return data
        except ConfluenceAPIError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching page {page_id}: {e}")
            raise ConfluenceAPIError(f"Unexpected error: {e}")
    
    def search_pages(self, query: str, limit: int = 25) -> Optional[ConfluenceSearchResult]:
        """
        Search for pages using CQL (Confluence Query Language)
        
        Args:
            query: CQL query string (e.g., 'space=DEV AND title~"API"')
            limit: Maximum number of results to return
        
        Returns:
            Search results as dictionary or None if failed
        """
        self.logger.info(f"Searching pages with query: {query}")
        self.logger.debug(f"Search limit: {limit}")
        
        url = f'{self.base_url}/rest/api/search'
        params = {
            'cql': query,
            'limit': limit,
            'expand': 'content.body.storage,content.version,content.space'
        }
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            start_time = datetime.now()
            response = self.session.get(url, params=params)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Request duration: {duration:.3f} seconds")
            
            response.raise_for_status()
            data = response.json()
            
            total_results = data.get('totalSize', 0)
            self.logger.info(f"Search completed. Found {total_results} results")
            
            if data.get('results'):
                self.logger.debug(f"First result: {data['results'][0].get('content', {}).get('title', 'Unknown')}")
            
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to search: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return None
    
    def get_space_pages(self, space_key: str, limit: int = 25) -> Optional[ConfluenceContentResult]:
        """
        Get all pages from a specific space
        
        Args:
            space_key: The key of the space (e.g., 'DEV', 'PROJ')
            limit: Maximum number of pages to return
        
        Returns:
            Pages data as dictionary or None if failed
        """
        self.logger.info(f"Getting pages from space: {space_key}")
        self.logger.debug(f"Page limit: {limit}")
        
        url = f'{self.base_url}/rest/api/content'
        params = {
            'spaceKey': space_key,
            'type': 'page',
            'limit': limit,
            'expand': 'body.storage,version,space'
        }
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            start_time = datetime.now()
            response = self.session.get(url, params=params)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Request duration: {duration:.3f} seconds")
            
            response.raise_for_status()
            data = response.json()
            
            page_count = len(data.get('results', []))
            self.logger.info(f"Retrieved {page_count} pages from space '{space_key}'")
            
            if data.get('results'):
                page_titles = [page.get('title', 'Unknown') for page in data['results'][:3]]
                self.logger.debug(f"First few pages: {page_titles}")
            
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get pages from space {space_key}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return None
    
    def get_page_by_title(self, space_key: str, title: str) -> Optional[ConfluencePage]:
        """
        Get a page by its title within a space
        
        Args:
            space_key: The key of the space
            title: The exact title of the page
        
        Returns:
            Page data as dictionary or None if failed
        """
        self.logger.info(f"Getting page by title: '{title}' from space: {space_key}")
        
        url = f'{self.base_url}/rest/api/content'
        params = {
            'spaceKey': space_key,
            'title': title,
            'expand': 'body.storage,version,space'
        }
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            start_time = datetime.now()
            response = self.session.get(url, params=params)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Request duration: {duration:.3f} seconds")
            
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            
            if results:
                page = results[0]
                self.logger.info(f"Found page '{title}' (ID: {page.get('id')})")
                return page
            else:
                self.logger.warning(f"No page found with title '{title}' in space '{space_key}'")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get page '{title}' from space {space_key}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return None
    
    def get_spaces(self, limit: int = 25) -> Optional[ConfluenceSpaceResult]:
        """
        Get all spaces
        
        Args:
            limit: Maximum number of spaces to return
        
        Returns:
            Spaces data as dictionary or None if failed
        """
        self.logger.info(f"Getting all spaces (limit: {limit})")
        
        url = f'{self.base_url}/rest/api/space'
        params = {
            'limit': limit,
            'expand': 'description.plain,homepage'
        }
        
        self.logger.debug(f"Request URL: {url}")
        self.logger.debug(f"Request params: {params}")
        
        try:
            start_time = datetime.now()
            response = self.session.get(url, params=params)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug(f"Request duration: {duration:.3f} seconds")
            
            response.raise_for_status()
            data = response.json()
            
            space_count = len(data.get('results', []))
            self.logger.info(f"Retrieved {space_count} spaces")
            
            if data.get('results'):
                space_keys = [space.get('key', 'Unknown') for space in data['results'][:5]]
                self.logger.debug(f"Space keys: {space_keys}")
            
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get spaces: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return None
    
    def get_page_content_html(self, page_id: str) -> Optional[str]:
        """
        Get the HTML content of a page
        
        Args:
            page_id: The ID of the page
        
        Returns:
            HTML content as string or None if failed
        """
        self.logger.info(f"Getting HTML content for page ID: {page_id}")
        
        page_data = self.get_page_by_id(page_id, expand='body.view')
        if page_data and 'body' in page_data and 'view' in page_data['body']:
            content = page_data['body']['view']['value']
            content_length = len(content)
            self.logger.info(f"Retrieved HTML content ({content_length} characters)")
            self.logger.debug(f"HTML preview: {content[:100]}...")
            return content
        else:
            self.logger.warning(f"No HTML content found for page ID: {page_id}")
            return None
    
    def get_page_content_storage(self, page_id: str) -> Optional[str]:
        """
        Get the storage format content of a page (Confluence markup)
        
        Args:
            page_id: The ID of the page
        
        Returns:
            Storage content as string or None if failed
        """
        self.logger.info(f"Getting storage content for page ID: {page_id}")
        
        page_data = self.get_page_by_id(page_id, expand='body.storage')
        if page_data and 'body' in page_data and 'storage' in page_data['body']:
            content = page_data['body']['storage']['value']
            content_length = len(content)
            self.logger.info(f"Retrieved storage content ({content_length} characters)")
            self.logger.debug(f"Storage preview: {content[:100]}...")
            return content
        else:
            self.logger.warning(f"No storage content found for page ID: {page_id}")
            return None

# Example usage
def main():
    """Main function demonstrating API usage."""
    # Setup logging level (DEBUG for detailed logs, INFO for general info)
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize the API client using environment variables (recommended)
        # Make sure to set up your .env file with credentials
        confluence = ConfluenceAPI()
        
        print("Confluence API client initialized successfully!")
        print("Configuration loaded from environment variables.")
        
    except ConfluenceConfigError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file or environment variables.")
        print("Copy .env.example to .env and fill in your credentials.")
        return
    except Exception as e:
        print(f"Failed to initialize API client: {e}")
        return


if __name__ == "__main__":
    main()
