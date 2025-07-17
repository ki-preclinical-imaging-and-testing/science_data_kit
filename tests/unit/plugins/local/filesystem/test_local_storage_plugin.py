"""
Unit tests for the LocalStoragePlugin.

This module contains tests for the LocalStoragePlugin, which provides
access to files on the local filesystem.
"""

import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any

from science_data_kit.plugins.local.filesystem.local_storage_plugin import LocalStoragePlugin


class TestLocalStoragePlugin(unittest.TestCase):
    """Tests for the LocalStoragePlugin."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)
        
        # Create a test file
        self.test_file_path = self.root_dir / "test_file.txt"
        self.test_file_path.write_text("Test content")
        
        # Create a test directory
        self.test_dir_path = self.root_dir / "test_dir"
        self.test_dir_path.mkdir()
        
        # Create a test file in the test directory
        self.test_nested_file_path = self.test_dir_path / "nested_file.txt"
        self.test_nested_file_path.write_text("Nested content")
        
        # Create the plugin
        self.plugin = LocalStoragePlugin()
        
        # Create a valid configuration
        self.config = {
            "root_directory": str(self.root_dir),
            "create_if_missing": False,
            "read_only": False,
        }
    
    def tearDown(self):
        """Clean up the test environment."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test plugin initialization."""
        # Test initialization with valid configuration
        self.assertTrue(self.plugin.initialize(self.config))
        self.assertTrue(self.plugin.is_initialized)
        
        # Test initialization with invalid configuration
        invalid_config = {
            "root_directory": "/path/that/does/not/exist",
            "create_if_missing": False,
        }
        plugin = LocalStoragePlugin()
        self.assertFalse(plugin.initialize(invalid_config))
        self.assertFalse(plugin.is_initialized)
        
        # Test initialization with create_if_missing=True
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_dir = Path(temp_dir) / "missing_dir"
            config = {
                "root_directory": str(missing_dir),
                "create_if_missing": True,
            }
            plugin = LocalStoragePlugin()
            self.assertTrue(plugin.initialize(config))
            self.assertTrue(plugin.is_initialized)
            self.assertTrue(missing_dir.exists())
    
    def test_connection(self):
        """Test plugin connection."""
        # Initialize the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        
        # Test connection
        self.plugin.connect(self.config)
        self.assertTrue(self.plugin.is_connected)
        
        # Test disconnection
        self.plugin.disconnect()
        self.assertFalse(self.plugin.is_connected)
        
        # Test connection with uninitialized plugin
        plugin = LocalStoragePlugin()
        with self.assertRaises(RuntimeError):
            plugin.connect(self.config)
    
    def test_capabilities(self):
        """Test plugin capabilities."""
        # Initialize the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        
        # Test capabilities with read_only=False
        capabilities = self.plugin.capabilities
        self.assertIn("filesystem", capabilities)
        self.assertIn("browsable", capabilities)
        self.assertIn("writable", capabilities)
        self.assertIn("deletable", capabilities)
        self.assertIn("creatable", capabilities)
        
        # Test capabilities with read_only=True
        config = self.config.copy()
        config["read_only"] = True
        plugin = LocalStoragePlugin()
        self.assertTrue(plugin.initialize(config))
        capabilities = plugin.capabilities
        self.assertIn("filesystem", capabilities)
        self.assertIn("browsable", capabilities)
        self.assertNotIn("writable", capabilities)
        self.assertNotIn("deletable", capabilities)
        self.assertNotIn("creatable", capabilities)
    
    def test_list_directory(self):
        """Test listing directory contents."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test listing the root directory
        items = self.plugin.list_directory("")
        self.assertEqual(len(items), 2)  # test_file.txt and test_dir
        
        # Verify the items
        file_item = next(item for item in items if item["name"] == "test_file.txt")
        self.assertEqual(file_item["path"], "test_file.txt")
        self.assertFalse(file_item["is_dir"])
        self.assertEqual(file_item["size"], len("Test content"))
        
        dir_item = next(item for item in items if item["name"] == "test_dir")
        self.assertEqual(dir_item["path"], "test_dir")
        self.assertTrue(dir_item["is_dir"])
        self.assertIsNone(dir_item["size"])
        
        # Test listing a subdirectory
        items = self.plugin.list_directory("test_dir")
        self.assertEqual(len(items), 1)  # nested_file.txt
        
        # Verify the item
        file_item = items[0]
        self.assertEqual(file_item["name"], "nested_file.txt")
        self.assertEqual(file_item["path"], "test_dir/nested_file.txt")
        self.assertFalse(file_item["is_dir"])
        self.assertEqual(file_item["size"], len("Nested content"))
        
        # Test listing a non-existent directory
        with self.assertRaises(FileNotFoundError):
            self.plugin.list_directory("non_existent_dir")
    
    def test_read_file(self):
        """Test reading a file."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test reading a file
        content = self.plugin.read_file("test_file.txt")
        self.assertEqual(content, b"Test content")
        
        # Test reading a nested file
        content = self.plugin.read_file("test_dir/nested_file.txt")
        self.assertEqual(content, b"Nested content")
        
        # Test reading a non-existent file
        with self.assertRaises(FileNotFoundError):
            self.plugin.read_file("non_existent_file.txt")
        
        # Test reading a directory as a file
        with self.assertRaises(FileNotFoundError):
            self.plugin.read_file("test_dir")
    
    def test_write_file(self):
        """Test writing a file."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test writing a new file
        new_file_path = "new_file.txt"
        content = b"New content"
        self.assertTrue(self.plugin.write_file(new_file_path, content))
        
        # Verify the file was written
        full_path = self.root_dir / new_file_path
        self.assertTrue(full_path.exists())
        self.assertEqual(full_path.read_bytes(), content)
        
        # Test writing to an existing file
        updated_content = b"Updated content"
        self.assertTrue(self.plugin.write_file("test_file.txt", updated_content))
        
        # Verify the file was updated
        self.assertEqual(self.test_file_path.read_bytes(), updated_content)
        
        # Test writing to a new file in a new directory
        new_dir_file_path = "new_dir/new_file.txt"
        self.assertTrue(self.plugin.write_file(new_dir_file_path, content))
        
        # Verify the file was written
        full_path = self.root_dir / new_dir_file_path
        self.assertTrue(full_path.exists())
        self.assertEqual(full_path.read_bytes(), content)
        
        # Test writing to a file in read-only mode
        config = self.config.copy()
        config["read_only"] = True
        plugin = LocalStoragePlugin()
        self.assertTrue(plugin.initialize(config))
        plugin.connect(config)
        
        with self.assertRaises(PermissionError):
            plugin.write_file("readonly_file.txt", b"Content")
    
    def test_delete_file(self):
        """Test deleting a file."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test deleting a file
        self.assertTrue(self.plugin.delete_file("test_file.txt"))
        
        # Verify the file was deleted
        self.assertFalse(self.test_file_path.exists())
        
        # Test deleting a non-existent file
        self.assertFalse(self.plugin.delete_file("non_existent_file.txt"))
        
        # Test deleting a directory as a file
        self.assertFalse(self.plugin.delete_file("test_dir"))
        
        # Test deleting a file in read-only mode
        config = self.config.copy()
        config["read_only"] = True
        plugin = LocalStoragePlugin()
        self.assertTrue(plugin.initialize(config))
        plugin.connect(config)
        
        with self.assertRaises(PermissionError):
            plugin.delete_file("test_dir/nested_file.txt")
    
    def test_create_directory(self):
        """Test creating a directory."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test creating a new directory
        new_dir_path = "new_dir"
        self.assertTrue(self.plugin.create_directory(new_dir_path))
        
        # Verify the directory was created
        full_path = self.root_dir / new_dir_path
        self.assertTrue(full_path.exists())
        self.assertTrue(full_path.is_dir())
        
        # Test creating a nested directory
        nested_dir_path = "new_dir/nested_dir"
        self.assertTrue(self.plugin.create_directory(nested_dir_path))
        
        # Verify the directory was created
        full_path = self.root_dir / nested_dir_path
        self.assertTrue(full_path.exists())
        self.assertTrue(full_path.is_dir())
        
        # Test creating a directory in read-only mode
        config = self.config.copy()
        config["read_only"] = True
        plugin = LocalStoragePlugin()
        self.assertTrue(plugin.initialize(config))
        plugin.connect(config)
        
        with self.assertRaises(PermissionError):
            plugin.create_directory("readonly_dir")
    
    def test_delete_directory(self):
        """Test deleting a directory."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test deleting an empty directory
        empty_dir_path = "empty_dir"
        (self.root_dir / empty_dir_path).mkdir()
        self.assertTrue(self.plugin.delete_directory(empty_dir_path))
        
        # Verify the directory was deleted
        self.assertFalse((self.root_dir / empty_dir_path).exists())
        
        # Test deleting a non-empty directory without recursive=True
        self.assertFalse(self.plugin.delete_directory("test_dir"))
        
        # Verify the directory still exists
        self.assertTrue(self.test_dir_path.exists())
        
        # Test deleting a non-empty directory with recursive=True
        self.assertTrue(self.plugin.delete_directory("test_dir", recursive=True))
        
        # Verify the directory was deleted
        self.assertFalse(self.test_dir_path.exists())
        
        # Test deleting a non-existent directory
        self.assertFalse(self.plugin.delete_directory("non_existent_dir"))
        
        # Test deleting a file as a directory
        self.assertFalse(self.plugin.delete_directory("test_file.txt"))
        
        # Test deleting a directory in read-only mode
        config = self.config.copy()
        config["read_only"] = True
        plugin = LocalStoragePlugin()
        self.assertTrue(plugin.initialize(config))
        plugin.connect(config)
        
        # Create a test directory
        test_dir = self.root_dir / "readonly_test_dir"
        test_dir.mkdir()
        
        with self.assertRaises(PermissionError):
            plugin.delete_directory("readonly_test_dir")
    
    def test_file_exists(self):
        """Test checking if a file exists."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test checking if an existing file exists
        self.assertTrue(self.plugin.file_exists("test_file.txt"))
        
        # Test checking if a non-existent file exists
        self.assertFalse(self.plugin.file_exists("non_existent_file.txt"))
        
        # Test checking if a directory exists as a file
        self.assertFalse(self.plugin.file_exists("test_dir"))
    
    def test_directory_exists(self):
        """Test checking if a directory exists."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test checking if an existing directory exists
        self.assertTrue(self.plugin.directory_exists("test_dir"))
        
        # Test checking if a non-existent directory exists
        self.assertFalse(self.plugin.directory_exists("non_existent_dir"))
        
        # Test checking if a file exists as a directory
        self.assertFalse(self.plugin.directory_exists("test_file.txt"))
    
    def test_path_security(self):
        """Test path security checks."""
        # Initialize and connect the plugin
        self.assertTrue(self.plugin.initialize(self.config))
        self.plugin.connect(self.config)
        
        # Test accessing a path outside the root directory
        with self.assertRaises(ValueError):
            self.plugin.read_file("../outside.txt")
        
        # Test accessing a path with directory traversal
        with self.assertRaises(ValueError):
            self.plugin.read_file("test_dir/../../outside.txt")
        
        # Test allowed_paths
        # Create a directory outside the root directory
        with tempfile.TemporaryDirectory() as allowed_dir:
            # Create a test file in the allowed directory
            allowed_file_path = Path(allowed_dir) / "allowed_file.txt"
            allowed_file_path.write_text("Allowed content")
            
            # Create a plugin with allowed_paths
            config = self.config.copy()
            config["allowed_paths"] = [allowed_dir]
            plugin = LocalStoragePlugin()
            self.assertTrue(plugin.initialize(config))
            plugin.connect(config)
            
            # Test accessing a file in the allowed directory
            with self.assertRaises(PermissionError):
                # This should fail because we're using an absolute path
                plugin.read_file(str(allowed_file_path))


if __name__ == "__main__":
    unittest.main()