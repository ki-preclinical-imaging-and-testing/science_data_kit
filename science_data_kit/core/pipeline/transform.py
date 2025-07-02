"""
Data Transformation for Science Data Kit

This module provides functionality for transforming data from various sources
into a knowledge graph, including tabular data mapping to nodes and relationships.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
import logging
from datetime import datetime

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