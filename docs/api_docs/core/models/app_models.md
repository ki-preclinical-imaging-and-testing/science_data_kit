# app_models.py - Application Models

This module provides utilities for working with Neo4j models using neomodel. It includes functions for mapping Neo4j types to neomodel property types, initializing neomodel classes dynamically, and merging nodes with existing nodes.

## Functions

### type_mapping

```python
def type_mapping(neo_type: str) -> Optional[Type]
```

Maps Neo4j types to neomodel property types.

**Parameters:**
- `neo_type` (str): The Neo4j type to map.

**Returns:**
- The corresponding neomodel property type, or None if not found.

### initialize_neomodel_classes

```python
def initialize_neomodel_classes(
    neomodel_map: Dict[str, Dict[str, str]], 
    rel_pair: Tuple[str, str] = ('has_parent', 'HAS_PARENT')
) -> Dict[str, Type[StructuredNode]]
```

Dynamically creates neomodel classes based on a mapping.

**Parameters:**
- `neomodel_map` (Dict[str, Dict[str, str]]): A dictionary mapping label names to property dictionaries. Each property dictionary maps property names to Neo4j types.
- `rel_pair` (Tuple[str, str], optional): A tuple containing (relationship_name, relationship_type). Defaults to ('has_parent', 'HAS_PARENT').

**Returns:**
- A dictionary mapping label names to neomodel classes.

### print_neomodel_map

```python
def print_neomodel_map(neomodel_map: Dict[str, Dict[str, str]]) -> None
```

Prints a neomodel map for debugging.

**Parameters:**
- `neomodel_map` (Dict[str, Dict[str, str]]): A dictionary mapping label names to property dictionaries.

### generate_neomodel_map

```python
def generate_neomodel_map(property_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, str]]
```

Generates a neomodel map from a property map.

**Parameters:**
- `property_map` (Dict[str, Dict[str, Any]]): A dictionary mapping label names to property dictionaries.

**Returns:**
- A dictionary mapping label names to property type dictionaries.

### test_labels_for_neomodel_class_availability

```python
def test_labels_for_neomodel_class_availability(samples_df: pd.DataFrame) -> Dict[str, bool]
```

Tests if neomodel classes are available for given labels.

**Parameters:**
- `samples_df` (pd.DataFrame): A DataFrame containing a 'label' column.

**Returns:**
- A dictionary mapping label names to availability status.

### merge_nodes_with_existing

```python
def merge_nodes_with_existing(
    db_connection: Any,
    entities_df: pd.DataFrame,
    label_column: str,
    property_columns: List[str],
    target_label: str,
    match_columns: List[str],
    relationship_type: str,
    source_to_target_map: Optional[Dict[str, str]] = None
) -> None
```

Merge new nodes with existing nodes in Neo4j.

**Parameters:**
- `db_connection` (Any): Neo4j database connection.
- `entities_df` (pd.DataFrame): DataFrame containing entities to be merged.
- `label_column` (str): Column specifying the node label for each entity.
- `property_columns` (List[str]): Columns to be included as properties in the node.
- `target_label` (str): Label of the target nodes to match against.
- `match_columns` (List[str]): Columns used to match existing nodes.
- `relationship_type` (str): Type of relationship to create between nodes.
- `source_to_target_map` (Dict[str, str], optional): Optional dictionary mapping source property names to target property names.

### create_default_models

```python
def create_default_models() -> Dict[str, Type[StructuredNode]]
```

Creates default models for the application.

**Returns:**
- A dictionary mapping label names to neomodel classes.

## Examples

### Mapping Neo4j Types to Neomodel Property Types

```python
from science_data_kit.core.models.app_models import type_mapping

# Map Neo4j types to neomodel property types
string_property = type_mapping("String")
integer_property = type_mapping("Integer")
date_property = type_mapping("Date")
```

### Dynamically Creating Neomodel Classes

```python
from science_data_kit.core.models.app_models import initialize_neomodel_classes

# Define a neomodel map
neomodel_map = {
    "Person": {
        "name": "String",
        "age": "Integer",
        "birth_date": "Date"
    },
    "Movie": {
        "title": "String",
        "year": "Integer"
    }
}

# Initialize neomodel classes
classes = initialize_neomodel_classes(neomodel_map)

# Use the dynamically created classes
person = classes["Person"](name="John Doe", age=30).save()
movie = classes["Movie"](title="The Matrix", year=1999).save()

# Create a relationship
person.has_parent.connect(movie)
```

### Merging Nodes with Existing Nodes

```python
import pandas as pd
from science_data_kit.core.models.app_models import merge_nodes_with_existing
from science_data_kit.core.db.db_manager import db_manager

# Create a DataFrame with entities to merge
data = {
    "label": ["Person", "Person", "Movie"],
    "name": ["Alice", "Bob", "The Matrix"],
    "age": [30, 25, None],
    "year": [None, None, 1999]
}
df = pd.DataFrame(data)

# Merge nodes with existing nodes
merge_nodes_with_existing(
    db_connection=db_manager._driver,
    entities_df=df,
    label_column="label",
    property_columns=["name", "age", "year"],
    target_label="Person",
    match_columns=["name"],
    relationship_type="ACTED_IN",
    source_to_target_map={"name": "title"}
)
```

### Using Default Models

```python
from science_data_kit.core.models.app_models import create_default_models

# Get default models
models = create_default_models()

# Use the Folder and File models
folder = models["Folder"](filepath="/path/to/folder").save()
file = models["File"](filepath="/path/to/file.txt").save()

# Create a relationship
file.is_in.connect(folder)
```