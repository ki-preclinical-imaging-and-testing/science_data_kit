"""
Performance Optimization Recommendations for Science Data Kit

This module provides functions for generating optimization recommendations based on profiling data.
"""

import re
import sys
from typing import Dict, List, Any, Optional, Tuple, Set

from .profiler import profiler
from .memory_profiler import memory_profiler
from science_data_kit.core.db.metrics import query_metrics


def get_optimization_recommendations() -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate optimization recommendations based on profiling data.

    Returns:
        Dictionary of recommendations by category
    """
    recommendations = {
        "database": get_database_recommendations(),
        "caching": get_caching_recommendations(),
        "code": get_code_recommendations(),
        "memory": get_memory_recommendations(),
    }

    return recommendations


def get_database_recommendations() -> List[Dict[str, Any]]:
    """
    Generate database optimization recommendations.

    Returns:
        List of database optimization recommendations
    """
    recommendations = []

    # Get query metrics
    metrics = query_metrics.get_metrics()
    slow_queries = query_metrics.get_slow_queries()

    # Check for slow queries
    if slow_queries:
        # Analyze slow queries for potential indexing opportunities
        index_recommendations = _analyze_queries_for_indexes(slow_queries)
        for prop, count in index_recommendations.items():
            if count >= 3:  # Only recommend if property appears in multiple slow queries
                recommendations.append({
                    "type": "index",
                    "property": prop,
                    "description": f"Create an index on property '{prop}' which appears in {count} slow queries",
                    "priority": "high" if count >= 5 else "medium",
                    "implementation": f"CREATE INDEX ON :<Label>('{prop}')"
                })

    # Check cache hit ratio
    cache_hit_ratio = metrics.get("cache_hit_ratio", 0)
    if cache_hit_ratio < 0.5:  # Less than 50% cache hits
        recommendations.append({
            "type": "caching",
            "description": f"Low cache hit ratio ({cache_hit_ratio:.2%}). Consider reviewing cache configuration.",
            "priority": "medium",
            "implementation": "Review cache TTL settings and consider increasing cache size."
        })

    # Check query types distribution
    query_types = metrics.get("query_types", {})
    read_queries = sum(query_types.get(t, 0) for t in ["MATCH_READ", "RETURN"])
    write_queries = sum(query_types.get(t, 0) for t in ["CREATE", "MERGE", "MATCH_CREATE", "MATCH_UPDATE", "MATCH_DELETE", "DELETE"])

    if write_queries > 0 and read_queries / max(1, write_queries) < 2:
        # More writes than expected for a typical application
        recommendations.append({
            "type": "query_pattern",
            "description": "High write-to-read ratio. Consider batch operations for writes.",
            "priority": "medium",
            "implementation": "Use UNWIND for batch operations instead of individual writes."
        })

    return recommendations


def _analyze_queries_for_indexes(slow_queries: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze slow queries to identify properties that might benefit from indexing.

    Args:
        slow_queries: List of slow query details

    Returns:
        Dictionary mapping property names to frequency counts
    """
    property_counts = {}

    # Regular expressions to find property access patterns in queries
    property_patterns = [
        r'WHERE\s+\w+\.(\w+)\s*=',  # WHERE n.property =
        r'WHERE\s+\w+\.(\w+)\s+IN',  # WHERE n.property IN
        r'WHERE\s+\w+\.(\w+)\s*<',   # WHERE n.property <
        r'WHERE\s+\w+\.(\w+)\s*>',   # WHERE n.property >
        r'ORDER BY\s+\w+\.(\w+)',    # ORDER BY n.property
        r'MATCH\s+\([\w:]*\s*\{(\w+):',  # MATCH (n {property:
    ]

    for query_info in slow_queries:
        query = query_info.get("query", "")

        # Skip if query is empty
        if not query:
            continue

        # Find properties in the query
        for pattern in property_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for prop in matches:
                property_counts[prop] = property_counts.get(prop, 0) + 1

    return property_counts


def get_caching_recommendations() -> List[Dict[str, Any]]:
    """
    Generate caching optimization recommendations.

    Returns:
        List of caching optimization recommendations
    """
    recommendations = []

    # Get profiling data
    profile_summary = profiler.get_summary()
    slow_operations = profiler.get_slow_operations()

    # Check for functions that might benefit from caching
    function_profiles = profile_summary.get("function_profiles", {})
    for func_name, stats in function_profiles.items():
        # If a function is called frequently and has consistent execution time, it might benefit from caching
        if stats.get("call_count", 0) >= 10 and stats.get("max_time", 0) / max(0.001, stats.get("min_time", 0.001)) < 3:
            # Check if it's a database query function
            if "execute_query" in func_name or "query_to_" in func_name:
                recommendations.append({
                    "type": "function_caching",
                    "function": func_name,
                    "description": f"Function '{func_name}' is called frequently ({stats.get('call_count')}) with consistent execution time. Consider caching results.",
                    "priority": "high" if stats.get("avg_time", 0) > 0.1 else "medium",
                    "implementation": "Apply @cached_query() decorator or implement result caching."
                })

    return recommendations


def get_code_recommendations() -> List[Dict[str, Any]]:
    """
    Generate code optimization recommendations.

    Returns:
        List of code optimization recommendations
    """
    recommendations = []

    # Get profiling data
    profile_summary = profiler.get_summary()
    slow_operations = profiler.get_slow_operations()

    # Check for slow functions
    function_profiles = profile_summary.get("function_profiles", {})
    for func_name, stats in function_profiles.items():
        if stats.get("avg_time", 0) > 1.0:  # Functions taking more than 1 second on average
            recommendations.append({
                "type": "slow_function",
                "function": func_name,
                "description": f"Function '{func_name}' is slow (avg: {stats.get('avg_time', 0):.2f}s, max: {stats.get('max_time', 0):.2f}s)",
                "priority": "high" if stats.get("avg_time", 0) > 2.0 else "medium",
                "implementation": "Profile the function in detail using profiler.detailed_profile() to identify bottlenecks."
            })

    # Check for slow code blocks
    block_profiles = profile_summary.get("block_profiles", {})
    for block_name, stats in block_profiles.items():
        if stats.get("avg_time", 0) > 1.0:  # Blocks taking more than 1 second on average
            recommendations.append({
                "type": "slow_code_block",
                "block": block_name,
                "description": f"Code block '{block_name}' is slow (avg: {stats.get('avg_time', 0):.2f}s, max: {stats.get('max_time', 0):.2f}s)",
                "priority": "high" if stats.get("avg_time", 0) > 2.0 else "medium",
                "implementation": "Review the code block for optimization opportunities."
            })

    return recommendations


def get_memory_recommendations() -> List[Dict[str, Any]]:
    """
    Generate memory optimization recommendations.

    Returns:
        List of memory optimization recommendations
    """
    recommendations = []

    # Get profiling data
    profile_summary = profiler.get_summary()

    # Check if memory profiler is enabled
    if memory_profiler.is_enabled():
        # Get memory profiling data
        memory_summary = memory_profiler.get_summary()
        memory_leaks = memory_profiler.get_memory_leaks()

        # Check for functions with high memory usage
        function_memory_stats = memory_summary.get("function_memory_stats", {})
        for func_name, stats in function_memory_stats.items():
            # If a function uses a lot of memory (more than 10MB)
            if stats.get("avg_memory_diff", 0) > 10 * 1024 * 1024:
                recommendations.append({
                    "type": "high_memory_function",
                    "function": func_name,
                    "description": f"Function '{func_name}' uses a lot of memory (avg: {stats.get('avg_memory_diff', 0) / (1024 * 1024):.2f}MB, max: {stats.get('max_memory_diff', 0) / (1024 * 1024):.2f}MB)",
                    "priority": "high" if stats.get("avg_memory_diff", 0) > 50 * 1024 * 1024 else "medium",
                    "implementation": "Consider optimizing memory usage by using generators, reducing intermediate data structures, or processing data in chunks."
                })

        # Check for code blocks with high memory usage
        block_memory_stats = memory_summary.get("block_memory_stats", {})
        for block_name, stats in block_memory_stats.items():
            # If a code block uses a lot of memory (more than 10MB)
            if stats.get("avg_memory_diff", 0) > 10 * 1024 * 1024:
                recommendations.append({
                    "type": "high_memory_block",
                    "block": block_name,
                    "description": f"Code block '{block_name}' uses a lot of memory (avg: {stats.get('avg_memory_diff', 0) / (1024 * 1024):.2f}MB, max: {stats.get('max_memory_diff', 0) / (1024 * 1024):.2f}MB)",
                    "priority": "high" if stats.get("avg_memory_diff", 0) > 50 * 1024 * 1024 else "medium",
                    "implementation": "Review the code block for memory optimization opportunities."
                })

        # Check for memory leaks
        if memory_leaks:
            for name, memory_increase, timestamp, details in memory_leaks[:5]:  # Top 5 memory leaks
                recommendations.append({
                    "type": "memory_leak",
                    "function_or_block": name,
                    "description": f"Potential memory leak in '{name}' (increase: {memory_increase / (1024 * 1024):.2f}MB)",
                    "priority": "high",
                    "implementation": "Check for unclosed resources, circular references, or large data structures that aren't being released."
                })

                # Add specific recommendations based on the details
                if details and "top_differences" in details:
                    for diff_desc, diff_size in details["top_differences"][:3]:  # Top 3 differences
                        if diff_size > 1024 * 1024:  # Only if difference is significant (>1MB)
                            recommendations.append({
                                "type": "memory_leak_detail",
                                "function_or_block": name,
                                "description": f"Memory leak detail: {diff_desc} ({diff_size / (1024 * 1024):.2f}MB)",
                                "priority": "medium",
                                "implementation": "Investigate this specific area for memory optimization."
                            })

    # Add general memory optimization recommendations
    recommendations.append({
        "type": "general",
        "description": "Consider using generators instead of lists for large data processing",
        "priority": "medium",
        "implementation": "Replace list comprehensions with generator expressions for large datasets."
    })

    recommendations.append({
        "type": "general",
        "description": "Use pagination for large query results",
        "priority": "medium",
        "implementation": "Use SKIP/LIMIT in queries or the fetch_nodes_paginated method for large result sets."
    })

    recommendations.append({
        "type": "general",
        "description": "Enable memory profiling for more detailed recommendations",
        "priority": "medium",
        "implementation": "Call memory_profiler.start() at the beginning of your application to enable memory profiling."
    })

    return recommendations


def get_database_indexing_strategy() -> Dict[str, Any]:
    """
    Generate a comprehensive database indexing strategy.

    Returns:
        Dictionary containing indexing strategy details
    """
    # Get query metrics
    metrics = query_metrics.get_metrics()
    slow_queries = query_metrics.get_slow_queries()

    # Analyze slow queries for potential indexing opportunities
    index_recommendations = _analyze_queries_for_indexes(slow_queries)

    # Prioritize index recommendations
    high_priority = []
    medium_priority = []
    low_priority = []

    for prop, count in index_recommendations.items():
        if count >= 5:
            high_priority.append((prop, count))
        elif count >= 3:
            medium_priority.append((prop, count))
        else:
            low_priority.append((prop, count))

    # Sort by count (descending)
    high_priority.sort(key=lambda x: x[1], reverse=True)
    medium_priority.sort(key=lambda x: x[1], reverse=True)
    low_priority.sort(key=lambda x: x[1], reverse=True)

    # Generate Cypher statements for creating indexes
    index_statements = []

    for prop, count in high_priority + medium_priority:
        index_statements.append(f"CREATE INDEX ON :<Label>('{prop}')")

    return {
        "high_priority_indexes": high_priority,
        "medium_priority_indexes": medium_priority,
        "low_priority_indexes": low_priority,
        "index_statements": index_statements,
        "recommendations": [
            "Create indexes for properties used in WHERE clauses",
            "Create indexes for properties used in ORDER BY clauses",
            "Consider creating composite indexes for frequently combined properties",
            "Monitor index usage with db.indexes() and EXPLAIN/PROFILE"
        ]
    }
