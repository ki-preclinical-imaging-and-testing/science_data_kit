"""
Versionable capability mixin for Science Data Kit connections.

This module provides a mixin that defines the versionable capability for connections,
allowing them to work with versioned resources.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional


class Versionable:
    """Mixin for connections that support versioning of resources."""
    
    @abstractmethod
    def get_versions(self, path: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a resource.
        
        Args:
            path: Path to the resource
            
        Returns:
            List of dictionaries containing version metadata
        """
        pass
    
    @abstractmethod
    def get_version(self, path: str, version_id: str) -> Dict[str, Any]:
        """
        Get a specific version of a resource.
        
        Args:
            path: Path to the resource
            version_id: ID of the version to get
            
        Returns:
            Dictionary containing resource data and metadata
        """
        pass
    
    @abstractmethod
    def restore_version(self, path: str, version_id: str) -> Dict[str, Any]:
        """
        Restore a resource to a specific version.
        
        Args:
            path: Path to the resource
            version_id: ID of the version to restore
            
        Returns:
            Dictionary containing metadata about the restored resource
        """
        pass
    
    def get_latest_version(self, path: str) -> Dict[str, Any]:
        """
        Get the latest version of a resource.
        
        Args:
            path: Path to the resource
            
        Returns:
            Dictionary containing resource data and metadata
        """
        versions = self.get_versions(path)
        if not versions:
            raise ValueError(f"No versions found for resource: {path}")
        
        # Assuming versions are sorted with most recent first
        latest_version = versions[0]
        return self.get_version(path, latest_version["version_id"])
    
    def compare_versions(self, path: str, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        Compare two versions of a resource.
        
        Args:
            path: Path to the resource
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dictionary containing comparison information
        """
        v1 = self.get_version(path, version_id1)
        v2 = self.get_version(path, version_id2)
        
        # Basic comparison - implementations can override for more sophisticated comparison
        return {
            "path": path,
            "version1": {
                "id": version_id1,
                "metadata": v1.get("metadata", {}),
            },
            "version2": {
                "id": version_id2,
                "metadata": v2.get("metadata", {}),
            },
            "differences": {
                "size": v1.get("size") != v2.get("size"),
                "modified": v1.get("modified") != v2.get("modified"),
                "content_type": v1.get("content_type") != v2.get("content_type"),
            }
        }