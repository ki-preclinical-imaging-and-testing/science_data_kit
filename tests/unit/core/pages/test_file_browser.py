"""
Unit tests for the FileBrowserPage class.
"""

import os
import json
import yaml
import csv
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO, BytesIO

from science_data_kit.core.pages.file_browser import FileBrowserPage

class TestFileBrowserPage(unittest.TestCase):
    """Test cases for the FileBrowserPage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.page = FileBrowserPage()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        
        # Create a test file
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("Test content")

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    def test_export_metadata_json(self, mock_get_interpreter):
        """Test exporting metadata in JSON format."""
        # Mock the file interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.extract_metadata.return_value = {
            "width": 100,
            "height": 200,
            "format": "JPEG"
        }
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.json")
        result = self.page.export_metadata(self.test_file_path, 'json', output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(result, output_path)
        
        # Check the content of the file
        with open(output_path, 'r') as f:
            metadata = json.load(f)
            self.assertEqual(metadata["width"], 100)
            self.assertEqual(metadata["height"], 200)
            self.assertEqual(metadata["format"], "JPEG")
        
        # Test returning metadata without saving to a file
        result = self.page.export_metadata(self.test_file_path, 'json')
        self.assertIsInstance(result, dict)
        self.assertEqual(result["width"], 100)
        self.assertEqual(result["height"], 200)
        self.assertEqual(result["format"], "JPEG")

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    def test_export_metadata_yaml(self, mock_get_interpreter):
        """Test exporting metadata in YAML format."""
        # Mock the file interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.extract_metadata.return_value = {
            "width": 100,
            "height": 200,
            "format": "JPEG"
        }
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.yaml")
        result = self.page.export_metadata(self.test_file_path, 'yaml', output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(result, output_path)
        
        # Check the content of the file
        with open(output_path, 'r') as f:
            metadata = yaml.safe_load(f)
            self.assertEqual(metadata["width"], 100)
            self.assertEqual(metadata["height"], 200)
            self.assertEqual(metadata["format"], "JPEG")
        
        # Test returning metadata without saving to a file
        result = self.page.export_metadata(self.test_file_path, 'yaml')
        self.assertIsInstance(result, str)
        metadata = yaml.safe_load(result)
        self.assertEqual(metadata["width"], 100)
        self.assertEqual(metadata["height"], 200)
        self.assertEqual(metadata["format"], "JPEG")

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    def test_export_metadata_csv(self, mock_get_interpreter):
        """Test exporting metadata in CSV format."""
        # Mock the file interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.extract_metadata.return_value = {
            "width": 100,
            "height": 200,
            "format": "JPEG"
        }
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.csv")
        result = self.page.export_metadata(self.test_file_path, 'csv', output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(result, output_path)
        
        # Check the content of the file
        with open(output_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(rows[0], ['Key', 'Value'])
            self.assertIn(['width', '100'], rows)
            self.assertIn(['height', '200'], rows)
            self.assertIn(['format', 'JPEG'], rows)
        
        # Test returning metadata without saving to a file
        result = self.page.export_metadata(self.test_file_path, 'csv')
        self.assertIsInstance(result, dict)
        self.assertEqual(result["width"], "100")
        self.assertEqual(result["height"], "200")
        self.assertEqual(result["format"], "JPEG")

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    @patch('science_data_kit.core.pages.file_browser.PANDAS_AVAILABLE', True)
    @patch('science_data_kit.core.pages.file_browser.pd')
    def test_export_metadata_excel(self, mock_pd, mock_get_interpreter):
        """Test exporting metadata in Excel format."""
        # Skip test if pandas is not available
        if not hasattr(self.page, 'PANDAS_AVAILABLE') or not self.page.PANDAS_AVAILABLE:
            self.skipTest("Pandas is not available")
        
        # Mock the file interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.extract_metadata.return_value = {
            "width": 100,
            "height": 200,
            "format": "JPEG"
        }
        mock_get_interpreter.return_value = mock_interpreter
        
        # Mock pandas DataFrame and ExcelWriter
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df
        mock_writer = MagicMock()
        mock_pd.ExcelWriter.return_value.__enter__.return_value = mock_writer
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.xlsx")
        result = self.page.export_metadata(self.test_file_path, 'excel', output_path)
        
        # Check that pandas was called correctly
        mock_pd.DataFrame.assert_called_once()
        mock_df.to_excel.assert_called_once_with(output_path, sheet_name='Metadata', index=False)
        
        # Test returning metadata without saving to a file
        mock_output = MagicMock(spec=BytesIO)
        mock_pd.ExcelWriter.return_value.__enter__.return_value = mock_writer
        
        # Reset mock
        mock_pd.DataFrame.reset_mock()
        mock_df.to_excel.reset_mock()
        
        result = self.page.export_metadata(self.test_file_path, 'excel')
        
        # Check that pandas was called correctly
        mock_pd.DataFrame.assert_called_once()
        mock_df.to_excel.assert_called_once_with(mock_writer, sheet_name='Metadata', index=False)

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    def test_export_metadata_no_interpreter(self, mock_get_interpreter):
        """Test exporting metadata when no interpreter is available."""
        # Mock no interpreter available
        mock_get_interpreter.return_value = None
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.json")
        result = self.page.export_metadata(self.test_file_path, 'json', output_path)
        
        # Check that the result is None
        self.assertIsNone(result)
        
        # Check that the file was not created
        self.assertFalse(os.path.exists(output_path))
        
        # Test returning metadata without saving to a file
        result = self.page.export_metadata(self.test_file_path, 'json')
        self.assertIsNone(result)

    @patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file')
    def test_export_metadata_unsupported_format(self, mock_get_interpreter):
        """Test exporting metadata with an unsupported format."""
        # Mock the file interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.extract_metadata.return_value = {
            "width": 100,
            "height": 200,
            "format": "JPEG"
        }
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test exporting to a file
        output_path = os.path.join(self.test_dir, "metadata.xyz")
        result = self.page.export_metadata(self.test_file_path, 'xyz', output_path)
        
        # Check that the result is None
        self.assertIsNone(result)
        
        # Check that the file was not created
        self.assertFalse(os.path.exists(output_path))
        
        # Test returning metadata without saving to a file
        result = self.page.export_metadata(self.test_file_path, 'xyz')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()