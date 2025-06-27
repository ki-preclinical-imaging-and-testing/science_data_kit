"""
Microsoft Graph API Adapter for Science Data Kit

This module provides an adapter for Microsoft Graph API, allowing
existing code to work with the new Microsoft Graph API connection manager.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.models.msgraph_schemas import (
    User, Group, Message, Event, DriveItem,
    convert_msgraph_user, convert_msgraph_group, convert_msgraph_message
)
from science_data_kit.core.utils.msgraph_utils import (
    build_msgraph_query, msgraph_to_dataframe, msgraph_to_network,
    extract_user_data, extract_group_data, extract_message_data
)


class MSGraphAdapter:
    """
    Adapter for Microsoft Graph API.
    
    This class provides methods that mimic the interface of the Neo4jManager,
    allowing existing code to work with Microsoft Graph API.
    """
    
    def __init__(self, connection_manager: Optional[MSGraphConnectionManager] = None,
                 tenant_id: str = None, client_id: str = None, client_secret: str = None,
                 auth_method: str = "device_code", config_file: str = None):
        """
        Initialize the Microsoft Graph API adapter.
        
        Args:
            connection_manager: An existing MSGraphConnectionManager instance.
            tenant_id: The tenant ID for the Microsoft 365 account.
            client_id: The client ID for the application.
            client_secret: The client secret for the application.
            auth_method: The authentication method to use.
            config_file: Path to a configuration file containing authentication details.
        """
        if connection_manager:
            self.connection_manager = connection_manager
        else:
            self.connection_manager = MSGraphConnectionManager(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                auth_method=auth_method,
                config_file=config_file
            )
    
    def connect(self) -> bool:
        """
        Connect to Microsoft Graph API.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        return self.connection_manager.connect()
    
    def close(self) -> None:
        """
        Close the connection to Microsoft Graph API.
        """
        # No explicit close method needed for MSGraphConnectionManager
        pass
    
    def is_connected(self) -> bool:
        """
        Check if connected to Microsoft Graph API.
        
        Returns:
            True if connected, False otherwise.
        """
        return self.connection_manager.connected
    
    def execute_query(self, resource_path: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a query against Microsoft Graph API.
        
        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            parameters: Optional query parameters.
            
        Returns:
            The response from Microsoft Graph API as a dictionary.
        """
        return self.connection_manager.execute_query(resource_path, parameters)
    
    def query_to_dataframe(self, resource_path: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.
        
        Args:
            resource_path: The resource path to query (e.g., '/me', '/users').
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing the query results.
        """
        return self.connection_manager.query_to_dataframe(resource_path, parameters)
    
    def get_users(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get users from Microsoft Graph API.
        
        Args:
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing user information.
        """
        return self.connection_manager.get_users(parameters)
    
    def get_groups(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get groups from Microsoft Graph API.
        
        Args:
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing group information.
        """
        return self.connection_manager.get_groups(parameters)
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get information about the current user.
        
        Returns:
            A dictionary containing information about the current user.
        """
        return self.connection_manager.get_me()
    
    def get_my_messages(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get messages for the current user.
        
        Args:
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing message information.
        """
        return self.connection_manager.get_my_messages(parameters)
    
    def get_my_events(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get calendar events for the current user.
        
        Args:
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing event information.
        """
        return self.connection_manager.get_my_events(parameters)
    
    def get_my_files(self, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Get files for the current user.
        
        Args:
            parameters: Optional query parameters.
            
        Returns:
            A pandas DataFrame containing file information.
        """
        return self.connection_manager.get_my_files(parameters)
    
    # Additional methods to mimic Neo4jManager interface
    
    def fetch_labels(self) -> List[str]:
        """
        Fetch available labels (entity types) from Microsoft Graph API.
        
        Returns:
            A list of available entity types.
        """
        return ['User', 'Group', 'Message', 'Event', 'DriveItem']
    
    def fetch_node_properties(self, label: str) -> List[str]:
        """
        Fetch properties for a given entity type.
        
        Args:
            label: The entity type to fetch properties for.
            
        Returns:
            A list of property names.
        """
        if label == 'User':
            return ['id', 'display_name', 'email', 'user_principal_name', 'department', 'job_title', 'office_location', 'business_phones', 'mobile_phone']
        elif label == 'Group':
            return ['id', 'display_name', 'description', 'mail', 'group_types', 'security_enabled', 'mail_enabled', 'members']
        elif label == 'Message':
            return ['id', 'subject', 'body', 'from_email', 'to_recipients', 'cc_recipients', 'bcc_recipients', 'received_datetime', 'has_attachments']
        elif label == 'Event':
            return ['id', 'subject', 'body', 'start_datetime', 'end_datetime', 'location', 'organizer', 'attendees', 'is_all_day']
        elif label == 'DriveItem':
            return ['id', 'name', 'size', 'web_url', 'created_by', 'last_modified_by', 'file_type', 'folder_child_count', 'parent_reference']
        else:
            return []
    
    def fetch_nodes(self, label: str, properties: Optional[List[str]] = None, limit: int = 100) -> pd.DataFrame:
        """
        Fetch nodes of a given type.
        
        Args:
            label: The entity type to fetch.
            properties: Optional list of properties to include.
            limit: Maximum number of nodes to return.
            
        Returns:
            A pandas DataFrame containing the nodes.
        """
        if label == 'User':
            return self.get_users({'top': limit})
        elif label == 'Group':
            return self.get_groups({'top': limit})
        elif label == 'Message':
            return self.get_my_messages({'top': limit})
        elif label == 'Event':
            return self.get_my_events({'top': limit})
        elif label == 'DriveItem':
            return self.get_my_files({'top': limit})
        else:
            return pd.DataFrame()