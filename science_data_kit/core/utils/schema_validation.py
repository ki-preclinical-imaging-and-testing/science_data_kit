"""
Schema Validation Utilities for Science Data Kit

This module provides utilities for validating data against schemas defined in
science_data_kit.core.models.entity_schemas.
"""

from typing import Dict, List, Any, Type, Union, Optional, Callable
import json
import re
from datetime import datetime
from science_data_kit.core.models.entity_schemas import BaseEntity


def validate_type(value: Any, expected_type: Type) -> List[str]:
    """
    Validates that a value is of the expected type.
    
    Args:
        value: The value to validate.
        expected_type: The expected type.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    errors = []
    
    # Handle None values
    if value is None:
        # If the expected type is Optional, None is valid
        if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Union:
            if type(None) in expected_type.__args__:
                return errors
        errors.append(f"Value is None, expected {expected_type}")
        return errors
    
    # Handle Union types
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is Union:
        valid_types = [t for t in expected_type.__args__ if t is not type(None)]
        if not any(isinstance(value, t) for t in valid_types):
            errors.append(f"Invalid type. Expected one of {valid_types}, got {type(value)}")
        return errors
    
    # Handle List types
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is list:
        if not isinstance(value, list):
            errors.append(f"Invalid type. Expected list, got {type(value)}")
            return errors
        
        # Validate each item in the list
        item_type = expected_type.__args__[0]
        for i, item in enumerate(value):
            item_errors = validate_type(item, item_type)
            for error in item_errors:
                errors.append(f"Item at index {i}: {error}")
        return errors
    
    # Handle Dict types
    if hasattr(expected_type, "__origin__") and expected_type.__origin__ is dict:
        if not isinstance(value, dict):
            errors.append(f"Invalid type. Expected dict, got {type(value)}")
            return errors
        
        # Validate keys and values
        key_type, value_type = expected_type.__args__
        for k, v in value.items():
            key_errors = validate_type(k, key_type)
            for error in key_errors:
                errors.append(f"Key '{k}': {error}")
            
            value_errors = validate_type(v, value_type)
            for error in value_errors:
                errors.append(f"Value for key '{k}': {error}")
        return errors
    
    # Handle regular types
    if not isinstance(value, expected_type):
        errors.append(f"Invalid type. Expected {expected_type}, got {type(value)}")
    
    return errors


def validate_schema(data: Dict[str, Any], schema_class: Type[BaseEntity]) -> List[str]:
    """
    Validates a dictionary against a schema class.
    
    Args:
        data: The dictionary to validate.
        schema_class: The schema class to validate against.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    errors = []
    
    # Check if data has all required fields from schema_class
    for field_name, field_type in schema_class.__annotations__.items():
        # Skip fields with default values if they're not in the data
        if field_name not in data:
            # Check if the field has a default value in the schema
            if hasattr(schema_class, field_name) and getattr(schema_class, field_name) is not None:
                continue
            errors.append(f"Missing required field: {field_name}")
            continue
        
        # Validate the field value
        field_value = data[field_name]
        field_errors = validate_type(field_value, field_type)
        for error in field_errors:
            errors.append(f"Field '{field_name}': {error}")
    
    return errors


def validate_json_schema(json_data: str, schema_class: Type[BaseEntity]) -> List[str]:
    """
    Validates a JSON string against a schema class.
    
    Args:
        json_data: The JSON string to validate.
        schema_class: The schema class to validate against.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    try:
        data = json.loads(json_data)
        return validate_schema(data, schema_class)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {str(e)}"]


def create_validator(pattern: str, error_message: str) -> Callable[[str], List[str]]:
    """
    Creates a validator function that checks if a string matches a regex pattern.
    
    Args:
        pattern: The regex pattern to match.
        error_message: The error message to return if validation fails.
        
    Returns:
        A validator function that takes a string and returns a list of errors.
    """
    def validator(value: str) -> List[str]:
        if not re.match(pattern, value):
            return [error_message]
        return []
    
    return validator


# Common validators
email_validator = create_validator(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "Invalid email address"
)

url_validator = create_validator(
    r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w%!$&\'()*+,;=:]+)*$',
    "Invalid URL"
)

uuid_validator = create_validator(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    "Invalid UUID format"
)


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> List[str]:
    """
    Validates that a string is in the specified date format.
    
    Args:
        date_str: The date string to validate.
        format_str: The expected date format.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    try:
        datetime.strptime(date_str, format_str)
        return []
    except ValueError:
        return [f"Invalid date format. Expected format: {format_str}"]


def validate_enum(value: Any, allowed_values: List[Any]) -> List[str]:
    """
    Validates that a value is one of the allowed values.
    
    Args:
        value: The value to validate.
        allowed_values: The list of allowed values.
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    if value not in allowed_values:
        return [f"Invalid value. Expected one of: {allowed_values}"]
    return []


def validate_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                  max_value: Optional[Union[int, float]] = None) -> List[str]:
    """
    Validates that a numeric value is within the specified range.
    
    Args:
        value: The value to validate.
        min_value: The minimum allowed value (inclusive).
        max_value: The maximum allowed value (inclusive).
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    errors = []
    
    if min_value is not None and value < min_value:
        errors.append(f"Value {value} is less than minimum {min_value}")
    
    if max_value is not None and value > max_value:
        errors.append(f"Value {value} is greater than maximum {max_value}")
    
    return errors


def validate_length(value: Union[str, List, Dict], min_length: Optional[int] = None, 
                   max_length: Optional[int] = None) -> List[str]:
    """
    Validates that a string, list, or dict has a length within the specified range.
    
    Args:
        value: The value to validate.
        min_length: The minimum allowed length (inclusive).
        max_length: The maximum allowed length (inclusive).
        
    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    errors = []
    length = len(value)
    
    if min_length is not None and length < min_length:
        errors.append(f"Length {length} is less than minimum {min_length}")
    
    if max_length is not None and length > max_length:
        errors.append(f"Length {length} is greater than maximum {max_length}")
    
    return errors