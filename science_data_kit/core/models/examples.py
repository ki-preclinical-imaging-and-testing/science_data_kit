"""
Examples of using entity schemas and validation utilities.

This module provides examples of how to use the entity schemas and validation utilities
in the Science Data Kit.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

from science_data_kit.core.models.entity_schemas import (
    BaseEntity, Dataset, File, Entity, Relationship, OntologyTerm, validate_entity
)
from science_data_kit.core.utils.schema_validation import (
    validate_schema, validate_json_schema, validate_type,
    email_validator, url_validator, uuid_validator,
    validate_date_format, validate_enum, validate_range, validate_length
)


def create_example_dataset() -> Dataset:
    """
    Creates an example Dataset object.

    Returns:
        A Dataset object with example data.
    """
    return Dataset(
        id="dataset-001",
        name="Example Dataset",
        description="This is an example dataset for demonstration purposes.",
        path="/path/to/dataset",
        files=["file1.csv", "file2.txt", "file3.json"],
        metadata={
            "author": "John Doe",
            "created": "2023-01-01",
            "version": "1.0",
            "tags": ["example", "demo", "test"]
        }
    )


def create_example_file() -> File:
    """
    Creates an example File object.

    Returns:
        A File object with example data.
    """
    return File(
        id="file-001",
        name="example.csv",
        path="/path/to/dataset/example.csv",
        size=1024,
        format="csv",
        dataset_id="dataset-001",
        metadata={
            "columns": ["id", "name", "value"],
            "rows": 100,
            "encoding": "utf-8"
        }
    )


def create_example_entity() -> Entity:
    """
    Creates an example Entity object.

    Returns:
        An Entity object with example data.
    """
    return Entity(
        id="entity-001",
        name="Example Entity",
        label="ExampleLabel",
        description="This is an example entity for demonstration purposes.",
        source="dataset-001",
        relationships=[
            {"target_id": "entity-002", "type": "RELATED_TO"},
            {"target_id": "entity-003", "type": "DEPENDS_ON"}
        ]
    )


def create_example_relationship() -> Relationship:
    """
    Creates an example Relationship object.

    Returns:
        A Relationship object with example data.
    """
    return Relationship(
        source_id="entity-001",
        target_id="entity-002",
        type="RELATED_TO",
        properties={
            "weight": 0.8,
            "since": "2023-01-01"
        }
    )


def create_example_ontology_term() -> OntologyTerm:
    """
    Creates an example OntologyTerm object.

    Returns:
        An OntologyTerm object with example data.
    """
    return OntologyTerm(
        id="term-001",
        term="Example Term",
        term_accession="http://example.org/terms/example",
        term_source="Example Ontology",
        definition="This is an example term for demonstration purposes."
    )


def example_entity_validation() -> List[str]:
    """
    Demonstrates how to validate an entity against its schema.

    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    # Create an example entity
    entity = create_example_entity()

    # Validate the entity
    errors = validate_entity(entity, Entity)

    # Print the result
    if errors:
        print("Validation failed with the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Validation passed!")

    return errors


def example_schema_validation() -> List[str]:
    """
    Demonstrates how to validate a dictionary against a schema.

    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    # Create a dictionary representing a dataset
    data = {
        "id": "dataset-002",
        "name": "Another Dataset",
        "description": "This is another example dataset.",
        "path": "/path/to/another/dataset",
        "files": ["file1.csv", "file2.txt"],
        "metadata": {
            "author": "Jane Smith",
            "created": "2023-02-01",
            "version": "1.1"
        }
    }

    # Validate the dictionary against the Dataset schema
    errors = validate_schema(data, Dataset)

    # Print the result
    if errors:
        print("Schema validation failed with the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("Schema validation passed!")

    return errors


def example_json_validation() -> List[str]:
    """
    Demonstrates how to validate a JSON string against a schema.

    Returns:
        A list of validation errors, or an empty list if validation passes.
    """
    # Create a JSON string representing a file
    json_data = """
    {
        "id": "file-002",
        "name": "another.txt",
        "path": "/path/to/another/dataset/another.txt",
        "size": 512,
        "format": "txt",
        "dataset_id": "dataset-002",
        "metadata": {
            "encoding": "utf-8",
            "lines": 50
        }
    }
    """

    # Validate the JSON string against the File schema
    errors = validate_json_schema(json_data, File)

    # Print the result
    if errors:
        print("JSON validation failed with the following errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("JSON validation passed!")

    return errors


def example_common_validators() -> None:
    """
    Demonstrates how to use the common validators.
    """
    # Email validation
    email = "user@example.com"
    email_errors = email_validator(email)
    print(f"Email '{email}': {'Valid' if not email_errors else 'Invalid'}")

    # URL validation
    url = "https://example.com/path?query=value"
    url_errors = url_validator(url)
    print(f"URL '{url}': {'Valid' if not url_errors else 'Invalid'}")

    # UUID validation
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    uuid_errors = uuid_validator(uuid)
    print(f"UUID '{uuid}': {'Valid' if not uuid_errors else 'Invalid'}")

    # Date format validation
    date = "2023-01-01"
    date_errors = validate_date_format(date)
    print(f"Date '{date}': {'Valid' if not date_errors else 'Invalid'}")

    # Enum validation
    value = "apple"
    allowed_values = ["apple", "banana", "orange"]
    enum_errors = validate_enum(value, allowed_values)
    print(f"Value '{value}' in {allowed_values}: {'Valid' if not enum_errors else 'Invalid'}")

    # Range validation
    number = 42
    range_errors = validate_range(number, min_value=0, max_value=100)
    print(f"Number {number} in range [0, 100]: {'Valid' if not range_errors else 'Invalid'}")

    # Length validation
    text = "Hello, world!"
    length_errors = validate_length(text, min_length=5, max_length=20)
    print(f"Text '{text}' length in range [5, 20]: {'Valid' if not length_errors else 'Invalid'}")


def example_ontology_operations():
    """
    Demonstrates how to use the ontology-related methods in Neo4jManager.

    This example shows how to:
    1. Create example ontology terms
    2. Load ontology terms into Neo4j
    3. Summarize available ontology terms in Neo4j
    4. Create relationships between ontology terms

    Note: This example requires a running Neo4j instance.
    """
    try:
        from science_data_kit.core.db.db_manager import Neo4jManager

        # Create a Neo4jManager instance
        db_manager = Neo4jManager()

        # Check if connected to Neo4j
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Please start a Neo4j instance and try again.")
            return

        # Create example ontology terms
        terms = [
            OntologyTerm(
                id="term-001",
                term="Glucose",
                term_accession="http://purl.obolibrary.org/obo/CHEBI_17234",
                term_source="CHEBI",
                definition="A monosaccharide that has a role as a human metabolite."
            ),
            OntologyTerm(
                id="term-002",
                term="Fructose",
                term_accession="http://purl.obolibrary.org/obo/CHEBI_28645",
                term_source="CHEBI",
                definition="A ketohexose that is the 2-ketose of glucose."
            ),
            OntologyTerm(
                id="term-003",
                term="Sucrose",
                term_accession="http://purl.obolibrary.org/obo/CHEBI_17992",
                term_source="CHEBI",
                definition="A disaccharide consisting of glucose and fructose units linked via their anomeric carbons."
            ),
            OntologyTerm(
                id="term-004",
                term="Mass Spectrometry",
                term_accession="http://purl.obolibrary.org/obo/MS_1000443",
                term_source="MS",
                definition="A technique used to measure the mass-to-charge ratio of ions."
            )
        ]

        # Load ontology terms into Neo4j
        print("Loading ontology terms into Neo4j...")
        result = db_manager.load_ontology_terms(terms)
        print(f"Loaded {result['terms_created']} new terms and updated {result['terms_updated']} existing terms.")
        print(f"Created {result['relationships_created']} relationships between terms.")

        # Summarize available ontology terms in Neo4j
        print("\nSummarizing ontology terms in Neo4j...")

        # Standard format
        standard_summary = db_manager.summarize_ontology_terms(format_type="standard")
        print(f"Found {standard_summary['total_ontology_properties']} ontology properties across {standard_summary['total_labels']} labels.")

        # Compact format
        compact_summary = db_manager.summarize_ontology_terms(format_type="compact")
        for label, properties in compact_summary.items():
            print(f"Label '{label}' has {len(properties)} ontology properties: {', '.join(properties)}")

        # Create OntologyAnnotation objects for demonstration
        try:
            from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation

            class OntologySource:
                def __init__(self, name, version=None, description=None):
                    self.name = name
                    self.version = version
                    self.description = description

            annotations = [
                OntologyAnnotation(
                    term="Metabolomics",
                    term_accession="http://purl.obolibrary.org/obo/NCIT_C16974",
                    term_source=OntologySource(
                        name="NCIT",
                        version="4.0",
                        description="National Cancer Institute Thesaurus"
                    )
                ),
                OntologyAnnotation(
                    term="Proteomics",
                    term_accession="http://purl.obolibrary.org/obo/NCIT_C20085",
                    term_source=OntologySource(
                        name="NCIT",
                        version="4.0",
                        description="National Cancer Institute Thesaurus"
                    )
                )
            ]

            # Load ontology relationships into Neo4j
            print("\nLoading ontology relationships into Neo4j...")
            rel_result = db_manager.load_ontology_relationships(
                annotations,
                create_source_nodes=True,
                relationship_type="HAS_TERM",
                additional_term_properties={"term_accession": "uri"}
            )

            print(f"Loaded {rel_result['terms_created']} new terms and {rel_result['sources_created']} new sources.")
            print(f"Created {rel_result['relationships_created']} relationships between sources and terms.")

        except ImportError:
            print("\nIsatools compatibility layer not available. Skipping OntologyAnnotation example.")

    except ImportError:
        print("Neo4jManager not available. Make sure science_data_kit is properly installed.")
    except Exception as e:
        print(f"Error during ontology operations: {str(e)}")


if __name__ == "__main__":
    # Run the examples
    print("Entity Validation Example:")
    example_entity_validation()
    print("\nSchema Validation Example:")
    example_schema_validation()
    print("\nJSON Validation Example:")
    example_json_validation()
    print("\nCommon Validators Example:")
    example_common_validators()
    print("\nOntology Operations Example:")
    example_ontology_operations()
