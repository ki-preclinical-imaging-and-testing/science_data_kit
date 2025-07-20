"""
Metadata Extractor Plugins for Science Data Kit

This package contains plugins for extracting metadata from specific file types
or from file content. These plugins can be used independently or in conjunction
with file interpreters to provide enhanced metadata extraction capabilities.

To create a new metadata extractor plugin:
1. Create a new Python module in this package
2. Define a class that inherits from MetadataExtractorPlugin
3. Implement the required methods
4. Decorate the class with @register_plugin

Example:
    from science_data_kit.core.integrations.plugin_architecture import MetadataExtractorPlugin, register_plugin
    
    @register_plugin
    class EXIFExtractor(MetadataExtractorPlugin):
        # Implementation here
"""

# Import for convenience
from science_data_kit.core.integrations.plugin_architecture import MetadataExtractorPlugin, register_plugin