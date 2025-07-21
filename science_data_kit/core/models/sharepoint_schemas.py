"""
SharePoint Entity Schemas for Science Data Kit

This module defines entity schemas for SharePoint entities,
providing a consistent structure for data validation and database operations.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

from science_data_kit.core.models.entity_schemas import BaseEntity, validate_entity
from science_data_kit.core.models.msgraph_schemas import MicrosoftGraphEntity, DriveItem


@dataclass
class SharePointSite(MicrosoftGraphEntity):
    """
    Schema for a SharePoint site.

    Attributes:
        display_name: The display name of the site.
        description: The description of the site.
        web_url: The URL to the site in the web browser.
        site_collection_id: The ID of the site collection.
        root_web: Whether this is the root web of the site collection.
        created_by: The user who created the site.
        last_modified_by: The user who last modified the site.
        drives: List of drive IDs associated with the site.
        lists: List of list IDs associated with the site.
    """
    display_name: str = ""
    description: str = ""
    web_url: str = ""
    site_collection_id: str = ""
    root_web: bool = False
    created_by: str = ""
    last_modified_by: str = ""
    drives: List[str] = field(default_factory=list)
    lists: List[str] = field(default_factory=list)


@dataclass
class SharePointList(MicrosoftGraphEntity):
    """
    Schema for a SharePoint list.

    Attributes:
        display_name: The display name of the list.
        description: The description of the list.
        web_url: The URL to the list in the web browser.
        site_id: The ID of the site containing the list.
        list_template: The template of the list.
        created_by: The user who created the list.
        last_modified_by: The user who last modified the list.
        columns: The columns in the list.
        items: List of item IDs in the list.
    """
    display_name: str = ""
    description: str = ""
    web_url: str = ""
    site_id: str = ""
    list_template: str = ""
    created_by: str = ""
    last_modified_by: str = ""
    columns: Dict[str, Any] = field(default_factory=dict)
    items: List[str] = field(default_factory=list)


@dataclass
class SharePointListItem(MicrosoftGraphEntity):
    """
    Schema for a SharePoint list item.

    Attributes:
        list_id: The ID of the list containing the item.
        site_id: The ID of the site containing the list.
        web_url: The URL to the item in the web browser.
        created_by: The user who created the item.
        last_modified_by: The user who last modified the item.
        fields: The fields of the item.
    """
    list_id: str = ""
    site_id: str = ""
    web_url: str = ""
    created_by: str = ""
    last_modified_by: str = ""
    fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharePointDrive(MicrosoftGraphEntity):
    """
    Schema for a SharePoint drive (document library).

    Attributes:
        display_name: The display name of the drive.
        description: The description of the drive.
        web_url: The URL to the drive in the web browser.
        site_id: The ID of the site containing the drive.
        drive_type: The type of drive.
        created_by: The user who created the drive.
        last_modified_by: The user who last modified the drive.
        quota: Quota information for the drive.
        root_folder_id: The ID of the root folder of the drive.
    """
    display_name: str = ""
    description: str = ""
    web_url: str = ""
    site_id: str = ""
    drive_type: str = ""
    created_by: str = ""
    last_modified_by: str = ""
    quota: Dict[str, Any] = field(default_factory=dict)
    root_folder_id: str = ""


@dataclass
class SharePointFile(DriveItem):
    """
    Schema for a SharePoint file.

    Attributes:
        site_id: The ID of the site containing the file.
        drive_id: The ID of the drive containing the file.
        content_type: The content type of the file.
        etag: The ETag of the file.
        shared: Whether the file is shared.
        sharing_info: Information about how the file is shared.
        virus_status: The virus scan status of the file.
        checkout_info: Information about checkout status.
        version_info: Information about file versions.
    """
    site_id: str = ""
    drive_id: str = ""
    content_type: str = ""
    etag: str = ""
    shared: bool = False
    sharing_info: Dict[str, Any] = field(default_factory=dict)
    virus_status: str = ""
    checkout_info: Dict[str, Any] = field(default_factory=dict)
    version_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharePointFolder(DriveItem):
    """
    Schema for a SharePoint folder.

    Attributes:
        site_id: The ID of the site containing the folder.
        drive_id: The ID of the drive containing the folder.
        child_count: The number of items in the folder.
        special_folder: Information if this is a special folder.
        shared: Whether the folder is shared.
        sharing_info: Information about how the folder is shared.
    """
    site_id: str = ""
    drive_id: str = ""
    child_count: int = 0
    special_folder: Dict[str, Any] = field(default_factory=dict)
    shared: bool = False
    sharing_info: Dict[str, Any] = field(default_factory=dict)


def convert_msgraph_site(site_data: Dict[str, Any]) -> SharePointSite:
    """
    Convert Microsoft Graph site data to a SharePointSite entity.

    Args:
        site_data: The site data from Microsoft Graph API.

    Returns:
        A SharePointSite entity.
    """
    return SharePointSite(
        id=site_data.get('id', ''),
        name=site_data.get('displayName', ''),
        graph_id=site_data.get('id', ''),
        resource_type='site',
        display_name=site_data.get('displayName', ''),
        description=site_data.get('description', ''),
        web_url=site_data.get('webUrl', ''),
        site_collection_id=site_data.get('siteCollection', {}).get('id', ''),
        root_web=site_data.get('root', {}).get('web', {}).get('id', '') != '',
        created_by=site_data.get('createdBy', {}).get('user', {}).get('displayName', ''),
        last_modified_by=site_data.get('lastModifiedBy', {}).get('user', {}).get('displayName', ''),
        drives=[],  # Drives need to be fetched separately
        lists=[],   # Lists need to be fetched separately
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_list(list_data: Dict[str, Any], site_id: str) -> SharePointList:
    """
    Convert Microsoft Graph list data to a SharePointList entity.

    Args:
        list_data: The list data from Microsoft Graph API.
        site_id: The ID of the site containing the list.

    Returns:
        A SharePointList entity.
    """
    return SharePointList(
        id=list_data.get('id', ''),
        name=list_data.get('displayName', ''),
        graph_id=list_data.get('id', ''),
        resource_type='list',
        display_name=list_data.get('displayName', ''),
        description=list_data.get('description', ''),
        web_url=list_data.get('webUrl', ''),
        site_id=site_id,
        list_template=list_data.get('list', {}).get('template', ''),
        created_by=list_data.get('createdBy', {}).get('user', {}).get('displayName', ''),
        last_modified_by=list_data.get('lastModifiedBy', {}).get('user', {}).get('displayName', ''),
        columns={},  # Columns need to be processed separately
        items=[],    # Items need to be fetched separately
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_list_item(item_data: Dict[str, Any], list_id: str, site_id: str) -> SharePointListItem:
    """
    Convert Microsoft Graph list item data to a SharePointListItem entity.

    Args:
        item_data: The list item data from Microsoft Graph API.
        list_id: The ID of the list containing the item.
        site_id: The ID of the site containing the list.

    Returns:
        A SharePointListItem entity.
    """
    return SharePointListItem(
        id=item_data.get('id', ''),
        name=f"Item {item_data.get('id', '')}",
        graph_id=item_data.get('id', ''),
        resource_type='listItem',
        list_id=list_id,
        site_id=site_id,
        web_url=item_data.get('webUrl', ''),
        created_by=item_data.get('createdBy', {}).get('user', {}).get('displayName', ''),
        last_modified_by=item_data.get('lastModifiedBy', {}).get('user', {}).get('displayName', ''),
        fields=item_data.get('fields', {}),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_drive(drive_data: Dict[str, Any], site_id: str) -> SharePointDrive:
    """
    Convert Microsoft Graph drive data to a SharePointDrive entity.

    Args:
        drive_data: The drive data from Microsoft Graph API.
        site_id: The ID of the site containing the drive.

    Returns:
        A SharePointDrive entity.
    """
    return SharePointDrive(
        id=drive_data.get('id', ''),
        name=drive_data.get('name', ''),
        graph_id=drive_data.get('id', ''),
        resource_type='drive',
        display_name=drive_data.get('name', ''),
        description=drive_data.get('description', ''),
        web_url=drive_data.get('webUrl', ''),
        site_id=site_id,
        drive_type=drive_data.get('driveType', ''),
        created_by=drive_data.get('createdBy', {}).get('user', {}).get('displayName', ''),
        last_modified_by=drive_data.get('lastModifiedBy', {}).get('user', {}).get('displayName', ''),
        quota=drive_data.get('quota', {}),
        root_folder_id=drive_data.get('root', {}).get('id', ''),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={}
    )


def convert_msgraph_drive_item(item_data: Dict[str, Any], site_id: str, drive_id: str) -> Union[SharePointFile, SharePointFolder]:
    """
    Convert Microsoft Graph drive item data to a SharePointFile or SharePointFolder entity.

    Args:
        item_data: The drive item data from Microsoft Graph API.
        site_id: The ID of the site containing the drive item.
        drive_id: The ID of the drive containing the drive item.

    Returns:
        A SharePointFile or SharePointFolder entity.
    """
    is_folder = 'folder' in item_data
    
    common_attrs = {
        'id': item_data.get('id', ''),
        'name': item_data.get('name', ''),
        'graph_id': item_data.get('id', ''),
        'resource_type': 'folder' if is_folder else 'file',
        'site_id': site_id,
        'drive_id': drive_id,
        'web_url': item_data.get('webUrl', ''),
        'size': item_data.get('size', 0),
        'created_by': item_data.get('createdBy', {}).get('user', {}).get('displayName', ''),
        'last_modified_by': item_data.get('lastModifiedBy', {}).get('user', {}).get('displayName', ''),
        'parent_reference': item_data.get('parentReference', {}).get('id', ''),
        'shared': '@microsoft.graph.downloadUrl' in item_data,
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'properties': {}
    }
    
    if is_folder:
        return SharePointFolder(
            **common_attrs,
            child_count=item_data.get('folder', {}).get('childCount', 0),
            special_folder=item_data.get('specialFolder', {}),
            sharing_info=item_data.get('sharingInfo', {})
        )
    else:
        return SharePointFile(
            **common_attrs,
            file_type=item_data.get('file', {}).get('mimeType', ''),
            content_type=item_data.get('contentType', {}).get('name', ''),
            etag=item_data.get('eTag', ''),
            sharing_info=item_data.get('sharingInfo', {}),
            virus_status=item_data.get('file', {}).get('virusStatus', ''),
            checkout_info=item_data.get('file', {}).get('checkoutInfo', {}),
            version_info=item_data.get('file', {}).get('versionInfo', {})
        )


def validate_sharepoint_entity(entity: Any, schema_class: type) -> List[str]:
    """
    Validates a SharePoint entity against a schema class.

    Args:
        entity: The entity to validate.
        schema_class: The schema class to validate against.

    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    return validate_entity(entity, schema_class)
"""