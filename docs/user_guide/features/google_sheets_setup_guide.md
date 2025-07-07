# Google Sheets Integration Setup Guide

## Overview

This guide provides instructions for setting up and configuring the Google Sheets integration with the Science Data Kit (SDK). The integration enables the SDK to access and analyze data from Google Sheets spreadsheets, allowing you to work with your spreadsheet data directly within the SDK.

## Prerequisites

Before you can use the Google Sheets integration, you need to have:

1. A Google account
2. A Google Cloud project with the Google Sheets API and Google Drive API enabled
3. OAuth 2.0 credentials for your Google Cloud project
4. The Science Data Kit installed and configured
5. Google Sheets API dependencies installed

### Installing Google Sheets API Dependencies

The Google Sheets integration requires additional dependencies that are not installed by default. You can install these dependencies using pip:

```bash
pip install science_data_kit[google_sheets]
```

Alternatively, you can install the dependencies directly:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Setting Up a Google Cloud Project

To use the Google Sheets API, you need to set up a Google Cloud project:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API:
   - In the left sidebar, click on **APIs & Services** > **Library**
   - Search for "Google Sheets API" and click on it
   - Click **Enable**
   - Repeat the process for "Google Drive API"

## Creating OAuth 2.0 Credentials

To authenticate with the Google Sheets API, you need to create OAuth 2.0 credentials:

1. In the Google Cloud Console, navigate to your project
2. In the left sidebar, click on **APIs & Services** > **Credentials**
3. Click **Create Credentials** and select **OAuth client ID**
4. Select **Desktop application** as the application type
5. Enter a name for your OAuth client
6. Click **Create**
7. Download the credentials JSON file by clicking the download icon
8. Save the credentials file to a secure location on your computer

## Configuring the SDK for Google Sheets

### Using the Configuration File

Create a configuration file (e.g., `config.json`) with the following content:

```json
{
  "spreadsheet": {
    "google_sheets": {
      "credentials_file": "/path/to/your/credentials.json",
      "token_file": "google_sheets_token.json"
    }
  }
}
```

Replace `/path/to/your/credentials.json` with the actual path to your credentials file.

### Using the UI

You can also configure the Google Sheets integration through the SDK's user interface:

1. Launch the SDK application
2. Navigate to the Data Source Selection page
3. Select the "Spreadsheets (Google Sheets)" tab
4. If Google Sheets is not configured, you will see setup instructions
5. Enter the path to your credentials file in the provided field
6. Click **Connect to Google Sheets**

## Authentication Process

When you first connect to Google Sheets, you will need to authenticate with your Google account:

1. A browser window will open (or you will be prompted to visit a URL and enter a code)
2. Sign in to your Google account
3. Review the permissions requested by the application
4. Click **Allow** to grant the necessary permissions
5. The browser will display a success message, and you can close it
6. The SDK will store the authentication token for future use

## Using the Google Sheets Integration

Once configured, you can use the Google Sheets integration to:

1. Browse your Google Sheets spreadsheets
2. View and select sheets within a spreadsheet
3. Preview sheet contents before importing
4. Import data as pandas DataFrames for analysis

### Browsing Spreadsheets

1. Navigate to the Data Source Selection page
2. Select the "Spreadsheets (Google Sheets)" tab
3. You will see a list of your Google Sheets spreadsheets
4. Click the "Refresh Spreadsheets" button to update the list

### Selecting and Importing Sheets

1. Click on a spreadsheet to view its sheets
2. Click on a sheet to select it
3. Preview the sheet contents in the right panel
4. Click "Import Data" to import the sheet into the SDK

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure that your credentials file is correct and that you have granted the necessary permissions.
2. **API Not Enabled**: Ensure that both the Google Sheets API and Google Drive API are enabled in your Google Cloud project.
3. **Permission Denied**: Ensure that you have access to the spreadsheets you are trying to view.

### Checking API Status

If you're experiencing API issues, check the API status in the Google Cloud Console:

1. In the Google Cloud Console, navigate to your project
2. In the left sidebar, click on **APIs & Services** > **Dashboard**
3. Ensure that both the Google Sheets API and Google Drive API are enabled

### Checking Authentication

If you're experiencing authentication issues, check the authentication configuration:

1. Ensure that the credentials file is correct and accessible
2. Delete the token file (default: `google_sheets_token.json`) to force re-authentication
3. Try authenticating again

## Next Steps

After setting up the Google Sheets integration, you can:

1. Import data from Google Sheets into the SDK
2. Analyze and visualize the imported data
3. Combine Google Sheets data with other data sources in the SDK
4. Create custom workflows using the Google Sheets integration

For more information, see the [Google Sheets Usage Guide](google_sheets_usage_guide.md).