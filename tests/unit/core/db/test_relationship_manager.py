"""
Unit tests for the relationship_manager module.

This module contains tests for the RelationshipType, RelationshipPattern, and RelationshipManager classes.
"""

import pytest
from unittest.mock import MagicMock, patch
import neo4j
from neo4j.exceptions import Neo4jError

from science_data_kit.core.db.relationship_manager import (
    RelationshipType, RelationshipPattern, RelationshipManager, relationship_manager
)
from science_data_kit.core.db.db_manager import QueryError, ConnectionError


@pytest.fixture
def mock_db_manager():
    """Mock Neo4jManager for testing."""
    mock = MagicMock()
    mock.execute_query.return_value = [{"r": {"property": "value"}}]
    mock.query_to_value.return_value = 10
    return mock


@pytest.fixture
def relationship_type():
    """Create a RelationshipType instance for testing."""
    return RelationshipType(
        name="TEST_RELATIONSHIP",
        description="Test relationship type",
        properties={"test_prop": "test_value"},
        bidirectional=True,
        validators={"test_prop": lambda x: isinstance(x, str)}
    )


@pytest.fixture
def relationship_pattern():
    """Create a RelationshipPattern instance for testing."""
    pattern = RelationshipPattern(
        name="TEST_PATTERN",
        description="Test relationship pattern"
    )
    pattern.add_step(
        source_label="Person",
        relationship_type="KNOWS",
        target_label="Person",
        direction="outgoing",
        properties={"since": 2020}
    )
    return pattern


@pytest.fixture
def relationship_manager_instance(mock_db_manager):
    """Create a RelationshipManager instance for testing."""
    return RelationshipManager(db_manager=mock_db_manager)


class TestRelationshipType:
    """Tests for the RelationshipType class."""

    def test_init(self, relationship_type):
        """Test RelationshipType initialization."""
        assert relationship_type.name == "TEST_RELATIONSHIP"
        assert relationship_type.description == "Test relationship type"
        assert relationship_type.properties == {"test_prop": "test_value"}
        assert relationship_type.bidirectional is True
        assert "test_prop" in relationship_type.validators

    def test_validate_properties_valid(self, relationship_type):
        """Test validate_properties with valid properties."""
        is_valid, errors = relationship_type.validate_properties({"test_prop": "valid_value"})
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_properties_invalid(self, relationship_type):
        """Test validate_properties with invalid properties."""
        is_valid, errors = relationship_type.validate_properties({"test_prop": 123})
        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid value for property test_prop" in errors[0]

    def test_validate_properties_exception(self):
        """Test validate_properties with a validator that raises an exception."""
        def validator(x):
            raise ValueError("Test error")

        rel_type = RelationshipType(
            name="TEST_EXCEPTION",
            validators={"test_prop": validator}
        )

        is_valid, errors = rel_type.validate_properties({"test_prop": "any_value"})
        assert is_valid is False
        assert len(errors) == 1
        assert "Error validating property test_prop" in errors[0]


class TestRelationshipPattern:
    """Tests for the RelationshipPattern class."""

    def test_init(self, relationship_pattern):
        """Test RelationshipPattern initialization."""
        assert relationship_pattern.name == "TEST_PATTERN"
        assert relationship_pattern.description == "Test relationship pattern"
        assert len(relationship_pattern.steps) == 1

    def test_add_step(self, relationship_pattern):
        """Test add_step method."""
        # Add another step
        relationship_pattern.add_step(
            source_label="Person",
            relationship_type="WORKS_FOR",
            target_label="Company",
            direction="outgoing",
            properties={"since": 2021},
            optional=True
        )

        # Check that the step was added
        assert len(relationship_pattern.steps) == 2
        assert relationship_pattern.steps[1]["source_label"] == "Person"
        assert relationship_pattern.steps[1]["relationship_type"] == "WORKS_FOR"
        assert relationship_pattern.steps[1]["target_label"] == "Company"
        assert relationship_pattern.steps[1]["direction"] == "outgoing"
        assert relationship_pattern.steps[1]["properties"] == {"since": 2021}
        assert relationship_pattern.steps[1]["optional"] is True

    def test_to_cypher_empty(self):
        """Test to_cypher method with an empty pattern."""
        pattern = RelationshipPattern("EMPTY")
        with pytest.raises(ValueError):
            pattern.to_cypher()

    def test_to_cypher_single_step(self, relationship_pattern):
        """Test to_cypher method with a single step."""
        query, params = relationship_pattern.to_cypher()

        # Check that the query contains the expected parts
        assert "MATCH (n0:Person)" in query
        assert "MATCH (n0)-[r0:KNOWS]->(n1:Person)" in query
        assert "RETURN n0, n1, r0" in query

        # Check that the parameters contain the expected values
        assert "props0" in params
        assert params["props0"] == {"since": 2020}

    def test_to_cypher_multiple_steps(self):
        """Test to_cypher method with multiple steps."""
        pattern = RelationshipPattern("MULTI_STEP")
        pattern.add_step(
            source_label="Person",
            relationship_type="KNOWS",
            target_label="Person",
            direction="outgoing"
        )
        pattern.add_step(
            source_label="Person",
            relationship_type="WORKS_FOR",
            target_label="Company",
            direction="outgoing",
            optional=True
        )

        query, params = pattern.to_cypher()

        # Check that the query contains the expected parts
        assert "MATCH (n0:Person)" in query
        assert "MATCH (n0)-[r0:KNOWS]->(n1:Person)" in query
        assert "OPTIONAL MATCH (n1)-[r1:WORKS_FOR]->(n2:Company)" in query
        assert "RETURN n0, n1, n2, r0, r1" in query

    def test_to_cypher_different_directions(self):
        """Test to_cypher method with different relationship directions."""
        pattern = RelationshipPattern("DIRECTIONS")
        pattern.add_step(
            source_label="Person",
            relationship_type="KNOWS",
            target_label="Person",
            direction="outgoing"
        )
        pattern.add_step(
            source_label="Person",
            relationship_type="MANAGED_BY",
            target_label="Person",
            direction="incoming"
        )
        pattern.add_step(
            source_label="Person",
            relationship_type="FRIENDS_WITH",
            target_label="Person",
            direction="both"
        )

        query, params = pattern.to_cypher()

        # Check that the query contains the expected parts
        assert "MATCH (n0:Person)" in query
        assert "MATCH (n0)-[r0:KNOWS]->(n1:Person)" in query
        assert "MATCH (n1)<-[r1:MANAGED_BY]-(n2:Person)" in query
        assert "MATCH (n2)-[r2:FRIENDS_WITH]-(n3:Person)" in query


class TestRelationshipManager:
    """Tests for the RelationshipManager class."""

    def test_init(self, mock_db_manager):
        """Test RelationshipManager initialization."""
        manager = RelationshipManager(db_manager=mock_db_manager)
        assert manager.db_manager == mock_db_manager
        assert isinstance(manager._relationship_types, dict)
        assert isinstance(manager._relationship_patterns, dict)

    def test_register_relationship_type(self, relationship_manager_instance, relationship_type):
        """Test register_relationship_type method."""
        relationship_manager_instance.register_relationship_type(relationship_type)
        assert "TEST_RELATIONSHIP" in relationship_manager_instance._relationship_types
        assert relationship_manager_instance._relationship_types["TEST_RELATIONSHIP"] == relationship_type

    def test_register_relationship_type_duplicate(self, relationship_manager_instance, relationship_type):
        """Test register_relationship_type method with a duplicate type."""
        relationship_manager_instance.register_relationship_type(relationship_type)
        with pytest.raises(ValueError):
            relationship_manager_instance.register_relationship_type(relationship_type)

    def test_get_relationship_type(self, relationship_manager_instance, relationship_type):
        """Test get_relationship_type method."""
        relationship_manager_instance.register_relationship_type(relationship_type)
        result = relationship_manager_instance.get_relationship_type("TEST_RELATIONSHIP")
        assert result == relationship_type

    def test_get_relationship_type_not_found(self, relationship_manager_instance):
        """Test get_relationship_type method with a non-existent type."""
        result = relationship_manager_instance.get_relationship_type("NON_EXISTENT")
        assert result is None

    def test_register_relationship_pattern(self, relationship_manager_instance, relationship_pattern):
        """Test register_relationship_pattern method."""
        relationship_manager_instance.register_relationship_pattern(relationship_pattern)
        assert "TEST_PATTERN" in relationship_manager_instance._relationship_patterns
        assert relationship_manager_instance._relationship_patterns["TEST_PATTERN"] == relationship_pattern

    def test_register_relationship_pattern_duplicate(self, relationship_manager_instance, relationship_pattern):
        """Test register_relationship_pattern method with a duplicate pattern."""
        relationship_manager_instance.register_relationship_pattern(relationship_pattern)
        with pytest.raises(ValueError):
            relationship_manager_instance.register_relationship_pattern(relationship_pattern)

    def test_get_relationship_pattern(self, relationship_manager_instance, relationship_pattern):
        """Test get_relationship_pattern method."""
        relationship_manager_instance.register_relationship_pattern(relationship_pattern)
        result = relationship_manager_instance.get_relationship_pattern("TEST_PATTERN")
        assert result == relationship_pattern

    def test_get_relationship_pattern_not_found(self, relationship_manager_instance):
        """Test get_relationship_pattern method with a non-existent pattern."""
        result = relationship_manager_instance.get_relationship_pattern("NON_EXISTENT")
        assert result is None

    def test_create_relationship(self, relationship_manager_instance):
        """Test create_relationship method."""
        result = relationship_manager_instance.create_relationship(
            source_id=1,
            target_id=2,
            relationship_type="KNOWS",
            properties={"since": 2020}
        )
        assert result == {"property": "value"}

        # Check that the query was executed with the correct parameters
        relationship_manager_instance.db_manager.execute_query.assert_called_once()
        args, kwargs = relationship_manager_instance.db_manager.execute_query.call_args
        assert "MATCH (a), (b)" in args[0]
        assert "WHERE id(a) = $source_id AND id(b) = $target_id" in args[0]
        assert "CREATE (a)-[r:`KNOWS`]->(b)" in args[0]
        assert "SET r = $properties" in args[0]
        assert "RETURN r" in args[0]
        assert kwargs["params"]["source_id"] == 1
        assert kwargs["params"]["target_id"] == 2
        assert kwargs["params"]["properties"] == {"since": 2020}

    def test_create_relationship_with_registered_type(self, relationship_manager_instance, relationship_type):
        """Test create_relationship method with a registered relationship type."""
        relationship_manager_instance.register_relationship_type(relationship_type)
        result = relationship_manager_instance.create_relationship(
            source_id=1,
            target_id=2,
            relationship_type="TEST_RELATIONSHIP",
            properties={"test_prop": "custom_value"}
        )
        assert result == {"property": "value"}

        # Check that the properties were merged with the default properties
        args, kwargs = relationship_manager_instance.db_manager.execute_query.call_args
        assert kwargs["params"]["properties"] == {"test_prop": "custom_value"}

    def test_create_relationship_with_invalid_properties(self, relationship_manager_instance, relationship_type):
        """Test create_relationship method with invalid properties."""
        relationship_manager_instance.register_relationship_type(relationship_type)
        with pytest.raises(ValueError):
            relationship_manager_instance.create_relationship(
                source_id=1,
                target_id=2,
                relationship_type="TEST_RELATIONSHIP",
                properties={"test_prop": 123}  # Invalid value (not a string)
            )

    def test_create_relationship_query_error(self, relationship_manager_instance):
        """Test create_relationship method with a query error."""
        relationship_manager_instance.db_manager.execute_query.return_value = []
        with pytest.raises(QueryError):
            relationship_manager_instance.create_relationship(
                source_id=1,
                target_id=2,
                relationship_type="KNOWS"
            )

    def test_create_relationship_by_properties(self, relationship_manager_instance):
        """Test create_relationship_by_properties method."""
        result = relationship_manager_instance.create_relationship_by_properties(
            source_label="Person",
            source_property="name",
            source_value="Alice",
            target_label="Person",
            target_property="name",
            target_value="Bob",
            relationship_type="KNOWS",
            properties={"since": 2020}
        )
        assert result == {"property": "value"}

        # Check that the template was rendered with the correct parameters
        relationship_manager_instance.db_manager.execute_query.assert_called_once()

    def test_get_relationships(self, relationship_manager_instance):
        """Test get_relationships method."""
        relationship_manager_instance.db_manager.execute_query.return_value = [
            {"a": {"name": "Alice"}, "r": {"since": 2020}, "b": {"name": "Bob"}}
        ]
        result = relationship_manager_instance.get_relationships(
            source_label="Person",
            relationship_type="KNOWS",
            target_label="Person",
            limit=10
        )
        assert len(result) == 1
        assert result[0]["source"]["name"] == "Alice"
        assert result[0]["relationship"]["since"] == 2020
        assert result[0]["target"]["name"] == "Bob"

    def test_get_relationship_by_id(self, relationship_manager_instance):
        """Test get_relationship_by_id method."""
        relationship_manager_instance.db_manager.execute_query.return_value = [
            {"a": {"name": "Alice"}, "r": {"since": 2020}, "b": {"name": "Bob"}}
        ]
        result = relationship_manager_instance.get_relationship_by_id(1)
        assert result["source"]["name"] == "Alice"
        assert result["relationship"]["since"] == 2020
        assert result["target"]["name"] == "Bob"

    def test_get_relationship_by_id_not_found(self, relationship_manager_instance):
        """Test get_relationship_by_id method with a non-existent relationship."""
        relationship_manager_instance.db_manager.execute_query.return_value = []
        result = relationship_manager_instance.get_relationship_by_id(999)
        assert result is None

    def test_update_relationship_properties(self, relationship_manager_instance):
        """Test update_relationship_properties method."""
        result = relationship_manager_instance.update_relationship_properties(
            relationship_id=1,
            properties={"since": 2021}
        )
        assert result is True

        # Check that the query was executed with the correct parameters
        relationship_manager_instance.db_manager.execute_query.assert_called_once()
        args, kwargs = relationship_manager_instance.db_manager.execute_query.call_args
        assert "MATCH ()-[r]->()" in args[0]
        assert "WHERE id(r) = $relationship_id" in args[0]
        assert "SET r += $properties" in args[0]
        assert "RETURN r" in args[0]
        assert kwargs["params"]["relationship_id"] == 1
        assert kwargs["params"]["properties"] == {"since": 2021}

    def test_update_relationship_properties_not_found(self, relationship_manager_instance):
        """Test update_relationship_properties method with a non-existent relationship."""
        relationship_manager_instance.db_manager.execute_query.return_value = []
        result = relationship_manager_instance.update_relationship_properties(
            relationship_id=999,
            properties={"since": 2021}
        )
        assert result is False

    def test_delete_relationship(self, relationship_manager_instance):
        """Test delete_relationship method."""
        result = relationship_manager_instance.delete_relationship(1)
        assert result is True

        # Check that the query was executed with the correct parameters
        relationship_manager_instance.db_manager.execute_query.assert_called_once()
        args, kwargs = relationship_manager_instance.db_manager.execute_query.call_args
        assert "MATCH ()-[r]->()" in args[0]
        assert "WHERE id(r) = $relationship_id" in args[0]
        assert "DELETE r" in args[0]
        assert kwargs["params"]["relationship_id"] == 1

    def test_delete_relationship_error(self, relationship_manager_instance):
        """Test delete_relationship method with an error."""
        relationship_manager_instance.db_manager.execute_query.side_effect = QueryError("Test error")
        result = relationship_manager_instance.delete_relationship(1)
        assert result is False

    def test_find_path(self, relationship_manager_instance):
        """Test find_path method."""
        # Mock the path result
        path_result = [{"type": "node", "data": {"name": "Alice"}}, {"type": "relationship", "data": {"since": 2020}}, {"type": "node", "data": {"name": "Bob"}}]
        relationship_manager_instance.db_manager.execute_query.return_value = [{"path": path_result}]

        result = relationship_manager_instance.find_path(
            start_node_id=1,
            end_node_id=2,
            relationship_types=["KNOWS", "WORKS_WITH"],
            max_depth=3
        )

        # Check that the result contains the expected path
        assert len(result) == 3
        assert result[0]["type"] == "node"
        assert result[0]["data"]["name"] == "Alice"
        assert result[1]["type"] == "relationship"
        assert result[1]["data"]["since"] == 2020
        assert result[2]["type"] == "node"
        assert result[2]["data"]["name"] == "Bob"

        # Check that the query was executed with the correct parameters
        relationship_manager_instance.db_manager.execute_query.assert_called_once()
        args, kwargs = relationship_manager_instance.db_manager.execute_query.call_args
        assert "MATCH (start), (end)" in args[0]
        assert "WHERE id(start) = $start_id AND id(end) = $end_id" in args[0]
        assert "MATCH path = shortestPath((start)-[:`KNOWS`|`WORKS_WITH`*1..3]->(end))" in args[0]
        assert "RETURN path" in args[0]
        assert kwargs["params"]["start_id"] == 1
        assert kwargs["params"]["end_id"] == 2

    def test_find_path_not_found(self, relationship_manager_instance):
        """Test find_path method with no path found."""
        relationship_manager_instance.db_manager.execute_query.return_value = []
        result = relationship_manager_instance.find_path(1, 2)
        assert result is None

    def test_execute_pattern(self, relationship_manager_instance, relationship_pattern):
        """Test execute_pattern method."""
        relationship_manager_instance.register_relationship_pattern(relationship_pattern)
        result = relationship_manager_instance.execute_pattern("TEST_PATTERN")
        assert result == [{"r": {"property": "value"}}]

    def test_execute_pattern_not_found(self, relationship_manager_instance):
        """Test execute_pattern method with a non-existent pattern."""
        with pytest.raises(ValueError):
            relationship_manager_instance.execute_pattern("NON_EXISTENT")

    def test_get_relationship_types(self, relationship_manager_instance):
        """Test get_relationship_types method."""
        relationship_manager_instance.db_manager.execute_query.return_value = [
            {"relationshipType": "KNOWS"},
            {"relationshipType": "WORKS_FOR"}
        ]
        result = relationship_manager_instance.get_relationship_types()
        assert result == ["KNOWS", "WORKS_FOR"]

    def test_get_relationship_type_counts(self, relationship_manager_instance):
        """Test get_relationship_type_counts method."""
        relationship_manager_instance.db_manager.execute_query.return_value = [
            {"type": "KNOWS", "count": 10},
            {"type": "WORKS_FOR", "count": 5}
        ]
        result = relationship_manager_instance.get_relationship_type_counts()
        assert result == {"KNOWS": 10, "WORKS_FOR": 5}

    def test_analyze_relationships(self, relationship_manager_instance):
        """Test analyze_relationships method."""
        # Mock the necessary method calls
        relationship_manager_instance.get_relationship_type_counts = MagicMock(return_value={"KNOWS": 10, "WORKS_FOR": 5})
        relationship_manager_instance.db_manager.query_to_value.return_value = 20
        relationship_manager_instance.db_manager.execute_query.return_value = [
            {"n": {"name": "Alice"}, "connections": 5},
            {"n": {"name": "Bob"}, "connections": 3}
        ]

        result = relationship_manager_instance.analyze_relationships()

        # Check that the result contains the expected data
        assert result["total_relationships"] == 15
        assert result["relationship_types"] == {"KNOWS": 10, "WORKS_FOR": 5}
        assert result["total_nodes"] == 20
        assert result["avg_relationships_per_node"] == 0.75
        assert len(result["most_connected_nodes"]) == 2
        assert result["most_connected_nodes"][0]["node"]["name"] == "Alice"
        assert result["most_connected_nodes"][0]["connections"] == 5


def test_singleton_instance():
    """Test that the relationship_manager is a singleton instance."""
    assert relationship_manager is not None
    assert isinstance(relationship_manager, RelationshipManager)

    # Create a new instance and check that it's the same object
    new_instance = RelationshipManager()
    assert new_instance is relationship_manager