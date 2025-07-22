"""
Science Data Kit - Microsoft Graph Extension
Connector Module

This module provides the MSGraphConnector class, which is the main entry point
for interacting with Microsoft Graph API.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from azure.identity import ClientSecretCredential, DeviceCodeCredential, InteractiveBrowserCredential
from msgraph.core import GraphClient

logger = logging.getLogger(__name__)

class MSGraphConnector:
    """
    Main connector class for Microsoft Graph integration.

    This class handles authentication, connection management, and provides
    methods for interacting with Microsoft Graph API.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        auth_method: str = "client_credentials",
        config_file: Optional[str] = None
    ):
        """
        Initialize the Microsoft Graph connector.

        Args:
            client_id: Microsoft Graph API client ID
            tenant_id: Microsoft Graph API tenant ID
            client_secret: Microsoft Graph API client secret (for client_credentials auth method)
            auth_method: Authentication method to use (client_credentials, device_code, or interactive)
            config_file: Path to a configuration file containing credentials
        """
        self.client_id = client_id or os.environ.get("MSGRAPH_CLIENT_ID")
        self.tenant_id = tenant_id or os.environ.get("MSGRAPH_TENANT_ID")
        self.client_secret = client_secret or os.environ.get("MSGRAPH_CLIENT_SECRET")
        self.auth_method = auth_method

        # Load configuration from file if provided
        if config_file:
            self._load_config(config_file)

        # Validate credentials
        if not self.client_id or not self.tenant_id:
            raise ValueError(
                "Microsoft Graph API credentials not provided. "
                "Please provide client_id and tenant_id or set MSGRAPH_CLIENT_ID "
                "and MSGRAPH_TENANT_ID environment variables."
            )

        if self.auth_method == "client_credentials" and not self.client_secret:
            raise ValueError(
                "Client secret not provided for client_credentials auth method. "
                "Please provide client_secret or set MSGRAPH_CLIENT_SECRET environment variable."
            )

        self.client = None
        self.connected = False
        self.credential = None

    def _load_config(self, config_file: str) -> None:
        """
        Load configuration from a file.

        Args:
            config_file: Path to the configuration file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Determine file type and load accordingly
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required for YAML config files. Install with 'pip install pyyaml'.")
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

        # Update credentials from config
        self.client_id = config.get('client_id', self.client_id)
        self.tenant_id = config.get('tenant_id', self.tenant_id)
        self.client_secret = config.get('client_secret', self.client_secret)
        self.auth_method = config.get('auth_method', self.auth_method)

    def connect(self) -> bool:
        """
        Connect to Microsoft Graph API using the provided credentials.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Create the appropriate credential based on the auth method
            scopes = ["https://graph.microsoft.com/.default"]

            if self.auth_method == "client_credentials":
                self.credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            elif self.auth_method == "device_code":
                self.credential = DeviceCodeCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    callback=lambda code: print(f"Please use the following code to authenticate: {code.user_code}")
                )
            elif self.auth_method == "interactive":
                self.credential = InteractiveBrowserCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id
                )
            else:
                logger.error(f"Unsupported auth_method: {self.auth_method}")
                return False

            # Create the Graph client
            self.client = GraphClient(credential=self.credential, scopes=scopes)

            # Test the connection
            response = self.client.get("/me")
            if response.status_code == 200:
                self.connected = True
                logger.info("Successfully connected to Microsoft Graph API")
                return True
            else:
                logger.error(f"Failed to connect to Microsoft Graph API: {response.status_code} {response.text}")
                self.connected = False
                return False
        except Exception as e:
            logger.error(f"Error during connection: {e}")
            self.connected = False
            return False

    def authenticate(self) -> str:
        """
        Start the authentication flow.

        Returns:
            str: URL for the user to visit to authorize the application (for device_code auth method)
                 or a message indicating that authentication has started (for interactive auth method)
        """
        if self.auth_method == "device_code":
            # For device code flow, we need to create the credential and then return the verification URL
            self.credential = DeviceCodeCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                callback=lambda code: print(f"Please use the following code to authenticate: {code.user_code}")
            )
            return "https://microsoft.com/devicelogin"
        elif self.auth_method == "interactive":
            # For interactive flow, we'll open a browser window
            self.credential = InteractiveBrowserCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id
            )
            return "Authentication started. Please complete the process in your browser."
        else:
            raise ValueError(f"Authentication flow not supported for auth_method: {self.auth_method}")

    def is_connected(self) -> bool:
        """
        Check if the connector is connected to Microsoft Graph API.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.client or not self.connected:
            return False

        try:
            # Test the connection by making a simple API call
            response = self.client.get("/me")
            return response.status_code == 200
        except Exception:
            self.connected = False
            return False

    def disconnect(self) -> None:
        """
        Disconnect from Microsoft Graph API.
        """
        self.client = None
        self.credential = None
        self.connected = False
        logger.info("Disconnected from Microsoft Graph API")

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the connected user.

        Returns:
            Dict[str, Any]: User information
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        try:
            response = self.client.get("/me")
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'id': user_info.get('id'),
                    'display_name': user_info.get('displayName'),
                    'email': user_info.get('mail') or user_info.get('userPrincipalName'),
                    'job_title': user_info.get('jobTitle'),
                    'business_phones': user_info.get('businessPhones', []),
                    'office_location': user_info.get('officeLocation')
                }
            else:
                logger.error(f"Error getting user info: {response.status_code} {response.text}")
                raise ConnectionError(f"Failed to get user info: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise

    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make an API request to the Microsoft Graph API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Request headers

        Returns:
            API response
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        try:
            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"

            # Make the request
            response = self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data,
                headers=headers
            )

            # Check for successful response
            if response.status_code >= 200 and response.status_code < 300:
                if response.headers.get('content-type', '').startswith('application/json'):
                    return response.json()
                else:
                    return response.content
            else:
                logger.error(f"API request failed: {response.status_code} {response.text}")
                raise ConnectionError(f"API request failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise

    def get_sharepoint_sites(self) -> List[Dict[str, Any]]:
        """
        Get a list of SharePoint sites.

        Returns:
            List[Dict[str, Any]]: List of SharePoint sites
        """
        response = self.request("GET", "/sites?search=*")
        return response.get('value', [])

    def get_sharepoint_lists(self, site_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of SharePoint lists for a site.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            List[Dict[str, Any]]: List of SharePoint lists
        """
        response = self.request("GET", f"/sites/{site_id}/lists")
        return response.get('value', [])

    def get_sharepoint_list_items(self, site_id: str, list_id: str) -> List[Dict[str, Any]]:
        """
        Get items from a SharePoint list.

        Args:
            site_id: ID of the SharePoint site
            list_id: ID of the SharePoint list

        Returns:
            List[Dict[str, Any]]: List of SharePoint list items
        """
        response = self.request("GET", f"/sites/{site_id}/lists/{list_id}/items?expand=fields")
        return response.get('value', [])

    def get_sharepoint_drives(self, site_id: str) -> List[Dict[str, Any]]:
        """
        Get document libraries (drives) for a SharePoint site.

        Args:
            site_id: ID of the SharePoint site

        Returns:
            List[Dict[str, Any]]: List of SharePoint document libraries
        """
        response = self.request("GET", f"/sites/{site_id}/drives")
        return response.get('value', [])

    def get_sharepoint_drive_items(self, site_id: str, drive_id: str, item_id: str = "root") -> List[Dict[str, Any]]:
        """
        Get items from a SharePoint document library.

        Args:
            site_id: ID of the SharePoint site
            drive_id: ID of the SharePoint drive (document library)
            item_id: ID of the item (folder) to list (default: "root")

        Returns:
            List[Dict[str, Any]]: List of items in the document library
        """
        response = self.request("GET", f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/children")
        return response.get('value', [])

    def get_sharepoint_drive_item(self, site_id: str, drive_id: str, item_id: str) -> Dict[str, Any]:
        """
        Get metadata for an item in a SharePoint document library.

        Args:
            site_id: ID of the SharePoint site
            drive_id: ID of the SharePoint drive (document library)
            item_id: ID of the item

        Returns:
            Dict[str, Any]: Metadata for the item
        """
        return self.request("GET", f"/sites/{site_id}/drives/{drive_id}/items/{item_id}")

    def download_sharepoint_file(self, site_id: str, drive_id: str, item_id: str) -> bytes:
        """
        Download a file from a SharePoint document library.

        Args:
            site_id: ID of the SharePoint site
            drive_id: ID of the SharePoint drive (document library)
            item_id: ID of the file

        Returns:
            bytes: File content
        """
        # Get the download URL
        item = self.get_sharepoint_drive_item(site_id, drive_id, item_id)
        if "@microsoft.graph.downloadUrl" not in item:
            raise ValueError(f"Item {item_id} is not a file or does not have a download URL")

        download_url = item["@microsoft.graph.downloadUrl"]

        # Download the file
        response = self.client.get(download_url)
        if response.status_code == 200:
            return response.content
        else:
            raise ValueError(f"Failed to download file: {response.status_code} {response.text}")

    def get_onedrive_files(self, drive_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get files from OneDrive.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)

        Returns:
            List[Dict[str, Any]]: List of OneDrive files
        """
        if drive_id:
            response = self.request("GET", f"/drives/{drive_id}/root/children")
        else:
            response = self.request("GET", "/me/drive/root/children")
        return response.get('value', [])

    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get a list of Microsoft Teams.

        Returns:
            List[Dict[str, Any]]: List of Teams
        """
        response = self.request("GET", "/me/joinedTeams")
        return response.get('value', [])

    def get_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Get channels for a team.

        Args:
            team_id: ID of the team

        Returns:
            List[Dict[str, Any]]: List of channels
        """
        response = self.request("GET", f"/teams/{team_id}/channels")
        return response.get('value', [])

    def get_messages(self, team_id: str, channel_id: str) -> List[Dict[str, Any]]:
        """
        Get messages from a channel.

        Args:
            team_id: ID of the team
            channel_id: ID of the channel

        Returns:
            List[Dict[str, Any]]: List of messages
        """
        response = self.request("GET", f"/teams/{team_id}/channels/{channel_id}/messages")
        return response.get('value', [])

    def get_message_replies(self, team_id: str, channel_id: str, message_id: str) -> List[Dict[str, Any]]:
        """
        Get replies to a specific message in a channel.

        Args:
            team_id: ID of the team
            channel_id: ID of the channel
            message_id: ID of the message

        Returns:
            List[Dict[str, Any]]: List of reply messages
        """
        response = self.request("GET", f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies")
        return response.get('value', [])

    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get messages from a Teams chat.

        Args:
            chat_id: ID of the chat

        Returns:
            List[Dict[str, Any]]: List of chat messages
        """
        response = self.request("GET", f"/chats/{chat_id}/messages")
        return response.get('value', [])

    def get_user_chats(self) -> List[Dict[str, Any]]:
        """
        Get all chats for the current user.

        Returns:
            List[Dict[str, Any]]: List of chats
        """
        response = self.request("GET", "/me/chats")
        return response.get('value', [])

    def analyze_conversation(self, team_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Analyze a Teams channel conversation to extract insights.

        This method retrieves all messages in a channel and performs basic analysis
        to extract conversation metrics, active participants, and conversation timeline.

        Args:
            team_id: ID of the team
            channel_id: ID of the channel

        Returns:
            Dict[str, Any]: Analysis results including:
                - message_count: Total number of messages
                - participant_count: Number of unique participants
                - participants: List of participants with message counts
                - timeline: Message counts by date
                - top_active_periods: Most active conversation periods
        """
        messages = self.get_messages(team_id, channel_id)

        # Extract basic metrics
        message_count = len(messages)

        # Extract participants and their message counts
        participants = {}
        timeline = {}

        for message in messages:
            # Count messages by participant
            from_user = message.get('from', {}).get('user', {})
            user_id = from_user.get('id', 'unknown')
            user_name = from_user.get('displayName', 'Unknown User')

            if user_id not in participants:
                participants[user_id] = {
                    'id': user_id,
                    'name': user_name,
                    'message_count': 0
                }

            participants[user_id]['message_count'] += 1

            # Track message timeline
            created_datetime = message.get('createdDateTime', '')
            if created_datetime:
                date_only = created_datetime.split('T')[0]  # Extract date part
                timeline[date_only] = timeline.get(date_only, 0) + 1

        # Sort timeline by date
        sorted_timeline = dict(sorted(timeline.items()))

        # Find most active periods
        sorted_by_activity = sorted(timeline.items(), key=lambda x: x[1], reverse=True)
        top_active_periods = sorted_by_activity[:5] if len(sorted_by_activity) >= 5 else sorted_by_activity

        return {
            'message_count': message_count,
            'participant_count': len(participants),
            'participants': list(participants.values()),
            'timeline': sorted_timeline,
            'top_active_periods': dict(top_active_periods)
        }

    def extract_conversation_topics(self, team_id: str, channel_id: str) -> Dict[str, Any]:
        """
        Extract potential topics from a Teams channel conversation.

        This method uses a simple frequency-based approach to identify potential
        topics from message content. For more advanced topic modeling, consider
        integrating with NLP services.

        Args:
            team_id: ID of the team
            channel_id: ID of the channel

        Returns:
            Dict[str, Any]: Topic analysis results including:
                - common_terms: Most frequently used terms
                - potential_topics: Potential conversation topics
        """
        messages = self.get_messages(team_id, channel_id)

        # Extract message content
        all_content = ""
        for message in messages:
            content = message.get('body', {}).get('content', '')
            # Remove HTML tags if present (simple approach)
            content = content.replace('<p>', ' ').replace('</p>', ' ')
            content = content.replace('<br>', ' ').replace('</br>', ' ')
            all_content += " " + content

        # Simple word frequency analysis
        # In a real implementation, you would use more sophisticated NLP techniques
        words = all_content.lower().split()
        word_freq = {}

        # Common English stop words to filter out
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                     'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 
                     'through', 'over', 'before', 'after', 'between', 'under', 'during',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        for word in words:
            # Remove punctuation
            word = word.strip('.,!?;:()"\'')
            if word and len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get most common terms
        sorted_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        common_terms = dict(sorted_terms[:20]) if len(sorted_terms) >= 20 else dict(sorted_terms)

        # Group related terms (simplified approach)
        # In a real implementation, you would use more sophisticated clustering or topic modeling
        potential_topics = []
        processed_terms = set()

        for term, count in sorted_terms[:50]:
            if term in processed_terms:
                continue

            related_terms = [term]
            for other_term, _ in sorted_terms[:100]:
                if other_term != term and other_term not in processed_terms:
                    # Simple string matching - in a real implementation, use semantic similarity
                    if term in other_term or other_term in term:
                        related_terms.append(other_term)
                        processed_terms.add(other_term)

            if len(related_terms) > 1 or count > 5:
                potential_topics.append({
                    'main_term': term,
                    'related_terms': related_terms,
                    'frequency': count
                })

            processed_terms.add(term)

            if len(potential_topics) >= 10:
                break

        return {
            'common_terms': common_terms,
            'potential_topics': potential_topics
        }

    def get_excel_file_metadata(self, drive_id: Optional[str] = None, item_id: str = None, 
                               site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for an Excel file stored in OneDrive or SharePoint.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            Dict[str, Any]: Metadata for the Excel file
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}"
        else:
            endpoint = f"/me/drive/items/{item_id}"

        # Get the file metadata
        return self.request("GET", endpoint)

    def get_excel_worksheets(self, drive_id: Optional[str] = None, item_id: str = None, 
                            site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of worksheets in an Excel file.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            List[Dict[str, Any]]: List of worksheets in the Excel file
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets"
        else:
            endpoint = f"/me/drive/items/{item_id}/workbook/worksheets"

        # Get the worksheets
        response = self.request("GET", endpoint)
        return response.get('value', [])

    def get_excel_worksheet_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                                worksheet_id: str = None, site_id: Optional[str] = None,
                                range_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel worksheet.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            worksheet_id: ID or name of the worksheet
            site_id: ID of the SharePoint site (if the file is in SharePoint)
            range_address: Address of the range to get (e.g., "A1:C10")

        Returns:
            Dict[str, Any]: Data from the worksheet
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        if not worksheet_id:
            raise ValueError("worksheet_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            base_endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}"
        elif drive_id:
            base_endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}"
        else:
            base_endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}"

        # If a range is specified, get that range, otherwise get the used range
        if range_address:
            endpoint = f"{base_endpoint}/range(address='{range_address}')"
        else:
            endpoint = f"{base_endpoint}/usedRange"

        # Get the worksheet data
        return self.request("GET", endpoint)

    def get_excel_chart_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                            worksheet_id: str = None, chart_id: str = None, 
                            site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel chart.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            worksheet_id: ID or name of the worksheet
            chart_id: ID of the chart
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            Dict[str, Any]: Data from the chart
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        if not worksheet_id:
            raise ValueError("worksheet_id is required")

        if not chart_id:
            raise ValueError("chart_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/charts/{chart_id}"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/charts/{chart_id}"
        else:
            endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/charts/{chart_id}"

        # Get the chart data
        return self.request("GET", endpoint)

    def get_excel_charts(self, drive_id: Optional[str] = None, item_id: str = None, 
                        worksheet_id: str = None, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of charts in an Excel worksheet.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            worksheet_id: ID or name of the worksheet
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            List[Dict[str, Any]]: List of charts in the worksheet
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        if not worksheet_id:
            raise ValueError("worksheet_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/charts"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/charts"
        else:
            endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/charts"

        # Get the charts
        response = self.request("GET", endpoint)
        return response.get('value', [])

    def get_excel_tables(self, drive_id: Optional[str] = None, item_id: str = None, 
                        worksheet_id: str = None, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of tables in an Excel worksheet.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            worksheet_id: ID or name of the worksheet
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            List[Dict[str, Any]]: List of tables in the worksheet
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        if not worksheet_id:
            raise ValueError("worksheet_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/tables"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/tables"
        else:
            endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/tables"

        # Get the tables
        response = self.request("GET", endpoint)
        return response.get('value', [])

    def get_excel_table_data(self, drive_id: Optional[str] = None, item_id: str = None, 
                            worksheet_id: str = None, table_id: str = None, 
                            site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data from an Excel table.

        Args:
            drive_id: ID of the drive (optional, defaults to the current user's drive)
            item_id: ID of the Excel file
            worksheet_id: ID or name of the worksheet
            table_id: ID of the table
            site_id: ID of the SharePoint site (if the file is in SharePoint)

        Returns:
            Dict[str, Any]: Data from the table
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Microsoft Graph API")

        if not item_id:
            raise ValueError("item_id is required")

        if not worksheet_id:
            raise ValueError("worksheet_id is required")

        if not table_id:
            raise ValueError("table_id is required")

        # Construct the appropriate endpoint based on the provided parameters
        if site_id and drive_id:
            endpoint = f"/sites/{site_id}/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/tables/{table_id}/range"
        elif drive_id:
            endpoint = f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/tables/{table_id}/range"
        else:
            endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/tables/{table_id}/range"

        # Get the table data
        return self.request("GET", endpoint)
