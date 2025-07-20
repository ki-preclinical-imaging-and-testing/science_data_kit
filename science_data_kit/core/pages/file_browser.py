"""
File Browser Page Module for Science Data Kit Core

This module provides the framework-independent implementation of the file browser page.
It defines the core functionality for browsing files and directories.
"""

from typing import List, Dict, Any, Optional
import os
import pathlib
import tempfile

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import FileExplorerPageData
from science_data_kit.core.integrations.plugin_architecture import get_file_interpreter_for_file

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

        This method includes metadata and preview information for the selected file,
        if a file is selected and a suitable interpreter is available.

        Returns:
            A FileExplorerPageData object containing the data needed to render the page.
        """
        # Get metadata and preview for the selected file
        selected_file_metadata = None
        selected_file_preview = None
        has_file_interpreter = False

        if self.selected_files and len(self.selected_files) == 1:
            selected_file_path = self.selected_files[0]

            # Check if a file interpreter is available
            interpreter = get_file_interpreter_for_file(selected_file_path)
            has_file_interpreter = interpreter is not None

            # Extract metadata if an interpreter is available
            if has_file_interpreter:
                selected_file_metadata = self.extract_metadata(selected_file_path)

                # Generate preview if metadata extraction was successful
                if selected_file_metadata:
                    selected_file_preview = self.generate_preview(selected_file_path)

        return FileExplorerPageData(
            title="File Browser",
            current_path=self.current_path,
            files=self._get_files(),
            directories=self._get_directories(),
            selected_files=self.selected_files,
            view_mode=self.view_mode,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            filter_pattern=self.filter_pattern,
            selected_file_metadata=selected_file_metadata,
            selected_file_preview=selected_file_preview,
            has_file_interpreter=has_file_interpreter
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

        This method first tries to use a FileInterpreterPlugin to determine the file type.
        If no suitable plugin is found, it falls back to a simple extension-based approach.

        Args:
            filename: The name of the file.

        Returns:
            The type of the file.
        """
        file_path = os.path.join(self.current_path, filename)

        # Try to get a file interpreter for this file
        interpreter = get_file_interpreter_for_file(file_path)
        if interpreter:
            # If we have an interpreter, use its capabilities to determine the type
            if hasattr(interpreter, 'extract_text') and callable(getattr(interpreter, 'extract_text')):
                return "text"
            elif hasattr(interpreter, 'generate_preview') and callable(getattr(interpreter, 'generate_preview')):
                # Check if it's an image or document based on MIME type
                mime_types = interpreter.get_supported_mime_types()
                if any(mime.startswith('image/') for mime in mime_types):
                    return "image"
                elif any(mime.startswith('application/pdf') or mime.startswith('application/vnd.openxmlformats') for mime in mime_types):
                    return "document"
                elif any(mime.startswith('application/x-netcdf') or mime.startswith('application/x-hdf5') for mime in mime_types):
                    return "scientific"

            # If we couldn't determine a specific type but have an interpreter, use "specialized"
            return "specialized"

        # Fall back to extension-based approach if no interpreter is available
        extension = os.path.splitext(filename)[1].lower()

        if extension in ['.txt', '.md', '.csv', '.json', '.yaml', '.yml']:
            return "text"
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return "image"
        elif extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']:
            return "document"
        elif extension in ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.h']:
            return "code"
        elif extension in ['.nc', '.hdf5', '.h5', '.fits', '.fts', '.fit', '.nii', '.nii.gz']:
            return "scientific"
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

    def extract_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a file using a FileInterpreterPlugin.

        Args:
            file_path: The path of the file to extract metadata from.

        Returns:
            A dictionary of metadata key-value pairs, or None if no suitable interpreter is found.
        """
        interpreter = get_file_interpreter_for_file(file_path)
        if interpreter:
            try:
                # Get basic file info
                basic_info = interpreter.get_file_info(file_path)

                # Extract specialized metadata
                metadata = interpreter.extract_metadata(file_path)

                # Combine basic info and specialized metadata
                combined_metadata = {**basic_info, **metadata}

                return combined_metadata
            except Exception as e:
                # Handle errors gracefully
                print(f"Error extracting metadata from {file_path}: {str(e)}")
                return None
        return None

    def generate_preview(self, file_path: str) -> Optional[Any]:
        """
        Generate a preview for a file using a FileInterpreterPlugin.

        Args:
            file_path: The path of the file to generate a preview for.

        Returns:
            Preview data or path to the generated preview, or None if no suitable interpreter is found.
        """
        interpreter = get_file_interpreter_for_file(file_path)
        if interpreter:
            try:
                # Create a temporary directory for the preview
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = os.path.join(temp_dir, "preview")

                    # Generate the preview
                    preview = interpreter.generate_preview(file_path, output_path)

                    return preview
            except Exception as e:
                # Handle errors gracefully
                print(f"Error generating preview for {file_path}: {str(e)}")
                return None
        return None

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
