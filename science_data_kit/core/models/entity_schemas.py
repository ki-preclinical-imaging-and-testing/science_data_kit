"""
Core Entity Schemas for Science Data Kit

This module defines the core entity schemas used throughout the Science Data Kit.
These schemas provide a consistent structure for data validation and database operations.
It also includes versioning support for schema evolution over time.
It also provides support for complex property types and validation.
"""

from typing import Dict, List, Optional, Any, Union, Type, TypeVar, ClassVar, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from enum import Enum


T = TypeVar('T', bound='VersionedEntity')
P = TypeVar('P', bound='ComplexProperty')


class PropertyType(Enum):
    """
    Enum for property types.

    This enum defines the different types of properties that can be used in complex property schemas.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    REFERENCE = "reference"
    GEO_POINT = "geo_point"
    GEO_SHAPE = "geo_shape"
    BINARY = "binary"
    ANY = "any"


@dataclass
class ComplexPropertySchema:
    """
    Schema for complex properties.

    This class defines the schema for a complex property, including its type, validation rules,
    and nested properties for object types.

    Attributes:
        property_type: The type of the property.
        required: Whether the property is required.
        default: The default value for the property.
        description: A description of the property.
        validators: A list of validator functions for the property.
        properties: For object types, a dictionary of nested property schemas.
        items: For array types, the schema for array items.
        min_length: For string and array types, the minimum length.
        max_length: For string and array types, the maximum length.
        pattern: For string types, a regex pattern to validate against.
        minimum: For numeric types, the minimum value.
        maximum: For numeric types, the maximum value.
        enum_values: For string types, a list of allowed values.
        format: For string types, a format specifier (e.g., "email", "uri").
    """
    property_type: PropertyType
    required: bool = False
    default: Any = None
    description: str = ""
    validators: List[Callable[[Any], bool]] = field(default_factory=list)
    properties: Dict[str, 'ComplexPropertySchema'] = field(default_factory=dict)
    items: Optional['ComplexPropertySchema'] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    enum_values: Optional[List[Any]] = None
    format: Optional[str] = None

    def validate(self, value: Any) -> List[str]:
        """
        Validate a value against this schema.

        Args:
            value: The value to validate.

        Returns:
            A list of validation errors, or an empty list if validation passes.
        """
        errors = []

        # Check if value is required but missing
        if self.required and value is None:
            errors.append("Value is required but missing")
            return errors

        # If value is None and not required, it's valid
        if value is None:
            return errors

        # Type validation
        if self.property_type == PropertyType.STRING:
            if not isinstance(value, str):
                errors.append(f"Expected string, got {type(value).__name__}")
            else:
                # String-specific validations
                if self.min_length is not None and len(value) < self.min_length:
                    errors.append(f"String length {len(value)} is less than minimum length {self.min_length}")
                if self.max_length is not None and len(value) > self.max_length:
                    errors.append(f"String length {len(value)} is greater than maximum length {self.max_length}")
                if self.pattern is not None:
                    import re
                    if not re.match(self.pattern, value):
                        errors.append(f"String does not match pattern {self.pattern}")
                if self.enum_values is not None and value not in self.enum_values:
                    errors.append(f"Value {value} is not one of the allowed values: {self.enum_values}")

        elif self.property_type == PropertyType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"Expected integer, got {type(value).__name__}")
            else:
                # Integer-specific validations
                if self.minimum is not None and value < self.minimum:
                    errors.append(f"Value {value} is less than minimum {self.minimum}")
                if self.maximum is not None and value > self.maximum:
                    errors.append(f"Value {value} is greater than maximum {self.maximum}")

        elif self.property_type == PropertyType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"Expected float, got {type(value).__name__}")
            else:
                # Float-specific validations
                if self.minimum is not None and value < self.minimum:
                    errors.append(f"Value {value} is less than minimum {self.minimum}")
                if self.maximum is not None and value > self.maximum:
                    errors.append(f"Value {value} is greater than maximum {self.maximum}")

        elif self.property_type == PropertyType.BOOLEAN:
            if not isinstance(value, bool):
                errors.append(f"Expected boolean, got {type(value).__name__}")

        elif self.property_type == PropertyType.DATETIME:
            if not isinstance(value, datetime):
                errors.append(f"Expected datetime, got {type(value).__name__}")

        elif self.property_type == PropertyType.ARRAY:
            if not isinstance(value, list):
                errors.append(f"Expected array, got {type(value).__name__}")
            else:
                # Array-specific validations
                if self.min_length is not None and len(value) < self.min_length:
                    errors.append(f"Array length {len(value)} is less than minimum length {self.min_length}")
                if self.max_length is not None and len(value) > self.max_length:
                    errors.append(f"Array length {len(value)} is greater than maximum length {self.max_length}")

                # Validate array items if schema is provided
                if self.items is not None:
                    for i, item in enumerate(value):
                        item_errors = self.items.validate(item)
                        if item_errors:
                            errors.extend([f"Item at index {i}: {error}" for error in item_errors])

        elif self.property_type == PropertyType.OBJECT:
            if not isinstance(value, dict):
                errors.append(f"Expected object, got {type(value).__name__}")
            else:
                # Object-specific validations
                for prop_name, prop_schema in self.properties.items():
                    if prop_name in value:
                        prop_errors = prop_schema.validate(value[prop_name])
                        if prop_errors:
                            errors.extend([f"Property '{prop_name}': {error}" for error in prop_errors])
                    elif prop_schema.required:
                        errors.append(f"Required property '{prop_name}' is missing")

        elif self.property_type == PropertyType.GEO_POINT:
            if not isinstance(value, dict) or 'latitude' not in value or 'longitude' not in value:
                errors.append("Expected geo_point object with latitude and longitude properties")
            else:
                # Geo point-specific validations
                lat = value.get('latitude')
                lng = value.get('longitude')
                if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
                    errors.append(f"Invalid latitude: {lat}. Must be between -90 and 90")
                if not isinstance(lng, (int, float)) or lng < -180 or lng > 180:
                    errors.append(f"Invalid longitude: {lng}. Must be between -180 and 180")

        elif self.property_type == PropertyType.BINARY:
            if not isinstance(value, bytes):
                errors.append(f"Expected binary data, got {type(value).__name__}")

        # Run custom validators
        for validator in self.validators:
            if not validator(value):
                errors.append(f"Failed custom validation: {validator.__name__}")

        return errors


@dataclass
class ComplexProperty:
    """
    Class for complex properties.

    This class represents a complex property with a schema and value.

    Attributes:
        schema: The schema for this property.
        value: The value of the property.
    """
    schema: ComplexPropertySchema
    value: Any = None

    def __post_init__(self):
        """
        Initialize the property with default value if value is None.
        """
        if self.value is None and self.schema.default is not None:
            self.value = self.schema.default

    def validate(self) -> List[str]:
        """
        Validate the property value against its schema.

        Returns:
            A list of validation errors, or an empty list if validation passes.
        """
        return self.schema.validate(self.value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the property to a dictionary.

        Returns:
            A dictionary representation of the property.
        """
        if self.schema.property_type == PropertyType.OBJECT and isinstance(self.value, dict):
            result = {}
            for key, value in self.value.items():
                if isinstance(value, ComplexProperty):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
            return result
        elif self.schema.property_type == PropertyType.ARRAY and isinstance(self.value, list):
            return [item.to_dict() if isinstance(item, ComplexProperty) else item for item in self.value]
        elif self.schema.property_type == PropertyType.DATETIME and isinstance(self.value, datetime):
            return self.value.isoformat()
        else:
            return self.value

    @classmethod
    def from_dict(cls, schema: ComplexPropertySchema, data: Dict[str, Any]) -> 'ComplexProperty':
        """
        Create a complex property from a dictionary.

        Args:
            schema: The schema for the property.
            data: The dictionary data.

        Returns:
            A new ComplexProperty instance.
        """
        if schema.property_type == PropertyType.OBJECT:
            value = {}
            for prop_name, prop_schema in schema.properties.items():
                if prop_name in data:
                    if prop_schema.property_type == PropertyType.OBJECT:
                        value[prop_name] = cls.from_dict(prop_schema, data[prop_name])
                    elif prop_schema.property_type == PropertyType.ARRAY and prop_schema.items:
                        value[prop_name] = [
                            cls.from_dict(prop_schema.items, item) if prop_schema.items.property_type == PropertyType.OBJECT else item
                            for item in data[prop_name]
                        ]
                    else:
                        value[prop_name] = data[prop_name]
            return cls(schema=schema, value=value)
        else:
            return cls(schema=schema, value=data)

    def to_json(self) -> str:
        """
        Convert the property to a JSON string.

        Returns:
            A JSON string representation of the property.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, schema: ComplexPropertySchema, json_str: str) -> 'ComplexProperty':
        """
        Create a complex property from a JSON string.

        Args:
            schema: The schema for the property.
            json_str: The JSON string.

        Returns:
            A new ComplexProperty instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(schema, data)


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
        name: Name of the entity.
        version: The version of the schema used by this instance.
        created_at: Timestamp when the entity was created.
        updated_at: Timestamp when the entity was last updated.
        properties: Additional properties not covered by the schema.
        complex_properties: Complex properties with schema validation.
    """
    id: str
    name: str
    version: str = field(default="1.0")
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    properties: Dict[str, Any] = field(default_factory=dict)
    complex_properties: Dict[str, ComplexProperty] = field(default_factory=dict)

    def add_complex_property(self, name: str, complex_property: ComplexProperty) -> None:
        """
        Add a complex property to the entity.

        Args:
            name: The name of the property.
            complex_property: The complex property to add.
        """
        self.complex_properties[name] = complex_property

    def get_complex_property(self, name: str) -> Optional[ComplexProperty]:
        """
        Get a complex property by name.

        Args:
            name: The name of the property.

        Returns:
            The complex property, or None if not found.
        """
        return self.complex_properties.get(name)

    def validate_complex_properties(self) -> List[str]:
        """
        Validate all complex properties.

        Returns:
            A list of validation errors, or an empty list if validation passes.
        """
        errors = []
        for name, prop in self.complex_properties.items():
            prop_errors = prop.validate()
            if prop_errors:
                errors.extend([f"Property '{name}': {error}" for error in prop_errors])
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entity to a dictionary.

        Returns:
            A dictionary representation of the entity.
        """
        result = {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "properties": self.properties.copy()
        }

        # Add complex properties
        if self.complex_properties:
            result["complex_properties"] = {
                name: prop.to_dict() for name, prop in self.complex_properties.items()
            }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """
        Create an entity from a dictionary.

        Args:
            data: The dictionary data.

        Returns:
            A new BaseEntity instance.
        """
        entity = cls(id=data["id"], name=data.get("name", ""))

        # Set basic properties
        if "created_at" in data:
            entity.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            entity.updated_at = datetime.fromisoformat(data["updated_at"])
        if "version" in data:
            entity.version = data["version"]
        if "properties" in data:
            entity.properties = data["properties"]

        # Set complex properties if schemas are provided
        if "complex_properties" in data and hasattr(cls, "complex_property_schemas"):
            schemas = getattr(cls, "complex_property_schemas", {})
            for name, prop_data in data["complex_properties"].items():
                if name in schemas:
                    entity.complex_properties[name] = ComplexProperty.from_dict(
                        schemas[name], prop_data
                    )

        return entity


@dataclass
class Dataset(BaseEntity):
    """
    Schema for a dataset.

    Attributes:
        description: Description of the dataset.
        path: Path to the dataset files.
        files: List of files in the dataset.
        metadata: Additional metadata about the dataset.
    """
    description: str = ""
    path: str = ""
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class File(BaseEntity):
    """
    Schema for a file.

    Attributes:
        path: Path to the file.
        size: Size of the file in bytes.
        format: Format of the file.
        dataset_id: ID of the dataset the file belongs to.
        metadata: Additional metadata about the file.
    """
    path: str = ""
    size: int = 0
    format: str = ""
    dataset_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity(BaseEntity):
    """
    Schema for a generic entity.

    Attributes:
        label: Label of the entity (node type in Neo4j).
        description: Description of the entity.
        source: Source of the entity (e.g., dataset, file).
        relationships: List of relationships to other entities.
    """
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

    # Validate complex properties if the entity has them
    if hasattr(entity, 'validate_complex_properties'):
        complex_property_errors = entity.validate_complex_properties()
        if complex_property_errors:
            errors.extend(complex_property_errors)

    return errors


# Example of using complex properties
def create_person_schema() -> ComplexPropertySchema:
    """
    Create a schema for a person.

    Returns:
        A ComplexPropertySchema for a person.
    """
    # Create schema for address
    address_schema = ComplexPropertySchema(
        property_type=PropertyType.OBJECT,
        description="Person's address",
        properties={
            "street": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="Street address"
            ),
            "city": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="City"
            ),
            "state": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="State or province"
            ),
            "postal_code": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="Postal code"
            ),
            "country": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="Country"
            ),
            "coordinates": ComplexPropertySchema(
                property_type=PropertyType.GEO_POINT,
                required=False,
                description="Geographic coordinates"
            )
        }
    )

    # Create schema for contact information
    contact_schema = ComplexPropertySchema(
        property_type=PropertyType.OBJECT,
        description="Person's contact information",
        properties={
            "email": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="Email address",
                pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            ),
            "phone": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=False,
                description="Phone number"
            ),
            "social_media": ComplexPropertySchema(
                property_type=PropertyType.ARRAY,
                required=False,
                description="Social media profiles",
                items=ComplexPropertySchema(
                    property_type=PropertyType.OBJECT,
                    properties={
                        "platform": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=True,
                            description="Social media platform"
                        ),
                        "username": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=True,
                            description="Username on the platform"
                        ),
                        "url": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=False,
                            description="URL to the profile"
                        )
                    }
                )
            )
        }
    )

    # Create schema for person
    return ComplexPropertySchema(
        property_type=PropertyType.OBJECT,
        description="Person information",
        properties={
            "first_name": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="First name"
            ),
            "last_name": ComplexPropertySchema(
                property_type=PropertyType.STRING,
                required=True,
                description="Last name"
            ),
            "birth_date": ComplexPropertySchema(
                property_type=PropertyType.DATETIME,
                required=False,
                description="Date of birth"
            ),
            "address": address_schema,
            "contact": contact_schema,
            "skills": ComplexPropertySchema(
                property_type=PropertyType.ARRAY,
                required=False,
                description="List of skills",
                items=ComplexPropertySchema(
                    property_type=PropertyType.STRING
                )
            ),
            "education": ComplexPropertySchema(
                property_type=PropertyType.ARRAY,
                required=False,
                description="Education history",
                items=ComplexPropertySchema(
                    property_type=PropertyType.OBJECT,
                    properties={
                        "institution": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=True,
                            description="Educational institution"
                        ),
                        "degree": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=True,
                            description="Degree obtained"
                        ),
                        "field": ComplexPropertySchema(
                            property_type=PropertyType.STRING,
                            required=True,
                            description="Field of study"
                        ),
                        "start_date": ComplexPropertySchema(
                            property_type=PropertyType.DATETIME,
                            required=False,
                            description="Start date"
                        ),
                        "end_date": ComplexPropertySchema(
                            property_type=PropertyType.DATETIME,
                            required=False,
                            description="End date"
                        )
                    }
                )
            )
        }
    )
