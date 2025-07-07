"""
Query Profiler for Science Data Kit

This module provides functionality for profiling Neo4j queries to identify
performance bottlenecks and optimization opportunities.
"""

import time
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from .metrics import query_metrics


class QueryProfiler:
    """
    Profiles Neo4j queries to identify performance bottlenecks and optimization opportunities.

    This class provides methods for:
    - Analyzing query patterns to identify slow queries
    - Providing recommendations for query optimization
    - Visualizing query performance data
    - Generating detailed profiling reports
    """

    def __init__(self, db_manager=None):
        """
        Initialize the query profiler.

        Args:
            db_manager: Optional Neo4jManager instance. If None, uses the singleton instance.
        """
        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Store the provided db_manager or set to None to be loaded lazily
        self._db_manager = db_manager

        # Get query metrics instance
        self.metrics = query_metrics

    def get_slow_queries(self, limit: int = 10, min_execution_time: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get a list of slow queries ordered by execution time.

        Args:
            limit: Maximum number of queries to return
            min_execution_time: Minimum execution time in seconds to consider a query as slow

        Returns:
            List of slow query details
        """
        # Get all slow queries from metrics
        slow_queries = self.metrics.get_slow_queries()

        # Filter by minimum execution time
        filtered_queries = [q for q in slow_queries if q["execution_time"] >= min_execution_time]

        # Sort by execution time (descending)
        sorted_queries = sorted(filtered_queries, key=lambda q: q["execution_time"], reverse=True)

        # Return limited number of queries
        return sorted_queries[:limit]

    def analyze_query_patterns(self) -> Dict[str, Any]:
        """
        Analyze query patterns to identify common performance issues.

        Returns:
            Dictionary containing analysis results
        """
        # Get query history
        query_history = self.metrics.get_query_history(limit=1000)

        # Initialize pattern counters
        patterns = {
            "cartesian_products": 0,
            "missing_indexes": 0,
            "unbound_variable_length": 0,
            "large_property_scans": 0,
            "complex_aggregations": 0
        }

        # Initialize query examples
        examples = {
            "cartesian_products": [],
            "missing_indexes": [],
            "unbound_variable_length": [],
            "large_property_scans": [],
            "complex_aggregations": []
        }

        # Analyze each query
        for query_info in query_history:
            query = query_info.get("query", "").upper()
            execution_time = query_info.get("execution_time", 0)

            # Check for cartesian products (multiple MATCH clauses without relationships between them)
            if "MATCH" in query and query.count("MATCH") > 1 and "WHERE" not in query:
                patterns["cartesian_products"] += 1
                if len(examples["cartesian_products"]) < 3:
                    examples["cartesian_products"].append(query_info)

            # Check for potential missing indexes (property lookups without USING INDEX hint)
            if "WHERE" in query and "=" in query and "USING INDEX" not in query:
                patterns["missing_indexes"] += 1
                if len(examples["missing_indexes"]) < 3:
                    examples["missing_indexes"].append(query_info)

            # Check for unbound variable length patterns
            if "-[*]-" in query or "-[*" in query:
                patterns["unbound_variable_length"] += 1
                if len(examples["unbound_variable_length"]) < 3:
                    examples["unbound_variable_length"].append(query_info)

            # Check for large property scans
            if "WHERE" in query and any(op in query for op in ["CONTAINS", "STARTS WITH", "ENDS WITH"]):
                patterns["large_property_scans"] += 1
                if len(examples["large_property_scans"]) < 3:
                    examples["large_property_scans"].append(query_info)

            # Check for complex aggregations
            if any(agg in query for agg in ["COUNT", "SUM", "AVG", "MIN", "MAX"]) and "GROUP BY" in query:
                patterns["complex_aggregations"] += 1
                if len(examples["complex_aggregations"]) < 3:
                    examples["complex_aggregations"].append(query_info)

        return {
            "patterns": patterns,
            "examples": examples
        }

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for query optimization based on analysis.

        Returns:
            List of recommendation dictionaries
        """
        # Analyze query patterns
        analysis = self.analyze_query_patterns()

        # Get slow queries
        slow_queries = self.get_slow_queries()

        # Initialize recommendations
        recommendations = []

        # Add recommendations based on patterns
        if analysis["patterns"]["cartesian_products"] > 0:
            recommendations.append({
                "type": "cartesian_products",
                "title": "Avoid Cartesian Products",
                "description": "Your queries contain potential cartesian products, which can cause performance issues with large datasets.",
                "suggestion": "Ensure that all MATCH clauses are connected through relationships or WHERE conditions.",
                "examples": analysis["examples"]["cartesian_products"],
                "impact": "high" if analysis["patterns"]["cartesian_products"] > 5 else "medium"
            })

        if analysis["patterns"]["missing_indexes"] > 0:
            recommendations.append({
                "type": "missing_indexes",
                "title": "Create Indexes for Property Lookups",
                "description": "Your queries contain property lookups that might benefit from indexes.",
                "suggestion": "Create indexes for frequently queried properties or use USING INDEX hint.",
                "examples": analysis["examples"]["missing_indexes"],
                "impact": "high" if analysis["patterns"]["missing_indexes"] > 10 else "medium"
            })

        if analysis["patterns"]["unbound_variable_length"] > 0:
            recommendations.append({
                "type": "unbound_variable_length",
                "title": "Bound Variable Length Patterns",
                "description": "Your queries contain unbound variable length patterns, which can lead to large traversals.",
                "suggestion": "Add upper bounds to variable length patterns, e.g., -[*1..5]- instead of -[*]-.",
                "examples": analysis["examples"]["unbound_variable_length"],
                "impact": "high"
            })

        if analysis["patterns"]["large_property_scans"] > 0:
            recommendations.append({
                "type": "large_property_scans",
                "title": "Optimize String Operations",
                "description": "Your queries use string operations that require scanning all properties.",
                "suggestion": "Consider using full-text indexes or refactoring queries to avoid string operations.",
                "examples": analysis["examples"]["large_property_scans"],
                "impact": "medium"
            })

        if analysis["patterns"]["complex_aggregations"] > 0:
            recommendations.append({
                "type": "complex_aggregations",
                "title": "Simplify Aggregations",
                "description": "Your queries contain complex aggregations that might be expensive.",
                "suggestion": "Consider breaking down complex aggregations into simpler queries or using APOC procedures.",
                "examples": analysis["examples"]["complex_aggregations"],
                "impact": "medium"
            })

        # Add recommendations for specific slow queries
        for query_info in slow_queries:
            query = query_info.get("query", "")
            execution_time = query_info.get("execution_time", 0)

            # Skip if already covered by pattern recommendations
            if any(query in [ex.get("query", "") for ex in r.get("examples", [])] for r in recommendations):
                continue

            # Add specific recommendation
            recommendations.append({
                "type": "slow_query",
                "title": f"Optimize Slow Query ({execution_time:.2f}s)",
                "description": f"This query is taking {execution_time:.2f} seconds to execute.",
                "suggestion": "Consider using PROFILE or EXPLAIN to analyze the query execution plan.",
                "examples": [query_info],
                "impact": "high" if execution_time > 2 else "medium"
            })

        return recommendations

    def visualize_query_performance(self, format: str = "png") -> str:
        """
        Generate a visualization of query performance.

        Args:
            format: Output format ("png" or "svg")

        Returns:
            Base64-encoded image data
        """
        # Get metrics
        metrics = self.metrics.get_metrics()

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Plot query types distribution
        query_types = metrics.get("query_types", {})
        if query_types:
            labels = list(query_types.keys())
            values = list(query_types.values())
            ax1.pie(values, labels=labels, autopct='%1.1f%%')
            ax1.set_title('Query Types Distribution')

        # Plot query execution times
        query_history = self.metrics.get_query_history(limit=100)
        if query_history:
            execution_times = [q.get("execution_time", 0) for q in query_history if not q.get("cache_hit", False)]
            timestamps = [q.get("timestamp", datetime.now()) for q in query_history if not q.get("cache_hit", False)]

            if execution_times and timestamps:
                ax2.plot(timestamps, execution_times, 'o-')
                ax2.set_title('Query Execution Times')
                ax2.set_ylabel('Time (seconds)')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True)

        # Adjust layout
        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format=format)
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode()
        plt.close()

        return image_data

    def generate_profiling_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive profiling report.

        Returns:
            Dictionary containing the profiling report
        """
        # Get metrics
        metrics = self.metrics.get_metrics()

        # Get slow queries
        slow_queries = self.get_slow_queries()

        # Get optimization recommendations
        recommendations = self.get_optimization_recommendations()

        # Generate visualization
        try:
            visualization = self.visualize_query_performance()
        except Exception as e:
            self.logger.error(f"Failed to generate visualization: {e}")
            visualization = None

        # Create report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_queries": metrics.get("total_queries", 0),
                "avg_execution_time": metrics.get("avg_execution_time", 0),
                "cache_hit_ratio": metrics.get("cache_hit_ratio", 0),
                "slow_queries_count": len(slow_queries)
            },
            "slow_queries": slow_queries,
            "recommendations": recommendations,
            "visualization": visualization
        }

        return report

    def explain_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain a query execution plan.

        Args:
            query: The query to explain
            parameters: Optional parameters for the query

        Returns:
            Dictionary containing the execution plan and analysis
        """
        try:
            # Get db_manager lazily to avoid circular imports
            db_manager = self._get_db_manager()

            # Add EXPLAIN if not already present
            if not query.strip().upper().startswith("EXPLAIN"):
                explain_query = f"EXPLAIN {query}"
            else:
                explain_query = query

            # Execute the explain query
            result = db_manager.execute_query(explain_query, parameters)

            if not result:
                return {"error": "No execution plan returned"}

            # Extract plan from result
            plan = result[0].get("plan", {})

            # Analyze the plan
            analysis = self._analyze_execution_plan(plan)

            return {
                "query": query,
                "parameters": parameters,
                "plan": plan,
                "analysis": analysis
            }

        except Exception as e:
            self.logger.error(f"Failed to explain query: {e}")
            return {"error": str(e)}

    def profile_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Profile a query execution.

        Args:
            query: The query to profile
            parameters: Optional parameters for the query

        Returns:
            Dictionary containing the execution profile and analysis
        """
        try:
            # Get db_manager lazily to avoid circular imports
            db_manager = self._get_db_manager()

            # Add PROFILE if not already present
            if not query.strip().upper().startswith("PROFILE"):
                profile_query = f"PROFILE {query}"
            else:
                profile_query = query

            # Execute the profile query
            result = db_manager.execute_query(profile_query, parameters)

            if not result:
                return {"error": "No execution profile returned"}

            # Extract profile from result
            profile = result[0].get("profile", {})

            # Analyze the profile
            analysis = self._analyze_execution_plan(profile)

            return {
                "query": query,
                "parameters": parameters,
                "profile": profile,
                "analysis": analysis
            }

        except Exception as e:
            self.logger.error(f"Failed to profile query: {e}")
            return {"error": str(e)}

    def _analyze_execution_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a query execution plan to identify optimization opportunities.

        Args:
            plan: The execution plan

        Returns:
            Dictionary containing analysis results
        """
        # Initialize analysis
        analysis = {
            "issues": [],
            "suggestions": []
        }

        # Check for cartesian products
        if self._has_cartesian_product(plan):
            analysis["issues"].append("Cartesian product detected")
            analysis["suggestions"].append("Ensure all patterns are connected or use WHERE clauses to relate them")

        # Check for full scans
        if self._has_full_scan(plan):
            analysis["issues"].append("Full scan detected")
            analysis["suggestions"].append("Consider adding indexes for the properties used in WHERE clauses")

        # Check for expensive operations
        expensive_ops = self._find_expensive_operations(plan)
        if expensive_ops:
            for op in expensive_ops:
                analysis["issues"].append(f"Expensive operation: {op}")
            analysis["suggestions"].append("Consider restructuring the query to avoid expensive operations")

        return analysis

    def _has_cartesian_product(self, plan: Dict[str, Any]) -> bool:
        """
        Check if an execution plan contains a cartesian product.

        Args:
            plan: The execution plan

        Returns:
            True if a cartesian product is detected, False otherwise
        """
        # Check operator name
        operator = plan.get("operatorType", "")
        if "CartesianProduct" in operator:
            return True

        # Recursively check children
        children = plan.get("children", [])
        for child in children:
            if self._has_cartesian_product(child):
                return True

        return False

    def _has_full_scan(self, plan: Dict[str, Any]) -> bool:
        """
        Check if an execution plan contains a full scan.

        Args:
            plan: The execution plan

        Returns:
            True if a full scan is detected, False otherwise
        """
        # Check operator name and identifiers
        operator = plan.get("operatorType", "")
        identifiers = plan.get("identifiers", [])

        if "Scan" in operator and not any("Index" in op for op in [operator]):
            return True

        # Recursively check children
        children = plan.get("children", [])
        for child in children:
            if self._has_full_scan(child):
                return True

        return False

    def _find_expensive_operations(self, plan: Dict[str, Any]) -> List[str]:
        """
        Find expensive operations in an execution plan.

        Args:
            plan: The execution plan

        Returns:
            List of expensive operations
        """
        expensive_operations = []

        # Check operator name
        operator = plan.get("operatorType", "")
        if any(op in operator for op in ["Eager", "Sort", "Distinct", "EagerAggregation"]):
            expensive_operations.append(operator)

        # Recursively check children
        children = plan.get("children", [])
        for child in children:
            expensive_operations.extend(self._find_expensive_operations(child))

        return expensive_operations

    def _get_db_manager(self):
        """
        Get the database manager instance lazily to avoid circular imports.

        Returns:
            The database manager instance
        """
        if self._db_manager is None:
            # Import here to avoid circular imports
            from .db_manager import db_manager as default_manager
            self._db_manager = default_manager
        return self._db_manager


# Create a singleton instance
# We'll initialize it without a db_manager to avoid circular imports
query_profiler = QueryProfiler()
