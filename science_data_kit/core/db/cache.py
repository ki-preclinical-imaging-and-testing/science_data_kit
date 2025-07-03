"""
Query Cache for Science Data Kit

This module provides caching functionality for database queries to improve
performance for frequently executed queries.
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple, List, Callable
from functools import wraps


class QueryCache:
    """
    Cache for database queries.
    
    This class provides a simple in-memory cache for database queries,
    with support for time-to-live (TTL) expiration.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize the query cache.
        
        Args:
            max_size: Maximum number of entries in the cache
            default_ttl: Default time-to-live for cache entries in seconds
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
    
    def _generate_key(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                     connection_name: Optional[str] = None) -> str:
        """
        Generate a cache key for a query.
        
        Args:
            query: The query string
            parameters: Optional parameters for the query
            connection_name: Optional name of the connection
            
        Returns:
            A string key for the cache
        """
        # Create a dictionary with all components
        key_dict = {
            "query": query,
            "parameters": parameters or {},
            "connection_name": connection_name
        }
        
        # Convert to a stable JSON string
        key_json = json.dumps(key_dict, sort_keys=True)
        
        # Hash the JSON string
        return hashlib.md5(key_json.encode()).hexdigest()
    
    def get(self, query: str, parameters: Optional[Dict[str, Any]] = None,
           connection_name: Optional[str] = None) -> Tuple[bool, Any]:
        """
        Get a value from the cache.
        
        Args:
            query: The query string
            parameters: Optional parameters for the query
            connection_name: Optional name of the connection
            
        Returns:
            A tuple of (hit, value) where hit is True if the value was found in the cache
        """
        key = self._generate_key(query, parameters, connection_name)
        
        if key in self._cache:
            value, expiry = self._cache[key]
            
            # Check if the entry has expired
            if expiry > time.time():
                return True, value
            
            # Remove expired entry
            del self._cache[key]
        
        return False, None
    
    def set(self, query: str, parameters: Optional[Dict[str, Any]] = None,
           connection_name: Optional[str] = None, value: Any = None,
           ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            query: The query string
            parameters: Optional parameters for the query
            connection_name: Optional name of the connection
            value: The value to cache
            ttl: Time-to-live for the cache entry in seconds
        """
        # If the cache is full, remove the oldest entry
        if len(self._cache) >= self._max_size:
            # Simple strategy: just remove a random entry
            # A more sophisticated strategy would be to use LRU
            if self._cache:
                self._cache.pop(next(iter(self._cache)))
        
        key = self._generate_key(query, parameters, connection_name)
        expiry = time.time() + (ttl if ttl is not None else self._default_ttl)
        self._cache[key] = (value, expiry)
    
    def invalidate(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None,
                  connection_name: Optional[str] = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            query: Optional query string to invalidate
            parameters: Optional parameters for the query
            connection_name: Optional name of the connection
            
        Returns:
            Number of entries invalidated
        """
        if query is None and parameters is None and connection_name is None:
            # Invalidate all entries
            count = len(self._cache)
            self._cache.clear()
            return count
        
        # Invalidate specific entries
        key = self._generate_key(query, parameters, connection_name)
        if key in self._cache:
            del self._cache[key]
            return 1
        
        return 0
    
    def clear(self) -> int:
        """
        Clear the entire cache.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count
    
    def size(self) -> int:
        """
        Get the current size of the cache.
        
        Returns:
            Number of entries in the cache
        """
        return len(self._cache)
    
    def cleanup(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        keys_to_remove = [key for key, (_, expiry) in self._cache.items() if expiry <= now]
        
        for key in keys_to_remove:
            del self._cache[key]
        
        return len(keys_to_remove)


# Create a singleton instance of the query cache
query_cache = QueryCache()


def cached_query(ttl: Optional[int] = None):
    """
    Decorator for caching query results.
    
    Args:
        ttl: Time-to-live for the cache entry in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query, parameters, and connection_name from args/kwargs
            # This assumes the function signature matches execute_query
            if len(args) > 1:
                query = args[1]  # First arg is self, second is query
                parameters = args[2] if len(args) > 2 else kwargs.get('parameters')
                connection_name = args[3] if len(args) > 3 else kwargs.get('connection_name')
            else:
                query = kwargs.get('query')
                parameters = kwargs.get('parameters')
                connection_name = kwargs.get('connection_name')
            
            # Check if caching is enabled for this query
            enable_cache = kwargs.pop('enable_cache', True)
            if not enable_cache:
                return func(*args, **kwargs)
            
            # Check if the query is cacheable (read-only)
            # Simple heuristic: if the query starts with SELECT, MATCH, or RETURN, it's read-only
            query_upper = query.strip().upper()
            is_read_only = (
                query_upper.startswith('SELECT') or 
                query_upper.startswith('MATCH') or 
                query_upper.startswith('RETURN')
            )
            
            if not is_read_only:
                return func(*args, **kwargs)
            
            # Try to get from cache
            hit, value = query_cache.get(query, parameters, connection_name)
            if hit:
                return value
            
            # Execute the query
            result = func(*args, **kwargs)
            
            # Cache the result
            query_cache.set(query, parameters, connection_name, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator