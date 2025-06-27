# msgraph_adapter.py - Microsoft Graph API Adapter

This module provides an adapter for Microsoft Graph API, allowing existing code to work with the new Microsoft Graph API connection manager.

## Classes

### MSGraphAdapter

Adapter for Microsoft Graph API. This class provides methods that mimic the interface of the Neo4jManager, allowing existing code to work with Microsoft Graph API.

#### Constructor

```python
def __init__(self, connection_manager: Optional[MSGraphConnectionManager] = None,
             tenant_id: str = None, client_id: str = None, client_secret: str = None,
             auth_method: str = "device_code", config_file: str = None)
```

**Parameters:**
- `connection_manager` (MSGraphConnectionManager, optional): An existing MSGraphConnectionManager instance.
- `tenant_id` (str, optional): The tenant ID for the Microsoft 365 account.
- `client_id` (str, optional): The client ID for the application.
- `client_secret` (str, optional): The client secret for the application.
- `auth_method` (str, optional): The authentication method to use. Defaults to "device_code".
- `config_file` (str, optional): Path to a configuration file containing authentication details.

#### Methods

##### connect

```python
def connect(self) -> bool
```

Connect to Microsoft Graph API.

**Returns:**
- True if connection is successful, False otherwise.

##### close

```python
def close(self) -> None
```

Close the connection to Microsoft Graph API.

##### is_connected

```python
def is_connected(self) -> bool
```

Check if connected to Microsoft Graph API.

**Returns:**
- True if connected, False otherwise.

##### execute_query

```python
def execute_query(self, resource_path: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
```

Execute a query against Microsoft Graph API.

**Parameters:**
- `resource_path` (str): The resource path to query (e.g., '/me', '/users').
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- The response from Microsoft Graph API as a dictionary.

##### query_to_dataframe

```python
def query_to_dataframe(self, resource_path: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Execute a query and return results as a pandas DataFrame.

**Parameters:**
- `resource_path` (str): The resource path to query (e.g., '/me', '/users').
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing the query results.

##### get_users

```python
def get_users(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Get users from Microsoft Graph API.

**Parameters:**
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing user information.

##### get_groups

```python
def get_groups(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Get groups from Microsoft Graph API.

**Parameters:**
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing group information.

##### get_me

```python
def get_me(self) -> Dict[str, Any]
```

Get information about the current user.

**Returns:**
- A dictionary containing information about the current user.

##### get_my_messages

```python
def get_my_messages(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Get messages for the current user.

**Parameters:**
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing message information.

##### get_my_events

```python
def get_my_events(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Get calendar events for the current user.

**Parameters:**
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing event information.

##### get_my_files

```python
def get_my_files(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame
```

Get files for the current user.

**Parameters:**
- `parameters` (Dict[str, Any], optional): Optional query parameters.

**Returns:**
- A pandas DataFrame containing file information.

##### fetch_labels

```python
def fetch_labels(self) -> List[str]
```

Fetch available labels (entity types) from Microsoft Graph API.

**Returns:**
- A list of available entity types.

##### fetch_node_properties

```python
def fetch_node_properties(self, label: str) -> List[str]
```

Fetch properties for a given entity type.

**Parameters:**
- `label` (str): The entity type to fetch properties for.

**Returns:**
- A list of property names.

##### fetch_nodes

```python
def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, limit: int = 100) -> pd.DataFrame
```

Fetch nodes of a given type.

**Parameters:**
- `label` (str): The entity type to fetch.
- `properties` (List[str], optional): Optional list of properties to include.
- `limit` (int, optional): Maximum number of nodes to return. Defaults to 100.

**Returns:**
- A pandas DataFrame containing the nodes.

## Examples

### Basic Usage

```python
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter

# Create an adapter
adapter = MSGraphAdapter(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Connect to Microsoft Graph API
if adapter.connect():
    print("Connected to Microsoft Graph API")
    
    # Get information about the current user
    me = adapter.get_me()
    print(f"Hello, {me.get('displayName', 'User')}")
    
    # Get users
    users = adapter.get_users({"top": 10})
    print(f"Found {len(users)} users")
    
    # Get groups
    groups = adapter.get_groups({"top": 10})
    print(f"Found {len(groups)} groups")
```

### Using with Existing Neo4j-Compatible Code

```python
# Code that expects a Neo4jManager
def process_users(db_manager):
    # Get available labels
    labels = db_manager.fetch_labels()
    print(f"Available labels: {labels}")
    
    # Get properties for User label
    user_properties = db_manager.fetch_node_properties("User")
    print(f"User properties: {user_properties}")
    
    # Fetch User nodes
    users = db_manager.fetch_nodes("User", limit=10)
    print(f"Found {len(users)} users")
    
    return users

# Create an adapter
adapter = MSGraphAdapter(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Connect to Microsoft Graph API
adapter.connect()

# Use the adapter with existing code
users = process_users(adapter)
```

### Using with an Existing Connection Manager

```python
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager

# Create a connection manager
connection_manager = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Connect to Microsoft Graph API
connection_manager.connect()

# Create an adapter using the existing connection manager
adapter = MSGraphAdapter(connection_manager=connection_manager)

# Use the adapter
users = adapter.get_users({"top": 10})
```