"""
Plugin configuration schema for Science Data Kit.

This module provides classes for defining and validating plugin configurations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
import json
import os
import re
from pathlib import Path


class ConfigFieldType(Enum):
    """Types of configuration fields."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    SECRET = "secret"  # For passwords, API keys, etc.
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"
    ENUM = "enum"  # For fields with predefined values


@dataclass
class ConfigField:
    """Definition of a configuration field."""
    name: str
    field_type: ConfigFieldType
    description: str
    required: bool = True
    default: Any = None
    enum_values: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None  # Regex pattern for validation
    nested_fields: Optional[List['ConfigField']] = None  # For OBJECT type
    array_item_type: Optional[ConfigFieldType] = None  # For ARRAY type
    secret: bool = False  # Whether to mask the value in logs and UI

    def validate(self, value: Any) -> bool:
        """
        Validate a value against this field's constraints.

        Args:
            value: The value to validate

        Returns:
            True if the value is valid, False otherwise
        """
        if value is None:
            return not self.required

        if self.field_type == ConfigFieldType.STRING:
            if not isinstance(value, str):
                return False
            if self.pattern and not re.match(self.pattern, value):
                return False

        elif self.field_type == ConfigFieldType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.field_type == ConfigFieldType.FLOAT:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.field_type == ConfigFieldType.BOOLEAN:
            return isinstance(value, bool)

        elif self.field_type == ConfigFieldType.ENUM:
            return value in (self.enum_values or [])

        elif self.field_type == ConfigFieldType.OBJECT:
            if not isinstance(value, dict):
                return False
            if self.nested_fields:
                for field in self.nested_fields:
                    if field.name in value:
                        if not field.validate(value[field.name]):
                            return False
                    elif field.required:
                        return False

        elif self.field_type == ConfigFieldType.ARRAY:
            if not isinstance(value, list):
                return False
            if self.array_item_type:
                for item in value:
                    if not self._validate_array_item(item):
                        return False

        elif self.field_type == ConfigFieldType.FILE_PATH:
            if not isinstance(value, str):
                return False
            path = Path(value)
            if not path.is_file():
                return False

        elif self.field_type == ConfigFieldType.DIRECTORY_PATH:
            if not isinstance(value, str):
                return False
            path = Path(value)
            if not path.is_dir():
                return False

        return True

    def _validate_array_item(self, item: Any) -> bool:
        """Validate an item in an array field."""
        if self.array_item_type == ConfigFieldType.STRING:
            return isinstance(item, str)
        elif self.array_item_type == ConfigFieldType.INTEGER:
            return isinstance(item, int)
        elif self.array_item_type == ConfigFieldType.FLOAT:
            return isinstance(item, (int, float))
        elif self.array_item_type == ConfigFieldType.BOOLEAN:
            return isinstance(item, bool)
        elif self.array_item_type == ConfigFieldType.OBJECT:
            return isinstance(item, dict)
        elif self.array_item_type == ConfigFieldType.ARRAY:
            return isinstance(item, list)
        return True


@dataclass
class PluginConfigSchema:
    """Schema for plugin configuration."""
    fields: List[ConfigField]
    version: str = "1.0"

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against this schema.

        Args:
            config: The configuration to validate

        Returns:
            True if the configuration is valid, False otherwise
        """
        for field in self.fields:
            if field.name in config:
                if not field.validate(config[field.name]):
                    return False
            elif field.required:
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema to a dictionary.

        Returns:
            Dictionary representation of the schema
        """
        return {
            "version": self.version,
            "fields": [self._field_to_dict(field) for field in self.fields]
        }

    def _field_to_dict(self, field: ConfigField) -> Dict[str, Any]:
        """Convert a field to a dictionary."""
        result = {
            "name": field.name,
            "type": field.field_type.value,
            "description": field.description,
            "required": field.required
        }

        if field.default is not None:
            result["default"] = field.default

        if field.enum_values:
            result["enum_values"] = field.enum_values

        if field.min_value is not None:
            result["min_value"] = field.min_value

        if field.max_value is not None:
            result["max_value"] = field.max_value

        if field.pattern:
            result["pattern"] = field.pattern

        if field.nested_fields:
            result["nested_fields"] = [
                self._field_to_dict(nested) for nested in field.nested_fields
            ]

        if field.array_item_type:
            result["array_item_type"] = field.array_item_type.value

        if field.secret:
            result["secret"] = field.secret

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfigSchema':
        """
        Create a schema from a dictionary.

        Args:
            data: Dictionary representation of the schema

        Returns:
            PluginConfigSchema instance
        """
        fields = [cls._dict_to_field(field_data) for field_data in data.get("fields", [])]
        return cls(fields=fields, version=data.get("version", "1.0"))

    @classmethod
    def _dict_to_field(cls, data: Dict[str, Any]) -> ConfigField:
        """Create a field from a dictionary."""
        nested_fields = None
        if "nested_fields" in data:
            nested_fields = [cls._dict_to_field(nested) for nested in data["nested_fields"]]

        array_item_type = None
        if "array_item_type" in data:
            array_item_type = ConfigFieldType(data["array_item_type"])

        return ConfigField(
            name=data["name"],
            field_type=ConfigFieldType(data["type"]),
            description=data["description"],
            required=data.get("required", True),
            default=data.get("default"),
            enum_values=data.get("enum_values"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            pattern=data.get("pattern"),
            nested_fields=nested_fields,
            array_item_type=array_item_type,
            secret=data.get("secret", False)
        )

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the schema to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the schema
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'PluginConfigSchema':
        """
        Create a schema from a JSON string.

        Args:
            json_str: JSON string representation of the schema

        Returns:
            PluginConfigSchema instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, file_path: str) -> 'PluginConfigSchema':
        """
        Create a schema from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            PluginConfigSchema instance
        """
        with open(file_path, 'r') as f:
            return cls.from_json(f.read())

    def to_file(self, file_path: str, indent: int = 2) -> None:
        """
        Write the schema to a JSON file.

        Args:
            file_path: Path to the JSON file
            indent: Number of spaces for indentation
        """
        with open(file_path, 'w') as f:
            f.write(self.to_json(indent=indent))


def create_default_config(schema: PluginConfigSchema) -> Dict[str, Any]:
    """
    Create a default configuration based on a schema.

    Args:
        schema: The configuration schema

    Returns:
        Default configuration dictionary
    """
    config = {}
    for field in schema.fields:
        if field.default is not None:
            config[field.name] = field.default
        elif field.required:
            if field.field_type == ConfigFieldType.STRING:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.INTEGER:
                config[field.name] = 0
            elif field.field_type == ConfigFieldType.FLOAT:
                config[field.name] = 0.0
            elif field.field_type == ConfigFieldType.BOOLEAN:
                config[field.name] = False
            elif field.field_type == ConfigFieldType.OBJECT:
                if field.nested_fields:
                    config[field.name] = _create_nested_default_config(field.nested_fields)
                else:
                    config[field.name] = {}
            elif field.field_type == ConfigFieldType.ARRAY:
                config[field.name] = []
            elif field.field_type == ConfigFieldType.ENUM and field.enum_values:
                config[field.name] = field.enum_values[0]
            elif field.field_type == ConfigFieldType.FILE_PATH:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.DIRECTORY_PATH:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.SECRET:
                config[field.name] = ""
    return config


def _create_nested_default_config(fields: List[ConfigField]) -> Dict[str, Any]:
    """Create default configuration for nested fields."""
    config = {}
    for field in fields:
        if field.default is not None:
            config[field.name] = field.default
        elif field.required:
            if field.field_type == ConfigFieldType.STRING:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.INTEGER:
                config[field.name] = 0
            elif field.field_type == ConfigFieldType.FLOAT:
                config[field.name] = 0.0
            elif field.field_type == ConfigFieldType.BOOLEAN:
                config[field.name] = False
            elif field.field_type == ConfigFieldType.OBJECT:
                if field.nested_fields:
                    config[field.name] = _create_nested_default_config(field.nested_fields)
                else:
                    config[field.name] = {}
            elif field.field_type == ConfigFieldType.ARRAY:
                config[field.name] = []
            elif field.field_type == ConfigFieldType.ENUM and field.enum_values:
                config[field.name] = field.enum_values[0]
            elif field.field_type == ConfigFieldType.FILE_PATH:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.DIRECTORY_PATH:
                config[field.name] = ""
            elif field.field_type == ConfigFieldType.SECRET:
                config[field.name] = ""
    return config
