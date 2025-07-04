# RESTful API Integration Guide

## Overview

The Science Data Kit (SDK) provides a RESTful API connector that allows you to connect to various RESTful web services. This guide explains how to configure and use the RESTful API connector to interact with external APIs.

## Configuration

To use the RESTful API connector, you need to create a configuration dictionary with the necessary connection parameters.

### Required Configuration Parameters

- `base_url`: Base URL for the API (e.g., "https://api.example.com")

### Optional Configuration Parameters

- `auth_type`: Authentication type ('none', 'basic', 'token', 'oauth2', 'api_key')
- `auth_params`: Authentication parameters (depends on auth_type)
- `headers`: Default headers to include in all requests
- `timeout`: Request timeout in seconds (default: 30)
- `verify_ssl`: Whether to verify SSL certificates (default: True)
- `proxies`: Proxy configuration
- `rate_limit`: Maximum requests per minute (0 for no limit)
- `health_endpoint`: Endpoint to use for health checks

### Authentication Configuration

#### No Authentication

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'none'
}
```

#### Basic Authentication

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'basic',
    'auth_params': {
        'username': 'myuser',
        'password': 'mypassword'
    }
}
```

#### Token Authentication

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'token',
    'auth_params': {
        'token': 'my-access-token',
        'token_type': 'Bearer'  # default is 'Bearer'
    }
}
```

#### API Key Authentication

For API key in header:

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'api_key',
    'auth_params': {
        'api_key': 'my-api-key',
        'api_key_name': 'X-API-Key',  # name of the header or query parameter
        'api_key_location': 'header'  # 'header' or 'query'
    }
}
```

For API key in query parameter:

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'api_key',
    'auth_params': {
        'api_key': 'my-api-key',
        'api_key_name': 'api_key',  # name of the header or query parameter
        'api_key_location': 'query'  # 'header' or 'query'
    }
}
```

#### OAuth2 Authentication

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'oauth2',
    'auth_params': {
        'access_token': 'my-oauth2-access-token'
    }
}
```

### Additional Configuration

```python
config = {
    'base_url': 'https://api.example.com',
    'auth_type': 'token',
    'auth_params': {
        'token': 'my-access-token'
    },
    'headers': {
        'Accept': 'application/json',
        'User-Agent': 'Science Data Kit/1.0'
    },
    'timeout': 60,  # 60 seconds
    'verify_ssl': True,
    'rate_limit': 100,  # 100 requests per minute
    'health_endpoint': '/health'
}
```

## Usage

### Creating a RESTful API Provider

To create a RESTful API provider, you need to use the provider registry:

```python
from science_data_kit.core.providers.registry import registry, ProviderType

# Create the provider
api_provider = registry.create_provider(
    provider_type=ProviderType.API,
    name='restful_api',
    config=config
)

# Initialize the provider
await api_provider.initialize()
```

### Making HTTP Requests

#### GET Request

```python
# Simple GET request
response = await api_provider.get('/users')

# GET request with query parameters
response = await api_provider.get(
    '/users',
    params={'page': 1, 'limit': 10}
)

# GET request with custom headers
response = await api_provider.get(
    '/users',
    headers={'X-Custom-Header': 'value'}
)
```

#### POST Request

```python
# POST request with JSON data
response = await api_provider.post(
    '/users',
    json_data={'name': 'John Doe', 'email': 'john@example.com'}
)

# POST request with form data
response = await api_provider.post(
    '/users',
    data={'name': 'John Doe', 'email': 'john@example.com'}
)

# POST request with query parameters
response = await api_provider.post(
    '/users',
    params={'token': 'abc123'},
    json_data={'name': 'John Doe'}
)
```

#### PUT Request

```python
# PUT request
response = await api_provider.put(
    '/users/123',
    json_data={'name': 'John Doe', 'email': 'john@example.com'}
)
```

#### PATCH Request

```python
# PATCH request
response = await api_provider.patch(
    '/users/123',
    json_data={'email': 'new.email@example.com'}
)
```

#### DELETE Request

```python
# DELETE request
response = await api_provider.delete('/users/123')
```

### Generic Request Method

For more control, you can use the generic request method:

```python
response = await api_provider.request(
    method='GET',
    endpoint='/users',
    params={'page': 1},
    headers={'X-Custom-Header': 'value'},
    data=None,
    json_data=None
)
```

### Handling Response Data

The response from the API provider is a dictionary containing the parsed response data. The format depends on the content type of the response:

- JSON responses are parsed into Python dictionaries/lists
- XML, CSV, and other formats are returned as text with a format indicator

```python
# Get JSON response
response = await api_provider.get('/users')
print(f"User count: {len(response['users'])}")

# Handle different response formats
response = await api_provider.get('/data.csv')
if isinstance(response, dict) and response.get('format') == 'csv':
    # Convert CSV to DataFrame
    df = await api_provider.to_dataframe(response)
    print(df.head())
```

### Converting Response to DataFrame

You can convert API responses to pandas DataFrames:

```python
# Convert JSON response to DataFrame
response = await api_provider.get('/users')
df = await api_provider.to_dataframe(response)

# Convert JSON response with nested data to DataFrame
response = await api_provider.get('/users')
df = await api_provider.to_dataframe(response, path='data.users')
```

### Paginated Requests

For APIs that return paginated results, you can use the paginated_request method:

```python
# Page-based pagination
all_items = await api_provider.paginated_request(
    method='GET',
    endpoint='/users',
    pagination_type='page',
    page_param='page',
    limit_param='limit',
    items_path='data',
    max_pages=10,
    page_size=100
)

# Offset-based pagination
all_items = await api_provider.paginated_request(
    method='GET',
    endpoint='/users',
    pagination_type='offset',
    offset_param='offset',
    limit_param='limit',
    items_path='data',
    max_pages=10,
    page_size=100
)

# Cursor-based pagination
all_items = await api_provider.paginated_request(
    method='GET',
    endpoint='/users',
    pagination_type='cursor',
    next_page_param='meta.next_cursor',
    items_path='data',
    max_pages=10,
    page_size=100
)
```

## Error Handling

The RESTful API provider methods raise exceptions when errors occur. You should wrap your code in try-except blocks to handle these exceptions:

```python
try:
    response = await api_provider.get('/non-existent-endpoint')
except Exception as e:
    print(f"An error occurred: {str(e)}")
```

## Rate Limiting

The RESTful API provider includes built-in rate limiting to prevent exceeding API rate limits:

```python
# Configure rate limiting (100 requests per minute)
config = {
    'base_url': 'https://api.example.com',
    'rate_limit': 100
}

# The provider will automatically add delays if necessary to stay within the rate limit
```

## Resource Cleanup

When you're done with the provider, close it to release resources:

```python
# Close the provider when done
await api_provider.close()
```

## Best Practices

1. **Authentication**: Use the appropriate authentication method for the API you're connecting to.

2. **Error Handling**: Always wrap API calls in try-except blocks to handle errors gracefully.

3. **Rate Limiting**: Set appropriate rate limits to avoid being blocked by the API provider.

4. **Pagination**: Use the paginated_request method for APIs that return large result sets.

5. **Resource Cleanup**: Always close the provider when you're done with it to release resources.

6. **SSL Verification**: Keep SSL verification enabled in production for security.

7. **Timeouts**: Set appropriate timeouts to prevent your application from hanging if the API is slow to respond.

## Supported Features

The RESTful API provider supports the following features:

- HTTP methods: GET, POST, PUT, PATCH, DELETE
- Authentication: None, Basic, Token, API Key, OAuth2
- Content types: JSON, XML, CSV, Text
- Rate limiting
- Pagination: Page-based, Offset-based, Cursor-based
- SSL verification
- Custom headers
- Proxy configuration
- Timeouts
- Response parsing
- DataFrame conversion

## Dependencies

The RESTful API provider requires the following dependencies:

- aiohttp: For making asynchronous HTTP requests
- pandas: For DataFrame conversion