"""
Data Transformation for Science Data Kit

This module provides functionality for transforming data from various sources
into a knowledge graph, including tabular data mapping to nodes and relationships.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
import logging
from datetime import datetime
import pathlib
import mimetypes
import hashlib

from .config import MappingRule, NodeLabelStrategy, RelationshipStrategy


class DataTransformer:
    """
    Base class for data transformers.

    Data transformers convert data from various sources into a format suitable
    for loading into a knowledge graph.
    """

    def __init__(self):
        """Initialize the data transformer."""
        self.logger = logging.getLogger(__name__)

    def transform(self, data: Any) -> Any:
        """
        Transform data from a source format to a target format.

        Args:
            data: Data to transform

        Returns:
            Transformed data
        """
        raise NotImplementedError("Subclasses must implement transform method")

    def _validate_data(self, data: Any) -> bool:
        """
        Validate that the data is in the expected format.

        Args:
            data: Data to validate

        Returns:
            True if the data is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement _validate_data method")


class TabularDataMapper(DataTransformer):
    """
    Transformer for mapping tabular data to nodes and relationships.

    This transformer converts tabular data (e.g., CSV, Excel) into nodes and
    relationships for a knowledge graph.
    """

    def __init__(self, 
                 node_label_strategy: NodeLabelStrategy = NodeLabelStrategy.FIXED,
                 node_label_config: Dict[str, Any] = None,
                 relationship_strategy: RelationshipStrategy = RelationshipStrategy.NONE,
                 relationship_config: Dict[str, Any] = None,
                 mapping_rules: List[MappingRule] = None):
        """
        Initialize the tabular data mapper.

        Args:
            node_label_strategy: Strategy for determining node labels
            node_label_config: Configuration for the node label strategy
            relationship_strategy: Strategy for creating relationships
            relationship_config: Configuration for the relationship strategy
            mapping_rules: Rules for mapping columns to properties
        """
        super().__init__()

        self.node_label_strategy = node_label_strategy
        self.node_label_config = node_label_config or {}
        self.relationship_strategy = relationship_strategy
        self.relationship_config = relationship_config or {}
        self.mapping_rules = mapping_rules or []

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the mapper configuration."""
        # Validate node label strategy configuration
        if self.node_label_strategy == NodeLabelStrategy.FIXED:
            if "label" not in self.node_label_config:
                raise ValueError("Fixed node label strategy requires 'label' in configuration")
        elif self.node_label_strategy == NodeLabelStrategy.COLUMN_VALUE:
            if "column" not in self.node_label_config:
                raise ValueError("Column value node label strategy requires 'column' in configuration")
        elif self.node_label_strategy == NodeLabelStrategy.TEMPLATE:
            if "template" not in self.node_label_config:
                raise ValueError("Template node label strategy requires 'template' in configuration")

        # Validate relationship strategy configuration
        if self.relationship_strategy == RelationshipStrategy.FIXED:
            if "type" not in self.relationship_config:
                raise ValueError("Fixed relationship strategy requires 'type' in configuration")
            if "target_label" not in self.relationship_config:
                raise ValueError("Fixed relationship strategy requires 'target_label' in configuration")
        elif self.relationship_strategy == RelationshipStrategy.COLUMN_BASED:
            if "type_column" not in self.relationship_config:
                raise ValueError("Column-based relationship strategy requires 'type_column' in configuration")
            if "target_column" not in self.relationship_config:
                raise ValueError("Column-based relationship strategy requires 'target_column' in configuration")
        elif self.relationship_strategy == RelationshipStrategy.TEMPLATE:
            if "type_template" not in self.relationship_config:
                raise ValueError("Template relationship strategy requires 'type_template' in configuration")
            if "target_template" not in self.relationship_config:
                raise ValueError("Template relationship strategy requires 'target_template' in configuration")

    def _validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the data is a pandas DataFrame.

        Args:
            data: Data to validate

        Returns:
            True if the data is valid, False otherwise
        """
        if not isinstance(data, pd.DataFrame):
            self.logger.error("Data must be a pandas DataFrame")
            return False

        # Check if required columns are present
        for rule in self.mapping_rules:
            if rule.required and rule.source_field not in data.columns:
                self.logger.error(f"Required column '{rule.source_field}' not found in data")
                return False

        # Check if columns needed for node label strategy are present
        if self.node_label_strategy == NodeLabelStrategy.COLUMN_VALUE:
            column = self.node_label_config.get("column")
            if column and column not in data.columns:
                self.logger.error(f"Column '{column}' for node label strategy not found in data")
                return False

        # Check if columns needed for relationship strategy are present
        if self.relationship_strategy == RelationshipStrategy.COLUMN_BASED:
            type_column = self.relationship_config.get("type_column")
            target_column = self.relationship_config.get("target_column")
            if type_column and type_column not in data.columns:
                self.logger.error(f"Column '{type_column}' for relationship type not found in data")
                return False
            if target_column and target_column not in data.columns:
                self.logger.error(f"Column '{target_column}' for relationship target not found in data")
                return False

        return True

    def _apply_mapping_rules(self, row: pd.Series) -> Dict[str, Any]:
        """
        Apply mapping rules to a row of data.

        Args:
            row: Row of data to map

        Returns:
            Dictionary of properties for the node or relationship
        """
        properties = {}

        for rule in self.mapping_rules:
            # Skip if source field is not in the row
            if rule.source_field not in row:
                if rule.required:
                    self.logger.warning(f"Required field '{rule.source_field}' not found in row")
                    if rule.default_value is not None:
                        properties[rule.target_property] = rule.default_value
                continue

            # Get the value from the row
            value = row[rule.source_field]

            # Apply transformation if specified
            if rule.transformation:
                try:
                    # Simple transformations
                    if rule.transformation == "uppercase":
                        value = str(value).upper()
                    elif rule.transformation == "lowercase":
                        value = str(value).lower()
                    elif rule.transformation == "capitalize":
                        value = str(value).capitalize()
                    elif rule.transformation == "strip":
                        value = str(value).strip()
                    # More complex transformations could be added here
                except Exception as e:
                    self.logger.warning(f"Error applying transformation '{rule.transformation}': {str(e)}")

            # Convert to the specified data type
            try:
                if rule.data_type == "string":
                    value = str(value) if pd.notna(value) else None
                elif rule.data_type == "integer":
                    value = int(value) if pd.notna(value) else None
                elif rule.data_type == "float":
                    value = float(value) if pd.notna(value) else None
                elif rule.data_type == "boolean":
                    if isinstance(value, bool):
                        pass
                    elif isinstance(value, (int, float)):
                        value = bool(value)
                    elif isinstance(value, str):
                        value = value.lower() in ["true", "yes", "1", "t", "y"]
                    else:
                        value = bool(value) if pd.notna(value) else None
                elif rule.data_type == "date":
                    if isinstance(value, (datetime, pd.Timestamp)):
                        value = value.isoformat()
                    else:
                        value = pd.to_datetime(value).isoformat() if pd.notna(value) else None
                # Add more data types as needed
            except Exception as e:
                self.logger.warning(f"Error converting value to {rule.data_type}: {str(e)}")
                if rule.default_value is not None:
                    value = rule.default_value
                else:
                    continue

            # Use default value if value is None or NaN
            if pd.isna(value) and rule.default_value is not None:
                value = rule.default_value

            # Add to properties
            if not pd.isna(value):
                properties[rule.target_property] = value

        return properties

    def _get_node_label(self, row: pd.Series) -> str:
        """
        Get the node label for a row of data.

        Args:
            row: Row of data

        Returns:
            Node label
        """
        if self.node_label_strategy == NodeLabelStrategy.FIXED:
            return self.node_label_config.get("label", "Node")

        elif self.node_label_strategy == NodeLabelStrategy.COLUMN_VALUE:
            column = self.node_label_config.get("column")
            if column and column in row:
                value = row[column]
                if pd.notna(value):
                    return str(value)
            return self.node_label_config.get("default_label", "Node")

        elif self.node_label_strategy == NodeLabelStrategy.TEMPLATE:
            template = self.node_label_config.get("template", "{label}")
            try:
                return template.format(**row.to_dict())
            except Exception as e:
                self.logger.warning(f"Error formatting node label template: {str(e)}")
                return self.node_label_config.get("default_label", "Node")

        return "Node"

    def _get_relationship_info(self, row: pd.Series) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the relationship type and target for a row of data.

        Args:
            row: Row of data

        Returns:
            Tuple of (relationship_type, target_identifier)
        """
        if self.relationship_strategy == RelationshipStrategy.NONE:
            return None, None

        elif self.relationship_strategy == RelationshipStrategy.FIXED:
            return (
                self.relationship_config.get("type", "RELATED_TO"),
                self.relationship_config.get("target_label", "Node")
            )

        elif self.relationship_strategy == RelationshipStrategy.COLUMN_BASED:
            type_column = self.relationship_config.get("type_column")
            target_column = self.relationship_config.get("target_column")

            rel_type = row.get(type_column) if type_column and type_column in row else "RELATED_TO"
            target = row.get(target_column) if target_column and target_column in row else None

            if pd.isna(rel_type):
                rel_type = self.relationship_config.get("default_type", "RELATED_TO")

            return str(rel_type), str(target) if pd.notna(target) else None

        elif self.relationship_strategy == RelationshipStrategy.TEMPLATE:
            type_template = self.relationship_config.get("type_template", "RELATED_TO")
            target_template = self.relationship_config.get("target_template")

            try:
                rel_type = type_template.format(**row.to_dict())
            except Exception as e:
                self.logger.warning(f"Error formatting relationship type template: {str(e)}")
                rel_type = self.relationship_config.get("default_type", "RELATED_TO")

            try:
                target = target_template.format(**row.to_dict()) if target_template else None
            except Exception as e:
                self.logger.warning(f"Error formatting relationship target template: {str(e)}")
                target = None

            return rel_type, target

        return None, None

    def transform(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Transform tabular data into nodes and relationships.

        Args:
            data: Pandas DataFrame containing the tabular data

        Returns:
            Dictionary containing nodes and relationships
        """
        if not self._validate_data(data):
            raise ValueError("Invalid data for transformation")

        nodes = []
        relationships = []

        # Process each row in the DataFrame
        for _, row in data.iterrows():
            # Create node
            node_label = self._get_node_label(row)
            node_properties = self._apply_mapping_rules(row)

            # Generate a unique identifier for the node
            node_id = f"{node_label}_{len(nodes)}"

            # Add node to the list
            nodes.append({
                "id": node_id,
                "label": node_label,
                "properties": node_properties
            })

            # Create relationship if applicable
            rel_type, target = self._get_relationship_info(row)
            if rel_type and target:
                # Add relationship to the list
                relationships.append({
                    "source": node_id,
                    "target": target,
                    "type": rel_type,
                    "properties": {}  # Could add properties to relationships if needed
                })

        return {
            "nodes": nodes,
            "relationships": relationships
        }


class FileTreeProcessor(DataTransformer):
    """
    Transformer for processing file trees into nodes and relationships.

    This transformer converts a directory structure into nodes (for directories and files)
    and relationships (for directory containment) in a knowledge graph.
    """

    def __init__(self, 
                 root_path: str,
                 file_node_label: str = "File",
                 directory_node_label: str = "Directory",
                 contains_relationship_type: str = "CONTAINS",
                 file_extensions: Optional[List[str]] = None,
                 max_depth: Optional[int] = None,
                 include_hidden: bool = False,
                 compute_checksums: bool = False,
                 extract_metadata: bool = True):
        """
        Initialize the file tree processor.

        Args:
            root_path: Root directory path to process
            file_node_label: Label for file nodes
            directory_node_label: Label for directory nodes
            contains_relationship_type: Type of relationship between directories and their contents
            file_extensions: List of file extensions to include (e.g., ['.txt', '.csv'])
            max_depth: Maximum depth to traverse (None for unlimited)
            include_hidden: Whether to include hidden files and directories
            compute_checksums: Whether to compute MD5 checksums for files
            extract_metadata: Whether to extract metadata from files
        """
        super().__init__()

        self.root_path = os.path.abspath(root_path)
        self.file_node_label = file_node_label
        self.directory_node_label = directory_node_label
        self.contains_relationship_type = contains_relationship_type
        self.file_extensions = file_extensions
        self.max_depth = max_depth
        self.include_hidden = include_hidden
        self.compute_checksums = compute_checksums
        self.extract_metadata = extract_metadata

        # Initialize mimetypes
        mimetypes.init()

    def _validate_data(self, data: str) -> bool:
        """
        Validate that the data is a valid directory path.

        Args:
            data: Directory path to validate

        Returns:
            True if the data is valid, False otherwise
        """
        if not isinstance(data, str):
            self.logger.error("Data must be a string path")
            return False

        path = pathlib.Path(data)
        if not path.exists():
            self.logger.error(f"Path does not exist: {data}")
            return False

        if not path.is_dir():
            self.logger.error(f"Path is not a directory: {data}")
            return False

        return True

    def _is_hidden(self, path: pathlib.Path) -> bool:
        """
        Check if a path is hidden.

        Args:
            path: Path to check

        Returns:
            True if the path is hidden, False otherwise
        """
        # On Unix-like systems, hidden files/dirs start with a dot
        if path.name.startswith('.'):
            return True

        # On Windows, check the hidden attribute
        if os.name == 'nt':
            import stat
            try:
                return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                pass

        return False

    def _should_include_file(self, path: pathlib.Path) -> bool:
        """
        Check if a file should be included based on configuration.

        Args:
            path: Path to check

        Returns:
            True if the file should be included, False otherwise
        """
        # Check if it's hidden and we're not including hidden files
        if not self.include_hidden and self._is_hidden(path):
            return False

        # Check if it has one of the specified extensions
        if self.file_extensions:
            return path.suffix.lower() in self.file_extensions

        return True

    def _should_include_directory(self, path: pathlib.Path, current_depth: int) -> bool:
        """
        Check if a directory should be included based on configuration.

        Args:
            path: Path to check
            current_depth: Current depth in the directory tree

        Returns:
            True if the directory should be included, False otherwise
        """
        # Check if it's hidden and we're not including hidden directories
        if not self.include_hidden and self._is_hidden(path):
            return False

        # Check if we've reached the maximum depth
        if self.max_depth is not None and current_depth >= self.max_depth:
            return False

        return True

    def _compute_checksum(self, file_path: pathlib.Path) -> str:
        """
        Compute MD5 checksum for a file.

        Args:
            file_path: Path to the file

        Returns:
            MD5 checksum as a hexadecimal string
        """
        try:
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read the file in chunks to avoid loading large files into memory
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            self.logger.warning(f"Error computing checksum for {file_path}: {str(e)}")
            return ""

    def _get_file_metadata(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Extract metadata from a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary of file metadata
        """
        try:
            stat_result = file_path.stat()

            # Basic metadata
            metadata = {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat_result.st_size,
                "created": datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_result.st_atime).isoformat(),
                "extension": file_path.suffix.lower(),
            }

            # Add MIME type
            mime_type, encoding = mimetypes.guess_type(str(file_path))
            if mime_type:
                metadata["mime_type"] = mime_type
            if encoding:
                metadata["encoding"] = encoding

            # Add checksum if requested
            if self.compute_checksums:
                metadata["md5_checksum"] = self._compute_checksum(file_path)

            return metadata
        except Exception as e:
            self.logger.warning(f"Error extracting metadata for {file_path}: {str(e)}")
            return {"name": file_path.name, "path": str(file_path)}

    def _get_directory_metadata(self, dir_path: pathlib.Path) -> Dict[str, Any]:
        """
        Extract metadata from a directory.

        Args:
            dir_path: Path to the directory

        Returns:
            Dictionary of directory metadata
        """
        try:
            stat_result = dir_path.stat()

            # Basic metadata
            metadata = {
                "name": dir_path.name,
                "path": str(dir_path),
                "created": datetime.fromtimestamp(stat_result.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_result.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_result.st_atime).isoformat(),
            }

            return metadata
        except Exception as e:
            self.logger.warning(f"Error extracting metadata for {dir_path}: {str(e)}")
            return {"name": dir_path.name, "path": str(dir_path)}

    def _process_directory(self, dir_path: pathlib.Path, current_depth: int, 
                          processed_paths: Set[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process a directory and its contents recursively.

        Args:
            dir_path: Path to the directory
            current_depth: Current depth in the directory tree
            processed_paths: Set of paths that have already been processed

        Returns:
            Tuple of (nodes, relationships)
        """
        # Skip if already processed (to avoid cycles)
        if str(dir_path) in processed_paths:
            return [], []

        processed_paths.add(str(dir_path))

        # Create node for the directory
        dir_metadata = self._get_directory_metadata(dir_path)
        dir_node = {
            "id": f"dir_{len(processed_paths)}",
            "label": self.directory_node_label,
            "properties": dir_metadata
        }

        nodes = [dir_node]
        relationships = []

        # Process contents
        try:
            for item in dir_path.iterdir():
                if item.is_file() and self._should_include_file(item):
                    # Process file
                    if self.extract_metadata:
                        file_metadata = self._get_file_metadata(item)
                    else:
                        file_metadata = {"name": item.name, "path": str(item)}

                    file_node = {
                        "id": f"file_{len(nodes)}",
                        "label": self.file_node_label,
                        "properties": file_metadata
                    }

                    nodes.append(file_node)

                    # Create relationship from directory to file
                    relationships.append({
                        "source": dir_node["id"],
                        "target": file_node["id"],
                        "type": self.contains_relationship_type,
                        "properties": {}
                    })

                elif item.is_dir() and self._should_include_directory(item, current_depth + 1):
                    # Process subdirectory recursively
                    subdir_nodes, subdir_relationships = self._process_directory(
                        item, current_depth + 1, processed_paths
                    )

                    # Add subdirectory nodes and relationships
                    nodes.extend(subdir_nodes)
                    relationships.extend(subdir_relationships)

                    # Create relationship from parent directory to subdirectory
                    if subdir_nodes:
                        relationships.append({
                            "source": dir_node["id"],
                            "target": subdir_nodes[0]["id"],
                            "type": self.contains_relationship_type,
                            "properties": {}
                        })

        except Exception as e:
            self.logger.error(f"Error processing directory {dir_path}: {str(e)}")

        return nodes, relationships

    def transform(self, data: Optional[str] = None) -> Dict[str, Any]:
        """
        Transform a file tree into nodes and relationships.

        Args:
            data: Optional path to the root directory. If None, uses the root_path from initialization.

        Returns:
            Dictionary containing nodes and relationships
        """
        # Use the provided path or the root path from initialization
        root_path = data if data else self.root_path

        # Validate the path
        if not self._validate_data(root_path):
            raise ValueError(f"Invalid directory path: {root_path}")

        # Process the directory tree
        processed_paths = set()
        nodes, relationships = self._process_directory(
            pathlib.Path(root_path), 0, processed_paths
        )

        return {
            "nodes": nodes,
            "relationships": relationships
        }


class DataValidator(DataTransformer):
    """
    Validator for data in transformation pipelines.

    This class validates data against a set of rules to ensure data quality
    before further processing or loading into a knowledge graph.
    """

    class ValidationRule:
        """
        Rule for validating data.

        Attributes:
            name: Name of the rule
            field: Field to validate (column name for tabular data, property name for objects)
            condition: Function that takes a value and returns True if valid, False otherwise
            error_message: Message to log when validation fails
            severity: Severity of validation failure ('error', 'warning', 'info')
            action: Action to take when validation fails ('reject', 'fix', 'log')
            fix_function: Optional function to fix invalid values
        """

        def __init__(self, 
                     name: str,
                     field: str,
                     condition: Callable[[Any], bool],
                     error_message: str = "Validation failed",
                     severity: str = "error",
                     action: str = "reject",
                     fix_function: Optional[Callable[[Any], Any]] = None):
            """
            Initialize a validation rule.

            Args:
                name: Name of the rule
                field: Field to validate
                condition: Function that takes a value and returns True if valid
                error_message: Message to log when validation fails
                severity: Severity of validation failure ('error', 'warning', 'info')
                action: Action to take when validation fails ('reject', 'fix', 'log')
                fix_function: Optional function to fix invalid values
            """
            self.name = name
            self.field = field
            self.condition = condition
            self.error_message = error_message
            self.severity = severity.lower()
            self.action = action.lower()
            self.fix_function = fix_function

            # Validate severity
            if self.severity not in ["error", "warning", "info"]:
                raise ValueError(f"Invalid severity: {severity}. Must be 'error', 'warning', or 'info'.")

            # Validate action
            if self.action not in ["reject", "fix", "log"]:
                raise ValueError(f"Invalid action: {action}. Must be 'reject', 'fix', or 'log'.")

            # Validate fix_function
            if self.action == "fix" and self.fix_function is None:
                raise ValueError("Fix function must be provided when action is 'fix'.")

    def __init__(self, rules: List[ValidationRule] = None):
        """
        Initialize the data validator.

        Args:
            rules: List of validation rules
        """
        super().__init__()
        self.rules = rules or []
        self.validation_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "fixed": 0,
            "rejected": 0,
            "errors": [],
            "warnings": [],
            "info": []
        }

    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a validation rule.

        Args:
            rule: Validation rule to add
        """
        self.rules.append(rule)

    def _validate_data(self, data: Any) -> bool:
        """
        Validate that the data can be processed.

        Args:
            data: Data to validate

        Returns:
            True if the data can be processed, False otherwise
        """
        # Reset validation results
        self.validation_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "fixed": 0,
            "rejected": 0,
            "errors": [],
            "warnings": [],
            "info": []
        }

        # Check if data is a pandas DataFrame
        if isinstance(data, pd.DataFrame):
            return True

        # Check if data is a list of dictionaries
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return True

        # Check if data is a dictionary with lists of values
        if isinstance(data, dict) and all(isinstance(value, list) for value in data.values()):
            return True

        self.logger.error("Data must be a pandas DataFrame, a list of dictionaries, or a dictionary of lists")
        return False

    def _apply_rule_to_value(self, rule: ValidationRule, value: Any, 
                            context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Apply a validation rule to a single value.

        Args:
            rule: Validation rule to apply
            value: Value to validate
            context: Additional context for logging

        Returns:
            Tuple of (is_valid, fixed_value)
        """
        self.validation_results["total"] += 1

        try:
            # Check if value is valid
            is_valid = rule.condition(value)

            if is_valid:
                self.validation_results["passed"] += 1
                return True, value

            # Value is invalid
            self.validation_results["failed"] += 1

            # Create error message with context
            error_message = f"{rule.error_message} - {context}"

            # Log based on severity
            if rule.severity == "error":
                self.logger.error(error_message)
                self.validation_results["errors"].append(error_message)
            elif rule.severity == "warning":
                self.logger.warning(error_message)
                self.validation_results["warnings"].append(error_message)
            else:  # info
                self.logger.info(error_message)
                self.validation_results["info"].append(error_message)

            # Handle based on action
            if rule.action == "fix" and rule.fix_function:
                fixed_value = rule.fix_function(value)
                self.validation_results["fixed"] += 1
                return True, fixed_value
            elif rule.action == "reject":
                self.validation_results["rejected"] += 1
                return False, value
            else:  # log
                return True, value

        except Exception as e:
            self.logger.error(f"Error applying rule {rule.name}: {str(e)}")
            self.validation_results["errors"].append(f"Error applying rule {rule.name}: {str(e)}")
            return False, value

    def _validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate a pandas DataFrame.

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame with invalid rows removed and values fixed
        """
        # Create a mask for rows to keep
        keep_mask = pd.Series(True, index=df.index)

        # Create a copy of the DataFrame to modify
        result_df = df.copy()

        # Apply each rule
        for rule in self.rules:
            if rule.field not in df.columns:
                self.logger.warning(f"Field '{rule.field}' not found in DataFrame")
                continue

            # Apply rule to each value in the column
            for idx, value in df[rule.field].items():
                context = {"row": idx, "field": rule.field, "value": value}
                is_valid, fixed_value = self._apply_rule_to_value(rule, value, context)

                if not is_valid:
                    keep_mask.at[idx] = False
                elif value != fixed_value:
                    result_df.at[idx, rule.field] = fixed_value

        # Filter out rejected rows
        return result_df[keep_mask]

    def _validate_list_of_dicts(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a list of dictionaries.

        Args:
            data: List of dictionaries to validate

        Returns:
            Validated list with invalid items removed and values fixed
        """
        result = []

        # Apply each rule to each dictionary
        for i, item in enumerate(data):
            keep_item = True

            # Create a copy of the item to modify
            result_item = item.copy()

            for rule in self.rules:
                if rule.field not in item:
                    continue

                value = item[rule.field]
                context = {"item": i, "field": rule.field, "value": value}
                is_valid, fixed_value = self._apply_rule_to_value(rule, value, context)

                if not is_valid:
                    keep_item = False
                    break
                elif value != fixed_value:
                    result_item[rule.field] = fixed_value

            if keep_item:
                result.append(result_item)

        return result

    def _validate_dict_of_lists(self, data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """
        Validate a dictionary of lists.

        Args:
            data: Dictionary of lists to validate

        Returns:
            Validated dictionary with invalid values removed and values fixed
        """
        result = {}

        # Apply each rule to each list
        for field, values in data.items():
            result_values = []

            for i, value in enumerate(values):
                keep_value = True
                fixed_value = value

                for rule in self.rules:
                    if rule.field != field:
                        continue

                    context = {"index": i, "field": field, "value": value}
                    is_valid, new_value = self._apply_rule_to_value(rule, value, context)

                    if not is_valid:
                        keep_value = False
                        break
                    elif value != new_value:
                        fixed_value = new_value

                if keep_value:
                    result_values.append(fixed_value)

            result[field] = result_values

        return result

    def transform(self, data: Any) -> Any:
        """
        Validate data against the defined rules.

        Args:
            data: Data to validate (DataFrame, list of dicts, or dict of lists)

        Returns:
            Validated data with invalid items removed and values fixed
        """
        if not self._validate_data(data):
            raise ValueError("Invalid data for validation")

        # Validate based on data type
        if isinstance(data, pd.DataFrame):
            return self._validate_dataframe(data)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return self._validate_list_of_dicts(data)
        elif isinstance(data, dict) and all(isinstance(value, list) for value in data.values()):
            return self._validate_dict_of_lists(data)

        # Should not reach here due to _validate_data check
        return data

    def get_validation_results(self) -> Dict[str, Any]:
        """
        Get the results of the most recent validation.

        Returns:
            Dictionary with validation statistics and error messages
        """
        return self.validation_results
