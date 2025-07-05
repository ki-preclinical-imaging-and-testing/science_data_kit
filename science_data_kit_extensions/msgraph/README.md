# Science Data Kit - Microsoft Graph Extension

This extension provides integration with Microsoft Graph API for the Science Data Kit. It enables access to Microsoft 365 services including Microsoft Teams, SharePoint, OneDrive, Outlook, and user/group information.

## Installation

```bash
pip install science_data_kit_msgraph
```

## Requirements

- Science Data Kit (core package)
- Microsoft Graph SDK for Python
- Azure Identity package

## Features

- **Microsoft Teams Integration**: Access teams, channels, and conversations
- **SharePoint Integration**: Access sites, lists, and documents
- **OneDrive Integration**: Access files and folders
- **Outlook Integration**: Access emails, calendar events, and contacts
- **User/Group Information**: Access user profiles and group memberships

## Usage

```python
from science_data_kit.core.database import DatabaseManager
from science_data_kit_msgraph import MSGraphConnector

# Initialize database manager
db_manager = DatabaseManager()
db_manager.connect_to_neo4j(uri="bolt://localhost:7687", username="neo4j", password="password")

# Initialize MS Graph connector
msgraph_connector = MSGraphConnector(
    client_id="your-client-id",
    tenant_id="your-tenant-id",
    client_secret="your-client-secret"
)

# Authenticate
msgraph_connector.authenticate()

# Get all teams
teams = msgraph_connector.get_teams()

# Get all channels in a team
channels = msgraph_connector.get_channels(team_id="team-id")

# Get all messages in a channel
messages = msgraph_connector.get_messages(team_id="team-id", channel_id="channel-id")

# Import data into Neo4j
msgraph_connector.import_teams_to_neo4j(db_manager)
msgraph_connector.import_sharepoint_sites_to_neo4j(db_manager)
msgraph_connector.import_onedrive_files_to_neo4j(db_manager)
```

## Configuration

You can configure the Microsoft Graph connector using environment variables:

```bash
export MSGRAPH_CLIENT_ID="your-client-id"
export MSGRAPH_TENANT_ID="your-tenant-id"
export MSGRAPH_CLIENT_SECRET="your-client-secret"
```

Or using a configuration file:

```yaml
# msgraph_config.yaml
client_id: "your-client-id"
tenant_id: "your-tenant-id"
client_secret: "your-client-secret"
```

## Authentication Methods

The extension supports multiple authentication methods:

1. **Client Credentials**: For service-to-service authentication
2. **Authorization Code**: For user-delegated permissions
3. **Device Code**: For devices without a web browser
4. **Interactive Browser**: For interactive login

## Permissions

The extension requires the following Microsoft Graph API permissions:

- User.Read
- Group.Read.All
- Team.ReadBasic.All
- Channel.ReadBasic.All
- Sites.Read.All
- Files.Read.All
- Mail.Read

## License

This extension is released under the MIT License.