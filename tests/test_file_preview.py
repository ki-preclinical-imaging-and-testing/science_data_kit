"""
Test script for file preview capabilities in the Science Data Kit.

This script tests the enhanced file preview capabilities for cloud storage files.
"""

import os
import sys
import asyncio
import tempfile
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from science_data_kit.core.pages.file_browser import FileBrowserPage

def test_generate_preview_local():
    """Test generating a preview for a local file."""
    # Create a mock file interpreter
    mock_interpreter = MagicMock()
    mock_interpreter.generate_preview.return_value = "preview_data"

    # Patch the get_file_interpreter_for_file function to return our mock
    with patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file', return_value=mock_interpreter):
        # Create a file browser page
        page = FileBrowserPage(connection_type='local_fs')

        # Generate a preview for a local file
        preview = page.generate_preview('/path/to/local/file.txt')

        # Check that the preview was generated correctly
        assert preview == "preview_data"
        mock_interpreter.generate_preview.assert_called_once()

def test_generate_preview_cloud_small():
    """Test generating a preview for a small cloud storage file."""
    # Create a mock file interpreter
    mock_interpreter = MagicMock()
    mock_interpreter.generate_preview.return_value = "preview_data"

    # Create a mock storage provider
    mock_provider = MagicMock()
    mock_provider.get_file_info.return_value = {'size': 1024 * 1024}  # 1 MB
    mock_provider.download_file.return_value = True

    # Patch the necessary functions
    with patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file', return_value=mock_interpreter), \
         patch.object(FileBrowserPage, '_get_storage_provider', return_value=mock_provider):

        # Create a file browser page
        page = FileBrowserPage(connection_type='dropbox')

        # Generate a preview for a cloud storage file
        preview = page.generate_preview('/path/to/cloud/file.txt')

        # Check that the preview was generated correctly
        assert preview == "preview_data"
        mock_provider.get_file_info.assert_called_once()
        mock_provider.download_file.assert_called_once()
        mock_interpreter.generate_preview.assert_called_once()

def test_generate_preview_cloud_large():
    """Test generating a preview for a large cloud storage file."""
    # Create a mock file interpreter with streaming preview support
    mock_interpreter = MagicMock()
    mock_interpreter.generate_streaming_preview = asyncio.coroutine(lambda stream, path: "streaming_preview_data")

    # Create a mock storage provider
    mock_provider = MagicMock()
    mock_provider.get_file_info.return_value = {'size': 100 * 1024 * 1024}  # 100 MB
    mock_provider.download_file_stream = asyncio.coroutine(lambda path: "download_stream")

    # Patch the necessary functions
    with patch('science_data_kit.core.pages.file_browser.get_file_interpreter_for_file', return_value=mock_interpreter), \
         patch.object(FileBrowserPage, '_get_storage_provider', return_value=mock_provider):

        # Create a file browser page
        page = FileBrowserPage(connection_type='dropbox')

        # Generate a preview for a large cloud storage file
        preview = page.generate_preview('/path/to/cloud/large_file.txt')

        # Check that the streaming preview was generated correctly
        assert preview == "streaming_preview_data"
        mock_provider.get_file_info.assert_called_once()
        # Note: We can't easily assert on the coroutine calls in this test

def run_tests():
    """Run all tests."""
    print("Running tests for file preview capabilities...")

    # Run the tests
    test_generate_preview_local()
    print("✓ test_generate_preview_local passed")

    test_generate_preview_cloud_small()
    print("✓ test_generate_preview_cloud_small passed")

    test_generate_preview_cloud_large()
    print("✓ test_generate_preview_cloud_large passed")

    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
