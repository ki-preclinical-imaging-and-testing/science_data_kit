"""
File Models for Science Data Kit

This module defines the core file and folder models used throughout the application.
It serves as the single source of truth for these models to prevent duplicate class definitions.

The implementation includes a check to prevent duplicate class registration in neomodel's registry,
which is particularly important in Streamlit applications where modules can be imported multiple times
during state changes, causing "Class already defined" errors.
"""

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo, db
)

# Check if Folder class is already registered to avoid duplicate registration
# This is especially important in Streamlit context where modules can be imported multiple times
_folder_labels = frozenset({"Folder"})
_file_labels = frozenset({"File"})

# Only define the classes if they're not already in the registry
if _folder_labels not in db._NODE_CLASS_REGISTRY:
    class Folder(StructuredNode):
        """
        Represents a folder in the file system.
        """
        uid = UniqueIdProperty()
        filepath = StringProperty(unique_index=True)
        is_in = RelationshipTo('Folder', 'IS_IN')
else:
    # If already registered, use the existing class
    Folder = db._NODE_CLASS_REGISTRY[_folder_labels]

if _file_labels not in db._NODE_CLASS_REGISTRY:
    class File(StructuredNode):
        """
        Represents a file in the file system.
        """
        uid = UniqueIdProperty()
        filepath = StringProperty(unique_index=True)
        is_in = RelationshipTo('Folder', 'IS_IN')
else:
    # If already registered, use the existing class
    File = db._NODE_CLASS_REGISTRY[_file_labels]
