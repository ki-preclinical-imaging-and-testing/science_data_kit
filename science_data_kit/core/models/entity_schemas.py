"""
Core Entity Schemas for Science Data Kit

This module defines the core entity schemas used throughout the Science Data Kit.
These schemas provide a consistent structure for data validation and database operations.
It also includes versioning support for schema evolution over time.
"""

from typing import Dict, List, Optional, Any, Union, Type, TypeVar, ClassVar
from dataclasses import dataclass, field
from datetime import datetime


T = TypeVar('T', bound='VersionedEntity')


@dataclass
class VersionedEntity:
    """
    Base class for versioned entities.

    This class provides versioning support for entity schemas, allowing for schema
    evolution over time while maintaining backward compatibility.

    Class Attributes:
        schema_version: The current version of the schema.
        schema_versions: A dictionary mapping version numbers to schema classes.

    Attributes:
        version: The version of the schema used by this instance.
    """
    schema_version: ClassVar[str] = "1.0"
    schema_versions: ClassVar[Dict[str, Type[T]]] = {}

    version: str = field(default="1.0")

    @classmethod
    def register_version(cls, version: str) -> None:
        """
        Register a schema version.

        Args:
            version: The version to register.
        """
        cls.schema_versions[version] = cls

    @classmethod
    def get_version(cls, version: str) -> Type[T]:
        """
        Get a schema class for a specific version.

        Args:
            version: The version to get.

        Returns:
            The schema class for the specified version.

        Raises:
            ValueError: If the version is not registered.
        """
        if version not in cls.schema_versions:
            raise ValueError(f"Version {version} not registered for {cls.__name__}")
        return cls.schema_versions[version]

    @classmethod
    def migrate(cls, entity: Any, target_version: str) -> T:
        """
        Migrate an entity from its current version to a target version.

        Args:
            entity: The entity to migrate.
            target_version: The target version to migrate to.

        Returns:
            The migrated entity.

        Raises:
            ValueError: If the target version is not registered.
        """
        if target_version not in cls.schema_versions:
            raise ValueError(f"Target version {target_version} not registered for {cls.__name__}")

        # If the entity is already at the target version, return it
        if hasattr(entity, "version") and entity.version == target_version:
            return entity

        # Get the target schema class
        target_cls = cls.schema_versions[target_version]

        # Create a new instance of the target schema class with the entity's attributes
        migrated = target_cls()

        # Copy attributes from the entity to the migrated entity
        for field_name, field_type in target_cls.__annotations__.items():
            if hasattr(entity, field_name):
                setattr(migrated, field_name, getattr(entity, field_name))

        # Set the version
        migrated.version = target_version

        return migrated


@dataclass
class BaseEntity(VersionedEntity):
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
class Relationship(VersionedEntity):
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
