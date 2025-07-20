# Plugin Interfaces Documentation

## Overview

This document provides detailed information about the plugin interfaces in the Science Data Kit, with a focus on file interpreters and metadata extractors. It explains how to create custom plugins, the required methods and capabilities, and how plugins are validated and registered.

## Plugin Architecture

The Science Data Kit uses a plugin architecture to enable extensibility and modularity. Plugins are used for various purposes, including data source integration, analysis tools, visualization, and file handling. The plugin architecture consists of:

1. **Base Classes**: Abstract base classes that define the interface for different types of plugins
2. **Plugin Registry**: A system for discovering, registering, and managing plugins
3. **Capability Mixins**: Classes that provide specific capabilities that can be mixed into plugins
4. **Validation**: Functions to ensure plugins implement the required methods and capabilities

## Plugin Categories

The Science Data Kit supports the following plugin categories:

- `DATA_SOURCE`: Plugins that provide access to external data sources
- `ANALYSIS_TOOL`: Plugins that provide data analysis capabilities
- `VISUALIZATION`: Plugins that provide data visualization capabilities
- `EXPORT`: Plugins that export data to external formats
- `IMPORT`: Plugins that import data from external formats
- `PLATFORM`: Plugins that integrate with external platforms
- `UTILITY`: Utility plugins for various purposes
- `FILE_INTERPRETER`: Plugins that interpret different file types
- `METADATA_EXTRACTOR`: Plugins that extract metadata from files
- `OTHER`: Other types of plugins

## File Interpreter Plugins

File interpreter plugins provide capabilities for interpreting different file types, extracting metadata, and generating previews. These plugins enable the system to work with specialized scientific file formats, document types, and media files.

### Creating a File Interpreter Plugin

To create a file interpreter plugin, you need to:

1. Create a class that inherits from `FileInterpreterPlugin`
2. Implement the required methods
3. Optionally mix in capability classes for additional functionality
4. Register the plugin with the plugin registry

Here's an example of a simple file interpreter plugin:

```python
from science_data_kit.core.integrations.plugin_architecture import (
    FileInterpreterPlugin, PluginMetadata, PluginCategory, 
    FileInterpreterCapability, TextExtractionCapability
)

class TextFileInterpreter(FileInterpreterPlugin, TextExtractionCapability):
    """A plugin for interpreting text files."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="text_file_interpreter",
            version="1.0.0",
            description="A plugin for interpreting text files",
            author="Your Name",
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
        return file_path.lower().endswith(('.txt', '.md', '.csv', '.json', '.yaml', '.yml'))
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of file extensions supported by this interpreter."""
        return ['.txt', '.md', '.csv', '.json', '.yaml', '.yml']
    
    def get_supported_mime_types(self) -> List[str]:
        """Get a list of MIME types supported by this interpreter."""
        return [
            'text/plain', 'text/markdown', 'text/csv', 
            'application/json', 'application/yaml', 'application/x-yaml'
        ]
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the file."""
        metadata = self.get_file_info(file_path)
        
        # Add additional metadata specific to text files
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            metadata['line_count'] = len(content.splitlines())
            metadata['word_count'] = len(content.split())
            metadata['char_count'] = len(content)
        
        return metadata
    
    def generate_preview(self, file_path: str, output_path: Optional[str] = None, **kwargs) -> Any:
        """Generate a preview for the file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Read first 1000 characters
            return content
    
    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        """Extract text content from the file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            return None
```

### Required Methods for File Interpreter Plugins

File interpreter plugins must implement the following methods:

1. **metadata**: A property that returns a `PluginMetadata` object with information about the plugin
2. **initialize**: Initialize the plugin
3. **shutdown**: Shut down the plugin and release any resources
4. **can_interpret**: Check if the plugin can interpret a given file
5. **get_supported_extensions**: Get a list of file extensions supported by the plugin
6. **get_supported_mime_types**: Get a list of MIME types supported by the plugin
7. **extract_metadata**: Extract metadata from a file
8. **generate_preview**: Generate a preview for a file

### File Interpreter Capabilities

File interpreter plugins can provide additional capabilities by mixing in capability classes or implementing specific methods. The following capabilities are supported:

1. **TextExtractionCapability**: Extract text content from files
2. **PreviewGenerationCapability**: Generate visual previews of files
3. **ThumbnailGenerationCapability**: Generate small thumbnail images for files
4. **ContentAnalysisCapability**: Analyze file content (keywords, sentiment, entities, etc.)
5. **StructuredDataExtractionCapability**: Extract structured data like tables, charts, forms, etc.

To add a capability to your plugin, either:
- Mix in the corresponding capability class, or
- Implement the required methods directly in your plugin class

For example, to add text extraction capability:

```python
class MyFileInterpreter(FileInterpreterPlugin, TextExtractionCapability):
    # ...
```

Or:

```python
class MyFileInterpreter(FileInterpreterPlugin):
    # ...
    
    def extract_text(self, file_path: str, **kwargs) -> Optional[str]:
        # Implementation here
        pass
```

## Metadata Extractor Plugins

Metadata extractor plugins provide specialized capabilities for extracting metadata from specific file types or from file content. These plugins can be used independently or in conjunction with file interpreters to provide enhanced metadata extraction capabilities.

### Creating a Metadata Extractor Plugin

To create a metadata extractor plugin, you need to:

1. Create a class that inherits from `MetadataExtractorPlugin`
2. Implement the required methods
3. Register the plugin with the plugin registry

Here's an example of a simple metadata extractor plugin:

```python
from science_data_kit.core.integrations.plugin_architecture import (
    MetadataExtractorPlugin, PluginMetadata, PluginCategory
)

class ExifMetadataExtractor(MetadataExtractorPlugin):
    """A plugin for extracting EXIF metadata from image files."""
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="exif_metadata_extractor",
            version="1.0.0",
            description="A plugin for extracting EXIF metadata from image files",
            author="Your Name",
            category=PluginCategory.METADATA_EXTRACTOR
        )
    
    def initialize(self) -> bool:
        """Initialize the plugin."""
        try:
            import PIL.Image
            import PIL.ExifTags
            return True
        except ImportError:
            logger.error("Failed to import PIL. Please install Pillow.")
            return False
    
    def shutdown(self) -> bool:
        """Shut down the plugin."""
        return True
    
    def can_extract(self, file_path: str, mime_type: Optional[str] = None) -> bool:
        """Check if this plugin can extract metadata from the given file."""
        return file_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif'))
    
    def get_supported_extensions(self) -> List[str]:
        """Get a list of file extensions supported by this extractor."""
        return ['.jpg', '.jpeg', '.tiff', '.tif']
    
    def get_supported_mime_types(self) -> List[str]:
        """Get a list of MIME types supported by this extractor."""
        return ['image/jpeg', 'image/tiff']
    
    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from the file."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            metadata = {}
            
            with Image.open(file_path) as img:
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata[tag] = value
                
                # Add basic image information
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['format'] = img.format
                metadata['mode'] = img.mode
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract EXIF metadata from {file_path}: {str(e)}")
            return {}
    
    def get_metadata_schema(self) -> Dict[str, Any]:
        """Get the schema for the metadata extracted by this plugin."""
        return {
            "type": "object",
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"},
                "format": {"type": "string"},
                "mode": {"type": "string"},
                "Make": {"type": "string"},
                "Model": {"type": "string"},
                "DateTime": {"type": "string"},
                "ExposureTime": {"type": "number"},
                "FNumber": {"type": "number"},
                "ISOSpeedRatings": {"type": "integer"},
                "FocalLength": {"type": "number"},
                "GPSInfo": {"type": "object"}
            }
        }
    
    def get_extraction_capabilities(self) -> List[str]:
        """Get a list of metadata extraction capabilities provided by this plugin."""
        return ["EXIF", "image_dimensions", "camera_info", "gps_location"]
```

### Required Methods for Metadata Extractor Plugins

Metadata extractor plugins must implement the following methods:

1. **metadata**: A property that returns a `PluginMetadata` object with information about the plugin
2. **initialize**: Initialize the plugin
3. **shutdown**: Shut down the plugin and release any resources
4. **can_extract**: Check if the plugin can extract metadata from a given file
5. **get_supported_extensions**: Get a list of file extensions supported by the plugin
6. **get_supported_mime_types**: Get a list of MIME types supported by the plugin
7. **extract_metadata**: Extract metadata from a file

### Optional Methods for Metadata Extractor Plugins

Metadata extractor plugins can optionally implement the following methods:

1. **get_metadata_schema**: Get the schema for the metadata extracted by the plugin
2. **get_extraction_capabilities**: Get a list of metadata extraction capabilities provided by the plugin

## Plugin Validation

The Science Data Kit includes validation functions to ensure that plugins implement all required methods and capabilities. When a plugin is registered, it is validated to ensure it meets the requirements for its category.

### Validation for File Interpreter Plugins

File interpreter plugins are validated to ensure they implement the following methods:

1. **can_interpret**: Check if the plugin can interpret a given file
2. **get_supported_extensions**: Get a list of file extensions supported by the plugin
3. **get_supported_mime_types**: Get a list of MIME types supported by the plugin
4. **extract_metadata**: Extract metadata from a file
5. **generate_preview**: Generate a preview for a file

If a plugin declares capabilities in its metadata, it is also validated to ensure it implements the required methods for those capabilities.

### Validation for Metadata Extractor Plugins

Metadata extractor plugins are validated to ensure they implement the following methods:

1. **can_extract**: Check if the plugin can extract metadata from a given file
2. **get_supported_extensions**: Get a list of file extensions supported by the plugin
3. **get_supported_mime_types**: Get a list of MIME types supported by the plugin
4. **extract_metadata**: Extract metadata from a file

### Validation Results

The validation functions return a dictionary mapping validation criteria to boolean results. The dictionary includes an "is_valid" key that indicates whether the plugin passed validation.

For example:

```python
{
    "has_can_interpret": True,
    "has_get_supported_extensions": True,
    "has_get_supported_mime_types": True,
    "has_extract_metadata": True,
    "has_generate_preview": True,
    "implements_text_extraction": True,
    "is_valid": True
}
```

## Plugin Registration

Plugins are registered with the plugin registry, which manages plugin discovery, loading, and lifecycle. When a plugin is registered, it is validated to ensure it meets the requirements for its category.

### Registering a Plugin

To register a plugin, you can use the `register_plugin` decorator:

```python
from science_data_kit.core.integrations.plugin_architecture import register_plugin

@register_plugin
class MyFileInterpreter(FileInterpreterPlugin):
    # ...
```

Or register it manually:

```python
from science_data_kit.core.integrations.plugin_architecture import plugin_registry

plugin_registry.register_plugin(MyFileInterpreter)
```

### Plugin Discovery

The plugin registry can automatically discover plugins in a package:

```python
from science_data_kit.core.integrations.plugin_architecture import discover_plugins

discover_plugins("my_package.plugins")
```

## Conclusion

The plugin architecture in the Science Data Kit provides a flexible and extensible way to add new capabilities to the system. By creating custom file interpreter and metadata extractor plugins, you can enable the system to work with specialized scientific file formats, document types, and media files.

For more information, see the API documentation for the `plugin_architecture` module.