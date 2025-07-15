"""
Relationship Management for Science Data Kit

This module provides utilities for managing relationships in Neo4j,
including creating, querying, and analyzing complex relationship patterns.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable
from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from .db_manager import Neo4jManager, QueryError, ConnectionError


class RelationshipType:
    """
    Represents a Neo4j relationship type with metadata.

    This class provides a way to define relationship types with additional
    metadata, such as descriptions, constraints, and validation rules.
    """

    def __init__(self, name: str, description: Optional[str] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 bidirectional: bool = False,
                 validators: Optional[Dict[str, Callable[[Any], bool]]] = None):
        """
        Initialize a relationship type.

        Args:
            name: Name of the relationship type (e.g., "KNOWS", "BELONGS_TO")
            description: Optional description of the relationship type
            properties: Optional dictionary of default properties for this relationship type
            bidirectional: Whether this relationship is conceptually bidirectional
            validators: Optional dictionary of property validators
        """
        self.name = name
        self.description = description
        self.properties = properties or {}
        self.bidirectional = bidirectional
        self.validators = validators or {}

    def validate_properties(self, properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate properties against the validators.

        Args:
            properties: Dictionary of property values to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        for prop, validator in self.validators.items():
            if prop in properties:
                try:
                    if not validator(properties[prop]):
                        errors.append(f"Invalid value for property {prop}: {properties[prop]}")
                except Exception as e:
                    errors.append(f"Error validating property {prop}: {str(e)}")

        return len(errors) == 0, errors


class RelationshipPattern:
    """
    Represents a pattern of relationships for querying or creating complex structures.

    This class provides a way to define and work with complex relationship patterns,
    such as paths, trees, and graphs.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a relationship pattern.

        Args:
            name: Name of the pattern
            description: Optional description of the pattern
        """
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, source_label: str, relationship_type: str, target_label: str,
                direction: str = "outgoing", properties: Optional[Dict[str, Any]] = None,
                optional: bool = False) -> "RelationshipPattern":
        """
        Add a step to the relationship pattern.

        Args:
            source_label: Label of the source node
            relationship_type: Type of relationship
            target_label: Label of the target node
            direction: Direction of the relationship ("outgoing", "incoming", or "both")
            properties: Optional properties for the relationship
            optional: Whether this step is optional in the pattern

        Returns:
            Self for method chaining
        """
        self.steps.append({
            "source_label": source_label,
            "relationship_type": relationship_type,
            "target_label": target_label,
            "direction": direction,
            "properties": properties or {},
            "optional": optional
        })
        return self

    def to_cypher(self, with_params: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Convert the pattern to a Cypher query.

        Args:
            with_params: Whether to use parameterized query

        Returns:
            Tuple of (query, parameters)
        """
        if not self.steps:
            raise ValueError("Pattern must have at least one step")

        query_parts = []
        params = {}

        # Start with the first node
        first_step = self.steps[0]
        source_var = "n0"
        query_parts.append(f"MATCH ({source_var}:{first_step['source_label']})")

        # Add each step
        for i, step in enumerate(self.steps):
            target_var = f"n{i+1}"
            rel_var = f"r{i}"

            # Determine relationship direction
            if step["direction"] == "outgoing":
                rel_pattern = f"({source_var})-[{rel_var}:{step['relationship_type']}]->({target_var}:{step['target_label']})"
            elif step["direction"] == "incoming":
                rel_pattern = f"({source_var})<-[{rel_var}:{step['relationship_type']}]-({target_var}:{step['target_label']})"
            else:  # both
                rel_pattern = f"({source_var})-[{rel_var}:{step['relationship_type']}]-({target_var}:{step['target_label']})"

            # Add OPTIONAL if the step is optional
            match_keyword = "OPTIONAL MATCH" if step["optional"] else "MATCH"
            query_parts.append(f"{match_keyword} {rel_pattern}")

            # Add relationship properties if any
            if step["properties"] and with_params:
                prop_param_name = f"props{i}"
                query_parts.append(f"WHERE ALL(k IN keys({rel_var}) WHERE {rel_var}[k] = ${prop_param_name}[k])")
                params[prop_param_name] = step["properties"]

            # Update source_var for the next step
            source_var = target_var

        # Return all nodes and relationships
        node_vars = [f"n{i}" for i in range(len(self.steps) + 1)]
        rel_vars = [f"r{i}" for i in range(len(self.steps))]
        query_parts.append(f"RETURN {', '.join(node_vars + rel_vars)}")

        return " ".join(query_parts), params


class RelationshipManager:
    """
    Manager for Neo4j relationships.

    This class provides methods for creating, querying, and analyzing
    relationships in Neo4j, with support for complex relationship patterns.
    """

    def __init__(self, db_manager: Optional[Neo4jManager] = None):
        """
        Initialize the relationship manager.

        Args:
            db_manager: Optional Neo4jManager instance. If not provided,
                       uses the singleton instance.
        """
        self.logger = logging.getLogger(__name__)

        if db_manager:
            self.db_manager = db_manager
        else:
            from .db_manager import db_manager as default_manager
            self.db_manager = default_manager

        # Dictionary of registered relationship types
        self._relationship_types: Dict[str, RelationshipType] = {}

        # Dictionary of registered relationship patterns
        self._relationship_patterns: Dict[str, RelationshipPattern] = {}

    def register_relationship_type(self, relationship_type: RelationshipType) -> None:
        """
        Register a relationship type.

        Args:
            relationship_type: RelationshipType instance to register

        Raises:
            ValueError: If a relationship type with the same name already exists
        """
        if relationship_type.name in self._relationship_types:
            raise ValueError(f"Relationship type '{relationship_type.name}' already registered")

        self._relationship_types[relationship_type.name] = relationship_type
        self.logger.debug(f"Registered relationship type: {relationship_type.name}")

    def get_relationship_type(self, name: str) -> Optional[RelationshipType]:
        """
        Get a registered relationship type by name.

        Args:
            name: Name of the relationship type

        Returns:
            RelationshipType if found, None otherwise
        """
        return self._relationship_types.get(name)

    def register_relationship_pattern(self, pattern: RelationshipPattern) -> None:
        """
        Register a relationship pattern.

        Args:
            pattern: RelationshipPattern instance to register

        Raises:
            ValueError: If a pattern with the same name already exists
        """
        if pattern.name in self._relationship_patterns:
            raise ValueError(f"Relationship pattern '{pattern.name}' already registered")

        self._relationship_patterns[pattern.name] = pattern
        self.logger.debug(f"Registered relationship pattern: {pattern.name}")

    def get_relationship_pattern(self, name: str) -> Optional[RelationshipPattern]:
        """
        Get a registered relationship pattern by name.

        Args:
            name: Name of the relationship pattern

        Returns:
            RelationshipPattern if found, None otherwise
        """
        return self._relationship_patterns.get(name)

    def create_relationship(self, source_id: Union[str, int], target_id: Union[str, int], relationship_type: str,
                           properties: Optional[Dict[str, Any]] = None,
                           connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a relationship between two nodes by their IDs.

        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relationship_type: Type of relationship to create
            properties: Optional properties for the relationship
            connection_name: Optional name of the connection to use

        Returns:
            Dictionary containing the created relationship

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
            ValueError: If the relationship type is not valid
        """
        # Validate relationship type if registered
        rel_type = self.get_relationship_type(relationship_type)
        if rel_type:
            properties = properties or {}

            # Merge with default properties
            merged_props = {**rel_type.properties, **properties}

            # Validate properties
            is_valid, errors = rel_type.validate_properties(merged_props)
            if not is_valid:
                raise ValueError(f"Invalid properties for relationship type '{relationship_type}': {', '.join(errors)}")

            properties = merged_props

        # Create the relationship
        query = """
        MATCH (a), (b)
        WHERE elementId(a) = $source_id AND elementId(b) = $target_id
        CREATE (a)-[r:`{relationship_type}`]->(b)
        SET r = $properties
        RETURN r
        """.format(relationship_type=relationship_type)

        params = {
            "source_id": source_id,
            "target_id": target_id,
            "properties": properties or {}
        }

        result = self.db_manager.execute_query(query, params, connection_name)
        if not result:
            raise QueryError(f"Failed to create relationship of type '{relationship_type}'")

        return result[0]["r"]

    def create_relationship_by_properties(self, source_label: str, source_property: str, source_value: Any,
                                         target_label: str, target_property: str, target_value: Any,
                                         relationship_type: str, properties: Optional[Dict[str, Any]] = None,
                                         connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a relationship between two nodes identified by their properties.

        Args:
            source_label: Label of the source node
            source_property: Property name to identify the source node
            source_value: Property value to identify the source node
            target_label: Label of the target node
            target_property: Property name to identify the target node
            target_value: Property value to identify the target node
            relationship_type: Type of relationship to create
            properties: Optional properties for the relationship
            connection_name: Optional name of the connection to use

        Returns:
            Dictionary containing the created relationship

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
            ValueError: If the relationship type is not valid
        """
        # Validate relationship type if registered
        rel_type = self.get_relationship_type(relationship_type)
        if rel_type:
            properties = properties or {}

            # Merge with default properties
            merged_props = {**rel_type.properties, **properties}

            # Validate properties
            is_valid, errors = rel_type.validate_properties(merged_props)
            if not is_valid:
                raise ValueError(f"Invalid properties for relationship type '{relationship_type}': {', '.join(errors)}")

            properties = merged_props

        # Use the create_relationship template
        from .query_templates import template_registry
        query, params = template_registry.render_template(
            "create_relationship",
            {
                "source_label": source_label,
                "source_property": source_property,
                "source_value": source_value,
                "target_label": target_label,
                "target_property": target_property,
                "target_value": target_value,
                "relationship_type": relationship_type,
                "properties": properties or {}
            }
        )

        result = self.db_manager.execute_query(query, params, connection_name)
        if not result:
            raise QueryError(f"Failed to create relationship of type '{relationship_type}'")

        return result[0]["r"]

    def get_relationships(self, source_label: str, relationship_type: str, target_label: str,
                         limit: int = 100, connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get relationships between nodes with the given labels and relationship type.

        Args:
            source_label: Label of the source nodes
            relationship_type: Type of relationship
            target_label: Label of the target nodes
            limit: Maximum number of relationships to return
            connection_name: Optional name of the connection to use

        Returns:
            List of dictionaries containing relationship details

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        # Use the get_relationships template
        from .query_templates import template_registry
        query, params = template_registry.render_template(
            "get_relationships",
            {
                "source_label": source_label,
                "relationship_type": relationship_type,
                "target_label": target_label,
                "limit": limit
            }
        )

        results = self.db_manager.execute_query(query, params, connection_name)

        # Process results to extract relationship details
        relationships = []
        for result in results:
            source_node = result.get('a', {})
            relationship = result.get('r', {})
            target_node = result.get('b', {})

            relationships.append({
                "source": source_node,
                "relationship": relationship,
                "target": target_node
            })

        return relationships

    def get_relationship_by_id(self, relationship_id: Union[str, int],
                              connection_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a relationship by its ID.

        Args:
            relationship_id: ID of the relationship
            connection_name: Optional name of the connection to use

        Returns:
            Dictionary containing the relationship details, or None if not found

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        query = """
        MATCH (a)-[r]->(b)
        WHERE elementId(r) = $relationship_id
        RETURN a, r, b
        """

        params = {"relationship_id": relationship_id}

        results = self.db_manager.execute_query(query, params, connection_name)
        if not results:
            return None

        result = results[0]
        return {
            "source": result.get('a', {}),
            "relationship": result.get('r', {}),
            "target": result.get('b', {})
        }

    def update_relationship_properties(self, relationship_id: Union[str, int], properties: Dict[str, Any],
                                      connection_name: Optional[str] = None) -> bool:
        """
        Update the properties of a relationship.

        Args:
            relationship_id: ID of the relationship
            properties: New properties to set
            connection_name: Optional name of the connection to use

        Returns:
            True if the relationship was updated, False otherwise

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        query = """
        MATCH ()-[r]->()
        WHERE elementId(r) = $relationship_id
        SET r += $properties
        RETURN r
        """

        params = {
            "relationship_id": relationship_id,
            "properties": properties
        }

        results = self.db_manager.execute_query(query, params, connection_name)
        return len(results) > 0

    def delete_relationship(self, relationship_id: Union[str, int],
                           connection_name: Optional[str] = None) -> bool:
        """
        Delete a relationship by its ID.

        Args:
            relationship_id: ID of the relationship
            connection_name: Optional name of the connection to use

        Returns:
            True if the relationship was deleted, False otherwise

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        query = """
        MATCH ()-[r]->()
        WHERE elementId(r) = $relationship_id
        DELETE r
        """

        params = {"relationship_id": relationship_id}

        try:
            self.db_manager.execute_query(query, params, connection_name)
            return True
        except QueryError:
            return False

    def find_path(self, start_node_id: Union[str, int], end_node_id: Union[str, int], relationship_types: Optional[List[str]] = None,
                 max_depth: int = 5, connection_name: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Find a path between two nodes.

        Args:
            start_node_id: ID of the start node
            end_node_id: ID of the end node
            relationship_types: Optional list of relationship types to consider
            max_depth: Maximum path length
            connection_name: Optional name of the connection to use

        Returns:
            List of dictionaries representing the path, or None if no path found

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        # Build relationship type filter
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(f"`{r}`" for r in relationship_types)
            rel_filter = f":{rel_types}"

        query = f"""
        MATCH (start), (end)
        WHERE elementId(start) = $start_id AND elementId(end) = $end_id
        MATCH path = shortestPath((start)-[{rel_filter}*1..{max_depth}]->(end))
        RETURN path
        """

        params = {
            "start_id": start_node_id,
            "end_id": end_node_id
        }

        results = self.db_manager.execute_query(query, params, connection_name)
        if not results:
            return None

        # Extract path from results
        path = results[0].get("path", [])
        if not path:
            return None

        # Process path into a list of nodes and relationships
        path_elements = []
        for i, element in enumerate(path):
            if i % 2 == 0:  # Node
                path_elements.append({"type": "node", "data": element})
            else:  # Relationship
                path_elements.append({"type": "relationship", "data": element})

        return path_elements

    def execute_pattern(self, pattern: Union[RelationshipPattern, str],
                       connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a relationship pattern query.

        Args:
            pattern: RelationshipPattern instance or name of a registered pattern
            connection_name: Optional name of the connection to use

        Returns:
            List of dictionaries containing the query results

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
            ValueError: If the pattern is not found
        """
        # Get the pattern if a name was provided
        if isinstance(pattern, str):
            pattern_obj = self.get_relationship_pattern(pattern)
            if not pattern_obj:
                raise ValueError(f"Relationship pattern '{pattern}' not found")
            pattern = pattern_obj

        # Generate the Cypher query
        query, params = pattern.to_cypher()

        # Execute the query
        return self.db_manager.execute_query(query, params, connection_name)

    def get_relationship_types(self, connection_name: Optional[str] = None) -> List[str]:
        """
        Get all relationship types in the database.

        Args:
            connection_name: Optional name of the connection to use

        Returns:
            List of relationship type names

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        query = "CALL db.relationshipTypes()"
        results = self.db_manager.execute_query(query, connection_name=connection_name)
        return [record["relationshipType"] for record in results]

    def get_relationship_type_counts(self, connection_name: Optional[str] = None) -> Dict[str, int]:
        """
        Get counts of relationships by type.

        Args:
            connection_name: Optional name of the connection to use

        Returns:
            Dictionary mapping relationship types to counts

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        query = """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
        """

        results = self.db_manager.execute_query(query, connection_name=connection_name)
        return {record["type"]: record["count"] for record in results}

    def analyze_relationships(self, connection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze relationships in the database.

        Args:
            connection_name: Optional name of the connection to use

        Returns:
            Dictionary containing relationship analysis results

        Raises:
            ConnectionError: If there is no active connection
            QueryError: If the query execution fails
        """
        # Get relationship type counts
        type_counts = self.get_relationship_type_counts(connection_name)

        # Get total relationship count
        total_count = sum(type_counts.values())

        # Get node counts
        node_query = "MATCH (n) RETURN count(n) AS count"
        node_count = self.db_manager.query_to_value(node_query, connection_name=connection_name)

        # Calculate average relationships per node
        avg_rels_per_node = total_count / max(1, node_count)

        # Get most connected nodes
        connected_query = """
        MATCH (n)
        WITH n, size((n)--()) AS connections
        ORDER BY connections DESC
        LIMIT 10
        RETURN n, connections
        """

        connected_results = self.db_manager.execute_query(connected_query, connection_name=connection_name)
        most_connected = [{"node": record["n"], "connections": record["connections"]} for record in connected_results]

        return {
            "total_relationships": total_count,
            "relationship_types": type_counts,
            "total_nodes": node_count,
            "avg_relationships_per_node": avg_rels_per_node,
            "most_connected_nodes": most_connected
        }


# Create a singleton instance
relationship_manager = RelationshipManager()
