"""
Text Extraction Framework for Science Data Kit

This module provides a comprehensive framework for extracting text from various file types.
It includes a base TextExtractor class, specialized extractors for different file types,
and utilities for working with extracted text.

The framework is designed to be extensible, allowing new extractors to be added for
additional file types, and to integrate with the existing plugin architecture.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, TextExtractionCapability, get_file_interpreter_for_file
)

# Set up logging
logger = logging.getLogger(__name__)


class TextExtractionFormat(Enum):
    """Formats for extracted text."""
    PLAIN = "plain"  # Plain text without formatting
    HTML = "html"    # HTML with formatting preserved
    MARKDOWN = "markdown"  # Markdown with basic formatting
    JSON = "json"    # JSON representation of text with structure


@dataclass
class TextExtractionOptions:
    """Options for text extraction."""
    format: TextExtractionFormat = TextExtractionFormat.PLAIN
    include_metadata: bool = False  # Whether to include metadata in the result
    page_numbers: Optional[List[int]] = None  # Specific pages to extract (for multi-page documents)
    max_length: Optional[int] = None  # Maximum length of extracted text
    encoding: str = "utf-8"  # Text encoding
    preserve_formatting: bool = False  # Whether to preserve formatting (when possible)
    extract_tables: bool = False  # Whether to extract tables as structured data
    extract_images: bool = False  # Whether to extract text from images (OCR)
    language: str = "en"  # Language for OCR and other language-specific processing
    additional_options: Dict[str, Any] = field(default_factory=dict)  # Additional extractor-specific options


@dataclass
class TextExtractionResult:
    """Result of text extraction."""
    text: str  # The extracted text
    format: TextExtractionFormat  # Format of the extracted text
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadata about the extraction
    tables: List[Dict[str, Any]] = field(default_factory=list)  # Extracted tables (if any)
    images: List[Dict[str, Any]] = field(default_factory=list)  # Extracted images (if any)
    pages: List[Dict[str, Any]] = field(default_factory=list)  # Page information (for multi-page documents)
    success: bool = True  # Whether extraction was successful
    error_message: Optional[str] = None  # Error message if extraction failed


class TextExtractor(ABC):
    """
    Base class for text extractors.

    Text extractors are responsible for extracting text from specific file types.
    They implement the extraction logic and handle format-specific details.
    """

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract text from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract text from the file, False otherwise.
        """
        pass

    @abstractmethod
    def extract_text(self, file_path: str, options: Optional[TextExtractionOptions] = None) -> TextExtractionResult:
        """
        Extract text from the file.

        Args:
            file_path: Path to the file to extract text from.
            options: Options for text extraction.

        Returns:
            TextExtractionResult containing the extracted text and metadata.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[TextExtractionFormat]:
        """
        Get a list of text extraction formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        pass

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions (e.g., ['.pdf', '.docx']).
        """
        return []

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types (e.g., ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']).
        """
        return []

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {}


class PluginBasedTextExtractor(TextExtractor):
    """
    Text extractor that uses file interpreter plugins for text extraction.

    This extractor acts as a bridge between the text extraction framework and
    the existing file interpreter plugins that implement the TextExtractionCapability.
    """

    def __init__(self, plugin: Optional[FileInterpreterPlugin] = None):
        """
        Initialize the extractor with an optional plugin.

        Args:
            plugin: Optional file interpreter plugin to use for extraction.
        """
        self.plugin = plugin

    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract text from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract text from the file, False otherwise.
        """
        if self.plugin:
            return (
                self.plugin.can_interpret(file_path) and
                isinstance(self.plugin, TextExtractionCapability)
            )
        
        # Try to find a suitable plugin
        plugin = get_file_interpreter_for_file(file_path)
        return plugin is not None and isinstance(plugin, TextExtractionCapability)

    def extract_text(self, file_path: str, options: Optional[TextExtractionOptions] = None) -> TextExtractionResult:
        """
        Extract text from the file using a file interpreter plugin.

        Args:
            file_path: Path to the file to extract text from.
            options: Options for text extraction.

        Returns:
            TextExtractionResult containing the extracted text and metadata.
        """
        if options is None:
            options = TextExtractionOptions()

        # Get a plugin if not already set
        plugin = self.plugin
        if not plugin:
            plugin = get_file_interpreter_for_file(file_path)
            if not plugin or not isinstance(plugin, TextExtractionCapability):
                return TextExtractionResult(
                    text="",
                    format=options.format,
                    success=False,
                    error_message=f"No suitable text extractor found for file: {file_path}"
                )

        # Extract text using the plugin
        try:
            # Convert our options to plugin-specific options
            plugin_options = {}
            if options.additional_options:
                plugin_options.update(options.additional_options)
            
            # Extract text
            text = plugin.extract_text(file_path, **plugin_options)
            if text is None:
                return TextExtractionResult(
                    text="",
                    format=options.format,
                    success=False,
                    error_message=f"Text extraction failed for file: {file_path}"
                )

            # Extract metadata if requested
            metadata = {}
            if options.include_metadata:
                try:
                    metadata = plugin.extract_metadata(file_path)
                except Exception as e:
                    logger.warning(f"Failed to extract metadata for file {file_path}: {str(e)}")

            # Create result
            return TextExtractionResult(
                text=text,
                format=options.format,
                metadata=metadata,
                success=True
            )
        except Exception as e:
            logger.error(f"Error extracting text from file {file_path}: {str(e)}")
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
        # Currently, plugin-based extractors only support plain text
        return [TextExtractionFormat.PLAIN]

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions.
        """
        if self.plugin:
            return self.plugin.get_supported_extensions()
        return []

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types.
        """
        if self.plugin:
            return self.plugin.get_supported_mime_types()
        return []

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        if self.plugin and isinstance(self.plugin, TextExtractionCapability):
            return self.plugin.get_text_extraction_options()
        return {}


def get_text_extractor_for_file(file_path: str) -> Optional[TextExtractor]:
    """
    Get a text extractor that can extract text from the given file.

    This function tries to find a suitable extractor based on the file type.
    It first checks for specialized extractors, then falls back to plugin-based extraction.

    Args:
        file_path: Path to the file to extract text from.

    Returns:
        A TextExtractor instance, or None if no suitable extractor is found.
    """
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Try to find a file interpreter plugin with text extraction capability
    plugin = get_file_interpreter_for_file(file_path)
    if plugin and isinstance(plugin, TextExtractionCapability):
        return PluginBasedTextExtractor(plugin)

    # No suitable extractor found
    logger.warning(f"No suitable text extractor found for file: {file_path}")
    return None


def extract_text_from_file(file_path: str, options: Optional[TextExtractionOptions] = None) -> TextExtractionResult:
    """
    Extract text from a file using the appropriate extractor.

    This is a convenience function that finds the appropriate extractor and
    extracts text from the file.

    Args:
        file_path: Path to the file to extract text from.
        options: Options for text extraction.

    Returns:
        TextExtractionResult containing the extracted text and metadata.
    """
    extractor = get_text_extractor_for_file(file_path)
    if not extractor:
        return TextExtractionResult(
            text="",
            format=options.format if options else TextExtractionFormat.PLAIN,
            success=False,
            error_message=f"No suitable text extractor found for file: {file_path}"
        )

    return extractor.extract_text(file_path, options)