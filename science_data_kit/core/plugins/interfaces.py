"""
Standardized plugin interfaces for Science Data Kit.

This module provides standardized interfaces for plugins to implement,
ensuring consistent behavior across different plugin types.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type, Union

from ..connections.protocols.base import ConnectionProtocol
from ..connections.protocols.filesystem import FilesystemProtocol
from ..connections.protocols.database import DatabaseProtocol
from ..connections.protocols.api import APIProtocol
from ..connections.protocols.object_storage import ObjectStorageProtocol
from .config import PluginConfigSchema


class PluginInterface(ABC):
    """Base interface for all plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get the plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the plugin description."""
        pass
    
    @property
    @abstractmethod
    def config_schema(self) -> PluginConfigSchema:
        """Get the plugin configuration schema."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against this plugin's schema.
        
        Args:
            config: The configuration to validate
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with the given configuration.
        
        Args:
            config: The configuration to use
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        pass
    
    @property
    def capabilities(self) -> Set[str]:
        """Get the plugin capabilities."""
        return set()


class ConnectionPluginInterface(PluginInterface, ConnectionProtocol):
    """Base interface for connection plugins."""
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> None:
        """
        Establish connection with the service.
        
        Args:
            config: Configuration dictionary for the connection
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Clean up connection."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Verify connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def connection_type(self) -> str:
        """
        Return the type of connection (filesystem, api, database, etc.).
        
        Returns:
            String representing the connection type
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """
        Check if the connection is currently established.
        
        Returns:
            True if connected, False otherwise
        """
        return False


class FilesystemPluginInterface(ConnectionPluginInterface, FilesystemProtocol):
    """Interface for filesystem plugins."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "filesystem"
    
    @abstractmethod
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            List of dictionaries containing file/directory information
        """
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> bytes:
        """
        Read a file.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: bytes) -> bool:
        """
        Write to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.
        
        Args:
            path: Path to the directory
            recursive: Whether to delete recursively
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            path: Path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            path: Path to the directory
            
        Returns:
            True if the directory exists, False otherwise
        """
        pass


class DatabasePluginInterface(ConnectionPluginInterface, DatabaseProtocol):
    """Interface for database plugins."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "database"
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a query.
        
        Args:
            query: The query to execute
            params: Query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    def execute_batch(self, queries: List[str]) -> List[Any]:
        """
        Execute multiple queries.
        
        Args:
            queries: List of queries to execute
            
        Returns:
            List of query results
        """
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        """
        Get a list of tables.
        
        Returns:
            List of table names
        """
        pass
    
    @abstractmethod
    def get_schema(self, table: str) -> Dict[str, Any]:
        """
        Get the schema for a table.
        
        Args:
            table: Table name
            
        Returns:
            Table schema
        """
        pass
    
    @abstractmethod
    def begin_transaction(self) -> bool:
        """
        Begin a transaction.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def commit_transaction(self) -> bool:
        """
        Commit a transaction.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> bool:
        """
        Rollback a transaction.
        
        Returns:
            True if successful, False otherwise
        """
        pass


class APIPluginInterface(ConnectionPluginInterface, APIProtocol):
    """Interface for API plugins."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "api"
    
    @abstractmethod
    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Request headers
            
        Returns:
            API response
        """
        pass
    
    @abstractmethod
    def get_endpoints(self) -> List[str]:
        """
        Get a list of available endpoints.
        
        Returns:
            List of endpoint names
        """
        pass
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get the current rate limit status.
        
        Returns:
            Rate limit information
        """
        pass


class ObjectStoragePluginInterface(ConnectionPluginInterface, ObjectStorageProtocol):
    """Interface for object storage plugins."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "object_storage"
    
    @abstractmethod
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all buckets.
        
        Returns:
            List of bucket information
        """
        pass
    
    @abstractmethod
    def list_objects(self, bucket: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List objects in a bucket.
        
        Args:
            bucket: Bucket name
            prefix: Object prefix
            
        Returns:
            List of object information
        """
        pass
    
    @abstractmethod
    def get_object(self, bucket: str, key: str) -> bytes:
        """
        Get an object.
        
        Args:
            bucket: Bucket name
            key: Object key
            
        Returns:
            Object contents as bytes
        """
        pass
    
    @abstractmethod
    def put_object(self, bucket: str, key: str, data: bytes) -> bool:
        """
        Put an object.
        
        Args:
            bucket: Bucket name
            key: Object key
            data: Object data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> bool:
        """
        Delete an object.
        
        Args:
            bucket: Bucket name
            key: Object key
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_bucket(self, bucket: str) -> bool:
        """
        Create a bucket.
        
        Args:
            bucket: Bucket name
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_bucket(self, bucket: str) -> bool:
        """
        Delete a bucket.
        
        Args:
            bucket: Bucket name
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def object_exists(self, bucket: str, key: str) -> bool:
        """
        Check if an object exists.
        
        Args:
            bucket: Bucket name
            key: Object key
            
        Returns:
            True if the object exists, False otherwise
        """
        pass
    
    @abstractmethod
    def bucket_exists(self, bucket: str) -> bool:
        """
        Check if a bucket exists.
        
        Args:
            bucket: Bucket name
            
        Returns:
            True if the bucket exists, False otherwise
        """
        pass