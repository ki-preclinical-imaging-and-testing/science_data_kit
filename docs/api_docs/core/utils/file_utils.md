# file_utils.py - File Utilities

This module provides utilities for organizing and managing files, including creating structured directory hierarchies and copying files.

## Classes

### FileOrganizer

A utility class for organizing files based on a CSV file with hierarchy information.

This class helps organize files by creating a structured directory hierarchy using symlinks based on columns in a CSV file, and then optionally copying the real files to a final destination using rsync.

#### Constructor

```python
def __init__(
    csv_file: Union[str, Path], 
    source_dir: Union[str, Path], 
    symlink_dir: Union[str, Path], 
    final_export_dir: Union[str, Path]
) -> None
```

**Parameters:**
- `csv_file` (Union[str, Path]): Path to the CSV containing file paths and hierarchy columns.
- `source_dir` (Union[str, Path]): Original directory where files are located.
- `symlink_dir` (Union[str, Path]): Directory where symlinked structure will be created.
- `final_export_dir` (Union[str, Path]): Directory where real files will be copied using rsync.

#### Attributes

- `csv_file` (str): Path to the CSV containing file paths and hierarchy columns.
- `source_dir` (str): Original directory where files are located.
- `symlink_dir` (str): Directory where symlinked structure will be created.
- `final_export_dir` (str): Directory where real files will be copied using rsync.
- `df` (pd.DataFrame): DataFrame containing the CSV data.
- `total_files` (int): Total number of files to process.

#### Methods

##### create_symlinks

```python
def create_symlinks(
    self, 
    hierarchy_columns: Optional[List[str]] = None,
    file_path_column: str = "filepath"
) -> None
```

Create a structured directory with symlinks based on CSV data.

This method reads the CSV file and creates a directory structure based on the hierarchy columns, with symlinks pointing to the original files.

**Parameters:**
- `hierarchy_columns` (Optional[List[str]]): List of column names to use for the hierarchy. If None, defaults to ["col1", "col2", "col3"].
- `file_path_column` (str): Name of the column containing the file paths. Defaults to "filepath".

##### run_rsync

```python
def run_rsync(self, rsync_options: Optional[List[str]] = None) -> int
```

Run rsync to copy the real files from the symlink structure.

This method uses rsync to copy the real files from the symlink structure to the final export directory.

**Parameters:**
- `rsync_options` (Optional[List[str]]): Additional options to pass to rsync. If None, defaults to ["-av", "--copy-links"].

**Returns:**
- The return code from the rsync process (0 for success).

##### execute

```python
def execute(
    self, 
    hierarchy_columns: Optional[List[str]] = None,
    file_path_column: str = "filepath",
    rsync_options: Optional[List[str]] = None,
    prompt_before_rsync: bool = True
) -> None
```

Execute the full pipeline: create symlinks and run rsync.

**Parameters:**
- `hierarchy_columns` (Optional[List[str]]): List of column names to use for the hierarchy. If None, defaults to ["col1", "col2", "col3"].
- `file_path_column` (str): Name of the column containing the file paths. Defaults to "filepath".
- `rsync_options` (Optional[List[str]]): Additional options to pass to rsync. If None, defaults to ["-av", "--copy-links"].
- `prompt_before_rsync` (bool): Whether to prompt the user before running rsync. Defaults to True.

## Functions

### organize_files

```python
def organize_files(
    csv_file: Union[str, Path], 
    source_dir: Union[str, Path], 
    output_dir: Union[str, Path],
    hierarchy_columns: Optional[List[str]] = None,
    file_path_column: str = "filepath",
    use_symlinks: bool = False,
    rsync_options: Optional[List[str]] = None
) -> None
```

Organize files based on a CSV file with hierarchy information.

This is a convenience function that wraps the FileOrganizer class.

**Parameters:**
- `csv_file` (Union[str, Path]): Path to the CSV containing file paths and hierarchy columns.
- `source_dir` (Union[str, Path]): Original directory where files are located.
- `output_dir` (Union[str, Path]): Directory where the organized files will be placed.
- `hierarchy_columns` (Optional[List[str]]): List of column names to use for the hierarchy. If None, defaults to ["col1", "col2", "col3"].
- `file_path_column` (str): Name of the column containing the file paths. Defaults to "filepath".
- `use_symlinks` (bool): Whether to create symlinks instead of copying files. Defaults to False.
- `rsync_options` (Optional[List[str]]): Additional options to pass to rsync if copying files. If None, defaults to ["-av", "--copy-links"].

## Examples

### Using FileOrganizer

```python
from science_data_kit.core.utils.file_utils import FileOrganizer

# Create a FileOrganizer instance
organizer = FileOrganizer(
    csv_file="metadata.csv",
    source_dir="/path/to/source",
    symlink_dir="/path/to/symlinks",
    final_export_dir="/path/to/final"
)

# Create symlinks based on hierarchy columns
organizer.create_symlinks(
    hierarchy_columns=["project", "sample", "experiment"],
    file_path_column="file_path"
)

# Run rsync to copy files
return_code = organizer.run_rsync()

# Or execute the full pipeline
organizer.execute(
    hierarchy_columns=["project", "sample", "experiment"],
    file_path_column="file_path",
    prompt_before_rsync=True
)
```

### Using organize_files

```python
from science_data_kit.core.utils.file_utils import organize_files

# Create symlinks only
organize_files(
    csv_file="metadata.csv",
    source_dir="/path/to/source",
    output_dir="/path/to/symlinks",
    hierarchy_columns=["project", "sample", "experiment"],
    file_path_column="file_path",
    use_symlinks=True
)

# Copy files (create symlinks and run rsync)
organize_files(
    csv_file="metadata.csv",
    source_dir="/path/to/source",
    output_dir="/path/to/final",
    hierarchy_columns=["project", "sample", "experiment"],
    file_path_column="file_path",
    use_symlinks=False,
    rsync_options=["-av", "--copy-links", "--progress"]
)
```

### Example CSV Format

```
project,sample,experiment,file_path
Project1,Sample1,Exp1,data/file1.txt
Project1,Sample1,Exp2,data/file2.txt
Project1,Sample2,Exp1,data/file3.txt
Project2,Sample3,Exp1,data/file4.txt
```

This CSV would create a directory structure like:

```
Project1/
  Sample1/
    Exp1/
      file1.txt
    Exp2/
      file2.txt
  Sample2/
    Exp1/
      file3.txt
Project2/
  Sample3/
    Exp1/
      file4.txt
```