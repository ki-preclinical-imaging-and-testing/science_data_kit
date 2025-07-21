"""
SharePoint Storage Provider for Science Data Kit

This module provides a SharePoint storage provider for accessing files
stored in SharePoint document libraries through the Microsoft Graph API.
"""

import io
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...providers.registry import BaseProvider
from ...db.msgraph_manager import MSGraphConnectionManager

class SharePointProvider(BaseProvider):
    """
    SharePoint storage provider for file access through Microsoft Graph API.

    This provider allows access to SharePoint document libraries and files
    using the Microsoft Graph API.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SharePoint storage provider.

        Args:
            config: Configuration dictionary containing:
                   tenant_id: Microsoft tenant ID
                   client_id: Microsoft application client ID
                   client_secret: Microsoft application client secret
                   auth_method: Authentication method (default: "device_code")
                   site_id: SharePoint site ID (optional)
                   drive_id: SharePoint drive ID (optional)
        """
        super().__init__(config)
        self.manager = None
        self.site_id = config.get("site_id")
        self.drive_id = config.get("drive_id")

    async def initialize(self) -> bool:
        """
        Initialize SharePoint storage access.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Extract configuration values
            tenant_id = self.config.get("tenant_id")
            client_id = self.config.get("client_id")
            client_secret = self.config.get("client_secret")
            auth_method = self.config.get("auth_method", "device_code")

            # Create the connection manager
            self.manager = MSGraphConnectionManager(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                auth_method=auth_method
            )

            # Connect to Microsoft Graph API
            success = self.manager.connect()
            if not success:
                print("Failed to connect to Microsoft Graph API")
                return False

            # If site_id and drive_id are not provided, use the default site and drive
            if not self.site_id or not self.drive_id:
                # Get the default site
                sites = self.manager.execute_query("/sites")
                if not sites or "value" not in sites or not sites["value"]:
                    print("No SharePoint sites found")
                    return False

                # Use the first site
                self.site_id = sites["value"][0]["id"]

                # Get the default document library (drive)
                drives = self.manager.execute_query(f"/sites/{self.site_id}/drives")
                if not drives or "value" not in drives or not drives["value"]:
                    print("No document libraries found for the site")
                    return False

                # Use the first drive
                self.drive_id = drives["value"][0]["id"]

            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Error initializing SharePoint provider: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Verify SharePoint storage access is working.

        Returns:
            True if the access is healthy, False otherwise
        """
        if not self.is_initialized or not self.manager:
            return False

        try:
            # Test the connection by getting the drive
            self.manager.execute_query(f"/drives/{self.drive_id}")
            return True
        except Exception as e:
            print(f"SharePoint health check failed: {str(e)}")
            return False

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities.

        Returns:
            Dictionary of provider capabilities
        """
        return {
            "data_types": ["files", "csv", "excel", "docx", "pdf"],
            "real_time": False,
            "formats": ["csv", "xlsx", "xls", "docx", "pdf"],
            "max_size": "15GB"  # SharePoint file size limit
        }

    async def list_files(self, folder_path: str = "", file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a SharePoint folder.

        Args:
            folder_path: Path to the folder in SharePoint (item ID or path)
            file_types: List of file extensions to filter by (e.g., ["csv", "xlsx"])

        Returns:
            List of file metadata dictionaries
        """
        if not self.is_initialized or not self.manager:
            raise Exception("SharePoint provider not initialized")

        if file_types is None:
            file_types = ["csv", "xlsx", "xls", "docx", "pdf"]

        try:
            # Determine the API path based on the folder_path
            if not folder_path or folder_path == "/":
                # List root items
                api_path = f"/drives/{self.drive_id}/root/children"
            elif folder_path.startswith("/"):
                # Path-based access
                path = folder_path.rstrip("/")
                api_path = f"/drives/{self.drive_id}/root:{path}:/children"
            else:
                # ID-based access
                api_path = f"/drives/{self.drive_id}/items/{folder_path}/children"

            # Execute the query
            response = self.manager.execute_query(api_path)

            # Process the response
            files = []
            if "value" in response:
                for item in response["value"]:
                    is_folder = "folder" in item

                    if is_folder:
                        # Include directories for navigation
                        files.append({
                            "id": item.get("id", ""),
                            "name": item.get("name", ""),
                            "path": item.get("id", ""),  # Use ID as path for navigation
                            "type": "folder"
                        })
                    else:
                        # Check if file has one of the specified extensions
                        file_ext = os.path.splitext(item.get("name", ""))[1].lower().lstrip(".")
                        if file_ext in file_types:
                            files.append({
                                "id": item.get("id", ""),
                                "name": item.get("name", ""),
                                "path": item.get("id", ""),  # Use ID as path for file operations
                                "size": item.get("size", 0),
                                "modified": item.get("lastModifiedDateTime", ""),
                                "type": file_ext
                            })

            return files

        except Exception as e:
            print(f"Error listing SharePoint files: {str(e)}")
            raise

    async def download_file_data(self, file_path: str) -> pd.DataFrame:
        """
        Download file and return as pandas DataFrame.

        Args:
            file_path: Path to the file in SharePoint (item ID)

        Returns:
            Pandas DataFrame containing the file data
        """
        if not self.is_initialized or not self.manager:
            raise Exception("SharePoint provider not initialized")

        try:
            # Get file content
            api_path = f"/drives/{self.drive_id}/items/{file_path}/content"
            content = self.manager.execute_query(api_path, use_cache=False)

            # Get file metadata to determine the file type
            api_path_meta = f"/drives/{self.drive_id}/items/{file_path}"
            metadata = self.manager.execute_query(api_path_meta)

            # Detect file type
            file_name = metadata.get("name", "")
            file_ext = os.path.splitext(file_name)[1].lower()

            # Parse with appropriate pandas function
            if file_ext == ".csv":
                return pd.read_csv(io.BytesIO(content))
            elif file_ext in [".xlsx", ".xls"]:
                return pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            print(f"Error downloading file from SharePoint: {str(e)}")
            raise

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata without downloading.

        Args:
            file_path: Path to the file in SharePoint (item ID)

        Returns:
            Dictionary containing file metadata
        """
        if not self.is_initialized or not self.manager:
            raise Exception("SharePoint provider not initialized")

        try:
            # Get file metadata
            api_path = f"/drives/{self.drive_id}/items/{file_path}"
            metadata = self.manager.execute_query(api_path)

            # Extract relevant information
            file_name = metadata.get("name", "")
            file_ext = os.path.splitext(file_name)[1].lower().lstrip(".")

            # Include parentReference for navigation
            result = {
                "id": metadata.get("id", ""),
                "name": file_name,
                "path": metadata.get("id", ""),  # Use ID as path for file operations
                "size": metadata.get("size", 0),
                "modified": metadata.get("lastModifiedDateTime", ""),
                "type": file_ext,
                "url": metadata.get("webUrl", ""),
                "created": metadata.get("createdDateTime", ""),
                "created_by": metadata.get("createdBy", {}).get("user", {}).get("displayName", ""),
                "modified_by": metadata.get("lastModifiedBy", {}).get("user", {}).get("displayName", "")
            }

            # Add parentReference if available
            if "parentReference" in metadata:
                result["parentReference"] = metadata["parentReference"]

            return result

        except Exception as e:
            print(f"Error getting SharePoint file info: {str(e)}")
            raise
