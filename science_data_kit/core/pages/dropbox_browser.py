"""
Dropbox Browser Page Module for Science Data Kit Core

This module provides the Dropbox Browser page for the Science Data Kit application.
It defines the framework-independent core functionality for the Dropbox Browser page.
"""

from typing import Dict, Any, List, Optional
import os
from datetime import datetime

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import DropboxBrowserPageData
from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.files import DropboxFileManager

class DropboxBrowserPage(BasePage):
    """
    Dropbox Browser page for browsing Dropbox files and folders.

    This class provides the core business logic for the Dropbox Browser page,
    independent of any UI framework.
    """

    def __init__(self, db_connection=None, connector=None, initial_path=""):
        """
        Initialize the Dropbox Browser page.

        Args:
            db_connection: Database connection (optional)
            connector: DropboxConnector instance (optional)
            initial_path: Initial path to browse (default: "")
        """
        super().__init__(db_connection)
        self.connector = connector
        self.current_path = initial_path
        self.connection_status = {"dropbox": False if connector is None else connector.is_connected()}
        self.connection_errors = {}
        self.files = []
        self.directories = []
        self.selected_file = None
        self.search_results = []
        self.view_mode = "list"
        self.sort_by = "name"
        self.sort_order = "ascending"
        self.filter_pattern = None
        
        # Initialize file manager if connector is provided
        self.file_manager = None
        if self.connector and self.connector.is_connected():
            self.file_manager = DropboxFileManager(self.connector)
            self._load_current_directory()

    def get_page_data(self) -> DropboxBrowserPageData:
        """
        Return data needed to render the Dropbox Browser page.

        Returns:
            An instance of DropboxBrowserPageData containing the data needed
            to render the Dropbox Browser page.
        """
        return DropboxBrowserPageData(
            title="Dropbox File Browser",
            requires_auth=True,
            current_path=self.current_path,
            files=self.files,
            directories=self.directories,
            selected_file=self.selected_file,
            search_results=self.search_results,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            view_mode=self.view_mode,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            filter_pattern=self.filter_pattern
        )

    def set_connector(self, connector: DropboxConnector) -> bool:
        """
        Set the Dropbox connector.

        Args:
            connector: DropboxConnector instance

        Returns:
            True if the connector is valid and connected, False otherwise
        """
        if not connector or not connector.is_connected():
            self.connection_status["dropbox"] = False
            self.connection_errors["dropbox"] = "Invalid or disconnected connector"
            return False

        self.connector = connector
        self.connection_status["dropbox"] = True
        self.file_manager = DropboxFileManager(self.connector)
        self._load_current_directory()
        return True

    def navigate_to(self, path: str) -> bool:
        """
        Navigate to a specific path.

        Args:
            path: The path to navigate to

        Returns:
            True if navigation was successful, False otherwise
        """
        if not self.file_manager:
            self.connection_errors["navigation"] = "No file manager available"
            return False

        try:
            self.current_path = path
            self._load_current_directory()
            return True
        except Exception as e:
            self.connection_errors["navigation"] = str(e)
            return False

    def select_file(self, file_path: str) -> bool:
        """
        Select a file for viewing details.

        Args:
            file_path: The path of the file to select

        Returns:
            True if file selection was successful, False otherwise
        """
        if not self.file_manager:
            self.connection_errors["file_selection"] = "No file manager available"
            return False

        try:
            # Find the file in the current directory
            selected_file = None
            for file in self.files:
                if file["path"] == file_path:
                    selected_file = file
                    break

            if not selected_file:
                # If not found, try to get metadata directly
                metadata = self.file_manager.get_metadata(file_path)
                if metadata and metadata["type"] == "file":
                    selected_file = metadata

            if not selected_file:
                self.connection_errors["file_selection"] = f"File not found: {file_path}"
                return False

            self.selected_file = selected_file
            return True
        except Exception as e:
            self.connection_errors["file_selection"] = str(e)
            return False

    def download_file(self, file_path: str) -> Dict[str, Any]:
        """
        Download a file from Dropbox.

        Args:
            file_path: The path of the file to download

        Returns:
            A dictionary with the file content and metadata
        """
        result = {
            "success": False,
            "error": None,
            "content": None,
            "metadata": None
        }

        if not self.file_manager:
            result["error"] = "No file manager available"
            return result

        try:
            content, metadata = self.file_manager.download_file(file_path)
            result["success"] = True
            result["content"] = content
            result["metadata"] = metadata
            return result
        except Exception as e:
            result["error"] = str(e)
            self.connection_errors["download"] = str(e)
            return result

    def search(self, query: str, path: Optional[str] = None, 
               file_extensions: Optional[List[str]] = None, max_results: int = 100) -> bool:
        """
        Search for files and folders in Dropbox.

        Args:
            query: The search query
            path: The path to search in (optional, defaults to current path)
            file_extensions: List of file extensions to filter by (optional)
            max_results: Maximum number of results to return (default: 100)

        Returns:
            True if search was successful, False otherwise
        """
        if not self.file_manager:
            self.connection_errors["search"] = "No file manager available"
            return False

        try:
            search_path = path if path is not None else self.current_path
            results = self.file_manager.search(
                query=query,
                path=search_path,
                max_results=max_results,
                file_extensions=file_extensions
            )
            
            self.search_results = results
            return True
        except Exception as e:
            self.connection_errors["search"] = str(e)
            return False

    def clear_search_results(self) -> None:
        """Clear search results."""
        self.search_results = []

    def set_view_mode(self, view_mode: str) -> None:
        """
        Set the view mode.

        Args:
            view_mode: The view mode ("list" or "grid")
        """
        self.view_mode = view_mode

    def set_sort(self, sort_by: str, sort_order: str) -> None:
        """
        Set the sort options.

        Args:
            sort_by: The field to sort by ("name", "size", "modified")
            sort_order: The sort order ("ascending" or "descending")
        """
        self.sort_by = sort_by
        self.sort_order = sort_order
        self._sort_items()

    def set_filter(self, filter_pattern: str) -> None:
        """
        Set the filter pattern.

        Args:
            filter_pattern: The filter pattern
        """
        self.filter_pattern = filter_pattern
        self._load_current_directory()

    def _load_current_directory(self) -> None:
        """Load the contents of the current directory."""
        if not self.file_manager:
            return

        try:
            items = self.file_manager.list_folder(self.current_path)
            
            # Separate folders and files
            self.directories = [item for item in items if item["type"] == "folder"]
            self.files = [item for item in items if item["type"] == "file"]
            
            # Apply filter if set
            if self.filter_pattern:
                self.directories = [d for d in self.directories if self.filter_pattern.lower() in d["name"].lower()]
                self.files = [f for f in self.files if self.filter_pattern.lower() in f["name"].lower()]
            
            # Sort items
            self._sort_items()
        except Exception as e:
            self.connection_errors["directory_listing"] = str(e)
            self.directories = []
            self.files = []

    def _sort_items(self) -> None:
        """Sort directories and files based on sort options."""
        # Define sort key function
        def get_sort_key(item):
            if self.sort_by == "name":
                return item["name"].lower()
            elif self.sort_by == "size":
                return item.get("size", 0)
            elif self.sort_by == "modified":
                return item.get("modified", datetime.min)
            else:
                return item["name"].lower()
        
        # Sort directories
        self.directories.sort(key=get_sort_key, reverse=(self.sort_order == "descending"))
        
        # Sort files
        self.files.sort(key=get_sort_key, reverse=(self.sort_order == "descending"))

    def format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def format_datetime(self, dt: datetime) -> str:
        """
        Format datetime in human-readable format.

        Args:
            dt: Datetime object

        Returns:
            Formatted datetime string
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")