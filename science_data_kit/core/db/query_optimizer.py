"""
Query Optimizer for Science Data Kit

This module provides functionality for automatically optimizing Neo4j queries
by analyzing query patterns and implementing appropriate indexing strategies.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import pandas as pd

from .indexing import IndexManager, index_manager
from .query_profiler import QueryProfiler, query_profiler
from .db_manager import db_manager


class QueryOptimizer:
    """
    Automatically optimizes Neo4j queries by analyzing query patterns and implementing
    appropriate indexing strategies.
    
    This class provides methods for:
    - Analyzing query performance
    - Identifying indexing opportunities
    - Automatically creating recommended indexes
    - Generating optimization reports
    """
    
    def __init__(self, db_manager=None, index_manager=None, query_profiler=None):
        """
        Initialize the query optimizer.
        
        Args:
            db_manager: Optional Neo4jManager instance. If None, uses the singleton instance.
            index_manager: Optional IndexManager instance. If None, uses the singleton instance.
            query_profiler: Optional QueryProfiler instance. If None, uses the singleton instance.
        """
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Use provided instances or get the singleton instances
        self.db_manager = db_manager if db_manager is not None else db_manager
        self.index_manager = index_manager if index_manager is not None else index_manager
        self.query_profiler = query_profiler if query_profiler is not None else query_profiler
    
    def analyze_query_performance(self) -> Dict[str, Any]:
        """
        Analyze query performance to identify optimization opportunities.
        
        Returns:
            Dictionary containing analysis results
        """
        # Get slow queries
        slow_queries = self.query_profiler.get_slow_queries()
        
        # Analyze query patterns
        query_patterns = self.query_profiler.analyze_query_patterns()
        
        # Get optimization recommendations
        recommendations = self.query_profiler.get_optimization_recommendations()
        
        return {
            "slow_queries": slow_queries,
            "query_patterns": query_patterns,
            "recommendations": recommendations
        }
    
    def get_indexing_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get indexing recommendations based on query analysis.
        
        Returns:
            List of indexing recommendations
        """
        return self.index_manager.get_index_recommendations()
    
    def optimize_queries(self, auto_create_indexes: bool = False) -> Dict[str, Any]:
        """
        Optimize queries by implementing recommended indexing strategies.
        
        Args:
            auto_create_indexes: If True, automatically creates recommended indexes.
            
        Returns:
            Dictionary containing optimization results
        """
        # Get existing indexes
        existing_indexes = self.index_manager.get_existing_indexes()
        
        # Implement indexing strategy
        indexing_results = self.index_manager.implement_indexing_strategy(auto_create=auto_create_indexes)
        
        # Get query performance analysis
        performance_analysis = self.analyze_query_performance()
        
        # Combine results
        results = {
            "existing_indexes": existing_indexes,
            "indexing_results": indexing_results,
            "performance_analysis": performance_analysis,
            "auto_created_indexes": indexing_results.get("created_indexes", []) if auto_create_indexes else []
        }
        
        return results
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive optimization report.
        
        Returns:
            Dictionary containing the optimization report
        """
        # Get query profiling report
        profiling_report = self.query_profiler.generate_profiling_report()
        
        # Get indexing recommendations
        indexing_recommendations = self.get_indexing_recommendations()
        
        # Get existing indexes
        existing_indexes = self.index_manager.get_existing_indexes()
        
        # Create report
        report = {
            "profiling_report": profiling_report,
            "indexing_recommendations": indexing_recommendations,
            "existing_indexes": existing_indexes,
            "summary": {
                "total_recommendations": len(indexing_recommendations),
                "high_priority_recommendations": len([r for r in indexing_recommendations if r.get("priority") == "high"]),
                "medium_priority_recommendations": len([r for r in indexing_recommendations if r.get("priority") == "medium"]),
                "existing_indexes_count": len(existing_indexes)
            }
        }
        
        return report
    
    def optimize_specific_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize a specific query by analyzing its execution plan and creating appropriate indexes.
        
        Args:
            query: The query to optimize
            parameters: Optional parameters for the query
            
        Returns:
            Dictionary containing optimization results
        """
        # Explain the query to get execution plan
        explain_results = self.query_profiler.explain_query(query, parameters)
        
        # Extract property names from WHERE clauses in the query
        property_names = self._extract_properties_from_query(query)
        
        # Get existing indexes
        existing_indexes = self.index_manager.get_existing_indexes()
        existing_index_properties = set()
        
        # Extract property names from existing indexes
        for index in existing_indexes:
            if "properties" in index:
                properties = index.get("properties", [])
                for prop in properties:
                    existing_index_properties.add(prop)
            elif "property_keys" in index:
                properties = index.get("property_keys", [])
                for prop in properties:
                    existing_index_properties.add(prop)
        
        # Filter out properties that already have indexes
        new_index_properties = [prop for prop in property_names if prop not in existing_index_properties]
        
        # Get node labels
        try:
            labels_query = "CALL db.labels()"
            labels_result = self.db_manager.execute_query(labels_query)
            labels = [record.get("label") for record in labels_result]
        except Exception:
            # Fall back to a different approach
            try:
                labels_query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
                labels_result = self.db_manager.execute_query(labels_query)
                labels = []
                for record in labels_result:
                    for label_list in record.get("labels", []):
                        labels.extend(label_list)
                labels = list(set(labels))
            except Exception:
                labels = []
        
        # Create indexes for properties
        created_indexes = []
        for prop in new_index_properties:
            for label in labels:
                if self.index_manager.create_index(label, prop):
                    created_indexes.append((label, prop))
        
        # Re-explain the query after creating indexes
        new_explain_results = self.query_profiler.explain_query(query, parameters)
        
        return {
            "query": query,
            "parameters": parameters,
            "original_plan": explain_results.get("plan", {}),
            "original_analysis": explain_results.get("analysis", {}),
            "created_indexes": created_indexes,
            "new_plan": new_explain_results.get("plan", {}),
            "new_analysis": new_explain_results.get("analysis", {})
        }
    
    def _extract_properties_from_query(self, query: str) -> List[str]:
        """
        Extract property names from WHERE clauses in a query.
        
        Args:
            query: The query to analyze
            
        Returns:
            List of property names
        """
        property_names = []
        
        # Regular expressions to find property access patterns in queries
        property_patterns = [
            r'WHERE\s+\w+\.(\w+)\s*=',  # WHERE n.property =
            r'WHERE\s+\w+\.(\w+)\s+IN',  # WHERE n.property IN
            r'WHERE\s+\w+\.(\w+)\s*<',   # WHERE n.property <
            r'WHERE\s+\w+\.(\w+)\s*>',   # WHERE n.property >
            r'ORDER BY\s+\w+\.(\w+)',    # ORDER BY n.property
            r'MATCH\s+\([\w:]*\s*\{(\w+):',  # MATCH (n {property:
        ]
        
        # Find properties in the query
        for pattern in property_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            property_names.extend(matches)
        
        # Remove duplicates
        return list(set(property_names))


# Create a singleton instance
query_optimizer = QueryOptimizer()


def optimize_all_queries(auto_create_indexes: bool = False) -> Dict[str, Any]:
    """
    Analyze and optimize all queries by implementing recommended indexing strategies.
    
    Args:
        auto_create_indexes: If True, automatically creates recommended indexes.
        
    Returns:
        Dictionary containing optimization results
    """
    return query_optimizer.optimize_queries(auto_create_indexes)


def optimize_query(query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optimize a specific query by analyzing its execution plan and creating appropriate indexes.
    
    Args:
        query: The query to optimize
        parameters: Optional parameters for the query
        
    Returns:
        Dictionary containing optimization results
    """
    return query_optimizer.optimize_specific_query(query, parameters)


def get_optimization_report() -> Dict[str, Any]:
    """
    Generate a comprehensive optimization report.
    
    Returns:
        Dictionary containing the optimization report
    """
    return query_optimizer.generate_optimization_report()