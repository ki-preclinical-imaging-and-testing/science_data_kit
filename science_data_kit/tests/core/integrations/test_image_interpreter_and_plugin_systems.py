"""
Tests for the ImageFileInterpreter plugin and plugin priority and dependency resolution systems.

This module contains tests for:
1. The ImageFileInterpreter plugin
2. The plugin priority system
3. The plugin dependency resolution system
"""

import os
import unittest
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from unittest.mock import patch, MagicMock

from PIL import Image

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin,
    PreviewGenerationCapability,
    ThumbnailGenerationCapability,
    register_plugin,
    PluginMetadata,
    PluginCategory,
    PluginRegistry,
    get_plugin_instance,
    get_plugin_registry
)

from science_data_kit.plugins.file_interpreters.image_interpreter import ImageFileInterpreter


class TestImageFileInterpreter(unittest.TestCase):
    """Tests for the ImageFileInterpreter plugin."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image_path = os.path.join(self.temp_dir.name, "test_image.jpg")
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image_path)
        
        # Create an instance of the image interpreter
        self.interpreter = ImageFileInterpreter()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_can_interpret(self):
        """Test that the interpreter can interpret image files."""
        self.assertTrue(self.interpreter.can_interpret(self.test_image_path))
        self.assertTrue(self.interpreter.can_interpret(self.test_image_path, mime_type="image/jpeg"))
        
        # Test with non-image file
        non_image_path = os.path.join(self.temp_dir.name, "test.txt")
        with open(non_image_path, "w") as f:
            f.write("This is not an image")
        self.assertFalse(self.interpreter.can_interpret(non_image_path))

    def test_get_supported_extensions(self):
        """Test that the interpreter returns the correct supported extensions."""
        extensions = self.interpreter.get_supported_extensions()
        self.assertIn(".jpg", extensions)
        self.assertIn(".jpeg", extensions)
        self.assertIn(".png", extensions)
        self.assertIn(".gif", extensions)
        self.assertIn(".bmp", extensions)

    def test_get_supported_mime_types(self):
        """Test that the interpreter returns the correct supported MIME types."""
        mime_types = self.interpreter.get_supported_mime_types()
        self.assertIn("image/jpeg", mime_types)
        self.assertIn("image/png", mime_types)
        self.assertIn("image/gif", mime_types)
        self.assertIn("image/bmp", mime_types)

    def test_extract_metadata(self):
        """Test that the interpreter can extract metadata from image files."""
        metadata = self.interpreter.extract_metadata(self.test_image_path)
        
        # Check basic metadata
        self.assertEqual(metadata["width"], 100)
        self.assertEqual(metadata["height"], 100)
        self.assertEqual(metadata["format"], "JPEG")
        self.assertEqual(metadata["mode"], "RGB")
        
        # Check file info
        self.assertEqual(metadata["name"], "test_image.jpg")
        self.assertEqual(metadata["extension"], ".jpg")
        self.assertFalse(metadata["is_directory"])

    def test_generate_preview(self):
        """Test that the interpreter can generate previews."""
        # Test with output path
        output_path = os.path.join(self.temp_dir.name, "preview.jpg")
        result = self.interpreter.generate_preview(self.test_image_path, output_path)
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Test without output path (returns bytes)
        result = self.interpreter.generate_preview(self.test_image_path)
        self.assertIsInstance(result, bytes)
        
        # Test with width and height
        result = self.interpreter.generate_preview(self.test_image_path, width=50, height=50)
        self.assertIsInstance(result, bytes)
        
        # Load the preview and check dimensions
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            temp.write(result)
            temp_path = temp.name
        
        with Image.open(temp_path) as img:
            self.assertLessEqual(img.width, 50)
            self.assertLessEqual(img.height, 50)
        
        os.unlink(temp_path)

    def test_generate_thumbnail(self):
        """Test that the interpreter can generate thumbnails."""
        # Test with output path
        output_path = os.path.join(self.temp_dir.name, "thumbnail.jpg")
        result = self.interpreter.generate_thumbnail(self.test_image_path, output_path)
        self.assertEqual(result, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Test without output path (returns bytes)
        result = self.interpreter.generate_thumbnail(self.test_image_path)
        self.assertIsInstance(result, bytes)
        
        # Test with custom dimensions
        result = self.interpreter.generate_thumbnail(self.test_image_path, width=64, height=64)
        self.assertIsInstance(result, bytes)
        
        # Load the thumbnail and check dimensions
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            temp.write(result)
            temp_path = temp.name
        
        with Image.open(temp_path) as img:
            self.assertLessEqual(img.width, 64)
            self.assertLessEqual(img.height, 64)
        
        os.unlink(temp_path)


class TestPluginPrioritySystem(unittest.TestCase):
    """Tests for the plugin priority system."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock plugin registry
        self.registry = PluginRegistry()
        
        # Create test plugins with different priorities
        @register_plugin
        class HighPriorityPlugin(FileInterpreterPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="HighPriorityPlugin",
                    description="High priority plugin",
                    version="1.0.0",
                    author="Test",
                    category=PluginCategory.FILE_INTERPRETER,
                    priority=100
                )
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith(".test")
            
            def get_supported_extensions(self) -> List[str]:
                return [".test"]
            
            def get_supported_mime_types(self) -> List[str]:
                return ["application/test"]
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {"plugin": "high_priority"}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
                return "high_priority_preview"
        
        @register_plugin
        class LowPriorityPlugin(FileInterpreterPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="LowPriorityPlugin",
                    description="Low priority plugin",
                    version="1.0.0",
                    author="Test",
                    category=PluginCategory.FILE_INTERPRETER,
                    priority=10
                )
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith(".test")
            
            def get_supported_extensions(self) -> List[str]:
                return [".test"]
            
            def get_supported_mime_types(self) -> List[str]:
                return ["application/test"]
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {"plugin": "low_priority"}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
                return "low_priority_preview"
        
        # Create a test file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test.test")
        with open(self.test_file_path, "w") as f:
            f.write("Test file")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch("science_data_kit.core.integrations.plugin_architecture.plugin_registry")
    def test_plugin_priority(self, mock_registry):
        """Test that the plugin with the highest priority is selected."""
        # Set up the mock registry
        mock_registry.get_plugins_by_extension.return_value = ["HighPriorityPlugin", "LowPriorityPlugin"]
        mock_registry.get_plugin_metadata.side_effect = lambda name: {
            "HighPriorityPlugin": PluginMetadata(
                name="HighPriorityPlugin",
                description="High priority plugin",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER,
                priority=100
            ),
            "LowPriorityPlugin": PluginMetadata(
                name="LowPriorityPlugin",
                description="Low priority plugin",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER,
                priority=10
            )
        }.get(name)
        
        # Set up the mock get_plugin_instance to return the appropriate plugin
        mock_registry.get_plugin_instance.side_effect = lambda name, initialize: {
            "HighPriorityPlugin": HighPriorityPlugin(),
            "LowPriorityPlugin": LowPriorityPlugin()
        }.get(name)
        
        # Call the method that uses the plugin priority system
        plugin = mock_registry.get_file_interpreter_for_file(self.test_file_path)
        
        # Verify that the high priority plugin was selected
        self.assertIsNotNone(plugin)
        metadata = plugin.extract_metadata(self.test_file_path)
        self.assertEqual(metadata["plugin"], "high_priority")


class TestPluginDependencyResolution(unittest.TestCase):
    """Tests for the plugin dependency resolution system."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock plugin registry
        self.registry = PluginRegistry()
        
        # Create test plugins with dependencies
        @register_plugin
        class DependentPlugin(FileInterpreterPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="DependentPlugin",
                    description="Plugin with dependencies",
                    version="1.0.0",
                    author="Test",
                    category=PluginCategory.FILE_INTERPRETER,
                    dependencies=["DependencyPlugin"]
                )
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith(".dep")
            
            def get_supported_extensions(self) -> List[str]:
                return [".dep"]
            
            def get_supported_mime_types(self) -> List[str]:
                return ["application/dep"]
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {"plugin": "dependent"}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
                return "dependent_preview"
        
        @register_plugin
        class DependencyPlugin(FileInterpreterPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="DependencyPlugin",
                    description="Dependency plugin",
                    version="1.0.0",
                    author="Test",
                    category=PluginCategory.FILE_INTERPRETER
                )
            
            def initialize(self) -> bool:
                return True
            
            def shutdown(self) -> bool:
                return True
            
            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return file_path.endswith(".base")
            
            def get_supported_extensions(self) -> List[str]:
                return [".base"]
            
            def get_supported_mime_types(self) -> List[str]:
                return ["application/base"]
            
            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {"plugin": "dependency"}
            
            def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
                return "dependency_preview"
        
        # Create a test file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test.dep")
        with open(self.test_file_path, "w") as f:
            f.write("Test file")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch("science_data_kit.core.integrations.plugin_architecture.plugin_registry")
    def test_dependency_resolution(self, mock_registry):
        """Test that plugin dependencies are resolved correctly."""
        # Set up the mock registry
        mock_registry.get_plugins_by_extension.return_value = ["DependentPlugin"]
        mock_registry.get_plugin_metadata.side_effect = lambda name: {
            "DependentPlugin": PluginMetadata(
                name="DependentPlugin",
                description="Plugin with dependencies",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER,
                dependencies=["DependencyPlugin"]
            ),
            "DependencyPlugin": PluginMetadata(
                name="DependencyPlugin",
                description="Dependency plugin",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER
            )
        }.get(name)
        
        # Track which plugins have been instantiated
        instantiated_plugins = []
        
        # Set up the mock get_plugin_instance to track instantiated plugins
        def mock_get_plugin_instance(name, initialize=True, _dependency_chain=None):
            instantiated_plugins.append(name)
            return {
                "DependentPlugin": DependentPlugin(),
                "DependencyPlugin": DependencyPlugin()
            }.get(name)
        
        mock_registry.get_plugin_instance.side_effect = mock_get_plugin_instance
        
        # Call the method that uses the dependency resolution system
        plugin = mock_registry.get_file_interpreter_for_file(self.test_file_path)
        
        # Verify that the dependency was instantiated before the dependent plugin
        self.assertIn("DependencyPlugin", instantiated_plugins)
        self.assertIn("DependentPlugin", instantiated_plugins)
        self.assertLess(instantiated_plugins.index("DependencyPlugin"), 
                        instantiated_plugins.index("DependentPlugin"))
        
        # Verify that the dependent plugin was returned
        self.assertIsNotNone(plugin)
        metadata = plugin.extract_metadata(self.test_file_path)
        self.assertEqual(metadata["plugin"], "dependent")

    @patch("science_data_kit.core.integrations.plugin_architecture.plugin_registry")
    def test_circular_dependency_detection(self, mock_registry):
        """Test that circular dependencies are detected and handled correctly."""
        # Set up the mock registry with circular dependencies
        mock_registry.get_plugins_by_extension.return_value = ["CircularPlugin1"]
        mock_registry.get_plugin_metadata.side_effect = lambda name: {
            "CircularPlugin1": PluginMetadata(
                name="CircularPlugin1",
                description="Circular dependency plugin 1",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER,
                dependencies=["CircularPlugin2"]
            ),
            "CircularPlugin2": PluginMetadata(
                name="CircularPlugin2",
                description="Circular dependency plugin 2",
                version="1.0.0",
                author="Test",
                category=PluginCategory.FILE_INTERPRETER,
                dependencies=["CircularPlugin1"]
            )
        }.get(name)
        
        # Set up the mock get_plugin_instance to handle circular dependencies
        def mock_get_plugin_instance(name, initialize=True, _dependency_chain=None):
            if _dependency_chain is None:
                _dependency_chain = []
            
            # Check for circular dependencies
            if name in _dependency_chain:
                return None
            
            # Add current plugin to dependency chain
            _dependency_chain = _dependency_chain + [name]
            
            # Get plugin metadata
            metadata = mock_registry.get_plugin_metadata(name)
            
            # Check and load dependencies
            if metadata and metadata.dependencies:
                for dependency in metadata.dependencies:
                    # Try to instantiate the dependency
                    dependency_instance = mock_get_plugin_instance(
                        dependency, initialize, _dependency_chain
                    )
                    
                    if not dependency_instance:
                        return None
            
            # Return a mock plugin instance
            return MagicMock()
        
        mock_registry.get_plugin_instance.side_effect = mock_get_plugin_instance
        
        # Call the method that uses the dependency resolution system
        plugin = mock_registry.get_file_interpreter_for_file(self.test_file_path)
        
        # Verify that no plugin was returned due to circular dependencies
        self.assertIsNone(plugin)


if __name__ == "__main__":
    unittest.main()