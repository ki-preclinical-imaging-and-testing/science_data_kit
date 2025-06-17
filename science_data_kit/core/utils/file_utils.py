"""
File Utilities for Science Data Kit

This module provides utilities for organizing and managing files, including
creating structured directory hierarchies and copying files.
"""

import os
import subprocess
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
import pandas as pd
from tqdm import tqdm


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