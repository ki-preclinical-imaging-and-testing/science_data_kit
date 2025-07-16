"""
File Browser Page Module for Science Data Kit Core

This module provides the framework-independent implementation of the file browser page.
It defines the core functionality for browsing files and directories.
"""

from typing import List, Dict, Any, Optional
import os
import pathlib

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import FileExplorerPageData

class FileBrowserPage(BasePage):
    """
    Core implementation of the file browser page.
    
    This class provides the framework-independent functionality for browsing
    files and directories. It returns a FileExplorerPageData object that can
    be rendered by any UI framework.
    """
    
    def __init__(self, db_connection=None, initial_path=None):
        """
        Initialize the file browser page.
        
        Args:
            db_connection: Optional database connection to use for data retrieval.
            initial_path: Optional initial path to display. Defaults to the user's home directory.
        """
        super().__init__(db_connection)
        self.current_path = initial_path or str(pathlib.Path.home())
        self.selected_files = []
        self.view_mode = "list"
        self.sort_by = "name"
        self.sort_order = "ascending"
        self.filter_pattern = None
    
    def get_page_data(self) -> FileExplorerPageData:
        """
        Return data needed to render the file browser page.
        
        Returns:
            A FileExplorerPageData object containing the data needed to render the page.
        """
        return FileExplorerPageData(
            title="File Browser",
            current_path=self.current_path,
            files=self._get_files(),
            directories=self._get_directories(),
            selected_files=self.selected_files,
            view_mode=self.view_mode,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            filter_pattern=self.filter_pattern
        )
    
    def _get_files(self) -> List[Dict[str, Any]]:
        """
        Get the list of files in the current directory.
        
        Returns:
            A list of dictionaries containing file information.
        """
        files = []
        try:
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                if os.path.isfile(item_path):
                    # Skip hidden files
                    if item.startswith('.'):
                        continue
                    
                    # Get file stats
                    stats = os.stat(item_path)
                    
                    # Add file to the list
                    files.append({
                        "name": item,
                        "path": item_path,
                        "size": stats.st_size,
                        "modified": stats.st_mtime,
                        "type": self._get_file_type(item),
                        "selected": item_path in self.selected_files
                    })
        except (FileNotFoundError, PermissionError) as e:
            # Handle errors gracefully
            pass
        
        # Apply sorting
        files = self._sort_items(files)
        
        # Apply filtering
        if self.filter_pattern:
            files = [f for f in files if self.filter_pattern.lower() in f["name"].lower()]
        
        return files
    
    def _get_directories(self) -> List[Dict[str, Any]]:
        """
        Get the list of directories in the current directory.
        
        Returns:
            A list of dictionaries containing directory information.
        """
        directories = []
        try:
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                if os.path.isdir(item_path):
                    # Skip hidden directories
                    if item.startswith('.'):
                        continue
                    
                    # Get directory stats
                    stats = os.stat(item_path)
                    
                    # Add directory to the list
                    directories.append({
                        "name": item,
                        "path": item_path,
                        "modified": stats.st_mtime,
                        "selected": item_path in self.selected_files
                    })
        except (FileNotFoundError, PermissionError) as e:
            # Handle errors gracefully
            pass
        
        # Apply sorting
        directories = self._sort_items(directories)
        
        # Apply filtering
        if self.filter_pattern:
            directories = [d for d in directories if self.filter_pattern.lower() in d["name"].lower()]
        
        return directories
    
    def _sort_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort the items based on the current sort settings.
        
        Args:
            items: The list of items to sort.
            
        Returns:
            The sorted list of items.
        """
        reverse = self.sort_order == "descending"
        
        if self.sort_by == "name":
            return sorted(items, key=lambda x: x["name"].lower(), reverse=reverse)
        elif self.sort_by == "size" and "size" in items[0] if items else False:
            return sorted(items, key=lambda x: x["size"], reverse=reverse)
        elif self.sort_by == "modified":
            return sorted(items, key=lambda x: x["modified"], reverse=reverse)
        else:
            return items
    
    def _get_file_type(self, filename: str) -> str:
        """
        Get the type of a file based on its extension.
        
        Args:
            filename: The name of the file.
            
        Returns:
            The type of the file.
        """
        extension = os.path.splitext(filename)[1].lower()
        
        if extension in ['.txt', '.md', '.csv', '.json', '.yaml', '.yml']:
            return "text"
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return "image"
        elif extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']:
            return "document"
        elif extension in ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h']:
            return "code"
        else:
            return "other"
    
    def navigate_to(self, path: str) -> None:
        """
        Navigate to the specified path.
        
        Args:
            path: The path to navigate to.
        """
        if os.path.isdir(path):
            self.current_path = path
            self.selected_files = []
    
    def navigate_up(self) -> None:
        """
        Navigate to the parent directory.
        """
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.selected_files = []
    
    def select_file(self, file_path: str, multi_select: bool = False) -> None:
        """
        Select a file.
        
        Args:
            file_path: The path of the file to select.
            multi_select: Whether to allow multiple selection.
        """
        if not multi_select:
            self.selected_files = [file_path]
        else:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            else:
                self.selected_files.append(file_path)
    
    def set_view_mode(self, mode: str) -> None:
        """
        Set the view mode.
        
        Args:
            mode: The view mode to set ("list" or "grid").
        """
        if mode in ["list", "grid"]:
            self.view_mode = mode
    
    def set_sort(self, sort_by: str, sort_order: str = None) -> None:
        """
        Set the sort settings.
        
        Args:
            sort_by: The field to sort by ("name", "size", or "modified").
            sort_order: The sort order ("ascending" or "descending").
        """
        if sort_by in ["name", "size", "modified"]:
            self.sort_by = sort_by
        
        if sort_order in ["ascending", "descending"]:
            self.sort_order = sort_order
        elif sort_by == self.sort_by and sort_order is None:
            # Toggle sort order if sorting by the same field
            self.sort_order = "descending" if self.sort_order == "ascending" else "ascending"
    
    def set_filter(self, pattern: str) -> None:
        """
        Set the filter pattern.
        
        Args:
            pattern: The pattern to filter by.
        """
        self.filter_pattern = pattern