"""
Tests for the OCR module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.file_handling.ocr import (
    OCRExtractor, OCROptions, OCREngine
)
from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions, TextExtractionFormat
)


class TestOCR(unittest.TestCase):
    """Test cases for the OCR module."""
    
    def test_ocr_extractor_initialization(self):
        """Test initializing the OCR extractor."""
        # Test with default options
        extractor = OCRExtractor()
        self.assertEqual(extractor.options.engine, OCREngine.AUTO)
        self.assertEqual(extractor.options.language, "eng")
        
        # Test with custom options
        options = OCROptions(
            engine=OCREngine.TESSERACT,
            language="fra",
            dpi=150
        )
        extractor = OCRExtractor(options)
        self.assertEqual(extractor.options.engine, OCREngine.TESSERACT)
        self.assertEqual(extractor.options.language, "fra")
        self.assertEqual(extractor.options.dpi, 150)
    
    def test_can_extract(self):
        """Test checking if the extractor can extract text from a file."""
        extractor = OCRExtractor()
        
        # Test with supported file types
        self.assertTrue(extractor.can_extract('/path/to/image.jpg'))
        self.assertTrue(extractor.can_extract('/path/to/image.jpeg'))
        self.assertTrue(extractor.can_extract('/path/to/image.png'))
        self.assertTrue(extractor.can_extract('/path/to/image.tiff'))
        self.assertTrue(extractor.can_extract('/path/to/image.gif'))
        
        # Test with unsupported file types
        self.assertFalse(extractor.can_extract('/path/to/document.pdf'))
        self.assertFalse(extractor.can_extract('/path/to/document.docx'))
        self.assertFalse(extractor.can_extract('/path/to/data.csv'))
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        extractor = OCRExtractor()
        formats = extractor.get_supported_formats()
        self.assertIn(TextExtractionFormat.PLAIN, formats)
        self.assertIn(TextExtractionFormat.HTML, formats)
    
    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extractor = OCRExtractor()
        extensions = extractor.get_supported_extensions()
        self.assertIn('.jpg', extensions)
        self.assertIn('.jpeg', extensions)
        self.assertIn('.png', extensions)
        self.assertIn('.tiff', extensions)
        self.assertIn('.gif', extensions)
    
    def test_get_supported_mime_types(self):
        """Test getting supported MIME types."""
        extractor = OCRExtractor()
        mime_types = extractor.get_supported_mime_types()
        self.assertIn('image/jpeg', mime_types)
        self.assertIn('image/png', mime_types)
        self.assertIn('image/tiff', mime_types)
        self.assertIn('image/gif', mime_types)
    
    def test_get_extraction_options(self):
        """Test getting extraction options."""
        extractor = OCRExtractor()
        options = extractor.get_extraction_options()
        self.assertIn('engine', options)
        self.assertIn('language', options)
        self.assertIn('dpi', options)
        self.assertIn('preprocess', options)
    
    @patch('science_data_kit.core.file_handling.ocr.OCRExtractor._get_ocr_engine')
    def test_extract_text_engine_failure(self, mock_get_engine):
        """Test extracting text when OCR engine initialization fails."""
        # Set up the mock to return None
        mock_get_engine.return_value = None
        
        # Create extractor and test
        extractor = OCRExtractor()
        result = extractor.extract_text('/path/to/image.jpg')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.text, '')
        self.assertIn('Failed to initialize OCR engine', result.error_message)
    
    @patch('science_data_kit.core.file_handling.ocr.OCRExtractor._get_ocr_engine')
    @patch('science_data_kit.core.file_handling.ocr.OCRExtractor._perform_ocr')
    def test_extract_text_success(self, mock_perform_ocr, mock_get_engine):
        """Test successful text extraction."""
        # Set up the mocks
        mock_get_engine.return_value = {'type': OCREngine.TESSERACT, 'engine': MagicMock()}
        mock_perform_ocr.return_value = {
            'text': 'Extracted text from image',
            'metadata': {'confidence': 95.5}
        }
        
        # Create extractor and test
        extractor = OCRExtractor()
        options = TextExtractionOptions(format=TextExtractionFormat.PLAIN)
        result = extractor.extract_text('/path/to/image.jpg', options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.text, 'Extracted text from image')
        self.assertEqual(result.format, TextExtractionFormat.PLAIN)
        self.assertIn('confidence', result.metadata)
        self.assertEqual(result.metadata['confidence'], 95.5)
    
    @patch('science_data_kit.core.file_handling.ocr.OCRExtractor._get_ocr_engine')
    @patch('science_data_kit.core.file_handling.ocr.OCRExtractor._perform_ocr')
    def test_extract_text_exception(self, mock_perform_ocr, mock_get_engine):
        """Test handling exceptions during text extraction."""
        # Set up the mocks
        mock_get_engine.return_value = {'type': OCREngine.TESSERACT, 'engine': MagicMock()}
        mock_perform_ocr.side_effect = Exception("OCR processing error")
        
        # Create extractor and test
        extractor = OCRExtractor()
        result = extractor.extract_text('/path/to/image.jpg')
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.text, '')
        self.assertEqual(result.error_message, 'OCR processing error')
    
    def test_convert_options(self):
        """Test converting TextExtractionOptions to OCROptions."""
        # Create extractor and options
        extractor = OCRExtractor()
        text_options = TextExtractionOptions(
            language='en',
            additional_options={
                'dpi': 200,
                'preprocess': False
            }
        )
        
        # Convert options
        ocr_options = extractor._convert_options(text_options)
        
        # Verify conversion
        self.assertEqual(ocr_options.language, 'eng')  # Should convert 'en' to 'eng'
        self.assertEqual(ocr_options.dpi, 200)
        self.assertFalse(ocr_options.preprocess)


if __name__ == '__main__':
    unittest.main()