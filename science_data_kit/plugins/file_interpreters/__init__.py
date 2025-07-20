"""
File Interpreter Plugins for Science Data Kit

This package contains plugins for interpreting different file types,
extracting metadata, and generating previews. These plugins enable
the system to work with specialized scientific file formats, document
types, and media files.

To create a new file interpreter plugin:
1. Create a new Python module in this package
2. Define a class that inherits from FileInterpreterPlugin
3. Implement the required methods
4. Decorate the class with @register_plugin

Example:
    from science_data_kit.core.integrations.plugin_architecture import FileInterpreterPlugin, register_plugin
    
    @register_plugin
    class PDFInterpreter(FileInterpreterPlugin):
        # Implementation here
"""

# Import for convenience
from science_data_kit.core.integrations.plugin_architecture import FileInterpreterPlugin, register_plugin