"""
Science Data Kit - Dropbox Extension
Entities Module

This module provides entity schemas for Dropbox files and folders that integrate
with the Science Data Kit core entity schemas.
"""

import logging
from typing import Dict, Any, Optional, List, Union, ClassVar
from datetime import datetime
from uuid import uuid4

from science_data_kit.core.models.entity_schemas import (
    BaseEntity,
    File,
    ComplexProperty,
    ComplexPropertySchema,
    PropertyType,
    validate_entity
)

logger = logging.getLogger(__name__)

# Define Dropbox-specific complex property schemas
DROPBOX_METADATA_SCHEMA = ComplexPropertySchema(
    property_type=PropertyType.OBJECT,
    properties={
        "id": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Dropbox file/folder ID",
            required=True
        ),
        "path": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Dropbox path",
            required=True
        ),
        "content_hash": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Content hash for files",
            required=False
        ),
        "shared": ComplexPropertySchema(
            property_type=PropertyType.BOOLEAN,
            description="Whether the item is shared",
            required=False
        ),
        "shared_folder_id": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="ID of the shared folder",
            required=False
        ),
        "parent_shared_folder_id": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="ID of the parent shared folder",
            required=False
        ),
        "sharing_info": ComplexPropertySchema(
            property_type=PropertyType.OBJECT,
            description="Sharing information",
            required=False
        ),
        "team_member_id": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Team member ID for team files",
            required=False
        )
    }
)

DROPBOX_SHARING_SCHEMA = ComplexPropertySchema(
    property_type=PropertyType.OBJECT,
    properties={
        "shared_link": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Shared link URL",
            required=False
        ),
        "shared_link_metadata": ComplexPropertySchema(
            property_type=PropertyType.OBJECT,
            description="Shared link metadata",
            required=False
        ),
        "access_level": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="Access level (viewer, editor, owner)",
            required=False
        ),
        "shared_folder_id": ComplexPropertySchema(
            property_type=PropertyType.STRING,
            description="ID of the shared folder",
            required=False
        ),
        "permissions": ComplexPropertySchema(
            property_type=PropertyType.ARRAY,
            description="List of permissions",
            required=False
        ),
        "shared_with": ComplexPropertySchema(
            property_type=PropertyType.ARRAY,
            description="List of users/groups the item is shared with",
            required=False
        )
    }
)

class DropboxFile(File):
    """
    Entity schema for Dropbox files.

    This class extends the core File entity schema with Dropbox-specific properties.
    """

    entity_type: ClassVar[str] = "dropbox_file"

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        description: str = "",
        file_path: str = "",
        file_type: str = "",
        size_bytes: int = 0,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        dropbox_id: str = "",
        dropbox_path: str = "",
        content_hash: Optional[str] = None,
        sharing_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize a Dropbox file entity.

        Args:
            id: Entity ID (generated if not provided)
            name: File name
            description: File description
            file_path: Local file path
            file_type: File type/extension
            size_bytes: File size in bytes
            created_at: Creation timestamp
            modified_at: Last modification timestamp
            dropbox_id: Dropbox file ID
            dropbox_path: Dropbox file path
            content_hash: Dropbox content hash
            sharing_info: Dropbox sharing information
            **kwargs: Additional properties
        """
        # Initialize the base File entity
        super().__init__(
            id=id or str(uuid4()),
            name=name,
            description=description,
            file_path=file_path,
            file_type=file_type,
            size_bytes=size_bytes,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
            **kwargs
        )

        # Add Dropbox-specific complex properties
        dropbox_metadata = {
            "id": dropbox_id,
            "path": dropbox_path
        }

        if content_hash:
            dropbox_metadata["content_hash"] = content_hash

        if sharing_info:
            dropbox_metadata["sharing_info"] = sharing_info

        self.add_complex_property(
            "dropbox_metadata",
            ComplexProperty(
                schema=DROPBOX_METADATA_SCHEMA,
                value=dropbox_metadata
            )
        )

        if sharing_info:
            self.add_complex_property(
                "dropbox_sharing",
                ComplexProperty(
                    schema=DROPBOX_SHARING_SCHEMA,
                    value={
                        "shared_link": sharing_info.get("shared_link"),
                        "access_level": sharing_info.get("access_level"),
                        "shared_folder_id": sharing_info.get("shared_folder_id"),
                        "permissions": sharing_info.get("permissions"),
                        "shared_with": sharing_info.get("shared_with")
                    }
                )
            )

    @classmethod
    def from_dropbox_metadata(cls, metadata: Dict[str, Any]) -> 'DropboxFile':
        """
        Create a DropboxFile entity from Dropbox metadata.

        Args:
            metadata: Dropbox file metadata dictionary

        Returns:
            DropboxFile entity
        """
        # Extract basic file information
        name = metadata.get('name', '')
        file_type = name.split('.')[-1] if '.' in name else ''

        # Create the entity
        return cls(
            name=name,
            description=f"Dropbox file: {metadata.get('path', '')}",
            file_path=metadata.get('path', ''),
            file_type=file_type,
            size_bytes=metadata.get('size', 0),
            created_at=None,  # Dropbox doesn't provide creation time
            modified_at=metadata.get('modified'),
            dropbox_id=metadata.get('id', ''),
            dropbox_path=metadata.get('path', ''),
            content_hash=metadata.get('content_hash'),
            sharing_info=metadata.get('sharing_info')
        )

class DropboxFolder(BaseEntity):
    """
    Entity schema for Dropbox folders.

    This class extends the core BaseEntity schema for Dropbox folders.
    """

    entity_type: ClassVar[str] = "dropbox_folder"

    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        description: str = "",
        dropbox_id: str = "",
        dropbox_path: str = "",
        sharing_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize a Dropbox folder entity.

        Args:
            id: Entity ID (generated if not provided)
            name: Folder name
            description: Folder description
            dropbox_id: Dropbox folder ID
            dropbox_path: Dropbox folder path
            sharing_info: Dropbox sharing information
            **kwargs: Additional properties
        """
        # Initialize the base entity
        super().__init__(
            id=id or str(uuid4()),
            name=name,
            description=description,
            **kwargs
        )

        # Add Dropbox-specific complex properties
        dropbox_metadata = {
            "id": dropbox_id,
            "path": dropbox_path
        }

        if sharing_info:
            dropbox_metadata["sharing_info"] = sharing_info

        self.add_complex_property(
            "dropbox_metadata",
            ComplexProperty(
                schema=DROPBOX_METADATA_SCHEMA,
                value=dropbox_metadata
            )
        )

        if sharing_info:
            self.add_complex_property(
                "dropbox_sharing",
                ComplexProperty(
                    schema=DROPBOX_SHARING_SCHEMA,
                    value={
                        "shared_link": sharing_info.get("shared_link"),
                        "access_level": sharing_info.get("access_level"),
                        "shared_folder_id": sharing_info.get("shared_folder_id"),
                        "permissions": sharing_info.get("permissions"),
                        "shared_with": sharing_info.get("shared_with")
                    }
                )
            )

    @classmethod
    def from_dropbox_metadata(cls, metadata: Dict[str, Any]) -> 'DropboxFolder':
        """
        Create a DropboxFolder entity from Dropbox metadata.

        Args:
            metadata: Dropbox folder metadata dictionary

        Returns:
            DropboxFolder entity
        """
        # Create the entity
        return cls(
            name=metadata.get('name', ''),
            description=f"Dropbox folder: {metadata.get('path', '')}",
            dropbox_id=metadata.get('id', ''),
            dropbox_path=metadata.get('path', ''),
            sharing_info=metadata.get('sharing_info')
        )

def validate_dropbox_file(entity: Any) -> bool:
    """
    Validate a DropboxFile entity.

    Args:
        entity: Entity to validate

    Returns:
        True if valid, raises exception otherwise
    """
    return validate_entity(entity, DropboxFile)

def validate_dropbox_folder(entity: Any) -> bool:
    """
    Validate a DropboxFolder entity.

    Args:
        entity: Entity to validate

    Returns:
        True if valid, raises exception otherwise
    """
    return validate_entity(entity, DropboxFolder)

def create_entities_from_dropbox_items(items: List[Dict[str, Any]]) -> List[BaseEntity]:
    """
    Create entity objects from a list of Dropbox items.

    Args:
        items: List of Dropbox item metadata dictionaries

    Returns:
        List of entity objects (DropboxFile or DropboxFolder)
    """
    entities = []

    for item in items:
        if item.get('type') == 'file':
            entities.append(DropboxFile.from_dropbox_metadata(item))
        elif item.get('type') == 'folder':
            entities.append(DropboxFolder.from_dropbox_metadata(item))

    return entities
