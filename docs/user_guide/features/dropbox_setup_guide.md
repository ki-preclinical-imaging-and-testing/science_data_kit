# Dropbox Integration Setup Guide

## Overview

This guide provides instructions for setting up and configuring the Dropbox integration with the Science Data Kit (SDK). The integration enables the SDK to access and analyze data from Dropbox, including CSV and Excel files stored in your Dropbox account.

## Prerequisites

Before you can use the Dropbox integration, you need to have:

1. A Dropbox account
2. A Dropbox API app with appropriate permissions
3. The Science Data Kit installed and configured
4. Dropbox SDK dependencies installed

### Installing Dropbox SDK Dependencies

The Dropbox integration requires additional dependencies that are not installed by default. You can install these dependencies using pip:

```bash
pip install science_data_kit[dropbox]
```

Alternatively, you can install the dependencies directly:

```bash
pip install dropbox==11.36.2
```

## Creating a Dropbox API App

To use the Dropbox API, you need to create a Dropbox API app:

1. Go to the [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click **Create app**
3. Select **Scoped access** for the API
4. Choose **Full Dropbox** access type (or "App folder" if you want to restrict access)
5. Enter a name for your app
6. Click **Create app**

After creation, note down the following information:
- **App key**
- **App secret**

## Configuring API Permissions

Your application needs appropriate permissions to access Dropbox resources:

1. In the Dropbox App Console, navigate to your app
2. Under **Permissions**, select the required permissions:
   - `files.metadata.read` (to list files and folders)
   - `files.content.read` (to download files)
3. Click **Submit**

## Generating an Access Token

To authenticate with the Dropbox API, you need to generate an access token:

1. In the Dropbox App Console, navigate to your app
2. Under **OAuth 2**, find the section for generating an access token
3. Click **Generate** next to "Generated access token"
4. Note down the access token (you won't be able to see it again)

## Configuring the SDK for Dropbox

### Using the Configuration File

Create a configuration file (e.g., `config.json`) with the following content:

```json
{
  "storage": {
    "dropbox": {
      "access_token": "your-access-token"
    }
  }
}
```

Replace `your-access-token` with your actual access token.

### Using the UI

You can also configure the Dropbox integration through the SDK's user interface:

1. Launch the SDK application
2. Navigate to the Data Source Selection page
3. Select the "File Storage (Dropbox)" tab
4. If Dropbox is not configured, you will see setup instructions
5. Enter your access token in the provided field
6. Click **Connect to Dropbox**

## Using the Dropbox Integration

Once configured, you can use the Dropbox integration to:

1. Browse your Dropbox folders
2. View and filter CSV and Excel files
3. Preview file contents before importing
4. Import data as pandas DataFrames for analysis

### Browsing Folders

1. Navigate to the Data Source Selection page
2. Select the "File Storage (Dropbox)" tab
3. Use the folder path input or click on folder names to navigate through your Dropbox
4. Click the "Browse Folder" button to refresh the file list

### Selecting and Importing Files

1. Browse to the folder containing your data files
2. Click on a CSV or Excel file to select it
3. Preview the file contents in the right panel
4. Click "Import Data" to import the file into the SDK

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure that your access token is correct and has not expired.
2. **Permission Denied**: Ensure that your app has the necessary permissions.
3. **File Not Found**: Ensure that the file path is correct and that the file exists in your Dropbox.

### Checking Permissions

If you're experiencing permission issues, check the permissions assigned to your app:

1. In the Dropbox App Console, navigate to your app
2. Under **Permissions**, ensure that the necessary permissions are enabled

### Checking Authentication

If you're experiencing authentication issues, check the authentication configuration:

1. Ensure that the access token is correct
2. Generate a new access token if the current one has expired

## Next Steps

After setting up the Dropbox integration, you can:

1. Import data from Dropbox files into the SDK
2. Analyze and visualize the imported data
3. Combine Dropbox data with other data sources in the SDK
4. Create custom workflows using the Dropbox integration

For more information, see the [Dropbox Usage Guide](dropbox_usage_guide.md).