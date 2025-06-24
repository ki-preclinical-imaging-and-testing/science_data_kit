"""
Microsoft Graph API Utility Functions for Science Data Kit

This module provides utility functions for working with Microsoft Graph API,
including data transformation, query building, and helper functions.
"""

import os
import json
import pandas as pd
import networkx as nx
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime

from science_data_kit.core.models.msgraph_schemas import (
    User, Group, Message, Event, DriveItem,
    convert_msgraph_user, convert_msgraph_group, convert_msgraph_message
)


def build_msgraph_query(resource_path: str, select: List[str] = None, 
                       filter_query: str = None, expand: List[str] = None,
                       orderby: List[str] = None, top: int = None,
                       skip: int = None) -> Tuple[str, Dict[str, Any]]:
    """
    Build a Microsoft Graph API query with OData parameters.
    
    Args:
        resource_path: The resource path to query (e.g., '/me', '/users').
        select: List of properties to include in the response.
        filter_query: OData filter query.
        expand: List of relationships to expand.
        orderby: List of properties to sort by.
        top: Maximum number of items to return.
        skip: Number of items to skip.
        
    Returns:
        A tuple containing the resource path and query parameters.
    """
    query_params = {}
    
    if select:
        query_params['select'] = ','.join(select)
    
    if filter_query:
        query_params['filter'] = filter_query
    
    if expand:
        query_params['expand'] = ','.join(expand)
    
    if orderby:
        query_params['orderby'] = ','.join(orderby)
    
    if top is not None:
        query_params['top'] = str(top)
    
    if skip is not None:
        query_params['skip'] = str(skip)
    
    return resource_path, query_params


def msgraph_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert Microsoft Graph API response to a pandas DataFrame.
    
    Args:
        data: The response data from Microsoft Graph API.
        
    Returns:
        A pandas DataFrame containing the data.
    """
    if 'value' in data:
        # Collection response
        return pd.DataFrame(data['value'])
    else:
        # Single entity response
        return pd.DataFrame([data])


def msgraph_to_network(data: Dict[str, Any], entity_type: str) -> nx.Graph:
    """
    Convert Microsoft Graph API response to a NetworkX graph.
    
    Args:
        data: The response data from Microsoft Graph API.
        entity_type: The type of entity in the data (e.g., 'users', 'groups').
        
    Returns:
        A NetworkX graph representing the data.
    """
    G = nx.Graph()
    
    if entity_type == 'users':
        if 'value' in data:
            for user in data['value']:
                G.add_node(user['id'], 
                           type='user',
                           name=user.get('displayName', ''),
                           email=user.get('mail', ''),
                           upn=user.get('userPrincipalName', ''),
                           department=user.get('department', ''),
                           job_title=user.get('jobTitle', ''))
        else:
            user = data
            G.add_node(user['id'], 
                       type='user',
                       name=user.get('displayName', ''),
                       email=user.get('mail', ''),
                       upn=user.get('userPrincipalName', ''),
                       department=user.get('department', ''),
                       job_title=user.get('jobTitle', ''))
    
    elif entity_type == 'groups':
        if 'value' in data:
            for group in data['value']:
                G.add_node(group['id'], 
                           type='group',
                           name=group.get('displayName', ''),
                           description=group.get('description', ''),
                           email=group.get('mail', ''))
                
                # Add members if available
                if 'members@odata.bind' in group:
                    for member_url in group['members@odata.bind']:
                        member_id = member_url.split('/')[-1]
                        G.add_edge(group['id'], member_id, relationship='member')
        else:
            group = data
            G.add_node(group['id'], 
                       type='group',
                       name=group.get('displayName', ''),
                       description=group.get('description', ''),
                       email=group.get('mail', ''))
            
            # Add members if available
            if 'members@odata.bind' in group:
                for member_url in group['members@odata.bind']:
                    member_id = member_url.split('/')[-1]
                    G.add_edge(group['id'], member_id, relationship='member')
    
    return G


def save_msgraph_response(data: Dict[str, Any], file_path: str) -> None:
    """
    Save Microsoft Graph API response to a file.
    
    Args:
        data: The response data from Microsoft Graph API.
        file_path: The path to save the data to.
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_msgraph_response(file_path: str) -> Dict[str, Any]:
    """
    Load Microsoft Graph API response from a file.
    
    Args:
        file_path: The path to load the data from.
        
    Returns:
        The response data from Microsoft Graph API.
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def extract_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant user data from Microsoft Graph API response.
    
    Args:
        user_data: The user data from Microsoft Graph API.
        
    Returns:
        A dictionary containing relevant user data.
    """
    return {
        'id': user_data.get('id', ''),
        'display_name': user_data.get('displayName', ''),
        'email': user_data.get('mail', ''),
        'user_principal_name': user_data.get('userPrincipalName', ''),
        'department': user_data.get('department', ''),
        'job_title': user_data.get('jobTitle', ''),
        'office_location': user_data.get('officeLocation', ''),
        'business_phones': user_data.get('businessPhones', []),
        'mobile_phone': user_data.get('mobilePhone', '')
    }


def extract_group_data(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant group data from Microsoft Graph API response.
    
    Args:
        group_data: The group data from Microsoft Graph API.
        
    Returns:
        A dictionary containing relevant group data.
    """
    return {
        'id': group_data.get('id', ''),
        'display_name': group_data.get('displayName', ''),
        'description': group_data.get('description', ''),
        'mail': group_data.get('mail', ''),
        'group_types': group_data.get('groupTypes', []),
        'security_enabled': group_data.get('securityEnabled', False),
        'mail_enabled': group_data.get('mailEnabled', False)
    }


def extract_message_data(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant message data from Microsoft Graph API response.
    
    Args:
        message_data: The message data from Microsoft Graph API.
        
    Returns:
        A dictionary containing relevant message data.
    """
    # Extract sender email
    from_email = ""
    if 'from' in message_data and 'emailAddress' in message_data['from']:
        from_email = message_data['from']['emailAddress'].get('address', '')
    
    # Extract recipient emails
    to_recipients = []
    if 'toRecipients' in message_data:
        to_recipients = [r['emailAddress'].get('address', '') for r in message_data['toRecipients'] if 'emailAddress' in r]
    
    # Extract CC recipient emails
    cc_recipients = []
    if 'ccRecipients' in message_data:
        cc_recipients = [r['emailAddress'].get('address', '') for r in message_data['ccRecipients'] if 'emailAddress' in r]
    
    # Extract BCC recipient emails
    bcc_recipients = []
    if 'bccRecipients' in message_data:
        bcc_recipients = [r['emailAddress'].get('address', '') for r in message_data['bccRecipients'] if 'emailAddress' in r]
    
    return {
        'id': message_data.get('id', ''),
        'subject': message_data.get('subject', ''),
        'body': message_data.get('body', {}).get('content', ''),
        'from_email': from_email,
        'to_recipients': to_recipients,
        'cc_recipients': cc_recipients,
        'bcc_recipients': bcc_recipients,
        'received_datetime': message_data.get('receivedDateTime', ''),
        'has_attachments': message_data.get('hasAttachments', False)
    }


def create_msgraph_config(tenant_id: str, client_id: str, client_secret: str = None,
                         auth_method: str = "device_code", output_file: str = None) -> Dict[str, Any]:
    """
    Create a configuration for Microsoft Graph API.
    
    Args:
        tenant_id: The tenant ID for the Microsoft 365 account.
        client_id: The client ID for the application.
        client_secret: The client secret for the application.
        auth_method: The authentication method to use.
        output_file: The path to save the configuration to.
        
    Returns:
        A dictionary containing the configuration.
    """
    config = {
        'tenant_id': tenant_id,
        'client_id': client_id,
        'auth_method': auth_method
    }
    
    if client_secret:
        config['client_secret'] = client_secret
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    return config