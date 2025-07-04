"""
RESTful API Provider for Science Data Kit

This module provides a provider for connecting to RESTful APIs, allowing
the Science Data Kit to interact with various RESTful web services.
"""

import json
import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple

from ...providers.registry import BaseProvider, ProviderType


class RESTfulAPIProvider(BaseProvider):
    """
    Provider for RESTful API connections.

    This class provides functionality for connecting to RESTful APIs and
    executing requests against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the RESTful API provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys:
                   - base_url: Base URL for the API
                   
                   Optional:
                   - auth_type: Authentication type ('none', 'basic', 'token', 'oauth2', 'api_key')
                   - auth_params: Authentication parameters (depends on auth_type)
                   - headers: Default headers to include in all requests
                   - timeout: Request timeout in seconds
                   - verify_ssl: Whether to verify SSL certificates
                   - proxies: Proxy configuration
                   - rate_limit: Maximum requests per minute
        """
        super().__init__(config)
        self.base_url = config.get('base_url', '').rstrip('/')
        self.auth_type = config.get('auth_type', 'none').lower()
        self.auth_params = config.get('auth_params', {})
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
        self.verify_ssl = config.get('verify_ssl', True)
        self.proxies = config.get('proxies', None)
        self.rate_limit = config.get('rate_limit', 0)
        self.session = None
        self.last_request_time = 0
        self.request_count = 0
        
    async def initialize(self) -> bool:
        """
        Initialize the RESTful API connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Validate base URL
            if not self.base_url:
                print("Base URL not provided")
                return False
            
            # Create aiohttp session
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Set up authentication
            if self.auth_type == 'basic':
                username = self.auth_params.get('username')
                password = self.auth_params.get('password')
                if not username or not password:
                    print("Missing username or password for basic authentication")
                    return False
                
                # Add basic auth to session
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    auth=aiohttp.BasicAuth(username, password)
                )
            
            elif self.auth_type == 'token':
                token = self.auth_params.get('token')
                token_type = self.auth_params.get('token_type', 'Bearer')
                if not token:
                    print("Missing token for token authentication")
                    return False
                
                # Add token to headers
                self.headers['Authorization'] = f"{token_type} {token}"
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            elif self.auth_type == 'api_key':
                api_key = self.auth_params.get('api_key')
                api_key_name = self.auth_params.get('api_key_name', 'api_key')
                api_key_location = self.auth_params.get('api_key_location', 'query')
                
                if not api_key:
                    print("Missing API key for API key authentication")
                    return False
                
                # For header-based API key
                if api_key_location == 'header':
                    self.headers[api_key_name] = api_key
                
                # For query-based API key, we'll add it during request
                
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            elif self.auth_type == 'oauth2':
                # OAuth2 is more complex and would typically require a separate flow
                # This is a simplified implementation
                token = self.auth_params.get('access_token')
                if not token:
                    print("Missing access token for OAuth2 authentication")
                    return False
                
                # Add token to headers
                self.headers['Authorization'] = f"Bearer {token}"
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            # Test connection with a health check
            health_check_result = await self.health_check()
            self.is_initialized = health_check_result
            return health_check_result
        
        except Exception as e:
            print(f"Error initializing RESTful API provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the API connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.base_url:
            return False
        
        try:
            # If a health check endpoint is specified, use it
            health_endpoint = self.config.get('health_endpoint')
            if health_endpoint:
                url = f"{self.base_url}{health_endpoint}"
                async with self.session.get(url, ssl=self.verify_ssl) as response:
                    return response.status < 400
            
            # Otherwise, just try to connect to the base URL
            async with self.session.get(self.base_url, ssl=self.verify_ssl) as response:
                return response.status < 400
        
        except Exception as e:
            print(f"API health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        return {
            "type": ProviderType.API.value,
            "name": "restful_api",
            "features": [
                "http_methods",
                "json_parsing",
                "authentication",
                "rate_limiting",
                "pagination"
            ],
            "supported_auth_methods": [
                "none",
                "basic",
                "token",
                "api_key",
                "oauth2"
            ],
            "supported_formats": [
                "json",
                "xml",
                "csv",
                "text"
            ]
        }
    
    async def _handle_rate_limit(self):
        """
        Handle rate limiting by adding delays if necessary.
        """
        if self.rate_limit <= 0:
            return
        
        # Calculate time since last request
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        # Reset counter if more than a minute has passed
        if time_since_last > 60:
            self.request_count = 0
            self.last_request_time = current_time
            return
        
        # Increment request counter
        self.request_count += 1
        
        # If we've hit the rate limit, sleep until the minute is up
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - time_since_last
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            self.request_count = 0
            self.last_request_time = asyncio.get_event_loop().time()
        else:
            self.last_request_time = current_time
    
    async def _prepare_request_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare request parameters, including API key if needed.
        
        Args:
            params: Original request parameters
            
        Returns:
            Updated request parameters
        """
        if params is None:
            params = {}
        
        # Add API key to query parameters if needed
        if self.auth_type == 'api_key' and self.auth_params.get('api_key_location') == 'query':
            api_key = self.auth_params.get('api_key')
            api_key_name = self.auth_params.get('api_key_name', 'api_key')
            if api_key:
                params[api_key_name] = api_key
        
        return params
    
    async def request(self, method: str, endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Any] = None,
                     headers: Optional[Dict[str, str]] = None,
                     json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Request body data
            headers: Additional headers for this request
            json_data: JSON data to send in the request body
            
        Returns:
            Response data as a dictionary
        """
        if not self.is_initialized or not self.session:
            raise Exception("RESTful API provider not initialized")
        
        try:
            # Handle rate limiting
            await self._handle_rate_limit()
            
            # Prepare URL
            url = f"{self.base_url}{endpoint}"
            
            # Prepare parameters
            params = await self._prepare_request_params(params)
            
            # Prepare headers
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Execute request
            async with self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                json=json_data,
                ssl=self.verify_ssl
            ) as response:
                # Check for successful response
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                # Parse response based on content type
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    return await response.json()
                elif 'application/xml' in content_type or 'text/xml' in content_type:
                    # For XML, return the raw text (would need additional parsing)
                    return {'content': await response.text(), 'format': 'xml'}
                elif 'text/csv' in content_type:
                    # For CSV, return the raw text (would need additional parsing)
                    return {'content': await response.text(), 'format': 'csv'}
                else:
                    # For other formats, return the raw text
                    return {'content': await response.text(), 'format': 'text'}
        
        except Exception as e:
            print(f"Error executing API request: {str(e)}")
            raise
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a GET request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            headers: Additional headers for this request
            
        Returns:
            Response data as a dictionary
        """
        return await self.request('GET', endpoint, params=params, headers=headers)
    
    async def post(self, endpoint: str, data: Optional[Any] = None,
                  params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a POST request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers for this request
            json_data: JSON data to send in the request body
            
        Returns:
            Response data as a dictionary
        """
        return await self.request('POST', endpoint, params=params, data=data, 
                                headers=headers, json_data=json_data)
    
    async def put(self, endpoint: str, data: Optional[Any] = None,
                 params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a PUT request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers for this request
            json_data: JSON data to send in the request body
            
        Returns:
            Response data as a dictionary
        """
        return await self.request('PUT', endpoint, params=params, data=data, 
                               headers=headers, json_data=json_data)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Execute a DELETE request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            headers: Additional headers for this request
            
        Returns:
            Response data as a dictionary
        """
        return await self.request('DELETE', endpoint, params=params, headers=headers)
    
    async def patch(self, endpoint: str, data: Optional[Any] = None,
                   params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a PATCH request to the API.
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers for this request
            json_data: JSON data to send in the request body
            
        Returns:
            Response data as a dictionary
        """
        return await self.request('PATCH', endpoint, params=params, data=data, 
                                headers=headers, json_data=json_data)
    
    async def to_dataframe(self, data: Dict[str, Any], path: Optional[str] = None) -> pd.DataFrame:
        """
        Convert API response data to a pandas DataFrame.
        
        Args:
            data: API response data
            path: JSON path to the data array (e.g., 'results.items')
            
        Returns:
            Pandas DataFrame containing the data
        """
        try:
            # Handle different response formats
            if isinstance(data, dict) and 'format' in data:
                if data['format'] == 'csv':
                    # Parse CSV data
                    import io
                    return pd.read_csv(io.StringIO(data['content']))
                elif data['format'] == 'xml':
                    # For XML, we would need additional parsing
                    # This is a simplified implementation
                    raise NotImplementedError("XML to DataFrame conversion not implemented")
                elif data['format'] == 'text':
                    # For plain text, return a single-column DataFrame
                    return pd.DataFrame({'content': [data['content']]})
            
            # For JSON data, extract the relevant part if path is provided
            if path:
                parts = path.split('.')
                current = data
                for part in parts:
                    if part in current:
                        current = current[part]
                    else:
                        raise ValueError(f"Path '{path}' not found in data")
                data = current
            
            # Convert to DataFrame
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a dictionary of lists with equal lengths, convert to DataFrame
                if all(isinstance(v, list) for v in data.values()) and len(set(len(v) for v in data.values())) == 1:
                    return pd.DataFrame(data)
                # Otherwise, convert to a single-row DataFrame
                return pd.DataFrame([data])
            else:
                raise ValueError("Data cannot be converted to DataFrame")
        
        except Exception as e:
            print(f"Error converting to DataFrame: {str(e)}")
            raise
    
    async def paginated_request(self, method: str, endpoint: str, 
                               params: Optional[Dict[str, Any]] = None,
                               data: Optional[Any] = None,
                               headers: Optional[Dict[str, str]] = None,
                               json_data: Optional[Dict[str, Any]] = None,
                               pagination_type: str = 'offset',
                               page_param: str = 'page',
                               limit_param: str = 'limit',
                               offset_param: str = 'offset',
                               next_page_param: str = 'next',
                               items_path: str = '',
                               max_pages: int = 10,
                               page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Execute a paginated request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Request body data
            headers: Additional headers for this request
            json_data: JSON data to send in the request body
            pagination_type: Type of pagination ('offset', 'page', 'cursor')
            page_param: Name of the page parameter for 'page' pagination
            limit_param: Name of the limit parameter
            offset_param: Name of the offset parameter for 'offset' pagination
            next_page_param: Path to the next page URL/token for 'cursor' pagination
            items_path: JSON path to the items array in the response
            max_pages: Maximum number of pages to retrieve
            page_size: Number of items per page
            
        Returns:
            List of all items from all pages
        """
        if not self.is_initialized or not self.session:
            raise Exception("RESTful API provider not initialized")
        
        all_items = []
        current_page = 1
        current_offset = 0
        next_cursor = None
        
        # Initialize parameters
        if params is None:
            params = {}
        
        try:
            while current_page <= max_pages:
                # Update pagination parameters based on pagination type
                request_params = params.copy()
                
                if pagination_type == 'page':
                    request_params[page_param] = current_page
                    request_params[limit_param] = page_size
                elif pagination_type == 'offset':
                    request_params[offset_param] = current_offset
                    request_params[limit_param] = page_size
                elif pagination_type == 'cursor' and next_cursor:
                    # For cursor-based pagination, we need the next cursor from the previous response
                    request_params['cursor'] = next_cursor
                
                # Execute request
                response = await self.request(
                    method=method,
                    endpoint=endpoint,
                    params=request_params,
                    data=data,
                    headers=headers,
                    json_data=json_data
                )
                
                # Extract items from response
                items = response
                if items_path:
                    parts = items_path.split('.')
                    for part in parts:
                        if part in items:
                            items = items[part]
                        else:
                            items = []
                            break
                
                # Add items to result
                if isinstance(items, list):
                    all_items.extend(items)
                else:
                    # If items is not a list, we've reached the end or there's an error
                    break
                
                # Check if we've reached the end
                if len(items) < page_size:
                    break
                
                # Update pagination parameters for next request
                if pagination_type == 'page':
                    current_page += 1
                elif pagination_type == 'offset':
                    current_offset += page_size
                elif pagination_type == 'cursor':
                    # Extract next cursor from response
                    next_cursor = None
                    cursor_path = next_page_param.split('.')
                    cursor_data = response
                    for part in cursor_path:
                        if part in cursor_data:
                            cursor_data = cursor_data[part]
                        else:
                            break
                    
                    if isinstance(cursor_data, str):
                        next_cursor = cursor_data
                    
                    # If no next cursor, we've reached the end
                    if not next_cursor:
                        break
            
            return all_items
        
        except Exception as e:
            print(f"Error executing paginated request: {str(e)}")
            raise
    
    async def close(self):
        """
        Close the API connection.
        """
        if self.session:
            await self.session.close()
            self.session = None
            self.is_initialized = False