"""
File Browser Page Module for Science Data Kit Core

This module provides the framework-independent implementation of the file browser page.
It defines the core functionality for browsing files and directories.
"""

from typing import List, Dict, Any, Optional
import os
import pathlib
import tempfile
import yaml
import json
from datetime import datetime

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import FileExplorerPageData
from science_data_kit.core.integrations.plugin_architecture import get_file_interpreter_for_file
from science_data_kit.core.db.db_manager import Neo4jManager

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
        self.metadata_filters = []  # List of metadata filter criteria
        self.saved_searches = {}  # Dictionary of saved searches

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

        # Apply name filtering
        if self.filter_pattern:
            files = [f for f in files if self.filter_pattern.lower() in f["name"].lower()]

        # Apply metadata filtering
        if self.metadata_filters:
            filtered_files = []
            for file in files:
                # Extract metadata for the file
                metadata = self.extract_metadata(file["path"])
                if metadata:
                    # Check if the file passes all metadata filters
                    passes_all_filters = True
                    for filter_criterion in self.metadata_filters:
                        field = filter_criterion["field"]
                        operator = filter_criterion["operator"]
                        filter_value = filter_criterion["value"]

                        # Handle nested fields (e.g., 'crs.epsg')
                        field_parts = field.split('.')
                        field_value = metadata
                        for part in field_parts:
                            if isinstance(field_value, dict) and part in field_value:
                                field_value = field_value[part]
                            else:
                                field_value = None
                                break

                        # Skip this filter if the field doesn't exist
                        if field_value is None:
                            passes_all_filters = False
                            break

                        # Apply the operator
                        if operator == '=':
                            if field_value != filter_value:
                                passes_all_filters = False
                                break
                        elif operator == '!=':
                            if field_value == filter_value:
                                passes_all_filters = False
                                break
                        elif operator == '>':
                            if not (isinstance(field_value, (int, float)) and field_value > filter_value):
                                passes_all_filters = False
                                break
                        elif operator == '<':
                            if not (isinstance(field_value, (int, float)) and field_value < filter_value):
                                passes_all_filters = False
                                break
                        elif operator == '>=':
                            if not (isinstance(field_value, (int, float)) and field_value >= filter_value):
                                passes_all_filters = False
                                break
                        elif operator == '<=':
                            if not (isinstance(field_value, (int, float)) and field_value <= filter_value):
                                passes_all_filters = False
                                break
                        elif operator == 'contains':
                            if not (isinstance(field_value, str) and filter_value.lower() in field_value.lower()):
                                passes_all_filters = False
                                break
                        elif operator == 'startswith':
                            if not (isinstance(field_value, str) and field_value.lower().startswith(filter_value.lower())):
                                passes_all_filters = False
                                break
                        elif operator == 'endswith':
                            if not (isinstance(field_value, str) and field_value.lower().endswith(filter_value.lower())):
                                passes_all_filters = False
                                break

                    # Add the file to the filtered list if it passes all filters
                    if passes_all_filters:
                        filtered_files.append(file)

            files = filtered_files

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

    def select_file(self, file_path: str, multi_select: bool = False, update_graph: bool = True) -> None:
        """
        Select a file.

        Args:
            file_path: The path of the file to select.
            multi_select: Whether to allow multiple selection.
            update_graph: Whether to update the knowledge graph with file metadata.
        """
        if not multi_select:
            self.selected_files = [file_path]
        else:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
            else:
                self.selected_files.append(file_path)

        # Update knowledge graph with file metadata if requested and file is selected
        if update_graph and file_path in self.selected_files and os.path.isfile(file_path):
            # Check if a file interpreter is available for this file
            interpreter = get_file_interpreter_for_file(file_path)
            if interpreter:
                # Update the knowledge graph in the background to avoid blocking the UI
                try:
                    self.update_knowledge_graph_with_metadata(file_path)
                except Exception as e:
                    self.logger.error(f"Error updating knowledge graph: {str(e)}")

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

    def set_metadata_filter(self, field: str, operator: str, value: Any) -> None:
        """
        Add a metadata filter criterion.

        Args:
            field: The metadata field to filter by (e.g., 'width', 'height', 'crs.epsg').
            operator: The operator to use ('=', '!=', '>', '<', '>=', '<=', 'contains', 'startswith', 'endswith').
            value: The value to compare against.
        """
        self.metadata_filters.append({
            'field': field,
            'operator': operator,
            'value': value
        })

    def clear_metadata_filters(self) -> None:
        """
        Clear all metadata filters.
        """
        self.metadata_filters = []

    def get_saved_searches_path(self) -> pathlib.Path:
        """
        Get the path to the saved searches file.

        Returns:
            Path to the saved searches file.
        """
        # Create saved searches directory in user's home directory
        saved_searches_dir = pathlib.Path.home() / ".science_data_kit"
        saved_searches_dir.mkdir(parents=True, exist_ok=True)
        return saved_searches_dir / "saved_searches.yaml"

    def save_search(self, name: str) -> Dict[str, Any]:
        """
        Save the current search criteria with the given name.

        Args:
            name: The name to save the search as.

        Returns:
            A dictionary with the result of the operation.
        """
        if not name:
            return {"success": False, "error": "Search name is required"}

        # Create search object
        search = {
            "name": name,
            "filter_pattern": self.filter_pattern,
            "metadata_filters": self.metadata_filters,
            "created_at": datetime.now().isoformat(),
            "path": self.current_path
        }

        # Load existing saved searches
        saved_searches = self.load_saved_searches()

        # Add or update the search
        saved_searches[name] = search

        # Save to file
        try:
            with open(self.get_saved_searches_path(), 'w') as file:
                yaml.dump({"saved_searches": saved_searches}, file)

            # Update instance variable
            self.saved_searches = saved_searches

            return {"success": True, "message": f"Search '{name}' saved successfully!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_saved_searches(self) -> Dict[str, Any]:
        """
        Load saved searches from file.

        Returns:
            A dictionary of saved searches.
        """
        saved_searches_path = self.get_saved_searches_path()

        if not saved_searches_path.exists():
            return {}

        try:
            with open(saved_searches_path, 'r') as file:
                data = yaml.safe_load(file)

            if data and "saved_searches" in data:
                self.saved_searches = data["saved_searches"]
                return self.saved_searches
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error loading saved searches: {str(e)}")
            return {}

    def delete_saved_search(self, name: str) -> Dict[str, Any]:
        """
        Delete a saved search.

        Args:
            name: The name of the search to delete.

        Returns:
            A dictionary with the result of the operation.
        """
        # Load existing saved searches
        saved_searches = self.load_saved_searches()

        # Check if the search exists
        if name not in saved_searches:
            return {"success": False, "error": f"Search '{name}' not found"}

        # Remove the search
        del saved_searches[name]

        # Save to file
        try:
            with open(self.get_saved_searches_path(), 'w') as file:
                yaml.dump({"saved_searches": saved_searches}, file)

            # Update instance variable
            self.saved_searches = saved_searches

            return {"success": True, "message": f"Search '{name}' deleted successfully!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def apply_saved_search(self, name: str) -> Dict[str, Any]:
        """
        Apply a saved search.

        Args:
            name: The name of the search to apply.

        Returns:
            A dictionary with the result of the operation.
        """
        # Load existing saved searches
        saved_searches = self.load_saved_searches()

        # Check if the search exists
        if name not in saved_searches:
            return {"success": False, "error": f"Search '{name}' not found"}

        # Get the search
        search = saved_searches[name]

        # Apply the search criteria
        self.filter_pattern = search.get("filter_pattern")
        self.metadata_filters = search.get("metadata_filters", [])

        # Navigate to the saved path if it exists
        saved_path = search.get("path")
        if saved_path and os.path.isdir(saved_path):
            self.current_path = saved_path

        return {
            "success": True, 
            "message": f"Search '{name}' applied successfully!",
            "filter_pattern": self.filter_pattern,
            "metadata_filters": self.metadata_filters,
            "current_path": self.current_path
        }

    def update_knowledge_graph_with_metadata(self, file_path: str) -> bool:
        """
        Update the knowledge graph with specialized metadata for a file.

        This method extracts metadata from a file using a file interpreter and
        updates or creates a file node in the knowledge graph with this metadata.

        Args:
            file_path: The path of the file to extract metadata from and update in the graph.

        Returns:
            True if the update was successful, False otherwise.
        """
        # Check if we have a database connection
        if not self.db_connection:
            self.logger.warning("No database connection available for knowledge graph update")
            return False

        # Get a Neo4j manager instance
        try:
            neo4j_manager = Neo4jManager()
            if not neo4j_manager.is_connected():
                self.logger.warning("Neo4j manager is not connected to a database")
                return False
        except Exception as e:
            self.logger.error(f"Error creating Neo4j manager: {str(e)}")
            return False

        # Extract metadata using a file interpreter
        metadata = self.extract_metadata(file_path)
        if not metadata:
            self.logger.warning(f"No metadata could be extracted from {file_path}")
            return False

        # Prepare metadata for Neo4j (convert non-primitive types to strings)
        processed_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                processed_metadata[key] = value
            else:
                processed_metadata[key] = str(value)

        # Check if a file node exists for this path
        query = """
        MATCH (f:File {path: $path})
        RETURN count(f) as count
        """
        result = neo4j_manager.execute_query(query, {"path": file_path})

        if result and result[0]["count"] > 0:
            # Update existing file node
            update_query = """
            MATCH (f:File {path: $path})
            SET f += $metadata
            RETURN f
            """
            try:
                neo4j_manager.execute_query(update_query, {
                    "path": file_path,
                    "metadata": processed_metadata
                })
                self.logger.info(f"Updated file node for {file_path} with specialized metadata")
                return True
            except Exception as e:
                self.logger.error(f"Error updating file node: {str(e)}")
                return False
        else:
            # Create new file node
            create_query = """
            CREATE (f:File $metadata)
            RETURN f
            """
            try:
                # Ensure path is included in metadata
                processed_metadata["path"] = file_path

                neo4j_manager.execute_query(create_query, {
                    "metadata": processed_metadata
                })
                self.logger.info(f"Created new file node for {file_path} with specialized metadata")
                return True
            except Exception as e:
                self.logger.error(f"Error creating file node: {str(e)}")
                return False
