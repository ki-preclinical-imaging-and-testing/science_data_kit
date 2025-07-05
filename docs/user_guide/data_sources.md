# Data Sources Guide

## Overview

The Science Data Kit provides robust data source connectors, allowing you to access data from various external systems and local storage. This guide explains how to use these connectors effectively.

## Table of Contents

1. [Introduction](#introduction)
2. [Office 365 Connector](#office-365-connector)
3. [Dropbox Connector](#dropbox-connector)
4. [Google Drive Connector](#google-drive-connector)
5. [Google Sheets Connector](#google-sheets-connector)
6. [Local Storage Connector](#local-storage-connector)
7. [Common Operations](#common-operations)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

Data source connectors are a core feature of the Science Data Kit that allow you to access data from various external systems and local storage. The SDK currently supports the following data sources:

- **Office 365**: Access data from Microsoft 365 services, including OneDrive, Excel, and SharePoint.
- **Dropbox**: Access CSV and Excel files stored in Dropbox.
- **Google Drive**: Access CSV and Excel files stored in Google Drive, with special handling for Google Sheets.
- **Local Storage**: Access CSV and Excel files stored on the local file system or network mountpoints.

All data source connectors follow a common interface, making it easy to switch between different data sources or use multiple data sources simultaneously.

## Office 365 Connector

The Office 365 connector allows you to access data from Microsoft 365 services, including OneDrive, Excel, and SharePoint.

### Configuration

To use the Office 365 connector, you need to provide the following configuration:

```python
from science_data_kit.core.providers.api import MSGraphProvider

# Create configuration
config = {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "auth_method": "device_code",  # or "client_credentials" or "interactive"
    "enable_cache": True,
    "cache_ttl": 300  # Cache time-to-live in seconds
}

# Create provider
provider = MSGraphProvider(config)

# Initialize provider
await provider.initialize()
```

### Authentication Methods

The Office 365 connector supports the following authentication methods:

- **device_code**: Authenticate using a device code flow, which is useful for applications without a user interface.
- **client_credentials**: Authenticate using client credentials, which is useful for server-to-server scenarios.
- **interactive**: Authenticate using an interactive flow, which is useful for applications with a user interface.

### File Operations

#### Listing Files

You can list files available in OneDrive as follows:

```python
# List files
files = await provider.list_files()

# Print file names
for file in files:
    print(f"File: {file['name']} ({file['type']})")
```

#### Downloading File Data

You can download and parse file data as follows:

```python
# Download file data
file_id = "your-file-id"
data = await provider.download_file_data(file_id)

# Print data
print(data.head())
```

### Excel Operations

#### Listing Spreadsheets

You can list available Excel spreadsheets as follows:

```python
# List spreadsheets
spreadsheets = await provider.list_spreadsheets()

# Print spreadsheet names
for spreadsheet in spreadsheets:
    print(f"Spreadsheet: {spreadsheet['name']}")
```

#### Listing Sheets

You can list sheets in an Excel spreadsheet as follows:

```python
# List sheets
spreadsheet_id = "your-spreadsheet-id"
sheets = await provider.list_sheets(spreadsheet_id)

# Print sheet names
for sheet in sheets:
    print(f"Sheet: {sheet['name']} ({sheet['rows']} rows, {sheet['columns']} columns)")
```

#### Getting Sheet Data

You can get data from a sheet in an Excel spreadsheet as follows:

```python
# Get sheet data
spreadsheet_id = "your-spreadsheet-id"
sheet_name = "your-sheet-name"
data = await provider.get_sheet_data(spreadsheet_id, sheet_name)

# Print data
print(data.head())
```

## Dropbox Connector

The Dropbox connector allows you to access CSV and Excel files stored in Dropbox.

### Configuration

To use the Dropbox connector, you need to provide the following configuration:

```python
from science_data_kit.core.providers.storage import DropboxProvider

# Create configuration
config = {
    "access_token": "your-dropbox-access-token"
}

# Create provider
provider = DropboxProvider(config)

# Initialize provider
await provider.initialize()
```

### File Operations

#### Listing Files

You can list CSV/Excel files in a Dropbox folder as follows:

```python
# List files in a folder
folder_path = "your-folder-path"  # e.g., "/Documents"
files = await provider.list_files(folder_path)

# Print file names
for file in files:
    print(f"File: {file['name']} ({file['type']})")
```

#### Downloading File Data

You can download and parse file data as follows:

```python
# Download file data
file_path = "your-file-path"  # e.g., "/Documents/data.csv"
data = await provider.download_file_data(file_path)

# Print data
print(data.head())
```

#### Getting File Information

You can get file metadata without downloading as follows:

```python
# Get file information
file_path = "your-file-path"  # e.g., "/Documents/data.csv"
file_info = await provider.get_file_info(file_path)

# Print file information
print(f"File: {file_info['name']}")
print(f"Size: {file_info['size']} bytes")
print(f"Modified: {file_info['modified']}")
```

## Google Drive Connector

The Google Drive connector allows you to access CSV and Excel files stored in Google Drive, with special handling for Google Sheets.

### Configuration

To use the Google Drive connector, you need to provide one of the following configurations:

#### Using a Token Path

```python
from science_data_kit.core.providers.storage import GoogleDriveProvider

# Create configuration with token path
config = {
    "token_path": "path/to/token.json"
}

# Create provider
provider = GoogleDriveProvider(config)

# Initialize provider
await provider.initialize()
```

#### Using Credentials Path

```python
from science_data_kit.core.providers.storage import GoogleDriveProvider

# Create configuration with credentials path
config = {
    "credentials_path": "path/to/credentials.json",
    "token_path": "path/to/token.json"  # Optional, to save the token
}

# Create provider
provider = GoogleDriveProvider(config)

# Initialize provider
await provider.initialize()
```

#### Using Token Dictionary

```python
from science_data_kit.core.providers.storage import GoogleDriveProvider

# Create configuration with token dictionary
config = {
    "token_dict": {
        "token": "your-token",
        "refresh_token": "your-refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
    }
}

# Create provider
provider = GoogleDriveProvider(config)

# Initialize provider
await provider.initialize()
```

### File Operations

#### Listing Files

You can list CSV/Excel files in a Google Drive folder as follows:

```python
# List files in a folder
folder_id = "your-folder-id"  # Use "root" for the root folder
files = await provider.list_files(folder_id)

# Print file names
for file in files:
    print(f"File: {file['name']} ({file['type']})")
```

#### Downloading File Data

You can download and parse file data as follows:

```python
# Download file data
file_id = "your-file-id"
data = await provider.download_file_data(file_id)

# Print data
print(data.head())
```

#### Getting File Information

You can get file metadata without downloading as follows:

```python
# Get file information
file_id = "your-file-id"
file_info = await provider.get_file_info(file_id)

# Print file information
print(f"File: {file_info['name']}")
print(f"Size: {file_info['size']} bytes")
print(f"Modified: {file_info['modified']}")
```

### Google Sheets

The Google Drive connector provides special handling for Google Sheets files. When you download a Google Sheets file, it is automatically exported as an Excel file and parsed into a pandas DataFrame.

## Google Sheets Connector

The Google Sheets connector allows you to access and analyze data from Google Sheets spreadsheets directly, providing more advanced functionality than the basic Google Drive connector.

### Configuration

To use the Google Sheets connector, you need to set up a Google Cloud project and create OAuth 2.0 credentials:

```python
from science_data_kit.core.providers.spreadsheet import GoogleSheetsProvider

# Create configuration
config = {
    "credentials_file": "/path/to/your/credentials.json",
    "token_file": "google_sheets_token.json"
}

# Create provider
provider = GoogleSheetsProvider(config)

# Initialize provider
await provider.initialize()
```

### Prerequisites

Before using the Google Sheets connector, you need to:

1. Create a Google Cloud project
2. Enable the Google Sheets API and Google Drive API
3. Create OAuth 2.0 credentials
4. Install the required dependencies:

```bash
pip install science_data_kit[google_sheets]
```

Or install the dependencies directly:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Spreadsheet Operations

#### Listing Spreadsheets

You can list available Google Sheets spreadsheets as follows:

```python
# List spreadsheets
spreadsheets = await provider.list_spreadsheets()

# Print spreadsheet names
for spreadsheet in spreadsheets:
    print(f"Spreadsheet: {spreadsheet['name']} ({spreadsheet['id']})")
```

#### Listing Sheets

You can list sheets in a Google Sheets spreadsheet as follows:

```python
# List sheets
spreadsheet_id = "your-spreadsheet-id"
sheets = await provider.list_sheets(spreadsheet_id)

# Print sheet names
for sheet in sheets:
    print(f"Sheet: {sheet['name']} ({sheet['rows']} rows, {sheet['columns']} columns)")
```

#### Getting Sheet Data

You can get data from a sheet in a Google Sheets spreadsheet as follows:

```python
# Get sheet data
spreadsheet_id = "your-spreadsheet-id"
sheet_name = "your-sheet-name"
data = await provider.get_sheet_data(spreadsheet_id, sheet_name)

# Print data
print(data.head())
```

### Authentication Process

When you first connect to Google Sheets, you will need to authenticate with your Google account:

1. A browser window will open (or you will be prompted to visit a URL and enter a code)
2. Sign in to your Google account
3. Review the permissions requested by the application
4. Click **Allow** to grant the necessary permissions
5. The SDK will store the authentication token for future use

## Local Storage Connector

The Local Storage connector allows you to access CSV and Excel files stored on the local file system or network mountpoints.

### Configuration

To use the Local Storage connector, you need to provide the following configuration:

```python
from science_data_kit.core.providers.storage import LocalStorageProvider

# Create configuration
config = {
    "base_path": "/path/to/your/data",
    "allowed_paths": ["/path/to/allowed/directory"]  # Optional, for security
}

# Create provider
provider = LocalStorageProvider(config)

# Initialize provider
await provider.initialize()
```

### Security Features

The Local Storage connector includes security features to prevent unauthorized access to files outside allowed paths:

- **base_path**: The root directory for file access. All relative paths are resolved relative to this directory.
- **allowed_paths**: Optional list of allowed paths. If specified, only files under these paths can be accessed.

### File Operations

#### Listing Files

You can list CSV/Excel files in a local folder as follows:

```python
# List files in a folder
folder_path = "your-folder-path"  # Relative to base_path
files = await provider.list_files(folder_path)

# Print file names
for file in files:
    print(f"File: {file['name']} ({file['type']})")
```

#### Downloading File Data

You can read file data as follows:

```python
# Read file data
file_path = "your-file-path"  # Relative to base_path
data = await provider.download_file_data(file_path)

# Print data
print(data.head())
```

#### Getting File Information

You can get file metadata without reading the file as follows:

```python
# Get file information
file_path = "your-file-path"  # Relative to base_path
file_info = await provider.get_file_info(file_path)

# Print file information
print(f"File: {file_info['name']}")
print(f"Size: {file_info['size']} bytes")
print(f"Modified: {file_info['modified']}")
```

## Common Operations

All data source connectors follow a common interface, making it easy to switch between different data sources or use multiple data sources simultaneously.

### Health Check

You can check if a provider is healthy and can be used as follows:

```python
# Check provider health
is_healthy = await provider.health_check()
print(f"Provider is healthy: {is_healthy}")
```

### Getting Capabilities

You can get the capabilities of a provider as follows:

```python
# Get provider capabilities
capabilities = provider.get_capabilities()
print(f"Provider capabilities: {capabilities}")
```

## Best Practices

Here are some best practices for using data source connectors in the Science Data Kit:

1. **Use Async/Await**: All provider methods that interact with external systems are asynchronous and should be called with `await`.
2. **Handle Exceptions**: Provider methods may raise exceptions if there are issues with authentication, network connectivity, or file access. Always handle these exceptions appropriately.
3. **Check Health**: Use the `health_check` method to verify that a provider is healthy before using it.
4. **Secure Credentials**: Store credentials securely and avoid hardcoding them in your code.
5. **Use Relative Paths**: When using the Local Storage provider, use relative paths to ensure portability.
6. **Limit Access**: When using the Local Storage provider, use the `allowed_paths` parameter to limit access to specific directories.
7. **Cache Results**: Consider caching the results of provider methods to improve performance, especially for operations that don't change frequently.

## Troubleshooting

Here are some common issues and their solutions:

### Authentication Issues

- **Issue**: Unable to authenticate with a data source.
  - **Solution**: Check that your credentials are correct and have the necessary permissions. For OAuth-based providers (Office 365, Google Drive), you may need to refresh your token or go through the authentication flow again.

### File Access Issues

- **Issue**: Unable to access a file.
  - **Solution**: Check that the file exists and that you have the necessary permissions to access it. For the Local Storage provider, check that the file is in an allowed path.

### Data Parsing Issues

- **Issue**: Unable to parse a file into a DataFrame.
  - **Solution**: Check that the file is in a supported format (CSV, Excel) and that it contains valid data. For Excel files, check that the sheet name is correct.

### Performance Issues

- **Issue**: Slow performance when accessing files.
  - **Solution**: Consider caching the results of provider methods, especially for operations that don't change frequently. For large files, consider using pagination or filtering to limit the amount of data retrieved.

If you encounter other issues, please refer to the API documentation or contact support.
