"""
Tests for the table extraction module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.file_handling.table_extraction import (
    TableExtractor, TableExtractionOptions, TableExtractionResult, Table,
    TableFormat, get_table_extractor_for_file, extract_tables_from_file,
    PDFTableExtractor
)
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, StructuredDataExtractionCapability
)


class MockStructuredDataExtractor(FileInterpreterPlugin, StructuredDataExtractionCapability):
    """Mock file interpreter with structured data extraction capability for testing."""
    
    def __init__(self):
        self._metadata = MagicMock()
        self._metadata.name = "MockStructuredDataExtractor"
        self._metadata.capabilities = ["structured_data_extraction"]
    
    @property
    def metadata(self):
        return self._metadata
    
    def initialize(self):
        return True
    
    def shutdown(self):
        return True
    
    def can_interpret(self, file_path, mime_type=None):
        return file_path.endswith('.xlsx') or file_path.endswith('.csv')
    
    def get_supported_extensions(self):
        return ['.xlsx', '.csv']
    
    def get_supported_mime_types(self):
        return ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']
    
    def extract_metadata(self, file_path):
        return {'filename': os.path.basename(file_path)}
    
    def generate_preview(self, file_path, output_path=None, **kwargs):
        return "Preview content"
    
    def extract_structured_data(self, file_path, data_type, **kwargs):
        if data_type != 'table':
            return None
        
        # Mock table data
        if file_path.endswith('.xlsx'):
            return [
                {
                    'data': [
                        ['Row 1, Cell 1', 'Row 1, Cell 2', 'Row 1, Cell 3'],
                        ['Row 2, Cell 1', 'Row 2, Cell 2', 'Row 2, Cell 3'],
                        ['Row 3, Cell 1', 'Row 3, Cell 2', 'Row 3, Cell 3']
                    ],
                    'headers': ['Column 1', 'Column 2', 'Column 3'],
                    'sheet_name': 'Sheet1',
                    'page_number': 1
                },
                {
                    'data': [
                        ['Row 1, Cell 1', 'Row 1, Cell 2'],
                        ['Row 2, Cell 1', 'Row 2, Cell 2']
                    ],
                    'headers': ['Column A', 'Column B'],
                    'sheet_name': 'Sheet2',
                    'page_number': 2
                }
            ]
        elif file_path.endswith('.csv'):
            return {
                'data': [
                    ['Row 1, Cell 1', 'Row 1, Cell 2', 'Row 1, Cell 3'],
                    ['Row 2, Cell 1', 'Row 2, Cell 2', 'Row 2, Cell 3'],
                    ['Row 3, Cell 1', 'Row 3, Cell 2', 'Row 3, Cell 3']
                ],
                'headers': ['Column 1', 'Column 2', 'Column 3']
            }
        
        return None
    
    def get_supported_data_types(self):
        return ['table', 'chart']
    
    def get_extraction_options(self, data_type):
        if data_type == 'table':
            return {
                'sheet_name': 'string or list of strings',
                'header_row': 'integer',
                'use_columns': 'list of strings or integers'
            }
        return {}


class TestTableExtraction(unittest.TestCase):
    """Test cases for the table extraction module."""
    
    @patch('science_data_kit.core.file_handling.table_extraction.get_file_interpreter_for_file')
    def test_get_table_extractor_for_file(self, mock_get_interpreter):
        """Test getting a table extractor for a file."""
        # Set up the mock
        mock_interpreter = MockStructuredDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test getting an extractor for a supported file
        extractor = get_table_extractor_for_file('/path/to/data.xlsx')
        self.assertIsNotNone(extractor)
        self.assertTrue(extractor.can_extract('/path/to/data.xlsx'))
        
        # Test getting an extractor for an unsupported file
        mock_get_interpreter.return_value = None
        extractor = get_table_extractor_for_file('/path/to/document.txt')
        self.assertIsNone(extractor)
    
    @patch('science_data_kit.core.file_handling.table_extraction.get_file_interpreter_for_file')
    def test_extract_tables_from_xlsx(self, mock_get_interpreter):
        """Test extracting tables from an XLSX file."""
        # Set up the mock
        mock_interpreter = MockStructuredDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test extracting tables
        options = TableExtractionOptions(
            format=TableFormat.CSV,
            include_headers=True
        )
        result = extract_tables_from_file('/path/to/data.xlsx', options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.format, TableFormat.CSV)
        self.assertEqual(len(result.tables), 2)
        
        # Check first table
        table1 = result.tables[0]
        self.assertEqual(len(table1.data), 3)
        self.assertEqual(len(table1.headers), 3)
        self.assertEqual(table1.headers[0], 'Column 1')
        self.assertEqual(table1.data[0][0], 'Row 1, Cell 1')
        self.assertEqual(table1.page_number, 1)
        
        # Check second table
        table2 = result.tables[1]
        self.assertEqual(len(table2.data), 2)
        self.assertEqual(len(table2.headers), 2)
        self.assertEqual(table2.headers[0], 'Column A')
        self.assertEqual(table2.data[0][0], 'Row 1, Cell 1')
        self.assertEqual(table2.page_number, 2)
    
    @patch('science_data_kit.core.file_handling.table_extraction.get_file_interpreter_for_file')
    def test_extract_tables_from_csv(self, mock_get_interpreter):
        """Test extracting tables from a CSV file."""
        # Set up the mock
        mock_interpreter = MockStructuredDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test extracting tables
        options = TableExtractionOptions(
            format=TableFormat.JSON,
            include_headers=True
        )
        result = extract_tables_from_file('/path/to/data.csv', options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.format, TableFormat.JSON)
        self.assertEqual(len(result.tables), 1)
        
        # Check the table
        table = result.tables[0]
        self.assertEqual(len(table.data), 3)
        self.assertEqual(len(table.headers), 3)
        self.assertEqual(table.headers[0], 'Column 1')
        self.assertEqual(table.data[0][0], 'Row 1, Cell 1')
    
    @patch('science_data_kit.core.file_handling.table_extraction.get_file_interpreter_for_file')
    def test_extract_tables_with_no_extractor(self, mock_get_interpreter):
        """Test extracting tables when no extractor is available."""
        # Set up the mock to return None
        mock_get_interpreter.return_value = None
        
        # Test extracting tables
        result = extract_tables_from_file('/path/to/unsupported.file')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(len(result.tables), 0)
        self.assertIsNotNone(result.error_message)
    
    @patch('science_data_kit.core.file_handling.table_extraction.get_file_interpreter_for_file')
    def test_extract_tables_with_no_tables_found(self, mock_get_interpreter):
        """Test extracting tables when no tables are found in the file."""
        # Set up the mock to return an empty result
        mock_interpreter = MockStructuredDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Override the extract_structured_data method to return None
        mock_interpreter.extract_structured_data = MagicMock(return_value=None)
        
        # Test extracting tables
        result = extract_tables_from_file('/path/to/empty.xlsx')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(len(result.tables), 0)
        self.assertIn('No tables found', result.error_message)
    
    def test_pdf_table_extractor(self):
        """Test the PDF table extractor."""
        # Create extractor
        extractor = PDFTableExtractor()
        
        # Test supported extensions and MIME types
        self.assertEqual(extractor.get_supported_extensions(), ['.pdf'])
        self.assertEqual(extractor.get_supported_mime_types(), ['application/pdf'])
        
        # Test supported formats
        formats = extractor.get_supported_formats()
        self.assertIn(TableFormat.CSV, formats)
        self.assertIn(TableFormat.JSON, formats)
        self.assertIn(TableFormat.DICT, formats)
        
        # Test extraction options
        options = extractor.get_extraction_options()
        self.assertIn('format', options)
        self.assertIn('include_headers', options)
        self.assertIn('page_numbers', options)


if __name__ == '__main__':
    unittest.main()