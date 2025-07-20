"""
Tests for plugin validation functions in the plugin architecture.
"""

import unittest
from typing import Any, Dict, List, Optional

from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, MetadataExtractorPlugin, PluginMetadata, PluginCategory,
    FileInterpreterCapability, TextExtractionCapability, validate_plugin
)


class TestFileInterpreter(FileInterpreterPlugin, TextExtractionCapability):
    """A test file interpreter plugin for validation testing."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="test_file_interpreter",
            version="1.0.0",
            description="A test file interpreter plugin",
            author="Test Author",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=[FileInterpreterCapability.TEXT_EXTRACTION.value]
        )
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        return True
    
    def shutdown(self) -> bool:
        """Shut down the plugin."""
        return True
    
    def can_interpret(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """Check if this plugin can interpret the given file."""
        return file_path.lower().endswith('.txt')
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of file extensions supported by this interpreter."""
        return ['.txt']
    
    def get_supported_mime_types(self) -> List[str]:
        """Get a list of MIME types supported by this interpreter."""
        return ['text/plain']
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the file."""
        return self.get_file_info(file_path)
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
        """Generate a preview for the file."""
        return "Test preview"
    
    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        """Extract text content from the file."""
        return "Test text content"


class TestMetadataExtractor(MetadataExtractorPlugin):
    """A test metadata extractor plugin for validation testing."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="test_metadata_extractor",
            version="1.0.0",
            description="A test metadata extractor plugin",
            author="Test Author",
            category=PluginCategory.METADATA_EXTRACTOR
        )
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        return True
    
    def shutdown(self) -> bool:
        """Shut down the plugin."""
        return True
    
    def can_extract(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """Check if this plugin can extract metadata from the given file."""
        return file_path.lower().endswith('.jpg')
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of file extensions supported by this extractor."""
        return ['.jpg', '.jpeg']
    
    def get_supported_mime_types(self) -> List[str]:
        """Get a list of MIME types supported by this extractor."""
        return ['image/jpeg']
    
    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from the file."""
        return {"test": "metadata"}


class InvalidFileInterpreter(FileInterpreterPlugin):
    """An invalid file interpreter plugin missing required methods."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="invalid_file_interpreter",
            version="1.0.0",
            description="An invalid file interpreter plugin",
            author="Test Author",
            category=PluginCategory.FILE_INTERPRETER,
            capabilities=[FileInterpreterCapability.TEXT_EXTRACTION.value]
        )
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        return True
    
    def shutdown(self) -> bool:
        """Shut down the plugin."""
        return True
    
    # Missing required methods:
    # - can_interpret
    # - get_supported_extensions
    # - get_supported_mime_types
    # - extract_metadata
    # - generate_preview
    
    # Missing capability methods:
    # - extract_text


class TestPluginValidation(unittest.TestCase):
    """Test cases for plugin validation functions."""
    
    def test_valid_file_interpreter(self):
        """Test validation of a valid file interpreter plugin."""
        plugin = TestFileInterpreter()
        validation_results = validate_plugin(plugin)
        
        self.assertTrue(validation_results["is_valid"])
        self.assertTrue(validation_results["has_can_interpret"])
        self.assertTrue(validation_results["has_get_supported_extensions"])
        self.assertTrue(validation_results["has_get_supported_mime_types"])
        self.assertTrue(validation_results["has_extract_metadata"])
        self.assertTrue(validation_results["has_generate_preview"])
        self.assertTrue(validation_results["implements_text_extraction"])
        self.assertTrue(validation_results["capabilities_valid"])
    
    def test_valid_metadata_extractor(self):
        """Test validation of a valid metadata extractor plugin."""
        plugin = TestMetadataExtractor()
        validation_results = validate_plugin(plugin)
        
        self.assertTrue(validation_results["is_valid"])
        self.assertTrue(validation_results["has_can_extract"])
        self.assertTrue(validation_results["has_get_supported_extensions"])
        self.assertTrue(validation_results["has_get_supported_mime_types"])
        self.assertTrue(validation_results["has_extract_metadata"])
    
    def test_invalid_file_interpreter(self):
        """Test validation of an invalid file interpreter plugin."""
        plugin = InvalidFileInterpreter()
        validation_results = validate_plugin(plugin)
        
        self.assertFalse(validation_results["is_valid"])
        self.assertFalse(validation_results["has_can_interpret"])
        self.assertFalse(validation_results["has_get_supported_extensions"])
        self.assertFalse(validation_results["has_get_supported_mime_types"])
        self.assertFalse(validation_results["has_extract_metadata"])
        self.assertFalse(validation_results["has_generate_preview"])
        self.assertFalse(validation_results["implements_text_extraction"])
        self.assertFalse(validation_results["capabilities_valid"])


if __name__ == '__main__':
    unittest.main()