from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo,
    db)
import sys

MODULE_NAME = "utils.registry"


def get_registered_model(class_name):
    """Check if a Neomodel class is already defined and return it if exists."""
    for model in db._NODE_CLASS_REGISTRY.values():
        if model.__name__ == class_name:
            return model
    return None  # Model is not registered


def register_model(class_name, base_class, attributes, relationships=None):
    """
    Registers a Neomodel class dynamically with attributes and relationships.

    Args:
        class_name (str): Name of the class.
        base_class (type): The base Neomodel class (StructuredNode).
        attributes (dict): Dictionary of field names and properties.
        relationships (dict, optional): Dictionary of relationships to other nodes.

    Returns:
        type: The registered Neomodel class.
    """
    # Check if the model is already registered
    for model in db._NODE_CLASS_REGISTRY.values():
        if model.__name__ == class_name:
            return model  # Use existing class

    # ✅ Define new class attributes dynamically, including relationships
    class_attrs = attributes.copy()  # Copy attributes to avoid mutation

    if relationships:
        for rel_name, rel_target in relationships.items():
            class_attrs[rel_name] = RelationshipTo(rel_target, rel_name.upper())  # ✅ Corrected

    # **Step 1: Register Class with Attributes and Relationships**
    new_class = type(class_name, (base_class,), class_attrs)

    # **Step 2: Register in Neomodel’s Registry**
    db._NODE_CLASS_REGISTRY[frozenset({class_name})] = new_class

    # **Step 3: Ensure Python Resolves the Class Properly**
    new_class.__module__ = MODULE_NAME
    sys.modules[MODULE_NAME] = sys.modules[__name__]
    sys.modules[f"{MODULE_NAME}.{class_name}"] = new_class

    return new_class


Folder = register_model(
    "Folder",
    StructuredNode,
    attributes={
        "uid": UniqueIdProperty(),
        "filepath": StringProperty(unique_index=True),
    },
    relationships={
        "is_in": "Folder"  # Reference itself in a self-referential relationship
    }
)

File = register_model(
    "File",
    StructuredNode,
    attributes={
        "uid": UniqueIdProperty(),
        "filepath": StringProperty(unique_index=True),
    },
    relationships={
        "is_in": "Folder"  # Reference itself in a self-referential relationship
    }
)