"""
Microsoft Graph API Utility Functions for Science Data Kit

This module provides utility functions for working with Microsoft Graph API,
including data transformation, visualization, and data extraction.
"""

import json
import pandas as pd
import networkx as nx
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from urllib.parse import urlencode

from science_data_kit.core.models.msgraph_schemas import (
    User, Group, Message, Event, DriveItem,
    convert_msgraph_user, convert_msgraph_group, convert_msgraph_message
)


def build_msgraph_query(resource_path: str, query_parameters: Optional[Dict[str, Any]] = None) -> str:
    """
    Build a Microsoft Graph API query URL from a resource path and query parameters.

    Args:
        resource_path: The resource path to query (e.g., '/me', '/users').
        query_parameters: Optional query parameters.

    Returns:
        The full query URL.
    """
    # Ensure resource_path starts with a slash
    if not resource_path.startswith('/'):
        resource_path = f'/{resource_path}'

    # If no query parameters, return the resource path
    if not query_parameters:
        return resource_path

    # Convert query parameters to OData format
    odata_params = {}
    for key, value in query_parameters.items():
        # Skip empty values
        if value is None or value == '':
            continue

        # Convert key to OData format (e.g., 'select' -> '$select')
        odata_key = f'${key}' if not key.startswith('$') else key
        odata_params[odata_key] = value

    # Build the query URL
    if odata_params:
        query_string = urlencode(odata_params)
        return f"{resource_path}?{query_string}"
    else:
        return resource_path


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

    Raises:
        IOError: If there is an error writing to the file.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise IOError(f"Error saving Microsoft Graph API response to file: {str(e)}")


def load_msgraph_response(file_path: str) -> Dict[str, Any]:
    """
    Load Microsoft Graph API response from a file.

    Args:
        file_path: The path to load the data from.

    Returns:
        The response data from Microsoft Graph API.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Microsoft Graph API response file not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading Microsoft Graph API response file: {str(e)}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in Microsoft Graph API response file: {str(e)}", e.doc, e.pos)


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


def msgraph_to_dataframe(response: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert Microsoft Graph API response to a pandas DataFrame.

    This function provides a more sophisticated conversion than the simple
    pd.DataFrame constructor, handling nested structures and special fields
    based on the entity type.

    Args:
        response: The response data from Microsoft Graph API.

    Returns:
        A pandas DataFrame representing the data.
    """
    # Check if the response contains a 'value' field (collection)
    if 'value' in response and isinstance(response['value'], list):
        items = response['value']
    else:
        # Single entity response
        items = [response]

    # If there are no items, return an empty DataFrame
    if not items:
        return pd.DataFrame()

    # Determine the entity type based on the response content
    entity_type = "unknown"
    sample_item = items[0]

    if '@odata.type' in sample_item:
        odata_type = sample_item['@odata.type']
        if '#microsoft.graph.user' in odata_type:
            entity_type = "users"
        elif '#microsoft.graph.group' in odata_type:
            entity_type = "groups"
        elif '#microsoft.graph.message' in odata_type:
            entity_type = "messages"
        elif '#microsoft.graph.event' in odata_type:
            entity_type = "events"
        elif '#microsoft.graph.driveItem' in odata_type:
            entity_type = "drive"
    else:
        # Try to infer type from fields
        if 'userPrincipalName' in sample_item:
            entity_type = "users"
        elif 'groupTypes' in sample_item:
            entity_type = "groups"
        elif 'subject' in sample_item and ('from' in sample_item or 'sender' in sample_item):
            entity_type = "messages"
        elif 'subject' in sample_item and ('start' in sample_item or 'end' in sample_item):
            entity_type = "events"
        elif 'name' in sample_item and ('file' in sample_item or 'folder' in sample_item):
            entity_type = "drive"

    # Process items based on entity type
    processed_items = []

    for item in items:
        if entity_type == "users":
            processed_items.append(extract_user_data(item))
        elif entity_type == "groups":
            processed_items.append(extract_group_data(item))
        elif entity_type == "messages":
            processed_items.append(extract_message_data(item))
        else:
            # For other types or unknown types, flatten one level of nested dictionaries
            processed_item = {}
            for key, value in item.items():
                if isinstance(value, dict) and not key.startswith('@'):
                    for sub_key, sub_value in value.items():
                        processed_item[f"{key}_{sub_key}"] = sub_value
                else:
                    processed_item[key] = value
            processed_items.append(processed_item)

    # Convert to DataFrame
    df = pd.DataFrame(processed_items)

    # Handle list columns by converting them to string representations
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    return df
