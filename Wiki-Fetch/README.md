# Confluence API Client

A robust Python client for the Confluence REST API with enterprise-grade features including secure credential management, retry mechanisms, rate limiting, and comprehensive error handling.

## Features

- 🔐 **Secure credential management** using environment variables
- 🔄 **Automatic retry** with exponential backoff for transient failures
- ⚡ **Rate limiting** to prevent API abuse
- 🛡️ **Comprehensive error handling** with specific exception types
- 📝 **Detailed logging** with sensitive data masking
- 🧪 **Extensive test coverage** with unit and integration tests
- 📊 **Type hints** for better IDE support and code quality
- 🔧 **Configurable** for different environments

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd confluence-api-client
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development:
```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

### Environment Variables (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your Confluence details:
```env
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token-here
CONFLUENCE_LOG_LEVEL=INFO
CONFLUENCE_RATE_LIMIT=2.0
```

### Getting Your API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label and copy the generated token
4. Use this token as your `CONFLUENCE_API_TOKEN`

## Usage

### Basic Usage

```python
from wiki_fetch import ConfluenceAPI
from config import ConfluenceConfig

# Initialize with environment variables (recommended)
api = ConfluenceAPI()

# Or initialize with explicit config
config = ConfluenceConfig(
    base_url="https://your-domain.atlassian.net/wiki",
    username="your-email@company.com",
    api_token="your-api-token"
)
api = ConfluenceAPI(config=config)
```

### Examples

#### Get a page by ID
```python
try:
    page = api.get_page_by_id("123456", expand="body.storage,version,space")
    print(f"Page title: {page['title']}")
    print(f"Space: {page['space']['name']}")
except ConfluenceNotFoundError:
    print("Page not found")
except ConfluenceAuthenticationError:
    print("Authentication failed - check your credentials")
```

#### Search for pages
```python
results = api.search_pages('space=DEV AND title~"API"', limit=10)
if results:
    for result in results['results']:
        content = result['content']
        print(f"- {content['title']} (ID: {content['id']})")
```

#### Get all pages from a space
```python
pages = api.get_space_pages("DEV", limit=50)
if pages:
    for page in pages['results']:
        print(f"- {page['title']} (ID: {page['id']})")
```

#### Get page content
```python
# Get HTML content
html_content = api.get_page_content_html("123456")

# Get storage format (Confluence markup)
storage_content = api.get_page_content_storage("123456")
```

### Error Handling

The client provides specific exception types for different error scenarios:

```python
from wiki_fetch import (
    ConfluenceAPIError,           # Base exception
    ConfluenceAuthenticationError, # 401, 403 errors
    ConfluenceNotFoundError,      # 404 errors
    ConfluenceRateLimitError,     # 429 errors
    ConfluenceServerError         # 5xx errors
)

try:
    page = api.get_page_by_id("123456")
except ConfluenceAuthenticationError:
    print("Check your credentials")
except ConfluenceNotFoundError:
    print("Page doesn't exist")
except ConfluenceRateLimitError:
    print("Rate limit exceeded - the client will automatically retry")
except ConfluenceServerError:
    print("Server error - the client will automatically retry")
except ConfluenceAPIError as e:
    print(f"Other API error: {e}")
```

## Testing

### Unit Tests

Run the unit tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Integration Tests

Integration tests run against a real Confluence instance and are disabled by default.

To enable integration tests:
1. Set up your environment variables with valid credentials
2. Set `CONFLUENCE_INTEGRATION_TESTS=true`
3. Run: `pytest -m integration`

To run only unit tests (skip integration):
```bash
pytest -m "not integration"
```

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `CONFLUENCE_BASE_URL` | Required | Your Confluence base URL |
| `CONFLUENCE_USERNAME` | Required | Your email address |
| `CONFLUENCE_API_TOKEN` | Required | Your API token |
| `CONFLUENCE_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CONFLUENCE_RATE_LIMIT` | `2.0` | Requests per second |

## Logging

The client provides detailed logging with sensitive data masking:

- **Console logging**: Configurable level (INFO by default)
- **File logging**: Always DEBUG level to `confluence_api.log`
- **Sensitive data masking**: API tokens and usernames are masked in logs
- **Performance metrics**: Request timing and rate limit information

## Rate Limiting

The client implements rate limiting to prevent API abuse:

- Default: 2 requests per second
- Configurable via `CONFLUENCE_RATE_LIMIT` environment variable
- Automatic handling of 429 (Rate Limited) responses
- Respects `Retry-After` headers when provided

## Retry Mechanism

Automatic retry with exponential backoff for:

- Network errors (connection timeouts, DNS failures)
- Server errors (500, 502, 503, 504)
- Rate limit errors (429)

Retry configuration:
- **Max retries**: 3
- **Backoff factor**: 1.0 (1s, 2s, 4s delays)
- **No retry** for client errors (4xx except 429)

## Development

### Setting up development environment

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Install pre-commit hooks (optional):
```bash
pre-commit install
```

### Running tests

```bash
# All tests
pytest

# Unit tests only
pytest -m "not integration"

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_confluence_api.py
```

### Code quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Security Considerations

- **Never hardcode credentials** in source code
- **Use environment variables** for all sensitive configuration
- **API tokens are masked** in all log output
- **HTTPS is enforced** for all API communications
- **Credentials are validated** on initialization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release with secure credential management
- Retry mechanism with exponential backoff
- Rate limiting support
- Comprehensive error handling
- Full test coverage
- Type hints and documentation