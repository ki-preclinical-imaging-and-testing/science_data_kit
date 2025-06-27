# msgraph_utils.py - Microsoft Graph API Utility Functions

This module provides utility functions for working with Microsoft Graph API, including data transformation, visualization, and data extraction.

## Functions

### msgraph_to_network

```python
def msgraph_to_network(data: Dict[str, Any], entity_type: str) -> nx.Graph
```

Convert Microsoft Graph API response to a NetworkX graph.

**Parameters:**
- `data` (Dict[str, Any]): The response data from Microsoft Graph API.
- `entity_type` (str): The type of entity in the data (e.g., 'users', 'groups').

**Returns:**
- A NetworkX graph representing the data.

### save_msgraph_response

```python
def save_msgraph_response(data: Dict[str, Any], file_path: str) -> None
```

Save Microsoft Graph API response to a file.

**Parameters:**
- `data` (Dict[str, Any]): The response data from Microsoft Graph API.
- `file_path` (str): The path to save the data to.

**Raises:**
- `IOError`: If there is an error writing to the file.

### load_msgraph_response

```python
def load_msgraph_response(file_path: str) -> Dict[str, Any]
```

Load Microsoft Graph API response from a file.

**Parameters:**
- `file_path` (str): The path to load the data from.

**Returns:**
- The response data from Microsoft Graph API.

**Raises:**
- `FileNotFoundError`: If the file does not exist.
- `IOError`: If there is an error reading the file.
- `json.JSONDecodeError`: If the file contains invalid JSON.

### extract_user_data

```python
def extract_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]
```

Extract relevant user data from Microsoft Graph API response.

**Parameters:**
- `user_data` (Dict[str, Any]): The user data from Microsoft Graph API.

**Returns:**
- A dictionary containing relevant user data.

### extract_group_data

```python
def extract_group_data(group_data: Dict[str, Any]) -> Dict[str, Any]
```

Extract relevant group data from Microsoft Graph API response.

**Parameters:**
- `group_data` (Dict[str, Any]): The group data from Microsoft Graph API.

**Returns:**
- A dictionary containing relevant group data.

### extract_message_data

```python
def extract_message_data(message_data: Dict[str, Any]) -> Dict[str, Any]
```

Extract relevant message data from Microsoft Graph API response.

**Parameters:**
- `message_data` (Dict[str, Any]): The message data from Microsoft Graph API.

**Returns:**
- A dictionary containing relevant message data.

## Examples

### Converting API Response to a NetworkX Graph

```python
import networkx as nx
import matplotlib.pyplot as plt
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.utils.msgraph_utils import msgraph_to_network

# Create a connection manager
manager = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    auth_method="device_code"
)

# Connect to Microsoft Graph API
manager.connect()

# Get users
users_response = manager.execute_query("/users")

# Convert to a NetworkX graph
users_graph = msgraph_to_network(users_response, "users")

# Visualize the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(users_graph)
nx.draw(users_graph, pos, with_labels=True, node_color="lightblue", node_size=1500, font_size=10)
plt.title("User Network")
plt.show()
```

### Saving and Loading API Responses

```python
from science_data_kit.core.utils.msgraph_utils import save_msgraph_response, load_msgraph_response

# Save API response to a file
save_msgraph_response(users_response, "users_response.json")

# Load API response from a file
loaded_response = load_msgraph_response("users_response.json")
```

### Extracting Data from API Responses

```python
from science_data_kit.core.utils.msgraph_utils import extract_user_data, extract_group_data, extract_message_data

# Get a user
user_response = manager.execute_query("/users/user-id")

# Extract user data
user_data = extract_user_data(user_response)
print(f"User: {user_data['display_name']}")
print(f"Email: {user_data['email']}")
print(f"Department: {user_data['department']}")

# Get a group
group_response = manager.execute_query("/groups/group-id")

# Extract group data
group_data = extract_group_data(group_response)
print(f"Group: {group_data['display_name']}")
print(f"Description: {group_data['description']}")
print(f"Email: {group_data['mail']}")

# Get a message
message_response = manager.execute_query("/me/messages/message-id")

# Extract message data
message_data = extract_message_data(message_response)
print(f"Subject: {message_data['subject']}")
print(f"From: {message_data['from_email']}")
print(f"To: {', '.join(message_data['to_recipients'])}")
```