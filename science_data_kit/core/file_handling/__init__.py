"""
File Handling Module for Science Data Kit

This module provides advanced file handling capabilities for the Science Data Kit,
including text extraction, OCR, table extraction, and other content processing features.

The module includes:
1. Text extraction framework for extracting text from various file types
2. OCR capabilities for extracting text from images
3. Table extraction for extracting structured data from documents
4. Content analysis utilities for processing extracted content
"""

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractor, TextExtractionOptions, TextExtractionResult,
    get_text_extractor_for_file, extract_text_from_file, TextExtractionFormat
)

from science_data_kit.core.file_handling.ocr import (
    OCRExtractor, OCROptions, OCREngine
)

from science_data_kit.core.file_handling.table_extraction import (
    TableExtractor, TableExtractionOptions, TableExtractionResult, Table,
    TableFormat, get_table_extractor_for_file, extract_tables_from_file,
    PDFTableExtractor
)

__all__ = [
    # Text extraction
    'TextExtractor', 'TextExtractionOptions', 'TextExtractionResult',
    'get_text_extractor_for_file', 'extract_text_from_file', 'TextExtractionFormat',

    # OCR
    'OCRExtractor', 'OCROptions', 'OCREngine',

    # Table extraction
    'TableExtractor', 'TableExtractionOptions', 'TableExtractionResult', 'Table',
    'TableFormat', 'get_table_extractor_for_file', 'extract_tables_from_file',
    'PDFTableExtractor'
]
