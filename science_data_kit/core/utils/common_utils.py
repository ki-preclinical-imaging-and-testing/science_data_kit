"""
Common Utility Functions for Science Data Kit

This module provides shared utility functions for common operations across the Science Data Kit codebase.
These utilities help reduce code duplication and standardize common patterns.

The module includes utilities for:
1. String manipulation and validation
2. File and path operations
3. Data structure operations
4. Date and time operations
5. Validation and error handling
6. Configuration management
7. Logging helpers
"""

import os
import re
import json
import yaml
import hashlib
import logging
import datetime
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, TypeVar, Generic, Callable, Iterable

# Type variables for generic functions
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Set up logging
logger = logging.getLogger(__name__)


# String manipulation and validation functions

def is_valid_identifier(identifier: str) -> bool:
    """
    Check if a string is a valid Python identifier.

    Args:
        identifier: The string to check.

    Returns:
        True if the string is a valid Python identifier, False otherwise.
    """
    return identifier.isidentifier()


def camel_to_snake(name: str) -> str:
    """
    Convert a camelCase string to snake_case.

    Args:
        name: The camelCase string to convert.

    Returns:
        The string in snake_case.
    """
    # Insert underscore before uppercase letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        name: The snake_case string to convert.

    Returns:
        The string in camelCase.
    """
    # Split by underscore and capitalize each word except the first
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length, adding a suffix if truncated.

    Args:
        text: The string to truncate.
        max_length: The maximum length of the string.
        suffix: The suffix to add if the string is truncated.

    Returns:
        The truncated string.
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def normalize_string(text: str) -> str:
    """
    Normalize a string by removing extra whitespace and converting to lowercase.

    Args:
        text: The string to normalize.

    Returns:
        The normalized string.
    """
    return ' '.join(text.strip().lower().split())


def generate_slug(text: str) -> str:
    """
    Generate a URL-friendly slug from a string.

    Args:
        text: The string to convert to a slug.

    Returns:
        The slug.
    """
    # Convert to lowercase, replace spaces with hyphens, and remove non-alphanumeric characters
    return re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))


# File and path operations

def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: The path to the directory.

    Returns:
        The Path object for the directory.
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The file extension (without the dot).
    """
    return Path(file_path).suffix.lstrip('.')


def is_file_newer_than(file_path: Union[str, Path], reference_time: Union[float, datetime.datetime]) -> bool:
    """
    Check if a file is newer than a reference time.

    Args:
        file_path: The path to the file.
        reference_time: The reference time (timestamp or datetime).

    Returns:
        True if the file is newer than the reference time, False otherwise.
    """
    if not Path(file_path).exists():
        return False

    file_mtime = Path(file_path).stat().st_mtime

    if isinstance(reference_time, datetime.datetime):
        reference_timestamp = reference_time.timestamp()
    else:
        reference_timestamp = reference_time

    return file_mtime > reference_timestamp


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256', block_size: int = 65536) -> str:
    """
    Calculate the hash of a file.

    Args:
        file_path: The path to the file.
        algorithm: The hash algorithm to use ('md5', 'sha1', 'sha256', etc.).
        block_size: The block size to use when reading the file.

    Returns:
        The hash of the file as a hexadecimal string.
    """
    hash_obj = getattr(hashlib, algorithm)()

    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hash_obj.update(block)

    return hash_obj.hexdigest()


def create_temp_file(content: Union[str, bytes], suffix: Optional[str] = None) -> str:
    """
    Create a temporary file with the given content.

    Args:
        content: The content to write to the file.
        suffix: Optional suffix for the temporary file.

    Returns:
        The path to the temporary file.
    """
    mode = 'wb' if isinstance(content, bytes) else 'w'

    with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as temp:
        temp.write(content)
        return temp.name


# Data structure operations

def deep_merge(dict1: Dict[K, Any], dict2: Dict[K, Any]) -> Dict[K, Any]:
    """
    Deep merge two dictionaries.

    Args:
        dict1: The first dictionary.
        dict2: The second dictionary.

    Returns:
        A new dictionary with the merged contents.
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        d: The dictionary to flatten.
        parent_key: The parent key for nested dictionaries.
        separator: The separator to use between keys.

    Returns:
        A flattened dictionary.
    """
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))

    return dict(items)


def group_by(items: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
    """
    Group a list of items by a key function.

    Args:
        items: The list of items to group.
        key_func: A function that returns the key for each item.

    Returns:
        A dictionary mapping keys to lists of items.
    """
    result: Dict[K, List[T]] = {}

    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)

    return result


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of a specified size.

    Args:
        items: The list to split.
        chunk_size: The size of each chunk.

    Returns:
        A list of chunks.
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def find_duplicates(items: List[T]) -> Set[T]:
    """
    Find duplicate items in a list.

    Args:
        items: The list to check for duplicates.

    Returns:
        A set of duplicate items.
    """
    seen = set()
    duplicates = set()

    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates


# Date and time operations

def parse_iso_datetime(datetime_str: str) -> datetime.datetime:
    """
    Parse an ISO 8601 datetime string.

    Args:
        datetime_str: The ISO 8601 datetime string.

    Returns:
        A datetime object.
    """
    return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))


def format_iso_datetime(dt: datetime.datetime) -> str:
    """
    Format a datetime object as an ISO 8601 string.

    Args:
        dt: The datetime object.

    Returns:
        An ISO 8601 datetime string.
    """
    return dt.isoformat()


def get_current_timestamp() -> float:
    """
    Get the current timestamp.

    Returns:
        The current timestamp.
    """
    return datetime.datetime.now().timestamp()


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as a human-readable string.

    Args:
        seconds: The duration in seconds.

    Returns:
        A human-readable duration string.
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"

    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)} minutes, {int(seconds)} seconds"

    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{int(hours)} hours, {int(minutes)} minutes"

    days, hours = divmod(hours, 24)
    return f"{int(days)} days, {int(hours)} hours"


# Validation and error handling

def validate_required_keys(data: Dict[str, Any], required_keys: List[str]) -> List[str]:
    """
    Validate that a dictionary contains all required keys.

    Args:
        data: The dictionary to validate.
        required_keys: The list of required keys.

    Returns:
        A list of missing keys, or an empty list if all required keys are present.
    """
    return [key for key in required_keys if key not in data]


def validate_type(value: Any, expected_type: Union[type, Tuple[type, ...]], name: str = 'value') -> None:
    """
    Validate that a value is of the expected type.

    Args:
        value: The value to validate.
        expected_type: The expected type or tuple of types.
        name: The name of the value for error messages.

    Raises:
        TypeError: If the value is not of the expected type.
    """
    if not isinstance(value, expected_type):
        expected_type_name = getattr(expected_type, '__name__', str(expected_type))
        raise TypeError(f"{name} must be of type {expected_type_name}, got {type(value).__name__}")


def validate_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                  max_value: Optional[Union[int, float]] = None, name: str = 'value') -> None:
    """
    Validate that a numeric value is within a specified range.

    Args:
        value: The value to validate.
        min_value: The minimum allowed value, or None for no minimum.
        max_value: The maximum allowed value, or None for no maximum.
        name: The name of the value for error messages.

    Raises:
        ValueError: If the value is outside the specified range.
    """
    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be at least {min_value}, got {value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be at most {max_value}, got {value}")


def safe_execute(func: Callable[..., T], *args, default: Optional[T] = None, 
                 error_handler: Optional[Callable[[Exception], None]] = None, **kwargs) -> Optional[T]:
    """
    Safely execute a function, catching any exceptions.

    Args:
        func: The function to execute.
        *args: Positional arguments to pass to the function.
        default: The default value to return if an exception occurs.
        error_handler: Optional function to handle exceptions.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function, or the default value if an exception occurs.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            error_handler(e)
        return default


# Configuration management

def load_config_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load a configuration file (JSON or YAML).

    Args:
        file_path: The path to the configuration file.

    Returns:
        The configuration as a dictionary.

    Raises:
        ValueError: If the file format is not supported.
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    with open(file_path, 'r') as f:
        if extension in ('.json', '.jsn'):
            return json.load(f)
        elif extension in ('.yaml', '.yml'):
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {extension}")


def save_config_file(config: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save a configuration dictionary to a file (JSON or YAML).

    Args:
        config: The configuration dictionary.
        file_path: The path to save the configuration file.

    Raises:
        ValueError: If the file format is not supported.
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    with open(file_path, 'w') as f:
        if extension in ('.json', '.jsn'):
            json.dump(config, f, indent=2)
        elif extension in ('.yaml', '.yml'):
            yaml.dump(config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported configuration file format: {extension}")


def get_config_value(config: Dict[str, Any], key_path: str, default: Optional[Any] = None, 
                    separator: str = '.') -> Any:
    """
    Get a value from a nested configuration dictionary using a key path.

    Args:
        config: The configuration dictionary.
        key_path: The path to the key, using the separator to indicate nesting.
        default: The default value to return if the key is not found.
        separator: The separator used in the key path.

    Returns:
        The value at the specified key path, or the default value if not found.
    """
    keys = key_path.split(separator)
    result = config

    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default

    return result


# Logging helpers

def setup_logger(name: str, level: int = logging.INFO, 
                log_file: Optional[Union[str, Path]] = None, 
                console: bool = True, 
                format_string: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with the specified configuration.

    Args:
        name: The name of the logger.
        level: The logging level.
        log_file: Optional path to a log file.
        console: Whether to log to the console.
        format_string: Optional format string for log messages.

    Returns:
        The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

    # Set up format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if a log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_execution_time(logger: logging.Logger, level: int = logging.INFO):
    """
    Decorator to log the execution time of a function.

    Args:
        logger: The logger to use.
        level: The logging level to use.

    Returns:
        A decorator function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.datetime.now()
            result = func(*args, **kwargs)
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.log(level, f"Function {func.__name__} executed in {format_duration(duration)}")
            return result
        return wrapper
    return decorator


# Miscellaneous utilities

def generate_uuid() -> str:
    """
    Generate a UUID string.

    Returns:
        A UUID string.
    """
    return str(uuid.uuid4())


def retry(max_attempts: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, 
         exceptions: Tuple[Exception, ...] = (Exception,)):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of attempts.
        delay: Initial delay between attempts in seconds.
        backoff_factor: Factor by which the delay increases with each attempt.
        exceptions: Tuple of exceptions to catch and retry on.

    Returns:
        A decorator function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time

            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise

                    logger.warning(f"Attempt {attempt} failed with error: {str(e)}. Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)

                    attempt += 1
                    current_delay *= backoff_factor

        return wrapper
    return decorator


class Cache:
    """
    A flexible caching system with various strategies and features.

    This class provides a foundation for different caching strategies including:
    - Simple in-memory cache
    - LRU (Least Recently Used) cache
    - TTL (Time To Live) cache

    Features include:
    - Cache size limits
    - Expiration policies
    - Cache invalidation strategies
    - Statistics tracking
    """

    def __init__(self, max_size: Optional[int] = None, ttl: Optional[float] = None):
        """
        Initialize a cache.

        Args:
            max_size: Maximum number of items to store in the cache. If None, the cache is unbounded.
            ttl: Time to live for cache entries in seconds. If None, entries never expire.
        """
        self._cache: Dict[Any, Any] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._timestamps: Dict[Any, float] = {}
        self._access_counts: Dict[Any, int] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a value from the cache.

        Args:
            key: The cache key.
            default: Value to return if key is not found.

        Returns:
            The cached value or the default value if not found.
        """
        if key in self._cache:
            # Check if the entry has expired
            if self._ttl is not None:
                timestamp = self._timestamps.get(key, 0)
                if time.time() - timestamp > self._ttl:
                    self._remove_entry(key)
                    self._misses += 1
                    return default

            # Update access statistics
            self._hits += 1
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            return self._cache[key]

        self._misses += 1
        return default

    def set(self, key: Any, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
        """
        # If the cache is full, make room
        if self._max_size is not None and len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_entry()

        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._access_counts[key] = 0

    def delete(self, key: Any) -> None:
        """
        Delete a value from the cache.

        Args:
            key: The cache key to delete.
        """
        self._remove_entry(key)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self._cache.clear()
        self._timestamps.clear()
        self._access_counts.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            A dictionary with cache statistics.
        """
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'ttl': self._ttl,
            'hits': self._hits,
            'misses': self._misses,
            'hit_ratio': self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0
        }

    def _remove_entry(self, key: Any) -> None:
        """
        Remove an entry from the cache and its metadata.

        Args:
            key: The cache key to remove.
        """
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_counts.pop(key, None)

    def _evict_entry(self) -> None:
        """
        Evict an entry from the cache based on the eviction policy.

        The default implementation uses LRU (Least Recently Used) policy.
        """
        if not self._cache:
            return

        # Find the least recently used entry
        oldest_key = min(self._timestamps.items(), key=lambda x: x[1])[0]
        self._remove_entry(oldest_key)


class LRUCache(Cache):
    """
    LRU (Least Recently Used) cache implementation.

    This cache evicts the least recently used entries when it reaches its capacity.
    """

    def __init__(self, max_size: int = 100, ttl: Optional[float] = None):
        """
        Initialize an LRU cache.

        Args:
            max_size: Maximum number of items to store in the cache.
            ttl: Time to live for cache entries in seconds. If None, entries never expire.
        """
        super().__init__(max_size=max_size, ttl=ttl)
        self._access_order: List[Any] = []

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a value from the cache.

        Args:
            key: The cache key.
            default: Value to return if key is not found.

        Returns:
            The cached value or the default value if not found.
        """
        value = super().get(key, default)

        # Update access order for LRU tracking
        if key in self._cache:
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

        return value

    def set(self, key: Any, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
        """
        # Update access order for LRU tracking
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        super().set(key, value)

    def _remove_entry(self, key: Any) -> None:
        """
        Remove an entry from the cache and its metadata.

        Args:
            key: The cache key to remove.
        """
        super()._remove_entry(key)
        if key in self._access_order:
            self._access_order.remove(key)

    def _evict_entry(self) -> None:
        """
        Evict the least recently used entry from the cache.
        """
        if self._access_order:
            oldest_key = self._access_order.pop(0)
            self._remove_entry(oldest_key)


def create_key_from_args(*args, **kwargs) -> str:
    """
    Create a cache key from function arguments.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        A string key.
    """
    try:
        # Try to create a more reliable key using repr
        key = repr(args) + repr(sorted(kwargs.items()))
        return key
    except:
        # Fall back to string representation if repr fails
        return str(args) + str(sorted(kwargs.items()))


def memoize(func=None, *, max_size: Optional[int] = None, ttl: Optional[float] = None, lru: bool = False):
    """
    Decorator to memoize a function (cache its results).

    Args:
        func: The function to memoize.
        max_size: Maximum number of items to store in the cache. If None, the cache is unbounded.
        ttl: Time to live for cache entries in seconds. If None, entries never expire.
        lru: Whether to use LRU (Least Recently Used) caching strategy.

    Returns:
        The memoized function.
    """
    def decorator(func):
        # Choose the appropriate cache type
        if lru:
            cache_obj = LRUCache(max_size=max_size if max_size is not None else 100, ttl=ttl)
        else:
            cache_obj = Cache(max_size=max_size, ttl=ttl)

        def wrapper(*args, **kwargs):
            # Create a key from the function arguments
            key = create_key_from_args(*args, **kwargs)

            # Check if the result is in the cache
            result = cache_obj.get(key)
            if result is None:
                # If not, compute it and store in the cache
                result = func(*args, **kwargs)
                cache_obj.set(key, result)

            return result

        # Add cache management attributes to the wrapper function
        wrapper.cache = cache_obj
        wrapper.clear_cache = cache_obj.clear
        wrapper.get_stats = cache_obj.get_stats

        return wrapper

    # Handle both @memoize and @memoize(...)
    if func is None:
        return decorator
    return decorator(func)
