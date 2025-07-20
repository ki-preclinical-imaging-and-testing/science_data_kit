"""
DOCX File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for DOCX files,
with a focus on extracting metadata and generating previews.
"""

import os
import io
import tempfile
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes

# DOCX libraries
try:
    import docx
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# For preview generation (convert DOCX to PDF, then PDF to image)
try:
    import subprocess
    LIBREOFFICE_AVAILABLE = True
except ImportError:
    LIBREOFFICE_AVAILABLE = False

try:
    from pdf2image import convert_from_path
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
class DOCXFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, 
                          ThumbnailGenerationCapability, TextExtractionCapability):
    """
    File interpreter plugin for DOCX files.
    
    This plugin can interpret DOCX files, extract metadata,
    generate previews and thumbnails, and extract text content.
    """
    
    def __init__(self):
        """Initialize the DOCX file interpreter."""
        super().__init__()
        self.supported_extensions = ['.docx']
        self.supported_mime_types = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        # Check if required libraries are available
        self.can_extract_metadata = DOCX_AVAILABLE
        self.can_generate_preview = LIBREOFFICE_AVAILABLE and PDF2IMAGE_AVAILABLE
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="DOCX File Interpreter",
            description="Interprets DOCX files, extracts metadata, and generates previews",
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
                },
                "libreoffice_path": {
                    "type": "string",
                    "description": "Path to LibreOffice executable",
                    "default": "libreoffice"
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
        if not DOCX_AVAILABLE:
            return False
            
        # Check file extension
        extension = os.path.splitext(file_path)[1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check MIME type if provided
        if mime_type and mime_type in self.supported_mime_types:
            return True
        
        # Try to open the file with python-docx as a last resort
        try:
            doc = Document(file_path)
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
        Extract metadata from the DOCX file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        if not DOCX_AVAILABLE:
            metadata['error'] = "python-docx library not available"
            return metadata
        
        try:
            doc = Document(file_path)
            
            # Extract core properties
            core_properties = doc.core_properties
            
            # Add document properties to metadata
            doc_info = {}
            
            # Extract standard properties
            if hasattr(core_properties, 'author') and core_properties.author:
                doc_info['author'] = core_properties.author
            
            if hasattr(core_properties, 'title') and core_properties.title:
                doc_info['title'] = core_properties.title
            
            if hasattr(core_properties, 'subject') and core_properties.subject:
                doc_info['subject'] = core_properties.subject
            
            if hasattr(core_properties, 'keywords') and core_properties.keywords:
                doc_info['keywords'] = core_properties.keywords
            
            if hasattr(core_properties, 'comments') and core_properties.comments:
                doc_info['comments'] = core_properties.comments
            
            if hasattr(core_properties, 'category') and core_properties.category:
                doc_info['category'] = core_properties.category
            
            if hasattr(core_properties, 'created') and core_properties.created:
                doc_info['created'] = str(core_properties.created)
            
            if hasattr(core_properties, 'modified') and core_properties.modified:
                doc_info['modified'] = str(core_properties.modified)
            
            if hasattr(core_properties, 'last_modified_by') and core_properties.last_modified_by:
                doc_info['last_modified_by'] = core_properties.last_modified_by
            
            if hasattr(core_properties, 'revision') and core_properties.revision:
                doc_info['revision'] = core_properties.revision
            
            # Add document info to metadata
            if doc_info:
                metadata['document_info'] = doc_info
            
            # Extract document statistics
            stats = {}
            
            # Count paragraphs
            stats['paragraphs'] = len(doc.paragraphs)
            
            # Count tables
            stats['tables'] = len(doc.tables)
            
            # Count sections
            stats['sections'] = len(doc.sections)
            
            # Estimate word count (approximate)
            word_count = 0
            for para in doc.paragraphs:
                word_count += len(para.text.split())
            stats['estimated_word_count'] = word_count
            
            # Add statistics to metadata
            metadata['statistics'] = stats
            
            # Extract page size information from sections
            page_sizes = []
            for i, section in enumerate(doc.sections):
                page_size = {
                    'section': i + 1,
                    'width': section.page_width.pt,
                    'height': section.page_height.pt,
                    'unit': 'points'  # Points (1/72 inch)
                }
                page_sizes.append(page_size)
            
            if page_sizes:
                metadata['page_sizes'] = page_sizes
            
            return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def _convert_docx_to_pdf(self, docx_path: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Convert DOCX to PDF using LibreOffice.
        
        Args:
            docx_path: Path to the DOCX file.
            output_dir: Optional directory to save the PDF file.
            
        Returns:
            Path to the generated PDF file, or None if conversion failed.
        """
        if not LIBREOFFICE_AVAILABLE:
            return None
        
        try:
            # Create temporary directory if output_dir is not provided
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Get LibreOffice path from config or use default
            libreoffice_path = "libreoffice"
            
            # Convert DOCX to PDF
            cmd = [
                libreoffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                docx_path
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Get the output PDF path
            pdf_filename = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            if os.path.exists(pdf_path):
                return pdf_path
            else:
                return None
        except Exception:
            return None
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the DOCX file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        if not (LIBREOFFICE_AVAILABLE and PDF2IMAGE_AVAILABLE):
            return {'error': "LibreOffice or pdf2image library not available"}
        
        try:
            # Create temporary directory for intermediate files
            temp_dir = tempfile.mkdtemp()
            
            # Convert DOCX to PDF
            pdf_path = self._convert_docx_to_pdf(file_path, temp_dir)
            
            if not pdf_path:
                return {'error': "Failed to convert DOCX to PDF"}
            
            # Get parameters from kwargs or use defaults
            dpi = kwargs.get('preview_dpi', 150)
            max_pages = kwargs.get('max_pages_to_preview', 1)
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
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
        finally:
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the DOCX file.
        
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
        Extract text content from the DOCX file.
        
        Args:
            file_path: Path to the file to extract text from.
            **kwargs: Additional parameters for text extraction.
            
        Returns:
            Extracted text content, or None if text extraction is not supported.
        """
        if not DOCX_AVAILABLE:
            return None
        
        try:
            doc = Document(file_path)
            
            # Extract text from paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():  # Skip empty paragraphs
                    paragraphs.append(para.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():  # Skip empty cells
                            row_text.append(cell.text)
                    if row_text:
                        paragraphs.append(' | '.join(row_text))
            
            # Join all paragraphs with double newlines
            return '\n\n'.join(paragraphs)
        except Exception:
            return None
    
    def get_text_extraction_options(self) -> Dict[str, Any]:
        """
        Get available options for text extraction.
        
        Returns:
            Dictionary of option names and their possible values.
        """
        return {
            'include_tables': {
                'type': 'boolean',
                'description': 'Whether to include text from tables',
                'default': True
            },
            'include_headers_footers': {
                'type': 'boolean',
                'description': 'Whether to include text from headers and footers',
                'default': False
            }
        }