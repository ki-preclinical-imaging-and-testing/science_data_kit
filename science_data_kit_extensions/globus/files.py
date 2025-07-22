"""
Globus file manager for Science Data Kit.

This module provides a file manager for Globus, handling file operations
for Globus endpoints.
"""

import os
import io
import logging
from typing import Dict, Any, Optional, List, Union, BinaryIO, Tuple
from datetime import datetime
from pathlib import Path

# Globus SDK imports
try:
    import globus_sdk
    from globus_sdk import TransferClient, TransferData
    from globus_sdk.exc import TransferAPIError
    GLOBUS_SDK_AVAILABLE = True
except ImportError:
    GLOBUS_SDK_AVAILABLE = False
    logging.warning("Globus SDK not available. Install with 'pip install globus-sdk'")

from .connector import GlobusConnector


class GlobusFileManager:
    """
    File manager for Globus endpoints.
    
    This class handles file operations for Globus endpoints, including
    listing, downloading, uploading, and deleting files.
    """
    
    def __init__(self, connector: GlobusConnector):
        """
        Initialize the Globus file manager.
        
        Args:
            connector: GlobusConnector instance
        """
        self.logger = logging.getLogger(__name__)
        
        if not GLOBUS_SDK_AVAILABLE:
            self.logger.error("Globus SDK not available. Install with 'pip install globus-sdk'")
            raise ImportError("Globus SDK not available")
        
        self.connector = connector
        self.transfer_client = None
        
        if connector.is_connected():
            self.transfer_client = connector.transfer_client
    
    def list_endpoints(self, filter_scope: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List available Globus endpoints.
        
        Args:
            filter_scope: Filter endpoints by scope (my-endpoints, shared-with-me, etc.)
            limit: Maximum number of endpoints to return
            
        Returns:
            List of endpoint dictionaries
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return []
        
        try:
            params = {"limit": limit}
            if filter_scope:
                params["filter_scope"] = filter_scope
                
            response = self.transfer_client.get_endpoint_list(**params)
            
            endpoints = []
            for ep in response.data:
                endpoints.append({
                    "id": ep["id"],
                    "display_name": ep["display_name"],
                    "owner_string": ep.get("owner_string", ""),
                    "description": ep.get("description", ""),
                    "is_globus_connect": ep.get("is_globus_connect", False),
                    "activated": ep.get("activated", False),
                    "gcp_connected": ep.get("gcp_connected", False),
                    "subscription_id": ep.get("subscription_id", None)
                })
            
            return endpoints
        except Exception as e:
            self.logger.error(f"Error listing endpoints: {str(e)}")
            return []
    
    def get_endpoint_details(self, endpoint_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            
        Returns:
            Dictionary with endpoint details
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return {"error": "Not connected to Globus Transfer service"}
        
        try:
            response = self.transfer_client.get_endpoint(endpoint_id)
            return response.data
        except Exception as e:
            self.logger.error(f"Error getting endpoint details: {str(e)}")
            return {"error": str(e)}
    
    def list_directory(self, endpoint_id: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        List contents of a directory on a Globus endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            path: Path to the directory
            
        Returns:
            List of file/directory dictionaries
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return []
        
        try:
            response = self.transfer_client.operation_ls(endpoint_id, path=path)
            
            items = []
            for item in response.data:
                item_info = {
                    "name": item["name"],
                    "type": "directory" if item["type"] == "dir" else "file",
                    "size": item.get("size", 0),
                    "last_modified": item.get("last_modified", ""),
                    "permissions": item.get("permissions", ""),
                    "user": item.get("user", ""),
                    "group": item.get("group", ""),
                    "path": os.path.join(path, item["name"]).replace("\\", "/")
                }
                items.append(item_info)
            
            return items
        except Exception as e:
            self.logger.error(f"Error listing directory: {str(e)}")
            return []
    
    def download_file(self, endpoint_id: str, path: str, local_path: Optional[str] = None) -> Union[bytes, str, None]:
        """
        Download a file from a Globus endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            path: Path to the file on the endpoint
            local_path: Local path to save the file (if None, returns file content as bytes)
            
        Returns:
            File content as bytes if local_path is None, otherwise the local path
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return None
        
        try:
            # For direct download, we need to use the TransferClient's get_data method
            # Note: This is only available for small files and some endpoints may not support it
            response = self.transfer_client.get_data(endpoint_id, path)
            
            if local_path:
                # Save to local file
                with open(local_path, 'wb') as f:
                    f.write(response.data)
                return local_path
            else:
                # Return the data directly
                return response.data
        except TransferAPIError as e:
            # If direct download is not supported, we need to use a transfer
            self.logger.warning(f"Direct download not supported: {str(e)}")
            self.logger.info("For large files or endpoints that don't support direct download, use transfer_file method")
            return None
        except Exception as e:
            self.logger.error(f"Error downloading file: {str(e)}")
            return None
    
    def transfer_file(self, source_endpoint_id: str, source_path: str, 
                     destination_endpoint_id: str, destination_path: str) -> Dict[str, Any]:
        """
        Transfer a file between Globus endpoints.
        
        Args:
            source_endpoint_id: ID of the source endpoint
            source_path: Path to the file on the source endpoint
            destination_endpoint_id: ID of the destination endpoint
            destination_path: Path to save the file on the destination endpoint
            
        Returns:
            Dictionary with transfer task information
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return {"error": "Not connected to Globus Transfer service"}
        
        try:
            # Create a transfer data object
            transfer_data = TransferData(
                self.transfer_client,
                source_endpoint_id,
                destination_endpoint_id,
                label=f"SDK Transfer {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                sync_level="checksum"
            )
            
            # Add the file to the transfer
            transfer_data.add_item(source_path, destination_path)
            
            # Submit the transfer
            response = self.transfer_client.submit_transfer(transfer_data)
            
            return {
                "task_id": response["task_id"],
                "status": "SUBMITTED",
                "message": "Transfer submitted successfully"
            }
        except Exception as e:
            self.logger.error(f"Error transferring file: {str(e)}")
            return {"error": str(e)}
    
    def get_transfer_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a transfer task.
        
        Args:
            task_id: ID of the transfer task
            
        Returns:
            Dictionary with transfer task status
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return {"error": "Not connected to Globus Transfer service"}
        
        try:
            response = self.transfer_client.get_task(task_id)
            return response.data
        except Exception as e:
            self.logger.error(f"Error getting transfer status: {str(e)}")
            return {"error": str(e)}
    
    def create_directory(self, endpoint_id: str, path: str) -> Dict[str, Any]:
        """
        Create a directory on a Globus endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            path: Path to the directory to create
            
        Returns:
            Dictionary with operation status
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return {"error": "Not connected to Globus Transfer service"}
        
        try:
            response = self.transfer_client.operation_mkdir(endpoint_id, path)
            return {
                "status": "success",
                "message": f"Directory created at {path}",
                "code": response.http_status
            }
        except Exception as e:
            self.logger.error(f"Error creating directory: {str(e)}")
            return {"error": str(e)}
    
    def delete(self, endpoint_id: str, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Delete a file or directory on a Globus endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            path: Path to the file or directory to delete
            recursive: Whether to delete directories recursively
            
        Returns:
            Dictionary with operation status
        """
        if not self.transfer_client:
            self.logger.error("Not connected to Globus Transfer service")
            return {"error": "Not connected to Globus Transfer service"}
        
        try:
            # Check if it's a directory
            try:
                self.transfer_client.operation_ls(endpoint_id, path=path)
                is_dir = True
            except TransferAPIError:
                is_dir = False
            
            if is_dir and not recursive:
                return {
                    "error": "Cannot delete directory without recursive flag"
                }
            
            response = self.transfer_client.operation_rm(endpoint_id, path, recursive=recursive)
            return {
                "status": "success",
                "message": f"Deleted {path}",
                "code": response.http_status
            }
        except Exception as e:
            self.logger.error(f"Error deleting: {str(e)}")
            return {"error": str(e)}
    
    def search(self, query: str, endpoint_id: Optional[str] = None, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for files on Globus endpoints.
        
        Note: This requires the Globus Search service and properly indexed endpoints.
        
        Args:
            query: Search query
            endpoint_id: Optional endpoint ID to limit search
            path: Optional path to limit search
            
        Returns:
            List of search results
        """
        if not self.connector.search_client:
            self.logger.error("Not connected to Globus Search service")
            return []
        
        try:
            search_params = {
                "q": query,
                "limit": 100
            }
            
            # Add filters if provided
            if endpoint_id or path:
                filters = []
                if endpoint_id:
                    filters.append(f"endpoint_id:{endpoint_id}")
                if path:
                    filters.append(f"path:{path}*")
                
                search_params["filters"] = " AND ".join(filters)
            
            response = self.connector.search_client.search(**search_params)
            
            results = []
            for item in response.data.get("gmeta", []):
                for entry in item.get("entries", []):
                    results.append(entry)
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching: {str(e)}")
            return []