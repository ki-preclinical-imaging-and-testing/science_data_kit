"""
Chart Data Extraction Module for Science Data Kit

This module provides capabilities for extracting data from charts and graphs in various file formats.
It integrates with the content extraction framework and supports different chart extraction
methods and output formats.

The module is designed to be extensible, allowing different extraction methods to be used
based on chart type and requirements.
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


class ChartType(Enum):
    """Types of charts that can be extracted."""
    BAR = "bar"  # Bar chart
    LINE = "line"  # Line chart
    PIE = "pie"  # Pie chart
    SCATTER = "scatter"  # Scatter plot
    AREA = "area"  # Area chart
    HISTOGRAM = "histogram"  # Histogram
    BOX = "box"  # Box plot
    HEATMAP = "heatmap"  # Heatmap
    UNKNOWN = "unknown"  # Unknown chart type


class ChartDataFormat(Enum):
    """Output formats for extracted chart data."""
    CSV = "csv"  # Comma-separated values
    JSON = "json"  # JSON representation
    DICT = "dict"  # Python dictionary (for internal use)
    PANDAS = "pandas"  # Pandas DataFrame (requires pandas)
    EXCEL = "excel"  # Excel format (requires openpyxl)


@dataclass
class ChartExtractionOptions:
    """Options for chart data extraction."""
    format: ChartDataFormat = ChartDataFormat.CSV
    chart_types: Optional[List[ChartType]] = None  # Specific chart types to extract
    page_numbers: Optional[List[int]] = None  # Specific pages to extract charts from
    chart_numbers: Optional[List[int]] = None  # Specific charts to extract
    include_chart_metadata: bool = True  # Whether to include chart metadata in the output
    extract_chart_title: bool = True  # Whether to extract chart title
    extract_axis_labels: bool = True  # Whether to extract axis labels
    extract_legend: bool = True  # Whether to extract legend
    extract_data_labels: bool = True  # Whether to extract data labels
    extract_trend_lines: bool = False  # Whether to extract trend lines
    extract_error_bars: bool = False  # Whether to extract error bars
    detect_chart_type: bool = True  # Whether to detect chart type
    additional_options: Dict[str, Any] = field(default_factory=dict)  # Additional extractor-specific options


@dataclass
class ChartData:
    """Representation of extracted chart data."""
    data: List[List[Any]]  # Chart data as a list of rows
    headers: Optional[List[str]] = None  # Column headers
    chart_type: ChartType = ChartType.UNKNOWN  # Type of chart
    title: Optional[str] = None  # Chart title
    x_label: Optional[str] = None  # X-axis label
    y_label: Optional[str] = None  # Y-axis label
    legend: Optional[List[str]] = None  # Legend entries
    page_number: Optional[int] = None  # Page number where the chart was found
    chart_number: Optional[int] = None  # Chart number on the page
    coordinates: Optional[Dict[str, Any]] = None  # Chart coordinates on the page
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata about the chart


@dataclass
class ChartExtractionResult:
    """Result of chart data extraction."""
    charts: List[ChartData]  # Extracted chart data
    format: ChartDataFormat  # Format of the extracted data
    success: bool = True  # Whether extraction was successful
    error_message: Optional[str] = None  # Error message if extraction failed
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadata about the extraction


class ChartExtractor(ABC):
    """
    Base class for chart data extractors.

    Chart extractors are responsible for extracting data from charts in specific file types.
    They implement the extraction logic and handle format-specific details.
    """

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract chart data from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract chart data from the file, False otherwise.
        """
        pass

    @abstractmethod
    def extract_charts(self, file_path: str, options: Optional[ChartExtractionOptions] = None) -> ChartExtractionResult:
        """
        Extract chart data from the file.

        Args:
            file_path: Path to the file to extract chart data from.
            options: Options for chart extraction.

        Returns:
            ChartExtractionResult containing the extracted chart data.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[ChartDataFormat]:
        """
        Get a list of chart data formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        pass

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions (e.g., ['.pdf', '.pptx']).
        """
        return []

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types.
        """
        return []

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for chart extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {}


class PluginBasedChartExtractor(ChartExtractor):
    """
    Chart extractor that uses file interpreter plugins for chart data extraction.

    This extractor acts as a bridge between the chart extraction framework and
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
        Check if this extractor can extract chart data from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract chart data from the file, False otherwise.
        """
        if self.plugin:
            return (
                self.plugin.can_interpret(file_path) and
                isinstance(self.plugin, StructuredDataExtractionCapability) and
                'chart' in self.plugin.get_supported_data_types()
            )
        
        # Try to find a suitable plugin
        plugin = get_file_interpreter_for_file(file_path)
        return (
            plugin is not None and
            isinstance(plugin, StructuredDataExtractionCapability) and
            'chart' in plugin.get_supported_data_types()
        )

    def extract_charts(self, file_path: str, options: Optional[ChartExtractionOptions] = None) -> ChartExtractionResult:
        """
        Extract chart data from the file using a file interpreter plugin.

        Args:
            file_path: Path to the file to extract chart data from.
            options: Options for chart extraction.

        Returns:
            ChartExtractionResult containing the extracted chart data.
        """
        if options is None:
            options = ChartExtractionOptions()

        # Get a plugin if not already set
        plugin = self.plugin
        if not plugin:
            plugin = get_file_interpreter_for_file(file_path)
            if not plugin or not isinstance(plugin, StructuredDataExtractionCapability) or 'chart' not in plugin.get_supported_data_types():
                return ChartExtractionResult(
                    charts=[],
                    format=options.format,
                    success=False,
                    error_message=f"No suitable chart extractor found for file: {file_path}"
                )

        # Extract charts using the plugin
        try:
            # Convert our options to plugin-specific options
            plugin_options = {}
            if options.additional_options:
                plugin_options.update(options.additional_options)
            
            # Add standard options
            if options.page_numbers:
                plugin_options['page_numbers'] = options.page_numbers
            if options.chart_numbers:
                plugin_options['chart_numbers'] = options.chart_numbers
            if options.chart_types:
                plugin_options['chart_types'] = [ct.value for ct in options.chart_types]
            
            # Extract structured data (charts)
            structured_data = plugin.extract_structured_data(file_path, 'chart', **plugin_options)
            if not structured_data:
                return ChartExtractionResult(
                    charts=[],
                    format=options.format,
                    success=False,
                    error_message=f"No charts found in file: {file_path}"
                )

            # Convert structured data to charts
            charts = self._convert_structured_data_to_charts(structured_data, options)
            
            # Create result
            return ChartExtractionResult(
                charts=charts,
                format=options.format,
                success=True
            )
        except Exception as e:
            logger.error(f"Error extracting charts from file {file_path}: {str(e)}")
            return ChartExtractionResult(
                charts=[],
                format=options.format,
                success=False,
                error_message=str(e)
            )

    def get_supported_formats(self) -> List[ChartDataFormat]:
        """
        Get a list of chart data formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        return [ChartDataFormat.CSV, ChartDataFormat.JSON, ChartDataFormat.DICT]

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
        Get available options for chart extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        if self.plugin and isinstance(self.plugin, StructuredDataExtractionCapability):
            # Get options specific to chart extraction
            plugin_options = {}
            try:
                plugin_options = self.plugin.get_extraction_options('chart')
            except:
                pass
            
            # Add standard options
            standard_options = {
                'format': [f.value for f in ChartDataFormat],
                'chart_types': [ct.value for ct in ChartType],
                'page_numbers': 'list of integers',
                'chart_numbers': 'list of integers',
                'include_chart_metadata': 'boolean',
                'extract_chart_title': 'boolean',
                'extract_axis_labels': 'boolean',
                'extract_legend': 'boolean',
                'extract_data_labels': 'boolean',
                'extract_trend_lines': 'boolean',
                'extract_error_bars': 'boolean',
                'detect_chart_type': 'boolean'
            }
            
            return {**standard_options, **plugin_options}
        
        return {}

    def _convert_structured_data_to_charts(self, structured_data: Any, options: ChartExtractionOptions) -> List[ChartData]:
        """
        Convert structured data from a plugin to ChartData objects.

        Args:
            structured_data: Structured data from the plugin.
            options: Chart extraction options.

        Returns:
            List of ChartData objects.
        """
        charts = []
        
        # Handle different structured data formats
        if isinstance(structured_data, list):
            # List of charts
            for i, chart_data in enumerate(structured_data):
                chart = self._convert_single_chart(chart_data, i, options)
                if chart:
                    charts.append(chart)
        elif isinstance(structured_data, dict):
            # Single chart or dictionary of charts
            if 'data' in structured_data:
                # Single chart
                chart = self._convert_single_chart(structured_data, 0, options)
                if chart:
                    charts.append(chart)
            else:
                # Dictionary of charts
                for key, chart_data in structured_data.items():
                    chart_number = int(key) if key.isdigit() else i
                    chart = self._convert_single_chart(chart_data, chart_number, options)
                    if chart:
                        charts.append(chart)
        
        return charts

    def _convert_single_chart(self, chart_data: Any, chart_number: int, options: ChartExtractionOptions) -> Optional[ChartData]:
        """
        Convert a single chart from structured data to a ChartData object.

        Args:
            chart_data: Data for a single chart.
            chart_number: Chart number.
            options: Chart extraction options.

        Returns:
            ChartData object or None if conversion failed.
        """
        try:
            # Extract chart data
            data = []
            headers = None
            chart_type = ChartType.UNKNOWN
            title = None
            x_label = None
            y_label = None
            legend = None
            page_number = None
            coordinates = None
            metadata = {}
            
            if isinstance(chart_data, dict):
                # Dictionary format
                if 'data' in chart_data:
                    data = chart_data['data']
                if 'headers' in chart_data:
                    headers = chart_data['headers']
                if 'chart_type' in chart_data:
                    chart_type_str = chart_data['chart_type'].lower()
                    try:
                        chart_type = ChartType(chart_type_str)
                    except ValueError:
                        chart_type = ChartType.UNKNOWN
                if 'title' in chart_data and options.extract_chart_title:
                    title = chart_data['title']
                if 'x_label' in chart_data and options.extract_axis_labels:
                    x_label = chart_data['x_label']
                if 'y_label' in chart_data and options.extract_axis_labels:
                    y_label = chart_data['y_label']
                if 'legend' in chart_data and options.extract_legend:
                    legend = chart_data['legend']
                if 'page_number' in chart_data:
                    page_number = chart_data['page_number']
                if 'coordinates' in chart_data:
                    coordinates = chart_data['coordinates']
                if 'metadata' in chart_data and options.include_chart_metadata:
                    metadata = chart_data['metadata']
            elif isinstance(chart_data, list):
                # List format (just the data)
                data = chart_data
                
                # Try to guess headers if available
                if len(data) > 0:
                    headers = data[0]
                    data = data[1:]
            
            # Create chart data object
            return ChartData(
                data=data,
                headers=headers,
                chart_type=chart_type,
                title=title,
                x_label=x_label,
                y_label=y_label,
                legend=legend,
                page_number=page_number,
                chart_number=chart_number,
                coordinates=coordinates,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error converting chart {chart_number}: {str(e)}")
            return None


class ImageBasedChartExtractor(ChartExtractor):
    """
    Chart extractor that uses image processing techniques to extract data from chart images.

    This extractor uses computer vision libraries to detect and extract data from charts
    in image files or document pages rendered as images.
    """

    def __init__(self):
        """Initialize the image-based chart extractor."""
        self._cv2_available = False
        self._plt_available = False
        self._np_available = False
        
        # Check for OpenCV
        try:
            import cv2
            self._cv2_available = True
        except ImportError:
            logger.warning("OpenCV (cv2) not available, image-based chart extraction will be limited")
        
        # Check for matplotlib
        try:
            import matplotlib.pyplot as plt
            self._plt_available = True
        except ImportError:
            logger.warning("matplotlib not available, some chart extraction features will be limited")
        
        # Check for numpy
        try:
            import numpy as np
            self._np_available = True
        except ImportError:
            logger.warning("numpy not available, image-based chart extraction will be limited")

    def can_extract(self, file_path: str) -> bool:
        """
        Check if this extractor can extract chart data from the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the extractor can extract chart data from the file, False otherwise.
        """
        ext = os.path.splitext(file_path)[1].lower()
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        return ext in image_extensions and self._cv2_available and self._np_available

    def extract_charts(self, file_path: str, options: Optional[ChartExtractionOptions] = None) -> ChartExtractionResult:
        """
        Extract chart data from an image file.

        Args:
            file_path: Path to the image file.
            options: Options for chart extraction.

        Returns:
            ChartExtractionResult containing the extracted chart data.
        """
        if options is None:
            options = ChartExtractionOptions()
        
        if not self._cv2_available or not self._np_available:
            return ChartExtractionResult(
                charts=[],
                format=options.format,
                success=False,
                error_message="OpenCV or numpy not available for image-based chart extraction"
            )
        
        try:
            import cv2
            import numpy as np
            
            # Load the image
            image = cv2.imread(file_path)
            if image is None:
                return ChartExtractionResult(
                    charts=[],
                    format=options.format,
                    success=False,
                    error_message=f"Failed to load image: {file_path}"
                )
            
            # Detect charts in the image
            charts = self._detect_charts(image, options)
            
            if not charts:
                return ChartExtractionResult(
                    charts=[],
                    format=options.format,
                    success=False,
                    error_message=f"No charts detected in image: {file_path}"
                )
            
            return ChartExtractionResult(
                charts=charts,
                format=options.format,
                success=True,
                metadata={'source': 'image-based-extraction'}
            )
        
        except Exception as e:
            logger.error(f"Error extracting charts from image {file_path}: {str(e)}")
            return ChartExtractionResult(
                charts=[],
                format=options.format,
                success=False,
                error_message=str(e)
            )

    def get_supported_formats(self) -> List[ChartDataFormat]:
        """
        Get a list of chart data formats supported by this extractor.

        Returns:
            List of supported formats.
        """
        formats = [ChartDataFormat.CSV, ChartDataFormat.JSON, ChartDataFormat.DICT]
        
        # Add pandas format if available
        try:
            import pandas
            formats.append(ChartDataFormat.PANDAS)
        except ImportError:
            pass
        
        return formats

    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this extractor.

        Returns:
            List of supported file extensions.
        """
        return ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']

    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this extractor.

        Returns:
            List of supported MIME types.
        """
        return [
            'image/png',
            'image/jpeg',
            'image/bmp',
            'image/tiff'
        ]

    def get_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for chart extraction.

        Returns:
            Dictionary of option names and their possible values.
        """
        return {
            'format': [f.value for f in ChartDataFormat],
            'chart_types': [ct.value for ct in ChartType],
            'detect_chart_type': 'boolean',
            'extract_chart_title': 'boolean',
            'extract_axis_labels': 'boolean',
            'extract_legend': 'boolean',
            'extract_data_labels': 'boolean',
            'min_confidence': 'float (0.0-1.0)',
            'use_ocr': 'boolean'
        }

    def _detect_charts(self, image, options: ChartExtractionOptions) -> List[ChartData]:
        """
        Detect and extract data from charts in an image.

        Args:
            image: The image to analyze.
            options: Chart extraction options.

        Returns:
            List of ChartData objects.
        """
        import cv2
        import numpy as np
        
        # This is a simplified implementation that would need to be expanded
        # with actual chart detection and data extraction algorithms
        
        # For now, we'll assume the entire image is a single chart and
        # extract some basic information
        
        # Determine chart type if requested
        chart_type = ChartType.UNKNOWN
        if options.detect_chart_type:
            # This would need a sophisticated algorithm to detect chart type
            # For now, we'll just use a placeholder
            chart_type = ChartType.BAR  # Placeholder
        
        # Extract chart title if requested
        title = None
        if options.extract_chart_title:
            # This would need OCR to extract the title
            # For now, we'll just use a placeholder
            title = "Chart Title"  # Placeholder
        
        # Extract axis labels if requested
        x_label = None
        y_label = None
        if options.extract_axis_labels:
            # This would need OCR to extract axis labels
            # For now, we'll just use placeholders
            x_label = "X Axis"  # Placeholder
            y_label = "Y Axis"  # Placeholder
        
        # Extract legend if requested
        legend = None
        if options.extract_legend:
            # This would need sophisticated image processing to extract the legend
            # For now, we'll just use a placeholder
            legend = ["Series 1", "Series 2"]  # Placeholder
        
        # Extract data
        # This would need sophisticated image processing to extract actual data points
        # For now, we'll just use placeholder data
        data = [
            [1, 10],
            [2, 20],
            [3, 15],
            [4, 25],
            [5, 30]
        ]
        
        headers = ["X", "Y"]
        
        # Create chart data object
        chart = ChartData(
            data=data,
            headers=headers,
            chart_type=chart_type,
            title=title,
            x_label=x_label,
            y_label=y_label,
            legend=legend,
            chart_number=0,
            metadata={'source': 'image-based-extraction'}
        )
        
        return [chart]


def get_chart_extractor_for_file(file_path: str) -> Optional[ChartExtractor]:
    """
    Get a chart extractor that can extract chart data from the given file.

    This function tries to find a suitable extractor based on the file type.
    It first checks for specialized extractors, then falls back to plugin-based extraction.

    Args:
        file_path: Path to the file to extract chart data from.

    Returns:
        A ChartExtractor instance, or None if no suitable extractor is found.
    """
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check for image-based extractor for image files
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
        extractor = ImageBasedChartExtractor()
        if extractor.can_extract(file_path):
            return extractor
    
    # Try to find a file interpreter plugin with structured data extraction capability
    plugin = get_file_interpreter_for_file(file_path)
    if plugin and isinstance(plugin, StructuredDataExtractionCapability) and 'chart' in plugin.get_supported_data_types():
        return PluginBasedChartExtractor(plugin)
    
    # No suitable extractor found
    logger.warning(f"No suitable chart extractor found for file: {file_path}")
    return None


def extract_charts_from_file(file_path: str, options: Optional[ChartExtractionOptions] = None) -> ChartExtractionResult:
    """
    Extract chart data from a file using the appropriate extractor.

    This is a convenience function that finds the appropriate extractor and
    extracts chart data from the file.

    Args:
        file_path: Path to the file to extract chart data from.
        options: Options for chart extraction.

    Returns:
        ChartExtractionResult containing the extracted chart data.
    """
    extractor = get_chart_extractor_for_file(file_path)
    if not extractor:
        return ChartExtractionResult(
            charts=[],
            format=options.format if options else ChartDataFormat.CSV,
            success=False,
            error_message=f"No suitable chart extractor found for file: {file_path}"
        )
    
    return extractor.extract_charts(file_path, options)