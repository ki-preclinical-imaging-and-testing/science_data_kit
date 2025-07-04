"""
Data Transformation Tutorial for Science Data Kit

This tutorial demonstrates how to use the data transformation functionality
in the Science Data Kit, including pipeline configuration, tabular data mapping,
file tree processing, and data validation.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

from science_data_kit.core.pipeline.config import (
    PipelineConfig, TransformationStep, MappingRule,
    NodeLabelStrategy, RelationshipStrategy, StepType
)
from science_data_kit.core.pipeline.transform import (
    TabularDataMapper, FileTreeProcessor, DataValidator
)
from science_data_kit.core.db.db_manager import Neo4jManager

# Create a temporary directory for file examples
TEMP_DIR = tempfile.mkdtemp()


def example_tabular_data_mapping():
    """
    Example of mapping tabular data to a graph structure.
    
    This function demonstrates how to use the TabularDataMapper to transform
    tabular data (like pandas DataFrames) into a graph structure suitable
    for import into Neo4j.
    """
    print("\n=== Tabular Data Mapping Example ===\n")
    
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
    print()
    
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
    print()
    
    # Print the first node and relationship
    if result['nodes']:
        print("Sample Node:")
        print(result['nodes'][0])
        print()
    
    if result['relationships']:
        print("Sample Relationship:")
        print(result['relationships'][0])
        print()
    
    # Example of using field-based node labels
    print("Example with Field-Based Node Labels:")
    
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
    
    print(f"Number of nodes: {len(field_result['nodes'])}")
    print(f"Number of relationships: {len(field_result['relationships'])}")
    print()
    
    # Print a sample node to show the different label
    if field_result['nodes']:
        print("Sample Node with Field-Based Label:")
        print(field_result['nodes'][0])
        print()
    
    return result


def example_file_tree_processing():
    """
    Example of processing a file tree to create a graph structure.
    
    This function demonstrates how to use the FileTreeProcessor to transform
    a file system directory structure into a graph representation.
    """
    print("\n=== File Tree Processing Example ===\n")
    
    # Create a sample file structure in the temporary directory
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
    print()
    
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
    
    # Process the file tree
    result = processor.transform()
    
    print("File Tree Processing Result:")
    print(f"Number of nodes: {len(result['nodes'])}")
    print(f"Number of relationships: {len(result['relationships'])}")
    print()
    
    # Print a sample directory node
    directory_nodes = [node for node in result['nodes'] if node['labels'] == ['Directory']]
    if directory_nodes:
        print("Sample Directory Node:")
        print(directory_nodes[0])
        print()
    
    # Print a sample file node
    file_nodes = [node for node in result['nodes'] if node['labels'] == ['File']]
    if file_nodes:
        print("Sample File Node:")
        print(file_nodes[0])
        print()
    
    # Print a sample relationship
    if result['relationships']:
        print("Sample Relationship:")
        print(result['relationships'][0])
        print()
    
    return result


def example_data_validation():
    """
    Example of validating data against a set of rules.
    
    This function demonstrates how to use the DataValidator to validate
    data against a set of rules and handle validation errors.
    """
    print("\n=== Data Validation Example ===\n")
    
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
    print()
    
    # Create a DataValidator with validation rules
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
    
    # Validate the data
    result = validator.transform(df)
    
    print("Validation Results:")
    validation_results = validator.get_validation_results()
    
    print(f"Total validation issues: {len(validation_results)}")
    print()
    
    # Print validation issues
    for i, issue in enumerate(validation_results):
        print(f"Issue {i+1}:")
        print(f"  Rule: {issue['rule_name']}")
        print(f"  Field: {issue['field']}")
        print(f"  Message: {issue['message']}")
        print(f"  Severity: {issue['severity']}")
        print(f"  Action: {issue['action']}")
        print(f"  Row: {issue['row_index']}")
        print()
    
    # Print the transformed data
    print("Transformed Data (after validation and fixes):")
    print(result)
    print()
    
    return result


def example_pipeline_configuration():
    """
    Example of creating and using a pipeline configuration.
    
    This function demonstrates how to create a PipelineConfig object,
    add transformation steps, save it to a file, and load it back.
    """
    print("\n=== Pipeline Configuration Example ===\n")
    
    # Create a PipelineConfig
    pipeline_config = PipelineConfig(
        name="Sample Data Pipeline",
        description="A sample data transformation pipeline for the tutorial",
        version="1.0.0",
        steps=[]
    )
    
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
    
    # Add a data validation step
    validation_step = TransformationStep(
        name="Validate Employee Data",
        description="Validate employee data against business rules",
        step_type=StepType.DATA_VALIDATION,
        config={
            "rules": [
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
    
    # Add the steps to the pipeline
    pipeline_config.steps.append(mapping_step)
    pipeline_config.steps.append(validation_step)
    
    # Convert to dictionary and print
    config_dict = pipeline_config.to_dict()
    print("Pipeline Configuration Dictionary:")
    print(config_dict)
    print()
    
    # Save to a YAML file
    yaml_file = os.path.join(TEMP_DIR, "pipeline_config.yaml")
    pipeline_config.save(yaml_file)
    print(f"Saved pipeline configuration to {yaml_file}")
    print()
    
    # Load from the YAML file
    loaded_config = PipelineConfig.load(yaml_file)
    print("Loaded Pipeline Configuration:")
    print(f"Name: {loaded_config.name}")
    print(f"Description: {loaded_config.description}")
    print(f"Version: {loaded_config.version}")
    print(f"Number of steps: {len(loaded_config.steps)}")
    print()
    
    # Print the first step
    if loaded_config.steps:
        print("First Step:")
        print(f"Name: {loaded_config.steps[0].name}")
        print(f"Description: {loaded_config.steps[0].description}")
        print(f"Type: {loaded_config.steps[0].step_type}")
        print()
    
    return loaded_config


def example_neo4j_import():
    """
    Example of importing transformed data into Neo4j.
    
    This function demonstrates how to use the Neo4jManager to import
    transformed data into a Neo4j database.
    """
    print("\n=== Neo4j Import Example ===\n")
    
    # Check if Neo4j is available
    try:
        # Create a Neo4jManager
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping Neo4j import example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Create a sample DataFrame
        data = {
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 40, 45],
            'department': ['HR', 'IT', 'Finance', 'IT', 'HR'],
            'manager_id': [None, 1, 1, 2, 3]
        }
        df = pd.DataFrame(data)
        
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
        
        # Create a TabularDataMapper
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
        
        # Import nodes into Neo4j
        print("Importing nodes into Neo4j...")
        for node in result['nodes']:
            properties = node['properties']
            labels = node['labels']
            
            # Create Cypher query
            query = f"CREATE (n:{':'.join(labels)} $properties)"
            
            # Execute query
            db_manager.execute_query(query, {"properties": properties})
        
        print(f"Imported {len(result['nodes'])} nodes.")
        print()
        
        # Import relationships into Neo4j
        print("Importing relationships into Neo4j...")
        for rel in result['relationships']:
            source_id = rel['source_id']
            target_id = rel['target_id']
            rel_type = rel['type']
            properties = rel.get('properties', {})
            
            # Create Cypher query
            query = """
            MATCH (source:Person {id: $source_id})
            MATCH (target:Person {id: $target_id})
            CREATE (source)-[r:%s $properties]->(target)
            """ % rel_type
            
            # Execute query
            db_manager.execute_query(
                query, 
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "properties": properties
                }
            )
        
        print(f"Imported {len(result['relationships'])} relationships.")
        print()
        
        # Query the data to verify import
        print("Verifying import with a query...")
        query = "MATCH (n:Person) RETURN n.name AS name, n.age AS age, n.department AS department"
        result = db_manager.query_to_dataframe(query)
        
        print("Query Result:")
        print(result)
        print()
        
        # Clean up
        print("Cleaning up imported data...")
        db_manager.execute_query("MATCH (n:Person) DETACH DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in Neo4j import example: {e}")
        print("Skipping Neo4j import example.")
    
    return


def run_tutorial():
    """Run all examples in the tutorial."""
    print("=== Data Transformation Tutorial ===")
    print("This tutorial demonstrates how to use the data transformation functionality")
    print("in the Science Data Kit, including pipeline configuration, tabular data mapping,")
    print("file tree processing, and data validation.")
    print()
    
    # Run the examples
    example_tabular_data_mapping()
    example_file_tree_processing()
    example_data_validation()
    example_pipeline_configuration()
    example_neo4j_import()
    
    # Clean up
    print("\n=== Cleaning Up ===\n")
    import shutil
    shutil.rmtree(TEMP_DIR)
    print(f"Removed temporary directory: {TEMP_DIR}")
    print()
    
    print("Tutorial complete!")


if __name__ == "__main__":
    run_tutorial()