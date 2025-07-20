"""
Tests for the file handling plugins in the Science Data Kit.

This module contains tests for the FileInterpreterPlugin and MetadataExtractorPlugin
base classes, as well as integration tests for plugin discovery and registration.
"""

import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any, List, Optional

from science_data_kit.core.integrations.plugin_architecture import (
    PluginBase, PluginCategory, PluginMetadata,
    FileInterpreterPlugin, MetadataExtractorPlugin,
    register_plugin, plugin_registry
)


class TestFileInterpreterPlugin(unittest.TestCase):
    """Tests for the FileInterpreterPlugin base class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("Test file content")

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_file_interpreter_plugin_interface(self):
        """Test that the FileInterpreterPlugin interface is correctly defined."""
        # Verify that FileInterpreterPlugin is a subclass of PluginBase
        self.assertTrue(issubclass(FileInterpreterPlugin, PluginBase))

        # Verify that the required abstract methods are defined
        required_methods = [
            "can_interpret",
            "get_supported_extensions",
            "get_supported_mime_types",
            "extract_metadata",
            "generate_preview",
            "metadata",  # From PluginBase
            "initialize",  # From PluginBase
            "shutdown",  # From PluginBase
        ]

        for method in required_methods:
            self.assertTrue(
                hasattr(FileInterpreterPlugin, method),
                f"FileInterpreterPlugin should have method '{method}'"
            )

    def test_get_file_info(self):
        """Test the get_file_info method."""
        # Create a mock implementation of FileInterpreterPlugin
        class MockFileInterpreter(FileInterpreterPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="MockFileInterpreter",
                    version="1.0.0",
                    description="Mock file interpreter for testing",
                    author="Test Author",
                    category=PluginCategory.FILE_INTERPRETER
                )

            def initialize(self) -> bool:
                return True

            def shutdown(self) -> bool:
                return True

            def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return True

            def get_supported_extensions(self) -> List[str]:
                return [".txt"]

            def get_supported_mime_types(self) -> List[str]:
                return ["text/plain"]

            def extract_metadata(self, file_path: str) -> Dict[str, Any]:
                return {"content_type": "text/plain"}

            def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
                return "Preview of text file"

        # Create an instance of the mock interpreter
        interpreter = MockFileInterpreter()

        # Test the get_file_info method
        file_info = interpreter.get_file_info(self.test_file_path)

        # Verify the file info
        self.assertEqual(file_info["name"], "test_file.txt")
        self.assertEqual(file_info["extension"], ".txt")
        self.assertFalse(file_info["is_directory"])
        self.assertTrue("size" in file_info)
        self.assertTrue("created" in file_info)
        self.assertTrue("modified" in file_info)
        self.assertTrue("accessed" in file_info)


class TestMetadataExtractorPlugin(unittest.TestCase):
    """Tests for the MetadataExtractorPlugin base class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, "test_image.jpg")
        with open(self.test_file_path, "w") as f:
            f.write("Mock image file content")

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_metadata_extractor_plugin_interface(self):
        """Test that the MetadataExtractorPlugin interface is correctly defined."""
        # Verify that MetadataExtractorPlugin is a subclass of PluginBase
        self.assertTrue(issubclass(MetadataExtractorPlugin, PluginBase))

        # Verify that the required abstract methods are defined
        required_methods = [
            "can_extract",
            "get_supported_extensions",
            "get_supported_mime_types",
            "extract_metadata",
            "metadata",  # From PluginBase
            "initialize",  # From PluginBase
            "shutdown",  # From PluginBase
        ]

        for method in required_methods:
            self.assertTrue(
                hasattr(MetadataExtractorPlugin, method),
                f"MetadataExtractorPlugin should have method '{method}'"
            )

    def test_default_methods(self):
        """Test the default methods of MetadataExtractorPlugin."""
        # Create a mock implementation of MetadataExtractorPlugin
        class MockMetadataExtractor(MetadataExtractorPlugin):
            @property
            def metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="MockMetadataExtractor",
                    version="1.0.0",
                    description="Mock metadata extractor for testing",
                    author="Test Author",
                    category=PluginCategory.METADATA_EXTRACTOR
                )

            def initialize(self) -> bool:
                return True

            def shutdown(self) -> bool:
                return True

            def can_extract(self, file_path: str, mime_type: Optional[str] = None) -> bool:
                return True

            def get_supported_extensions(self) -> List[str]:
                return [".jpg", ".jpeg"]

            def get_supported_mime_types(self) -> List[str]:
                return ["image/jpeg"]

            def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
                return {"image_width": 800, "image_height": 600}

        # Create an instance of the mock extractor
        extractor = MockMetadataExtractor()

        # Test the default methods
        self.assertEqual(extractor.get_metadata_schema(), {})
        self.assertEqual(extractor.get_extraction_capabilities(), [])


class TestPluginDiscovery(unittest.TestCase):
    """Integration tests for plugin discovery and registration."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test plugins
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_plugin_path = os.path.join(self.temp_dir.name, "test_plugins")
        os.makedirs(self.test_plugin_path, exist_ok=True)

        # Create a test plugin module
        self.test_plugin_file = os.path.join(self.test_plugin_path, "test_plugin.py")
        with open(self.test_plugin_file, "w") as f:
            f.write("""
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, MetadataExtractorPlugin, PluginMetadata, PluginCategory, register_plugin
)
from typing import Dict, Any, List, Optional

@register_plugin
class TestFileInterpreter(FileInterpreterPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="TestFileInterpreter",
            version="1.0.0",
            description="Test file interpreter",
            author="Test Author",
            category=PluginCategory.FILE_INTERPRETER
        )

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        return file_path.endswith(".txt")

    def get_supported_extensions(self) -> List[str]:
        return [".txt"]

    def get_supported_mime_types(self) -> List[str]:
        return ["text/plain"]

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        return {"content_type": "text/plain"}

    def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
        return "Preview of text file"

@register_plugin
class TestMetadataExtractor(MetadataExtractorPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="TestMetadataExtractor",
            version="1.0.0",
            description="Test metadata extractor",
            author="Test Author",
            category=PluginCategory.METADATA_EXTRACTOR
        )

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def can_extract(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        return file_path.endswith(".jpg") or file_path.endswith(".jpeg")

    def get_supported_extensions(self) -> List[str]:
        return [".jpg", ".jpeg"]

    def get_supported_mime_types(self) -> List[str]:
        return ["image/jpeg"]

    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        return {"image_width": 800, "image_height": 600}
""")

        # Create an __init__.py file to make it a proper package
        with open(os.path.join(self.test_plugin_path, "__init__.py"), "w") as f:
            f.write("")

        # Add the temporary directory to the Python path
        import sys
        sys.path.insert(0, self.temp_dir.name)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory from the Python path
        import sys
        if self.temp_dir.name in sys.path:
            sys.path.remove(self.temp_dir.name)

        # Clean up the temporary directory
        self.temp_dir.cleanup()

        # Reset the plugin registry
        plugin_registry._plugins = {}
        plugin_registry._instances = {}
        plugin_registry._categories = {
            category: set() for category in PluginCategory
        }
        plugin_registry._initialized = False

    def test_plugin_discovery(self):
        """Test that plugins can be discovered and registered."""
        # Import the test plugin package
        import test_plugins

        # Discover plugins in the test package
        count = plugin_registry.discover_plugins("test_plugins")

        # Verify that the plugins were discovered
        self.assertEqual(count, 2, "Should have discovered 2 plugins")

        # Verify that the plugins are registered with the correct categories
        file_interpreter_plugins = plugin_registry.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)
        metadata_extractor_plugins = plugin_registry.get_plugins_by_category(PluginCategory.METADATA_EXTRACTOR)

        self.assertEqual(len(file_interpreter_plugins), 1, "Should have 1 file interpreter plugin")
        self.assertEqual(len(metadata_extractor_plugins), 1, "Should have 1 metadata extractor plugin")

        self.assertEqual(file_interpreter_plugins[0], "TestFileInterpreter")
        self.assertEqual(metadata_extractor_plugins[0], "TestMetadataExtractor")

    def test_plugin_instantiation(self):
        """Test that plugins can be instantiated and used."""
        # Import the test plugin package
        import test_plugins

        # Discover plugins in the test package
        plugin_registry.discover_plugins("test_plugins")

        # Get instances of the plugins
        file_interpreter = plugin_registry.get_plugin_instance("TestFileInterpreter")
        metadata_extractor = plugin_registry.get_plugin_instance("TestMetadataExtractor")

        # Verify that the plugins were instantiated
        self.assertIsNotNone(file_interpreter, "File interpreter plugin should be instantiated")
        self.assertIsNotNone(metadata_extractor, "Metadata extractor plugin should be instantiated")

        # Verify that the plugins have the correct type
        self.assertIsInstance(file_interpreter, FileInterpreterPlugin)
        self.assertIsInstance(metadata_extractor, MetadataExtractorPlugin)

        # Create test files
        text_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(text_file, "w") as f:
            f.write("Test file content")

        image_file = os.path.join(self.temp_dir.name, "test.jpg")
        with open(image_file, "w") as f:
            f.write("Mock image file content")

        # Test the file interpreter
        self.assertTrue(file_interpreter.can_interpret(text_file))
        self.assertFalse(file_interpreter.can_interpret(image_file))
        self.assertEqual(file_interpreter.extract_metadata(text_file), {"content_type": "text/plain"})
        self.assertEqual(file_interpreter.generate_preview(text_file), "Preview of text file")

        # Test the metadata extractor
        self.assertTrue(metadata_extractor.can_extract(image_file))
        self.assertFalse(metadata_extractor.can_extract(text_file))
        self.assertEqual(metadata_extractor.extract_metadata(image_file), {"image_width": 800, "image_height": 600})


if __name__ == "__main__":
    unittest.main()