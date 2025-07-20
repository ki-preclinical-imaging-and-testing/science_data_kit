"""
Image File Interpreter Plugin for Science Data Kit

This module provides a file interpreter plugin for image files,
with a focus on extracting EXIF metadata and generating previews.
"""

import os
import io
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes
from PIL import Image, ExifTags
import piexif

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class ImageFileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, ThumbnailGenerationCapability):
    """
    File interpreter plugin for image files.
    
    This plugin can interpret common image formats (JPEG, TIFF, PNG, etc.),
    extract EXIF metadata, and generate previews and thumbnails.
    """
    
    def __init__(self):
        """Initialize the image file interpreter."""
        super().__init__()
        self.supported_extensions = ['.jpg', '.jpeg', '.tiff', '.tif', '.png', '.gif', '.bmp']
        self.supported_mime_types = [
            'image/jpeg', 'image/tiff', 'image/png', 'image/gif', 'image/bmp'
        ]
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="Image File Interpreter",
            description="Interprets image files, extracts EXIF metadata, and generates previews",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation"],
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
        
        # Try to open the file with PIL as a last resort
        try:
            with Image.open(file_path) as img:
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
        Extract metadata from the image file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        try:
            with Image.open(file_path) as img:
                # Add basic image info
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'is_animated': getattr(img, 'is_animated', False),
                    'n_frames': getattr(img, 'n_frames', 1)
                })
                
                # Extract EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            exif_data[tag] = value
                
                # Use piexif as a fallback for more comprehensive EXIF extraction
                if not exif_data:
                    try:
                        exif_dict = piexif.load(file_path)
                        for ifd in ("0th", "Exif", "GPS", "1st"):
                            for tag in exif_dict[ifd]:
                                tag_name = piexif.TAGS[ifd][tag]["name"]
                                tag_value = exif_dict[ifd][tag]
                                # Convert byte values to strings
                                if isinstance(tag_value, bytes):
                                    try:
                                        tag_value = tag_value.decode('utf-8')
                                    except UnicodeDecodeError:
                                        tag_value = str(tag_value)
                                exif_data[tag_name] = tag_value
                    except (piexif.InvalidImageDataError, ValueError):
                        pass
                
                # Add EXIF data to metadata
                if exif_data:
                    # Process and clean up EXIF data
                    cleaned_exif = {}
                    for key, value in exif_data.items():
                        # Skip binary data or very large values
                        if isinstance(value, bytes) and len(value) > 100:
                            continue
                        # Convert non-serializable types to strings
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            value = str(value)
                        cleaned_exif[key] = value
                    
                    metadata['exif'] = cleaned_exif
                
                # Extract color profile information if available
                if 'icc_profile' in img.info:
                    metadata['has_color_profile'] = True
                
                return metadata
        except Exception as e:
            # Return basic metadata with error information
            metadata['error'] = str(e)
            return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the image file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview, or the preview data as bytes.
        """
        try:
            # Get max preview size from config or use default
            max_size = kwargs.get('max_preview_size', 1024)
            if width is None and height is None:
                width = max_size
            
            # Open the image
            with Image.open(file_path) as img:
                # Resize the image while maintaining aspect ratio
                img.thumbnail((width if width else max_size, height if height else max_size))
                
                # Save the preview
                if output_path:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Save to the specified path
                    img.save(output_path)
                    return output_path
                else:
                    # Return the image data as bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format if img.format else 'JPEG')
                    return img_byte_arr.getvalue()
        except Exception as e:
            # Return error information
            return {'error': str(e)}
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 128, **kwargs) -> Any:
        """
        Generate a thumbnail for the image file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 128).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail, or the thumbnail data as bytes.
        """
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
        return ['image/jpeg', 'image/png', 'image/gif']