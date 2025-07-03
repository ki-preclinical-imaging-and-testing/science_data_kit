"""
Client-side Cache for Science Data Kit API

This module provides caching functionality for the Science Data Kit API client,
allowing responses to be cached and reused to improve performance.
"""

import json
import hashlib
import time
from typing import Any, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class CacheEntry:
    """A cache entry with expiration."""
    
    def __init__(self, data: Any, expires_at: Optional[float] = None):
        """
        Initialize a cache entry.
        
        Args:
            data: The data to cache.
            expires_at: The timestamp when the entry expires, or None for no expiration.
        """
        self.data = data
        self.expires_at = expires_at
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """
        Check if the cache entry is expired.
        
        Returns:
            True if the entry is expired, False otherwise.
        """
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class APICache:
    """Cache for API responses."""
    
    def __init__(self, max_size: int = 100, default_ttl: Optional[int] = 300):
        """
        Initialize the API cache.
        
        Args:
            max_size: The maximum number of entries in the cache.
            default_ttl: The default time-to-live for cache entries in seconds,
                         or None for no expiration.
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _generate_key(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key from request parameters.
        
        Args:
            method: The HTTP method.
            path: The request path.
            params: The query parameters.
            data: The request body.
            
        Returns:
            A string key for the cache.
        """
        # Create a dictionary with all request parameters
        key_dict = {
            "method": method,
            "path": path,
            "params": params or {},
            "data": data or {}
        }
        
        # Convert to a stable string representation
        key_str = json.dumps(key_dict, sort_keys=True)
        
        # Hash the string to get a fixed-length key
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
        """
        Get a value from the cache.
        
        Args:
            method: The HTTP method.
            path: The request path.
            params: The query parameters.
            data: The request body.
            
        Returns:
            A tuple (hit, value) where hit is True if the value was found in the cache,
            and value is the cached value (or None if not found).
        """
        key = self._generate_key(method, path, params, data)
        
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    self.logger.debug(f"Cache entry expired for {method} {path}")
                    del self.cache[key]
                    return False, None
                
                self.logger.debug(f"Cache hit for {method} {path}")
                return True, entry.data
        
        self.logger.debug(f"Cache miss for {method} {path}")
        return False, None
    
    def set(self, method: str, path: str, value: Any, ttl: Optional[int] = None,
            params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            method: The HTTP method.
            path: The request path.
            value: The value to cache.
            ttl: The time-to-live in seconds, or None to use the default.
            params: The query parameters.
            data: The request body.
        """
        key = self._generate_key(method, path, params, data)
        
        # Calculate expiration time
        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl
        elif self.default_ttl is not None:
            expires_at = time.time() + self.default_ttl
        
        with self.lock:
            # If cache is full, remove the oldest entry
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
                del self.cache[oldest_key]
                self.logger.debug(f"Removed oldest cache entry for {oldest_key}")
            
            # Add the new entry
            self.cache[key] = CacheEntry(value, expires_at)
            self.logger.debug(f"Cached response for {method} {path}")
    
    def invalidate(self, method: Optional[str] = None, path: Optional[str] = None) -> int:
        """
        Invalidate cache entries matching the given criteria.
        
        Args:
            method: The HTTP method to match, or None to match any method.
            path: The request path to match, or None to match any path.
            
        Returns:
            The number of entries invalidated.
        """
        count = 0
        
        with self.lock:
            keys_to_remove = []
            
            for key in self.cache:
                # If no criteria are provided, invalidate all entries
                if method is None and path is None:
                    keys_to_remove.append(key)
                    continue
                
                # Otherwise, check if the entry matches the criteria
                entry_dict = json.loads(key)
                if (method is None or entry_dict["method"] == method) and \
                   (path is None or entry_dict["path"] == path):
                    keys_to_remove.append(key)
            
            # Remove the matching entries
            for key in keys_to_remove:
                del self.cache[key]
                count += 1
        
        self.logger.debug(f"Invalidated {count} cache entries")
        return count
    
    def clear(self) -> int:
        """
        Clear the entire cache.
        
        Returns:
            The number of entries cleared.
        """
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.logger.debug(f"Cleared {count} cache entries")
            return count
    
    def cleanup(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            The number of entries removed.
        """
        count = 0
        
        with self.lock:
            keys_to_remove = []
            
            for key, entry in self.cache.items():
                if entry.is_expired():
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
                count += 1
        
        self.logger.debug(f"Removed {count} expired cache entries")
        return count


class CacheableEndpoint:
    """Decorator for marking API endpoints as cacheable."""
    
    def __init__(self, ttl: Optional[int] = None, methods: Optional[list] = None):
        """
        Initialize the cacheable endpoint decorator.
        
        Args:
            ttl: The time-to-live for cache entries in seconds, or None to use the default.
            methods: The HTTP methods to cache, or None to cache all methods.
        """
        self.ttl = ttl
        self.methods = methods or ["GET"]
    
    def __call__(self, func):
        """
        Decorate a function to make it cacheable.
        
        Args:
            func: The function to decorate.
            
        Returns:
            The decorated function.
        """
        func._cacheable = True
        func._cache_ttl = self.ttl
        func._cache_methods = self.methods
        return func