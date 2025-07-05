# Science Data Kit - Dropbox Extension

This extension provides integration with Dropbox for the Science Data Kit. It enables access to files and folders stored in Dropbox, supporting data import, export, and synchronization.

## Installation

```bash
pip install science_data_kit_dropbox
```

## Requirements

- Science Data Kit (core package)
- Dropbox Python SDK

## Features

- **File Access**: Read and write files stored in Dropbox
- **Folder Navigation**: Browse and search folders
- **Data Import**: Import data from Dropbox files into Neo4j
- **Data Export**: Export analysis results to Dropbox
- **File Synchronization**: Keep local files in sync with Dropbox
- **File Metadata**: Access and update file metadata
- **Sharing**: Manage shared links and folder permissions

## Usage

```python
from science_data_kit.core.database import DatabaseManager
from science_data_kit_dropbox import DropboxConnector

# Initialize database manager
db_manager = DatabaseManager()
db_manager.connect_to_neo4j(uri="bolt://localhost:7687", username="neo4j", password="password")

# Initialize Dropbox connector
dropbox_connector = DropboxConnector(
    app_key="your-app-key",
    app_secret="your-app-secret",
    refresh_token="your-refresh-token"
)

# List files in a folder
files = dropbox_connector.list_files(folder_path="/Research Data")

# Download a file
file_content = dropbox_connector.download_file(file_path="/Research Data/experiment_results.csv")

# Import CSV data into Neo4j
dropbox_connector.import_csv_to_neo4j(
    db_manager,
    file_path="/Research Data/experiment_results.csv",
    node_label="Experiment",
    relationship_config={
        "source_column": "sample_id",
        "source_label": "Sample",
        "target_column": "researcher_id",
        "target_label": "Researcher",
        "relationship_type": "CONDUCTED_BY"
    }
)

# Upload analysis results
dropbox_connector.upload_file(
    local_path="analysis_results.xlsx",
    dropbox_path="/Research Data/Analysis/analysis_results.xlsx"
)

# Create a shared link
shared_link = dropbox_connector.create_shared_link(
    file_path="/Research Data/Analysis/analysis_results.xlsx",
    expires=30  # days
)
```

## Configuration

You can configure the Dropbox connector using environment variables:

```bash
export DROPBOX_APP_KEY="your-app-key"
export DROPBOX_APP_SECRET="your-app-secret"
export DROPBOX_REFRESH_TOKEN="your-refresh-token"
```

Or using a configuration file:

```yaml
# dropbox_config.yaml
app_key: "your-app-key"
app_secret: "your-app-secret"
refresh_token: "your-refresh-token"
```

## Authentication Methods

The extension supports multiple authentication methods:

1. **OAuth 2.0 Authorization Flow**: For interactive applications
2. **Refresh Token**: For long-running applications
3. **App Authentication**: For apps with team-level access

## Supported File Types

The extension supports various file types for data import:

- CSV files
- Excel files (XLSX, XLS)
- JSON files
- XML files
- Text files
- And more

## License

This extension is released under the MIT License.