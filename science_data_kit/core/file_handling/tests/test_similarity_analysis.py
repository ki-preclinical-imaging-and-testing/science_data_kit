"""
Tests for the similarity_analysis module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.similarity_analysis import (
    SimilarityMetricType,
    SimilarityOptions,
    SimilarityResult,
    JaccardSimilarity,
    CosineSimilarity,
    LevenshteinSimilarity,
    EuclideanSimilarity,
    get_similarity_metric,
    calculate_content_similarity,
    calculate_metadata_similarity,
    calculate_metadata_similarity_for_dicts,
    compare_files,
    find_similar_files,
    find_duplicate_files
)
from science_data_kit.core.file_handling.text_extraction import TextExtractionResult


class TestSimilarityOptions(unittest.TestCase):
    """Tests for the SimilarityOptions class."""
    
    def test_default_initialization(self):
        """Test that default initialization works correctly."""
        options = SimilarityOptions()
        self.assertEqual(options.metric_type, SimilarityMetricType.COSINE)
        self.assertEqual(options.threshold, 0.7)
        self.assertTrue(options.use_content)
        self.assertEqual(options.content_weight, 0.7)
        self.assertTrue(options.use_metadata)
        self.assertEqual(options.metadata_weight, 0.3)
        self.assertEqual(options.metadata_fields, [])
        self.assertTrue(options.normalize_scores)
        self.assertFalse(options.case_sensitive)
    
    def test_weight_normalization(self):
        """Test that weights are normalized if they don't sum to 1.0."""
        options = SimilarityOptions(content_weight=0.8, metadata_weight=0.8)
        self.assertAlmostEqual(options.content_weight, 0.5)
        self.assertAlmostEqual(options.metadata_weight, 0.5)
    
    def test_threshold_validation(self):
        """Test that threshold is validated."""
        with self.assertRaises(ValueError):
            SimilarityOptions(threshold=-0.1)
        
        with self.assertRaises(ValueError):
            SimilarityOptions(threshold=1.1)


class TestSimilarityResult(unittest.TestCase):
    """Tests for the SimilarityResult class."""
    
    def test_initialization(self):
        """Test that initialization works correctly."""
        result = SimilarityResult(
            file1_path="/path/to/file1.txt",
            file2_path="/path/to/file2.txt",
            similarity_score=0.85,
            content_similarity=0.9,
            metadata_similarity=0.7,
            metric_type=SimilarityMetricType.COSINE
        )
        
        self.assertEqual(result.file1_path, "/path/to/file1.txt")
        self.assertEqual(result.file2_path, "/path/to/file2.txt")
        self.assertEqual(result.similarity_score, 0.85)
        self.assertEqual(result.content_similarity, 0.9)
        self.assertEqual(result.metadata_similarity, 0.7)
        self.assertEqual(result.metric_type, SimilarityMetricType.COSINE)
        self.assertEqual(result.comparison_details, {})
    
    def test_is_similar(self):
        """Test the is_similar property."""
        result1 = SimilarityResult(
            file1_path="/path/to/file1.txt",
            file2_path="/path/to/file2.txt",
            similarity_score=0.8
        )
        self.assertTrue(result1.is_similar)
        
        result2 = SimilarityResult(
            file1_path="/path/to/file1.txt",
            file2_path="/path/to/file2.txt",
            similarity_score=0.6
        )
        self.assertFalse(result2.is_similar)
    
    def test_str_representation(self):
        """Test the string representation."""
        result = SimilarityResult(
            file1_path="/path/to/file1.txt",
            file2_path="/path/to/file2.txt",
            similarity_score=0.85,
            metric_type=SimilarityMetricType.JACCARD
        )
        
        expected_str = "Similarity between 'file1.txt' and 'file2.txt': 0.85 (jaccard)"
        self.assertEqual(str(result), expected_str)


class TestJaccardSimilarity(unittest.TestCase):
    """Tests for the JaccardSimilarity class."""
    
    def setUp(self):
        """Set up the test case."""
        self.metric = JaccardSimilarity()
    
    def test_metric_type(self):
        """Test the metric_type property."""
        self.assertEqual(self.metric.metric_type, SimilarityMetricType.JACCARD)
    
    def test_calculate_with_sets(self):
        """Test calculating similarity with sets."""
        set1 = {"apple", "banana", "orange"}
        set2 = {"apple", "banana", "grape"}
        
        # 2 common elements out of 4 unique elements
        expected_similarity = 2 / 4
        
        similarity = self.metric.calculate(set1, set2)
        self.assertEqual(similarity, expected_similarity)
    
    def test_calculate_with_strings(self):
        """Test calculating similarity with strings."""
        str1 = "apple banana orange"
        str2 = "apple banana grape"
        
        # 2 common words out of 4 unique words
        expected_similarity = 2 / 4
        
        similarity = self.metric.calculate(str1, str2)
        self.assertEqual(similarity, expected_similarity)
    
    def test_calculate_with_empty_sets(self):
        """Test calculating similarity with empty sets."""
        set1 = set()
        set2 = set()
        
        similarity = self.metric.calculate(set1, set2)
        self.assertEqual(similarity, 1.0)  # Empty sets are identical
    
    def test_calculate_with_one_empty_set(self):
        """Test calculating similarity with one empty set."""
        set1 = {"apple", "banana", "orange"}
        set2 = set()
        
        similarity = self.metric.calculate(set1, set2)
        self.assertEqual(similarity, 0.0)  # No overlap
    
    def test_case_sensitivity(self):
        """Test case sensitivity option."""
        str1 = "Apple Banana Orange"
        str2 = "apple banana grape"
        
        # Case-sensitive: 0 common words out of 6 unique words
        options_sensitive = SimilarityOptions(case_sensitive=True)
        similarity_sensitive = self.metric.calculate(str1, str2, options_sensitive)
        self.assertEqual(similarity_sensitive, 0.0)
        
        # Case-insensitive: 2 common words out of 4 unique words
        options_insensitive = SimilarityOptions(case_sensitive=False)
        similarity_insensitive = self.metric.calculate(str1, str2, options_insensitive)
        self.assertEqual(similarity_insensitive, 2 / 4)


class TestCosineSimilarity(unittest.TestCase):
    """Tests for the CosineSimilarity class."""
    
    def setUp(self):
        """Set up the test case."""
        self.metric = CosineSimilarity()
    
    def test_metric_type(self):
        """Test the metric_type property."""
        self.assertEqual(self.metric.metric_type, SimilarityMetricType.COSINE)
    
    def test_calculate_with_identical_texts(self):
        """Test calculating similarity with identical texts."""
        text1 = "This is a test document for cosine similarity."
        text2 = "This is a test document for cosine similarity."
        
        similarity = self.metric.calculate(text1, text2)
        self.assertAlmostEqual(similarity, 1.0)
    
    def test_calculate_with_similar_texts(self):
        """Test calculating similarity with similar texts."""
        text1 = "This is a test document for cosine similarity."
        text2 = "This is a test file for cosine similarity calculation."
        
        similarity = self.metric.calculate(text1, text2)
        self.assertGreater(similarity, 0.7)  # Should be fairly similar
    
    def test_calculate_with_different_texts(self):
        """Test calculating similarity with different texts."""
        text1 = "This is a test document for cosine similarity."
        text2 = "Python is a programming language with clear syntax."
        
        similarity = self.metric.calculate(text1, text2)
        self.assertLess(similarity, 0.3)  # Should be quite different
    
    def test_calculate_with_empty_texts(self):
        """Test calculating similarity with empty texts."""
        text1 = ""
        text2 = ""
        
        similarity = self.metric.calculate(text1, text2)
        self.assertEqual(similarity, 1.0)  # Empty texts are identical
    
    def test_calculate_with_one_empty_text(self):
        """Test calculating similarity with one empty text."""
        text1 = "This is a test document for cosine similarity."
        text2 = ""
        
        similarity = self.metric.calculate(text1, text2)
        self.assertEqual(similarity, 0.0)  # No overlap
    
    def test_case_sensitivity(self):
        """Test case sensitivity option."""
        text1 = "This is a TEST document."
        text2 = "This is a test document."
        
        # With default options (case-insensitive)
        similarity_insensitive = self.metric.calculate(text1, text2)
        self.assertAlmostEqual(similarity_insensitive, 1.0)
        
        # With case-sensitive option
        options_sensitive = SimilarityOptions(case_sensitive=True)
        similarity_sensitive = self.metric.calculate(text1, text2, options_sensitive)
        self.assertLess(similarity_sensitive, 1.0)


class TestLevenshteinSimilarity(unittest.TestCase):
    """Tests for the LevenshteinSimilarity class."""
    
    def setUp(self):
        """Set up the test case."""
        self.metric = LevenshteinSimilarity()
    
    def test_metric_type(self):
        """Test the metric_type property."""
        self.assertEqual(self.metric.metric_type, SimilarityMetricType.LEVENSHTEIN)
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.distance')
    def test_calculate_with_strings(self, mock_distance):
        """Test calculating similarity with strings."""
        mock_distance.return_value = 2  # Mock Levenshtein distance
        
        str1 = "kitten"
        str2 = "sitting"
        
        # Max length is 7, distance is 2, so similarity is 1 - (2/7) = 5/7
        expected_similarity = 1.0 - (2.0 / 7.0)
        
        similarity = self.metric.calculate(str1, str2)
        self.assertAlmostEqual(similarity, expected_similarity)
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.distance')
    def test_calculate_with_identical_strings(self, mock_distance):
        """Test calculating similarity with identical strings."""
        mock_distance.return_value = 0  # No difference
        
        str1 = "identical"
        str2 = "identical"
        
        similarity = self.metric.calculate(str1, str2)
        self.assertEqual(similarity, 1.0)
    
    def test_calculate_with_empty_strings(self):
        """Test calculating similarity with empty strings."""
        str1 = ""
        str2 = ""
        
        similarity = self.metric.calculate(str1, str2)
        self.assertEqual(similarity, 1.0)  # Empty strings are identical
    
    def test_calculate_with_one_empty_string(self):
        """Test calculating similarity with one empty string."""
        str1 = "kitten"
        str2 = ""
        
        similarity = self.metric.calculate(str1, str2)
        self.assertEqual(similarity, 0.0)  # Maximum distance
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.distance', side_effect=ImportError)
    def test_fallback_to_jaccard(self, mock_distance):
        """Test fallback to Jaccard similarity if Levenshtein is not available."""
        str1 = "apple banana orange"
        str2 = "apple banana grape"
        
        # Should fall back to Jaccard similarity: 2 common words out of 4 unique words
        expected_similarity = 2 / 4
        
        similarity = self.metric.calculate(str1, str2)
        self.assertEqual(similarity, expected_similarity)


class TestEuclideanSimilarity(unittest.TestCase):
    """Tests for the EuclideanSimilarity class."""
    
    def setUp(self):
        """Set up the test case."""
        self.metric = EuclideanSimilarity()
    
    def test_metric_type(self):
        """Test the metric_type property."""
        self.assertEqual(self.metric.metric_type, SimilarityMetricType.EUCLIDEAN)
    
    def test_calculate_with_identical_vectors(self):
        """Test calculating similarity with identical vectors."""
        vec1 = [1.0, 2.0, 3.0, 4.0]
        vec2 = [1.0, 2.0, 3.0, 4.0]
        
        similarity = self.metric.calculate(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0)  # Identical vectors
    
    def test_calculate_with_numpy_arrays(self):
        """Test calculating similarity with numpy arrays."""
        vec1 = np.array([1.0, 2.0, 3.0, 4.0])
        vec2 = np.array([1.0, 2.0, 3.0, 4.0])
        
        similarity = self.metric.calculate(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0)  # Identical vectors
    
    def test_calculate_with_different_vectors(self):
        """Test calculating similarity with different vectors."""
        vec1 = [1.0, 2.0, 3.0, 4.0]
        vec2 = [5.0, 6.0, 7.0, 8.0]
        
        similarity = self.metric.calculate(vec1, vec2)
        self.assertLess(similarity, 1.0)  # Different vectors
        self.assertGreater(similarity, 0.0)  # But still some similarity
    
    def test_calculate_with_different_shapes(self):
        """Test calculating similarity with vectors of different shapes."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0, 4.0]
        
        similarity = self.metric.calculate(vec1, vec2)
        self.assertEqual(similarity, 0.0)  # Different shapes, no similarity


class TestGetSimilarityMetric(unittest.TestCase):
    """Tests for the get_similarity_metric function."""
    
    def test_get_jaccard_metric(self):
        """Test getting a Jaccard similarity metric."""
        metric = get_similarity_metric(SimilarityMetricType.JACCARD)
        self.assertIsInstance(metric, JaccardSimilarity)
    
    def test_get_cosine_metric(self):
        """Test getting a Cosine similarity metric."""
        metric = get_similarity_metric(SimilarityMetricType.COSINE)
        self.assertIsInstance(metric, CosineSimilarity)
    
    def test_get_levenshtein_metric(self):
        """Test getting a Levenshtein similarity metric."""
        metric = get_similarity_metric(SimilarityMetricType.LEVENSHTEIN)
        self.assertIsInstance(metric, LevenshteinSimilarity)
    
    def test_get_euclidean_metric(self):
        """Test getting a Euclidean similarity metric."""
        metric = get_similarity_metric(SimilarityMetricType.EUCLIDEAN)
        self.assertIsInstance(metric, EuclideanSimilarity)
    
    def test_get_unsupported_metric(self):
        """Test getting an unsupported similarity metric."""
        with self.assertRaises(ValueError):
            get_similarity_metric(SimilarityMetricType.CUSTOM)


class TestCalculateContentSimilarity(unittest.TestCase):
    """Tests for the calculate_content_similarity function."""
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.extract_text_from_file')
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_similarity_metric')
    def test_calculate_content_similarity(self, mock_get_metric, mock_extract_text):
        """Test calculating content similarity between two files."""
        # Mock the text extraction
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            TextExtractionResult(text="This is file 2", metadata={})
        ]
        
        # Mock the similarity metric
        mock_metric = MagicMock()
        mock_metric.calculate.return_value = 0.75
        mock_get_metric.return_value = mock_metric
        
        # Calculate similarity
        similarity = calculate_content_similarity(
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            SimilarityOptions(metric_type=SimilarityMetricType.COSINE)
        )
        
        # Check the result
        self.assertEqual(similarity, 0.75)
        
        # Verify the mocks were called correctly
        mock_extract_text.assert_called()
        mock_get_metric.assert_called_with(SimilarityMetricType.COSINE)
        mock_metric.calculate.assert_called()
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.extract_text_from_file')
    def test_calculate_content_similarity_extraction_failure(self, mock_extract_text):
        """Test calculating content similarity when text extraction fails."""
        # Mock the text extraction to fail for one file
        mock_extract_text.side_effect = [
            TextExtractionResult(text="This is file 1", metadata={}),
            None
        ]
        
        # Calculate similarity
        similarity = calculate_content_similarity(
            "/path/to/file1.txt",
            "/path/to/file2.txt"
        )
        
        # Check the result
        self.assertEqual(similarity, 0.0)
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.extract_text_from_file')
    def test_calculate_content_similarity_exception(self, mock_extract_text):
        """Test calculating content similarity when an exception occurs."""
        # Mock the text extraction to raise an exception
        mock_extract_text.side_effect = Exception("Test exception")
        
        # Calculate similarity
        similarity = calculate_content_similarity(
            "/path/to/file1.txt",
            "/path/to/file2.txt"
        )
        
        # Check the result
        self.assertEqual(similarity, 0.0)


class TestCalculateMetadataSimilarity(unittest.TestCase):
    """Tests for the calculate_metadata_similarity function."""
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_file_interpreter_for_file')
    def test_calculate_metadata_similarity(self, mock_get_interpreter):
        """Test calculating metadata similarity between two files."""
        # Mock the file interpreters
        mock_interpreter1 = MagicMock()
        mock_interpreter1.extract_metadata.return_value = {
            "width": 800,
            "height": 600,
            "format": "JPEG",
            "tags": ["photo", "landscape"]
        }
        
        mock_interpreter2 = MagicMock()
        mock_interpreter2.extract_metadata.return_value = {
            "width": 800,
            "height": 600,
            "format": "PNG",
            "tags": ["photo", "portrait"]
        }
        
        mock_get_interpreter.side_effect = [mock_interpreter1, mock_interpreter2]
        
        # Calculate similarity
        similarity = calculate_metadata_similarity(
            "/path/to/file1.jpg",
            "/path/to/file2.png"
        )
        
        # Check the result
        self.assertGreater(similarity, 0.5)  # Should be fairly similar
        
        # Verify the mocks were called correctly
        mock_get_interpreter.assert_called()
        mock_interpreter1.extract_metadata.assert_called_with("/path/to/file1.jpg")
        mock_interpreter2.extract_metadata.assert_called_with("/path/to/file2.png")
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_file_interpreter_for_file')
    def test_calculate_metadata_similarity_with_fields(self, mock_get_interpreter):
        """Test calculating metadata similarity with specific fields."""
        # Mock the file interpreters
        mock_interpreter1 = MagicMock()
        mock_interpreter1.extract_metadata.return_value = {
            "width": 800,
            "height": 600,
            "format": "JPEG",
            "tags": ["photo", "landscape"]
        }
        
        mock_interpreter2 = MagicMock()
        mock_interpreter2.extract_metadata.return_value = {
            "width": 800,
            "height": 600,
            "format": "PNG",
            "tags": ["photo", "portrait"]
        }
        
        mock_get_interpreter.side_effect = [mock_interpreter1, mock_interpreter2]
        
        # Calculate similarity with specific fields
        similarity = calculate_metadata_similarity(
            "/path/to/file1.jpg",
            "/path/to/file2.png",
            SimilarityOptions(metadata_fields=["width", "height"])
        )
        
        # Check the result
        self.assertEqual(similarity, 1.0)  # Width and height are identical
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_file_interpreter_for_file')
    def test_calculate_metadata_similarity_no_interpreter(self, mock_get_interpreter):
        """Test calculating metadata similarity when no interpreter is available."""
        # Mock the file interpreters to return None
        mock_get_interpreter.side_effect = [None, None]
        
        # Calculate similarity
        similarity = calculate_metadata_similarity(
            "/path/to/file1.jpg",
            "/path/to/file2.png"
        )
        
        # Check the result
        self.assertEqual(similarity, 0.0)
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_file_interpreter_for_file')
    def test_calculate_metadata_similarity_no_metadata(self, mock_get_interpreter):
        """Test calculating metadata similarity when no metadata is available."""
        # Mock the file interpreters to return empty metadata
        mock_interpreter1 = MagicMock()
        mock_interpreter1.extract_metadata.return_value = {}
        
        mock_interpreter2 = MagicMock()
        mock_interpreter2.extract_metadata.return_value = {}
        
        mock_get_interpreter.side_effect = [mock_interpreter1, mock_interpreter2]
        
        # Calculate similarity
        similarity = calculate_metadata_similarity(
            "/path/to/file1.jpg",
            "/path/to/file2.png"
        )
        
        # Check the result
        self.assertEqual(similarity, 0.0)
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.get_file_interpreter_for_file')
    def test_calculate_metadata_similarity_exception(self, mock_get_interpreter):
        """Test calculating metadata similarity when an exception occurs."""
        # Mock the file interpreters to raise an exception
        mock_get_interpreter.side_effect = Exception("Test exception")
        
        # Calculate similarity
        similarity = calculate_metadata_similarity(
            "/path/to/file1.jpg",
            "/path/to/file2.png"
        )
        
        # Check the result
        self.assertEqual(similarity, 0.0)


class TestCalculateMetadataSimilarityForDicts(unittest.TestCase):
    """Tests for the calculate_metadata_similarity_for_dicts function."""
    
    def test_calculate_with_identical_dicts(self):
        """Test calculating similarity with identical dictionaries."""
        dict1 = {
            "width": 800,
            "height": 600,
            "format": "JPEG",
            "tags": ["photo", "landscape"]
        }
        
        dict2 = {
            "width": 800,
            "height": 600,
            "format": "JPEG",
            "tags": ["photo", "landscape"]
        }
        
        similarity = calculate_metadata_similarity_for_dicts(dict1, dict2)
        self.assertEqual(similarity, 1.0)  # Identical dictionaries
    
    def test_calculate_with_similar_dicts(self):
        """Test calculating similarity with similar dictionaries."""
        dict1 = {
            "width": 800,
            "height": 600,
            "format": "JPEG",
            "tags": ["photo", "landscape"]
        }
        
        dict2 = {
            "width": 800,
            "height": 600,
            "format": "PNG",
            "tags": ["photo", "portrait"]
        }
        
        similarity = calculate_metadata_similarity_for_dicts(dict1, dict2)
        self.assertGreater(similarity, 0.5)  # Should be fairly similar
    
    def test_calculate_with_different_dicts(self):
        """Test calculating similarity with different dictionaries."""
        dict1 = {
            "width": 800,
            "height": 600,
            "format": "JPEG"
        }
        
        dict2 = {
            "author": "John Doe",
            "title": "Test Document",
            "pages": 10
        }
        
        similarity = calculate_metadata_similarity_for_dicts(dict1, dict2)
        self.assertEqual(similarity, 0.0)  # No common fields
    
    def test_calculate_with_nested_dicts(self):
        """Test calculating similarity with nested dictionaries."""
        dict1 = {
            "dimensions": {
                "width": 800,
                "height": 600
            },
            "format": "JPEG"
        }
        
        dict2 = {
            "dimensions": {
                "width": 800,
                "height": 600
            },
            "format": "PNG"
        }
        
        similarity = calculate_metadata_similarity_for_dicts(dict1, dict2)
        self.assertGreater(similarity, 0.5)  # Should be fairly similar
    
    def test_calculate_with_empty_dicts(self):
        """Test calculating similarity with empty dictionaries."""
        dict1 = {}
        dict2 = {}
        
        similarity = calculate_metadata_similarity_for_dicts(dict1, dict2)
        self.assertEqual(similarity, 0.0)  # No fields to compare


class TestCompareFiles(unittest.TestCase):
    """Tests for the compare_files function."""
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.calculate_content_similarity')
    @patch('science_data_kit.core.file_handling.similarity_analysis.calculate_metadata_similarity')
    def test_compare_files_both_enabled(self, mock_metadata_sim, mock_content_sim):
        """Test comparing files with both content and metadata similarity enabled."""
        # Mock the similarity calculations
        mock_content_sim.return_value = 0.8
        mock_metadata_sim.return_value = 0.6
        
        # Compare files
        result = compare_files(
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            SimilarityOptions(
                content_weight=0.7,
                metadata_weight=0.3
            )
        )
        
        # Check the result
        self.assertEqual(result.file1_path, "/path/to/file1.txt")
        self.assertEqual(result.file2_path, "/path/to/file2.txt")
        self.assertEqual(result.content_similarity, 0.8)
        self.assertEqual(result.metadata_similarity, 0.6)
        self.assertEqual(result.similarity_score, 0.7 * 0.8 + 0.3 * 0.6)  # Weighted average
        self.assertEqual(result.metric_type, SimilarityMetricType.COSINE)
        self.assertEqual(result.comparison_details, {
            "content_similarity": 0.8,
            "metadata_similarity": 0.6
        })
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.calculate_content_similarity')
    def test_compare_files_content_only(self, mock_content_sim):
        """Test comparing files with only content similarity enabled."""
        # Mock the similarity calculations
        mock_content_sim.return_value = 0.8
        
        # Compare files
        result = compare_files(
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            SimilarityOptions(
                use_content=True,
                use_metadata=False
            )
        )
        
        # Check the result
        self.assertEqual(result.content_similarity, 0.8)
        self.assertIsNone(result.metadata_similarity)
        self.assertEqual(result.similarity_score, 0.8)
        self.assertEqual(result.comparison_details, {
            "content_similarity": 0.8
        })
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.calculate_metadata_similarity')
    def test_compare_files_metadata_only(self, mock_metadata_sim):
        """Test comparing files with only metadata similarity enabled."""
        # Mock the similarity calculations
        mock_metadata_sim.return_value = 0.6
        
        # Compare files
        result = compare_files(
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            SimilarityOptions(
                use_content=False,
                use_metadata=True
            )
        )
        
        # Check the result
        self.assertIsNone(result.content_similarity)
        self.assertEqual(result.metadata_similarity, 0.6)
        self.assertEqual(result.similarity_score, 0.6)
        self.assertEqual(result.comparison_details, {
            "metadata_similarity": 0.6
        })
    
    def test_compare_files_none_enabled(self):
        """Test comparing files with neither content nor metadata similarity enabled."""
        # Compare files
        result = compare_files(
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            SimilarityOptions(
                use_content=False,
                use_metadata=False
            )
        )
        
        # Check the result
        self.assertIsNone(result.content_similarity)
        self.assertIsNone(result.metadata_similarity)
        self.assertEqual(result.similarity_score, 0.0)
        self.assertEqual(result.comparison_details, {})


class TestFindSimilarFiles(unittest.TestCase):
    """Tests for the find_similar_files function."""
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.compare_files')
    def test_find_similar_files(self, mock_compare_files):
        """Test finding similar files."""
        # Mock the compare_files function
        mock_compare_files.side_effect = [
            SimilarityResult(
                file1_path="/path/to/target.txt",
                file2_path="/path/to/file1.txt",
                similarity_score=0.8
            ),
            SimilarityResult(
                file1_path="/path/to/target.txt",
                file2_path="/path/to/file2.txt",
                similarity_score=0.6
            ),
            SimilarityResult(
                file1_path="/path/to/target.txt",
                file2_path="/path/to/file3.txt",
                similarity_score=0.9
            )
        ]
        
        # Find similar files
        results = find_similar_files(
            "/path/to/target.txt",
            [
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt"
            ],
            SimilarityOptions(threshold=0.7)
        )
        
        # Check the results
        self.assertEqual(len(results), 2)  # Only 2 files above threshold
        self.assertEqual(results[0].file2_path, "/path/to/file3.txt")  # Highest similarity first
        self.assertEqual(results[1].file2_path, "/path/to/file1.txt")
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.compare_files')
    def test_find_similar_files_skip_self(self, mock_compare_files):
        """Test that finding similar files skips the target file itself."""
        # Find similar files
        results = find_similar_files(
            "/path/to/target.txt",
            [
                "/path/to/target.txt",  # Same as target
                "/path/to/file1.txt",
                "/path/to/file2.txt"
            ]
        )
        
        # Check that compare_files was called only twice (skipping target.txt)
        self.assertEqual(mock_compare_files.call_count, 2)


class TestFindDuplicateFiles(unittest.TestCase):
    """Tests for the find_duplicate_files function."""
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.compare_files')
    def test_find_duplicate_files(self, mock_compare_files):
        """Test finding duplicate files."""
        # Mock the compare_files function
        mock_compare_files.side_effect = [
            # file1 vs file2
            SimilarityResult(
                file1_path="/path/to/file1.txt",
                file2_path="/path/to/file2.txt",
                similarity_score=0.98
            ),
            # file1 vs file3
            SimilarityResult(
                file1_path="/path/to/file1.txt",
                file2_path="/path/to/file3.txt",
                similarity_score=0.5
            ),
            # file1 vs file4
            SimilarityResult(
                file1_path="/path/to/file1.txt",
                file2_path="/path/to/file4.txt",
                similarity_score=0.4
            ),
            # file2 vs file3
            SimilarityResult(
                file1_path="/path/to/file2.txt",
                file2_path="/path/to/file3.txt",
                similarity_score=0.5
            ),
            # file2 vs file4
            SimilarityResult(
                file1_path="/path/to/file2.txt",
                file2_path="/path/to/file4.txt",
                similarity_score=0.4
            ),
            # file3 vs file4
            SimilarityResult(
                file1_path="/path/to/file3.txt",
                file2_path="/path/to/file4.txt",
                similarity_score=0.97
            )
        ]
        
        # Find duplicate files
        results = find_duplicate_files(
            [
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt",
                "/path/to/file4.txt"
            ],
            SimilarityOptions(threshold=0.95)
        )
        
        # Check the results
        self.assertEqual(len(results), 2)  # Two groups of duplicates
        
        # Check that each group contains the right files
        self.assertTrue(
            any(
                set(group) == {"/path/to/file1.txt", "/path/to/file2.txt"}
                for group in results
            )
        )
        self.assertTrue(
            any(
                set(group) == {"/path/to/file3.txt", "/path/to/file4.txt"}
                for group in results
            )
        )
    
    @patch('science_data_kit.core.file_handling.similarity_analysis.compare_files')
    def test_find_duplicate_files_no_duplicates(self, mock_compare_files):
        """Test finding duplicate files when there are no duplicates."""
        # Mock the compare_files function to return low similarity scores
        mock_compare_files.return_value = SimilarityResult(
            file1_path="/path/to/file1.txt",
            file2_path="/path/to/file2.txt",
            similarity_score=0.5
        )
        
        # Find duplicate files
        results = find_duplicate_files(
            [
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt"
            ],
            SimilarityOptions(threshold=0.95)
        )
        
        # Check the results
        self.assertEqual(len(results), 0)  # No duplicates found


if __name__ == '__main__':
    unittest.main()
"""