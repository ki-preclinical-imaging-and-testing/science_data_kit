# file_models.py - File System Models

This module defines the core file and folder models used throughout the application. It serves as the single source of truth for these models to prevent duplicate class definitions.

## Classes

### Folder

Represents a folder in the file system.

#### Properties

- `uid` (UniqueIdProperty): A unique identifier for the folder.
- `filepath` (StringProperty): The path to the folder in the file system. This property has a unique index.

#### Relationships

- `is_in` (RelationshipTo): A relationship to another Folder, indicating that this folder is contained within another folder.

### File

Represents a file in the file system.

#### Properties

- `uid` (UniqueIdProperty): A unique identifier for the file.
- `filepath` (StringProperty): The path to the file in the file system. This property has a unique index.

#### Relationships

- `is_in` (RelationshipTo): A relationship to a Folder, indicating that this file is contained within a folder.

## Examples

### Creating Folders and Files

```python
from science_data_kit.core.models.file_models import Folder, File

# Create a folder
root_folder = Folder(filepath="/path/to/root").save()

# Create a subfolder
subfolder = Folder(filepath="/path/to/root/subfolder").save()

# Create a file in the subfolder
file = File(filepath="/path/to/root/subfolder/example.txt").save()

# Establish relationships
subfolder.is_in.connect(root_folder)
file.is_in.connect(subfolder)
```

### Querying Folders and Files

```python
from science_data_kit.core.models.file_models import Folder, File

# Find a folder by filepath
folder = Folder.nodes.get(filepath="/path/to/root")

# Get all files in a folder
files_in_folder = File.nodes.filter(is_in=folder)

# Find a file by filepath
file = File.nodes.get(filepath="/path/to/root/subfolder/example.txt")

# Get the parent folder of a file
parent_folder = file.is_in.all()[0]
```