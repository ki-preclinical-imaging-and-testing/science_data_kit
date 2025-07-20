"""
XLSX file interpreter plugin for Science Data Kit.

This plugin can interpret XLSX spreadsheet files, extract metadata,
and generate previews.
"""

import os
import io
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes
import openpyxl
from openpyxl.utils import get_column_letter

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    TextExtractionCapability,
    StructuredDataExtractionCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class XLSXFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                         ThumbnailGenerationCapability, TextExtractionCapability,
                         StructuredDataExtractionCapability):
    """
    File interpreter plugin for XLSX spreadsheet files.
    
    This plugin can interpret XLSX spreadsheet files, extract metadata,
    generate previews, extract text content, and extract structured data.
    """
    
    def __init__(self):
        """Initialize the XLSX file interpreter."""
        super().__init__()
        self.supported_extensions = ['.xlsx', '.xlsm', '.xltx', '.xltm']
        self.supported_mime_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel.sheet.macroEnabled.12',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
            'application/vnd.ms-excel.template.macroEnabled.12'
        ]
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="XLSX File Interpreter",
            description="Interprets XLSX spreadsheet files, extracts metadata, and generates previews",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation", "text_extraction", "structured_data_extraction"],
            config_schema={
                "max_preview_rows": {
                    "type": "integer",
                    "description": "Maximum number of rows to include in preview",
                    "default": 100
                },
                "max_preview_cols": {
                    "type": "integer",
                    "description": "Maximum number of columns to include in preview",
                    "default": 20
                },
                "max_text_extraction_rows": {
                    "type": "integer",
                    "description": "Maximum number of rows to extract text from",
                    "default": 1000
                },
                "max_text_extraction_cols": {
                    "type": "integer",
                    "description": "Maximum number of columns to extract text from",
                    "default": 100
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
        
        # Try to open the file with openpyxl as a last resort
        try:
            openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            return True
        except Exception:
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
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from the XLSX file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        try:
            # Load the workbook
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            
            # Extract document properties
            metadata.update({
                'title': wb.properties.title,
                'subject': wb.properties.subject,
                'creator': wb.properties.creator,
                'keywords': wb.properties.keywords,
                'description': wb.properties.description,
                'category': wb.properties.category,
                'created': wb.properties.created,
                'modified': wb.properties.modified,
                'last_modified_by': wb.properties.lastModifiedBy
            })
            
            # Extract workbook structure
            sheet_info = []
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                sheet_data = {
                    'name': sheet_name,
                    'is_visible': not sheet.sheet_state == 'hidden',
                    'dimensions': sheet.calculate_dimension() if hasattr(sheet, 'calculate_dimension') else 'Unknown'
                }
                
                # Try to get row and column counts
                try:
                    if hasattr(sheet, 'max_row') and hasattr(sheet, 'max_column'):
                        sheet_data['rows'] = sheet.max_row
                        sheet_data['columns'] = sheet.max_column
                except Exception:
                    # Some sheets might not have these properties in read_only mode
                    sheet_data['rows'] = 'Unknown'
                    sheet_data['columns'] = 'Unknown'
                
                sheet_info.append(sheet_data)
            
            metadata['sheets'] = sheet_info
            metadata['sheet_count'] = len(sheet_info)
            metadata['active_sheet'] = wb.active.title if wb.active else None
            
            # Extract named ranges if available
            if hasattr(wb, 'defined_names') and wb.defined_names:
                named_ranges = []
                for name in wb.defined_names:
                    named_ranges.append({
                        'name': name.name,
                        'value': name.value,
                        'comment': name.comment
                    })
                metadata['named_ranges'] = named_ranges
            
            # Close the workbook
            wb.close()
            
        except Exception as e:
            metadata['error'] = f"Error extracting XLSX metadata: {str(e)}"
        
        return metadata
    
    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        """
        Extract text content from the XLSX file.
        
        Args:
            file_path: Path to the file to extract text from.
            **kwargs: Additional parameters for text extraction.
            
        Returns:
            Extracted text content, or None if extraction failed.
        """
        try:
            # Get configuration parameters
            max_rows = kwargs.get('max_rows', 1000)
            max_cols = kwargs.get('max_cols', 100)
            
            # Load the workbook
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            
            # Extract text from each sheet
            text_content = []
            
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                sheet_text = [f"Sheet: {sheet_name}"]
                
                # Get rows and columns to extract
                row_count = min(sheet.max_row, max_rows) if hasattr(sheet, 'max_row') else max_rows
                col_count = min(sheet.max_column, max_cols) if hasattr(sheet, 'max_column') else max_cols
                
                # Extract cell values
                for row in range(1, row_count + 1):
                    row_values = []
                    for col in range(1, col_count + 1):
                        cell = sheet.cell(row=row, column=col)
                        if cell.value is not None:
                            row_values.append(str(cell.value))
                    if row_values:
                        sheet_text.append("\t".join(row_values))
                
                text_content.append("\n".join(sheet_text))
            
            # Close the workbook
            wb.close()
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            return f"Error extracting text from XLSX: {str(e)}"
    
    def extract_structured_data(self, file_path: str, data_type: str, **kwargs) -> Any:
        """
        Extract structured data from the XLSX file.
        
        Args:
            file_path: Path to the file to extract data from.
            data_type: Type of data to extract (e.g., 'table', 'chart').
            **kwargs: Additional parameters for data extraction.
            
        Returns:
            Extracted structured data.
        """
        if data_type == 'table':
            try:
                # Get configuration parameters
                sheet_name = kwargs.get('sheet_name', None)
                max_rows = kwargs.get('max_rows', 1000)
                max_cols = kwargs.get('max_cols', 100)
                include_headers = kwargs.get('include_headers', True)
                
                # Load the workbook
                wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                
                # If sheet_name is provided, extract data from that sheet only
                if sheet_name and sheet_name in wb.sheetnames:
                    sheets_to_extract = [sheet_name]
                else:
                    sheets_to_extract = wb.sheetnames
                
                # Extract data from each sheet
                result = {}
                
                for sheet_name in sheets_to_extract:
                    sheet = wb[sheet_name]
                    
                    # Get rows and columns to extract
                    row_count = min(sheet.max_row, max_rows) if hasattr(sheet, 'max_row') else max_rows
                    col_count = min(sheet.max_column, max_cols) if hasattr(sheet, 'max_column') else max_cols
                    
                    # Extract cell values
                    sheet_data = []
                    for row in range(1, row_count + 1):
                        row_data = []
                        for col in range(1, col_count + 1):
                            cell = sheet.cell(row=row, column=col)
                            row_data.append(cell.value)
                        sheet_data.append(row_data)
                    
                    # Convert to dict with headers if requested
                    if include_headers and sheet_data:
                        headers = sheet_data[0]
                        data_rows = []
                        for row in sheet_data[1:]:
                            row_dict = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    row_dict[str(header)] = row[i]
                            data_rows.append(row_dict)
                        result[sheet_name] = data_rows
                    else:
                        result[sheet_name] = sheet_data
                
                # Close the workbook
                wb.close()
                
                return result
                
            except Exception as e:
                return {'error': f"Error extracting table data from XLSX: {str(e)}"}
        
        elif data_type == 'chart':
            # Chart extraction would require more complex processing
            return {'error': "Chart extraction not implemented"}
        
        else:
            return {'error': f"Unsupported data type: {data_type}"}
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the XLSX file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Preview data or path to the generated preview.
        """
        # For now, return a placeholder message
        # In a real implementation, this would generate an HTML table or image of the spreadsheet
        if output_path:
            with open(output_path, 'w') as f:
                f.write("XLSX spreadsheet preview placeholder")
            return output_path
        else:
            return "XLSX spreadsheet preview placeholder"
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the XLSX file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Thumbnail data or path to the generated thumbnail.
        """
        # For now, return a placeholder message
        # In a real implementation, this would generate a small image of the spreadsheet
        if output_path:
            with open(output_path, 'w') as f:
                f.write("XLSX spreadsheet thumbnail placeholder")
            return output_path
        else:
            return "XLSX spreadsheet thumbnail placeholder"
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.
        
        Returns:
            List of supported preview formats.
        """
        return ['text/html', 'image/png', 'image/jpeg']
    
    def get_supported_data_types(self) -> List[str]:
        """
        Get a list of structured data types supported by this interpreter.
        
        Returns:
            List of supported data types.
        """
        return ['table', 'chart']
    
    def get_text_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.
        
        Returns:
            Dictionary of option names and their possible values.
        """
        return {
            'max_rows': {
                'type': 'integer',
                'description': 'Maximum number of rows to extract',
                'default': 1000
            },
            'max_cols': {
                'type': 'integer',
                'description': 'Maximum number of columns to extract',
                'default': 100
            }
        }