"""
Advanced Query Builder for Science Data Kit

This module provides functionality for building complex Neo4j Cypher queries
programmatically, with support for nodes, relationships, filters, and more.
"""

import re
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from enum import Enum

from .query_templates import QueryTemplate, template_registry


class NodePattern:
    """
    Represents a node pattern in a Cypher query.
    
    This class provides a way to define a node pattern with variable name,
    labels, and properties.
    """
    
    def __init__(self, variable: str, labels: Optional[List[str]] = None, 
                properties: Optional[Dict[str, Any]] = None):
        """
        Initialize a node pattern.
        
        Args:
            variable: Variable name for the node
            labels: Optional list of labels for the node
            properties: Optional dictionary of properties for the node
        """
        self.variable = variable
        self.labels = labels or []
        self.properties = properties or {}
    
    def to_cypher(self) -> str:
        """
        Convert the node pattern to Cypher syntax.
        
        Returns:
            Cypher representation of the node pattern
        """
        # Build labels part
        labels_str = "".join([f":{label}" for label in self.labels])
        
        # Build properties part
        if self.properties:
            props_list = [f"{k}: ${self.variable}_{k}" for k in self.properties.keys()]
            props_str = f" {{{', '.join(props_list)}}}"
        else:
            props_str = ""
        
        return f"({self.variable}{labels_str}{props_str})"
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get parameters for the node pattern.
        
        Returns:
            Dictionary of parameters for the node pattern
        """
        return {f"{self.variable}_{k}": v for k, v in self.properties.items()}


class RelationshipDirection(Enum):
    """Enum for relationship directions in Cypher."""
    OUTGOING = 1  # -->
    INCOMING = 2  # <--
    UNDIRECTED = 3  # --


class RelationshipPattern:
    """
    Represents a relationship pattern in a Cypher query.
    
    This class provides a way to define a relationship pattern with variable name,
    type, direction, and properties.
    """
    
    def __init__(self, variable: str, rel_type: Optional[str] = None,
                direction: RelationshipDirection = RelationshipDirection.OUTGOING,
                properties: Optional[Dict[str, Any]] = None):
        """
        Initialize a relationship pattern.
        
        Args:
            variable: Variable name for the relationship
            rel_type: Optional relationship type
            direction: Direction of the relationship
            properties: Optional dictionary of properties for the relationship
        """
        self.variable = variable
        self.rel_type = rel_type
        self.direction = direction
        self.properties = properties or {}
    
    def to_cypher(self) -> str:
        """
        Convert the relationship pattern to Cypher syntax.
        
        Returns:
            Cypher representation of the relationship pattern
        """
        # Build type part
        type_str = f":{self.rel_type}" if self.rel_type else ""
        
        # Build properties part
        if self.properties:
            props_list = [f"{k}: ${self.variable}_{k}" for k in self.properties.keys()]
            props_str = f" {{{', '.join(props_list)}}}"
        else:
            props_str = ""
        
        # Build direction part
        if self.direction == RelationshipDirection.OUTGOING:
            return f"-[{self.variable}{type_str}{props_str}]->"
        elif self.direction == RelationshipDirection.INCOMING:
            return f"<-[{self.variable}{type_str}{props_str}]-"
        else:  # UNDIRECTED
            return f"-[{self.variable}{type_str}{props_str}]-"
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get parameters for the relationship pattern.
        
        Returns:
            Dictionary of parameters for the relationship pattern
        """
        return {f"{self.variable}_{k}": v for k, v in self.properties.items()}


class PathPattern:
    """
    Represents a path pattern in a Cypher query.
    
    This class provides a way to define a path pattern with nodes and relationships.
    """
    
    def __init__(self, nodes: Optional[List[NodePattern]] = None,
                relationships: Optional[List[RelationshipPattern]] = None):
        """
        Initialize a path pattern.
        
        Args:
            nodes: Optional list of node patterns
            relationships: Optional list of relationship patterns
        """
        self.nodes = nodes or []
        self.relationships = relationships or []
        
        # Validate that there is one more node than relationships
        if len(self.nodes) != len(self.relationships) + 1:
            raise ValueError("Number of nodes must be one more than number of relationships")
    
    def to_cypher(self) -> str:
        """
        Convert the path pattern to Cypher syntax.
        
        Returns:
            Cypher representation of the path pattern
        """
        # Interleave nodes and relationships
        path_parts = []
        for i in range(len(self.nodes)):
            path_parts.append(self.nodes[i].to_cypher())
            if i < len(self.relationships):
                path_parts.append(self.relationships[i].to_cypher())
        
        return "".join(path_parts)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get parameters for the path pattern.
        
        Returns:
            Dictionary of parameters for the path pattern
        """
        params = {}
        for node in self.nodes:
            params.update(node.get_parameters())
        for rel in self.relationships:
            params.update(rel.get_parameters())
        return params


class WhereClause:
    """
    Represents a WHERE clause in a Cypher query.
    
    This class provides a way to define complex WHERE conditions with
    support for AND, OR, and nested conditions.
    """
    
    class Operator(Enum):
        """Enum for operators in WHERE conditions."""
        EQUALS = "="
        NOT_EQUALS = "<>"
        GREATER_THAN = ">"
        GREATER_THAN_OR_EQUAL = ">="
        LESS_THAN = "<"
        LESS_THAN_OR_EQUAL = "<="
        IN = "IN"
        CONTAINS = "CONTAINS"
        STARTS_WITH = "STARTS WITH"
        ENDS_WITH = "ENDS WITH"
        IS_NULL = "IS NULL"
        IS_NOT_NULL = "IS NOT NULL"
    
    def __init__(self):
        """Initialize a WHERE clause."""
        self.conditions = []
        self.parameters = {}
    
    def add_condition(self, variable: str, property_name: str, operator: Operator, 
                     value: Any, param_name: Optional[str] = None) -> 'WhereClause':
        """
        Add a condition to the WHERE clause.
        
        Args:
            variable: Variable name for the node or relationship
            property_name: Property name
            operator: Operator for the condition
            value: Value for the condition
            param_name: Optional parameter name (if not provided, one will be generated)
            
        Returns:
            Self for method chaining
        """
        # Generate parameter name if not provided
        if param_name is None:
            param_name = f"{variable}_{property_name}_{len(self.conditions)}"
        
        # Handle special operators
        if operator == self.Operator.IS_NULL:
            self.conditions.append(f"{variable}.{property_name} IS NULL")
        elif operator == self.Operator.IS_NOT_NULL:
            self.conditions.append(f"{variable}.{property_name} IS NOT NULL")
        else:
            # Add condition and parameter
            self.conditions.append(f"{variable}.{property_name} {operator.value} ${param_name}")
            self.parameters[param_name] = value
        
        return self
    
    def add_raw_condition(self, condition: str, parameters: Optional[Dict[str, Any]] = None) -> 'WhereClause':
        """
        Add a raw condition to the WHERE clause.
        
        Args:
            condition: Raw condition string
            parameters: Optional parameters for the condition
            
        Returns:
            Self for method chaining
        """
        self.conditions.append(condition)
        if parameters:
            self.parameters.update(parameters)
        return self
    
    def to_cypher(self) -> str:
        """
        Convert the WHERE clause to Cypher syntax.
        
        Returns:
            Cypher representation of the WHERE clause
        """
        if not self.conditions:
            return ""
        
        return f"WHERE {' AND '.join(self.conditions)}"
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get parameters for the WHERE clause.
        
        Returns:
            Dictionary of parameters for the WHERE clause
        """
        return self.parameters


class ReturnClause:
    """
    Represents a RETURN clause in a Cypher query.
    
    This class provides a way to define what to return from a Cypher query,
    with support for expressions, aliases, and aggregations.
    """
    
    def __init__(self):
        """Initialize a RETURN clause."""
        self.expressions = []
    
    def add_expression(self, expression: str, alias: Optional[str] = None) -> 'ReturnClause':
        """
        Add an expression to the RETURN clause.
        
        Args:
            expression: Expression to return
            alias: Optional alias for the expression
            
        Returns:
            Self for method chaining
        """
        if alias:
            self.expressions.append(f"{expression} AS {alias}")
        else:
            self.expressions.append(expression)
        return self
    
    def to_cypher(self) -> str:
        """
        Convert the RETURN clause to Cypher syntax.
        
        Returns:
            Cypher representation of the RETURN clause
        """
        if not self.expressions:
            return ""
        
        return f"RETURN {', '.join(self.expressions)}"


class OrderByClause:
    """
    Represents an ORDER BY clause in a Cypher query.
    
    This class provides a way to define sorting for a Cypher query.
    """
    
    class Direction(Enum):
        """Enum for sort directions."""
        ASCENDING = "ASC"
        DESCENDING = "DESC"
    
    def __init__(self):
        """Initialize an ORDER BY clause."""
        self.expressions = []
    
    def add_expression(self, expression: str, direction: Direction = Direction.ASCENDING) -> 'OrderByClause':
        """
        Add an expression to the ORDER BY clause.
        
        Args:
            expression: Expression to sort by
            direction: Sort direction
            
        Returns:
            Self for method chaining
        """
        self.expressions.append(f"{expression} {direction.value}")
        return self
    
    def to_cypher(self) -> str:
        """
        Convert the ORDER BY clause to Cypher syntax.
        
        Returns:
            Cypher representation of the ORDER BY clause
        """
        if not self.expressions:
            return ""
        
        return f"ORDER BY {', '.join(self.expressions)}"


class LimitClause:
    """
    Represents a LIMIT clause in a Cypher query.
    
    This class provides a way to limit the number of results returned.
    """
    
    def __init__(self, limit: Optional[int] = None):
        """
        Initialize a LIMIT clause.
        
        Args:
            limit: Optional limit value
        """
        self.limit = limit
    
    def to_cypher(self) -> str:
        """
        Convert the LIMIT clause to Cypher syntax.
        
        Returns:
            Cypher representation of the LIMIT clause
        """
        if self.limit is None:
            return ""
        
        return f"LIMIT {self.limit}"


class SkipClause:
    """
    Represents a SKIP clause in a Cypher query.
    
    This class provides a way to skip a number of results.
    """
    
    def __init__(self, skip: Optional[int] = None):
        """
        Initialize a SKIP clause.
        
        Args:
            skip: Optional skip value
        """
        self.skip = skip
    
    def to_cypher(self) -> str:
        """
        Convert the SKIP clause to Cypher syntax.
        
        Returns:
            Cypher representation of the SKIP clause
        """
        if self.skip is None or self.skip <= 0:
            return ""
        
        return f"SKIP {self.skip}"


class QueryBuilder:
    """
    Advanced query builder for Neo4j Cypher queries.
    
    This class provides a way to build complex Cypher queries programmatically,
    with support for nodes, relationships, filters, and more.
    """
    
    def __init__(self):
        """Initialize a query builder."""
        self.match_patterns = []
        self.where_clause = WhereClause()
        self.return_clause = ReturnClause()
        self.order_by_clause = OrderByClause()
        self.limit_clause = LimitClause()
        self.skip_clause = SkipClause()
        self.parameters = {}
    
    def match(self, pattern: Union[NodePattern, PathPattern]) -> 'QueryBuilder':
        """
        Add a MATCH pattern to the query.
        
        Args:
            pattern: Node or path pattern to match
            
        Returns:
            Self for method chaining
        """
        self.match_patterns.append(pattern)
        self.parameters.update(pattern.get_parameters())
        return self
    
    def where(self, where_clause: WhereClause) -> 'QueryBuilder':
        """
        Set the WHERE clause for the query.
        
        Args:
            where_clause: WHERE clause to set
            
        Returns:
            Self for method chaining
        """
        self.where_clause = where_clause
        self.parameters.update(where_clause.get_parameters())
        return self
    
    def returns(self, return_clause: ReturnClause) -> 'QueryBuilder':
        """
        Set the RETURN clause for the query.
        
        Args:
            return_clause: RETURN clause to set
            
        Returns:
            Self for method chaining
        """
        self.return_clause = return_clause
        return self
    
    def order_by(self, order_by_clause: OrderByClause) -> 'QueryBuilder':
        """
        Set the ORDER BY clause for the query.
        
        Args:
            order_by_clause: ORDER BY clause to set
            
        Returns:
            Self for method chaining
        """
        self.order_by_clause = order_by_clause
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        """
        Set the LIMIT clause for the query.
        
        Args:
            limit: Limit value
            
        Returns:
            Self for method chaining
        """
        self.limit_clause = LimitClause(limit)
        return self
    
    def skip(self, skip: int) -> 'QueryBuilder':
        """
        Set the SKIP clause for the query.
        
        Args:
            skip: Skip value
            
        Returns:
            Self for method chaining
        """
        self.skip_clause = SkipClause(skip)
        return self
    
    def build(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build the Cypher query.
        
        Returns:
            Tuple of (query, parameters)
        """
        # Build MATCH clause
        match_clauses = []
        for pattern in self.match_patterns:
            match_clauses.append(f"MATCH {pattern.to_cypher()}")
        
        # Build query parts
        query_parts = []
        if match_clauses:
            query_parts.extend(match_clauses)
        
        # Add WHERE clause
        where_str = self.where_clause.to_cypher()
        if where_str:
            query_parts.append(where_str)
        
        # Add RETURN clause
        return_str = self.return_clause.to_cypher()
        if return_str:
            query_parts.append(return_str)
        else:
            # Default return if none specified
            query_parts.append("RETURN *")
        
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
        
        return query, self.parameters


# Example usage:
def example_query_builder():
    """
    Example of using the query builder.
    
    Returns:
        Tuple of (query, parameters)
    """
    # Create a query builder
    builder = QueryBuilder()
    
    # Create node patterns
    person = NodePattern("p", ["Person"], {"name": "John"})
    movie = NodePattern("m", ["Movie"])
    
    # Create relationship pattern
    acted_in = RelationshipPattern("r", "ACTED_IN")
    
    # Create path pattern
    path = PathPattern([person, movie], [acted_in])
    
    # Create WHERE clause
    where = WhereClause()
    where.add_condition("m", "title", WhereClause.Operator.CONTAINS, "Matrix")
    
    # Create RETURN clause
    returns = ReturnClause()
    returns.add_expression("p.name", "actor")
    returns.add_expression("m.title", "movie")
    
    # Create ORDER BY clause
    order_by = OrderByClause()
    order_by.add_expression("m.title", OrderByClause.Direction.ASCENDING)
    
    # Build the query
    builder.match(path).where(where).returns(returns).order_by(order_by).limit(10)
    
    return builder.build()