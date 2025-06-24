"""
Core Entity Schemas for Science Data Kit

This module defines the core entity schemas used throughout the Science Data Kit.
These schemas provide a consistent structure for data validation and database operations.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BaseEntity:
    """
    Base class for all entity schemas.
    
    Attributes:
        id: Unique identifier for the entity.
        created_at: Timestamp when the entity was created.
        updated_at: Timestamp when the entity was last updated.
        properties: Additional properties not covered by the schema.
    """
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dataset(BaseEntity):
    """
    Schema for a dataset.
    
    Attributes:
        name: Name of the dataset.
        description: Description of the dataset.
        path: Path to the dataset files.
        files: List of files in the dataset.
        metadata: Additional metadata about the dataset.
    """
    name: str
    description: str = ""
    path: str = ""
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class File(BaseEntity):
    """
    Schema for a file.
    
    Attributes:
        name: Name of the file.
        path: Path to the file.
        size: Size of the file in bytes.
        format: Format of the file.
        dataset_id: ID of the dataset the file belongs to.
        metadata: Additional metadata about the file.
    """
    name: str
    path: str
    size: int = 0
    format: str = ""
    dataset_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity(BaseEntity):
    """
    Schema for a generic entity.
    
    Attributes:
        name: Name of the entity.
        label: Label of the entity (node type in Neo4j).
        description: Description of the entity.
        source: Source of the entity (e.g., dataset, file).
        relationships: List of relationships to other entities.
    """
    name: str
    label: str
    description: str = ""
    source: str = ""
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class Relationship:
    """
    Schema for a relationship between entities.
    
    Attributes:
        source_id: ID of the source entity.
        target_id: ID of the target entity.
        type: Type of the relationship.
        properties: Additional properties of the relationship.
    """
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OntologyTerm(BaseEntity):
    """
    Schema for an ontology term.
    
    Attributes:
        term: The ontology term.
        term_accession: URI or identifier for the term.
        term_source: Source of the term (ontology name).
        definition: Definition of the term.
    """
    term: str
    term_accession: str = ""
    term_source: str = ""
    definition: str = ""


def validate_entity(entity: Any, schema_class: type) -> List[str]:
    """
    Validates an entity against a schema class.
    
    Args:
        entity: The entity to validate.
        schema_class: The schema class to validate against.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    errors = []
    
    # Check if entity has all required fields from schema_class
    for field_name, field_type in schema_class.__annotations__.items():
        if not hasattr(entity, field_name):
            errors.append(f"Missing required field: {field_name}")
            continue
            
        # Get the field value
        field_value = getattr(entity, field_name)
        
        # Check if field value is of the correct type
        if field_value is not None:
            # Handle Union types
            if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
                valid_types = field_type.__args__
                if not any(isinstance(field_value, t) for t in valid_types):
                    errors.append(f"Field {field_name} has invalid type. Expected one of {valid_types}, got {type(field_value)}")
            # Handle regular types
            elif not isinstance(field_value, field_type):
                errors.append(f"Field {field_name} has invalid type. Expected {field_type}, got {type(field_value)}")
    
    return errors