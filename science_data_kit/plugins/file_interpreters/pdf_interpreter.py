"""
PDF File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for PDF files,
with a focus on extracting metadata and generating previews.
"""

import os
import io
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes
import tempfile

# PDF libraries
try:
    import PyPDF2
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    TextExtractionCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class PDFFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                         ThumbnailGenerationCapability, TextExtractionCapability):
    """
    File interpreter plugin for PDF files.
    
    This plugin can interpret PDF files, extract metadata,
    generate previews and thumbnails, and extract text content.
    """
    
    def __init__(self):
        """Initialize the PDF file interpreter."""
        super().__init__()
        self.supported_extensions = ['.pdf']
        self.supported_mime_types = ['application/pdf']
        
        # Check if required libraries are available
        self.can_extract_metadata = PYPDF2_AVAILABLE
        self.can_generate_preview = PDF2IMAGE_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="PDF File Interpreter",
            description="Interprets PDF files, extracts metadata, and generates previews",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation", "text_extraction"],
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
                "preview_dpi": {
                    "type": "integer",
                    "description": "DPI for preview generation",
                    "default": 150
                },
                "thumbnail_dpi": {
                    "type": "integer",
                    "description": "DPI for thumbnail generation",
                    "default": 72
                },
                "max_pages_to_preview": {
                    "type": "integer",
                    "description": "Maximum number of pages to convert for preview",
                    "default": 1
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
        # Check if required libraries are available
        if not PYPDF2_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with PyPDF2 as a last resort
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
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
        Extract metadata from the PDF file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not PYPDF2_AVAILABLE:
            metadata['error'] = "PyPDF2 library not available"
            return metadata
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Add basic PDF info
                metadata.update({
                    'num_pages': len(reader.pages),
                    'is_encrypted': reader.is_encrypted,
                })
                
                # Extract document info if available
                if reader.metadata:
                    doc_info = {}
                    for key, value in reader.metadata.items():
                        # Convert key to string and remove leading '/'
                        key_str = str(key)
                        if key_str.startswith('/'):
                            key_str = key_str[1:]
                        
                        # Convert value to string if it's not None
                        if value is not None:
                            # Handle different types of values
                            if isinstance(value, (bytes, bytearray)):
                                try:
                                    value = value.decode('utf-8', errors='replace')
                                except UnicodeDecodeError:
                                    value = str(value)
                            else:
                                value = str(value)
                            
                            doc_info[key_str] = value
                    
                    # Add document info to metadata
                    metadata['document_info'] = doc_info
                
                # Extract page sizes
                page_sizes = []
                for i, page in enumerate(reader.pages):
                    if i < 10:  # Limit to first 10 pages to avoid performance issues
                        if page.mediabox:
                            width = page.mediabox.width
                            height = page.mediabox.height
                            page_sizes.append({
                                'page': i + 1,
                                'width': width,
                                'height': height,
                                'unit': 'points'  # PDF uses points (1/72 inch)
                            })
                
                if page_sizes:
                    metadata['page_sizes'] = page_sizes
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the PDF file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not PDF2IMAGE_AVAILABLE:
            return {'error': "pdf2image library not available"}
        
        try:
            # Get parameters from kwargs or use defaults
            dpi = kwargs.get('preview_dpi', 150)
            max_pages = kwargs.get('max_pages_to_preview', 1)
            
            # Convert PDF to images
            images = convert_from_path(
                file_path,
                dpi=dpi,
                first_page=1,
                last_page=max_pages
            )
            
            if not images:
                return {'error': "Failed to convert PDF to images"}
            
            # Use the first page as preview
            img = images[0]
            
            # Resize if width or height is specified
            if width or height:
                # Calculate new dimensions while maintaining aspect ratio
                if width and height:
                    img.thumbnail((width, height))
                elif width:
                    ratio = width / img.width
                    img.thumbnail((width, int(img.height * ratio)))
                elif height:
                    ratio = height / img.height
                    img.thumbnail((int(img.width * ratio), height))
            
            # Save the preview
            if output_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save to the specified path
                img.save(output_path, format='JPEG')
                return output_path
            else:
                # Return the image data as bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                return img_byte_arr.getvalue()
        except Exception as e:
            # Return error information
            return {'error': str(e)}
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the PDF file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
        # Use a lower DPI for thumbnails
        kwargs['preview_dpi'] = kwargs.get('thumbnail_dpi', 72)
        
        # Thumbnails are just smaller previews, so we can reuse the preview generation code
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
        return ['image/jpeg', 'image/png']
    
    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        """
        Extract text content from the PDF file.
        
        Args:
            file_path: Path to the file to extract text from.
            **kwargs: Additional parameters for text extraction.
            
        Returns:
            Extracted text content, or None if text extraction is not supported.
        """
        if not PYPDF2_AVAILABLE:
            return None
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Get parameters from kwargs
                max_pages = kwargs.get('max_pages', None)
                page_numbers = kwargs.get('page_numbers', None)
                
                text = ""
                
                # Extract text from specified pages or all pages
                if page_numbers:
                    for page_num in page_numbers:
                        if 0 <= page_num < len(reader.pages):
                            page = reader.pages[page_num]
                            text += page.extract_text() + "\n\n"
                else:
                    # Extract from all pages or up to max_pages
                    page_count = len(reader.pages)
                    if max_pages:
                        page_count = min(page_count, max_pages)
                    
                    for i in range(page_count):
                        page = reader.pages[i]
                        text += page.extract_text() + "\n\n"
                
                return text
        except Exception:
            return None
    
    def get_text_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.
        
        Returns:
            Dictionary of option names and their possible values.
        """
        return {
            'max_pages': {
                'type': 'integer',
                'description': 'Maximum number of pages to extract text from',
                'default': None  # None means all pages
            },
            'page_numbers': {
                'type': 'array',
                'description': 'List of specific page numbers to extract text from (0-based)',
                'default': None  # None means all pages
            }
        }