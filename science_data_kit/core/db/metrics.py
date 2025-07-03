"""
Query Metrics for Science Data Kit

This module provides functionality for tracking and analyzing database query performance.
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

class QueryMetrics:
    """
    Tracks performance metrics for database queries.
    
    This class collects and analyzes metrics about query execution times,
    cache hits/misses, and other performance data to help identify
    slow queries and optimization opportunities.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implement singleton pattern with thread safety."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(QueryMetrics, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the query metrics tracker."""
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return
            
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self._metrics = {
            "total_queries": 0,
            "total_execution_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "query_types": defaultdict(int),
            "slow_queries": [],  # List of (query, params, time, timestamp) for slow queries
            "query_history": [],  # List of recent queries for analysis
        }
        
        # Configuration
        self._max_history_size = 1000
        self._slow_query_threshold = 1.0  # seconds
        self._max_slow_queries = 100
        
        # Thread safety
        self._metrics_lock = threading.Lock()
        
        self._initialized = True
    
    def record_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                    execution_time: float = 0.0, cache_hit: bool = False,
                    connection_name: Optional[str] = None) -> None:
        """
        Record metrics for a query execution.
        
        Args:
            query: The query string
            parameters: Optional parameters for the query
            execution_time: Time taken to execute the query in seconds
            cache_hit: Whether the query result was served from cache
            connection_name: Optional name of the connection used
        """
        with self._metrics_lock:
            # Update basic metrics
            self._metrics["total_queries"] += 1
            
            if cache_hit:
                self._metrics["cache_hits"] += 1
            else:
                self._metrics["cache_misses"] += 1
                self._metrics["total_execution_time"] += execution_time
            
            # Determine query type (simple heuristic)
            query_type = self._get_query_type(query)
            self._metrics["query_types"][query_type] += 1
            
            # Record timestamp
            timestamp = datetime.now()
            
            # Add to history (limited size)
            history_entry = {
                "query": query,
                "parameters": parameters,
                "execution_time": execution_time,
                "cache_hit": cache_hit,
                "connection_name": connection_name,
                "timestamp": timestamp,
                "query_type": query_type
            }
            
            self._metrics["query_history"].append(history_entry)
            if len(self._metrics["query_history"]) > self._max_history_size:
                self._metrics["query_history"].pop(0)
            
            # Track slow queries
            if not cache_hit and execution_time > self._slow_query_threshold:
                slow_query = {
                    "query": query,
                    "parameters": parameters,
                    "execution_time": execution_time,
                    "timestamp": timestamp,
                    "connection_name": connection_name
                }
                self._metrics["slow_queries"].append(slow_query)
                
                # Log slow query
                self.logger.warning(
                    f"Slow query detected ({execution_time:.2f}s): {query[:100]}..."
                )
                
                # Limit the number of slow queries stored
                if len(self._metrics["slow_queries"]) > self._max_slow_queries:
                    self._metrics["slow_queries"].pop(0)
    
    def _get_query_type(self, query: str) -> str:
        """
        Determine the type of a query.
        
        Args:
            query: The query string
            
        Returns:
            A string representing the query type
        """
        query_upper = query.strip().upper()
        
        if query_upper.startswith("MATCH") and "CREATE" in query_upper:
            return "MATCH_CREATE"
        elif query_upper.startswith("MATCH") and "DELETE" in query_upper:
            return "MATCH_DELETE"
        elif query_upper.startswith("MATCH") and "SET" in query_upper:
            return "MATCH_UPDATE"
        elif query_upper.startswith("MATCH") and "RETURN" in query_upper:
            return "MATCH_READ"
        elif query_upper.startswith("CREATE"):
            return "CREATE"
        elif query_upper.startswith("MERGE"):
            return "MERGE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        elif query_upper.startswith("RETURN"):
            return "RETURN"
        else:
            return "OTHER"
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get a copy of the current metrics.
        
        Returns:
            Dictionary containing the current metrics
        """
        with self._metrics_lock:
            # Create a copy to avoid thread safety issues
            metrics_copy = {
                "total_queries": self._metrics["total_queries"],
                "total_execution_time": self._metrics["total_execution_time"],
                "cache_hits": self._metrics["cache_hits"],
                "cache_misses": self._metrics["cache_misses"],
                "query_types": dict(self._metrics["query_types"]),
                "slow_queries": list(self._metrics["slow_queries"]),
                "avg_execution_time": (
                    self._metrics["total_execution_time"] / max(1, self._metrics["cache_misses"])
                ),
                "cache_hit_ratio": (
                    self._metrics["cache_hits"] / max(1, self._metrics["total_queries"])
                ),
            }
            return metrics_copy
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """
        Get a list of slow queries.
        
        Returns:
            List of slow query details
        """
        with self._metrics_lock:
            return list(self._metrics["slow_queries"])
    
    def get_query_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent query history.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of recent query details
        """
        with self._metrics_lock:
            return list(self._metrics["query_history"][-limit:])
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self._metrics_lock:
            self._metrics = {
                "total_queries": 0,
                "total_execution_time": 0.0,
                "cache_hits": 0,
                "cache_misses": 0,
                "query_types": defaultdict(int),
                "slow_queries": [],
                "query_history": [],
            }
    
    def set_slow_query_threshold(self, threshold: float) -> None:
        """
        Set the threshold for identifying slow queries.
        
        Args:
            threshold: Time threshold in seconds
        """
        with self._metrics_lock:
            self._slow_query_threshold = threshold
    
    def get_slow_query_threshold(self) -> float:
        """
        Get the current slow query threshold.
        
        Returns:
            Current threshold in seconds
        """
        return self._slow_query_threshold


# Create a singleton instance
query_metrics = QueryMetrics()