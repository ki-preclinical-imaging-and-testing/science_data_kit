"""
MP4 file interpreter plugin for Science Data Kit.

This plugin can interpret MP4 video files, extract metadata,
and generate thumbnail previews.
"""

import os
import io
from typing import Any, Dict, List, Optional
from pathlib import Path
import mimetypes
import mutagen
from mutagen.mp4 import MP4

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory
)


@register_plugin
class MP4FileInterpreter(FileInterpreterPlugin, PreviewGenerationCapability, ThumbnailGenerationCapability):
    """
    File interpreter plugin for MP4 video files.
    
    This plugin can interpret MP4 video files, extract metadata,
    and generate thumbnail previews.
    """
    
    def __init__(self):
        """Initialize the MP4 file interpreter."""
        super().__init__()
        self.supported_extensions = ['.mp4', '.m4a', '.m4v']
        self.supported_mime_types = ['video/mp4', 'audio/mp4', 'audio/x-m4a', 'video/x-m4v']
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="MP4 File Interpreter",
            description="Interprets MP4 video files, extracts metadata, and generates thumbnail previews",
            version="1.0.0",
            author="Science Data Kit Team",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=["preview_generation", "thumbnail_generation"],
            config_schema={
                "max_preview_width": {
                    "type": "integer",
                    "description": "Maximum width for video previews",
                    "default": 1024
                },
                "max_preview_height": {
                    "type": "integer",
                    "description": "Maximum height for video previews",
                    "default": 576
                },
                "max_thumbnail_width": {
                    "type": "integer",
                    "description": "Maximum width for video thumbnails",
                    "default": 192
                },
                "max_thumbnail_height": {
                    "type": "integer",
                    "description": "Maximum height for video thumbnails",
                    "default": 108
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
            MP4(file_path)
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
        Extract metadata from the MP4 file.
        
        Args:
            file_path: Path to the file to extract metadata from.
            
        Returns:
            Dictionary of metadata key-value pairs.
        """
        # Get basic file info
        metadata = self.get_file_info(file_path)
        
        try:
            # Extract MP4-specific metadata
            video = MP4(file_path)
            
            # Add basic video/audio info
            metadata.update({
                'length': video.info.length,
                'bitrate': getattr(video.info, 'bitrate', None),
                'channels': getattr(video.info, 'channels', None),
                'sample_rate': getattr(video.info, 'sample_rate', None),
                'codec': getattr(video.info, 'codec', None),
                'codec_description': getattr(video.info, 'codec_description', None)
            })
            
            # Extract MP4 tags if available
            if video.tags:
                mp4_metadata = {}
                
                # Map common MP4 tags to more readable names
                tag_mapping = {
                    '©nam': 'title',
                    '©ART': 'artist',
                    '©alb': 'album',
                    '©day': 'year',
                    '©gen': 'genre',
                    'trkn': 'track',
                    'disk': 'disc',
                    '©wrt': 'composer',
                    '©cmt': 'comment',
                    'cprt': 'copyright',
                    '©too': 'encoded_by',
                    'tmpo': 'bpm',
                    'covr': 'cover_art'
                }
                
                # Extract mapped tags
                for tag_id, tag_name in tag_mapping.items():
                    if tag_id in video.tags:
                        # Handle special cases for track, disc, and cover art
                        if tag_id == 'trkn' or tag_id == 'disk':
                            mp4_metadata[tag_name] = str(video.tags[tag_id][0][0])
                            if video.tags[tag_id][0][1] > 0:
                                mp4_metadata[f'{tag_name}_total'] = str(video.tags[tag_id][0][1])
                        elif tag_id == 'covr':
                            mp4_metadata[tag_name] = f"Cover art present ({len(video.tags[tag_id])} images)"
                        else:
                            mp4_metadata[tag_name] = str(video.tags[tag_id][0])
                
                # Add MP4 metadata to the main metadata dictionary
                metadata['mp4'] = mp4_metadata
            
            # Try to extract video dimensions if available
            # Note: This would typically require a video processing library like ffmpeg or opencv
            # For now, we'll just add a placeholder
            metadata['video_info'] = {
                'dimensions': 'Not available in this implementation',
                'frame_rate': 'Not available in this implementation',
                'video_codec': 'Not available in this implementation'
            }
            
        except Exception as e:
            metadata['error'] = f"Error extracting MP4 metadata: {str(e)}"
        
        return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, 
                         width: Optional[int] = None, height: Optional[int] = None,
                         **kwargs) -> Any:
        """
        Generate a preview for the MP4 file.
        
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
        # In a real implementation, this would extract a frame from the video
        if output_path:
            with open(output_path, 'w') as f:
                f.write("MP4 video preview placeholder")
            return output_path
        else:
            return "MP4 video preview placeholder"
    
    def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                          width: int = 192, height: int = 108, **kwargs) -> Any:
        """
        Generate a thumbnail for the MP4 file.
        
        Args:
            file_path: Path to the file to generate a thumbnail for.
            output_path: Optional path to save the thumbnail to.
            width: Width for the thumbnail (default: 192).
            height: Height for the thumbnail (default: 108).
            **kwargs: Additional parameters for thumbnail generation.
            
        Returns:
            Path to the generated thumbnail image.
        """
        # For now, return a placeholder message
        # In a real implementation, this would extract a frame from the video and resize it
        if output_path:
            with open(output_path, 'w') as f:
                f.write("MP4 video thumbnail placeholder")
            return output_path
        else:
            return "MP4 video thumbnail placeholder"
    
    def get_preview_formats(self) -> List[str]:
        """
        Get a list of preview formats supported by this interpreter.
        
        Returns:
            List of supported preview formats.
        """
        return ['image/png', 'image/jpeg']