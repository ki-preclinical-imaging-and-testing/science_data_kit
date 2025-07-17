"""
Unit tests for the filesystem plugin template.

This module provides unit tests for the filesystem plugin template.
"""

import os
import tempfile
import unittest
from pathlib import Path

from science_data_kit.plugins.templates.filesystem_plugin_template import FilesystemPluginTemplate


class TestFilesystemPluginTemplate(unittest.TestCase):
    """Test case for the filesystem plugin template."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        
        # Create the plugin instance
        self.plugin = FilesystemPluginTemplate()
        
        # Initialize the plugin with the temporary directory
        self.config = {
            "root_directory": str(self.root_dir),
            "create_if_missing": True,
            "read_only": False,
        }
        self.plugin.initialize(self.config)
        
        # Connect to the filesystem
        self.plugin.connect(self.config)
        
    def tearDown(self):
        """Tear down the test case."""
        # Disconnect and shut down the plugin
        if self.plugin.is_connected:
            self.plugin.disconnect()
        if self.plugin.is_initialized:
            self.plugin.shutdown()
            
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization(self):
        """Test plugin initialization."""
        # Test that the plugin is initialized
        self.assertTrue(self.plugin.is_initialized)
        
        # Test that the plugin has the correct name, version, and description
        self.assertEqual(self.plugin.name, "filesystem_template")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.description, "Template implementation of a filesystem plugin")
        
        # Test that the plugin has the correct capabilities
        capabilities = self.plugin.capabilities
        self.assertIn("filesystem", capabilities)
        self.assertIn("browsable", capabilities)
        self.assertIn("writable", capabilities)
        self.assertIn("deletable", capabilities)
        self.assertIn("creatable", capabilities)
        
    def test_connection(self):
        """Test connection management."""
        # Test that the plugin is connected
        self.assertTrue(self.plugin.is_connected)
        
        # Test that the connection type is correct
        self.assertEqual(self.plugin.connection_type, "filesystem")
        
        # Test disconnection
        self.plugin.disconnect()
        self.assertFalse(self.plugin.is_connected)
        
        # Test reconnection
        self.plugin.connect(self.config)
        self.assertTrue(self.plugin.is_connected)
        
    def test_directory_operations(self):
        """Test directory operations."""
        # Test creating a directory
        self.assertTrue(self.plugin.create_directory("test_dir"))
        self.assertTrue(self.plugin.directory_exists("test_dir"))
        
        # Test creating a nested directory
        self.assertTrue(self.plugin.create_directory("test_dir/nested_dir"))
        self.assertTrue(self.plugin.directory_exists("test_dir/nested_dir"))
        
        # Test listing a directory
        dir_contents = self.plugin.list_directory("test_dir")
        self.assertEqual(len(dir_contents), 1)
        self.assertEqual(dir_contents[0]["name"], "nested_dir")
        self.assertTrue(dir_contents[0]["is_dir"])
        
        # Test deleting a directory
        self.assertTrue(self.plugin.delete_directory("test_dir/nested_dir"))
        self.assertFalse(self.plugin.directory_exists("test_dir/nested_dir"))
        
        # Test recursive directory deletion
        self.assertTrue(self.plugin.create_directory("test_dir/nested_dir"))
        self.assertTrue(self.plugin.create_directory("test_dir/nested_dir/deep_dir"))
        self.assertTrue(self.plugin.delete_directory("test_dir", recursive=True))
        self.assertFalse(self.plugin.directory_exists("test_dir"))
        
    def test_file_operations(self):
        """Test file operations."""
        # Test creating a file
        test_content = b"Hello, world!"
        self.assertTrue(self.plugin.write_file("test_file.txt", test_content))
        self.assertTrue(self.plugin.file_exists("test_file.txt"))
        
        # Test reading a file
        read_content = self.plugin.read_file("test_file.txt")
        self.assertEqual(read_content, test_content)
        
        # Test creating a file in a directory
        self.assertTrue(self.plugin.create_directory("test_dir"))
        self.assertTrue(self.plugin.write_file("test_dir/test_file.txt", test_content))
        self.assertTrue(self.plugin.file_exists("test_dir/test_file.txt"))
        
        # Test listing a directory with files
        dir_contents = self.plugin.list_directory("test_dir")
        self.assertEqual(len(dir_contents), 1)
        self.assertEqual(dir_contents[0]["name"], "test_file.txt")
        self.assertFalse(dir_contents[0]["is_dir"])
        self.assertEqual(dir_contents[0]["size"], len(test_content))
        
        # Test deleting a file
        self.assertTrue(self.plugin.delete_file("test_dir/test_file.txt"))
        self.assertFalse(self.plugin.file_exists("test_dir/test_file.txt"))
        
    def test_read_only_mode(self):
        """Test read-only mode."""
        # Create a file and directory for testing
        test_content = b"Hello, world!"
        self.assertTrue(self.plugin.write_file("test_file.txt", test_content))
        self.assertTrue(self.plugin.create_directory("test_dir"))
        
        # Disconnect and reconnect with read-only mode
        self.plugin.disconnect()
        read_only_config = self.config.copy()
        read_only_config["read_only"] = True
        self.plugin.initialize(read_only_config)
        self.plugin.connect(read_only_config)
        
        # Test that the plugin has the correct capabilities
        capabilities = self.plugin.capabilities
        self.assertIn("filesystem", capabilities)
        self.assertIn("browsable", capabilities)
        self.assertNotIn("writable", capabilities)
        self.assertNotIn("deletable", capabilities)
        self.assertNotIn("creatable", capabilities)
        
        # Test that we can read files
        read_content = self.plugin.read_file("test_file.txt")
        self.assertEqual(read_content, test_content)
        
        # Test that we can list directories
        dir_contents = self.plugin.list_directory(".")
        self.assertGreaterEqual(len(dir_contents), 2)
        
        # Test that we cannot write files
        with self.assertRaises(PermissionError):
            self.plugin.write_file("new_file.txt", b"New content")
            
        # Test that we cannot create directories
        with self.assertRaises(PermissionError):
            self.plugin.create_directory("new_dir")
            
        # Test that we cannot delete files
        with self.assertRaises(PermissionError):
            self.plugin.delete_file("test_file.txt")
            
        # Test that we cannot delete directories
        with self.assertRaises(PermissionError):
            self.plugin.delete_directory("test_dir")
            
    def test_path_validation(self):
        """Test path validation."""
        # Test that we cannot access files outside the root directory
        with self.assertRaises(ValueError):
            self.plugin.read_file("../outside.txt")
            
        with self.assertRaises(ValueError):
            self.plugin.read_file("test_dir/../../outside.txt")
            
        # Test that we can access files with normalized paths
        test_content = b"Hello, world!"
        self.assertTrue(self.plugin.write_file("test_file.txt", test_content))
        self.assertEqual(self.plugin.read_file("./test_file.txt"), test_content)
        self.assertEqual(self.plugin.read_file("test_dir/../test_file.txt"), test_content)


if __name__ == "__main__":
    unittest.main()