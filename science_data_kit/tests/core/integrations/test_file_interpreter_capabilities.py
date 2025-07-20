"""
Tests for the file interpreter capabilities and plugin selection logic.

This module contains tests for the capability mixins, MIME type mapping,
and plugin selection logic for file interpreter plugins.
"""

import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any, List, Optional

from science_data_kit.core.integrations.plugin_architecture import (
    PluginBase, PluginMetadata, PluginCategory, FileInterpreterPlugin,
    TextExtractionCapability, PreviewGenerationCapability, ThumbnailGenerationCapability,
    ContentAnalysisCapability, StructuredDataExtractionCapability,
    FileInterpreterCapability, register_plugin, get_mime_type,
    get_plugins_by_capability, get_plugins_by_mime_type, get_plugins_by_extension,
    get_file_interpreter_for_file, plugin_registry
)


class TestFileInterpreterCapabilities(unittest.TestCase):
    """Tests for the file interpreter capabilities."""

    def setUp(self):
        """Set up the test environment."""
        # Clear the plugin registry before each test
        plugin_registry._plugins = {}
        plugin_registry._instances = {}
        plugin_registry._categories = {category: set() for category in PluginCategory}
        plugin_registry._capabilities = {}
        plugin_registry._mime_types = {}
        plugin_registry._file_extensions = {}
        plugin_registry._initialized = False

    def test_mime_type_mapping(self):
        """Test the MIME type mapping function."""
        # Test common file types
        self.assertEqual(get_mime_type('test.txt'), 'text/plain')
        self.assertEqual(get_mime_type('test.html'), 'text/html')
        self.assertEqual(get_mime_type('test.jpg'), 'image/jpeg')
        self.assertEqual(get_mime_type('test.png'), 'image/png')
        self.assertEqual(get_mime_type('test.pdf'), 'application/pdf')
        
        # Test scientific file types
        self.assertEqual(get_mime_type('test.nc'), 'application/x-netcdf')
        self.assertEqual(get_mime_type('test.hdf5'), 'application/x-hdf5')
        self.assertEqual(get_mime_type('test.fits'), 'application/fits')
        
        # Test unknown file type
        self.assertEqual(get_mime_type('test.unknown'), 'application/octet-stream')

    def test_capability_mixins(self):
        """Test the capability mixins for file interpreters."""
        
        # Create a test plugin that implements multiple capabilities
        class TestPlugin(FileInterpreterPlugin, TextExtractionCapability, PreviewGenerationCapability):
            """Test plugin implementing multiple capabilities."""
            
            def __init__(self):
                self._metadata = PluginMetadata(
                    name="test_plugin",
                    version="1.0.0",
                    description="Test plugin",
                    author="Test Author",
                    category=PluginCategory.FILE_INTERPRETER,
                    capabilities=[
                        FileInterpreterCapability.TEXT_EXTRACTION.value,
                        FileInterpreterCapability.PREVIEW_GENERATION.value
                    ]
                )
            
            @property
            def metadata(self) -> PluginMetadata:
                return self._metadata
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith('.txt') or file_path.endswith('.md')
            
            def get_supported_extensions(self) -> List[str]:
                return ['.txt', '.md']
            
            def get_supported_mime_types(self) -> List[str]:
                return ['text/plain', 'text/markdown']
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {'content_type': 'text', 'extension': Path(file_path).suffix}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None,
                               width: Optional[int] = None, height: Optional[int] = None,
                               **kwargs) -> Any:
                return f"Preview of {file_path}"
            
            def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except Exception:
                    return None
        
        # Register the test plugin
        register_plugin(TestPlugin)
        
        # Test that the plugin is registered with the correct capabilities
        self.assertIn("test_plugin", get_plugins_by_capability(FileInterpreterCapability.TEXT_EXTRACTION.value))
        self.assertIn("test_plugin", get_plugins_by_capability(FileInterpreterCapability.PREVIEW_GENERATION.value))
        
        # Test that the plugin is registered with the correct MIME types and extensions
        self.assertIn("test_plugin", get_plugins_by_mime_type('text/plain'))
        self.assertIn("test_plugin", get_plugins_by_mime_type('text/markdown'))
        self.assertIn("test_plugin", get_plugins_by_extension('.txt'))
        self.assertIn("test_plugin", get_plugins_by_extension('.md'))
        
        # Create a temporary text file for testing
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+', delete=False) as temp_file:
            temp_file.write("This is a test file.")
            temp_file_path = temp_file.name
        
        try:
            # Test that the plugin can be found for the file
            interpreter = get_file_interpreter_for_file(temp_file_path)
            self.assertIsNotNone(interpreter)
            self.assertEqual(interpreter.metadata.name, "test_plugin")
            
            # Test that the plugin can extract text from the file
            self.assertEqual(interpreter.extract_text(temp_file_path), "This is a test file.")
            
            # Test that the plugin can generate a preview for the file
            self.assertEqual(interpreter.generate_preview(temp_file_path), f"Preview of {temp_file_path}")
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_plugin_selection(self):
        """Test the plugin selection logic for file interpreters."""
        
        # Create multiple plugins with different capabilities and supported file types
        class TextPlugin(FileInterpreterPlugin, TextExtractionCapability):
            """Plugin for text files."""
            
            def __init__(self):
                self._metadata = PluginMetadata(
                    name="text_plugin",
                    version="1.0.0",
                    description="Text plugin",
                    author="Test Author",
                    category=PluginCategory.FILE_INTERPRETER,
                    capabilities=[FileInterpreterCapability.TEXT_EXTRACTION.value]
                )
            
            @property
            def metadata(self) -> PluginMetadata:
                return self._metadata
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith('.txt')
            
            def get_supported_extensions(self) -> List[str]:
                return ['.txt']
            
            def get_supported_mime_types(self) -> List[str]:
                return ['text/plain']
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {'content_type': 'text', 'extension': '.txt'}
            
            def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except Exception:
                    return None
        
        class ImagePlugin(FileInterpreterPlugin, PreviewGenerationCapability, ThumbnailGenerationCapability):
            """Plugin for image files."""
            
            def __init__(self):
                self._metadata = PluginMetadata(
                    name="image_plugin",
                    version="1.0.0",
                    description="Image plugin",
                    author="Test Author",
                    category=PluginCategory.FILE_INTERPRETER,
                    capabilities=[
                        FileInterpreterCapability.PREVIEW_GENERATION.value,
                        FileInterpreterCapability.THUMBNAIL_GENERATION.value
                    ]
                )
            
            @property
            def metadata(self) -> PluginMetadata:
                return self._metadata
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith(('.jpg', '.jpeg', '.png', '.gif'))
            
            def get_supported_extensions(self) -> List[str]:
                return ['.jpg', '.jpeg', '.png', '.gif']
            
            def get_supported_mime_types(self) -> List[str]:
                return ['image/jpeg', 'image/png', 'image/gif']
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {'content_type': 'image', 'extension': Path(file_path).suffix}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None,
                               width: Optional[int] = None, height: Optional[int] = None,
                               **kwargs) -> Any:
                return f"Preview of {file_path}"
            
            def generate_thumbnail(self, file_path: str, output_path: Optional[str] = None,
                                 width: int = 128, height: int = 128, **kwargs) -> Any:
                return f"Thumbnail of {file_path}"
        
        # Register the plugins
        register_plugin(TextPlugin)
        register_plugin(ImagePlugin)
        
        # Test plugin selection by file extension
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+', delete=False) as text_file:
            text_file_path = text_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', mode='wb', delete=False) as image_file:
            image_file_path = image_file.name
        
        try:
            # Test that the correct plugin is selected for a text file
            text_interpreter = get_file_interpreter_for_file(text_file_path)
            self.assertIsNotNone(text_interpreter)
            self.assertEqual(text_interpreter.metadata.name, "text_plugin")
            
            # Test that the correct plugin is selected for an image file
            image_interpreter = get_file_interpreter_for_file(image_file_path)
            self.assertIsNotNone(image_interpreter)
            self.assertEqual(image_interpreter.metadata.name, "image_plugin")
            
            # Test that no plugin is selected for an unsupported file type
            with tempfile.NamedTemporaryFile(suffix='.xyz', mode='w+', delete=False) as unknown_file:
                unknown_file_path = unknown_file.name
            
            try:
                unknown_interpreter = get_file_interpreter_for_file(unknown_file_path)
                self.assertIsNone(unknown_interpreter)
            finally:
                os.unlink(unknown_file_path)
        finally:
            # Clean up the temporary files
            os.unlink(text_file_path)
            os.unlink(image_file_path)


if __name__ == '__main__':
    unittest.main()