"""
MP3 file interpreter plugin for Science Data Kit.

This plugin can interpret MP3 audio files, extract metadata,
and generate waveform previews.
"""

import os
import io
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class MP3FileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, ThumbnailGenerationCapability):
    """
    File interpreter plugin for MP3 audio files.
    
    This plugin can interpret MP3 audio files, extract ID3 metadata,
    and generate waveform previews and thumbnails.
    """
    
    def __init__(self):
        """Initialize the MP3 file interpreter."""
        super().__init__()
        self.supported_extensions = ['.mp3']
        self.supported_mime_types = ['audio/mpeg']
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="MP3 File Interpreter",
            description="Interprets MP3 audio files, extracts ID3 metadata, and generates waveform previews",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation"],
            config_schema={
                "max_preview_width": {
                    "type": "integer",
                    "description": "Maximum width for waveform previews",
                    "default": 1024
                },
                "max_preview_height": {
                    "type": "integer",
                    "description": "Maximum height for waveform previews",
                    "default": 256
                },
                "max_thumbnail_width": {
                    "type": "integer",
                    "description": "Maximum width for waveform thumbnails",
                    "default": 128
                },
                "max_thumbnail_height": {
                    "type": "integer",
                    "description": "Maximum height for waveform thumbnails",
                    "default": 64
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
        
        # Try to open the file with mutagen as a last resort
        try:
            MP3(file_path)
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
        Extract metadata from the MP3 file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        try:
            # Extract MP3-specific metadata
            audio = MP3(file_path)
            
            # Add basic audio info
            metadata.update({
                'bitrate': audio.info.bitrate,
                'sample_rate': audio.info.sample_rate,
                'channels': audio.info.channels,
                'length': audio.info.length,
                'encoder_info': getattr(audio.info, 'encoder_info', None),
                'layer': getattr(audio.info, 'layer', None),
                'mode': getattr(audio.info, 'mode', None)
            })
            
            # Extract ID3 tags if available
            if audio.tags:
                id3_metadata = {}
                
                # Map common ID3 tags to more readable names
                tag_mapping = {
                    'TIT2': 'title',
                    'TPE1': 'artist',
                    'TALB': 'album',
                    'TDRC': 'year',
                    'TCON': 'genre',
                    'TRCK': 'track',
                    'TPOS': 'disc',
                    'TCOM': 'composer',
                    'TPUB': 'publisher',
                    'TCOP': 'copyright',
                    'TENC': 'encoded_by',
                    'COMM': 'comments',
                    'TLEN': 'length_ms',
                    'TBPM': 'bpm'
                }
                
                # Extract mapped tags
                for tag_id, tag_name in tag_mapping.items():
                    if tag_id in audio.tags:
                        id3_metadata[tag_name] = str(audio.tags[tag_id])
                
                # Add ID3 metadata to the main metadata dictionary
                metadata['id3'] = id3_metadata
        except Exception as e:
            metadata['error'] = f"Error extracting MP3 metadata: {str(e)}"
        
        return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a waveform preview for the MP3 file.
        
        Args:
            file_path: Path to the file to generate a preview for.
            output_path: Optional path to save the preview to.
            width: Optional width for the preview.
            height: Optional height for the preview.
            **kwargs: Additional parameters for preview generation.
            
        Returns:
            Path to the generated preview image.
        """
        # For now, return a placeholder message
        # In a real implementation, this would generate a waveform image
        if output_path:
            with open(output_path, 'w') as f:
                f.write("MP3 waveform preview placeholder")
            return output_path
        else:
            return "MP3 waveform preview placeholder"
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 128, height: int = 64, **kwargs) -> Any:
        """
        Generate a waveform thumbnail for the MP3 file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 128).
            height: Height for the thumbnail (default: 64).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail image.
        """
        # For now, return a placeholder message
        # In a real implementation, this would generate a small waveform image
        if output_path:
            with open(output_path, 'w') as f:
                f.write("MP3 waveform thumbnail placeholder")
            return output_path
        else:
            return "MP3 waveform thumbnail placeholder"
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.
        
        Returns:
            List of supported preview formats.
        """
        return ['image/png', 'image/jpeg']