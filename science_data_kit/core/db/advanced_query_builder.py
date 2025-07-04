"""
Advanced Query Builder for Science Data Kit

This module provides an enhanced query builder for Neo4j Cypher queries,
building on the base QueryBuilder with additional features like template integration,
query optimization, batch requests, and more sophisticated query construction capabilities.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

from .query_builder import (
    QueryBuilder, NodePattern, RelationshipPattern, PathPattern,
    WhereClause, ReturnClause, OrderByClause, LimitClause, SkipClause
)
from .query_templates import QueryTemplate, template_registry


class QueryOptimizer:
    """
    Optimizer for Cypher queries.

    This class analyzes queries and provides optimization suggestions
    to improve query performance.
    """

    def __init__(self):
        """Initialize the query optimizer."""
        self.logger = logging.getLogger(__name__)

    def analyze_query(self, query: str) -> List[str]:
        """
        Analyze a Cypher query and provide optimization suggestions.

        Args:
            query: The Cypher query to analyze

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Check for missing indexes
        if "WHERE" in query and not "USING INDEX" in query:
            suggestions.append("Consider adding indexes for properties used in WHERE clauses")

        # Check for inefficient patterns
        if "MATCH (n)" in query and not "MATCH (n:" in query:
            suggestions.append("Specify node labels in MATCH patterns to improve performance")

        # Check for large result sets without limits
        if "RETURN" in query and not "LIMIT" in query:
            suggestions.append("Consider adding a LIMIT clause to prevent large result sets")

        # Check for inefficient relationship traversals
        if "-[*]-" in query:
            suggestions.append("Unbounded variable length paths can be expensive, consider adding limits")

        return suggestions


class AdvancedQueryBuilder(QueryBuilder):
    """
    Advanced query builder for Neo4j Cypher queries.

    This class extends the base QueryBuilder with additional features like
    template integration, query optimization, and more sophisticated query construction.
    """

    def __init__(self):
        """Initialize an advanced query builder."""
        super().__init__()
        self.optimizer = QueryOptimizer()
        self.with_clauses = []
        self.merge_patterns = []
        self.create_patterns = []
        self.delete_expressions = []
        self.set_clauses = []
        self.remove_clauses = []
        self.logger = logging.getLogger(__name__)

    def from_template(self, template_name: str, parameters: Dict[str, Any]) -> 'AdvancedQueryBuilder':
        """
        Initialize the query builder from a template.

        Args:
            template_name: Name of the template to use
            parameters: Parameters for the template

        Returns:
            Self for method chaining

        Raises:
            ValueError: If the template is not found
        """
        template = template_registry.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Render the template
        query, params = template.render(parameters)

        # Store the rendered query for later use
        self._template_query = query
        self.parameters.update(params)

        return self

    def with_clause(self, expressions: List[str]) -> 'AdvancedQueryBuilder':
        """
        Add a WITH clause to the query.

        Args:
            expressions: List of expressions for the WITH clause

        Returns:
            Self for method chaining
        """
        self.with_clauses.append(expressions)
        return self

    def merge(self, pattern: Union[NodePattern, PathPattern]) -> 'AdvancedQueryBuilder':
        """
        Add a MERGE pattern to the query.

        Args:
            pattern: Node or path pattern to merge

        Returns:
            Self for method chaining
        """
        self.merge_patterns.append(pattern)
        self.parameters.update(pattern.get_parameters())
        return self

    def create(self, pattern: Union[NodePattern, PathPattern]) -> 'AdvancedQueryBuilder':
        """
        Add a CREATE pattern to the query.

        Args:
            pattern: Node or path pattern to create

        Returns:
            Self for method chaining
        """
        self.create_patterns.append(pattern)
        self.parameters.update(pattern.get_parameters())
        return self

    def delete(self, expressions: List[str], detach: bool = False) -> 'AdvancedQueryBuilder':
        """
        Add a DELETE clause to the query.

        Args:
            expressions: List of expressions to delete
            detach: Whether to use DETACH DELETE

        Returns:
            Self for method chaining
        """
        self.delete_expressions.append((expressions, detach))
        return self

    def set(self, assignments: List[str]) -> 'AdvancedQueryBuilder':
        """
        Add a SET clause to the query.

        Args:
            assignments: List of assignment expressions

        Returns:
            Self for method chaining
        """
        self.set_clauses.append(assignments)
        return self

    def remove(self, expressions: List[str]) -> 'AdvancedQueryBuilder':
        """
        Add a REMOVE clause to the query.

        Args:
            expressions: List of expressions to remove

        Returns:
            Self for method chaining
        """
        self.remove_clauses.append(expressions)
        return self

    def build(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build the Cypher query.

        Returns:
            Tuple of (query, parameters)
        """
        # If we're using a template and no other clauses have been added, just return the template
        if hasattr(self, '_template_query') and not (
            self.match_patterns or self.merge_patterns or self.create_patterns or
            self.delete_expressions or self.set_clauses or self.remove_clauses
        ):
            return self._template_query, self.parameters

        # Build query parts
        query_parts = []

        # Add MATCH clauses
        match_clauses = []
        for pattern in self.match_patterns:
            match_clauses.append(f"MATCH {pattern.to_cypher()}")

        if match_clauses:
            query_parts.extend(match_clauses)

        # Add MERGE clauses
        merge_clauses = []
        for pattern in self.merge_patterns:
            merge_clauses.append(f"MERGE {pattern.to_cypher()}")

        if merge_clauses:
            query_parts.extend(merge_clauses)

        # Add CREATE clauses
        create_clauses = []
        for pattern in self.create_patterns:
            create_clauses.append(f"CREATE {pattern.to_cypher()}")

        if create_clauses:
            query_parts.extend(create_clauses)

        # Add WHERE clause
        where_str = self.where_clause.to_cypher()
        if where_str:
            query_parts.append(where_str)

        # Add WITH clauses
        for expressions in self.with_clauses:
            query_parts.append(f"WITH {', '.join(expressions)}")

        # Add SET clauses
        for assignments in self.set_clauses:
            query_parts.append(f"SET {', '.join(assignments)}")

        # Add REMOVE clauses
        for expressions in self.remove_clauses:
            query_parts.append(f"REMOVE {', '.join(expressions)}")

        # Add DELETE clauses
        for expressions, detach in self.delete_expressions:
            if detach:
                query_parts.append(f"DETACH DELETE {', '.join(expressions)}")
            else:
                query_parts.append(f"DELETE {', '.join(expressions)}")

        # Add RETURN clause
        return_str = self.return_clause.to_cypher()
        if return_str:
            query_parts.append(return_str)

        # Add ORDER BY clause
        order_by_str = self.order_by_clause.to_cypher()
        if order_by_str:
            query_parts.append(order_by_str)

        # Add SKIP clause
        skip_str = self.skip_clause.to_cypher()
        if skip_str:
            query_parts.append(skip_str)

        # Add LIMIT clause
        limit_str = self.limit_clause.to_cypher()
        if limit_str:
            query_parts.append(limit_str)

        # Join query parts
        query = "\n".join(query_parts)

        # Get optimization suggestions
        suggestions = self.optimizer.analyze_query(query)
        if suggestions:
            self.logger.info("Query optimization suggestions:")
            for suggestion in suggestions:
                self.logger.info(f"- {suggestion}")

        return query, self.parameters


class QueryDirector:
    """
    Director for building common query patterns.

    This class provides methods for building common query patterns
    using the AdvancedQueryBuilder.
    """

    @staticmethod
    def build_node_creation_query(
        label: str,
        properties: Dict[str, Any],
        variable: str = "n"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build a query for creating a node.

        Args:
            label: Label for the node
            properties: Properties for the node
            variable: Variable name for the node

        Returns:
            Tuple of (query, parameters)
        """
        builder = AdvancedQueryBuilder()
        node = NodePattern(variable, [label], properties)

        return builder.create(node).returns(
            ReturnClause().add_expression(variable)
        ).build()

    @staticmethod
    def build_relationship_creation_query(
        from_label: str,
        from_property: str,
        from_value: Any,
        to_label: str,
        to_property: str,
        to_value: Any,
        rel_type: str,
        rel_properties: Optional[Dict[str, Any]] = None,
        from_variable: str = "a",
        to_variable: str = "b",
        rel_variable: str = "r"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build a query for creating a relationship between two nodes.

        Args:
            from_label: Label for the source node
            from_property: Property name to identify the source node
            from_value: Property value to identify the source node
            to_label: Label for the target node
            to_property: Property name to identify the target node
            to_value: Property value to identify the target node
            rel_type: Type of relationship to create
            rel_properties: Properties for the relationship
            from_variable: Variable name for the source node
            to_variable: Variable name for the target node
            rel_variable: Variable name for the relationship

        Returns:
            Tuple of (query, parameters)
        """
        builder = AdvancedQueryBuilder()

        # Create node patterns
        from_node = NodePattern(from_variable, [from_label], {from_property: from_value})
        to_node = NodePattern(to_variable, [to_label], {to_property: to_value})

        # Create relationship pattern
        rel = RelationshipPattern(rel_variable, rel_type, properties=rel_properties or {})

        # Create path pattern
        path = PathPattern([from_node, to_node], [rel])

        return builder.match(
            NodePattern(from_variable, [from_label])
        ).where(
            WhereClause().add_condition(from_variable, from_property, WhereClause.Operator.EQUALS, from_value)
        ).match(
            NodePattern(to_variable, [to_label])
        ).where(
            WhereClause().add_condition(to_variable, to_property, WhereClause.Operator.EQUALS, to_value)
        ).create(
            path
        ).returns(
            ReturnClause().add_expression(rel_variable)
        ).build()

    @staticmethod
    def build_node_search_query(
        label: str,
        properties: Dict[str, Any],
        return_fields: Optional[List[str]] = None,
        variable: str = "n",
        limit: Optional[int] = 100
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build a query for searching nodes.

        Args:
            label: Label for the nodes
            properties: Properties to search for
            return_fields: Fields to return
            variable: Variable name for the nodes
            limit: Maximum number of nodes to return

        Returns:
            Tuple of (query, parameters)
        """
        builder = AdvancedQueryBuilder()
        node = NodePattern(variable, [label])

        # Add match clause
        builder.match(node)

        # Add where clause
        where = WhereClause()
        for prop, value in properties.items():
            where.add_condition(variable, prop, WhereClause.Operator.EQUALS, value)

        builder.where(where)

        # Add return clause
        returns = ReturnClause()
        if return_fields:
            for field in return_fields:
                returns.add_expression(f"{variable}.{field}", field)
        else:
            returns.add_expression(variable)

        builder.returns(returns)

        # Add limit
        if limit is not None:
            builder.limit(limit)

        return builder.build()


def example_advanced_query_builder():
    """
    Example of using the advanced query builder.

    Returns:
        Tuple of (query, parameters)
    """
    # Create an advanced query builder
    builder = AdvancedQueryBuilder()

    # Create node patterns
    person = NodePattern("p", ["Person"], {"name": "John"})
    movie = NodePattern("m", ["Movie"])

    # Create relationship pattern
    acted_in = RelationshipPattern("r", "ACTED_IN", properties={"role": "Neo"})

    # Create path pattern
    path = PathPattern([person, movie], [acted_in])

    # Create WHERE clause
    where = WhereClause()
    where.add_condition("m", "title", WhereClause.Operator.CONTAINS, "Matrix")

    # Create RETURN clause
    returns = ReturnClause()
    returns.add_expression("p.name", "actor")
    returns.add_expression("m.title", "movie")
    returns.add_expression("r.role", "role")

    # Create ORDER BY clause
    order_by = OrderByClause()
    order_by.add_expression("m.title", OrderByClause.Direction.ASCENDING)

    # Build the query
    builder.match(path).where(where).returns(returns).order_by(order_by).limit(10)

    return builder.build()


def example_query_director():
    """
    Example of using the query director.

    Returns:
        List of example queries
    """
    examples = []

    # Example 1: Create a node
    query, params = QueryDirector.build_node_creation_query(
        "Person",
        {"name": "Alice", "age": 30}
    )
    examples.append((query, params))

    # Example 2: Create a relationship
    query, params = QueryDirector.build_relationship_creation_query(
        "Person", "name", "Alice",
        "Movie", "title", "The Matrix",
        "ACTED_IN",
        {"role": "Trinity"}
    )
    examples.append((query, params))

    # Example 3: Search for nodes
    query, params = QueryDirector.build_node_search_query(
        "Person",
        {"name": "Alice"},
        ["name", "age"]
    )
    examples.append((query, params))

    return examples


def example_template_integration():
    """
    Example of using templates with the advanced query builder.

    Returns:
        Tuple of (query, parameters)
    """
    # Create an advanced query builder from a template
    builder = AdvancedQueryBuilder().from_template(
        "get_nodes_by_property",
        {
            "label": "Person",
            "property": "name",
            "value": "John",
            "limit": 10
        }
    )

    return builder.build()


class BatchQueryBuilder:
    """
    Builder for batch queries.

    This class allows building multiple queries that can be executed
    in a single batch for improved performance.
    """

    def __init__(self):
        """Initialize a batch query builder."""
        self.queries = []
        self.parameters = {}
        self.logger = logging.getLogger(__name__)

    def add_query(self, query_builder: Union[QueryBuilder, AdvancedQueryBuilder]) -> 'BatchQueryBuilder':
        """
        Add a query to the batch.

        Args:
            query_builder: Query builder to add

        Returns:
            Self for method chaining
        """
        query, params = query_builder.build()

        # Generate unique parameter names to avoid conflicts
        param_mapping = {}
        for key in params:
            new_key = f"{key}_{len(self.queries)}"
            param_mapping[key] = new_key

        # Update parameter references in the query
        for old_key, new_key in param_mapping.items():
            query = query.replace(f"${{{old_key}}}", f"${{{new_key}}}")

        # Update parameters dictionary with new keys
        new_params = {new_key: params[old_key] for old_key, new_key in param_mapping.items()}

        self.queries.append(query)
        self.parameters.update(new_params)

        return self

    def add_raw_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> 'BatchQueryBuilder':
        """
        Add a raw query to the batch.

        Args:
            query: Raw Cypher query
            parameters: Parameters for the query

        Returns:
            Self for method chaining
        """
        if parameters:
            # Generate unique parameter names to avoid conflicts
            param_mapping = {}
            for key in parameters:
                new_key = f"{key}_{len(self.queries)}"
                param_mapping[key] = new_key

            # Update parameter references in the query
            for old_key, new_key in param_mapping.items():
                query = query.replace(f"${{{old_key}}}", f"${{{new_key}}}")

            # Update parameters dictionary with new keys
            new_params = {new_key: parameters[old_key] for old_key, new_key in param_mapping.items()}
            self.parameters.update(new_params)

        self.queries.append(query)

        return self

    def build(self) -> Tuple[List[str], Dict[str, Any]]:
        """
        Build the batch of queries.

        Returns:
            Tuple of (queries, parameters)
        """
        return self.queries, self.parameters


def example_batch_query_builder():
    """
    Example of using the batch query builder.

    Returns:
        Tuple of (queries, parameters)
    """
    # Create a batch query builder
    batch_builder = BatchQueryBuilder()

    # Example 1: Add a node creation query
    node_builder = AdvancedQueryBuilder()
    node = NodePattern("n", ["Person"], {"name": "John", "age": 30})
    node_builder.create(node).returns(ReturnClause().add_expression("n"))
    batch_builder.add_query(node_builder)

    # Example 2: Add a relationship creation query
    rel_builder = AdvancedQueryBuilder()
    from_node = NodePattern("a", ["Person"], {"name": "John"})
    to_node = NodePattern("b", ["Movie"], {"title": "The Matrix"})
    rel = RelationshipPattern("r", "WATCHED", properties={"rating": 5})
    path = PathPattern([from_node, to_node], [rel])
    rel_builder.match(from_node).match(to_node).create(path).returns(
        ReturnClause().add_expression("r")
    )
    batch_builder.add_query(rel_builder)

    # Example 3: Add a raw query
    batch_builder.add_raw_query(
        "MATCH (p:Person {name: $name}) RETURN p.age",
        {"name": "Alice"}
    )

    return batch_builder.build()
