# msgraph_manager.py - Microsoft Graph API Connection Manager

This module provides a connection manager for Microsoft Graph API, allowing the Science Data Kit to interact with Microsoft 365 services.

## Classes

### MSGraphConnectionManager

Connection manager for Microsoft Graph API. This class provides methods for authenticating with Microsoft Graph API and executing queries against it.

#### Constructor

```python
def __init__(self, tenant_id: str = None, client_id: str = None, client_secret: str = None,
             auth_method: str = "device_code", config_file: str = None, 
             enable_cache: bool = True, cache_ttl: int = 300)
```

**Parameters:**
- `tenant_id` (str, optional): The tenant ID for the Microsoft 365 account.
- `client_id` (str, optional): The client ID for the application.
- `client_secret` (str, optional): The client secret for the application.
- `auth_method` (str, optional): The authentication method to use. Options are:
  - "client_credentials": For daemon or service applications
  - "device_code": For command-line tools or IoT devices
  - "interactive": For web applications
  Defaults to "device_code".
- `config_file` (str, optional): Path to a configuration file containing authentication details.
- `enable_cache` (bool, optional): Whether to enable caching of API responses. Defaults to True.
- `cache_ttl` (int, optional): Time-to-live for cached responses in seconds. Defaults to 300 (5 minutes).

**Raises:**
- `ImportError`: If the Microsoft Graph SDK is not installed.

#### Methods

##### _load_config_values

```python
def _load_config_values(self, config_file: str) -> None
```

Load configuration values from a file.

**Parameters:**
- `config_file` (str): Path to the configuration file.

**Raises:**
- `ConfigurationError`: If there is an error loading the configuration.

##### connect

```python
def connect(self) -> bool
```

Connect to Microsoft Graph API.

**Returns:**
- True if connection is successful, False otherwise.

**Raises:**
- `AuthenticationError`: If there is an error with the authentication credentials.
- `ConnectionError`: If there is an error connecting to the API.

##### execute_query

```python
def execute_query(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None, 
              use_cache: bool = True) -> Dict[str, Any]
```

Execute a query against Microsoft Graph API.

**Parameters:**
- `resource_path` (str): The resource path to query (e.g., '/me', '/users').
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- The response from Microsoft Graph API as a dictionary.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### query_to_dataframe

```python
def query_to_dataframe(self, resource_path: str, query_parameters: Optional[Dict[str, Any]] = None,
                   use_cache: bool = True) -> pd.DataFrame
```

Execute a query and return results as a pandas DataFrame.

**Parameters:**
- `resource_path` (str): The resource path to query (e.g., '/me', '/users').
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing the query results.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_users

```python
def get_users(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame
```

Get users from Microsoft Graph API.

**Parameters:**
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing user information.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_groups

```python
def get_groups(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame
```

Get groups from Microsoft Graph API.

**Parameters:**
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing group information.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_me

```python
def get_me(self, use_cache: bool = True) -> Dict[str, Any]
```

Get information about the current user.

**Parameters:**
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A dictionary containing information about the current user.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_my_messages

```python
def get_my_messages(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame
```

Get messages for the current user.

**Parameters:**
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing message information.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_my_events

```python
def get_my_events(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame
```

Get calendar events for the current user.

**Parameters:**
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing event information.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

##### get_my_files

```python
def get_my_files(self, query_parameters: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> pd.DataFrame
```

Get files for the current user.

**Parameters:**
- `query_parameters` (Dict[str, Any], optional): Optional query parameters.
- `use_cache` (bool, optional): Whether to use the cache for this query. Defaults to True.

**Returns:**
- A pandas DataFrame containing file information.

**Raises:**
- `ConnectionError`: If not connected to Microsoft Graph API.
- `QueryError`: If there is an error executing the query.

## Examples

### Basic Usage

```python
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager

# Create a connection manager
manager = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Connect to Microsoft Graph API
if manager.connect():
    print("Connected to Microsoft Graph API")
    
    # Get information about the current user
    me = manager.get_me()
    print(f"Hello, {me.get('displayName', 'User')}")
    
    # Get users
    users = manager.get_users({"top": 10})
    print(f"Found {len(users)} users")
    
    # Get groups
    groups = manager.get_groups({"top": 10})
    print(f"Found {len(groups)} groups")
```

### Using Configuration File

```python
# Create a configuration file (msgraph_config.json)
# {
#   "tenant_id": "your-tenant-id",
#   "client_id": "your-client-id",
#   "auth_method": "device_code"
# }

# Create a connection manager with configuration from file
manager = MSGraphConnectionManager(config_file="msgraph_config.json")

# Connect to Microsoft Graph API
manager.connect()
```

### Using Caching

```python
# Create a connection manager with caching enabled
manager = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code",
    enable_cache=True,
    cache_ttl=600  # 10 minutes cache TTL
)

# Connect to Microsoft Graph API
manager.connect()

# Execute a query (will be cached)
response1 = manager.execute_query("/users", {"top": 10})

# Execute the same query again (will use cached response)
response2 = manager.execute_query("/users", {"top": 10})

# Execute the query bypassing the cache
response3 = manager.execute_query("/users", {"top": 10}, use_cache=False)

# Clear the cache
manager.clear_cache()
```

### Using Different Authentication Methods

```python
# Client Credentials (for daemon or service applications)
manager_client_credentials = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",
    auth_method="client_credentials"
)

# Device Code (for command-line tools or IoT devices)
manager_device_code = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Interactive (for web applications)
manager_interactive = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="interactive"
)
```