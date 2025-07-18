"""
Microsoft Graph API Entity Schemas for Science Data Kit

This module defines entity schemas for Microsoft Graph API entities,
providing a consistent structure for data validation and database operations.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

from science_data_kit.core.models.entity_schemas import BaseEntity, validate_entity


@dataclass
class MicrosoftGraphEntity(BaseEntity):
    """
    Base class for Microsoft Graph API entities.

    Attributes:
        graph_id: The unique identifier for the entity in Microsoft Graph.
        resource_type: The type of resource in Microsoft Graph.
    """
    graph_id: str = ""  # Add default value
    resource_type: str = ""  # Add default value


@dataclass
class User(MicrosoftGraphEntity):
    """
    Schema for a Microsoft Graph user.

    Attributes:
        display_name: The display name of the user.
        email: The email address of the user.
        user_principal_name: The user principal name (UPN) of the user.
        department: The department the user works in.
        job_title: The job title of the user.
        office_location: The office location of the user.
        business_phones: The business phone numbers of the user.
        mobile_phone: The mobile phone number of the user.
    """
    display_name: str
    email: str
    user_principal_name: str
    department: str = ""
    job_title: str = ""
    office_location: str = ""
    business_phones: List[str] = field(default_factory=list)
    mobile_phone: str = ""


@dataclass
class Group(MicrosoftGraphEntity):
    """
    Schema for a Microsoft Graph group.

    Attributes:
        display_name: The display name of the group.
        description: The description of the group.
        mail: The email address of the group.
        group_types: The types of the group.
        security_enabled: Whether the group is security-enabled.
        mail_enabled: Whether the group is mail-enabled.
        members: The members of the group.
    """
    display_name: str
    description: str = ""
    mail: str = ""
    group_types: List[str] = field(default_factory=list)
    security_enabled: bool = False
    mail_enabled: bool = False
    members: List[str] = field(default_factory=list)


@dataclass
class Message(MicrosoftGraphEntity):
    """
    Schema for a Microsoft Graph message.

    Attributes:
        subject: The subject of the message.
        body: The body of the message.
        from_email: The email address of the sender.
        to_recipients: The email addresses of the recipients.
        cc_recipients: The email addresses of the CC recipients.
        bcc_recipients: The email addresses of the BCC recipients.
        received_datetime: The date and time the message was received.
        has_attachments: Whether the message has attachments.
    """
    subject: str
    body: str
    from_email: str
    to_recipients: List[str]
    cc_recipients: List[str] = field(default_factory=list)
    bcc_recipients: List[str] = field(default_factory=list)
    received_datetime: datetime = field(default_factory=datetime.now)
    has_attachments: bool = False


@dataclass
class Event(MicrosoftGraphEntity):
    """
    Schema for a Microsoft Graph calendar event.

    Attributes:
        subject: The subject of the event.
        body: The body of the event.
        start_datetime: The start date and time of the event.
        end_datetime: The end date and time of the event.
        location: The location of the event.
        organizer: The organizer of the event.
        attendees: The attendees of the event.
        is_all_day: Whether the event is an all-day event.
    """
    subject: str
    body: str
    start_datetime: datetime
    end_datetime: datetime
    location: str = ""
    organizer: str = ""
    attendees: List[str] = field(default_factory=list)
    is_all_day: bool = False


@dataclass
class DriveItem(MicrosoftGraphEntity):
    """
    Schema for a Microsoft Graph drive item (file or folder).

    Attributes:
        name: The name of the drive item.
        size: The size of the drive item in bytes.
        web_url: The URL to the drive item in the web browser.
        created_by: The user who created the drive item.
        last_modified_by: The user who last modified the drive item.
        file_type: The file type of the drive item.
        folder_child_count: The number of children in the folder.
        parent_reference: The parent folder of the drive item.
    """
    name: str
    size: int
    web_url: str
    created_by: str
    last_modified_by: str
    file_type: str = ""
    folder_child_count: int = 0
    parent_reference: str = ""


def validate_msgraph_entity(entity: Any, schema_class: type) -> List[str]:
    """
    Validates a Microsoft Graph entity against a schema class.

    Args:
        entity: The entity to validate.
        schema_class: The schema class to validate against.

    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    return validate_entity(entity, schema_class)


def convert_msgraph_user(user_data: Dict[str, Any]) -> User:
    """
    Convert Microsoft Graph user data to a User entity.

    Args:
        user_data: The user data from Microsoft Graph API.

    Returns:
        A User entity.
    """
    return User(
        id=user_data.get('id', ''),
        graph_id=user_data.get('id', ''),
        resource_type='user',
        display_name=user_data.get('displayName', ''),
        email=user_data.get('mail', ''),
        user_principal_name=user_data.get('userPrincipalName', ''),
        department=user_data.get('department', ''),
        job_title=user_data.get('jobTitle', ''),
        office_location=user_data.get('officeLocation', ''),
        business_phones=user_data.get('businessPhones', []),
        mobile_phone=user_data.get('mobilePhone', ''),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_group(group_data: Dict[str, Any]) -> Group:
    """
    Convert Microsoft Graph group data to a Group entity.

    Args:
        group_data: The group data from Microsoft Graph API.

    Returns:
        A Group entity.
    """
    return Group(
        id=group_data.get('id', ''),
        graph_id=group_data.get('id', ''),
        resource_type='group',
        display_name=group_data.get('displayName', ''),
        description=group_data.get('description', ''),
        mail=group_data.get('mail', ''),
        group_types=group_data.get('groupTypes', []),
        security_enabled=group_data.get('securityEnabled', False),
        mail_enabled=group_data.get('mailEnabled', False),
        members=[],  # Members need to be fetched separately
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_message(message_data: Dict[str, Any]) -> Message:
    """
    Convert Microsoft Graph message data to a Message entity.

    Args:
        message_data: The message data from Microsoft Graph API.

    Returns:
        A Message entity.
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

    # Extract received datetime
    received_datetime = datetime.now()
    if 'receivedDateTime' in message_data:
        try:
            received_datetime = datetime.fromisoformat(message_data['receivedDateTime'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            pass

    return Message(
        id=message_data.get('id', ''),
        graph_id=message_data.get('id', ''),
        resource_type='message',
        subject=message_data.get('subject', ''),
        body=message_data.get('body', {}).get('content', ''),
        from_email=from_email,
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
        bcc_recipients=bcc_recipients,
        received_datetime=received_datetime,
        has_attachments=message_data.get('hasAttachments', False),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )
