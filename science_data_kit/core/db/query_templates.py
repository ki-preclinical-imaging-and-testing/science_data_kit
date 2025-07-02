"""
Query Templates for Science Data Kit

This module provides functionality for creating and using parameterized query templates
for Neo4j Cypher queries, improving performance, security, and code reusability.
"""

import re
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
import logging
from datetime import datetime


class QueryTemplate:
    """
    Template for parameterized Cypher queries.
    
    This class provides a way to define reusable query templates with named parameters,
    validation, and documentation.
    """
    
    def __init__(self, 
                 name: str,
                 template: str,
                 description: Optional[str] = None,
                 parameter_descriptions: Optional[Dict[str, str]] = None,
                 required_parameters: Optional[Set[str]] = None,
                 parameter_validators: Optional[Dict[str, Callable[[Any], bool]]] = None):
        """
        Initialize a query template.
        
        Args:
            name: Name of the template
            template: Cypher query template with named parameters in the format {param_name}
            description: Optional description of the template
            parameter_descriptions: Optional dictionary mapping parameter names to descriptions
            required_parameters: Optional set of parameter names that are required
            parameter_validators: Optional dictionary mapping parameter names to validator functions
        """
        self.name = name
        self.template = template
        self.description = description
        self.parameter_descriptions = parameter_descriptions or {}
        self.required_parameters = required_parameters or set()
        self.parameter_validators = parameter_validators or {}
        
        # Extract parameter names from the template
        self.parameter_names = self._extract_parameter_names(template)
        
        # Validate that required_parameters is a subset of parameter_names
        if not self.required_parameters.issubset(self.parameter_names):
            invalid_params = self.required_parameters - self.parameter_names
            raise ValueError(f"Required parameters not found in template: {invalid_params}")
        
        # Validate that parameter_validators keys are a subset of parameter_names
        if not set(self.parameter_validators.keys()).issubset(self.parameter_names):
            invalid_params = set(self.parameter_validators.keys()) - self.parameter_names
            raise ValueError(f"Validator parameters not found in template: {invalid_params}")
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
    
    def _extract_parameter_names(self, template: str) -> Set[str]:
        """
        Extract parameter names from a template string.
        
        Args:
            template: Template string with parameters in the format {param_name}
            
        Returns:
            Set of parameter names
        """
        # Use regex to find all parameters in the format {param_name}
        pattern = r'\{([a-zA-Z0-9_]+)\}'
        return set(re.findall(pattern, template))
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate parameters against the template requirements.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check for missing required parameters
        for param in self.required_parameters:
            if param not in parameters:
                errors.append(f"Missing required parameter: {param}")
        
        # Check for parameters not in the template
        for param in parameters:
            if param not in self.parameter_names:
                errors.append(f"Unknown parameter: {param}")
        
        # Apply validators
        for param, validator in self.parameter_validators.items():
            if param in parameters:
                try:
                    if not validator(parameters[param]):
                        errors.append(f"Invalid value for parameter {param}: {parameters[param]}")
                except Exception as e:
                    errors.append(f"Error validating parameter {param}: {str(e)}")
        
        return len(errors) == 0, errors
    
    def render(self, parameters: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Render the template with the given parameters.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Tuple of (rendered_query, neo4j_parameters)
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        is_valid, errors = self.validate_parameters(parameters)
        if not is_valid:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")
        
        # Create a copy of parameters for Neo4j
        neo4j_params = {k: v for k, v in parameters.items() if k in self.parameter_names}
        
        # Render the template
        rendered_query = self.template.format(**parameters)
        
        return rendered_query, neo4j_params
    
    def get_documentation(self) -> Dict[str, Any]:
        """
        Get documentation for the template.
        
        Returns:
            Dictionary with template documentation
        """
        return {
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "parameters": {
                param: {
                    "description": self.parameter_descriptions.get(param, ""),
                    "required": param in self.required_parameters,
                    "has_validator": param in self.parameter_validators
                }
                for param in self.parameter_names
            }
        }


class QueryTemplateRegistry:
    """
    Registry for query templates.
    
    This class manages a collection of query templates and provides methods for
    registering, retrieving, and using templates.
    """
    
    def __init__(self):
        """Initialize the query template registry."""
        self._templates: Dict[str, QueryTemplate] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_template(self, template: QueryTemplate) -> None:
        """
        Register a query template.
        
        Args:
            template: Query template to register
            
        Raises:
            ValueError: If a template with the same name already exists
        """
        if template.name in self._templates:
            raise ValueError(f"Template with name '{template.name}' already exists")
        
        self._templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[QueryTemplate]:
        """
        Get a template by name.
        
        Args:
            name: Name of the template
            
        Returns:
            Query template if found, None otherwise
        """
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """
        List all registered template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())
    
    def render_template(self, name: str, parameters: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Render a template with the given parameters.
        
        Args:
            name: Name of the template
            parameters: Dictionary of parameter values
            
        Returns:
            Tuple of (rendered_query, neo4j_parameters)
            
        Raises:
            ValueError: If the template is not found or parameters are invalid
        """
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        return template.render(parameters)
    
    def get_documentation(self, name: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get documentation for templates.
        
        Args:
            name: Optional name of the template to get documentation for
            
        Returns:
            If name is provided, returns documentation for that template.
            Otherwise, returns a list of documentation for all templates.
            
        Raises:
            ValueError: If the specified template is not found
        """
        if name:
            template = self.get_template(name)
            if not template:
                raise ValueError(f"Template not found: {name}")
            return template.get_documentation()
        
        return [template.get_documentation() for template in self._templates.values()]


# Create a singleton instance of the registry
template_registry = QueryTemplateRegistry()


# Register some common query templates
def register_common_templates():
    """Register common query templates in the registry."""
    
    # Node retrieval templates
    template_registry.register_template(
        QueryTemplate(
            name="get_node_by_id",
            template="MATCH (n) WHERE id(n) = {node_id} RETURN n",
            description="Get a node by its internal ID",
            parameter_descriptions={"node_id": "Internal ID of the node"},
            required_parameters={"node_id"},
            parameter_validators={"node_id": lambda x: isinstance(x, int) and x >= 0}
        )
    )
    
    template_registry.register_template(
        QueryTemplate(
            name="get_nodes_by_label",
            template="MATCH (n:{label}) RETURN n LIMIT {limit}",
            description="Get nodes with a specific label",
            parameter_descriptions={
                "label": "Label of the nodes to retrieve",
                "limit": "Maximum number of nodes to return"
            },
            required_parameters={"label"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "limit": lambda x: isinstance(x, int) and x > 0
            }
        )
    )
    
    template_registry.register_template(
        QueryTemplate(
            name="get_nodes_by_property",
            template="MATCH (n:{label}) WHERE n.{property} = {value} RETURN n LIMIT {limit}",
            description="Get nodes with a specific property value",
            parameter_descriptions={
                "label": "Label of the nodes to retrieve",
                "property": "Property name to filter on",
                "value": "Property value to filter on",
                "limit": "Maximum number of nodes to return"
            },
            required_parameters={"label", "property", "value"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "property": lambda x: isinstance(x, str) and len(x) > 0,
                "limit": lambda x: isinstance(x, int) and x > 0
            }
        )
    )
    
    # Relationship templates
    template_registry.register_template(
        QueryTemplate(
            name="get_relationships",
            template="MATCH (a:{source_label})-[r:{relationship_type}]->(b:{target_label}) RETURN a, r, b LIMIT {limit}",
            description="Get relationships between nodes",
            parameter_descriptions={
                "source_label": "Label of the source nodes",
                "relationship_type": "Type of relationship",
                "target_label": "Label of the target nodes",
                "limit": "Maximum number of relationships to return"
            },
            required_parameters={"source_label", "relationship_type", "target_label"},
            parameter_validators={
                "source_label": lambda x: isinstance(x, str) and len(x) > 0,
                "relationship_type": lambda x: isinstance(x, str) and len(x) > 0,
                "target_label": lambda x: isinstance(x, str) and len(x) > 0,
                "limit": lambda x: isinstance(x, int) and x > 0
            }
        )
    )
    
    # Path templates
    template_registry.register_template(
        QueryTemplate(
            name="get_shortest_path",
            template="MATCH (a:{source_label}), (b:{target_label}) WHERE a.{source_property} = {source_value} AND b.{target_property} = {target_value} MATCH p = shortestPath((a)-[*..{max_depth}]-(b)) RETURN p",
            description="Get the shortest path between two nodes",
            parameter_descriptions={
                "source_label": "Label of the source node",
                "source_property": "Property name to identify the source node",
                "source_value": "Property value to identify the source node",
                "target_label": "Label of the target node",
                "target_property": "Property name to identify the target node",
                "target_value": "Property value to identify the target node",
                "max_depth": "Maximum path length"
            },
            required_parameters={"source_label", "source_property", "source_value", 
                                "target_label", "target_property", "target_value", "max_depth"},
            parameter_validators={
                "source_label": lambda x: isinstance(x, str) and len(x) > 0,
                "source_property": lambda x: isinstance(x, str) and len(x) > 0,
                "target_label": lambda x: isinstance(x, str) and len(x) > 0,
                "target_property": lambda x: isinstance(x, str) and len(x) > 0,
                "max_depth": lambda x: isinstance(x, int) and x > 0
            }
        )
    )
    
    # Aggregation templates
    template_registry.register_template(
        QueryTemplate(
            name="count_nodes_by_label",
            template="MATCH (n:{label}) RETURN count(n) as count",
            description="Count nodes with a specific label",
            parameter_descriptions={"label": "Label of the nodes to count"},
            required_parameters={"label"},
            parameter_validators={"label": lambda x: isinstance(x, str) and len(x) > 0}
        )
    )
    
    template_registry.register_template(
        QueryTemplate(
            name="count_relationships_by_type",
            template="MATCH ()-[r:{relationship_type}]->() RETURN count(r) as count",
            description="Count relationships with a specific type",
            parameter_descriptions={"relationship_type": "Type of relationship to count"},
            required_parameters={"relationship_type"},
            parameter_validators={"relationship_type": lambda x: isinstance(x, str) and len(x) > 0}
        )
    )
    
    # Creation templates
    template_registry.register_template(
        QueryTemplate(
            name="create_node",
            template="CREATE (n:{label} {properties}) RETURN n",
            description="Create a new node",
            parameter_descriptions={
                "label": "Label for the new node",
                "properties": "Dictionary of properties for the new node"
            },
            required_parameters={"label", "properties"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "properties": lambda x: isinstance(x, dict)
            }
        )
    )
    
    template_registry.register_template(
        QueryTemplate(
            name="create_relationship",
            template="MATCH (a:{source_label}), (b:{target_label}) WHERE a.{source_property} = {source_value} AND b.{target_property} = {target_value} CREATE (a)-[r:{relationship_type} {properties}]->(b) RETURN r",
            description="Create a relationship between two nodes",
            parameter_descriptions={
                "source_label": "Label of the source node",
                "source_property": "Property name to identify the source node",
                "source_value": "Property value to identify the source node",
                "target_label": "Label of the target node",
                "target_property": "Property name to identify the target node",
                "target_value": "Property value to identify the target node",
                "relationship_type": "Type of relationship to create",
                "properties": "Dictionary of properties for the new relationship"
            },
            required_parameters={"source_label", "source_property", "source_value", 
                                "target_label", "target_property", "target_value", 
                                "relationship_type"},
            parameter_validators={
                "source_label": lambda x: isinstance(x, str) and len(x) > 0,
                "source_property": lambda x: isinstance(x, str) and len(x) > 0,
                "target_label": lambda x: isinstance(x, str) and len(x) > 0,
                "target_property": lambda x: isinstance(x, str) and len(x) > 0,
                "relationship_type": lambda x: isinstance(x, str) and len(x) > 0,
                "properties": lambda x: isinstance(x, dict)
            }
        )
    )
    
    # Update templates
    template_registry.register_template(
        QueryTemplate(
            name="update_node_properties",
            template="MATCH (n:{label}) WHERE n.{property} = {value} SET n += {new_properties} RETURN n",
            description="Update properties of nodes",
            parameter_descriptions={
                "label": "Label of the nodes to update",
                "property": "Property name to identify the nodes",
                "value": "Property value to identify the nodes",
                "new_properties": "Dictionary of properties to update"
            },
            required_parameters={"label", "property", "value", "new_properties"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "property": lambda x: isinstance(x, str) and len(x) > 0,
                "new_properties": lambda x: isinstance(x, dict)
            }
        )
    )
    
    # Delete templates
    template_registry.register_template(
        QueryTemplate(
            name="delete_node",
            template="MATCH (n:{label}) WHERE n.{property} = {value} DETACH DELETE n",
            description="Delete nodes and their relationships",
            parameter_descriptions={
                "label": "Label of the nodes to delete",
                "property": "Property name to identify the nodes",
                "value": "Property value to identify the nodes"
            },
            required_parameters={"label", "property", "value"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "property": lambda x: isinstance(x, str) and len(x) > 0
            }
        )
    )
    
    # Pagination templates
    template_registry.register_template(
        QueryTemplate(
            name="paginated_nodes",
            template="MATCH (n:{label}) RETURN n ORDER BY n.{order_by} SKIP {skip} LIMIT {limit}",
            description="Get a paginated list of nodes",
            parameter_descriptions={
                "label": "Label of the nodes to retrieve",
                "order_by": "Property to order by",
                "skip": "Number of nodes to skip",
                "limit": "Maximum number of nodes to return"
            },
            required_parameters={"label", "order_by", "skip", "limit"},
            parameter_validators={
                "label": lambda x: isinstance(x, str) and len(x) > 0,
                "order_by": lambda x: isinstance(x, str) and len(x) > 0,
                "skip": lambda x: isinstance(x, int) and x >= 0,
                "limit": lambda x: isinstance(x, int) and x > 0
            }
        )
    )


# Register common templates when the module is imported
register_common_templates()