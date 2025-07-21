"""
Batch Processing Module for Science Data Kit

This module provides functionality for performing operations on multiple files at once,
including common file operations and specialized operations using file interpreters.
"""

from typing import List, Dict, Any, Optional, Callable, Union, Tuple
import os
import shutil
import concurrent.futures
from pathlib import Path
import logging
from datetime import datetime
import tempfile

from science_data_kit.core.integrations.plugin_architecture import get_file_interpreter_for_file
from science_data_kit.core.db.db_manager import Neo4jManager

# Configure logging
logger = logging.getLogger(__name__)

class BatchProcessingResult:
    """
    Class for storing the results of a batch processing operation.
    
    This class tracks successful and failed operations, along with
    detailed information about each operation.
    """
    
    def __init__(self):
        """Initialize a new batch processing result."""
        self.successful_operations = []
        self.failed_operations = []
        self.start_time = datetime.now()
        self.end_time = None
        self.total_files = 0
        self.processed_files = 0
        self.operation_type = None
        
    def add_success(self, file_path: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a successful operation to the result.
        
        Args:
            file_path: The path of the file that was successfully processed.
            details: Optional details about the operation.
        """
        self.successful_operations.append({
            "file_path": file_path,
            "details": details or {},
            "timestamp": datetime.now()
        })
        self.processed_files += 1
        
    def add_failure(self, file_path: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a failed operation to the result.
        
        Args:
            file_path: The path of the file that failed to process.
            error: The error message.
            details: Optional details about the operation.
        """
        self.failed_operations.append({
            "file_path": file_path,
            "error": error,
            "details": details or {},
            "timestamp": datetime.now()
        })
        self.processed_files += 1
        
    def complete(self, operation_type: str) -> None:
        """
        Mark the batch processing as complete.
        
        Args:
            operation_type: The type of operation that was performed.
        """
        self.end_time = datetime.now()
        self.operation_type = operation_type
        
    @property
    def duration(self) -> float:
        """
        Get the duration of the batch processing in seconds.
        
        Returns:
            The duration in seconds, or None if the processing is not complete.
        """
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
        
    @property
    def success_count(self) -> int:
        """
        Get the number of successful operations.
        
        Returns:
            The number of successful operations.
        """
        return len(self.successful_operations)
        
    @property
    def failure_count(self) -> int:
        """
        Get the number of failed operations.
        
        Returns:
            The number of failed operations.
        """
        return len(self.failed_operations)
        
    @property
    def success_rate(self) -> float:
        """
        Get the success rate of the batch processing.
        
        Returns:
            The success rate as a percentage, or 0 if no files were processed.
        """
        if self.processed_files == 0:
            return 0
        return (self.success_count / self.processed_files) * 100
        
    @property
    def is_complete(self) -> bool:
        """
        Check if the batch processing is complete.
        
        Returns:
            True if the processing is complete, False otherwise.
        """
        return self.end_time is not None
        
    @property
    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the batch processing.
        
        Returns:
            A dictionary containing summary information.
        """
        return {
            "operation_type": self.operation_type,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_complete": self.is_complete
        }
        
    def __str__(self) -> str:
        """
        Get a string representation of the batch processing result.
        
        Returns:
            A string representation of the result.
        """
        return (
            f"BatchProcessingResult: {self.operation_type}\n"
            f"Total files: {self.total_files}\n"
            f"Processed files: {self.processed_files}\n"
            f"Success count: {self.success_count}\n"
            f"Failure count: {self.failure_count}\n"
            f"Success rate: {self.success_rate:.2f}%\n"
            f"Duration: {self.duration:.2f} seconds\n"
            f"Status: {'Complete' if self.is_complete else 'In progress'}"
        )


class BatchProcessor:
    """
    Class for performing batch operations on multiple files.
    
    This class provides methods for common file operations (copy, move, delete)
    and specialized operations using file interpreters (extract metadata,
    generate previews, update knowledge graph).
    """
    
    def __init__(self, max_workers: int = 4, db_connection=None):
        """
        Initialize a new batch processor.
        
        Args:
            max_workers: The maximum number of worker threads to use for parallel processing.
            db_connection: Optional database connection to use for knowledge graph operations.
        """
        self.max_workers = max_workers
        self.db_connection = db_connection
        
    def process_files(self, file_paths: List[str], operation: Callable, 
                     operation_type: str, **kwargs) -> BatchProcessingResult:
        """
        Process multiple files with the given operation.
        
        Args:
            file_paths: List of file paths to process.
            operation: The operation to perform on each file.
            operation_type: The type of operation being performed (for logging).
            **kwargs: Additional arguments to pass to the operation.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        result = BatchProcessingResult()
        result.total_files = len(file_paths)
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path, operation, **kwargs): file_path
                for file_path in file_paths
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success, message, details = future.result()
                    if success:
                        result.add_success(file_path, details)
                    else:
                        result.add_failure(file_path, message, details)
                except Exception as e:
                    result.add_failure(file_path, str(e), {"exception": type(e).__name__})
        
        # Mark the result as complete
        result.complete(operation_type)
        return result
    
    def _process_single_file(self, file_path: str, operation: Callable, **kwargs) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process a single file with the given operation.
        
        Args:
            file_path: The path of the file to process.
            operation: The operation to perform on the file.
            **kwargs: Additional arguments to pass to the operation.
            
        Returns:
            A tuple containing (success, message, details).
        """
        try:
            # Check if the file exists
            if not os.path.isfile(file_path):
                return False, f"File not found: {file_path}", {}
            
            # Perform the operation
            result = operation(file_path, **kwargs)
            
            # Handle different return types
            if isinstance(result, tuple) and len(result) >= 2:
                success, message = result[0], result[1]
                details = result[2] if len(result) > 2 else {}
                return success, message, details
            elif isinstance(result, bool):
                return result, "Operation completed" if result else "Operation failed", {}
            elif result is None:
                return True, "Operation completed", {}
            else:
                return True, "Operation completed", {"result": result}
        except Exception as e:
            logger.exception(f"Error processing file {file_path}: {str(e)}")
            return False, str(e), {"exception": type(e).__name__}
    
    # Common file operations
    
    def copy_files(self, file_paths: List[str], destination_dir: str, 
                  overwrite: bool = False) -> BatchProcessingResult:
        """
        Copy multiple files to a destination directory.
        
        Args:
            file_paths: List of file paths to copy.
            destination_dir: The destination directory.
            overwrite: Whether to overwrite existing files.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        # Create the destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        def copy_operation(file_path, destination_dir, overwrite):
            try:
                # Get the destination file path
                dest_path = os.path.join(destination_dir, os.path.basename(file_path))
                
                # Check if the destination file already exists
                if os.path.exists(dest_path) and not overwrite:
                    return False, f"Destination file already exists: {dest_path}", {}
                
                # Copy the file
                shutil.copy2(file_path, dest_path)
                
                return True, f"File copied to {dest_path}", {"destination": dest_path}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            copy_operation, 
            "copy_files", 
            destination_dir=destination_dir, 
            overwrite=overwrite
        )
    
    def move_files(self, file_paths: List[str], destination_dir: str, 
                  overwrite: bool = False) -> BatchProcessingResult:
        """
        Move multiple files to a destination directory.
        
        Args:
            file_paths: List of file paths to move.
            destination_dir: The destination directory.
            overwrite: Whether to overwrite existing files.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        # Create the destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        def move_operation(file_path, destination_dir, overwrite):
            try:
                # Get the destination file path
                dest_path = os.path.join(destination_dir, os.path.basename(file_path))
                
                # Check if the destination file already exists
                if os.path.exists(dest_path) and not overwrite:
                    return False, f"Destination file already exists: {dest_path}", {}
                
                # Move the file
                shutil.move(file_path, dest_path)
                
                return True, f"File moved to {dest_path}", {"destination": dest_path}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            move_operation, 
            "move_files", 
            destination_dir=destination_dir, 
            overwrite=overwrite
        )
    
    def delete_files(self, file_paths: List[str]) -> BatchProcessingResult:
        """
        Delete multiple files.
        
        Args:
            file_paths: List of file paths to delete.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        def delete_operation(file_path):
            try:
                # Delete the file
                os.remove(file_path)
                
                return True, f"File deleted: {file_path}", {}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(file_paths, delete_operation, "delete_files")
    
    def rename_files(self, file_paths: List[str], new_names: List[str]) -> BatchProcessingResult:
        """
        Rename multiple files.
        
        Args:
            file_paths: List of file paths to rename.
            new_names: List of new names for the files.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        if len(file_paths) != len(new_names):
            raise ValueError("The number of file paths must match the number of new names")
        
        # Create a dictionary mapping file paths to new names
        rename_map = dict(zip(file_paths, new_names))
        
        def rename_operation(file_path, rename_map):
            try:
                # Get the new name
                new_name = rename_map[file_path]
                
                # Get the directory of the file
                directory = os.path.dirname(file_path)
                
                # Create the new file path
                new_path = os.path.join(directory, new_name)
                
                # Check if the new file already exists
                if os.path.exists(new_path):
                    return False, f"File already exists: {new_path}", {}
                
                # Rename the file
                os.rename(file_path, new_path)
                
                return True, f"File renamed to {new_name}", {"new_path": new_path}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            rename_operation, 
            "rename_files", 
            rename_map=rename_map
        )
    
    # Specialized operations using file interpreters
    
    def extract_metadata(self, file_paths: List[str]) -> BatchProcessingResult:
        """
        Extract metadata from multiple files using file interpreters.
        
        Args:
            file_paths: List of file paths to extract metadata from.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        def extract_metadata_operation(file_path):
            try:
                # Get a file interpreter for this file
                interpreter = get_file_interpreter_for_file(file_path)
                if not interpreter:
                    return False, f"No suitable interpreter found for {file_path}", {}
                
                # Get basic file info
                basic_info = interpreter.get_file_info(file_path)
                
                # Extract specialized metadata
                metadata = interpreter.extract_metadata(file_path)
                
                # Combine basic info and specialized metadata
                combined_metadata = {**basic_info, **metadata}
                
                return True, f"Metadata extracted from {file_path}", {"metadata": combined_metadata}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(file_paths, extract_metadata_operation, "extract_metadata")
    
    def generate_previews(self, file_paths: List[str], output_dir: str = None) -> BatchProcessingResult:
        """
        Generate previews for multiple files using file interpreters.
        
        Args:
            file_paths: List of file paths to generate previews for.
            output_dir: Optional directory to save the previews. If not provided,
                        a temporary directory will be used.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        # Create the output directory if it doesn't exist and was provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        def generate_preview_operation(file_path, output_dir):
            try:
                # Get a file interpreter for this file
                interpreter = get_file_interpreter_for_file(file_path)
                if not interpreter:
                    return False, f"No suitable interpreter found for {file_path}", {}
                
                # Create a temporary directory for the preview if no output_dir was provided
                if not output_dir:
                    temp_dir = tempfile.mkdtemp()
                    output_path = os.path.join(temp_dir, "preview")
                else:
                    # Create a subdirectory for each file to avoid name conflicts
                    file_name = os.path.basename(file_path)
                    file_dir = os.path.join(output_dir, os.path.splitext(file_name)[0])
                    os.makedirs(file_dir, exist_ok=True)
                    output_path = os.path.join(file_dir, "preview")
                
                # Generate the preview
                preview = interpreter.generate_preview(file_path, output_path)
                
                return True, f"Preview generated for {file_path}", {"preview": preview, "output_path": output_path}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            generate_preview_operation, 
            "generate_previews", 
            output_dir=output_dir
        )
    
    def update_knowledge_graph(self, file_paths: List[str]) -> BatchProcessingResult:
        """
        Update the knowledge graph with metadata from multiple files.
        
        Args:
            file_paths: List of file paths to update in the knowledge graph.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        # Check if we have a database connection
        if not self.db_connection:
            logger.warning("No database connection available for knowledge graph update")
            result = BatchProcessingResult()
            result.total_files = len(file_paths)
            for file_path in file_paths:
                result.add_failure(file_path, "No database connection available", {})
            result.complete("update_knowledge_graph")
            return result
        
        # Get a Neo4j manager instance
        try:
            neo4j_manager = Neo4jManager()
            if not neo4j_manager.is_connected():
                logger.warning("Neo4j manager is not connected to a database")
                result = BatchProcessingResult()
                result.total_files = len(file_paths)
                for file_path in file_paths:
                    result.add_failure(file_path, "Neo4j manager is not connected", {})
                result.complete("update_knowledge_graph")
                return result
        except Exception as e:
            logger.error(f"Error creating Neo4j manager: {str(e)}")
            result = BatchProcessingResult()
            result.total_files = len(file_paths)
            for file_path in file_paths:
                result.add_failure(file_path, f"Error creating Neo4j manager: {str(e)}", {})
            result.complete("update_knowledge_graph")
            return result
        
        def update_knowledge_graph_operation(file_path, neo4j_manager):
            try:
                # Extract metadata using a file interpreter
                interpreter = get_file_interpreter_for_file(file_path)
                if not interpreter:
                    return False, f"No suitable interpreter found for {file_path}", {}
                
                # Get basic file info
                basic_info = interpreter.get_file_info(file_path)
                
                # Extract specialized metadata
                metadata = interpreter.extract_metadata(file_path)
                
                # Combine basic info and specialized metadata
                combined_metadata = {**basic_info, **metadata}
                
                # Prepare metadata for Neo4j (convert non-primitive types to strings)
                processed_metadata = {}
                for key, value in combined_metadata.items():
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
                    neo4j_manager.execute_query(update_query, {
                        "path": file_path,
                        "metadata": processed_metadata
                    })
                    return True, f"Updated file node for {file_path}", {"action": "updated"}
                else:
                    # Create new file node
                    create_query = """
                    CREATE (f:File $metadata)
                    RETURN f
                    """
                    # Ensure path is included in metadata
                    processed_metadata["path"] = file_path
                    
                    neo4j_manager.execute_query(create_query, {
                        "metadata": processed_metadata
                    })
                    return True, f"Created new file node for {file_path}", {"action": "created"}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            update_knowledge_graph_operation, 
            "update_knowledge_graph", 
            neo4j_manager=neo4j_manager
        )
    
    def export_metadata(self, file_paths: List[str], export_format: str = 'json', 
                       output_dir: str = None) -> BatchProcessingResult:
        """
        Export metadata from multiple files to the specified format.
        
        Args:
            file_paths: List of file paths to export metadata from.
            export_format: The format to export to ('json', 'yaml', 'csv', or 'excel').
            output_dir: Optional directory to save the exported metadata. If not provided,
                        the metadata will be returned in the result details.
            
        Returns:
            A BatchProcessingResult object containing the results of the operation.
        """
        # Create the output directory if it doesn't exist and was provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        def export_metadata_operation(file_path, export_format, output_dir):
            try:
                # Extract metadata using a file interpreter
                interpreter = get_file_interpreter_for_file(file_path)
                if not interpreter:
                    return False, f"No suitable interpreter found for {file_path}", {}
                
                # Get basic file info
                basic_info = interpreter.get_file_info(file_path)
                
                # Extract specialized metadata
                metadata = interpreter.extract_metadata(file_path)
                
                # Combine basic info and specialized metadata
                combined_metadata = {**basic_info, **metadata}
                
                # If output_dir is provided, save to file
                if output_dir:
                    # Create the output file path
                    file_name = os.path.basename(file_path)
                    output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.{export_format}")
                    
                    # Export based on format
                    if export_format.lower() == 'json':
                        import json
                        with open(output_file, 'w') as f:
                            json.dump(combined_metadata, f, indent=2)
                    elif export_format.lower() == 'yaml':
                        import yaml
                        with open(output_file, 'w') as f:
                            yaml.dump(combined_metadata, f, sort_keys=False)
                    elif export_format.lower() == 'csv':
                        import csv
                        # Flatten the metadata for CSV export
                        flattened_data = self._flatten_metadata(combined_metadata)
                        
                        with open(output_file, 'w', newline='') as f:
                            writer = csv.writer(f)
                            # Write header
                            writer.writerow(['Key', 'Value'])
                            # Write data
                            for key, value in flattened_data.items():
                                writer.writerow([key, value])
                    elif export_format.lower() == 'excel':
                        try:
                            import pandas as pd
                            # Flatten the metadata for Excel export
                            flattened_data = self._flatten_metadata(combined_metadata)
                            
                            # Create DataFrame and save to Excel
                            df = pd.DataFrame(list(flattened_data.items()), columns=['Key', 'Value'])
                            df.to_excel(output_file, sheet_name='Metadata', index=False)
                        except ImportError:
                            return False, "Pandas is required for Excel export but is not available", {}
                    else:
                        return False, f"Unsupported export format: {export_format}", {}
                    
                    return True, f"Metadata exported to {output_file}", {"output_file": output_file}
                else:
                    # Return the metadata in the result details
                    return True, f"Metadata extracted from {file_path}", {"metadata": combined_metadata}
            except Exception as e:
                return False, str(e), {"exception": type(e).__name__}
        
        return self.process_files(
            file_paths, 
            export_metadata_operation, 
            "export_metadata", 
            export_format=export_format, 
            output_dir=output_dir
        )
    
    def _flatten_metadata(self, metadata: Dict[str, Any], parent_key: str = '') -> Dict[str, str]:
        """
        Flatten nested metadata dictionary for CSV export.
        
        Args:
            metadata: The metadata dictionary to flatten.
            parent_key: The parent key for nested dictionaries.
            
        Returns:
            A flattened dictionary with dot-notation keys.
        """
        flattened = {}
        for key, value in metadata.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                flattened.update(self._flatten_metadata(value, new_key))
            elif isinstance(value, (list, tuple)):
                # Convert lists to strings
                flattened[new_key] = ', '.join(str(item) for item in value)
            else:
                # Convert value to string
                flattened[new_key] = str(value) if value is not None else ''
                
        return flattened


# Convenience functions for batch processing

def batch_copy_files(file_paths: List[str], destination_dir: str, 
                    overwrite: bool = False, max_workers: int = 4) -> BatchProcessingResult:
    """
    Copy multiple files to a destination directory.
    
    Args:
        file_paths: List of file paths to copy.
        destination_dir: The destination directory.
        overwrite: Whether to overwrite existing files.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.copy_files(file_paths, destination_dir, overwrite)

def batch_move_files(file_paths: List[str], destination_dir: str, 
                    overwrite: bool = False, max_workers: int = 4) -> BatchProcessingResult:
    """
    Move multiple files to a destination directory.
    
    Args:
        file_paths: List of file paths to move.
        destination_dir: The destination directory.
        overwrite: Whether to overwrite existing files.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.move_files(file_paths, destination_dir, overwrite)

def batch_delete_files(file_paths: List[str], max_workers: int = 4) -> BatchProcessingResult:
    """
    Delete multiple files.
    
    Args:
        file_paths: List of file paths to delete.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.delete_files(file_paths)

def batch_rename_files(file_paths: List[str], new_names: List[str], 
                      max_workers: int = 4) -> BatchProcessingResult:
    """
    Rename multiple files.
    
    Args:
        file_paths: List of file paths to rename.
        new_names: List of new names for the files.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.rename_files(file_paths, new_names)

def batch_extract_metadata(file_paths: List[str], max_workers: int = 4) -> BatchProcessingResult:
    """
    Extract metadata from multiple files.
    
    Args:
        file_paths: List of file paths to extract metadata from.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.extract_metadata(file_paths)

def batch_generate_previews(file_paths: List[str], output_dir: str = None, 
                          max_workers: int = 4) -> BatchProcessingResult:
    """
    Generate previews for multiple files.
    
    Args:
        file_paths: List of file paths to generate previews for.
        output_dir: Optional directory to save the previews.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.generate_previews(file_paths, output_dir)

def batch_update_knowledge_graph(file_paths: List[str], db_connection=None, 
                               max_workers: int = 4) -> BatchProcessingResult:
    """
    Update the knowledge graph with metadata from multiple files.
    
    Args:
        file_paths: List of file paths to update in the knowledge graph.
        db_connection: Optional database connection to use.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers, db_connection=db_connection)
    return processor.update_knowledge_graph(file_paths)

def batch_export_metadata(file_paths: List[str], export_format: str = 'json', 
                         output_dir: str = None, max_workers: int = 4) -> BatchProcessingResult:
    """
    Export metadata from multiple files to the specified format.
    
    Args:
        file_paths: List of file paths to export metadata from.
        export_format: The format to export to ('json', 'yaml', 'csv', or 'excel').
        output_dir: Optional directory to save the exported metadata.
        max_workers: The maximum number of worker threads to use.
        
    Returns:
        A BatchProcessingResult object containing the results of the operation.
    """
    processor = BatchProcessor(max_workers=max_workers)
    return processor.export_metadata(file_paths, export_format, output_dir)