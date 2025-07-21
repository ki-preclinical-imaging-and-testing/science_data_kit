"""
Unit tests for the recommendation engine module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from science_data_kit.core.file_handling.recommendation_engine import (
    RecommendationStrategy,
    RecommendationOptions,
    Recommendation,
    RecommendationResult,
    RecommendationEngine,
    recommend_similar_files,
    recommend_for_directory
)


class TestRecommendationOptions(unittest.TestCase):
    """Test cases for RecommendationOptions."""
    
    def test_default_options(self):
        """Test default options."""
        options = RecommendationOptions()
        self.assertEqual(options.strategy, RecommendationStrategy.HYBRID)
        self.assertEqual(options.max_recommendations, 10)
        self.assertEqual(options.min_similarity_score, 0.3)
        self.assertEqual(options.content_weight, 0.7)
        self.assertEqual(options.metadata_weight, 0.3)
        self.assertEqual(options.metadata_fields, [])
        self.assertTrue(options.use_keywords)
        self.assertEqual(options.keyword_weight, 0.5)
        self.assertFalse(options.use_file_history)
        self.assertEqual(options.history_weight, 0.2)
    
    def test_weight_normalization(self):
        """Test weight normalization."""
        options = RecommendationOptions(content_weight=0.8, metadata_weight=0.8)
        self.assertAlmostEqual(options.content_weight + options.metadata_weight, 1.0)
        self.assertAlmostEqual(options.content_weight, 0.5)
        self.assertAlmostEqual(options.metadata_weight, 0.5)


class TestRecommendation(unittest.TestCase):
    """Test cases for Recommendation."""
    
    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        rec = Recommendation(
            file_path="/path/to/file.txt",
            score=0.85,
            reason="Content similarity",
            similarity_details={"content_similarity": 0.85}
        )
        self.assertEqual(rec.file_path, "/path/to/file.txt")
        self.assertEqual(rec.score, 0.85)
        self.assertEqual(rec.reason, "Content similarity")
        self.assertEqual(rec.similarity_details, {"content_similarity": 0.85})
        self.assertIsNone(rec.keywords)
    
    def test_recommendation_string_representation(self):
        """Test string representation of a recommendation."""
        rec = Recommendation(
            file_path="/path/to/file.txt",
            score=0.85,
            reason="Content similarity"
        )
        self.assertEqual(str(rec), "Recommendation: file.txt (score: 0.85) - Content similarity")


class TestRecommendationResult(unittest.TestCase):
    """Test cases for RecommendationResult."""
    
    def test_result_creation(self):
        """Test creating a recommendation result."""
        rec1 = Recommendation(
            file_path="/path/to/file1.txt",
            score=0.85,
            reason="Content similarity"
        )
        rec2 = Recommendation(
            file_path="/path/to/file2.txt",
            score=0.75,
            reason="Metadata similarity"
        )
        result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[rec1, rec2],
            strategy=RecommendationStrategy.HYBRID,
            metadata={"num_candidates": 10, "num_recommendations": 2}
        )
        self.assertEqual(result.target_file, "/path/to/target.txt")
        self.assertEqual(len(result.recommendations), 2)
        self.assertEqual(result.strategy, RecommendationStrategy.HYBRID)
        self.assertEqual(result.metadata, {"num_candidates": 10, "num_recommendations": 2})
    
    def test_result_string_representation(self):
        """Test string representation of a recommendation result."""
        rec1 = Recommendation(
            file_path="/path/to/file1.txt",
            score=0.85,
            reason="Content similarity"
        )
        rec2 = Recommendation(
            file_path="/path/to/file2.txt",
            score=0.75,
            reason="Metadata similarity"
        )
        result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[rec1, rec2],
            strategy=RecommendationStrategy.HYBRID
        )
        expected_str = (
            "Recommendations for target.txt using hybrid strategy:\n"
            "- Recommendation: file1.txt (score: 0.85) - Content similarity\n"
            "- Recommendation: file2.txt (score: 0.75) - Metadata similarity"
        )
        self.assertEqual(str(result), expected_str)
    
    def test_empty_result_string_representation(self):
        """Test string representation of an empty recommendation result."""
        result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[],
            strategy=RecommendationStrategy.HYBRID
        )
        expected_str = (
            "Recommendations for target.txt using hybrid strategy:\n"
            "No recommendations found."
        )
        self.assertEqual(str(result), expected_str)


class TestRecommendationEngine(unittest.TestCase):
    """Test cases for RecommendationEngine."""
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.find_content_based_similar_files')
    def test_content_based_recommendations(self, mock_find_similar):
        """Test content-based recommendations."""
        # Mock the find_content_based_similar_files function
        mock_find_similar.return_value = [
            ("/path/to/file1.txt", 0.85),
            ("/path/to/file2.txt", 0.75),
            ("/path/to/file3.txt", 0.65),
            ("/path/to/file4.txt", 0.25)  # Below threshold
        ]
        
        # Create engine with content-based strategy
        options = RecommendationOptions(
            strategy=RecommendationStrategy.CONTENT_BASED,
            min_similarity_score=0.3
        )
        engine = RecommendationEngine(options)
        
        # Generate recommendations
        result = engine.recommend_similar_files(
            target_file="/path/to/target.txt",
            file_list=[
                "/path/to/target.txt",
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt",
                "/path/to/file4.txt"
            ]
        )
        
        # Verify results
        self.assertEqual(result.target_file, "/path/to/target.txt")
        self.assertEqual(result.strategy, RecommendationStrategy.CONTENT_BASED)
        self.assertEqual(len(result.recommendations), 3)  # file4.txt is below threshold
        self.assertEqual(result.recommendations[0].file_path, "/path/to/file1.txt")
        self.assertEqual(result.recommendations[0].score, 0.85)
        self.assertEqual(result.recommendations[0].reason, "Content similarity")
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.find_similar_files')
    def test_metadata_based_recommendations(self, mock_find_similar):
        """Test metadata-based recommendations."""
        # Mock the find_similar_files function
        mock_find_similar.return_value = [
            MagicMock(
                file2_path="/path/to/file1.txt",
                similarity_score=0.85,
                metadata_similarity=0.85
            ),
            MagicMock(
                file2_path="/path/to/file2.txt",
                similarity_score=0.75,
                metadata_similarity=0.75
            )
        ]
        
        # Create engine with metadata-based strategy
        options = RecommendationOptions(
            strategy=RecommendationStrategy.METADATA_BASED,
            min_similarity_score=0.3
        )
        engine = RecommendationEngine(options)
        
        # Generate recommendations
        result = engine.recommend_similar_files(
            target_file="/path/to/target.txt",
            file_list=[
                "/path/to/target.txt",
                "/path/to/file1.txt",
                "/path/to/file2.txt"
            ]
        )
        
        # Verify results
        self.assertEqual(result.target_file, "/path/to/target.txt")
        self.assertEqual(result.strategy, RecommendationStrategy.METADATA_BASED)
        self.assertEqual(len(result.recommendations), 2)
        self.assertEqual(result.recommendations[0].file_path, "/path/to/file1.txt")
        self.assertEqual(result.recommendations[0].score, 0.85)
        self.assertEqual(result.recommendations[0].reason, "Metadata similarity")
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.extract_keywords_from_file')
    def test_keyword_based_recommendations(self, mock_extract_keywords):
        """Test keyword-based recommendations."""
        # Create mock keyword extraction results
        target_keywords = MagicMock()
        target_keywords.keywords = [
            MagicMock(text="keyword1", score=0.9),
            MagicMock(text="keyword2", score=0.8),
            MagicMock(text="keyword3", score=0.7)
        ]
        
        file1_keywords = MagicMock()
        file1_keywords.keywords = [
            MagicMock(text="keyword1", score=0.85),
            MagicMock(text="keyword2", score=0.75),
            MagicMock(text="keyword4", score=0.65)
        ]
        
        file2_keywords = MagicMock()
        file2_keywords.keywords = [
            MagicMock(text="keyword3", score=0.8),
            MagicMock(text="keyword5", score=0.7)
        ]
        
        # Mock the extract_keywords_from_file function
        mock_extract_keywords.side_effect = lambda file_path, options: {
            "/path/to/target.txt": target_keywords,
            "/path/to/file1.txt": file1_keywords,
            "/path/to/file2.txt": file2_keywords
        }[file_path]
        
        # Create engine with keyword-based strategy
        options = RecommendationOptions(
            strategy=RecommendationStrategy.KEYWORD_BASED,
            min_similarity_score=0.3
        )
        engine = RecommendationEngine(options)
        
        # Generate recommendations
        result = engine.recommend_similar_files(
            target_file="/path/to/target.txt",
            file_list=[
                "/path/to/target.txt",
                "/path/to/file1.txt",
                "/path/to/file2.txt"
            ]
        )
        
        # Verify results
        self.assertEqual(result.target_file, "/path/to/target.txt")
        self.assertEqual(result.strategy, RecommendationStrategy.KEYWORD_BASED)
        self.assertEqual(len(result.recommendations), 2)
        
        # File1 has 2 common keywords out of 4 unique keywords
        self.assertEqual(result.recommendations[0].file_path, "/path/to/file1.txt")
        self.assertAlmostEqual(result.recommendations[0].score, 2/4)
        self.assertTrue("Keyword similarity" in result.recommendations[0].reason)
        self.assertEqual(len(result.recommendations[0].keywords), 2)
        
        # File2 has 1 common keyword out of 4 unique keywords
        self.assertEqual(result.recommendations[1].file_path, "/path/to/file2.txt")
        self.assertAlmostEqual(result.recommendations[1].score, 1/4)
        self.assertTrue("Keyword similarity" in result.recommendations[1].reason)
        self.assertEqual(len(result.recommendations[1].keywords), 1)
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine._recommend_content_based')
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine._recommend_metadata_based')
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine._recommend_keyword_based')
    def test_hybrid_recommendations(self, mock_keyword, mock_metadata, mock_content):
        """Test hybrid recommendations."""
        # Create mock recommendation results
        content_result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[
                Recommendation(
                    file_path="/path/to/file1.txt",
                    score=0.85,
                    reason="Content similarity",
                    similarity_details={"content_similarity": 0.85}
                ),
                Recommendation(
                    file_path="/path/to/file2.txt",
                    score=0.75,
                    reason="Content similarity",
                    similarity_details={"content_similarity": 0.75}
                )
            ],
            strategy=RecommendationStrategy.CONTENT_BASED
        )
        
        metadata_result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[
                Recommendation(
                    file_path="/path/to/file1.txt",
                    score=0.8,
                    reason="Metadata similarity",
                    similarity_details={"metadata_similarity": 0.8}
                ),
                Recommendation(
                    file_path="/path/to/file3.txt",
                    score=0.7,
                    reason="Metadata similarity",
                    similarity_details={"metadata_similarity": 0.7}
                )
            ],
            strategy=RecommendationStrategy.METADATA_BASED
        )
        
        keyword_result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[
                Recommendation(
                    file_path="/path/to/file2.txt",
                    score=0.6,
                    reason="Keyword similarity (2 common keywords)",
                    keywords=[("keyword1", 0.9), ("keyword2", 0.8)]
                ),
                Recommendation(
                    file_path="/path/to/file3.txt",
                    score=0.5,
                    reason="Keyword similarity (1 common keyword)",
                    keywords=[("keyword3", 0.7)]
                )
            ],
            strategy=RecommendationStrategy.KEYWORD_BASED
        )
        
        # Mock the recommendation methods
        mock_content.return_value = content_result
        mock_metadata.return_value = metadata_result
        mock_keyword.return_value = keyword_result
        
        # Create engine with hybrid strategy
        options = RecommendationOptions(
            strategy=RecommendationStrategy.HYBRID,
            content_weight=0.6,
            metadata_weight=0.4,
            keyword_weight=0.3,
            min_similarity_score=0.3
        )
        engine = RecommendationEngine(options)
        
        # Generate recommendations
        result = engine.recommend_similar_files(
            target_file="/path/to/target.txt",
            file_list=[
                "/path/to/target.txt",
                "/path/to/file1.txt",
                "/path/to/file2.txt",
                "/path/to/file3.txt"
            ]
        )
        
        # Verify results
        self.assertEqual(result.target_file, "/path/to/target.txt")
        self.assertEqual(result.strategy, RecommendationStrategy.HYBRID)
        self.assertEqual(len(result.recommendations), 3)
        
        # Verify file1 (content + metadata)
        file1_rec = next(r for r in result.recommendations if r.file_path == "/path/to/file1.txt")
        self.assertAlmostEqual(file1_rec.score, 0.6*0.85 + 0.4*0.8)
        self.assertTrue("Content similarity" in file1_rec.reason)
        self.assertTrue("Metadata similarity" in file1_rec.reason)
        
        # Verify file2 (content + keyword)
        file2_rec = next(r for r in result.recommendations if r.file_path == "/path/to/file2.txt")
        self.assertAlmostEqual(file2_rec.score, 0.6*0.75 + 0.3*0.6)
        self.assertTrue("Content similarity" in file2_rec.reason)
        self.assertTrue("Keyword similarity" in file2_rec.reason)
        
        # Verify file3 (metadata + keyword)
        file3_rec = next(r for r in result.recommendations if r.file_path == "/path/to/file3.txt")
        self.assertAlmostEqual(file3_rec.score, 0.4*0.7 + 0.3*0.5)
        self.assertTrue("Metadata similarity" in file3_rec.reason)
        self.assertTrue("Keyword similarity" in file3_rec.reason)
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine.recommend_similar_files')
    def test_recommend_for_directory(self, mock_recommend):
        """Test recommending for a directory."""
        # Mock the recommend_similar_files method
        mock_result = RecommendationResult(
            target_file="/path/to/file1.txt",
            recommendations=[
                Recommendation(
                    file_path="/path/to/file2.txt",
                    score=0.85,
                    reason="Content similarity"
                )
            ],
            strategy=RecommendationStrategy.HYBRID
        )
        mock_recommend.return_value = mock_result
        
        # Mock os.walk to return a list of files
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("/path/to", [], ["file1.txt", "file2.txt", "file3.txt"])
            ]
            
            # Create engine
            engine = RecommendationEngine()
            
            # Generate recommendations for directory
            results = engine.recommend_for_directory("/path/to")
            
            # Verify results
            self.assertEqual(len(results), 3)
            self.assertIn("/path/to/file1.txt", results)
            self.assertIn("/path/to/file2.txt", results)
            self.assertIn("/path/to/file3.txt", results)
            self.assertEqual(results["/path/to/file1.txt"], mock_result)


class TestRecommendationFunctions(unittest.TestCase):
    """Test cases for recommendation functions."""
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine.recommend_similar_files')
    def test_recommend_similar_files_function(self, mock_recommend):
        """Test recommend_similar_files function."""
        # Mock the engine's recommend_similar_files method
        mock_result = RecommendationResult(
            target_file="/path/to/target.txt",
            recommendations=[
                Recommendation(
                    file_path="/path/to/file1.txt",
                    score=0.85,
                    reason="Content similarity"
                )
            ],
            strategy=RecommendationStrategy.HYBRID
        )
        mock_recommend.return_value = mock_result
        
        # Call the function
        result = recommend_similar_files(
            target_file="/path/to/target.txt",
            file_list=["/path/to/target.txt", "/path/to/file1.txt"]
        )
        
        # Verify result
        self.assertEqual(result, mock_result)
    
    @patch('science_data_kit.core.file_handling.recommendation_engine.RecommendationEngine.recommend_for_directory')
    def test_recommend_for_directory_function(self, mock_recommend):
        """Test recommend_for_directory function."""
        # Mock the engine's recommend_for_directory method
        mock_results = {
            "/path/to/file1.txt": RecommendationResult(
                target_file="/path/to/file1.txt",
                recommendations=[
                    Recommendation(
                        file_path="/path/to/file2.txt",
                        score=0.85,
                        reason="Content similarity"
                    )
                ],
                strategy=RecommendationStrategy.HYBRID
            )
        }
        mock_recommend.return_value = mock_results
        
        # Call the function
        results = recommend_for_directory("/path/to")
        
        # Verify results
        self.assertEqual(results, mock_results)


if __name__ == '__main__':
    unittest.main()
"""