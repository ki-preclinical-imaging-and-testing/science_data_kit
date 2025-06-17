"""
Unit tests for the entity_schemas module.

This module contains tests for the entity schemas defined in science_data_kit.core.models.entity_schemas.
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any

from science_data_kit.core.models.entity_schemas import (
    BaseEntity, Dataset, File, Entity, Relationship, OntologyTerm, validate_entity
)


@pytest.mark.unit
class TestBaseEntity:
    """Tests for the BaseEntity class."""

    def test_create_base_entity(self):
        """Test creating a BaseEntity instance."""
        entity = BaseEntity(id="test-id")
        
        assert entity.id == "test-id"
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
        assert isinstance(entity.properties, dict)
        assert len(entity.properties) == 0

    def test_base_entity_with_properties(self):
        """Test creating a BaseEntity with custom properties."""
        properties = {"key1": "value1", "key2": 123}
        entity = BaseEntity(id="test-id", properties=properties)
        
        assert entity.properties == properties
        assert entity.properties["key1"] == "value1"
        assert entity.properties["key2"] == 123


@pytest.mark.unit
class TestDataset:
    """Tests for the Dataset class."""

    def test_create_dataset(self):
        """Test creating a Dataset instance."""
        dataset = Dataset(id="dataset-001", name="Test Dataset")
        
        assert dataset.id == "dataset-001"
        assert dataset.name == "Test Dataset"
        assert dataset.description == ""
        assert dataset.path == ""
        assert isinstance(dataset.files, list)
        assert len(dataset.files) == 0
        assert isinstance(dataset.metadata, dict)
        assert len(dataset.metadata) == 0

    def test_dataset_with_all_attributes(self):
        """Test creating a Dataset with all attributes."""
        files = ["file1.csv", "file2.txt"]
        metadata = {"author": "Test Author", "date": "2023-01-01"}
        
        dataset = Dataset(
            id="dataset-001",
            name="Test Dataset",
            description="A test dataset",
            path="/path/to/dataset",
            files=files,
            metadata=metadata
        )
        
        assert dataset.id == "dataset-001"
        assert dataset.name == "Test Dataset"
        assert dataset.description == "A test dataset"
        assert dataset.path == "/path/to/dataset"
        assert dataset.files == files
        assert dataset.metadata == metadata


@pytest.mark.unit
class TestFile:
    """Tests for the File class."""

    def test_create_file(self):
        """Test creating a File instance."""
        file = File(id="file-001", name="test.csv", path="/path/to/test.csv")
        
        assert file.id == "file-001"
        assert file.name == "test.csv"
        assert file.path == "/path/to/test.csv"
        assert file.size == 0
        assert file.format == ""
        assert file.dataset_id is None
        assert isinstance(file.metadata, dict)
        assert len(file.metadata) == 0

    def test_file_with_all_attributes(self):
        """Test creating a File with all attributes."""
        metadata = {"columns": ["id", "name"], "rows": 100}
        
        file = File(
            id="file-001",
            name="test.csv",
            path="/path/to/test.csv",
            size=1024,
            format="csv",
            dataset_id="dataset-001",
            metadata=metadata
        )
        
        assert file.id == "file-001"
        assert file.name == "test.csv"
        assert file.path == "/path/to/test.csv"
        assert file.size == 1024
        assert file.format == "csv"
        assert file.dataset_id == "dataset-001"
        assert file.metadata == metadata


@pytest.mark.unit
class TestEntity:
    """Tests for the Entity class."""

    def test_create_entity(self):
        """Test creating an Entity instance."""
        entity = Entity(id="entity-001", name="Test Entity", label="TestLabel")
        
        assert entity.id == "entity-001"
        assert entity.name == "Test Entity"
        assert entity.label == "TestLabel"
        assert entity.description == ""
        assert entity.source == ""
        assert isinstance(entity.relationships, list)
        assert len(entity.relationships) == 0

    def test_entity_with_relationships(self):
        """Test creating an Entity with relationships."""
        relationships = [
            {"target_id": "entity-002", "type": "RELATED_TO"},
            {"target_id": "entity-003", "type": "DEPENDS_ON"}
        ]
        
        entity = Entity(
            id="entity-001",
            name="Test Entity",
            label="TestLabel",
            description="A test entity",
            source="dataset-001",
            relationships=relationships
        )
        
        assert entity.id == "entity-001"
        assert entity.name == "Test Entity"
        assert entity.label == "TestLabel"
        assert entity.description == "A test entity"
        assert entity.source == "dataset-001"
        assert entity.relationships == relationships
        assert len(entity.relationships) == 2
        assert entity.relationships[0]["target_id"] == "entity-002"
        assert entity.relationships[0]["type"] == "RELATED_TO"


@pytest.mark.unit
class TestRelationship:
    """Tests for the Relationship class."""

    def test_create_relationship(self):
        """Test creating a Relationship instance."""
        relationship = Relationship(
            source_id="entity-001",
            target_id="entity-002",
            type="RELATED_TO"
        )
        
        assert relationship.source_id == "entity-001"
        assert relationship.target_id == "entity-002"
        assert relationship.type == "RELATED_TO"
        assert isinstance(relationship.properties, dict)
        assert len(relationship.properties) == 0

    def test_relationship_with_properties(self):
        """Test creating a Relationship with properties."""
        properties = {"weight": 0.8, "since": "2023-01-01"}
        
        relationship = Relationship(
            source_id="entity-001",
            target_id="entity-002",
            type="RELATED_TO",
            properties=properties
        )
        
        assert relationship.source_id == "entity-001"
        assert relationship.target_id == "entity-002"
        assert relationship.type == "RELATED_TO"
        assert relationship.properties == properties
        assert relationship.properties["weight"] == 0.8
        assert relationship.properties["since"] == "2023-01-01"


@pytest.mark.unit
class TestOntologyTerm:
    """Tests for the OntologyTerm class."""

    def test_create_ontology_term(self):
        """Test creating an OntologyTerm instance."""
        term = OntologyTerm(id="term-001", term="Test Term")
        
        assert term.id == "term-001"
        assert term.term == "Test Term"
        assert term.term_accession == ""
        assert term.term_source == ""
        assert term.definition == ""

    def test_ontology_term_with_all_attributes(self):
        """Test creating an OntologyTerm with all attributes."""
        term = OntologyTerm(
            id="term-001",
            term="Test Term",
            term_accession="http://example.org/terms/test",
            term_source="Example Ontology",
            definition="A test ontology term"
        )
        
        assert term.id == "term-001"
        assert term.term == "Test Term"
        assert term.term_accession == "http://example.org/terms/test"
        assert term.term_source == "Example Ontology"
        assert term.definition == "A test ontology term"


@pytest.mark.unit
class TestValidateEntity:
    """Tests for the validate_entity function."""

    def test_validate_valid_entity(self):
        """Test validating a valid entity."""
        entity = Dataset(id="dataset-001", name="Test Dataset")
        errors = validate_entity(entity, Dataset)
        
        assert len(errors) == 0

    def test_validate_invalid_entity(self):
        """Test validating an invalid entity."""
        # Create a BaseEntity but try to validate it as a Dataset
        entity = BaseEntity(id="test-id")
        errors = validate_entity(entity, Dataset)
        
        assert len(errors) > 0
        assert any("Missing required field: name" in error for error in errors)

    def test_validate_entity_with_wrong_type(self):
        """Test validating an entity with a field of the wrong type."""
        # Create a custom class with a name attribute of the wrong type
        class InvalidEntity:
            def __init__(self):
                self.id = "test-id"
                self.name = 123  # Should be a string
        
        entity = InvalidEntity()
        errors = validate_entity(entity, Dataset)
        
        assert len(errors) > 0
        assert any("Field name has invalid type" in error for error in errors)