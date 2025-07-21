"""
File Handling Module for Science Data Kit

This module provides advanced file handling capabilities for the Science Data Kit,
including text extraction, OCR, table extraction, chart data extraction, AI service integration, and other content processing features.

The module includes:
1. Text extraction framework for extracting text from various file types
2. OCR capabilities for extracting text from images
3. Table extraction for extracting structured data from documents
4. Chart data extraction for extracting data from charts and graphs
5. AI service integration for leveraging external AI services
6. Content analysis utilities for processing extracted content
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

from science_data_kit.core.file_handling.chart_extraction import (
    ChartExtractor, ChartExtractionOptions, ChartExtractionResult, ChartData,
    ChartType, ChartDataFormat, get_chart_extractor_for_file, extract_charts_from_file,
    ImageBasedChartExtractor
)

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServicePlugin, AIServiceCapability, AIServiceResult,
    ImageAnalysisResult, TextAnalysisResult, SpeechRecognitionResult,
    TranslationResult, DocumentAnalysisResult,
    ImageAnalysisCapability, TextAnalysisCapability, SpeechRecognitionCapability,
    TranslationCapability, DocumentAnalysisCapability,
    get_ai_service_for_capability, get_image_analysis_service, get_text_analysis_service,
    get_speech_recognition_service, get_translation_service, get_document_analysis_service,
    analyze_image, analyze_text, analyze_text_file, recognize_speech, translate_text, analyze_document
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
    'PDFTableExtractor',

    # Chart data extraction
    'ChartExtractor', 'ChartExtractionOptions', 'ChartExtractionResult', 'ChartData',
    'ChartType', 'ChartDataFormat', 'get_chart_extractor_for_file', 'extract_charts_from_file',
    'ImageBasedChartExtractor',

    # AI service integration
    'AIServicePlugin', 'AIServiceCapability', 'AIServiceResult',
    'ImageAnalysisResult', 'TextAnalysisResult', 'SpeechRecognitionResult',
    'TranslationResult', 'DocumentAnalysisResult',
    'ImageAnalysisCapability', 'TextAnalysisCapability', 'SpeechRecognitionCapability',
    'TranslationCapability', 'DocumentAnalysisCapability',
    'get_ai_service_for_capability', 'get_image_analysis_service', 'get_text_analysis_service',
    'get_speech_recognition_service', 'get_translation_service', 'get_document_analysis_service',
    'analyze_image', 'analyze_text', 'analyze_text_file', 'recognize_speech', 'translate_text', 'analyze_document'
]
