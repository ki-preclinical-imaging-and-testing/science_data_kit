"""
OCR (Optical Character Recognition) Module for Science Data Kit

This module provides OCR capabilities for extracting text from images.
It integrates with the text extraction framework and supports various
image formats and OCR engines.

The module is designed to be extensible, allowing different OCR engines
to be used based on availability and requirements.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractor, TextExtractionFormat, TextExtractionOptions, TextExtractionResult
)

# Set up logging
logger = logging.getLogger(__name__)


class OCREngine(Enum):
    """OCR engines supported by the system."""
    TESSERACT = "tesseract"  # Tesseract OCR (open source)
    GOOGLE_VISION = "google_vision"  # Google Cloud Vision API
    AZURE_VISION = "azure_vision"  # Azure Computer Vision API
    AWS_TEXTRACT = "aws_textract"  # AWS Textract
    AUTO = "auto"  # Automatically select the best available engine


@dataclass
class OCROptions:
    """Options for OCR processing."""
    engine: OCREngine = OCREngine.AUTO
    language: str = "eng"  # Language code (ISO 639-2)
    dpi: int = 300  # DPI for image processing
    preprocess: bool = True  # Whether to preprocess the image
    page_segmentation_mode: int = 3  # Tesseract page segmentation mode
    ocr_engine_mode: int = 3  # Tesseract OCR engine mode
    confidence_threshold: float = 0.0  # Minimum confidence threshold for results
    detect_orientation: bool = True  # Whether to detect and correct text orientation
    api_key: Optional[str] = None  # API key for cloud OCR services
    additional_options: Dict[str, Any] = field(default_factory=dict)  # Additional engine-specific options


class OCRExtractor(TextExtractor):
    """
    Text extractor that uses OCR to extract text from images.

    This extractor implements the TextExtractor interface and provides
    OCR capabilities for extracting text from various image formats.
    """

    def __init__(self, options: Optional[OCROptions] = None):
        """
        Initialize the OCR extractor.

        Args:
            options: OCR options to use for extraction.
        """
        self.options = options or OCROptions()
        self._engine = None  # Lazy-loaded OCR engine

    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract text from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract text from the file, False otherwise.
        """
        # Check if the file is an image
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']

    def extract_text(self, file_path: str, options: Optional[TextExtractionOptions] = None) -> TextExtractionResult:
        """
        Extract text from an image using OCR.

        Args:
            file_path: Path to the image file.
            options: Text extraction options.

        Returns:
            TextExtractionResult containing the extracted text and metadata.
        """
        if options is None:
            options = TextExtractionOptions()

        # Initialize OCR engine if needed
        if self._engine is None:
            self._engine = self._get_ocr_engine()
            if self._engine is None:
                return TextExtractionResult(
                    text="",
                    format=options.format,
                    success=False,
                    error_message="Failed to initialize OCR engine"
                )

        # Perform OCR
        try:
            # Convert TextExtractionOptions to OCROptions
            ocr_options = self._convert_options(options)
            
            # Extract text using the OCR engine
            ocr_result = self._perform_ocr(file_path, ocr_options)
            
            # Create result
            return TextExtractionResult(
                text=ocr_result.get('text', ''),
                format=options.format,
                metadata=ocr_result.get('metadata', {}),
                success=True
            )
        except Exception as e:
            logger.error(f"Error performing OCR on image {file_path}: {str(e)}")
            return TextExtractionResult(
                text="",
                format=options.format,
                success=False,
                error_message=str(e)
            )

    def get_supported_formats(self) -> List[TextExtractionFormat]:
        """
        Get a list of text extraction formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        return [TextExtractionFormat.PLAIN, TextExtractionFormat.HTML]

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions.
        """
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types.
        """
        return [
            'image/jpeg', 'image/png', 'image/bmp', 
            'image/tiff', 'image/gif'
        ]

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for OCR extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {
            'engine': [e.value for e in OCREngine],
            'language': ['eng', 'fra', 'deu', 'spa', 'ita', 'por', 'chi_sim', 'chi_tra', 'jpn', 'kor'],
            'dpi': 'integer (72-1200)',
            'preprocess': 'boolean',
            'page_segmentation_mode': 'integer (0-13)',
            'ocr_engine_mode': 'integer (0-3)',
            'confidence_threshold': 'float (0.0-1.0)',
            'detect_orientation': 'boolean'
        }

    def _get_ocr_engine(self) -> Any:
        """
        Get the appropriate OCR engine based on options and availability.

        Returns:
            OCR engine instance or None if no engine is available.
        """
        engine_type = self.options.engine

        # If AUTO, try to find the best available engine
        if engine_type == OCREngine.AUTO:
            # Try Tesseract first (most commonly available)
            try:
                import pytesseract
                return {'type': OCREngine.TESSERACT, 'engine': pytesseract}
            except ImportError:
                logger.warning("Tesseract OCR not available")

            # Try cloud services if API keys are provided
            if self.options.api_key:
                # Try Google Vision
                try:
                    from google.cloud import vision
                    return {'type': OCREngine.GOOGLE_VISION, 'engine': vision.ImageAnnotatorClient()}
                except ImportError:
                    logger.warning("Google Cloud Vision not available")

                # Try Azure Vision
                try:
                    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
                    return {'type': OCREngine.AZURE_VISION, 'engine': ComputerVisionClient()}
                except ImportError:
                    logger.warning("Azure Computer Vision not available")

                # Try AWS Textract
                try:
                    import boto3
                    return {'type': OCREngine.AWS_TEXTRACT, 'engine': boto3.client('textract')}
                except ImportError:
                    logger.warning("AWS Textract not available")

            logger.error("No OCR engine available")
            return None

        # Specific engine requested
        if engine_type == OCREngine.TESSERACT:
            try:
                import pytesseract
                return {'type': OCREngine.TESSERACT, 'engine': pytesseract}
            except ImportError:
                logger.error("Tesseract OCR requested but not available")
                return None
        elif engine_type == OCREngine.GOOGLE_VISION:
            try:
                from google.cloud import vision
                return {'type': OCREngine.GOOGLE_VISION, 'engine': vision.ImageAnnotatorClient()}
            except ImportError:
                logger.error("Google Cloud Vision requested but not available")
                return None
        elif engine_type == OCREngine.AZURE_VISION:
            try:
                from azure.cognitiveservices.vision.computervision import ComputerVisionClient
                return {'type': OCREngine.AZURE_VISION, 'engine': ComputerVisionClient()}
            except ImportError:
                logger.error("Azure Computer Vision requested but not available")
                return None
        elif engine_type == OCREngine.AWS_TEXTRACT:
            try:
                import boto3
                return {'type': OCREngine.AWS_TEXTRACT, 'engine': boto3.client('textract')}
            except ImportError:
                logger.error("AWS Textract requested but not available")
                return None

        logger.error(f"Unsupported OCR engine: {engine_type}")
        return None

    def _convert_options(self, options: TextExtractionOptions) -> OCROptions:
        """
        Convert TextExtractionOptions to OCROptions.

        Args:
            options: Text extraction options.

        Returns:
            OCR options.
        """
        ocr_options = self.options  # Use default OCR options

        # Update with relevant options from TextExtractionOptions
        if options.language:
            # Convert ISO 639-1 to ISO 639-2 if needed
            lang_map = {
                'en': 'eng',
                'fr': 'fra',
                'de': 'deu',
                'es': 'spa',
                'it': 'ita',
                'pt': 'por',
                'zh': 'chi_sim',
                'ja': 'jpn',
                'ko': 'kor'
            }
            ocr_options.language = lang_map.get(options.language, options.language)

        # Apply any additional options
        if options.additional_options:
            for key, value in options.additional_options.items():
                if hasattr(ocr_options, key):
                    setattr(ocr_options, key, value)
                else:
                    ocr_options.additional_options[key] = value

        return ocr_options

    def _perform_ocr(self, file_path: str, options: OCROptions) -> Dict[str, Any]:
        """
        Perform OCR on an image.

        Args:
            file_path: Path to the image file.
            options: OCR options.

        Returns:
            Dictionary containing OCR results.
        """
        if not self._engine:
            raise ValueError("OCR engine not initialized")

        engine_type = self._engine['type']
        engine = self._engine['engine']

        # Tesseract OCR
        if engine_type == OCREngine.TESSERACT:
            return self._perform_tesseract_ocr(file_path, options, engine)
        
        # Google Cloud Vision
        elif engine_type == OCREngine.GOOGLE_VISION:
            return self._perform_google_vision_ocr(file_path, options, engine)
        
        # Azure Computer Vision
        elif engine_type == OCREngine.AZURE_VISION:
            return self._perform_azure_vision_ocr(file_path, options, engine)
        
        # AWS Textract
        elif engine_type == OCREngine.AWS_TEXTRACT:
            return self._perform_aws_textract_ocr(file_path, options, engine)
        
        raise ValueError(f"Unsupported OCR engine: {engine_type}")

    def _perform_tesseract_ocr(self, file_path: str, options: OCROptions, engine: Any) -> Dict[str, Any]:
        """
        Perform OCR using Tesseract.

        Args:
            file_path: Path to the image file.
            options: OCR options.
            engine: Tesseract engine instance.

        Returns:
            Dictionary containing OCR results.
        """
        try:
            # Prepare Tesseract configuration
            config = f'--psm {options.page_segmentation_mode} --oem {options.ocr_engine_mode}'
            
            # Perform OCR
            text = engine.image_to_string(
                file_path,
                lang=options.language,
                config=config
            )
            
            # Get additional data if available
            metadata = {}
            try:
                # Get confidence data
                data = engine.image_to_data(
                    file_path,
                    lang=options.language,
                    config=config,
                    output_type=engine.Output.DICT
                )
                
                # Calculate average confidence
                if 'conf' in data and data['conf']:
                    confidences = [float(c) for c in data['conf'] if c != '-1']
                    if confidences:
                        metadata['confidence'] = sum(confidences) / len(confidences)
                
                # Get word-level data
                words = []
                for i in range(len(data['text'])):
                    if data['text'][i].strip():
                        words.append({
                            'text': data['text'][i],
                            'confidence': float(data['conf'][i]) if data['conf'][i] != '-1' else 0,
                            'bbox': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        })
                
                if words:
                    metadata['words'] = words
            
            except Exception as e:
                logger.warning(f"Failed to get detailed OCR data: {str(e)}")
            
            return {
                'text': text,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            raise

    def _perform_google_vision_ocr(self, file_path: str, options: OCROptions, engine: Any) -> Dict[str, Any]:
        """
        Perform OCR using Google Cloud Vision.

        Args:
            file_path: Path to the image file.
            options: OCR options.
            engine: Google Vision client instance.

        Returns:
            Dictionary containing OCR results.
        """
        try:
            from google.cloud import vision
            
            # Read the image file
            with open(file_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = vision.Image(content=content)
            
            # Perform OCR
            response = engine.text_detection(image=image)
            
            # Check for errors
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            # Extract text
            text = response.text_annotations[0].description if response.text_annotations else ""
            
            # Extract metadata
            metadata = {}
            if response.text_annotations:
                # Get word-level data
                words = []
                for annotation in response.text_annotations[1:]:  # Skip the first one (full text)
                    vertices = [(vertex.x, vertex.y) for vertex in annotation.bounding_poly.vertices]
                    words.append({
                        'text': annotation.description,
                        'bbox': vertices
                    })
                
                if words:
                    metadata['words'] = words
            
            return {
                'text': text,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {str(e)}")
            raise

    def _perform_azure_vision_ocr(self, file_path: str, options: OCROptions, engine: Any) -> Dict[str, Any]:
        """
        Perform OCR using Azure Computer Vision.

        Args:
            file_path: Path to the image file.
            options: OCR options.
            engine: Azure Computer Vision client instance.

        Returns:
            Dictionary containing OCR results.
        """
        # Implementation would go here
        # This is a placeholder for the Azure OCR implementation
        logger.warning("Azure Vision OCR not fully implemented")
        return {
            'text': '',
            'metadata': {}
        }

    def _perform_aws_textract_ocr(self, file_path: str, options: OCROptions, engine: Any) -> Dict[str, Any]:
        """
        Perform OCR using AWS Textract.

        Args:
            file_path: Path to the image file.
            options: OCR options.
            engine: AWS Textract client instance.

        Returns:
            Dictionary containing OCR results.
        """
        # Implementation would go here
        # This is a placeholder for the AWS Textract implementation
        logger.warning("AWS Textract OCR not fully implemented")
        return {
            'text': '',
            'metadata': {}
        }