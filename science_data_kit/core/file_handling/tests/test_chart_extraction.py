"""
Tests for the chart data extraction module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.file_handling.chart_extraction import (
    ChartExtractor, ChartExtractionOptions, ChartExtractionResult, ChartData,
    ChartType, ChartDataFormat, get_chart_extractor_for_file, extract_charts_from_file,
    ImageBasedChartExtractor
)
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, StructuredDataExtractionCapability
)


class MockChartDataExtractor(FileInterpreterPlugin, StructuredDataExtractionCapability):
    """Mock file interpreter with structured data extraction capability for testing."""
    
    def __init__(self):
        self._metadata = MagicMock()
        self._metadata.name = "MockChartDataExtractor"
        self._metadata.capabilities = ["structured_data_extraction"]
    
    @property
    def metadata(self):
        return self._metadata
    
    def initialize(self):
        return True
    
    def shutdown(self):
        return True
    
    def can_interpret(self, file_path, mime_type=None):
        return file_path.endswith('.pptx') or file_path.endswith('.xlsx')
    
    def get_supported_extensions(self):
        return ['.pptx', '.xlsx']
    
    def get_supported_mime_types(self):
        return [
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
    
    def extract_metadata(self, file_path):
        return {'filename': os.path.basename(file_path)}
    
    def generate_preview(self, file_path, output_path=None, **kwargs):
        return "Preview content"
    
    def extract_structured_data(self, file_path, data_type, **kwargs):
        if data_type != 'chart':
            return None
        
        # Mock chart data
        if file_path.endswith('.pptx'):
            return [
                {
                    'data': [
                        [1, 10],
                        [2, 20],
                        [3, 15],
                        [4, 25],
                        [5, 30]
                    ],
                    'headers': ['X', 'Y'],
                    'chart_type': 'bar',
                    'title': 'Sample Bar Chart',
                    'x_label': 'X Axis',
                    'y_label': 'Y Axis',
                    'legend': ['Series 1'],
                    'page_number': 1
                },
                {
                    'data': [
                        [1, 5, 8],
                        [2, 10, 12],
                        [3, 15, 18],
                        [4, 20, 22]
                    ],
                    'headers': ['X', 'Y1', 'Y2'],
                    'chart_type': 'line',
                    'title': 'Sample Line Chart',
                    'x_label': 'X Axis',
                    'y_label': 'Y Axis',
                    'legend': ['Series 1', 'Series 2'],
                    'page_number': 2
                }
            ]
        elif file_path.endswith('.xlsx'):
            return {
                'data': [
                    ['Category A', 30],
                    ['Category B', 25],
                    ['Category C', 15],
                    ['Category D', 10],
                    ['Category E', 20]
                ],
                'headers': ['Category', 'Value'],
                'chart_type': 'pie',
                'title': 'Sample Pie Chart',
                'legend': ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'],
                'sheet_name': 'Sheet1'
            }
        
        return None
    
    def get_supported_data_types(self):
        return ['table', 'chart']
    
    def get_extraction_options(self, data_type):
        if data_type == 'chart':
            return {
                'chart_types': ['bar', 'line', 'pie', 'scatter'],
                'include_data_labels': 'boolean',
                'include_trend_lines': 'boolean'
            }
        return {}


class TestChartExtraction(unittest.TestCase):
    """Test cases for the chart data extraction module."""
    
    @patch('science_data_kit.core.file_handling.chart_extraction.get_file_interpreter_for_file')
    def test_get_chart_extractor_for_file(self, mock_get_interpreter):
        """Test getting a chart extractor for a file."""
        # Set up the mock
        mock_interpreter = MockChartDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test getting an extractor for a supported file
        extractor = get_chart_extractor_for_file('/path/to/presentation.pptx')
        self.assertIsNotNone(extractor)
        self.assertTrue(extractor.can_extract('/path/to/presentation.pptx'))
        
        # Test getting an extractor for an unsupported file
        mock_get_interpreter.return_value = None
        extractor = get_chart_extractor_for_file('/path/to/document.txt')
        self.assertIsNone(extractor)
    
    @patch('science_data_kit.core.file_handling.chart_extraction.get_file_interpreter_for_file')
    def test_extract_charts_from_pptx(self, mock_get_interpreter):
        """Test extracting charts from a PPTX file."""
        # Set up the mock
        mock_interpreter = MockChartDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test extracting charts
        options = ChartExtractionOptions(
            format=ChartDataFormat.CSV,
            extract_chart_title=True,
            extract_axis_labels=True,
            extract_legend=True
        )
        result = extract_charts_from_file('/path/to/presentation.pptx', options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.format, ChartDataFormat.CSV)
        self.assertEqual(len(result.charts), 2)
        
        # Check first chart
        chart1 = result.charts[0]
        self.assertEqual(len(chart1.data), 5)
        self.assertEqual(len(chart1.headers), 2)
        self.assertEqual(chart1.headers[0], 'X')
        self.assertEqual(chart1.data[0][0], 1)
        self.assertEqual(chart1.data[0][1], 10)
        self.assertEqual(chart1.chart_type, ChartType.BAR)
        self.assertEqual(chart1.title, 'Sample Bar Chart')
        self.assertEqual(chart1.x_label, 'X Axis')
        self.assertEqual(chart1.y_label, 'Y Axis')
        self.assertEqual(chart1.legend, ['Series 1'])
        self.assertEqual(chart1.page_number, 1)
        
        # Check second chart
        chart2 = result.charts[1]
        self.assertEqual(len(chart2.data), 4)
        self.assertEqual(len(chart2.headers), 3)
        self.assertEqual(chart2.headers[0], 'X')
        self.assertEqual(chart2.data[0][0], 1)
        self.assertEqual(chart2.data[0][1], 5)
        self.assertEqual(chart2.data[0][2], 8)
        self.assertEqual(chart2.chart_type, ChartType.LINE)
        self.assertEqual(chart2.title, 'Sample Line Chart')
        self.assertEqual(chart2.x_label, 'X Axis')
        self.assertEqual(chart2.y_label, 'Y Axis')
        self.assertEqual(chart2.legend, ['Series 1', 'Series 2'])
        self.assertEqual(chart2.page_number, 2)
    
    @patch('science_data_kit.core.file_handling.chart_extraction.get_file_interpreter_for_file')
    def test_extract_charts_from_xlsx(self, mock_get_interpreter):
        """Test extracting charts from an XLSX file."""
        # Set up the mock
        mock_interpreter = MockChartDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Test extracting charts
        options = ChartExtractionOptions(
            format=ChartDataFormat.JSON,
            extract_chart_title=True,
            extract_legend=True
        )
        result = extract_charts_from_file('/path/to/spreadsheet.xlsx', options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.format, ChartDataFormat.JSON)
        self.assertEqual(len(result.charts), 1)
        
        # Check the chart
        chart = result.charts[0]
        self.assertEqual(len(chart.data), 5)
        self.assertEqual(len(chart.headers), 2)
        self.assertEqual(chart.headers[0], 'Category')
        self.assertEqual(chart.data[0][0], 'Category A')
        self.assertEqual(chart.data[0][1], 30)
        self.assertEqual(chart.chart_type, ChartType.PIE)
        self.assertEqual(chart.title, 'Sample Pie Chart')
        self.assertEqual(chart.legend, ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'])
    
    @patch('science_data_kit.core.file_handling.chart_extraction.get_file_interpreter_for_file')
    def test_extract_charts_with_no_extractor(self, mock_get_interpreter):
        """Test extracting charts when no extractor is available."""
        # Set up the mock to return None
        mock_get_interpreter.return_value = None
        
        # Test extracting charts
        result = extract_charts_from_file('/path/to/unsupported.file')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(len(result.charts), 0)
        self.assertIsNotNone(result.error_message)
    
    @patch('science_data_kit.core.file_handling.chart_extraction.get_file_interpreter_for_file')
    def test_extract_charts_with_no_charts_found(self, mock_get_interpreter):
        """Test extracting charts when no charts are found in the file."""
        # Set up the mock to return an empty result
        mock_interpreter = MockChartDataExtractor()
        mock_get_interpreter.return_value = mock_interpreter
        
        # Override the extract_structured_data method to return None
        mock_interpreter.extract_structured_data = MagicMock(return_value=None)
        
        # Test extracting charts
        result = extract_charts_from_file('/path/to/empty.pptx')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(len(result.charts), 0)
        self.assertIn('No charts found', result.error_message)
    
    @patch('science_data_kit.core.file_handling.chart_extraction.cv2')
    @patch('science_data_kit.core.file_handling.chart_extraction.np')
    def test_image_based_chart_extractor(self, mock_np, mock_cv2):
        """Test the ImageBasedChartExtractor."""
        # Mock cv2.imread to return a valid image
        mock_image = MagicMock()
        mock_cv2.imread.return_value = mock_image
        
        # Create extractor
        extractor = ImageBasedChartExtractor()
        
        # Test supported extensions and MIME types
        self.assertEqual(extractor.get_supported_extensions(), ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'])
        self.assertIn('image/png', extractor.get_supported_mime_types())
        self.assertIn('image/jpeg', extractor.get_supported_mime_types())
        
        # Test supported formats
        formats = extractor.get_supported_formats()
        self.assertIn(ChartDataFormat.CSV, formats)
        self.assertIn(ChartDataFormat.JSON, formats)
        self.assertIn(ChartDataFormat.DICT, formats)
        
        # Test extraction options
        options = extractor.get_extraction_options()
        self.assertIn('format', options)
        self.assertIn('chart_types', options)
        self.assertIn('detect_chart_type', options)
        self.assertIn('extract_chart_title', options)
        self.assertIn('extract_axis_labels', options)
        self.assertIn('extract_legend', options)


if __name__ == '__main__':
    unittest.main()