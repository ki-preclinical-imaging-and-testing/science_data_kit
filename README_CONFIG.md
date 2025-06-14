# Database Configuration Guide

## Overview
This document explains how to configure the database connection for the Science Data Kit application.

## Configuration Files
The application uses YAML configuration files to store database connection details. There are three configuration files, listed in order of priority:

1. `app/.db_config_auto.yaml` - Automatically generated by the application when a Neo4j container is started
2. `.db_config.yaml` - User-defined hidden configuration file
3. `db_config.yaml` - User-defined visible configuration file

If multiple configuration files exist, the application will use the first one it finds in the order listed above.

## Configuration File Structure
Each configuration file should have the following structure:

```yaml
uri: "bolt://hostname:port"
user: "username"
password: "password"
database: "database_name"
```

Where:
- `uri` is the Neo4j connection URI (e.g., "bolt://localhost:7687")
- `user` is the Neo4j username (default: "neo4j")
- `password` is the Neo4j password
- `database` is the Neo4j database name (default: "neo4j")

## How to Configure
1. Create or edit one of the configuration files (preferably `db_config.yaml`)
2. Set the appropriate values for your Neo4j instance
3. Restart the application to apply the changes

## Automatic Configuration
When you start a Neo4j container through the application, it will automatically create or update the `app/.db_config_auto.yaml` file with the connection details for the container. This ensures that the application can connect to the Neo4j instance even if the container's IP address changes.

## Neo4j Version Selection
The application allows you to select different Neo4j versions when starting a container. This feature is available in the Streamlit interface under the "Neo4j Database" section when the database is not running.

Available versions include:
- `latest` - The latest stable version of Neo4j
- `2025.04` - A specific recent version
- Various older versions (5.x, 4.x series)

To use a specific Neo4j version:
1. Ensure the Neo4j container is not running
2. Select your desired version from the dropdown menu
3. Click "Start DBMS" to start a container with the selected version

Note that changing versions may affect database compatibility. It's recommended to export your data before switching to a different version if you have important data in your database.

## Neo4j Plugins
The Neo4j container started by the application comes with the APOC (Awesome Procedures On Cypher) plugin pre-installed and configured. APOC provides many useful procedures and functions that extend Neo4j's capabilities, such as:

- Data import/export
- Graph algorithms
- Data conversion
- Text processing
- And many more

You can use APOC procedures and functions in your Cypher queries without any additional configuration.

## Security Considerations
- The configuration files contain sensitive information (passwords)
- Ensure that the configuration files are not committed to version control
- The `.gitignore` file is configured to exclude these files
- Consider using different passwords for development and production environments
