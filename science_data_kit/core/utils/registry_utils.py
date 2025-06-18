"""
Registry Utilities for Science Data Kit

This module provides utilities for dynamically registering Neo4j models using neomodel.
It includes functions for checking if a model is already registered and registering new models.
"""

from typing import Dict, Any, Optional, Type, List, Union
import sys
from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo, db
)
from science_data_kit.core.models.file_models import Folder, File

# Module name for registration
MODULE_NAME = "science_data_kit.core.utils.registry_utils"

def get_registered_model(class_name: str) -> Optional[Type[StructuredNode]]:
    """
    Check if a Neomodel class is already defined and return it if exists.

    Args:
        class_name: The name of the class to check.

    Returns:
        The registered model class if found, None otherwise.
    """
    for model in db._NODE_CLASS_REGISTRY.values():
        if model.__name__ == class_name:
            return model
    return None  # Model is not registered

def register_model(
    class_name: str, 
    base_class: Type[StructuredNode], 
    attributes: Dict[str, Any], 
    relationships: Optional[Dict[str, str]] = None
) -> Type[StructuredNode]:
    """
    Registers a Neomodel class dynamically with attributes and relationships.

    Args:
        class_name: Name of the class.
        base_class: The base Neomodel class (StructuredNode).
        attributes: Dictionary of field names and properties.
        relationships: Dictionary of relationships to other nodes.

    Returns:
        The registered Neomodel class.
    """
    # Check if the model is already registered
    existing_model = get_registered_model(class_name)
    if existing_model:
        return existing_model  # Use existing class

    # Define new class attributes dynamically, including relationships
    class_attrs = attributes.copy()  # Copy attributes to avoid mutation

    if relationships:
        for rel_name, rel_target in relationships.items():
            class_attrs[rel_name] = RelationshipTo(rel_target, rel_name.upper())

    # Step 1: Register Class with Attributes and Relationships
    new_class = type(class_name, (base_class,), class_attrs)

    # Step 2: Register in Neomodel's Registry
    db._NODE_CLASS_REGISTRY[frozenset({class_name})] = new_class

    # Step 3: Ensure Python Resolves the Class Properly
    new_class.__module__ = MODULE_NAME
    sys.modules[MODULE_NAME] = sys.modules[__name__]
    sys.modules[f"{MODULE_NAME}.{class_name}"] = new_class

    return new_class

def register_models(
    model_definitions: Dict[str, Dict[str, Any]], 
    base_class: Type[StructuredNode] = StructuredNode
) -> Dict[str, Type[StructuredNode]]:
    """
    Registers multiple Neomodel classes at once.

    Args:
        model_definitions: Dictionary mapping class names to model definitions.
            Each model definition should have 'attributes' and optionally 'relationships'.
        base_class: The base Neomodel class to use for all models.

    Returns:
        Dictionary mapping class names to registered model classes.
    """
    registered_models = {}

    for class_name, definition in model_definitions.items():
        attributes = definition.get('attributes', {})
        relationships = definition.get('relationships', {})

        model_class = register_model(class_name, base_class, attributes, relationships)
        registered_models[class_name] = model_class

    return registered_models

