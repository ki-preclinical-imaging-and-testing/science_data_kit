"""
Tests for the text extraction framework.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractor, TextExtractionOptions, TextExtractionResult, TextExtractionFormat,
    get_text_extractor_for_file, extract_text_from_file
)
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, TextExtractionCapability
)


class MockFileInterpreter(FileInterpreterPlugin, TextExtractionCapability):
    """Mock file interpreter for testing."""
    
    def __init__(self):
        self._metadata = MagicMock()
        self._metadata.name = "MockFileInterpreter"
        self._metadata.capabilities = ["text_extraction"]
    
    @property
    def metadata(self):
        return self._metadata
    
    def initialize(self):
        return True
    
    def shutdown(self):
        return True
    
    def can_interpret(self, file_path, mime_type=None):
        return file_path.endswith('.txt')
    
    def get_supported_extensions(self):
        return ['.txt']
    
    def get_supported_mime_types(self):
        return ['text/plain']
    
    def extract_metadata(self, file_path):
        return {'filename': os.path.basename(file_path)}
    
    def generate_preview(self, file_path, output_path=None, **kwargs):
        return "Preview content"
    
    def extract_text(self, file_path, **kwargs):
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def get_text_extraction_options(self):
        return {'encoding': ['utf-8', 'latin-1', 'ascii']}


class TestTextExtraction(unittest.TestCase):
    """Test cases for the text extraction framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary text file for testing
        self.test_file = '/tmp/test_file.txt'
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('This is a test file.\nIt has multiple lines.\nFor testing text extraction.')
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    @patch('science_data_kit.core.file_handling.text_extraction.get_file_interpreter_for_file')
    def test_get_text_extractor_for_file(self, mock_get_interpreter):
        """Test getting a text extractor for a file."""
        # Set up the mock
        mock_interpreter = MockFileInterpreter()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test getting an extractor
        extractor = get_text_extractor_for_file(self.test_file)
        self.assertIsNotNone(extractor)
        self.assertTrue(extractor.can_extract(self.test_file))
    
    @patch('science_data_kit.core.file_handling.text_extraction.get_file_interpreter_for_file')
    def test_extract_text_from_file(self, mock_get_interpreter):
        """Test extracting text from a file."""
        # Set up the mock
        mock_interpreter = MockFileInterpreter()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test extracting text
        options = TextExtractionOptions(
            format=TextExtractionFormat.PLAIN,
            include_metadata=True
        )
        result = extract_text_from_file(self.test_file, options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.format, TextExtractionFormat.PLAIN)
        self.assertIn('This is a test file.', result.text)
        self.assertIn('It has multiple lines.', result.text)
        self.assertIn('For testing text extraction.', result.text)
        self.assertIn('filename', result.metadata)
        self.assertEqual(result.metadata['filename'], 'test_file.txt')
    
    @patch('science_data_kit.core.file_handling.text_extraction.get_file_interpreter_for_file')
    def test_extract_text_with_no_extractor(self, mock_get_interpreter):
        """Test extracting text when no extractor is available."""
        # Set up the mock to return None
        mock_get_interpreter.return_value = None
        
        # Test extracting text
        result = extract_text_from_file('/tmp/nonexistent.xyz')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.text, '')
        self.assertIsNotNone(result.error_message)


if __name__ == '__main__':
    unittest.main()