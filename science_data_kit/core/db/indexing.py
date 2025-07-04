"""
Database Indexing for Science Data Kit

This module provides functionality for managing database indexes to improve query performance.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union

from .db_manager import Neo4jManager, QueryError, ConnectionError
from .metrics import query_metrics
from ..profiling.recommendations import get_database_indexing_strategy


class IndexManager:
    """
    Manages database indexes for optimizing query performance.
    
    This class provides methods for:
    - Analyzing query patterns to identify indexing opportunities
    - Creating and managing indexes
    - Monitoring index usage
    """
    
    def __init__(self, db_manager: Optional[Neo4jManager] = None):
        """
        Initialize the index manager.
        
        Args:
            db_manager: Optional Neo4jManager instance. If None, uses the singleton instance.
        """
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Use provided db_manager or get the singleton instance
        if db_manager is None:
            from .db_manager import db_manager as default_manager
            self.db_manager = default_manager
        else:
            self.db_manager = db_manager
    
    def get_existing_indexes(self) -> List[Dict[str, Any]]:
        """
        Get a list of existing indexes in the database.
        
        Returns:
            List of dictionaries containing index information
            
        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        try:
            # For Neo4j 4.x+
            result = self.db_manager.execute_query("SHOW INDEXES")
            if result:
                return result
        except QueryError:
            # Fall back to older Neo4j versions
            try:
                result = self.db_manager.execute_query("CALL db.indexes()")
                return result
            except QueryError as e:
                self.logger.error(f"Failed to get indexes: {e}")
                return []
        
        return []
    
    def create_index(self, label: str, property_name: str, index_name: Optional[str] = None) -> bool:
        """
        Create an index on a property for a specific label.
        
        Args:
            label: The node label
            property_name: The property name to index
            index_name: Optional name for the index
            
        Returns:
            True if the index was created successfully, False otherwise
            
        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        try:
            if index_name:
                # For Neo4j 4.x+
                query = f"CREATE INDEX {index_name} FOR (n:{label}) ON (n.{property_name})"
            else:
                # For Neo4j 3.x or 4.x
                query = f"CREATE INDEX ON :{label}({property_name})"
            
            self.db_manager.execute_query(query)
            self.logger.info(f"Created index on :{label}({property_name})")
            return True
        except QueryError as e:
            self.logger.error(f"Failed to create index on :{label}({property_name}): {e}")
            return False
    
    def drop_index(self, index_name: str) -> bool:
        """
        Drop an index by name.
        
        Args:
            index_name: The name of the index to drop
            
        Returns:
            True if the index was dropped successfully, False otherwise
            
        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        try:
            # For Neo4j 4.x+
            query = f"DROP INDEX {index_name}"
            self.db_manager.execute_query(query)
            self.logger.info(f"Dropped index {index_name}")
            return True
        except QueryError as e:
            self.logger.error(f"Failed to drop index {index_name}: {e}")
            return False
    
    def get_index_usage(self) -> List[Dict[str, Any]]:
        """
        Get information about index usage.
        
        Returns:
            List of dictionaries containing index usage information
            
        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        try:
            # For Neo4j 4.x+
            result = self.db_manager.execute_query("SHOW INDEX USAGE")
            if result:
                return result
        except QueryError:
            # Fall back to older Neo4j versions or if the command is not available
            self.logger.warning("SHOW INDEX USAGE command not available in this Neo4j version")
            return []
        
        return []
    
    def analyze_query_patterns(self) -> Dict[str, Any]:
        """
        Analyze query patterns to identify indexing opportunities.
        
        Returns:
            Dictionary containing analysis results
        """
        # Get indexing strategy from recommendations
        return get_database_indexing_strategy()
    
    def implement_indexing_strategy(self, strategy: Optional[Dict[str, Any]] = None, 
                                   auto_create: bool = False) -> Dict[str, Any]:
        """
        Implement an indexing strategy based on query analysis.
        
        Args:
            strategy: Optional indexing strategy. If None, generates one using analyze_query_patterns.
            auto_create: If True, automatically creates recommended indexes.
            
        Returns:
            Dictionary containing implementation results
        """
        if strategy is None:
            strategy = self.analyze_query_patterns()
        
        # Get existing indexes
        existing_indexes = self.get_existing_indexes()
        existing_index_properties = set()
        
        # Extract property names from existing indexes
        for index in existing_indexes:
            # Different Neo4j versions have different output formats
            if "properties" in index:
                # Neo4j 4.x+
                properties = index.get("properties", [])
                for prop in properties:
                    existing_index_properties.add(prop)
            elif "property_keys" in index:
                # Neo4j 3.x
                properties = index.get("property_keys", [])
                for prop in properties:
                    existing_index_properties.add(prop)
        
        # Get high and medium priority index recommendations
        high_priority = strategy.get("high_priority_indexes", [])
        medium_priority = strategy.get("medium_priority_indexes", [])
        
        # Filter out properties that already have indexes
        new_high_priority = [(prop, count) for prop, count in high_priority 
                            if prop not in existing_index_properties]
        new_medium_priority = [(prop, count) for prop, count in medium_priority 
                              if prop not in existing_index_properties]
        
        # Create indexes if auto_create is True
        created_indexes = []
        if auto_create:
            # Get node labels
            try:
                labels_query = "CALL db.labels()"
                labels_result = self.db_manager.execute_query(labels_query)
                labels = [record.get("label") for record in labels_result]
            except QueryError:
                # Fall back to a different approach
                try:
                    labels_query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
                    labels_result = self.db_manager.execute_query(labels_query)
                    labels = []
                    for record in labels_result:
                        for label_list in record.get("labels", []):
                            labels.extend(label_list)
                    labels = list(set(labels))
                except QueryError:
                    labels = []
            
            # Create indexes for high priority properties
            for prop, count in new_high_priority:
                for label in labels:
                    if self.create_index(label, prop):
                        created_indexes.append((label, prop))
        
        return {
            "existing_indexes": existing_indexes,
            "high_priority_recommendations": high_priority,
            "medium_priority_recommendations": medium_priority,
            "new_high_priority": new_high_priority,
            "new_medium_priority": new_medium_priority,
            "created_indexes": created_indexes if auto_create else []
        }
    
    def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get index recommendations based on query patterns.
        
        Returns:
            List of dictionaries containing index recommendations
        """
        strategy = self.analyze_query_patterns()
        implementation = self.implement_indexing_strategy(strategy, auto_create=False)
        
        recommendations = []
        
        # Add high priority recommendations
        for prop, count in implementation.get("new_high_priority", []):
            recommendations.append({
                "property": prop,
                "frequency": count,
                "priority": "high",
                "description": f"Create an index on property '{prop}' which appears in {count} slow queries",
                "implementation": f"CREATE INDEX ON :<Label>('{prop}')"
            })
        
        # Add medium priority recommendations
        for prop, count in implementation.get("new_medium_priority", []):
            recommendations.append({
                "property": prop,
                "frequency": count,
                "priority": "medium",
                "description": f"Create an index on property '{prop}' which appears in {count} slow queries",
                "implementation": f"CREATE INDEX ON :<Label>('{prop}')"
            })
        
        return recommendations


# Create a singleton instance
index_manager = IndexManager()