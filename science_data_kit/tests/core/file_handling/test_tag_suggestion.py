"""
Tests for the tag suggestion module.

This module contains tests for the tag suggestion functionality, including
the TagSuggestionEngine class and utility functions.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import pytest

from science_data_kit.core.file_handling.tag_suggestion import (
    TagSuggestionStrategy,
    TagSuggestionOptions,
    TagSuggestion,
    TagSuggestionResult,
    TagSuggestionEngine,
    suggest_tags,
    suggest_tags_for_directory,
    apply_tags_to_file
)
from science_data_kit.core.file_handling.keyword_extraction import (
    KeywordExtractionResult,
    KeywordExtractionMethod,
    Keyword
)
from science_data_kit.core.file_handling.entity_recognition import (
    EntityExtractionResult,
    Entity,
    EntityType
)


class TestTagSuggestionOptions(unittest.TestCase):
    """Tests for TagSuggestionOptions class."""

    def test_default_options(self):
        """Test default options."""
        options = TagSuggestionOptions()
        self.assertEqual(options.strategy, TagSuggestionStrategy.HYBRID)
        self.assertEqual(options.max_suggestions, 10)
        self.assertEqual(options.min_score, 0.3)
        self.assertEqual(options.keyword_weight, 0.6)
        self.assertEqual(options.entity_weight, 0.4)
        self.assertTrue(options.filter_common_words)
        self.assertFalse(options.use_stemming)

    def test_weight_normalization(self):
        """Test weight normalization."""
        options = TagSuggestionOptions(keyword_weight=0.8, entity_weight=0.8)
        self.assertAlmostEqual(options.keyword_weight + options.entity_weight, 1.0)
        self.assertAlmostEqual(options.keyword_weight, 0.5)
        self.assertAlmostEqual(options.entity_weight, 0.5)


class TestTagSuggestion(unittest.TestCase):
    """Tests for TagSuggestion class."""

    def test_tag_suggestion_creation(self):
        """Test creating a tag suggestion."""
        suggestion = TagSuggestion(
            tag="example",
            score=0.75,
            source="Test source",
            details={"key": "value"}
        )
        self.assertEqual(suggestion.tag, "example")
        self.assertEqual(suggestion.score, 0.75)
        self.assertEqual(suggestion.source, "Test source")
        self.assertEqual(suggestion.details, {"key": "value"})

    def test_tag_suggestion_string_representation(self):
        """Test string representation of a tag suggestion."""
        suggestion = TagSuggestion(
            tag="example",
            score=0.75,
            source="Test source"
        )
        self.assertEqual(str(suggestion), "example (0.75) - Test source")


class TestTagSuggestionResult(unittest.TestCase):
    """Tests for TagSuggestionResult class."""

    def test_tag_suggestion_result_creation(self):
        """Test creating a tag suggestion result."""
        suggestion1 = TagSuggestion(tag="tag1", score=0.8, source="Source 1")
        suggestion2 = TagSuggestion(tag="tag2", score=0.6, source="Source 2")
        
        result = TagSuggestionResult(
            file_path="/path/to/file.txt",
            suggestions=[suggestion1, suggestion2],
            strategy=TagSuggestionStrategy.HYBRID,
            metadata={"key": "value"}
        )
        
        self.assertEqual(result.file_path, "/path/to/file.txt")
        self.assertEqual(len(result.suggestions), 2)
        self.assertEqual(result.strategy, TagSuggestionStrategy.HYBRID)
        self.assertEqual(result.metadata, {"key": "value"})

    def test_get_tags(self):
        """Test getting just the tag strings."""
        suggestion1 = TagSuggestion(tag="tag1", score=0.8, source="Source 1")
        suggestion2 = TagSuggestion(tag="tag2", score=0.6, source="Source 2")
        
        result = TagSuggestionResult(
            file_path="/path/to/file.txt",
            suggestions=[suggestion1, suggestion2],
            strategy=TagSuggestionStrategy.HYBRID
        )
        
        self.assertEqual(result.get_tags(), ["tag1", "tag2"])

    def test_string_representation_with_suggestions(self):
        """Test string representation with suggestions."""
        suggestion1 = TagSuggestion(tag="tag1", score=0.8, source="Source 1")
        suggestion2 = TagSuggestion(tag="tag2", score=0.6, source="Source 2")
        
        result = TagSuggestionResult(
            file_path="/path/to/file.txt",
            suggestions=[suggestion1, suggestion2],
            strategy=TagSuggestionStrategy.HYBRID
        )
        
        expected = "Tag suggestions for file.txt using hybrid strategy:\n- tag1 (0.80) - Source 1\n- tag2 (0.60) - Source 2"
        self.assertEqual(str(result), expected)

    def test_string_representation_without_suggestions(self):
        """Test string representation without suggestions."""
        result = TagSuggestionResult(
            file_path="/path/to/file.txt",
            suggestions=[],
            strategy=TagSuggestionStrategy.HYBRID
        )
        
        expected = "Tag suggestions for file.txt using hybrid strategy:\nNo suggestions found."
        self.assertEqual(str(result), expected)


class TestTagSuggestionEngine(unittest.TestCase):
    """Tests for TagSuggestionEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = TagSuggestionEngine()
        self.test_file_path = "/path/to/test_file.txt"

    def test_load_common_words(self):
        """Test loading common words."""
        common_words = self.engine._load_common_words()
        self.assertIsInstance(common_words, set)
        self.assertIn("the", common_words)
        self.assertIn("and", common_words)
        self.assertIn("or", common_words)

    @patch('os.path.exists')
    def test_suggest_tags_file_not_found(self, mock_exists):
        """Test suggesting tags for a non-existent file."""
        mock_exists.return_value = False
        
        result = self.engine.suggest_tags(self.test_file_path)
        
        self.assertEqual(result.file_path, self.test_file_path)
        self.assertEqual(result.suggestions, [])
        self.assertEqual(result.strategy, TagSuggestionStrategy.HYBRID)

    @patch('os.path.exists')
    @patch('science_data_kit.core.file_handling.tag_suggestion.extract_keywords_from_file')
    def test_suggest_keyword_based(self, mock_extract_keywords, mock_exists):
        """Test keyword-based tag suggestions."""
        mock_exists.return_value = True
        
        # Mock keyword extraction result
        mock_keywords = [
            Keyword(text="keyword1", score=0.9),
            Keyword(text="keyword2", score=0.8),
            Keyword(text="keyword3", score=0.7),
            Keyword(text="the", score=0.6)  # Common word that should be filtered
        ]
        mock_result = KeywordExtractionResult(
            file_path=self.test_file_path,
            keywords=mock_keywords,
            method=KeywordExtractionMethod.RAKE
        )
        mock_extract_keywords.return_value = mock_result
        
        # Create engine with keyword-based strategy
        engine = TagSuggestionEngine(TagSuggestionOptions(
            strategy=TagSuggestionStrategy.KEYWORD_BASED
        ))
        
        result = engine.suggest_tags(self.test_file_path)
        
        self.assertEqual(result.file_path, self.test_file_path)
        self.assertEqual(result.strategy, TagSuggestionStrategy.KEYWORD_BASED)
        self.assertEqual(len(result.suggestions), 3)  # "the" should be filtered out
        self.assertEqual(result.suggestions[0].tag, "keyword1")
        self.assertEqual(result.suggestions[1].tag, "keyword2")
        self.assertEqual(result.suggestions[2].tag, "keyword3")

    @patch('os.path.exists')
    @patch('science_data_kit.core.file_handling.tag_suggestion.extract_entities_from_file')
    def test_suggest_entity_based(self, mock_extract_entities, mock_exists):
        """Test entity-based tag suggestions."""
        mock_exists.return_value = True
        
        # Mock entity extraction result
        mock_entities = [
            Entity(text="Person1", entity_type=EntityType.PERSON),
            Entity(text="Organization1", entity_type=EntityType.ORGANIZATION),
            Entity(text="Location1", entity_type=EntityType.LOCATION),
            Entity(text="the", entity_type=EntityType.OTHER)  # Common word that should be filtered
        ]
        mock_result = EntityExtractionResult(
            file_path=self.test_file_path,
            entities=mock_entities
        )
        mock_extract_entities.return_value = mock_result
        
        # Create engine with entity-based strategy
        engine = TagSuggestionEngine(TagSuggestionOptions(
            strategy=TagSuggestionStrategy.ENTITY_BASED
        ))
        
        result = engine.suggest_tags(self.test_file_path)
        
        self.assertEqual(result.file_path, self.test_file_path)
        self.assertEqual(result.strategy, TagSuggestionStrategy.ENTITY_BASED)
        self.assertEqual(len(result.suggestions), 3)  # "the" should be filtered out
        
        # Check that entities are sorted by priority (PERSON > ORGANIZATION > LOCATION)
        self.assertEqual(result.suggestions[0].tag, "Person1")
        self.assertEqual(result.suggestions[1].tag, "Organization1")
        self.assertEqual(result.suggestions[2].tag, "Location1")

    @patch('os.path.exists')
    @patch('science_data_kit.core.file_handling.tag_suggestion.TagSuggestionEngine._suggest_keyword_based')
    @patch('science_data_kit.core.file_handling.tag_suggestion.TagSuggestionEngine._suggest_entity_based')
    def test_suggest_hybrid(self, mock_entity_based, mock_keyword_based, mock_exists):
        """Test hybrid tag suggestions."""
        mock_exists.return_value = True
        
        # Mock keyword-based result
        keyword_suggestions = [
            TagSuggestion(tag="keyword1", score=0.9, source="Keyword extraction"),
            TagSuggestion(tag="keyword2", score=0.8, source="Keyword extraction"),
            TagSuggestion(tag="common", score=0.7, source="Keyword extraction")
        ]
        mock_keyword_based.return_value = TagSuggestionResult(
            file_path=self.test_file_path,
            suggestions=keyword_suggestions,
            strategy=TagSuggestionStrategy.KEYWORD_BASED
        )
        
        # Mock entity-based result
        entity_suggestions = [
            TagSuggestion(tag="entity1", score=1.0, source="Entity (PERSON)", details={"entity_type": "PERSON"}),
            TagSuggestion(tag="common", score=1.0, source="Entity (ORGANIZATION)", details={"entity_type": "ORGANIZATION"})
        ]
        mock_entity_based.return_value = TagSuggestionResult(
            file_path=self.test_file_path,
            suggestions=entity_suggestions,
            strategy=TagSuggestionStrategy.ENTITY_BASED
        )
        
        # Create engine with hybrid strategy
        engine = TagSuggestionEngine(TagSuggestionOptions(
            strategy=TagSuggestionStrategy.HYBRID,
            keyword_weight=0.6,
            entity_weight=0.4
        ))
        
        result = engine.suggest_tags(self.test_file_path)
        
        self.assertEqual(result.file_path, self.test_file_path)
        self.assertEqual(result.strategy, TagSuggestionStrategy.HYBRID)
        self.assertEqual(len(result.suggestions), 3)
        
        # Check that "common" has a higher score due to being found by both methods
        common_suggestion = next(s for s in result.suggestions if s.tag == "common")
        self.assertGreater(common_suggestion.score, 0.7)  # Should be 0.6*0.7 + 0.4*1.0 = 0.82

    @patch('os.path.exists')
    @patch('os.walk')
    @patch('science_data_kit.core.file_handling.tag_suggestion.TagSuggestionEngine.suggest_tags')
    def test_suggest_tags_for_directory(self, mock_suggest_tags, mock_walk, mock_exists):
        """Test suggesting tags for a directory."""
        mock_exists.return_value = True
        
        # Mock os.walk to return some files
        mock_walk.return_value = [
            ("/path/to/dir", [], ["file1.txt", "file2.txt"])
        ]
        
        # Mock suggest_tags to return some results
        def mock_suggest_tags_func(file_path):
            return TagSuggestionResult(
                file_path=file_path,
                suggestions=[TagSuggestion(tag=f"tag_for_{os.path.basename(file_path)}", score=0.8, source="Test")],
                strategy=TagSuggestionStrategy.HYBRID
            )
        
        mock_suggest_tags.side_effect = mock_suggest_tags_func
        
        results = self.engine.suggest_tags_for_directory("/path/to/dir")
        
        self.assertEqual(len(results), 2)
        self.assertIn("/path/to/dir/file1.txt", results)
        self.assertIn("/path/to/dir/file2.txt", results)
        self.assertEqual(results["/path/to/dir/file1.txt"].suggestions[0].tag, "tag_for_file1.txt")
        self.assertEqual(results["/path/to/dir/file2.txt"].suggestions[0].tag, "tag_for_file2.txt")


class TestTagSuggestionUtilities(unittest.TestCase):
    """Tests for tag suggestion utility functions."""

    @patch('science_data_kit.core.file_handling.tag_suggestion.TagSuggestionEngine')
    def test_suggest_tags(self, mock_engine_class):
        """Test suggest_tags utility function."""
        # Mock TagSuggestionEngine.suggest_tags
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine
        
        mock_result = TagSuggestionResult(
            file_path="/path/to/file.txt",
            suggestions=[TagSuggestion(tag="test_tag", score=0.8, source="Test")],
            strategy=TagSuggestionStrategy.HYBRID
        )
        mock_engine.suggest_tags.return_value = mock_result
        
        # Call the utility function
        result = suggest_tags("/path/to/file.txt")
        
        # Verify the result
        self.assertEqual(result, mock_result)
        mock_engine_class.assert_called_once()
        mock_engine.suggest_tags.assert_called_once_with("/path/to/file.txt")

    @patch('science_data_kit.core.file_handling.tag_suggestion.TagSuggestionEngine')
    def test_suggest_tags_for_directory(self, mock_engine_class):
        """Test suggest_tags_for_directory utility function."""
        # Mock TagSuggestionEngine.suggest_tags_for_directory
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine
        
        mock_results = {
            "/path/to/dir/file1.txt": TagSuggestionResult(
                file_path="/path/to/dir/file1.txt",
                suggestions=[TagSuggestion(tag="tag1", score=0.8, source="Test")],
                strategy=TagSuggestionStrategy.HYBRID
            ),
            "/path/to/dir/file2.txt": TagSuggestionResult(
                file_path="/path/to/dir/file2.txt",
                suggestions=[TagSuggestion(tag="tag2", score=0.7, source="Test")],
                strategy=TagSuggestionStrategy.HYBRID
            )
        }
        mock_engine.suggest_tags_for_directory.return_value = mock_results
        
        # Call the utility function
        results = suggest_tags_for_directory("/path/to/dir", max_files=100)
        
        # Verify the result
        self.assertEqual(results, mock_results)
        mock_engine_class.assert_called_once()
        mock_engine.suggest_tags_for_directory.assert_called_once_with("/path/to/dir", 100)

    def test_apply_tags_to_file(self):
        """Test apply_tags_to_file utility function."""
        # Since this is a placeholder function, just verify it returns True
        result = apply_tags_to_file("/path/to/file.txt", ["tag1", "tag2"])
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
"""