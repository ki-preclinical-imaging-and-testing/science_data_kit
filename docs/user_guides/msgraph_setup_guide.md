# Microsoft Graph API Setup Guide

## Overview

This guide provides instructions for setting up and configuring the Microsoft Graph API integration with the Science Data Kit (SDK). The integration enables the SDK to access and analyze data from Microsoft 365 services, including Microsoft Teams, SharePoint, OneDrive, Outlook, and user/group information.

## Prerequisites

Before you can use the Microsoft Graph API integration, you need to have:

1. A Microsoft 365 account with appropriate permissions
2. An Azure Active Directory (Azure AD) tenant
3. Registered an application in Azure AD
4. The Science Data Kit installed and configured

## Registering an Application in Azure AD

To use the Microsoft Graph API, you need to register an application in Azure AD:

1. Sign in to the [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Enter a name for your application
5. Select the appropriate supported account type:
   - **Accounts in this organizational directory only** (for single-tenant applications)
   - **Accounts in any organizational directory** (for multi-tenant applications)
   - **Accounts in any organizational directory and personal Microsoft accounts** (for applications that need to access personal Microsoft accounts)
6. For the Redirect URI, select **Web** and enter a URI (e.g., `http://localhost:8501`)
7. Click **Register**

After registration, note down the following information:
- **Application (client) ID**
- **Directory (tenant) ID**

## Configuring API Permissions

Your application needs appropriate permissions to access Microsoft Graph API resources:

1. In the Azure Portal, navigate to your application
2. Select **API permissions**
3. Click **Add a permission**
4. Select **Microsoft Graph**
5. Choose the type of permissions:
   - **Delegated permissions** (for applications that access API on behalf of a signed-in user)
   - **Application permissions** (for applications that run without a signed-in user)
6. Select the required permissions based on your needs:
   - For user data: `User.Read`, `User.ReadBasic.All`, `User.Read.All`
   - For email data: `Mail.Read`, `Mail.ReadBasic`, `Mail.Read.Shared`
   - For calendar data: `Calendars.Read`, `Calendars.ReadWrite`
   - For files data: `Files.Read`, `Files.Read.All`
   - For groups data: `Group.Read.All`
7. Click **Add permissions**
8. For application permissions, click **Grant admin consent for [your tenant]**

## Creating a Client Secret (for Client Credentials Flow)

If you plan to use the client credentials flow (for daemon or service applications):

1. In the Azure Portal, navigate to your application
2. Select **Certificates & secrets**
3. Click **New client secret**
4. Enter a description and select an expiration period
5. Click **Add**
6. Note down the client secret value (you won't be able to see it again)

## Configuring the SDK for Microsoft Graph API

### Using the Configuration File

Create a configuration file (e.g., `msgraph_config.json`) with the following content:

```json
{
  "tenant_id": "your-tenant-id",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "auth_method": "client_credentials"
}
```

Replace the placeholder values with your actual values. The `auth_method` can be one of:
- `client_credentials` (for daemon or service applications)
- `device_code` (for command-line tools or IoT devices)
- `interactive` (for web applications)

### Using the UI

You can also configure the Microsoft Graph API integration through the SDK's user interface:

1. Launch the SDK application
2. Navigate to the Microsoft Graph API connection page
3. Select the authentication method
4. Enter your tenant ID and client ID (and client secret if using client credentials flow)
5. Click **Connect to Microsoft Graph API**

## Authentication Methods

The SDK supports multiple authentication methods for Microsoft Graph API:

### Device Code Flow

The device code flow is designed for devices and applications that don't have a web browser or have limited input capabilities. This is the recommended method for command-line tools.

1. Enter your Tenant ID and Client ID
2. Click **Connect to Microsoft Graph API**
3. You will be prompted to visit a URL and enter a code
4. After authentication, the connection will be established

### Client Credentials Flow

The client credentials flow is designed for daemon or service applications that run without user interaction. This method requires a client secret.

1. Enter your Tenant ID, Client ID, and Client Secret
2. Click **Connect to Microsoft Graph API**
3. The connection will be established using the provided credentials

### Interactive Flow

The interactive flow is designed for web applications that can open a browser window for authentication.

1. Enter your Tenant ID and Client ID
2. Click **Connect to Microsoft Graph API**
3. A browser window will open for authentication
4. After authentication, the connection will be established

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure that your tenant ID, client ID, and client secret (if applicable) are correct.
2. **Permission Denied**: Ensure that your application has the necessary permissions and that admin consent has been granted.
3. **Connection Timeout**: Check your network connection and ensure that your firewall is not blocking the connection.

### Checking Permissions

If you're experiencing permission issues, check the permissions assigned to your application:

1. In the Azure Portal, navigate to your application
2. Select **API permissions**
3. Ensure that the necessary permissions are listed and that admin consent has been granted

### Checking Authentication

If you're experiencing authentication issues, check the authentication configuration:

1. Ensure that the authentication method is appropriate for your application
2. For client credentials flow, ensure that the client secret is correct and has not expired
3. For device code and interactive flows, ensure that the redirect URI is correctly configured

## Next Steps

After setting up the Microsoft Graph API integration, you can:

1. Explore Microsoft Graph API data using the SDK's explorer page
2. Create visualizations of Microsoft Graph API data
3. Integrate Microsoft Graph API data with other data sources in the SDK

For more information, see the [Microsoft Graph API Usage Guide](msgraph_usage_guide.md).