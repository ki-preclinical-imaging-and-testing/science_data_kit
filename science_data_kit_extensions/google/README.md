# Science Data Kit - Google Extension

This extension provides integration with Google services for the Science Data Kit. It enables access to Google Sheets, Google Drive, and other Google services for data import, export, and analysis.

## Installation

```bash
pip install science_data_kit_google
```

## Requirements

- Science Data Kit (core package)
- Google API Python Client
- Google Auth HTTP Lib2
- Google Auth OAuthlib

## Features

- **Google Sheets Integration**: Read and write data in Google Sheets
- **Google Drive Integration**: Access files and folders in Google Drive
- **Data Import**: Import data from Google Sheets into Neo4j
- **Data Export**: Export analysis results to Google Sheets
- **File Management**: Upload, download, and manage files in Google Drive
- **Collaboration**: Share files and manage permissions
- **Automated Reporting**: Create and update reports in Google Sheets

## Usage

```python
from science_data_kit.core.database import DatabaseManager
from science_data_kit_google import GoogleSheetsConnector, GoogleDriveConnector

# Initialize database manager
db_manager = DatabaseManager()
db_manager.connect_to_neo4j(uri="bolt://localhost:7687", username="neo4j", password="password")

# Initialize Google Sheets connector
sheets_connector = GoogleSheetsConnector(
    credentials_file="credentials.json",
    token_file="token.json"
)

# Read data from a Google Sheet
data = sheets_connector.read_sheet(
    spreadsheet_id="your-spreadsheet-id",
    sheet_name="Sheet1",
    range="A1:F100"
)

# Import data into Neo4j
sheets_connector.import_sheet_to_neo4j(
    db_manager,
    spreadsheet_id="your-spreadsheet-id",
    sheet_name="Sheet1",
    range="A1:F100",
    node_label="Experiment",
    id_column="experiment_id"
)

# Export Neo4j query results to Google Sheets
query = """
MATCH (e:Experiment)-[:HAS_RESULT]->(r:Result)
WHERE e.status = 'Completed'
RETURN e.id, e.name, e.date, r.value, r.unit
"""
sheets_connector.export_query_to_sheet(
    db_manager,
    query,
    spreadsheet_id="your-spreadsheet-id",
    sheet_name="Results",
    clear_sheet=True
)

# Initialize Google Drive connector
drive_connector = GoogleDriveConnector(
    credentials_file="credentials.json",
    token_file="token.json"
)

# List files in a folder
files = drive_connector.list_files(
    folder_id="your-folder-id",
    file_type="spreadsheet"
)

# Upload a file to Google Drive
file_id = drive_connector.upload_file(
    local_path="analysis_results.xlsx",
    folder_id="your-folder-id",
    name="Analysis Results",
    mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Share a file
drive_connector.share_file(
    file_id=file_id,
    email="colleague@example.com",
    role="writer"
)
```

## Configuration

You can configure the Google connectors using a credentials file obtained from the Google Cloud Console:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create OAuth 2.0 credentials and download the credentials file
5. Save the credentials file as `credentials.json` in your project directory

The first time you run the code, it will open a browser window for authentication and save the token to `token.json`.

## Authentication Methods

The extension supports multiple authentication methods:

1. **OAuth 2.0**: For interactive applications
2. **Service Account**: For server-to-server applications
3. **Application Default Credentials**: For Google Cloud environments

## Supported Google Services

- Google Sheets
- Google Drive
- Google Docs (for text extraction)
- Google Slides (for text extraction)
- Google Forms (for form responses)

## License

This extension is released under the MIT License.