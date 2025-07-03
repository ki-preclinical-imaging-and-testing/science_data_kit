"""
Data Validation Rules Engine for Science Data Kit

This module provides a comprehensive validation rules engine for data validation
in the Science Data Kit. It allows defining validation rules, rule sets, and
validation contexts for validating data against complex rule sets.
"""

from typing import Dict, List, Optional, Any, Union, Type, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime


class ValidationSeverity(Enum):
    """
    Enum for validation severity levels.
    
    This enum defines the different severity levels for validation errors.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """
    Result of a validation check.
    
    Attributes:
        is_valid: Whether the validation passed.
        message: A message describing the validation result.
        severity: The severity level of the validation result.
        path: The path to the validated element (for nested validations).
    """
    is_valid: bool
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    path: str = ""
    
    def __bool__(self) -> bool:
        """
        Convert to boolean.
        
        Returns:
            True if validation passed, False otherwise.
        """
        return self.is_valid


class ValidationRule:
    """
    Base class for validation rules.
    
    This class defines the interface for validation rules.
    """
    
    def __init__(self, message: str = "", severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a validation rule.
        
        Args:
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        self.message = message
        self.severity = severity
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate a value against this rule.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        raise NotImplementedError("Subclasses must implement validate method")


class RequiredRule(ValidationRule):
    """
    Rule that requires a value to be present and not None.
    """
    
    def __init__(self, message: str = "Value is required", severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a required rule.
        
        Args:
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a value is present and not None.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        is_valid = value is not None
        return ValidationResult(
            is_valid=is_valid,
            message=self.message if not is_valid else "",
            severity=self.severity,
            path=path
        )


class TypeRule(ValidationRule):
    """
    Rule that validates the type of a value.
    """
    
    def __init__(self, expected_type: Union[Type, Tuple[Type, ...]], 
                 message: str = "Invalid type", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a type rule.
        
        Args:
            expected_type: The expected type or types.
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.expected_type = expected_type
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a value is of the expected type.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        if value is None:
            return ValidationResult(is_valid=True, message="", severity=self.severity, path=path)
            
        is_valid = isinstance(value, self.expected_type)
        message = self.message
        if not is_valid and not message:
            message = f"Expected {self.expected_type}, got {type(value).__name__}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message if not is_valid else "",
            severity=self.severity,
            path=path
        )


class RangeRule(ValidationRule):
    """
    Rule that validates a numeric value is within a range.
    """
    
    def __init__(self, minimum: Optional[Union[int, float]] = None, 
                 maximum: Optional[Union[int, float]] = None,
                 message: str = "", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a range rule.
        
        Args:
            minimum: The minimum allowed value (inclusive).
            maximum: The maximum allowed value (inclusive).
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.minimum = minimum
        self.maximum = maximum
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a numeric value is within the specified range.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        if value is None:
            return ValidationResult(is_valid=True, message="", severity=self.severity, path=path)
            
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return ValidationResult(
                is_valid=False,
                message="Value must be a number",
                severity=self.severity,
                path=path
            )
            
        is_valid = True
        message = ""
        
        if self.minimum is not None and value < self.minimum:
            is_valid = False
            message = self.message or f"Value {value} is less than minimum {self.minimum}"
            
        if is_valid and self.maximum is not None and value > self.maximum:
            is_valid = False
            message = self.message or f"Value {value} is greater than maximum {self.maximum}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message,
            severity=self.severity,
            path=path
        )


class LengthRule(ValidationRule):
    """
    Rule that validates the length of a string or collection.
    """
    
    def __init__(self, min_length: Optional[int] = None, 
                 max_length: Optional[int] = None,
                 message: str = "", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a length rule.
        
        Args:
            min_length: The minimum allowed length.
            max_length: The maximum allowed length.
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.min_length = min_length
        self.max_length = max_length
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a string or collection has a length within the specified range.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        if value is None:
            return ValidationResult(is_valid=True, message="", severity=self.severity, path=path)
            
        try:
            length = len(value)
        except (TypeError, AttributeError):
            return ValidationResult(
                is_valid=False,
                message="Value must have a length",
                severity=self.severity,
                path=path
            )
            
        is_valid = True
        message = ""
        
        if self.min_length is not None and length < self.min_length:
            is_valid = False
            message = self.message or f"Length {length} is less than minimum length {self.min_length}"
            
        if is_valid and self.max_length is not None and length > self.max_length:
            is_valid = False
            message = self.message or f"Length {length} is greater than maximum length {self.max_length}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message,
            severity=self.severity,
            path=path
        )


class PatternRule(ValidationRule):
    """
    Rule that validates a string against a regular expression pattern.
    """
    
    def __init__(self, pattern: str, 
                 message: str = "", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a pattern rule.
        
        Args:
            pattern: The regular expression pattern to match against.
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.pattern = pattern
        self.regex = re.compile(pattern)
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a string matches the specified pattern.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        if value is None:
            return ValidationResult(is_valid=True, message="", severity=self.severity, path=path)
            
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                message="Value must be a string",
                severity=self.severity,
                path=path
            )
            
        is_valid = bool(self.regex.match(value))
        message = self.message or f"String does not match pattern {self.pattern}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message if not is_valid else "",
            severity=self.severity,
            path=path
        )


class EnumRule(ValidationRule):
    """
    Rule that validates a value is one of a set of allowed values.
    """
    
    def __init__(self, allowed_values: List[Any], 
                 message: str = "", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize an enum rule.
        
        Args:
            allowed_values: The list of allowed values.
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.allowed_values = allowed_values
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate that a value is one of the allowed values.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        if value is None:
            return ValidationResult(is_valid=True, message="", severity=self.severity, path=path)
            
        is_valid = value in self.allowed_values
        message = self.message or f"Value {value} is not one of the allowed values: {self.allowed_values}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message if not is_valid else "",
            severity=self.severity,
            path=path
        )


class CustomRule(ValidationRule):
    """
    Rule that uses a custom validation function.
    """
    
    def __init__(self, validator: Callable[[Any], bool], 
                 message: str = "", 
                 severity: ValidationSeverity = ValidationSeverity.ERROR):
        """
        Initialize a custom rule.
        
        Args:
            validator: A function that takes a value and returns True if valid, False otherwise.
            message: A message to use when validation fails.
            severity: The severity level of validation failures.
        """
        super().__init__(message, severity)
        self.validator = validator
        
    def validate(self, value: Any, path: str = "") -> ValidationResult:
        """
        Validate a value using the custom validation function.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A ValidationResult indicating whether validation passed.
        """
        is_valid = self.validator(value)
        message = self.message or f"Failed custom validation: {self.validator.__name__}"
            
        return ValidationResult(
            is_valid=is_valid,
            message=message if not is_valid else "",
            severity=self.severity,
            path=path
        )


class ValidationRuleSet:
    """
    A set of validation rules to apply to a value.
    """
    
    def __init__(self, rules: List[ValidationRule] = None):
        """
        Initialize a validation rule set.
        
        Args:
            rules: A list of validation rules to apply.
        """
        self.rules = rules or []
        
    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a rule to the rule set.
        
        Args:
            rule: The rule to add.
        """
        self.rules.append(rule)
        
    def validate(self, value: Any, path: str = "") -> List[ValidationResult]:
        """
        Validate a value against all rules in the rule set.
        
        Args:
            value: The value to validate.
            path: The path to the validated element.
            
        Returns:
            A list of ValidationResult objects, one for each rule that failed.
        """
        results = []
        for rule in self.rules:
            result = rule.validate(value, path)
            if not result.is_valid:
                results.append(result)
        return results


class ValidationContext:
    """
    A context for validating complex data structures.
    """
    
    def __init__(self):
        """
        Initialize a validation context.
        """
        self.rule_sets: Dict[str, ValidationRuleSet] = {}
        
    def add_rule_set(self, path: str, rule_set: ValidationRuleSet) -> None:
        """
        Add a rule set for a specific path.
        
        Args:
            path: The path to apply the rule set to.
            rule_set: The rule set to apply.
        """
        self.rule_sets[path] = rule_set
        
    def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate data against all rule sets in the context.
        
        Args:
            data: The data to validate.
            
        Returns:
            A list of ValidationResult objects, one for each rule that failed.
        """
        results = []
        for path, rule_set in self.rule_sets.items():
            # Split the path into parts
            parts = path.split('.')
            
            # Navigate to the value at the path
            value = data
            for part in parts:
                if part == '':
                    continue
                    
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                    value = value[int(part)]
                else:
                    # Path doesn't exist in data
                    value = None
                    break
                    
            # Validate the value
            path_results = rule_set.validate(value, path)
            results.extend(path_results)
            
        return results


# Example of creating and using validation rules
def create_person_validation_context() -> ValidationContext:
    """
    Create a validation context for a person.
    
    Returns:
        A ValidationContext for validating person data.
    """
    context = ValidationContext()
    
    # Add rule set for first name
    first_name_rules = ValidationRuleSet([
        RequiredRule("First name is required"),
        TypeRule(str, "First name must be a string"),
        LengthRule(min_length=1, max_length=50, message="First name must be between 1 and 50 characters")
    ])
    context.add_rule_set("first_name", first_name_rules)
    
    # Add rule set for last name
    last_name_rules = ValidationRuleSet([
        RequiredRule("Last name is required"),
        TypeRule(str, "Last name must be a string"),
        LengthRule(min_length=1, max_length=50, message="Last name must be between 1 and 50 characters")
    ])
    context.add_rule_set("last_name", last_name_rules)
    
    # Add rule set for email
    email_rules = ValidationRuleSet([
        RequiredRule("Email is required"),
        TypeRule(str, "Email must be a string"),
        PatternRule(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "Invalid email format")
    ])
    context.add_rule_set("contact.email", email_rules)
    
    # Add rule set for age
    age_rules = ValidationRuleSet([
        TypeRule(int, "Age must be an integer"),
        RangeRule(minimum=0, maximum=120, message="Age must be between 0 and 120")
    ])
    context.add_rule_set("age", age_rules)
    
    # Add rule set for country
    country_rules = ValidationRuleSet([
        TypeRule(str, "Country must be a string"),
        EnumRule(["USA", "Canada", "UK", "Australia", "Other"], "Country must be one of the allowed values")
    ])
    context.add_rule_set("address.country", country_rules)
    
    return context