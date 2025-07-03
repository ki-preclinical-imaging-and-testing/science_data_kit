"""
Pipeline Templates for Science Data Kit

This module provides templates for common data transformation scenarios,
making it easy to get started with data transformation pipelines.
"""

import os
import yaml
from typing import Dict, List, Any, Optional

from ..config import PipelineConfig


def get_available_templates() -> List[str]:
    """
    Get a list of available template names.
    
    Returns:
        List of template names (without the .yaml extension)
    """
    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_files = [f for f in os.listdir(template_dir) if f.endswith('.yaml')]
    return [os.path.splitext(f)[0] for f in template_files]


def load_template(template_name: str) -> PipelineConfig:
    """
    Load a pipeline template by name.
    
    Args:
        template_name: Name of the template (without the .yaml extension)
        
    Returns:
        PipelineConfig object initialized from the template
        
    Raises:
        ValueError: If the template does not exist
    """
    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(template_dir, f"{template_name}.yaml")
    
    if not os.path.exists(template_path):
        available = get_available_templates()
        raise ValueError(
            f"Template '{template_name}' not found. Available templates: {', '.join(available)}"
        )
    
    return PipelineConfig.load(template_path)


def customize_template(template_name: str, customizations: Dict[str, Any]) -> PipelineConfig:
    """
    Load and customize a pipeline template.
    
    Args:
        template_name: Name of the template (without the .yaml extension)
        customizations: Dictionary of customizations to apply to the template
        
    Returns:
        Customized PipelineConfig object
        
    Example:
        >>> config = customize_template('csv_to_graph', {
        ...     'name': 'My CSV Pipeline',
        ...     'source.config.delimiter': ';',
        ...     'steps[0].config.rules[0].fields': ['id', 'name', 'email']
        ... })
    """
    config = load_template(template_name)
    config_dict = config.to_dict()
    
    for path, value in customizations.items():
        _set_nested_value(config_dict, path, value)
    
    return PipelineConfig.from_dict(config_dict)


def _set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set a value in a nested dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to modify
        path: Dot-separated path to the value (e.g., 'source.config.delimiter')
        value: Value to set
    """
    # Handle array indexing with square brackets
    if '[' in path and ']' in path:
        parts = path.split('.')
        current = data
        
        for i, part in enumerate(parts):
            if '[' in part and ']' in part:
                # Extract the key and index
                key, idx_part = part.split('[', 1)
                idx = int(idx_part.split(']')[0])
                
                if i == len(parts) - 1:
                    # Last part, set the value
                    current[key][idx] = value
                else:
                    # Navigate to the next level
                    current = current[key][idx]
            else:
                if i == len(parts) - 1:
                    # Last part, set the value
                    current[part] = value
                else:
                    # Navigate to the next level
                    if part not in current:
                        current[part] = {}
                    current = current[part]
    else:
        # Simple dot-separated path
        parts = path.split('.')
        current = data
        
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Last part, set the value
                current[part] = value
            else:
                # Navigate to the next level
                if part not in current:
                    current[part] = {}
                current = current[part]