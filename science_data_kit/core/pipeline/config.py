"""
Pipeline Configuration for Science Data Kit

This module defines the configuration format for data transformation pipelines,
which specify how data from various sources should be transformed and mapped
into a knowledge graph.
"""

import enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import yaml
import json


class StepType(enum.Enum):
    """Types of transformation steps supported in a pipeline."""
    
    FILTER = "filter"  # Filter rows or columns
    TRANSFORM = "transform"  # Transform data (e.g., format conversion)
    MAP = "map"  # Map data to nodes/relationships
    VALIDATE = "validate"  # Validate data against rules
    ENRICH = "enrich"  # Enrich data with additional information
    
    def __str__(self) -> str:
        """Return the string representation of the step type."""
        return self.value


class NodeLabelStrategy(enum.Enum):
    """Strategies for determining node labels when mapping tabular data."""
    
    FIXED = "fixed"  # Use a fixed label for all nodes
    COLUMN_VALUE = "column_value"  # Use values from a specific column
    TEMPLATE = "template"  # Use a template with placeholders
    
    def __str__(self) -> str:
        """Return the string representation of the strategy."""
        return self.value


class RelationshipStrategy(enum.Enum):
    """Strategies for creating relationships when mapping tabular data."""
    
    NONE = "none"  # Don't create relationships
    FIXED = "fixed"  # Create fixed relationships between nodes
    COLUMN_BASED = "column_based"  # Create relationships based on column values
    TEMPLATE = "template"  # Use a template with placeholders
    
    def __str__(self) -> str:
        """Return the string representation of the strategy."""
        return self.value


@dataclass
class MappingRule:
    """
    Rule for mapping data to nodes or relationships in the knowledge graph.
    
    Attributes:
        source_field: Field name in the source data
        target_property: Property name in the target node/relationship
        data_type: Data type for the property (string, integer, float, boolean, date, etc.)
        required: Whether the field is required
        default_value: Default value if the field is missing
        transformation: Optional transformation to apply to the field value
    """
    
    source_field: str
    target_property: str
    data_type: str = "string"
    required: bool = False
    default_value: Optional[Any] = None
    transformation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the mapping rule to a dictionary."""
        return {
            "source_field": self.source_field,
            "target_property": self.target_property,
            "data_type": self.data_type,
            "required": self.required,
            "default_value": self.default_value,
            "transformation": self.transformation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MappingRule':
        """Create a mapping rule from a dictionary."""
        return cls(
            source_field=data["source_field"],
            target_property=data["target_property"],
            data_type=data.get("data_type", "string"),
            required=data.get("required", False),
            default_value=data.get("default_value"),
            transformation=data.get("transformation")
        )


@dataclass
class TransformationStep:
    """
    Step in a data transformation pipeline.
    
    Attributes:
        name: Name of the step
        type: Type of the step (filter, transform, map, validate, enrich)
        config: Configuration for the step
        enabled: Whether the step is enabled
        description: Description of the step
    """
    
    name: str
    type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the transformation step to a dictionary."""
        return {
            "name": self.name,
            "type": str(self.type),
            "config": self.config,
            "enabled": self.enabled,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransformationStep':
        """Create a transformation step from a dictionary."""
        return cls(
            name=data["name"],
            type=StepType(data["type"]),
            config=data.get("config", {}),
            enabled=data.get("enabled", True),
            description=data.get("description")
        )


@dataclass
class PipelineConfig:
    """
    Configuration for a data transformation pipeline.
    
    Attributes:
        name: Name of the pipeline
        description: Description of the pipeline
        version: Version of the pipeline configuration
        source: Source configuration (provider type, name, and config)
        steps: List of transformation steps
        target: Target configuration (database connection, etc.)
        metadata: Additional metadata for the pipeline
    """
    
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    source: Dict[str, Any] = field(default_factory=dict)
    steps: List[TransformationStep] = field(default_factory=list)
    target: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the pipeline configuration to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "source": self.source,
            "steps": [step.to_dict() for step in self.steps],
            "target": self.target,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfig':
        """Create a pipeline configuration from a dictionary."""
        steps = [
            TransformationStep.from_dict(step_data)
            for step_data in data.get("steps", [])
        ]
        
        return cls(
            name=data["name"],
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            source=data.get("source", {}),
            steps=steps,
            target=data.get("target", {}),
            metadata=data.get("metadata", {})
        )
    
    def to_yaml(self) -> str:
        """Convert the pipeline configuration to YAML."""
        return yaml.dump(self.to_dict(), sort_keys=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'PipelineConfig':
        """Create a pipeline configuration from YAML."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    def to_json(self) -> str:
        """Convert the pipeline configuration to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PipelineConfig':
        """Create a pipeline configuration from JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, file_path: str) -> None:
        """
        Save the pipeline configuration to a file.
        
        Args:
            file_path: Path to the file to save to (must end with .yaml or .json)
        """
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            with open(file_path, "w") as f:
                f.write(self.to_yaml())
        elif file_path.endswith(".json"):
            with open(file_path, "w") as f:
                f.write(self.to_json())
        else:
            raise ValueError("File path must end with .yaml, .yml, or .json")
    
    @classmethod
    def load(cls, file_path: str) -> 'PipelineConfig':
        """
        Load a pipeline configuration from a file.
        
        Args:
            file_path: Path to the file to load from (must end with .yaml or .json)
            
        Returns:
            Loaded pipeline configuration
        """
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            with open(file_path, "r") as f:
                return cls.from_yaml(f.read())
        elif file_path.endswith(".json"):
            with open(file_path, "r") as f:
                return cls.from_json(f.read())
        else:
            raise ValueError("File path must end with .yaml, .yml, or .json")