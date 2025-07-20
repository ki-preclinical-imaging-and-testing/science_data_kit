"""
CSV/TSV File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for CSV (Comma-Separated Values) and
TSV (Tab-Separated Values) files, with a focus on extracting metadata and generating
previews of tabular data.
"""

import os
import io
import csv
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes
import json

# For data handling
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# For preview generation
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    StructuredDataExtractionCapability,
    TextExtractionCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class CSVFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                        ThumbnailGenerationCapability, StructuredDataExtractionCapability,
                        TextExtractionCapability):
    """
    File interpreter plugin for CSV and TSV files.
    
    This plugin can interpret CSV (Comma-Separated Values) and TSV (Tab-Separated Values) files,
    extract metadata, generate previews and thumbnails, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the CSV/TSV file interpreter."""
        super().__init__()
        self.supported_extensions = ['.csv', '.tsv', '.tab', '.data', '.txt']
        self.supported_mime_types = [
            'text/csv', 
            'text/tab-separated-values',
            'text/plain'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = True  # Basic extraction works without pandas
        self.can_generate_preview = PANDAS_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="CSV/TSV File Interpreter",
            description="Interprets CSV and TSV files, extracts metadata, and generates previews of tabular data",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation", "structured_data_extraction", "text_extraction"],
            config_schema={
                "max_preview_size": {
                    "type": "integer",
                    "description": "Maximum dimension (width or height) for previews",
                    "default": 1024
                },
                "max_thumbnail_size": {
                    "type": "integer",
                    "description": "Maximum dimension (width or height) for thumbnails",
                    "default": 128
                },
                "max_rows_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of rows to include in preview",
                    "default": 100
                },
                "max_columns_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of columns to include in preview",
                    "default": 20
                },
                "preview_dpi": {
                    "type": "integer",
                    "description": "DPI for preview generation",
                    "default": 100
                },
                "delimiter_detection": {
                    "type": "boolean",
                    "description": "Automatically detect delimiter based on file content",
                    "default": True
                }
            }
        )
    
    def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Check if this plugin can interpret the given file.
        
        Args:
            file_path: Path to the file to check.
            mime_type: Optional MIME type of the file, if known.
            
        Returns:
            True if the plugin can interpret the file, False otherwise.
        """
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file and check if it looks like CSV/TSV
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                # Read a few lines to check
                sample = ''.join([f.readline() for _ in range(5)])
                
                # Check for common delimiters
                for delimiter in [',', '\t', ';', '|']:
                    if delimiter in sample:
                        # Count delimiters in each line
                        lines = sample.strip().split('\n')
                        if len(lines) > 1:
                            # Check if the number of delimiters is consistent
                            delimiter_counts = [line.count(delimiter) for line in lines]
                            if len(set(delimiter_counts)) <= 2 and min(delimiter_counts) > 0:
                                return True
        except Exception:
            pass
        
        return False
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get a list of file extensions supported by this interpreter.
        
        Returns:
            List of supported file extensions.
        """
        return self.supported_extensions
    
    def get_supported_mime_types(self) -> List[str]:
        """
        Get a list of MIME types supported by this interpreter.
        
        Returns:
            List of supported MIME types.
        """
        return self.supported_mime_types
    
    def _detect_delimiter(self, file_path: str) -> str:
        """
        Detect the delimiter used in the CSV/TSV file.
        
        Args:
            file_path: Path to the file to analyze.
            
        Returns:
            Detected delimiter character.
        """
        # Common delimiters to check
        delimiters = [',', '\t', ';', '|']
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                # Read a few lines to check
                sample = ''.join([f.readline() for _ in range(5)])
                
                # Count occurrences of each delimiter
                counts = {delimiter: sample.count(delimiter) for delimiter in delimiters}
                
                # Return the delimiter with the highest count
                if max(counts.values()) > 0:
                    return max(counts.items(), key=lambda x: x[1])[0]
                
                # If no delimiter found, default to comma
                return ','
        except Exception:
            # Default to comma if detection fails
            return ','
    
    def _get_data_sample(self, file_path: str, max_rows: int = 100, delimiter: Optional[str] = None) -> Tuple[List[str], List[List[str]]]:
        """
        Get a sample of data from the CSV/TSV file.
        
        Args:
            file_path: Path to the file to sample.
            max_rows: Maximum number of rows to read.
            delimiter: Delimiter character to use. If None, auto-detect.
            
        Returns:
            Tuple of (header_row, data_rows).
        """
        # Detect delimiter if not provided
        if delimiter is None:
            delimiter = self._detect_delimiter(file_path)
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                # Create CSV reader
                reader = csv.reader(f, delimiter=delimiter)
                
                # Read header row
                header_row = next(reader, [])
                
                # Read data rows (up to max_rows)
                data_rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    data_rows.append(row)
                
                return header_row, data_rows
        except Exception:
            # Return empty data if reading fails
            return [], []
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the CSV/TSV file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        try:
            # Detect delimiter
            delimiter = self._detect_delimiter(file_path)
            metadata['delimiter'] = delimiter
            
            # Get data sample
            header_row, data_rows = self._get_data_sample(file_path, max_rows=10, delimiter=delimiter)
            
            # Add basic structure information
            metadata['has_header'] = len(header_row) > 0
            metadata['num_columns'] = len(header_row) if header_row else (len(data_rows[0]) if data_rows else 0)
            
            # Count total rows
            total_rows = 0
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    # Skip header if present
                    if metadata['has_header']:
                        next(reader, None)
                    # Count rows
                    total_rows = sum(1 for _ in reader)
            except Exception:
                # If counting fails, estimate from file size
                total_rows = "Unknown"
            
            metadata['num_rows'] = total_rows
            
            # Add column information if header is present
            if metadata['has_header'] and header_row:
                metadata['columns'] = header_row
            
            # Add data type information if pandas is available
            if PANDAS_AVAILABLE:
                try:
                    # Read a sample with pandas
                    df = pd.read_csv(file_path, delimiter=delimiter, nrows=100)
                    
                    # Get column data types
                    column_types = {}
                    for column in df.columns:
                        dtype = str(df[column].dtype)
                        column_types[column] = dtype
                    
                    metadata['column_types'] = column_types
                    
                    # Add basic statistics for numeric columns
                    numeric_stats = {}
                    for column in df.select_dtypes(include=['number']).columns:
                        stats = {
                            'min': float(df[column].min()),
                            'max': float(df[column].max()),
                            'mean': float(df[column].mean()),
                            'std': float(df[column].std())
                        }
                        numeric_stats[column] = stats
                    
                    if numeric_stats:
                        metadata['numeric_statistics'] = numeric_stats
                except Exception:
                    pass
            
            return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from the CSV/TSV file.
        
        Args:
            file_path: Path to the file to extract text from.
            
        Returns:
            Extracted text content.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the CSV/TSV file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview in pixels.
            height: Optional height for the preview in pixels.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (PANDAS_AVAILABLE and NUMPY_AVAILABLE and MATPLOTLIB_AVAILABLE):
            return {'error': "Required libraries not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            max_rows = kwargs.get('max_rows_to_preview', 100)
            max_cols = kwargs.get('max_columns_to_preview', 20)
            dpi = kwargs.get('preview_dpi', 100)
            
            # Calculate figure size based on width/height if provided
            figsize = (10, 8)  # default size in inches
            if width and height:
                figsize = (width / dpi, height / dpi)
            elif width:
                figsize = (width / dpi, figsize[1])
            elif height:
                figsize = (figsize[0], height / dpi)
            
            # Detect delimiter
            delimiter = self._detect_delimiter(file_path)
            
            # Read data with pandas
            df = pd.read_csv(file_path, delimiter=delimiter, nrows=max_rows)
            
            # Limit columns if needed
            if len(df.columns) > max_cols:
                df = df.iloc[:, :max_cols]
            
            # Create figure
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            
            # Hide axes
            ax.axis('off')
            
            # Create table
            table = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                cellLoc='center',
                loc='center',
                bbox=[0, 0, 1, 1]
            )
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
            # Add title with filename and dimensions
            plt.title(f"{os.path.basename(file_path)}\n{df.shape[0]} rows × {df.shape[1]} columns (sample)")
            
            # Adjust layout
            fig.tight_layout()
            
            # Save or return the figure
            if output_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save to the specified path
                fig.savefig(output_path, format='png', dpi=dpi)
                plt.close(fig)
                return output_path
            else:
                # Return the image data as bytes
                img_byte_arr = io.BytesIO()
                fig.savefig(img_byte_arr, format='png', dpi=dpi)
                plt.close(fig)
                return img_byte_arr.getvalue()
        except Exception as e:
            # If pandas preview fails, create a text-based preview
            try:
                # Get data sample
                delimiter = self._detect_delimiter(file_path)
                header_row, data_rows = self._get_data_sample(file_path, max_rows=20, delimiter=delimiter)
                
                # Create figure
                fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
                
                # Hide axes
                ax.axis('off')
                
                # Create text representation
                text = f"CSV/TSV File: {os.path.basename(file_path)}\n\n"
                
                # Add header row
                if header_row:
                    text += "Header: " + ", ".join(header_row) + "\n\n"
                
                # Add sample rows
                text += "Sample Data:\n"
                for i, row in enumerate(data_rows[:10]):
                    text += f"Row {i+1}: " + ", ".join(row) + "\n"
                
                # Add error message
                text += f"\nNote: Full preview failed with error: {str(e)}"
                
                # Display the text
                ax.text(0.5, 0.5, text,
                       horizontalalignment='center', verticalalignment='center',
                       fontsize=9, family='monospace',
                       transform=ax.transAxes)
                
                # Save or return the figure
                if output_path:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Save to the specified path
                    fig.savefig(output_path, format='png', dpi=dpi)
                    plt.close(fig)
                    return output_path
                else:
                    # Return the image data as bytes
                    img_byte_arr = io.BytesIO()
                    fig.savefig(img_byte_arr, format='png', dpi=dpi)
                    plt.close(fig)
                    return img_byte_arr.getvalue()
            except Exception as e2:
                # Return error information
                return {'error': f"Preview generation failed: {str(e2)}"}
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the CSV/TSV file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # For thumbnails, use a simpler preview with fewer rows and columns
        kwargs['max_rows_to_preview'] = 5
        kwargs['max_columns_to_preview'] = 5
        kwargs['preview_dpi'] = 72
        
        # Generate the preview with the specified width and height
        return self.generate_preview(
            file_path=file_path,
            output_path=output_path,
            width=width,
            height=height,
            **kwargs
        )
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.
        
        Returns:
            List of supported preview formats.
        """
        return ['image/png']
    
    def extract_structured_data(self, file_path: str, data_type: str, **kwargs) -> Any:
        """
        Extract structured data from the CSV/TSV file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'table', 'columns', 'statistics').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        # Detect delimiter
        delimiter = kwargs.get('delimiter', self._detect_delimiter(file_path))
        
        try:
            if data_type == 'table':
                # Extract table data
                max_rows = kwargs.get('max_rows', 100)
                
                if PANDAS_AVAILABLE:
                    # Use pandas for more robust parsing
                    df = pd.read_csv(file_path, delimiter=delimiter, nrows=max_rows)
                    
                    # Convert to records
                    records = df.to_dict(orient='records')
                    
                    # Get column types
                    column_types = {column: str(df[column].dtype) for column in df.columns}
                    
                    return {
                        'columns': list(df.columns),
                        'column_types': column_types,
                        'num_rows': len(df),
                        'num_columns': len(df.columns),
                        'data': records
                    }
                else:
                    # Fallback to csv module
                    header_row, data_rows = self._get_data_sample(file_path, max_rows=max_rows, delimiter=delimiter)
                    
                    # Convert to records
                    records = []
                    for row in data_rows:
                        if header_row:
                            # Use header as keys
                            record = {}
                            for i, value in enumerate(row):
                                if i < len(header_row):
                                    record[header_row[i]] = value
                            records.append(record)
                        else:
                            # Use indices as keys
                            record = {f"column_{i}": value for i, value in enumerate(row)}
                            records.append(record)
                    
                    return {
                        'columns': header_row if header_row else [f"column_{i}" for i in range(len(data_rows[0]) if data_rows else 0)],
                        'num_rows': len(data_rows),
                        'num_columns': len(header_row) if header_row else (len(data_rows[0]) if data_rows else 0),
                        'data': records
                    }
            
            elif data_type == 'columns':
                # Extract column information
                if PANDAS_AVAILABLE:
                    # Use pandas for more robust parsing
                    df = pd.read_csv(file_path, delimiter=delimiter, nrows=10)
                    
                    # Get column information
                    columns = []
                    for column in df.columns:
                        column_info = {
                            'name': column,
                            'dtype': str(df[column].dtype)
                        }
                        
                        # Add sample values
                        column_info['sample_values'] = df[column].head(5).tolist()
                        
                        columns.append(column_info)
                    
                    return columns
                else:
                    # Fallback to csv module
                    header_row, data_rows = self._get_data_sample(file_path, max_rows=10, delimiter=delimiter)
                    
                    # Get column information
                    columns = []
                    if header_row:
                        for i, name in enumerate(header_row):
                            column_info = {
                                'name': name,
                                'sample_values': [row[i] for row in data_rows if i < len(row)]
                            }
                            columns.append(column_info)
                    else:
                        # Use indices as column names
                        num_columns = len(data_rows[0]) if data_rows else 0
                        for i in range(num_columns):
                            column_info = {
                                'name': f"column_{i}",
                                'sample_values': [row[i] for row in data_rows if i < len(row)]
                            }
                            columns.append(column_info)
                    
                    return columns
            
            elif data_type == 'statistics':
                # Extract statistics for numeric columns
                if not PANDAS_AVAILABLE:
                    return {'error': "pandas library not available"}
                
                # Use pandas for statistics
                df = pd.read_csv(file_path, delimiter=delimiter)
                
                # Get statistics for numeric columns
                statistics = {}
                for column in df.select_dtypes(include=['number']).columns:
                    stats = {
                        'min': float(df[column].min()),
                        'max': float(df[column].max()),
                        'mean': float(df[column].mean()),
                        'median': float(df[column].median()),
                        'std': float(df[column].std()),
                        'count': int(df[column].count()),
                        'null_count': int(df[column].isna().sum())
                    }
                    statistics[column] = stats
                
                return statistics
            
            else:
                return {'error': f"Unsupported data type: {data_type}"}
        except Exception as e:
            return {'error': str(e)}
    
    def get_supported_data_types(self) -> List[str]:
        """
        Get a list of structured data types supported by this interpreter.
        
        Returns:
            List of supported data types.
        """
        return ['table', 'columns', 'statistics']