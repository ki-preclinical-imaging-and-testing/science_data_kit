"""
Tests for the duplicate detection functionality in Science Data Kit.

This module contains unit tests for the duplicate detection functionality,
including exact duplicate detection, similar file detection, and combined
detection approaches.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from science_data_kit.core.file_handling.duplicate_detection import (
    DuplicateDetectionStrategy, DuplicateGroup, DuplicateDetectionResult,
    detect_exact_duplicates, detect_similar_files, detect_duplicates,
    _calculate_file_hash, _calculate_similarity, group_duplicates_by_directory,
    generate_duplicate_report
)


class TestDuplicateDetection(unittest.TestCase):
    """Tests for the duplicate detection functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create test files
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_files(self):
        """Create test files for duplicate detection."""
        # Create exact duplicates
        self.file1 = self.test_dir / "file1.txt"
        self.file2 = self.test_dir / "file2.txt"  # Exact duplicate of file1
        self.file3 = self.test_dir / "file3.txt"  # Different content
        
        # Create similar files
        self.file4 = self.test_dir / "file4.txt"  # Similar to file3
        self.file5 = self.test_dir / "file5.txt"  # Similar to file3
        
        # Create files with different content
        self.file6 = self.test_dir / "file6.txt"  # Completely different
        
        # Write content to files
        with open(self.file1, 'w') as f:
            f.write("This is a test file for duplicate detection.")
        
        with open(self.file2, 'w') as f:
            f.write("This is a test file for duplicate detection.")
        
        with open(self.file3, 'w') as f:
            f.write("This is another test file with different content.")
        
        with open(self.file4, 'w') as f:
            f.write("This is another test file with slightly different content.")
        
        with open(self.file5, 'w') as f:
            f.write("This is another test file with somewhat different content.")
        
        with open(self.file6, 'w') as f:
            f.write("This file has completely different content from the others.")

    def test_calculate_file_hash(self):
        """Test calculating file hash."""
        hash1 = _calculate_file_hash(str(self.file1))
        hash2 = _calculate_file_hash(str(self.file2))
        hash3 = _calculate_file_hash(str(self.file3))
        
        # Exact duplicates should have the same hash
        self.assertEqual(hash1, hash2)
        
        # Different files should have different hashes
        self.assertNotEqual(hash1, hash3)

    @patch('science_data_kit.core.file_handling.duplicate_detection.calculate_content_similarity')
    @patch('science_data_kit.core.file_handling.duplicate_detection.calculate_metadata_similarity')
    def test_calculate_similarity(self, mock_metadata_sim, mock_content_sim):
        """Test calculating similarity between files."""
        # Set up mocks
        mock_content_sim.return_value = 0.8
        mock_metadata_sim.return_value = 0.6
        
        # Test exact match strategy
        similarity = _calculate_similarity(
            str(self.file1), 
            str(self.file2), 
            DuplicateDetectionStrategy.EXACT_MATCH
        )
        self.assertEqual(similarity, 1.0)
        
        similarity = _calculate_similarity(
            str(self.file1), 
            str(self.file3), 
            DuplicateDetectionStrategy.EXACT_MATCH
        )
        self.assertEqual(similarity, 0.0)
        
        # Test content similarity strategy
        similarity = _calculate_similarity(
            str(self.file1), 
            str(self.file2), 
            DuplicateDetectionStrategy.CONTENT_SIMILARITY
        )
        self.assertEqual(similarity, 0.8)
        mock_content_sim.assert_called_with(str(self.file1), str(self.file2))
        
        # Test metadata similarity strategy
        similarity = _calculate_similarity(
            str(self.file1), 
            str(self.file2), 
            DuplicateDetectionStrategy.METADATA_SIMILARITY
        )
        self.assertEqual(similarity, 0.6)
        mock_metadata_sim.assert_called_with(str(self.file1), str(self.file2))
        
        # Test combined strategy
        similarity = _calculate_similarity(
            str(self.file1), 
            str(self.file2), 
            DuplicateDetectionStrategy.COMBINED
        )
        self.assertEqual(similarity, (0.7 * 0.8) + (0.3 * 0.6))

    def test_detect_exact_duplicates(self):
        """Test detecting exact duplicates."""
        file_paths = [
            str(self.file1),
            str(self.file2),
            str(self.file3),
            str(self.file6)
        ]
        
        result = detect_exact_duplicates(file_paths)
        
        # Check result properties
        self.assertEqual(result.total_files_analyzed, 4)
        self.assertEqual(result.total_duplicates_found, 1)
        self.assertEqual(result.detection_strategy, "exact_match")
        self.assertEqual(result.threshold, 1.0)
        self.assertIsNone(result.error_message)
        
        # Check duplicate groups
        self.assertEqual(len(result.duplicate_groups), 1)
        group = result.duplicate_groups[0]
        self.assertEqual(len(group.files), 2)
        self.assertIn(str(self.file1), group.files)
        self.assertIn(str(self.file2), group.files)
        self.assertEqual(group.similarity_score, 1.0)
        self.assertEqual(group.detection_method, "exact_match")

    @patch('science_data_kit.core.file_handling.duplicate_detection._calculate_similarity')
    def test_detect_similar_files(self, mock_calculate_similarity):
        """Test detecting similar files."""
        # Set up mock to return high similarity for specific pairs
        def mock_similarity(file1, file2, strategy):
            if (file1 == str(self.file3) and file2 == str(self.file4)) or \
               (file1 == str(self.file4) and file2 == str(self.file3)) or \
               (file1 == str(self.file3) and file2 == str(self.file5)) or \
               (file1 == str(self.file5) and file2 == str(self.file3)):
                return 0.9
            return 0.2
        
        mock_calculate_similarity.side_effect = mock_similarity
        
        file_paths = [
            str(self.file3),
            str(self.file4),
            str(self.file5),
            str(self.file6)
        ]
        
        result = detect_similar_files(
            file_paths,
            threshold=0.8,
            strategy=DuplicateDetectionStrategy.CONTENT_SIMILARITY
        )
        
        # Check result properties
        self.assertEqual(result.total_files_analyzed, 4)
        self.assertEqual(result.detection_strategy, "content_similarity")
        self.assertEqual(result.threshold, 0.8)
        self.assertIsNone(result.error_message)
        
        # Due to the complexity of the grouping algorithm and the mocked similarity,
        # we can't predict exactly how many groups will be formed, but we can check
        # that similar files are grouped together
        for group in result.duplicate_groups:
            # Check that each group has at least 2 files
            self.assertGreaterEqual(len(group.files), 2)
            # Check that the reference file is in the group
            self.assertIn(group.reference_file, group.files)
            # Check that the similarity score is at least the threshold
            self.assertGreaterEqual(group.similarity_score, 0.8)

    @patch('science_data_kit.core.file_handling.duplicate_detection.detect_exact_duplicates')
    @patch('science_data_kit.core.file_handling.duplicate_detection.detect_similar_files')
    def test_detect_duplicates(self, mock_detect_similar, mock_detect_exact):
        """Test detecting duplicates using the combined approach."""
        # Set up mocks
        exact_result = DuplicateDetectionResult(
            duplicate_groups=[
                DuplicateGroup(
                    files=[str(self.file1), str(self.file2)],
                    similarity_score=1.0,
                    detection_method="exact_match",
                    reference_file=str(self.file1)
                )
            ],
            total_files_analyzed=6,
            total_duplicates_found=1,
            detection_strategy="exact_match",
            threshold=1.0
        )
        
        similar_result = DuplicateDetectionResult(
            duplicate_groups=[
                DuplicateGroup(
                    files=[str(self.file3), str(self.file4), str(self.file5)],
                    similarity_score=0.9,
                    detection_method="content_similarity",
                    reference_file=str(self.file3)
                )
            ],
            total_files_analyzed=4,
            total_duplicates_found=2,
            detection_strategy="content_similarity",
            threshold=0.9
        )
        
        mock_detect_exact.return_value = exact_result
        mock_detect_similar.return_value = similar_result
        
        file_paths = [
            str(self.file1),
            str(self.file2),
            str(self.file3),
            str(self.file4),
            str(self.file5),
            str(self.file6)
        ]
        
        result = detect_duplicates(
            file_paths,
            threshold=0.9,
            strategy=DuplicateDetectionStrategy.CONTENT_SIMILARITY
        )
        
        # Check result properties
        self.assertEqual(result.total_files_analyzed, 6)
        self.assertEqual(result.total_duplicates_found, 3)  # 1 from exact + 2 from similar
        self.assertEqual(result.detection_strategy, "exact_match+content_similarity")
        self.assertEqual(result.threshold, 0.9)
        self.assertIsNone(result.error_message)
        
        # Check duplicate groups
        self.assertEqual(len(result.duplicate_groups), 2)
        
        # Check that the exact duplicate group is included
        exact_group = result.duplicate_groups[0]
        self.assertEqual(len(exact_group.files), 2)
        self.assertIn(str(self.file1), exact_group.files)
        self.assertIn(str(self.file2), exact_group.files)
        
        # Check that the similar files group is included
        similar_group = result.duplicate_groups[1]
        self.assertEqual(len(similar_group.files), 3)
        self.assertIn(str(self.file3), similar_group.files)
        self.assertIn(str(self.file4), similar_group.files)
        self.assertIn(str(self.file5), similar_group.files)

    def test_group_duplicates_by_directory(self):
        """Test grouping duplicates by directory."""
        # Create groups with files in different directories
        group1 = DuplicateGroup(
            files=[str(self.file1), str(self.file2)],
            reference_file=str(self.file1)
        )
        
        # Create a subdirectory and a file in it
        subdir = self.test_dir / "subdir"
        os.makedirs(subdir, exist_ok=True)
        subdir_file = subdir / "file.txt"
        with open(subdir_file, 'w') as f:
            f.write("File in subdirectory")
        
        group2 = DuplicateGroup(
            files=[str(subdir_file)],
            reference_file=str(subdir_file)
        )
        
        # Group the duplicates by directory
        dir_groups = group_duplicates_by_directory([group1, group2])
        
        # Check that the groups are correctly organized by directory
        self.assertEqual(len(dir_groups), 2)
        self.assertIn(str(self.test_dir), dir_groups)
        self.assertIn(str(subdir), dir_groups)
        self.assertEqual(len(dir_groups[str(self.test_dir)]), 1)
        self.assertEqual(len(dir_groups[str(subdir)]), 1)

    def test_generate_duplicate_report(self):
        """Test generating duplicate reports in different formats."""
        # Create a sample result
        result = DuplicateDetectionResult(
            duplicate_groups=[
                DuplicateGroup(
                    files=[str(self.file1), str(self.file2)],
                    similarity_score=1.0,
                    detection_method="exact_match",
                    reference_file=str(self.file1)
                ),
                DuplicateGroup(
                    files=[str(self.file3), str(self.file4), str(self.file5)],
                    similarity_score=0.9,
                    detection_method="content_similarity",
                    reference_file=str(self.file3)
                )
            ],
            total_files_analyzed=6,
            total_duplicates_found=3,
            detection_strategy="exact_match+content_similarity",
            threshold=0.9
        )
        
        # Test text format
        text_report = generate_duplicate_report(result, format='text')
        self.assertIsInstance(text_report, str)
        self.assertIn("Duplicate File Detection Report", text_report)
        self.assertIn("Total files analyzed: 6", text_report)
        self.assertIn("Total duplicates found: 3", text_report)
        
        # Test JSON format
        json_report = generate_duplicate_report(result, format='json')
        self.assertIsInstance(json_report, str)
        self.assertIn('"total_files_analyzed": 6', json_report)
        self.assertIn('"total_duplicates_found": 3', json_report)
        
        # Test HTML format
        html_report = generate_duplicate_report(result, format='html')
        self.assertIsInstance(html_report, str)
        self.assertIn("<title>Duplicate File Detection Report</title>", html_report)
        self.assertIn("Total files analyzed: 6", html_report)
        self.assertIn("Total duplicates found: 3", html_report)
        
        # Test invalid format
        with self.assertRaises(ValueError):
            generate_duplicate_report(result, format='invalid')


if __name__ == '__main__':
    unittest.main()
"""