"""
File Utilities for Science Data Kit

This module provides utilities for organizing and managing files, including
creating structured directory hierarchies, copying files, browsing file trees,
reading spreadsheets/tables, and compressing/extracting files.
"""

import os
import subprocess
import zipfile
import tarfile
import shutil
from typing import List, Optional, Union, Dict, Any, Tuple
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import datetime
import json


class FileOrganizer:
    """
    A utility class for organizing files based on a CSV file with hierarchy information.

    This class helps organize files by creating a structured directory hierarchy using
    symlinks based on columns in a CSV file, and then optionally copying the real files
    to a final destination using rsync.

    Attributes:
        csv_file (str): Path to the CSV containing file paths and hierarchy columns.
        source_dir (str): Original directory where files are located.
        symlink_dir (str): Directory where symlinked structure will be created.
        final_export_dir (str): Directory where real files will be copied using rsync.
        df (pd.DataFrame): DataFrame containing the CSV data.
        total_files (int): Total number of files to process.
    """

    def __init__(
        self, 
        csv_file: Union[str, Path], 
        source_dir: Union[str, Path], 
        symlink_dir: Union[str, Path], 
        final_export_dir: Union[str, Path]
    ) -> None:
        """
        Initialize the FileOrganizer.

        Args:
            csv_file: Path to the CSV containing file paths and hierarchy columns.
            source_dir: Original directory where files are located.
            symlink_dir: Directory where symlinked structure will be created.
            final_export_dir: Directory where real files will be copied using rsync.
        """
        self.csv_file = str(csv_file)
        self.source_dir = str(source_dir).rstrip("/")
        self.symlink_dir = str(symlink_dir).rstrip("/")
        self.final_export_dir = str(final_export_dir).rstrip("/")
        self.df = pd.read_csv(self.csv_file)
        self.total_files = len(self.df)

    def create_symlinks(
        self, 
        hierarchy_columns: Optional[List[str]] = None,
        file_path_column: str = "filepath"
    ) -> None:
        """
        Create a structured directory with symlinks based on CSV data.

        This method reads the CSV file and creates a directory structure based on
        the hierarchy columns, with symlinks pointing to the original files.

        Args:
            hierarchy_columns: List of column names to use for the hierarchy.
                If None, defaults to ["col1", "col2", "col3"].
            file_path_column: Name of the column containing the file paths.
        """
        print("\n📁 Creating symlink structure...\n")

        if hierarchy_columns is None:
            hierarchy_columns = ["col1", "col2", "col3"]

        for _, row in tqdm(self.df.iterrows(), total=self.total_files, desc="🔗 Creating symlinks"):
            original_path = os.path.join(self.source_dir, row[file_path_column])

            # Construct the new path based on hierarchy columns
            hierarchy_path = os.path.join(
                self.symlink_dir, 
                *[str(row[col]) for col in hierarchy_columns]
            )
            new_path = os.path.join(hierarchy_path, os.path.basename(original_path))

            # Ensure the directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            # Create the symlink
            if not os.path.exists(new_path):  # Avoid duplicate symlinks
                try:
                    os.symlink(original_path, new_path)
                except Exception as e:
                    print(f"⚠️ Error creating symlink for {original_path}: {e}")

    def run_rsync(self, rsync_options: Optional[List[str]] = None) -> int:
        """
        Run rsync to copy the real files from the symlink structure.

        This method uses rsync to copy the real files from the symlink structure
        to the final export directory.

        Args:
            rsync_options: Additional options to pass to rsync.
                If None, defaults to ["-av", "--copy-links"].

        Returns:
            The return code from the rsync process (0 for success).
        """
        print("\n🚀 Running rsync to copy real files...\n")

        if rsync_options is None:
            rsync_options = ["-av", "--copy-links"]

        rsync_cmd = [
            "rsync", *rsync_options,
            f"{self.symlink_dir}/", f"{self.final_export_dir}/"
        ]

        # Run rsync as a subprocess and track progress
        process = subprocess.Popen(
            rsync_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )

        # Count total symlinks (files to copy)
        total_symlinks = sum([len(files) for _, _, files in os.walk(self.symlink_dir)])

        with tqdm(total=total_symlinks, desc="📂 Copying files with rsync") as pbar:
            for line in iter(process.stdout.readline, ''):
                pbar.update(1)  # Increment tqdm progress bar
                print(line.strip())  # Print rsync output in real-time

        return_code = process.wait()
        return return_code

    def execute(self, 
                hierarchy_columns: Optional[List[str]] = None,
                file_path_column: str = "filepath",
                rsync_options: Optional[List[str]] = None,
                prompt_before_rsync: bool = True
    ) -> None:
        """
        Execute the full pipeline: create symlinks and run rsync.

        Args:
            hierarchy_columns: List of column names to use for the hierarchy.
                If None, defaults to ["col1", "col2", "col3"].
            file_path_column: Name of the column containing the file paths.
            rsync_options: Additional options to pass to rsync.
                If None, defaults to ["-av", "--copy-links"].
            prompt_before_rsync: Whether to prompt the user before running rsync.
        """
        self.create_symlinks(hierarchy_columns, file_path_column)

        if prompt_before_rsync:
            input("\n🔴 Press Enter to proceed with final rsync (this will copy actual files)...")

        return_code = self.run_rsync(rsync_options)

        if return_code == 0:
            print("\n✅ All files copied successfully! New structure is in:", self.final_export_dir)
        else:
            print(f"\n❌ rsync failed with return code {return_code}")


def organize_files(
    csv_file: Union[str, Path], 
    source_dir: Union[str, Path], 
    output_dir: Union[str, Path],
    hierarchy_columns: Optional[List[str]] = None,
    file_path_column: str = "filepath",
    use_symlinks: bool = False,
    rsync_options: Optional[List[str]] = None
) -> None:
    """
    Organize files based on a CSV file with hierarchy information.

    This is a convenience function that wraps the FileOrganizer class.

    Args:
        csv_file: Path to the CSV containing file paths and hierarchy columns.
        source_dir: Original directory where files are located.
        output_dir: Directory where the organized files will be placed.
        hierarchy_columns: List of column names to use for the hierarchy.
            If None, defaults to ["col1", "col2", "col3"].
        file_path_column: Name of the column containing the file paths.
        use_symlinks: Whether to create symlinks instead of copying files.
        rsync_options: Additional options to pass to rsync if copying files.
            If None, defaults to ["-av", "--copy-links"].
    """
    if use_symlinks:
        # If using symlinks, output_dir is the symlink directory
        organizer = FileOrganizer(
            csv_file=csv_file,
            source_dir=source_dir,
            symlink_dir=output_dir,
            final_export_dir=output_dir  # Not used in this case
        )
        organizer.create_symlinks(hierarchy_columns, file_path_column)
        print("\n✅ Symlink structure created successfully in:", output_dir)
    else:
        # If copying files, create a temporary symlink directory
        temp_symlink_dir = os.path.join(os.path.dirname(output_dir), ".temp_symlinks")
        organizer = FileOrganizer(
            csv_file=csv_file,
            source_dir=source_dir,
            symlink_dir=temp_symlink_dir,
            final_export_dir=output_dir
        )
        organizer.execute(
            hierarchy_columns=hierarchy_columns,
            file_path_column=file_path_column,
            rsync_options=rsync_options,
            prompt_before_rsync=False
        )

        # Clean up temporary symlink directory
        try:
            import shutil
            shutil.rmtree(temp_symlink_dir)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove temporary symlink directory: {e}")


# File Tree Browsing Functions

def get_directory_contents(path: str) -> List[Dict[str, Any]]:
    """
    Get the contents of a directory.

    Args:
        path: Path to the directory.

    Returns:
        List of dictionaries containing information about each item in the directory.
        Each dictionary has the following keys:
        - name: Name of the item
        - path: Full path to the item
        - type: Type of the item (file or directory)
        - size: Size of the item in bytes (for files only)
        - modified: Last modified time of the item as a formatted string
        - is_readable: Whether the item can be read as a spreadsheet or table
    """
    contents = []

    try:
        # Get all items in the directory
        items = os.listdir(path)

        # Sort items: directories first, then files, both alphabetically
        dirs = []
        files = []

        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)

        # Sort directories and files alphabetically
        dirs.sort()
        files.sort()

        # Add directories to contents
        for item in dirs:
            item_path = os.path.join(path, item)
            stat = os.stat(item_path)
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            contents.append({
                "name": item,
                "path": item_path,
                "type": "directory",
                "size": None,
                "modified": modified_time,
                "is_readable": False
            })

        # Add files to contents
        for item in files:
            item_path = os.path.join(path, item)
            stat = os.stat(item_path)
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            contents.append({
                "name": item,
                "path": item_path,
                "type": "file",
                "size": stat.st_size,
                "modified": modified_time,
                "is_readable": is_readable_file(item_path)
            })

        return contents
    except Exception as e:
        print(f"Error getting directory contents: {e}")
        return []


def is_readable_file(file_path: str) -> bool:
    """
    Check if a file can be read as a spreadsheet or table.

    Args:
        file_path: Path to the file.

    Returns:
        True if the file can be read as a spreadsheet or table, False otherwise.
    """
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.csv', '.xlsx', '.xls', '.tsv', '.json', '.db', '.sqlite', '.sqlite3']


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file.

    Args:
        file_path: Path to the file.

    Returns:
        Dictionary containing information about the file.
    """
    try:
        stat = os.stat(file_path)
        modified_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "type": "file",
            "size": stat.st_size,
            "modified": modified_time,
            "is_readable": is_readable_file(file_path)
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {}


# Spreadsheet/Table Reading Functions

def read_file_as_dataframe(file_path: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Read a file as a pandas DataFrame.

    Args:
        file_path: Path to the file.

    Returns:
        Tuple containing:
        - Pandas DataFrame containing the file data, or None if the file could not be read.
        - Error message if the file could not be read, or empty string if successful.
    """
    try:
        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()

        # Read file based on extension
        if ext == '.csv':
            df = pd.read_csv(file_path)
            return df, ""
        elif ext == '.xlsx' or ext == '.xls':
            df = pd.read_excel(file_path)
            return df, ""
        elif ext == '.tsv':
            df = pd.read_csv(file_path, sep='\t')
            return df, ""
        elif ext == '.json':
            df = pd.read_json(file_path)
            return df, ""
        elif ext in ['.db', '.sqlite', '.sqlite3']:
            import sqlite3
            conn = sqlite3.connect(file_path)
            # Get list of tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                # Read first table
                table_name = tables[0][0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
                return df, ""
            else:
                conn.close()
                return None, "No tables found in the database"
        else:
            return None, f"Unsupported file extension: {ext}"
    except Exception as e:
        return None, f"Error reading file: {e}"


def get_file_preview(file_path: str, max_rows: int = 5) -> Dict[str, Any]:
    """
    Get a preview of a file as a pandas DataFrame.

    Args:
        file_path: Path to the file.
        max_rows: Maximum number of rows to include in the preview.

    Returns:
        Dictionary containing:
        - success: True if the file was successfully read, False otherwise.
        - data: JSON-serializable representation of the DataFrame, or None if the file could not be read.
        - error: Error message if the file could not be read, or empty string if successful.
    """
    df, error = read_file_as_dataframe(file_path)

    if df is not None:
        # Get preview of DataFrame
        preview_df = df.head(max_rows)

        # Convert to JSON-serializable format
        preview_data = {
            "columns": preview_df.columns.tolist(),
            "data": preview_df.values.tolist(),
            "total_rows": len(df),
            "preview_rows": len(preview_df)
        }

        return {
            "success": True,
            "data": preview_data,
            "error": ""
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": error
        }


# File Compression/Extraction Functions

def is_archive_file(file_path: str) -> bool:
    """
    Check if a file is an archive (zip, tar, etc.).

    Args:
        file_path: Path to the file.

    Returns:
        True if the file is an archive, False otherwise.
    """
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.zip', '.tar', '.gz', '.tgz', '.bz2', '.tbz2', '.xz', '.txz']


def get_archive_type(file_path: str) -> str:
    """
    Get the type of archive file.

    Args:
        file_path: Path to the archive file.

    Returns:
        String indicating the archive type ('zip', 'tar', 'gzip', 'bzip2', 'xz', or 'unknown').
    """
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()

    # Check for double extensions like .tar.gz
    if ext == '.gz' or ext == '.bz2' or ext == '.xz':
        base_name = os.path.splitext(os.path.splitext(file_path)[0])[0]
        if base_name.endswith('.tar'):
            if ext == '.gz':
                return 'tar_gzip'
            elif ext == '.bz2':
                return 'tar_bzip2'
            elif ext == '.xz':
                return 'tar_xz'

    # Check for single extensions
    if ext == '.zip':
        return 'zip'
    elif ext == '.tar':
        return 'tar'
    elif ext == '.gz':
        return 'gzip'
    elif ext == '.tgz':
        return 'tar_gzip'
    elif ext == '.bz2':
        return 'bzip2'
    elif ext == '.tbz2':
        return 'tar_bzip2'
    elif ext == '.xz':
        return 'xz'
    elif ext == '.txz':
        return 'tar_xz'
    else:
        return 'unknown'


def compress_files(
    files: List[str], 
    output_path: str, 
    archive_type: str = 'zip',
    compression_level: int = 9,
    include_base_dir: bool = False
) -> Tuple[bool, str]:
    """
    Compress files or directories into an archive.

    Args:
        files: List of file or directory paths to compress.
        output_path: Path where the archive will be created.
        archive_type: Type of archive to create ('zip', 'tar', 'tar_gzip', 'tar_bzip2', 'tar_xz').
        compression_level: Compression level (0-9, where 9 is highest compression).
        include_base_dir: Whether to include the base directory in the archive.

    Returns:
        Tuple containing:
        - Success flag (True if compression was successful, False otherwise).
        - Error message if compression failed, or empty string if successful.
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Create appropriate archive based on type
        if archive_type == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                for file_path in tqdm(files, desc="Compressing files"):
                    if os.path.isdir(file_path):
                        # Walk directory and add all files
                        for root, _, files_in_dir in os.walk(file_path):
                            for file in files_in_dir:
                                file_to_add = os.path.join(root, file)
                                # Determine arcname (path within the archive)
                                if include_base_dir:
                                    arcname = os.path.relpath(file_to_add, os.path.dirname(file_path))
                                else:
                                    arcname = os.path.relpath(file_to_add, file_path)
                                    if arcname == '.':
                                        arcname = os.path.basename(file_path)
                                zipf.write(file_to_add, arcname)
                    else:
                        # Add single file
                        if include_base_dir:
                            arcname = os.path.basename(file_path)
                        else:
                            arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)

        elif archive_type.startswith('tar'):
            # Determine compression mode
            if archive_type == 'tar':
                mode = 'w'
            elif archive_type == 'tar_gzip':
                mode = 'w:gz'
            elif archive_type == 'tar_bzip2':
                mode = 'w:bz2'
            elif archive_type == 'tar_xz':
                mode = 'w:xz'
            else:
                return False, f"Unsupported tar archive type: {archive_type}"

            with tarfile.open(output_path, mode) as tarf:
                for file_path in tqdm(files, desc="Compressing files"):
                    if os.path.isdir(file_path):
                        # Add directory recursively
                        base_dir = os.path.basename(file_path)
                        if include_base_dir:
                            tarf.add(file_path, arcname=base_dir)
                        else:
                            # Add contents of directory without the base directory
                            for item in os.listdir(file_path):
                                tarf.add(os.path.join(file_path, item), arcname=item)
                    else:
                        # Add single file
                        if include_base_dir:
                            arcname = os.path.basename(file_path)
                        else:
                            arcname = os.path.basename(file_path)
                        tarf.add(file_path, arcname=arcname)

        else:
            return False, f"Unsupported archive type: {archive_type}"

        return True, ""

    except Exception as e:
        return False, f"Error compressing files: {str(e)}"


def extract_archive(
    archive_path: str, 
    output_dir: str,
    specific_files: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Extract files from an archive.

    Args:
        archive_path: Path to the archive file.
        output_dir: Directory where files will be extracted.
        specific_files: Optional list of specific files to extract. If None, all files are extracted.

    Returns:
        Tuple containing:
        - Success flag (True if extraction was successful, False otherwise).
        - Error message if extraction failed, or empty string if successful.
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Determine archive type
        archive_type = get_archive_type(archive_path)

        # Extract based on archive type
        if archive_type == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                if specific_files:
                    # Extract specific files
                    for file in tqdm(specific_files, desc="Extracting files"):
                        zipf.extract(file, output_dir)
                else:
                    # Extract all files
                    for file in tqdm(zipf.namelist(), desc="Extracting files"):
                        zipf.extract(file, output_dir)

        elif archive_type.startswith('tar'):
            with tarfile.open(archive_path, 'r:*') as tarf:
                if specific_files:
                    # Extract specific files
                    for file in tqdm(specific_files, desc="Extracting files"):
                        tarf.extract(file, output_dir)
                else:
                    # Extract all files
                    tarf.extractall(output_dir, members=tqdm(tarf.getmembers(), desc="Extracting files"))

        else:
            return False, f"Unsupported archive type: {archive_type}"

        return True, ""

    except Exception as e:
        return False, f"Error extracting archive: {str(e)}"


def list_archive_contents(archive_path: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    List the contents of an archive file.

    Args:
        archive_path: Path to the archive file.

    Returns:
        Tuple containing:
        - List of dictionaries with information about each file in the archive.
          Each dictionary has keys: name, size, modified, is_dir
        - Error message if listing failed, or empty string if successful.
    """
    try:
        contents = []
        archive_type = get_archive_type(archive_path)

        if archive_type == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                for info in zipf.infolist():
                    contents.append({
                        "name": info.filename,
                        "size": info.file_size,
                        "modified": datetime.datetime(*info.date_time).strftime('%Y-%m-%d %H:%M:%S'),
                        "is_dir": info.filename.endswith('/')
                    })

        elif archive_type.startswith('tar'):
            with tarfile.open(archive_path, 'r:*') as tarf:
                for info in tarf.getmembers():
                    contents.append({
                        "name": info.name,
                        "size": info.size,
                        "modified": datetime.datetime.fromtimestamp(info.mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        "is_dir": info.isdir()
                    })

        else:
            return [], f"Unsupported archive type: {archive_type}"

        return contents, ""

    except Exception as e:
        return [], f"Error listing archive contents: {str(e)}"
