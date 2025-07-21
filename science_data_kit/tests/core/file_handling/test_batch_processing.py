"""
Tests for the batch processing module.

This module contains tests for the batch processing functionality,
including the BatchProcessor class and the convenience functions.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from science_data_kit.core.file_handling.batch_processing import (
    BatchProcessor, BatchProcessingResult,
    batch_copy_files, batch_move_files, batch_delete_files, batch_rename_files,
    batch_extract_metadata, batch_generate_previews, batch_update_knowledge_graph,
    batch_export_metadata
)


class TestBatchProcessingResult(unittest.TestCase):
    """Tests for the BatchProcessingResult class."""

    def test_initialization(self):
        """Test initialization of BatchProcessingResult."""
        result = BatchProcessingResult()
        self.assertEqual(result.total_files, 0)
        self.assertEqual(result.processed_files, 0)
        self.assertEqual(result.success_count, 0)
        self.assertEqual(result.failure_count, 0)
        self.assertEqual(result.success_rate, 0)
        self.assertFalse(result.is_complete)

    def test_add_success(self):
        """Test adding a successful operation."""
        result = BatchProcessingResult()
        result.add_success("file1.txt", {"key": "value"})
        self.assertEqual(result.processed_files, 1)
        self.assertEqual(result.success_count, 1)
        self.assertEqual(result.failure_count, 0)
        self.assertEqual(result.success_rate, 100)
        self.assertEqual(result.successful_operations[0]["file_path"], "file1.txt")
        self.assertEqual(result.successful_operations[0]["details"], {"key": "value"})

    def test_add_failure(self):
        """Test adding a failed operation."""
        result = BatchProcessingResult()
        result.add_failure("file1.txt", "Error message", {"key": "value"})
        self.assertEqual(result.processed_files, 1)
        self.assertEqual(result.success_count, 0)
        self.assertEqual(result.failure_count, 1)
        self.assertEqual(result.success_rate, 0)
        self.assertEqual(result.failed_operations[0]["file_path"], "file1.txt")
        self.assertEqual(result.failed_operations[0]["error"], "Error message")
        self.assertEqual(result.failed_operations[0]["details"], {"key": "value"})

    def test_complete(self):
        """Test marking the batch processing as complete."""
        result = BatchProcessingResult()
        result.complete("test_operation")
        self.assertTrue(result.is_complete)
        self.assertEqual(result.operation_type, "test_operation")

    def test_summary(self):
        """Test getting a summary of the batch processing."""
        result = BatchProcessingResult()
        result.total_files = 10
        result.add_success("file1.txt")
        result.add_success("file2.txt")
        result.add_failure("file3.txt", "Error message")
        result.complete("test_operation")
        
        summary = result.summary
        self.assertEqual(summary["operation_type"], "test_operation")
        self.assertEqual(summary["total_files"], 10)
        self.assertEqual(summary["processed_files"], 3)
        self.assertEqual(summary["success_count"], 2)
        self.assertEqual(summary["failure_count"], 1)
        self.assertAlmostEqual(summary["success_rate"], 66.66666666666667)
        self.assertTrue(summary["is_complete"])


class TestBatchProcessor(unittest.TestCase):
    """Tests for the BatchProcessor class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create some test files
        self.test_files = []
        for i in range(5):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)
        
        # Create a destination directory for copy/move operations
        self.dest_dir = os.path.join(self.test_dir, "dest")
        os.makedirs(self.dest_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_process_files(self):
        """Test processing multiple files with a custom operation."""
        processor = BatchProcessor()
        
        # Define a simple operation that returns success for even-numbered files
        def test_operation(file_path):
            file_num = int(os.path.basename(file_path).split("_")[2].split(".")[0])
            if file_num % 2 == 0:
                return True, f"Success for {file_path}", {"file_num": file_num}
            else:
                return False, f"Failure for {file_path}", {"file_num": file_num}
        
        # Process the files
        result = processor.process_files(self.test_files, test_operation, "test_operation")
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.processed_files, 5)
        self.assertEqual(result.success_count, 3)  # Files 0, 2, 4
        self.assertEqual(result.failure_count, 2)  # Files 1, 3
        self.assertEqual(result.operation_type, "test_operation")
        self.assertTrue(result.is_complete)

    def test_copy_files(self):
        """Test copying multiple files."""
        processor = BatchProcessor()
        
        # Copy the files
        result = processor.copy_files(self.test_files, self.dest_dir)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the files were actually copied
        for file_path in self.test_files:
            dest_path = os.path.join(self.dest_dir, os.path.basename(file_path))
            self.assertTrue(os.path.exists(dest_path))
            
            # Check that the content is the same
            with open(file_path, "r") as f1, open(dest_path, "r") as f2:
                self.assertEqual(f1.read(), f2.read())

    def test_move_files(self):
        """Test moving multiple files."""
        processor = BatchProcessor()
        
        # Move the files
        result = processor.move_files(self.test_files, self.dest_dir)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the files were actually moved
        for file_path in self.test_files:
            # Original file should no longer exist
            self.assertFalse(os.path.exists(file_path))
            
            # Destination file should exist
            dest_path = os.path.join(self.dest_dir, os.path.basename(file_path))
            self.assertTrue(os.path.exists(dest_path))

    def test_delete_files(self):
        """Test deleting multiple files."""
        processor = BatchProcessor()
        
        # Delete the files
        result = processor.delete_files(self.test_files)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the files were actually deleted
        for file_path in self.test_files:
            self.assertFalse(os.path.exists(file_path))

    def test_rename_files(self):
        """Test renaming multiple files."""
        processor = BatchProcessor()
        
        # Create new names for the files
        new_names = [f"renamed_{i}.txt" for i in range(5)]
        
        # Rename the files
        result = processor.rename_files(self.test_files, new_names)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the files were actually renamed
        for i, file_path in enumerate(self.test_files):
            # Original file should no longer exist
            self.assertFalse(os.path.exists(file_path))
            
            # New file should exist
            new_path = os.path.join(os.path.dirname(file_path), new_names[i])
            self.assertTrue(os.path.exists(new_path))

    @patch('science_data_kit.core.file_handling.batch_processing.get_file_interpreter_for_file')
    def test_extract_metadata(self, mock_get_interpreter):
        """Test extracting metadata from multiple files."""
        # Create a mock interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.get_file_info.return_value = {"name": "test", "size": 100}
        mock_interpreter.extract_metadata.return_value = {"width": 800, "height": 600}
        
        # Configure the mock to return our mock interpreter
        mock_get_interpreter.return_value = mock_interpreter
        
        processor = BatchProcessor()
        
        # Extract metadata
        result = processor.extract_metadata(self.test_files)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the interpreter was called for each file
        self.assertEqual(mock_get_interpreter.call_count, 5)
        self.assertEqual(mock_interpreter.get_file_info.call_count, 5)
        self.assertEqual(mock_interpreter.extract_metadata.call_count, 5)
        
        # Check the metadata in the result
        for success in result.successful_operations:
            self.assertEqual(success["details"]["metadata"], {
                "name": "test", 
                "size": 100, 
                "width": 800, 
                "height": 600
            })

    @patch('science_data_kit.core.file_handling.batch_processing.get_file_interpreter_for_file')
    def test_generate_previews(self, mock_get_interpreter):
        """Test generating previews for multiple files."""
        # Create a mock interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.generate_preview.return_value = "preview_data"
        
        # Configure the mock to return our mock interpreter
        mock_get_interpreter.return_value = mock_interpreter
        
        processor = BatchProcessor()
        
        # Generate previews
        result = processor.generate_previews(self.test_files, self.dest_dir)
        
        # Check the result
        self.assertEqual(result.total_files, 5)
        self.assertEqual(result.success_count, 5)
        self.assertEqual(result.failure_count, 0)
        
        # Check that the interpreter was called for each file
        self.assertEqual(mock_get_interpreter.call_count, 5)
        self.assertEqual(mock_interpreter.generate_preview.call_count, 5)
        
        # Check the preview data in the result
        for success in result.successful_operations:
            self.assertEqual(success["details"]["preview"], "preview_data")


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for the convenience functions."""

    @patch('science_data_kit.core.file_handling.batch_processing.BatchProcessor')
    def test_batch_copy_files(self, mock_processor_class):
        """Test the batch_copy_files convenience function."""
        # Create a mock processor instance
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create a mock result
        mock_result = MagicMock()
        mock_processor.copy_files.return_value = mock_result
        
        # Call the convenience function
        result = batch_copy_files(["file1.txt", "file2.txt"], "dest_dir", True, 8)
        
        # Check that the processor was created with the right parameters
        mock_processor_class.assert_called_once_with(max_workers=8)
        
        # Check that the copy_files method was called with the right parameters
        mock_processor.copy_files.assert_called_once_with(
            ["file1.txt", "file2.txt"], "dest_dir", True
        )
        
        # Check that the result is what we expect
        self.assertEqual(result, mock_result)

    @patch('science_data_kit.core.file_handling.batch_processing.BatchProcessor')
    def test_batch_move_files(self, mock_processor_class):
        """Test the batch_move_files convenience function."""
        # Create a mock processor instance
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create a mock result
        mock_result = MagicMock()
        mock_processor.move_files.return_value = mock_result
        
        # Call the convenience function
        result = batch_move_files(["file1.txt", "file2.txt"], "dest_dir", True, 8)
        
        # Check that the processor was created with the right parameters
        mock_processor_class.assert_called_once_with(max_workers=8)
        
        # Check that the move_files method was called with the right parameters
        mock_processor.move_files.assert_called_once_with(
            ["file1.txt", "file2.txt"], "dest_dir", True
        )
        
        # Check that the result is what we expect
        self.assertEqual(result, mock_result)

    @patch('science_data_kit.core.file_handling.batch_processing.BatchProcessor')
    def test_batch_delete_files(self, mock_processor_class):
        """Test the batch_delete_files convenience function."""
        # Create a mock processor instance
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create a mock result
        mock_result = MagicMock()
        mock_processor.delete_files.return_value = mock_result
        
        # Call the convenience function
        result = batch_delete_files(["file1.txt", "file2.txt"], 8)
        
        # Check that the processor was created with the right parameters
        mock_processor_class.assert_called_once_with(max_workers=8)
        
        # Check that the delete_files method was called with the right parameters
        mock_processor.delete_files.assert_called_once_with(["file1.txt", "file2.txt"])
        
        # Check that the result is what we expect
        self.assertEqual(result, mock_result)

    @patch('science_data_kit.core.file_handling.batch_processing.BatchProcessor')
    def test_batch_rename_files(self, mock_processor_class):
        """Test the batch_rename_files convenience function."""
        # Create a mock processor instance
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create a mock result
        mock_result = MagicMock()
        mock_processor.rename_files.return_value = mock_result
        
        # Call the convenience function
        result = batch_rename_files(["file1.txt", "file2.txt"], ["new1.txt", "new2.txt"], 8)
        
        # Check that the processor was created with the right parameters
        mock_processor_class.assert_called_once_with(max_workers=8)
        
        # Check that the rename_files method was called with the right parameters
        mock_processor.rename_files.assert_called_once_with(
            ["file1.txt", "file2.txt"], ["new1.txt", "new2.txt"]
        )
        
        # Check that the result is what we expect
        self.assertEqual(result, mock_result)


if __name__ == '__main__':
    unittest.main()