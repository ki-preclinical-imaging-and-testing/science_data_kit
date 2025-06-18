"""
File Models for Science Data Kit

This module defines the core file and folder models used throughout the application.
It serves as the single source of truth for these models to prevent duplicate class definitions.
"""

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo
)

class Folder(StructuredNode):
    """
    Represents a folder in the file system.
    """
    uid = UniqueIdProperty()
    filepath = StringProperty(unique_index=True)
    is_in = RelationshipTo('Folder', 'IS_IN')

class File(StructuredNode):
    """
    Represents a file in the file system.
    """
    uid = UniqueIdProperty()
    filepath = StringProperty(unique_index=True)
    is_in = RelationshipTo('Folder', 'IS_IN')