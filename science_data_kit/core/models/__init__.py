"""
Entity Models for Science Data Kit

This package provides entity models for the Science Data Kit,
including base entity schemas, versioned entities, and specialized entity schemas.
"""

from .entity_schemas import (
    BaseEntity, Dataset, File, Entity, Relationship, OntologyTerm,
    PropertyType, ComplexPropertySchema, ComplexProperty, VersionedEntity,
    validate_entity
)

from .msgraph_schemas import (
    MicrosoftGraphEntity, User, Group, Message, Event, DriveItem,
    validate_msgraph_entity, convert_msgraph_user, convert_msgraph_group, convert_msgraph_message
)

from .sharepoint_schemas import (
    SharePointSite, SharePointList, SharePointListItem, 
    SharePointDrive, SharePointFile, SharePointFolder,
    convert_msgraph_site, convert_msgraph_list, convert_msgraph_list_item,
    convert_msgraph_drive, convert_msgraph_drive_item, validate_sharepoint_entity
)

__all__ = [
    # Base entity schemas
    'BaseEntity', 'Dataset', 'File', 'Entity', 'Relationship', 'OntologyTerm',
    'PropertyType', 'ComplexPropertySchema', 'ComplexProperty', 'VersionedEntity',
    'validate_entity',
    
    # Microsoft Graph schemas
    'MicrosoftGraphEntity', 'User', 'Group', 'Message', 'Event', 'DriveItem',
    'validate_msgraph_entity', 'convert_msgraph_user', 'convert_msgraph_group', 'convert_msgraph_message',
    
    # SharePoint schemas
    'SharePointSite', 'SharePointList', 'SharePointListItem', 
    'SharePointDrive', 'SharePointFile', 'SharePointFolder',
    'convert_msgraph_site', 'convert_msgraph_list', 'convert_msgraph_list_item',
    'convert_msgraph_drive', 'convert_msgraph_drive_item', 'validate_sharepoint_entity'
]
"""