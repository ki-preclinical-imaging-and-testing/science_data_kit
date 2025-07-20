"""
Tests for file interpreter plugins.

This module contains tests for the file interpreter plugins,
including PDF, DOCX, NetCDF, and HDF5 interpreters.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

from science_data_kit.core.integrations.plugin_architecture import (
    PluginRegistry,
    PluginCategory,
    FileInterpreterPlugin
)


class TestFileInterpreters(unittest.TestCase):
    """Test case for file interpreter plugins."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a plugin registry
        self.registry = PluginRegistry()
        
        # Ensure the registry is initialized
        self.registry.initialize()
    
    def test_file_interpreter_plugins_registered(self):
        """Test that file interpreter plugins are registered."""
        # Get all file interpreter plugins
        file_interpreter_plugins = self.registry.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)
        
        # Check that we have at least one file interpreter plugin
        self.assertGreater(len(file_interpreter_plugins), 0)
        
        # Check for specific plugins
        plugin_names = [plugin.metadata.name for plugin in file_interpreter_plugins]
        
        # Print the available plugins for debugging
        print(f"Available file interpreter plugins: {plugin_names}")
        
        # Check for the PDF interpreter
        self.assertIn("PDF File Interpreter", plugin_names)
        
        # Check for the DOCX interpreter
        self.assertIn("DOCX File Interpreter", plugin_names)
        
        # Check for the NetCDF interpreter
        self.assertIn("NetCDF File Interpreter", plugin_names)
        
        # Check for the HDF5 interpreter
        self.assertIn("HDF5 File Interpreter", plugin_names)
    
    def test_file_interpreter_capabilities(self):
        """Test that file interpreter plugins have the expected capabilities."""
        # Get all file interpreter plugins
        file_interpreter_plugins = self.registry.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)
        
        for plugin in file_interpreter_plugins:
            # Check that the plugin has the required methods
            self.assertTrue(hasattr(plugin, 'can_interpret'))
            self.assertTrue(hasattr(plugin, 'get_supported_extensions'))
            self.assertTrue(hasattr(plugin, 'get_supported_mime_types'))
            self.assertTrue(hasattr(plugin, 'extract_metadata'))
            self.assertTrue(hasattr(plugin, 'generate_preview'))
            
            # Check that the plugin has the expected capabilities
            capabilities = plugin.metadata.capabilities
            
            # All plugins should have preview_generation capability
            self.assertIn('preview_generation', capabilities)
            
            # All plugins should have thumbnail_generation capability
            self.assertIn('thumbnail_generation', capabilities)
            
            # PDF and DOCX interpreters should have text_extraction capability
            if plugin.metadata.name in ["PDF File Interpreter", "DOCX File Interpreter"]:
                self.assertIn('text_extraction', capabilities)
            
            # NetCDF and HDF5 interpreters should have structured_data_extraction capability
            if plugin.metadata.name in ["NetCDF File Interpreter", "HDF5 File Interpreter"]:
                self.assertIn('structured_data_extraction', capabilities)
    
    def test_file_interpreter_supported_extensions(self):
        """Test that file interpreter plugins have the expected supported extensions."""
        # Get all file interpreter plugins
        file_interpreter_plugins = self.registry.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)
        
        for plugin in file_interpreter_plugins:
            extensions = plugin.get_supported_extensions()
            
            # Check that the plugin has at least one supported extension
            self.assertGreater(len(extensions), 0)
            
            # Check specific extensions for each plugin
            if plugin.metadata.name == "PDF File Interpreter":
                self.assertIn('.pdf', extensions)
            
            elif plugin.metadata.name == "DOCX File Interpreter":
                self.assertIn('.docx', extensions)
            
            elif plugin.metadata.name == "NetCDF File Interpreter":
                self.assertIn('.nc', extensions)
                self.assertIn('.nc4', extensions)
                self.assertIn('.cdf', extensions)
            
            elif plugin.metadata.name == "HDF5 File Interpreter":
                self.assertIn('.h5', extensions)
                self.assertIn('.hdf5', extensions)
    
    def test_file_interpreter_supported_mime_types(self):
        """Test that file interpreter plugins have the expected supported MIME types."""
        # Get all file interpreter plugins
        file_interpreter_plugins = self.registry.get_plugins_by_category(PluginCategory.FILE_INTERPRETER)
        
        for plugin in file_interpreter_plugins:
            mime_types = plugin.get_supported_mime_types()
            
            # Check that the plugin has at least one supported MIME type
            self.assertGreater(len(mime_types), 0)
            
            # Check specific MIME types for each plugin
            if plugin.metadata.name == "PDF File Interpreter":
                self.assertIn('application/pdf', mime_types)
            
            elif plugin.metadata.name == "DOCX File Interpreter":
                self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', mime_types)
            
            elif plugin.metadata.name == "NetCDF File Interpreter":
                self.assertIn('application/x-netcdf', mime_types)
                self.assertIn('application/netcdf', mime_types)
            
            elif plugin.metadata.name == "HDF5 File Interpreter":
                self.assertIn('application/x-hdf5', mime_types)
                self.assertIn('application/hdf5', mime_types)


if __name__ == '__main__':
    unittest.main()