# Data Transformation Guide

## Overview

The Science Data Kit provides powerful data transformation capabilities that allow you to convert data from various sources into a knowledge graph format. This guide explains how to use the SDK's data transformation pipelines to process and transform your data.

## Table of Contents

1. [Introduction](#introduction)
2. [Pipeline Configuration](#pipeline-configuration)
3. [Tabular Data Mapping](#tabular-data-mapping)
4. [File Tree Processing](#file-tree-processing)
5. [Data Validation](#data-validation)
6. [Pipeline Templates](#pipeline-templates)
7. [Advanced Transformations](#advanced-transformations)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

Data transformation is a critical step in the data analysis process. The Science Data Kit provides a flexible pipeline-based approach to data transformation, allowing you to:

- Convert tabular data (CSV, Excel) into nodes and relationships for a knowledge graph
- Process directory structures and file metadata
- Validate data against a set of rules
- Use templates for common transformation scenarios

The transformation process typically involves the following steps:

1. Configure a transformation pipeline
2. Define mapping rules for your data
3. Apply validation rules
4. Execute the pipeline
5. Review and analyze the transformed data

## Pipeline Configuration

Transformation pipelines in the Science Data Kit are defined using a configuration format that specifies the input data, transformation steps, and output format.

### Basic Pipeline Configuration

Here's an example of a basic pipeline configuration:

```python
from science_data_kit.core.transform import Pipeline, TabularDataSource, Neo4jSink

# Create a pipeline
pipeline = Pipeline(
    name="Sample Pipeline",
    description="A sample pipeline that transforms CSV data into a knowledge graph"
)

# Add a data source
csv_source = TabularDataSource(
    name="Sample CSV",
    file_path="path/to/your/data.csv",
    has_header=True
)
pipeline.add_source(csv_source)

# Add transformation steps (will be covered in later sections)
# ...

# Add a data sink (output)
neo4j_sink = Neo4jSink(
    name="Neo4j Database",
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)
pipeline.add_sink(neo4j_sink)

# Execute the pipeline
result = pipeline.execute()
print(f"Pipeline execution result: {result.success}")
if not result.success:
    print(f"Error: {result.error_message}")
```

### Pipeline Components

A pipeline consists of the following components:

- **Sources**: Define where the data comes from (e.g., CSV file, Excel file, database)
- **Transformers**: Define how the data is transformed (e.g., mapping, filtering, aggregation)
- **Validators**: Define rules for validating the data
- **Sinks**: Define where the transformed data goes (e.g., Neo4j database, file)

### Pipeline Configuration Options

The `Pipeline` class supports the following configuration options:

- `name`: A name for the pipeline
- `description`: A description of what the pipeline does
- `max_errors`: The maximum number of errors allowed before the pipeline fails (default: 0)
- `continue_on_error`: Whether to continue execution when errors occur (default: False)
- `log_level`: The logging level for the pipeline (default: INFO)

## Tabular Data Mapping

Tabular data mapping allows you to convert tabular data (CSV, Excel) into nodes and relationships for a knowledge graph.

### Basic Mapping

Here's an example of a basic mapping configuration:

```python
from science_data_kit.core.transform import TabularMapping, NodeMapping, RelationshipMapping

# Create a mapping for the CSV data
mapping = TabularMapping(
    name="Person Mapping",
    description="Maps CSV data to Person nodes"
)

# Define node mapping
person_mapping = NodeMapping(
    label="Person",
    properties={
        "name": "Name",  # Maps the "Name" column to the "name" property
        "age": "Age",    # Maps the "Age" column to the "age" property
        "email": "Email" # Maps the "Email" column to the "email" property
    },
    primary_key="email"  # Use the "email" property as the primary key
)
mapping.add_node_mapping(person_mapping)

# Add the mapping to the pipeline
pipeline.add_transformer(mapping)
```

### Relationship Mapping

You can also map relationships between nodes:

```python
# Define relationship mapping
works_for_mapping = RelationshipMapping(
    type="WORKS_FOR",
    source_node=person_mapping,  # Source node mapping
    target_node_label="Company",  # Target node label
    target_node_properties={
        "name": "Company"  # Maps the "Company" column to the "name" property
    },
    target_node_primary_key="name"  # Use the "name" property as the primary key
)
mapping.add_relationship_mapping(works_for_mapping)
```

### Property Transformations

You can transform properties during the mapping process:

```python
from science_data_kit.core.transform import PropertyTransformer

# Define a property transformer
class UppercaseTransformer(PropertyTransformer):
    def transform(self, value):
        if isinstance(value, str):
            return value.upper()
        return value

# Apply the transformer to a property
person_mapping.add_property_transformer("name", UppercaseTransformer())
```

## File Tree Processing

File tree processing allows you to process directory structures and file metadata, creating nodes for directories and files and relationships between them.

### Basic File Tree Processing

Here's an example of basic file tree processing:

```python
from science_data_kit.core.transform import FileTreeProcessor, FileTreeSource

# Create a file tree source
file_tree_source = FileTreeSource(
    name="Sample File Tree",
    root_path="path/to/your/directory",
    include_patterns=["*.csv", "*.xlsx"],  # Only include CSV and Excel files
    exclude_patterns=["*temp*"]  # Exclude temporary files
)

# Create a file tree processor
file_tree_processor = FileTreeProcessor(
    name="File Tree Processor",
    create_directory_nodes=True,  # Create nodes for directories
    create_file_nodes=True,  # Create nodes for files
    extract_metadata=True  # Extract metadata from files
)

# Add the source and processor to the pipeline
pipeline.add_source(file_tree_source)
pipeline.add_transformer(file_tree_processor)
```

### File Metadata Extraction

The file tree processor can extract metadata from files:

```python
# Configure metadata extraction
file_tree_processor.configure_metadata_extraction(
    extract_creation_time=True,
    extract_modification_time=True,
    extract_size=True,
    extract_mime_type=True,
    extract_custom_metadata=True
)

# Add custom metadata extractors
from science_data_kit.core.transform import MetadataExtractor

class CSVRowCountExtractor(MetadataExtractor):
    def can_extract(self, file_path):
        return file_path.endswith(".csv")
    
    def extract(self, file_path):
        with open(file_path, 'r') as f:
            return {"row_count": sum(1 for line in f)}

file_tree_processor.add_metadata_extractor(CSVRowCountExtractor())
```

## Data Validation

Data validation allows you to validate data against a set of rules to ensure data quality before further processing or loading into a knowledge graph.

### Basic Validation

Here's an example of basic data validation:

```python
from science_data_kit.core.transform import Validator, ValidationRule

# Create a validator
validator = Validator(
    name="Data Validator",
    description="Validates the transformed data"
)

# Add validation rules
validator.add_rule(
    ValidationRule(
        name="Age Range Check",
        description="Checks that age is between 18 and 100",
        entity_type="Person",
        property_name="age",
        rule_type="range",
        parameters={"min": 18, "max": 100}
    )
)

validator.add_rule(
    ValidationRule(
        name="Email Format Check",
        description="Checks that email is in a valid format",
        entity_type="Person",
        property_name="email",
        rule_type="regex",
        parameters={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
    )
)

# Add the validator to the pipeline
pipeline.add_validator(validator)
```

### Custom Validation Rules

You can create custom validation rules:

```python
from science_data_kit.core.transform import CustomValidationRule

class UniqueEmailRule(CustomValidationRule):
    def __init__(self):
        super().__init__(
            name="Unique Email Rule",
            description="Checks that email addresses are unique"
        )
        self.emails = set()
    
    def validate(self, entity):
        if entity.get("label") == "Person" and "email" in entity.get("properties", {}):
            email = entity["properties"]["email"]
            if email in self.emails:
                return False, f"Duplicate email: {email}"
            self.emails.add(email)
        return True, None

validator.add_rule(UniqueEmailRule())
```

## Pipeline Templates

The Science Data Kit provides templates for common data transformation scenarios.

### Using a Template

Here's an example of using a template:

```python
from science_data_kit.core.transform.templates import CSVToGraphTemplate

# Create a pipeline from a template
pipeline = CSVToGraphTemplate.create_pipeline(
    csv_file_path="path/to/your/data.csv",
    node_label="Person",
    property_mappings={
        "name": "Name",
        "age": "Age",
        "email": "Email"
    },
    primary_key="email",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    neo4j_database="neo4j"
)

# Execute the pipeline
result = pipeline.execute()
```

### Available Templates

The SDK includes the following templates:

- **CSVToGraphTemplate**: Converts CSV data to a graph
- **ExcelToGraphTemplate**: Converts Excel data to a graph
- **FileTreeToGraphTemplate**: Converts a file tree to a graph
- **JSONToGraphTemplate**: Converts JSON data to a graph
- **XMLToGraphTemplate**: Converts XML data to a graph

## Advanced Transformations

The Science Data Kit supports advanced transformation scenarios.

### Data Aggregation

You can aggregate data during the transformation process:

```python
from science_data_kit.core.transform import AggregationTransformer

# Create an aggregation transformer
aggregator = AggregationTransformer(
    name="Age Aggregator",
    description="Aggregates ages by company"
)

# Configure the aggregation
aggregator.configure(
    group_by_entity="Company",
    group_by_property="name",
    target_entity="Person",
    target_property="age",
    aggregation_type="average",
    output_property="average_age"
)

# Add the aggregator to the pipeline
pipeline.add_transformer(aggregator)
```

### Data Filtering

You can filter data during the transformation process:

```python
from science_data_kit.core.transform import FilterTransformer

# Create a filter transformer
filter = FilterTransformer(
    name="Adult Filter",
    description="Filters out persons under 18"
)

# Configure the filter
filter.configure(
    entity_type="Person",
    property_name="age",
    operator=">=",
    value=18
)

# Add the filter to the pipeline
pipeline.add_transformer(filter)
```

### Data Enrichment

You can enrich data during the transformation process:

```python
from science_data_kit.core.transform import EnrichmentTransformer

# Create an enrichment transformer
enricher = EnrichmentTransformer(
    name="Location Enricher",
    description="Adds location data to companies"
)

# Configure the enrichment
enricher.configure(
    entity_type="Company",
    property_name="name",
    lookup_service="location_service",
    lookup_parameters={"api_key": "your_api_key"},
    output_properties=["city", "country", "latitude", "longitude"]
)

# Add the enricher to the pipeline
pipeline.add_transformer(enricher)
```

## Best Practices

Here are some best practices for using the data transformation capabilities of the Science Data Kit:

1. **Start Simple**: Begin with simple transformations and gradually add complexity.
2. **Use Templates**: Use templates for common transformation scenarios to save time.
3. **Validate Early**: Validate your data early in the pipeline to catch issues before they propagate.
4. **Monitor Performance**: Monitor the performance of your pipelines and optimize as needed.
5. **Document Your Pipelines**: Document your pipelines to make them easier to understand and maintain.
6. **Use Transactions**: Use transactions when writing to databases to ensure data consistency.
7. **Handle Errors**: Implement proper error handling to make your pipelines more robust.
8. **Test Thoroughly**: Test your pipelines with various data scenarios to ensure they work correctly.

## Troubleshooting

Here are some common issues and their solutions:

### Pipeline Execution Fails

- **Issue**: The pipeline execution fails with an error.
  - **Solution**: Check the error message and logs for details. Common issues include invalid file paths, missing data, or validation failures.

### Mapping Issues

- **Issue**: The mapping doesn't produce the expected nodes or relationships.
  - **Solution**: Verify that your column names match the mapping configuration. Check that your primary keys are unique.

### Performance Issues

- **Issue**: The pipeline is slow to execute.
  - **Solution**: Consider optimizing your transformations, using batch processing, or implementing parallel processing for large datasets.

### Memory Issues

- **Issue**: The pipeline runs out of memory.
  - **Solution**: Process data in smaller batches or implement streaming processing for large datasets.

If you encounter other issues, please refer to the SDK documentation or contact support.