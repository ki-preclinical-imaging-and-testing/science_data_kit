# Microsoft Graph API Usage Guide

## Overview

This guide provides instructions for using the Microsoft Graph API integration with the Science Data Kit (SDK). It covers how to query data, work with different data types, and create visualizations using the SDK's Microsoft Graph API integration.

## Prerequisites

Before using the Microsoft Graph API integration, ensure that:

1. You have set up and configured the Microsoft Graph API integration as described in the [Microsoft Graph API Setup Guide](msgraph_setup_guide.md)
2. You have successfully connected to Microsoft Graph API using one of the supported authentication methods
3. You have the necessary permissions to access the data you want to query

## Connecting to Microsoft Graph API

### Using the UI

1. Launch the SDK application
2. Navigate to the Microsoft Graph API connection page (from the sidebar or by going to `/msgraph_connect`)
3. Select the authentication method
4. Enter your tenant ID and client ID (and client secret if using client credentials flow)
5. Click **Connect to Microsoft Graph API**
6. Verify that the connection is successful by checking the connection status

### Using the API

You can also connect to Microsoft Graph API programmatically:

```python
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter

# Create a connection manager
connection_manager = MSGraphConnectionManager(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",  # Only for client_credentials flow
    auth_method="client_credentials"  # Or "device_code" or "interactive"
)

# Connect to Microsoft Graph API
if connection_manager.connect():
    print("Connected to Microsoft Graph API")
    
    # Create an adapter (optional, for compatibility with existing code)
    adapter = MSGraphAdapter(connection_manager=connection_manager)
else:
    print("Failed to connect to Microsoft Graph API")
```

## Querying Data

### Using the Explorer Page

The SDK provides a Microsoft Graph API Explorer page that allows you to:

1. Browse available Microsoft Graph API endpoints
2. Execute queries against Microsoft Graph API
3. View and export results
4. Create visualizations of the results

To use the Explorer page:

1. Navigate to the Microsoft Graph API Explorer page (from the sidebar or by going to `/msgraph_explore`)
2. Select a sample query or enter a custom resource path (e.g., `/me`, `/users`, `/groups`)
3. Configure query parameters (select, filter, expand, orderby, top, skip)
4. Click **Execute Query**
5. View the results in the **Results** tab
6. Create visualizations in the **Visualization** tab

### Using the API

You can also query Microsoft Graph API programmatically:

```python
# Using the connection manager
users = connection_manager.get_users()  # Returns a pandas DataFrame
groups = connection_manager.get_groups()
me = connection_manager.get_me()  # Returns a dictionary
my_messages = connection_manager.get_my_messages()
my_events = connection_manager.get_my_events()
my_files = connection_manager.get_my_files()

# Custom queries
response = connection_manager.execute_query('/users', {'top': 10})  # Returns a dictionary
df = connection_manager.query_to_dataframe('/users', {'top': 10})  # Returns a pandas DataFrame

# Using the adapter (for compatibility with existing code)
users = adapter.get_users()
groups = adapter.get_groups()
me = adapter.get_me()
```

## Working with Different Data Types

### Users and Groups

```python
# Get users
users = connection_manager.get_users()

# Get a specific user
user = connection_manager.execute_query(f'/users/{user_id}')

# Get groups
groups = connection_manager.get_groups()

# Get a specific group
group = connection_manager.execute_query(f'/groups/{group_id}')

# Get members of a group
group_members = connection_manager.query_to_dataframe(f'/groups/{group_id}/members')
```

### Messages and Calendar Events

```python
# Get messages
messages = connection_manager.get_my_messages()

# Get messages with specific filter
filtered_messages = connection_manager.query_to_dataframe('/me/messages', {
    'filter': "receivedDateTime ge 2023-01-01",
    'top': 50
})

# Get calendar events
events = connection_manager.get_my_events()

# Get events in a specific time range
filtered_events = connection_manager.query_to_dataframe('/me/events', {
    'filter': "start/dateTime ge '2023-01-01T00:00:00Z' and end/dateTime le '2023-12-31T23:59:59Z'",
    'top': 50
})
```

### Files and Folders

```python
# Get files in root folder
files = connection_manager.get_my_files()

# Get files in a specific folder
folder_id = "your-folder-id"
folder_files = connection_manager.query_to_dataframe(f'/me/drive/items/{folder_id}/children')

# Get file content
file_id = "your-file-id"
file_content = connection_manager.execute_query(f'/me/drive/items/{file_id}/content')
```

## Creating Visualizations

The SDK provides several visualization components for Microsoft Graph API data:

### Organizational Charts

```python
from science_data_kit.ui.components.msgraph_visualizations import render_organizational_chart

# Get users with manager information
users_df = connection_manager.query_to_dataframe('/users', {
    'select': 'id,displayName,jobTitle,department,manager',
    'expand': 'manager'
})

# Render organizational chart
render_organizational_chart(users_df, manager_column='manager')
```

### Communication Networks

```python
from science_data_kit.ui.components.msgraph_visualizations import render_communication_network

# Get messages
messages_df = connection_manager.get_my_messages()

# Render communication network
render_communication_network(messages_df)
```

### Document Collaboration Graphs

```python
from science_data_kit.ui.components.msgraph_visualizations import render_document_collaboration_graph

# Get files
files_df = connection_manager.get_my_files()

# Get users
users_df = connection_manager.get_users()

# Render document collaboration graph
render_document_collaboration_graph(files_df, users_df)
```

## Integrating with Other Data Sources

The SDK allows you to integrate Microsoft Graph API data with other data sources, such as Neo4j:

```python
from science_data_kit.core.db.db_factory import DatabaseFactory

# Create Neo4j connection
neo4j_connection = DatabaseFactory.create_connection("neo4j", {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "password",
    "database": "neo4j"
})

# Create Microsoft Graph API connection
msgraph_connection = DatabaseFactory.create_connection("msgraph", {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "auth_method": "client_credentials"
})

# Get data from Neo4j
neo4j_data = neo4j_connection.query_to_dataframe("MATCH (n:Person) RETURN n.name, n.email")

# Get data from Microsoft Graph API
msgraph_data = msgraph_connection.get_users()

# Combine data
combined_data = pd.merge(neo4j_data, msgraph_data, left_on="n.email", right_on="mail")
```

## Best Practices

### Handling Large Datasets

When working with large datasets, consider:

1. Using pagination to retrieve data in chunks
2. Filtering data on the server side using the `filter` parameter
3. Selecting only the fields you need using the `select` parameter

Example:

```python
# Retrieve data in chunks
page_size = 100
skip = 0
all_users = []

while True:
    users_page = connection_manager.query_to_dataframe('/users', {
        'select': 'id,displayName,mail',
        'top': page_size,
        'skip': skip
    })
    
    if users_page.empty:
        break
    
    all_users.append(users_page)
    skip += page_size

# Combine all pages
all_users_df = pd.concat(all_users, ignore_index=True)
```

### Error Handling

Always handle errors when working with Microsoft Graph API:

```python
try:
    response = connection_manager.execute_query('/users')
except Exception as e:
    print(f"Error executing query: {str(e)}")
    # Handle the error appropriately
```

### Caching Results

For better performance, consider caching results:

```python
import os
import json
from science_data_kit.core.utils.msgraph_utils import save_msgraph_response, load_msgraph_response

# Define cache file path
cache_file = "users_cache.json"

# Check if cache exists and is recent
if os.path.exists(cache_file) and (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))).days < 1:
    # Load from cache
    response = load_msgraph_response(cache_file)
else:
    # Fetch from API and save to cache
    response = connection_manager.execute_query('/users')
    save_msgraph_response(response, cache_file)
```

## Troubleshooting

### Common Issues

1. **Query Failed**: Ensure that the resource path is correct and that you have the necessary permissions.
2. **Data Not Available**: Check that the data exists and that you have the necessary permissions to access it.
3. **Rate Limiting**: Microsoft Graph API has rate limits. If you're making too many requests, you may be rate limited.

### Checking Query Parameters

If you're experiencing issues with queries, check the query parameters:

1. Ensure that the resource path is correct (e.g., `/users`, `/groups`, `/me/messages`)
2. Ensure that the query parameters are correctly formatted (e.g., `filter`, `select`, `expand`)
3. Check the documentation for the specific endpoint you're querying

### Logging

Enable logging to troubleshoot issues:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("msgraph")

# Log query information
logger.debug(f"Executing query: {resource_path} with parameters: {query_parameters}")
```

## Next Steps

After mastering the basics of the Microsoft Graph API integration, you can:

1. Explore more advanced queries and data analysis techniques
2. Create custom visualizations for your specific needs
3. Integrate Microsoft Graph API data with other data sources in your organization

For more information, see the [Microsoft Graph API documentation](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0).