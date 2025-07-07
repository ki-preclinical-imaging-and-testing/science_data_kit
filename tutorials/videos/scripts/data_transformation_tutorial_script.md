# Data Transformation Tutorial Script

## Introduction (0:00-0:30)
Hello and welcome to this video tutorial on data transformation in the Science Data Kit. In this tutorial, we'll explore how to use the data transformation functionality to convert data between different formats, validate data against rules, and prepare it for analysis and visualization.

## Prerequisites (0:30-1:00)
Before we begin, make sure you have:
- The Science Data Kit installed
- Basic knowledge of Python and pandas
- Familiarity with data structures like DataFrames and graphs

If you need help setting these up, please refer to our installation guide in the documentation.

## Overview of Data Transformation (1:00-2:00)
The Science Data Kit provides several powerful tools for data transformation:

1. **TabularDataMapper**: Transforms tabular data (like pandas DataFrames) into graph structures
2. **FileTreeProcessor**: Transforms file system directory structures into graph representations
3. **DataValidator**: Validates data against a set of rules and handles validation errors
4. **PipelineConfig**: Configures and manages complex transformation pipelines

These tools help you prepare your data for analysis, visualization, and storage in graph databases like Neo4j.

## Tabular Data Mapping (2:00-5:30)

### Creating a Sample DataFrame (2:00-2:30)
Let's start by creating a sample DataFrame that we'll transform:

```python
import pandas as pd
import numpy as np
from science_data_kit.core.pipeline.config import (
    PipelineConfig, TransformationStep, MappingRule,
    NodeLabelStrategy, RelationshipStrategy, StepType
)
from science_data_kit.core.pipeline.transform import (
    TabularDataMapper, FileTreeProcessor, DataValidator
)

# Create a sample DataFrame
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45],
    'department': ['HR', 'IT', 'Finance', 'IT', 'HR'],
    'manager_id': [None, 1, 1, 2, 3]
}
df = pd.DataFrame(data)

print("Sample DataFrame:")
print(df)
```

### Defining Mapping Rules (2:30-3:30)
Now, let's define mapping rules to specify how DataFrame columns should be mapped to node properties:

```python
# Create mapping rules
mapping_rules = [
    MappingRule(
        source_field="id",
        target_field="id",
        data_type="int"
    ),
    MappingRule(
        source_field="name",
        target_field="name",
        data_type="string"
    ),
    MappingRule(
        source_field="age",
        target_field="age",
        data_type="int"
    ),
    MappingRule(
        source_field="department",
        target_field="department",
        data_type="string"
    )
]
```

These rules specify which columns from the DataFrame should be included in the transformed data and what data types they should have.

### Creating a TabularDataMapper with Fixed Node Labels (3:30-4:30)
Let's create a TabularDataMapper with fixed node labels:

```python
# Create a TabularDataMapper with fixed node labels
mapper = TabularDataMapper(
    node_label_strategy=NodeLabelStrategy.FIXED,
    node_label_config={"label": "Person"},
    relationship_strategy=RelationshipStrategy.FIELD_REFERENCE,
    relationship_config={
        "source_field": "id",
        "target_field": "manager_id",
        "relationship_type": "REPORTS_TO"
    },
    mapping_rules=mapping_rules
)

# Transform the data
result = mapper.transform(df)

print("Transformation Result:")
print(f"Number of nodes: {len(result['nodes'])}")
print(f"Number of relationships: {len(result['relationships'])}")

# Print a sample node and relationship
if result['nodes']:
    print("\nSample Node:")
    print(result['nodes'][0])

if result['relationships']:
    print("\nSample Relationship:")
    print(result['relationships'][0])
```

This creates a graph structure where each row in the DataFrame becomes a node with the label "Person", and relationships are created based on the manager_id field.

### Using Field-Based Node Labels (4:30-5:30)
We can also use field-based node labels, where the label for each node is determined by a field in the DataFrame:

```python
# Create a TabularDataMapper with field-based node labels
field_mapper = TabularDataMapper(
    node_label_strategy=NodeLabelStrategy.FIELD_BASED,
    node_label_config={"field": "department"},
    relationship_strategy=RelationshipStrategy.FIELD_REFERENCE,
    relationship_config={
        "source_field": "id",
        "target_field": "manager_id",
        "relationship_type": "REPORTS_TO"
    },
    mapping_rules=mapping_rules
)

# Transform the data
field_result = field_mapper.transform(df)

print("Field-Based Transformation Result:")
print(f"Number of nodes: {len(field_result['nodes'])}")
print(f"Number of relationships: {len(field_result['relationships'])}")

# Print a sample node to show the different label
if field_result['nodes']:
    print("\nSample Node with Field-Based Label:")
    print(field_result['nodes'][0])
```

With field-based node labels, each node gets a label based on the value in the "department" column, so we have nodes labeled "HR", "IT", and "Finance".

## File Tree Processing (5:30-8:30)

### Creating a Sample File Structure (5:30-6:30)
Let's create a sample file structure that we'll transform into a graph:

```python
import os
import tempfile

# Create a temporary directory for file examples
TEMP_DIR = tempfile.mkdtemp()

# Create a sample file structure
os.makedirs(os.path.join(TEMP_DIR, "docs"), exist_ok=True)
os.makedirs(os.path.join(TEMP_DIR, "src", "components"), exist_ok=True)
os.makedirs(os.path.join(TEMP_DIR, "tests"), exist_ok=True)

# Create some sample files
with open(os.path.join(TEMP_DIR, "README.md"), "w") as f:
    f.write("# Sample Project\n\nThis is a sample project for the tutorial.")

with open(os.path.join(TEMP_DIR, "docs", "index.md"), "w") as f:
    f.write("# Documentation\n\nThis is the documentation index.")

with open(os.path.join(TEMP_DIR, "src", "main.py"), "w") as f:
    f.write("print('Hello, world!')")

with open(os.path.join(TEMP_DIR, "src", "components", "component1.py"), "w") as f:
    f.write("class Component1:\n    pass")

with open(os.path.join(TEMP_DIR, "tests", "test_main.py"), "w") as f:
    f.write("def test_main():\n    assert True")

print(f"Created sample file structure in {TEMP_DIR}")
```

### Creating a FileTreeProcessor (6:30-7:30)
Now, let's create a FileTreeProcessor to transform this file structure into a graph:

```python
# Create a FileTreeProcessor
processor = FileTreeProcessor(
    root_path=TEMP_DIR,
    file_node_label="File",
    directory_node_label="Directory",
    contains_relationship_type="CONTAINS",
    file_extensions=[".py", ".md"],
    max_depth=3,
    include_hidden=False,
    compute_checksums=True,
    extract_metadata=True
)
```

### Processing the File Tree (7:30-8:30)
Let's process the file tree and examine the results:

```python
# Process the file tree
result = processor.transform()

print("File Tree Processing Result:")
print(f"Number of nodes: {len(result['nodes'])}")
print(f"Number of relationships: {len(result['relationships'])}")

# Print a sample directory node
directory_nodes = [node for node in result['nodes'] if node['labels'] == ['Directory']]
if directory_nodes:
    print("\nSample Directory Node:")
    print(directory_nodes[0])

# Print a sample file node
file_nodes = [node for node in result['nodes'] if node['labels'] == ['File']]
if file_nodes:
    print("\nSample File Node:")
    print(file_nodes[0])

# Print a sample relationship
if result['relationships']:
    print("\nSample Relationship:")
    print(result['relationships'][0])
```

This creates a graph structure where directories and files are represented as nodes, and the directory structure is represented by "CONTAINS" relationships.

## Data Validation (8:30-11:30)

### Creating a Sample DataFrame with Invalid Data (8:30-9:15)
Let's create a sample DataFrame with some invalid data that we'll validate:

```python
# Create a sample DataFrame with some invalid data
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', '', 'David', 'Eve'],
    'age': [25, -30, 35, 400, 45],
    'email': ['alice@example.com', 'bob@example', 'charlie@example.com', 'david@example.com', 'eve@example.com']
}
df = pd.DataFrame(data)

print("Sample DataFrame with Invalid Data:")
print(df)
```

This DataFrame has several issues:
- An empty name (row 3)
- Negative and unrealistically high ages (rows 2 and 4)
- An invalid email format (row 2)

### Creating a DataValidator with Validation Rules (9:15-10:15)
Let's create a DataValidator with rules to catch these issues:

```python
# Create a DataValidator
validator = DataValidator()

# Add validation rules
validator.add_rule(
    DataValidator.ValidationRule(
        name="name_not_empty",
        field="name",
        condition=lambda x: x and len(str(x).strip()) > 0,
        error_message="Name cannot be empty",
        severity="error",
        action="reject"
    )
)

validator.add_rule(
    DataValidator.ValidationRule(
        name="age_range",
        field="age",
        condition=lambda x: 0 <= x <= 120,
        error_message="Age must be between 0 and 120",
        severity="error",
        action="fix",
        fix_function=lambda x: max(0, min(x, 120))
    )
)

validator.add_rule(
    DataValidator.ValidationRule(
        name="valid_email",
        field="email",
        condition=lambda x: "@" in str(x) and "." in str(x).split("@")[1],
        error_message="Invalid email format",
        severity="warning",
        action="flag"
    )
)
```

These rules define conditions that the data must meet, error messages for when they don't, and actions to take (reject, fix, or flag).

### Validating the Data (10:15-11:30)
Now, let's validate the data and examine the results:

```python
# Validate the data
result = validator.transform(df)

print("Validation Results:")
validation_results = validator.get_validation_results()

print(f"Total validation issues: {len(validation_results)}")

# Print validation issues
for i, issue in enumerate(validation_results):
    print(f"\nIssue {i+1}:")
    print(f"  Rule: {issue['rule_name']}")
    print(f"  Field: {issue['field']}")
    print(f"  Message: {issue['message']}")
    print(f"  Severity: {issue['severity']}")
    print(f"  Action: {issue['action']}")
    print(f"  Row: {issue['row_index']}")

# Print the transformed data
print("\nTransformed Data (after validation and fixes):")
print(result)
```

The validation process identifies the issues in our data and takes the specified actions:
- Rejects the row with an empty name
- Fixes the negative and unrealistically high ages
- Flags the invalid email format

## Pipeline Configuration (11:30-14:00)

### Creating a PipelineConfig (11:30-12:30)
Let's create a PipelineConfig to manage a complex transformation pipeline:

```python
# Create a PipelineConfig
pipeline_config = PipelineConfig(
    name="Sample Data Pipeline",
    description="A sample data transformation pipeline for the tutorial",
    version="1.0.0",
    steps=[]
)
```

### Adding Transformation Steps (12:30-13:30)
Now, let's add transformation steps to the pipeline:

```python
# Add a tabular data mapping step
mapping_step = TransformationStep(
    name="Map Employee Data",
    description="Map employee data to a graph structure",
    step_type=StepType.TABULAR_MAPPING,
    config={
        "node_label_strategy": "FIXED",
        "node_label_config": {"label": "Person"},
        "relationship_strategy": "FIELD_REFERENCE",
        "relationship_config": {
            "source_field": "id",
            "target_field": "manager_id",
            "relationship_type": "REPORTS_TO"
        },
        "mapping_rules": [
            {
                "source_field": "id",
                "target_field": "id",
                "data_type": "int"
            },
            {
                "source_field": "name",
                "target_field": "name",
                "data_type": "string"
            },
            {
                "source_field": "age",
                "target_field": "age",
                "data_type": "int"
            },
            {
                "source_field": "department",
                "target_field": "department",
                "data_type": "string"
            }
        ]
    }
)

pipeline_config.add_step(mapping_step)

# Add a data validation step
validation_step = TransformationStep(
    name="Validate Employee Data",
    description="Validate employee data against rules",
    step_type=StepType.DATA_VALIDATION,
    config={
        "validation_rules": [
            {
                "name": "name_not_empty",
                "field": "name",
                "condition": "lambda x: x and len(str(x).strip()) > 0",
                "error_message": "Name cannot be empty",
                "severity": "error",
                "action": "reject"
            },
            {
                "name": "age_range",
                "field": "age",
                "condition": "lambda x: 0 <= x <= 120",
                "error_message": "Age must be between 0 and 120",
                "severity": "error",
                "action": "fix",
                "fix_function": "lambda x: max(0, min(x, 120))"
            }
        ]
    }
)

pipeline_config.add_step(validation_step)

# Add a file tree processing step
file_tree_step = TransformationStep(
    name="Process Project Files",
    description="Process project files into a graph structure",
    step_type=StepType.FILE_TREE_PROCESSING,
    config={
        "root_path": TEMP_DIR,
        "file_node_label": "File",
        "directory_node_label": "Directory",
        "contains_relationship_type": "CONTAINS",
        "file_extensions": [".py", ".md"],
        "max_depth": 3,
        "include_hidden": False,
        "compute_checksums": True,
        "extract_metadata": True
    }
)

pipeline_config.add_step(file_tree_step)
```

### Saving and Loading the Pipeline Configuration (13:30-14:00)
We can save the pipeline configuration to a file and load it back:

```python
# Save the pipeline configuration to a file
config_file = os.path.join(TEMP_DIR, "pipeline_config.json")
pipeline_config.save(config_file)

print(f"Saved pipeline configuration to {config_file}")

# Load the pipeline configuration from the file
loaded_config = PipelineConfig.load(config_file)

print("Loaded Pipeline Configuration:")
print(f"Name: {loaded_config.name}")
print(f"Description: {loaded_config.description}")
print(f"Version: {loaded_config.version}")
print(f"Number of steps: {len(loaded_config.steps)}")

# Verify that the loaded configuration matches the original
print("\nVerification:")
print(f"Names match: {loaded_config.name == pipeline_config.name}")
print(f"Descriptions match: {loaded_config.description == pipeline_config.description}")
print(f"Versions match: {loaded_config.version == pipeline_config.version}")
print(f"Number of steps match: {len(loaded_config.steps) == len(pipeline_config.steps)}")
```

This allows you to save complex transformation pipelines and reuse them later.

## Conclusion (14:00-14:30)
In this tutorial, we've explored the data transformation functionality in the Science Data Kit:

1. **Tabular Data Mapping**: Converting tabular data to graph structures with TabularDataMapper
2. **File Tree Processing**: Transforming file system structures to graphs with FileTreeProcessor
3. **Data Validation**: Validating data against rules with DataValidator
4. **Pipeline Configuration**: Managing complex transformation pipelines with PipelineConfig

These tools help you prepare your data for analysis, visualization, and storage in graph databases. By transforming your data into appropriate formats and validating it against rules, you can ensure that your analyses are based on clean, well-structured data.

Thank you for watching this tutorial. For more information, please refer to the documentation and other tutorials in the Science Data Kit.