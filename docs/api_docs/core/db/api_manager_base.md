# api_manager_base.py - Base API Manager

This module provides a base class for API connection managers, defining common patterns and standardizing error handling across different API integrations.

## Exception Classes

### APIError

Base exception class for API-related errors.

### ConnectionError

Exception raised when there is an error connecting to the API.

### AuthenticationError

Exception raised when there is an authentication error.

### QueryError

Exception raised when there is an error executing a query.

### ConfigurationError

Exception raised when there is an error in the configuration.

## Classes

### CacheableMixin

Mixin that provides caching functionality for API responses.

#### Constructor

```python
def __init__(self, enable_cache: bool = True, cache_ttl: int = 300)
```

**Parameters:**
- `enable_cache` (bool, optional): Whether to enable caching of API responses. Defaults to True.
- `cache_ttl` (int, optional): Time-to-live for cached responses in seconds. Defaults to 300 (5 minutes).

#### Methods

##### _get_cache_key

```python
def _get_cache_key(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None) -> str
```

Generate a cache key for a query.

**Parameters:**
- `resource_path` (str): The resource path to query.
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A string that can be used as a cache key.

##### _is_cache_valid

```python
def _is_cache_valid(self, cache_key: str) -> bool
```

Check if a cached response is still valid.

**Parameters:**
- `cache_key` (str): The cache key to check.

**Returns:**
- True if the cached response is valid, False otherwise.

##### _get_from_cache

```python
def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]
```

Get a response from the cache.

**Parameters:**
- `cache_key` (str): The cache key to retrieve.

**Returns:**
- The cached response, or None if the cache is invalid.

##### _store_in_cache

```python
def _store_in_cache(self, cache_key: str, response: Dict[str, Any]) -> None
```

Store a response in the cache.

**Parameters:**
- `cache_key` (str): The cache key to store.
- `response` (Dict[str, Any]): The response to cache.

##### clear_cache

```python
def clear_cache(self) -> None
```

Clear the cache.

### ConfigurableMixin

Mixin that provides configuration loading functionality.

#### Methods

##### _load_config

```python
def _load_config(self, config_file: str) -> Dict[str, Any]
```

Load configuration from a file.

**Parameters:**
- `config_file` (str): Path to the configuration file.

**Returns:**
- The configuration as a dictionary.

**Raises:**
- `ConfigurationError`: If there is an error loading the configuration.

### APIManagerBase

Base class for API connection managers. This class defines the common interface and functionality for all API connection managers.

#### Constructor

```python
def __init__(self, config_file: str = None, enable_cache: bool = True, cache_ttl: int = 300)
```

**Parameters:**
- `config_file` (str, optional): Path to a configuration file containing authentication details.
- `enable_cache` (bool, optional): Whether to enable caching of API responses. Defaults to True.
- `cache_ttl` (int, optional): Time-to-live for cached responses in seconds. Defaults to 300 (5 minutes).

#### Methods

##### connect

```python
@abstractmethod
def connect(self) -> bool
```

Connect to the API.

**Returns:**
- True if connection is successful, False otherwise.

**Raises:**
- `ConnectionError`: If there is an error connecting to the API.
- `AuthenticationError`: If there is an authentication error.

##### execute_query

```python
@abstractmethod
def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> Dict[str, Any]
```

Execute a query against the API.

**Parameters:**
- `resource_path` (str): The resource path to query.
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- The response from the API as a dictionary.

**Raises:**
- `ConnectionError`: If not connected to the API.
- `QueryError`: If there is an error executing the query.

##### build_query

```python
def build_query(self, resource_path: str, **kwargs) -> Dict[str, Any]
```

Build a query with parameters.

**Parameters:**
- `resource_path` (str): The resource path to query.
- `**kwargs`: Query parameters.

**Returns:**
- A dictionary containing the query parameters.

## Examples

### Creating a Custom API Manager

```python
from science_data_kit.core.db.api_manager_base import APIManagerBase, ConnectionError, QueryError

class MyAPIManager(APIManagerBase):
    def __init__(self, config_file=None, enable_cache=True, cache_ttl=300):
        super().__init__(config_file, enable_cache, cache_ttl)
        self.api_client = None
    
    def connect(self) -> bool:
        try:
            # Initialize API client
            self.api_client = SomeAPIClient()
            self.connected = True
            return True
        except Exception as e:
            raise ConnectionError(f"Error connecting to API: {str(e)}")
    
    def execute_query(self, resource_path, query_parameters=None, use_cache=True):
        if not self.connected:
            raise ConnectionError("Not connected to API. Call connect() first.")
        
        # Check cache
        if use_cache and self.enable_cache:
            cache_key = self._get_cache_key(resource_path, query_parameters)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
        
        try:
            # Execute query
            response = self.api_client.get(resource_path, params=query_parameters)
            
            # Store in cache
            if use_cache and self.enable_cache:
                cache_key = self._get_cache_key(resource_path, query_parameters)
                self._store_in_cache(cache_key, response)
            
            return response
        except Exception as e:
            raise QueryError(f"Error executing query: {str(e)}")
```

### Using the Cache

```python
# Create an API manager with caching enabled
manager = MyAPIManager(enable_cache=True, cache_ttl=600)  # 10 minutes cache TTL

# Connect to the API
manager.connect()

# Execute a query (will be cached)
response1 = manager.execute_query("/users", {"limit": 10})

# Execute the same query again (will use cached response)
response2 = manager.execute_query("/users", {"limit": 10})

# Execute the query bypassing the cache
response3 = manager.execute_query("/users", {"limit": 10}, use_cache=False)

# Clear the cache
manager.clear_cache()
```

### Loading Configuration from a File

```python
# Create a configuration file (config.json)
# {
#   "api_key": "your-api-key",
#   "base_url": "https://api.example.com",
#   "timeout": 30
# }

# Create an API manager with configuration from file
manager = MyAPIManager(config_file="config.json")

# Access configuration values
api_key = manager.config.get("api_key")
base_url = manager.config.get("base_url")
```