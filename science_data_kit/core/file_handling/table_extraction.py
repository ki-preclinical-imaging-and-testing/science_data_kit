"""
Table Extraction Module for Science Data Kit

This module provides capabilities for extracting tables from various document formats.
It integrates with the text extraction framework and supports different table extraction
methods and output formats.

The module is designed to be extensible, allowing different extraction methods to be used
based on document type and requirements.
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
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, StructuredDataExtractionCapability, get_file_interpreter_for_file
)

# Set up logging
logger = logging.getLogger(__name__)


class TableFormat(Enum):
    """Output formats for extracted tables."""
    CSV = "csv"  # Comma-separated values
    JSON = "json"  # JSON array of arrays or objects
    HTML = "html"  # HTML table
    MARKDOWN = "markdown"  # Markdown table
    DICT = "dict"  # Python dictionary (for internal use)
    PANDAS = "pandas"  # Pandas DataFrame (requires pandas)


@dataclass
class TableExtractionOptions:
    """Options for table extraction."""
    format: TableFormat = TableFormat.CSV
    include_headers: bool = True  # Whether to include headers in the output
    guess_headers: bool = True  # Whether to guess headers if not explicitly defined
    page_numbers: Optional[List[int]] = None  # Specific pages to extract tables from
    table_numbers: Optional[List[int]] = None  # Specific tables to extract
    min_rows: int = 2  # Minimum number of rows for a valid table
    min_columns: int = 2  # Minimum number of columns for a valid table
    extract_cell_coordinates: bool = False  # Whether to extract cell coordinates
    extract_cell_styles: bool = False  # Whether to extract cell styles
    extract_merged_cells: bool = True  # Whether to extract merged cells
    extract_cell_data_types: bool = False  # Whether to extract cell data types
    additional_options: Dict[str, Any] = field(default_factory=dict)  # Additional extractor-specific options


@dataclass
class Table:
    """Representation of an extracted table."""
    data: List[List[Any]]  # Table data as a list of rows
    headers: Optional[List[str]] = None  # Table headers
    page_number: Optional[int] = None  # Page number where the table was found
    table_number: Optional[int] = None  # Table number on the page
    coordinates: Optional[Dict[str, Any]] = None  # Table coordinates on the page
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata about the table


@dataclass
class TableExtractionResult:
    """Result of table extraction."""
    tables: List[Table]  # Extracted tables
    format: TableFormat  # Format of the extracted tables
    success: bool = True  # Whether extraction was successful
    error_message: Optional[str] = None  # Error message if extraction failed
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadata about the extraction


class TableExtractor(ABC):
    """
    Base class for table extractors.

    Table extractors are responsible for extracting tables from specific document types.
    They implement the extraction logic and handle format-specific details.
    """

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract tables from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract tables from the file, False otherwise.
        """
        pass

    @abstractmethod
    def extract_tables(self, file_path: str, options: Optional[TableExtractionOptions] = None) -> TableExtractionResult:
        """
        Extract tables from the file.

        Args:
            file_path: Path to the file to extract tables from.
            options: Options for table extraction.

        Returns:
            TableExtractionResult containing the extracted tables.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[TableFormat]:
        """
        Get a list of table formats supported by this extractor.

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
        Get available options for table extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {}


class PluginBasedTableExtractor(TableExtractor):
    """
    Table extractor that uses file interpreter plugins for table extraction.

    This extractor acts as a bridge between the table extraction framework and
    the existing file interpreter plugins that implement the StructuredDataExtractionCapability.
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
        Check if this extractor can extract tables from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract tables from the file, False otherwise.
        """
        if self.plugin:
            return (
                self.plugin.can_interpret(file_path) and
                isinstance(self.plugin, StructuredDataExtractionCapability) and
                'table' in self.plugin.get_supported_data_types()
            )
        
        # Try to find a suitable plugin
        plugin = get_file_interpreter_for_file(file_path)
        return (
            plugin is not None and
            isinstance(plugin, StructuredDataExtractionCapability) and
            'table' in plugin.get_supported_data_types()
        )

    def extract_tables(self, file_path: str, options: Optional[TableExtractionOptions] = None) -> TableExtractionResult:
        """
        Extract tables from the file using a file interpreter plugin.

        Args:
            file_path: Path to the file to extract tables from.
            options: Options for table extraction.

        Returns:
            TableExtractionResult containing the extracted tables.
        """
        if options is None:
            options = TableExtractionOptions()

        # Get a plugin if not already set
        plugin = self.plugin
        if not plugin:
            plugin = get_file_interpreter_for_file(file_path)
            if not plugin or not isinstance(plugin, StructuredDataExtractionCapability) or 'table' not in plugin.get_supported_data_types():
                return TableExtractionResult(
                    tables=[],
                    format=options.format,
                    success=False,
                    error_message=f"No suitable table extractor found for file: {file_path}"
                )

        # Extract tables using the plugin
        try:
            # Convert our options to plugin-specific options
            plugin_options = {}
            if options.additional_options:
                plugin_options.update(options.additional_options)
            
            # Add standard options
            if options.page_numbers:
                plugin_options['page_numbers'] = options.page_numbers
            if options.table_numbers:
                plugin_options['table_numbers'] = options.table_numbers
            
            # Extract structured data (tables)
            structured_data = plugin.extract_structured_data(file_path, 'table', **plugin_options)
            if not structured_data:
                return TableExtractionResult(
                    tables=[],
                    format=options.format,
                    success=False,
                    error_message=f"No tables found in file: {file_path}"
                )

            # Convert structured data to tables
            tables = self._convert_structured_data_to_tables(structured_data, options)
            
            # Create result
            return TableExtractionResult(
                tables=tables,
                format=options.format,
                success=True
            )
        except Exception as e:
            logger.error(f"Error extracting tables from file {file_path}: {str(e)}")
            return TableExtractionResult(
                tables=[],
                format=options.format,
                success=False,
                error_message=str(e)
            )

    def get_supported_formats(self) -> List[TableFormat]:
        """
        Get a list of table formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        return [TableFormat.CSV, TableFormat.JSON, TableFormat.DICT]

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
        Get available options for table extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        if self.plugin and isinstance(self.plugin, StructuredDataExtractionCapability):
            # Get options specific to table extraction
            plugin_options = {}
            try:
                plugin_options = self.plugin.get_extraction_options('table')
            except:
                pass
            
            # Add standard options
            standard_options = {
                'format': [f.value for f in TableFormat],
                'include_headers': 'boolean',
                'guess_headers': 'boolean',
                'page_numbers': 'list of integers',
                'table_numbers': 'list of integers',
                'min_rows': 'integer',
                'min_columns': 'integer',
                'extract_cell_coordinates': 'boolean',
                'extract_cell_styles': 'boolean',
                'extract_merged_cells': 'boolean',
                'extract_cell_data_types': 'boolean'
            }
            
            return {**standard_options, **plugin_options}
        
        return {}

    def _convert_structured_data_to_tables(self, structured_data: Any, options: TableExtractionOptions) -> List[Table]:
        """
        Convert structured data from a plugin to Table objects.

        Args:
            structured_data: Structured data from the plugin.
            options: Table extraction options.

        Returns:
            List of Table objects.
        """
        tables = []
        
        # Handle different structured data formats
        if isinstance(structured_data, list):
            # List of tables
            for i, table_data in enumerate(structured_data):
                table = self._convert_single_table(table_data, i, options)
                if table:
                    tables.append(table)
        elif isinstance(structured_data, dict):
            # Single table or dictionary of tables
            if 'data' in structured_data:
                # Single table
                table = self._convert_single_table(structured_data, 0, options)
                if table:
                    tables.append(table)
            else:
                # Dictionary of tables
                for key, table_data in structured_data.items():
                    table_number = int(key) if key.isdigit() else i
                    table = self._convert_single_table(table_data, table_number, options)
                    if table:
                        tables.append(table)
        
        return tables

    def _convert_single_table(self, table_data: Any, table_number: int, options: TableExtractionOptions) -> Optional[Table]:
        """
        Convert a single table from structured data to a Table object.

        Args:
            table_data: Data for a single table.
            table_number: Table number.
            options: Table extraction options.

        Returns:
            Table object or None if conversion failed.
        """
        try:
            # Extract table data
            data = []
            headers = None
            page_number = None
            coordinates = None
            metadata = {}
            
            if isinstance(table_data, dict):
                # Dictionary format
                if 'data' in table_data:
                    data = table_data['data']
                if 'headers' in table_data:
                    headers = table_data['headers']
                if 'page_number' in table_data:
                    page_number = table_data['page_number']
                if 'coordinates' in table_data:
                    coordinates = table_data['coordinates']
                if 'metadata' in table_data:
                    metadata = table_data['metadata']
            elif isinstance(table_data, list):
                # List format (just the data)
                data = table_data
                
                # Try to guess headers if requested
                if options.guess_headers and options.include_headers and len(data) > 0:
                    # Use first row as headers
                    headers = data[0]
                    data = data[1:]
            
            # Validate table
            if len(data) < options.min_rows:
                logger.warning(f"Table {table_number} has fewer than {options.min_rows} rows, skipping")
                return None
            
            if any(len(row) < options.min_columns for row in data):
                logger.warning(f"Table {table_number} has rows with fewer than {options.min_columns} columns, skipping")
                return None
            
            # Create table object
            return Table(
                data=data,
                headers=headers if options.include_headers else None,
                page_number=page_number,
                table_number=table_number,
                coordinates=coordinates,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error converting table {table_number}: {str(e)}")
            return None


class PDFTableExtractor(TableExtractor):
    """
    Specialized table extractor for PDF files.

    This extractor uses libraries like tabula-py or camelot to extract tables from PDF files.
    """

    def __init__(self):
        """Initialize the PDF table extractor."""
        self._tabula_available = False
        self._camelot_available = False
        
        # Check for tabula-py
        try:
            import tabula
            self._tabula_available = True
        except ImportError:
            logger.warning("tabula-py not available, some PDF table extraction features will be limited")
        
        # Check for camelot
        try:
            import camelot
            self._camelot_available = True
        except ImportError:
            logger.warning("camelot not available, some PDF table extraction features will be limited")

    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract tables from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract tables from the file, False otherwise.
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext == '.pdf' and (self._tabula_available or self._camelot_available)

    def extract_tables(self, file_path: str, options: Optional[TableExtractionOptions] = None) -> TableExtractionResult:
        """
        Extract tables from a PDF file.

        Args:
            file_path: Path to the PDF file.
            options: Options for table extraction.

        Returns:
            TableExtractionResult containing the extracted tables.
        """
        if options is None:
            options = TableExtractionOptions()
        
        # Choose extraction method based on availability
        if self._camelot_available:
            return self._extract_with_camelot(file_path, options)
        elif self._tabula_available:
            return self._extract_with_tabula(file_path, options)
        else:
            return TableExtractionResult(
                tables=[],
                format=options.format,
                success=False,
                error_message="No PDF table extraction library available"
            )

    def get_supported_formats(self) -> List[TableFormat]:
        """
        Get a list of table formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        formats = [TableFormat.CSV, TableFormat.JSON, TableFormat.DICT]
        
        # Add pandas format if available
        try:
            import pandas
            formats.append(TableFormat.PANDAS)
        except ImportError:
            pass
        
        return formats

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions.
        """
        return ['.pdf']

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types.
        """
        return ['application/pdf']

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for table extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        options = {
            'format': [f.value for f in TableFormat],
            'include_headers': 'boolean',
            'guess_headers': 'boolean',
            'page_numbers': 'list of integers',
            'table_numbers': 'list of integers',
            'min_rows': 'integer',
            'min_columns': 'integer'
        }
        
        # Add tabula-specific options
        if self._tabula_available:
            options.update({
                'multiple_tables': 'boolean',
                'area': 'list of floats [top, left, bottom, right]',
                'lattice': 'boolean',
                'stream': 'boolean',
                'guess': 'boolean'
            })
        
        # Add camelot-specific options
        if self._camelot_available:
            options.update({
                'flavor': ['lattice', 'stream'],
                'edge_tol': 'float',
                'row_tol': 'float',
                'column_tol': 'float'
            })
        
        return options

    def _extract_with_tabula(self, file_path: str, options: TableExtractionOptions) -> TableExtractionResult:
        """
        Extract tables from a PDF file using tabula-py.

        Args:
            file_path: Path to the PDF file.
            options: Options for table extraction.

        Returns:
            TableExtractionResult containing the extracted tables.
        """
        try:
            import tabula
            import pandas as pd
            
            # Prepare tabula options
            tabula_options = {
                'pages': ','.join(map(str, options.page_numbers)) if options.page_numbers else 'all',
                'multiple_tables': True
            }
            
            # Add additional options
            if options.additional_options:
                for key, value in options.additional_options.items():
                    tabula_options[key] = value
            
            # Extract tables
            dfs = tabula.read_pdf(file_path, **tabula_options)
            
            # Convert DataFrames to Table objects
            tables = []
            for i, df in enumerate(dfs):
                if len(df) >= options.min_rows and len(df.columns) >= options.min_columns:
                    # Convert DataFrame to list of lists
                    data = df.values.tolist()
                    headers = df.columns.tolist() if options.include_headers else None
                    
                    # Create Table object
                    table = Table(
                        data=data,
                        headers=headers,
                        table_number=i,
                        metadata={'source': 'tabula-py'}
                    )
                    tables.append(table)
            
            return TableExtractionResult(
                tables=tables,
                format=options.format,
                success=True
            )
        
        except Exception as e:
            logger.error(f"Error extracting tables with tabula-py: {str(e)}")
            return TableExtractionResult(
                tables=[],
                format=options.format,
                success=False,
                error_message=str(e)
            )

    def _extract_with_camelot(self, file_path: str, options: TableExtractionOptions) -> TableExtractionResult:
        """
        Extract tables from a PDF file using camelot.

        Args:
            file_path: Path to the PDF file.
            options: Options for table extraction.

        Returns:
            TableExtractionResult containing the extracted tables.
        """
        try:
            import camelot
            
            # Prepare camelot options
            camelot_options = {
                'pages': ','.join(map(str, options.page_numbers)) if options.page_numbers else 'all',
                'flavor': options.additional_options.get('flavor', 'lattice')
            }
            
            # Add additional options
            if options.additional_options:
                for key, value in options.additional_options.items():
                    if key != 'flavor':  # Already handled
                        camelot_options[key] = value
            
            # Extract tables
            tables_obj = camelot.read_pdf(file_path, **camelot_options)
            
            # Convert camelot tables to Table objects
            tables = []
            for i, table_obj in enumerate(tables_obj):
                df = table_obj.df
                if len(df) >= options.min_rows and len(df.columns) >= options.min_columns:
                    # Convert DataFrame to list of lists
                    data = df.values.tolist()
                    headers = df.columns.tolist() if options.include_headers else None
                    
                    # Get table metadata
                    metadata = {
                        'source': 'camelot',
                        'accuracy': table_obj.accuracy,
                        'whitespace': table_obj.whitespace,
                        'order': table_obj.order
                    }
                    
                    # Create Table object
                    table = Table(
                        data=data,
                        headers=headers,
                        table_number=i,
                        page_number=table_obj.page,
                        metadata=metadata
                    )
                    tables.append(table)
            
            return TableExtractionResult(
                tables=tables,
                format=options.format,
                success=True
            )
        
        except Exception as e:
            logger.error(f"Error extracting tables with camelot: {str(e)}")
            return TableExtractionResult(
                tables=[],
                format=options.format,
                success=False,
                error_message=str(e)
            )


def get_table_extractor_for_file(file_path: str) -> Optional[TableExtractor]:
    """
    Get a table extractor that can extract tables from the given file.

    This function tries to find a suitable extractor based on the file type.
    It first checks for specialized extractors, then falls back to plugin-based extraction.

    Args:
        file_path: Path to the file to extract tables from.

    Returns:
        A TableExtractor instance, or None if no suitable extractor is found.
    """
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check for specialized extractors based on file extension
    if ext == '.pdf':
        extractor = PDFTableExtractor()
        if extractor.can_extract(file_path):
            return extractor
    
    # Try to find a file interpreter plugin with structured data extraction capability
    plugin = get_file_interpreter_for_file(file_path)
    if plugin and isinstance(plugin, StructuredDataExtractionCapability) and 'table' in plugin.get_supported_data_types():
        return PluginBasedTableExtractor(plugin)
    
    # No suitable extractor found
    logger.warning(f"No suitable table extractor found for file: {file_path}")
    return None


def extract_tables_from_file(file_path: str, options: Optional[TableExtractionOptions] = None) -> TableExtractionResult:
    """
    Extract tables from a file using the appropriate extractor.

    This is a convenience function that finds the appropriate extractor and
    extracts tables from the file.

    Args:
        file_path: Path to the file to extract tables from.
        options: Options for table extraction.

    Returns:
        TableExtractionResult containing the extracted tables.
    """
    extractor = get_table_extractor_for_file(file_path)
    if not extractor:
        return TableExtractionResult(
            tables=[],
            format=options.format if options else TableFormat.CSV,
            success=False,
            error_message=f"No suitable table extractor found for file: {file_path}"
        )
    
    return extractor.extract_tables(file_path, options)