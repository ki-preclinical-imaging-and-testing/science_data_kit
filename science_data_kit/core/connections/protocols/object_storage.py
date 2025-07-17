"""
Object Storage protocol for Science Data Kit connections.

This module provides the object storage protocol class that defines the interface
for connections to object storage-based data sources like S3, Azure Blob Storage, etc.
"""

import pandas as pd
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union, BinaryIO, Iterator

from .base import ConnectionProtocol


class ObjectStorageProtocol(ConnectionProtocol):
    """Protocol for object storage-based connections."""
    
    @property
    def connection_type(self) -> str:
        """Return the connection type."""
        return "object_storage"
    
    @abstractmethod
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all buckets/containers.
        
        Returns:
            List of dictionaries containing metadata about buckets
        """
        pass
    
    @abstractmethod
    def list_objects(self, bucket_name: str, prefix: str = "", 
                    delimiter: str = "/") -> Dict[str, List[Dict[str, Any]]]:
        """
        List objects in a bucket with optional prefix and delimiter.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Prefix to filter objects
            delimiter: Delimiter for hierarchical listing
            
        Returns:
            Dictionary with 'objects' and 'prefixes' keys containing lists of objects and prefixes
        """
        pass
    
    @abstractmethod
    def get_object_metadata(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """
        Get metadata for an object.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            
        Returns:
            Dictionary containing object metadata
        """
        pass
    
    @abstractmethod
    def download_object(self, bucket_name: str, object_key: str) -> bytes:
        """
        Download an object and return its contents as bytes.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            
        Returns:
            Object contents as bytes
        """
        pass
    
    @abstractmethod
    def upload_object(self, bucket_name: str, object_key: str, 
                     content: Union[bytes, BinaryIO],
                     metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload content to an object.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            content: Content to upload (bytes or file-like object)
            metadata: Optional metadata to attach to the object
            
        Returns:
            Dictionary containing metadata about the uploaded object
        """
        pass
    
    @abstractmethod
    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """
        Delete an object.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_bucket(self, bucket_name: str, 
                     region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a bucket.
        
        Args:
            bucket_name: Name of the bucket
            region: Optional region for the bucket
            
        Returns:
            Dictionary containing metadata about the created bucket
        """
        pass
    
    @abstractmethod
    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete a bucket.
        
        Args:
            bucket_name: Name of the bucket
            force: Whether to delete all objects in the bucket first
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_presigned_url(self, bucket_name: str, object_key: str, 
                              expiration: int = 3600, 
                              http_method: str = "GET") -> str:
        """
        Generate a presigned URL for an object.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            expiration: Expiration time in seconds
            http_method: HTTP method for the URL
            
        Returns:
            Presigned URL as a string
        """
        pass
    
    def download_as_dataframe(self, bucket_name: str, object_key: str, **kwargs) -> pd.DataFrame:
        """
        Download an object and return its contents as a pandas DataFrame.
        
        Args:
            bucket_name: Name of the bucket
            object_key: Key of the object
            **kwargs: Additional arguments to pass to pandas
            
        Returns:
            Pandas DataFrame containing the object data
        """
        content = self.download_object(bucket_name, object_key)
        # Determine file type from extension
        if object_key.endswith('.csv'):
            return pd.read_csv(content, **kwargs)
        elif object_key.endswith('.xlsx') or object_key.endswith('.xls'):
            return pd.read_excel(content, **kwargs)
        elif object_key.endswith('.json'):
            return pd.read_json(content, **kwargs)
        elif object_key.endswith('.parquet'):
            return pd.read_parquet(content, **kwargs)
        else:
            raise ValueError(f"Unsupported file format for object: {object_key}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this connection."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "browsable": True,
            "readable": True,
            "writable": True,
            "data_types": ["objects", "buckets"],
            "supports_presigned_urls": True,
        })
        return capabilities