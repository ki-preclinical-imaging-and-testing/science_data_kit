"""
Tests for the Google Drive plugin.

This module contains tests for the Google Drive plugin implementation.
"""

import unittest
from unittest.mock import MagicMock, patch
import io
import os
from typing import Dict, Any

from science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin import GoogleDrivePlugin


class TestGoogleDrivePlugin(unittest.TestCase):
    """Test cases for the Google Drive plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = GoogleDrivePlugin()
        
        # Mock configuration
        self.config = {
            "token_dict": {
                "token": "mock_token",
                "refresh_token": "mock_refresh_token",
                "client_id": "mock_client_id",
                "client_secret": "mock_client_secret",
                "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
            },
            "root_folder_id": "root"
        }
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_initialize(self, mock_build, mock_credentials):
        """Test plugin initialization."""
        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Test initialization
        result = self.plugin.initialize(self.config)
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized)
        mock_credentials.from_authorized_user_info.assert_called_once()
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_connect(self, mock_build, mock_credentials):
        """Test plugin connection."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Assertions
        self.assertTrue(self.plugin.is_connected)
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_creds)
        mock_files.list.assert_called_once()
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_list_directory(self, mock_build, mock_credentials):
        """Test listing directory contents."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock service response
        mock_files_result = {
            "files": [
                {
                    "id": "folder1",
                    "name": "Folder 1",
                    "mimeType": "application/vnd.google-apps.folder",
                    "modifiedTime": "2023-01-01T00:00:00Z"
                },
                {
                    "id": "file1",
                    "name": "File 1.txt",
                    "mimeType": "text/plain",
                    "size": "1024",
                    "modifiedTime": "2023-01-02T00:00:00Z"
                }
            ]
        }
        
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = mock_files_result
        mock_files.list.return_value = mock_list
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test list_directory
        result = self.plugin.list_directory("root")
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Folder 1")
        self.assertEqual(result[0]["path"], "folder1")
        self.assertTrue(result[0]["is_dir"])
        self.assertEqual(result[1]["name"], "File 1.txt")
        self.assertEqual(result[1]["path"], "file1")
        self.assertFalse(result[1]["is_dir"])
        self.assertEqual(result[1]["size"], "1024")
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.MediaIoBaseDownload')
    def test_read_file(self, mock_download, mock_build, mock_credentials):
        """Test reading a file."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock file metadata
        mock_file_metadata = {
            "name": "File 1.txt",
            "mimeType": "text/plain"
        }
        
        # Mock service
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_file_metadata
        mock_get_media = MagicMock()
        mock_files.get.return_value = mock_get
        mock_files.get_media.return_value = mock_get_media
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service
        
        # Mock download
        mock_downloader = MagicMock()
        mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]
        mock_download.return_value = mock_downloader
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test read_file
        with patch('io.BytesIO') as mock_bytesio:
            mock_buffer = MagicMock()
            mock_buffer.read.return_value = b"file content"
            mock_bytesio.return_value = mock_buffer
            
            result = self.plugin.read_file("file1")
            
            # Assertions
            self.assertEqual(result, b"file content")
            mock_files.get.assert_called_once_with(fileId="file1", fields="name,mimeType")
            mock_files.get_media.assert_called_once_with(fileId="file1")
            mock_download.assert_called_once()
            mock_downloader.next_chunk.assert_called()
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_file_exists(self, mock_build, mock_credentials):
        """Test checking if a file exists."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock file metadata
        mock_file_metadata = {
            "mimeType": "text/plain"
        }
        
        # Mock service
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_file_metadata
        mock_files.get.return_value = mock_get
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test file_exists
        result = self.plugin.file_exists("file1")
        
        # Assertions
        self.assertTrue(result)
        mock_files.get.assert_called_once_with(fileId="file1", fields="mimeType")
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_directory_exists(self, mock_build, mock_credentials):
        """Test checking if a directory exists."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        # Mock folder metadata
        mock_folder_metadata = {
            "mimeType": "application/vnd.google-apps.folder"
        }
        
        # Mock service
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_get = MagicMock()
        mock_get.execute.return_value = mock_folder_metadata
        mock_files.get.return_value = mock_get
        mock_service.files.return_value = mock_files
        mock_build.return_value = mock_service
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test directory_exists
        result = self.plugin.directory_exists("folder1")
        
        # Assertions
        self.assertTrue(result)
        mock_files.get.assert_called_once_with(fileId="folder1", fields="mimeType")
    
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.Credentials')
    @patch('science_data_kit.plugins.cloud_storage.google_drive.google_drive_plugin.build')
    def test_write_file_permission_error(self, mock_build, mock_credentials):
        """Test that write_file raises PermissionError."""
        # Mock credentials and service
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_info.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Initialize and connect
        self.plugin.initialize(self.config)
        self.plugin.connect(self.config)
        
        # Test write_file raises PermissionError
        with self.assertRaises(PermissionError):
            self.plugin.write_file("file1", b"content")
    
    def test_capabilities(self):
        """Test plugin capabilities."""
        capabilities = self.plugin.capabilities
        self.assertIn("filesystem", capabilities)
        self.assertIn("browsable", capabilities)
        self.assertIn("readable", capabilities)
        self.assertNotIn("writable", capabilities)
        self.assertNotIn("deletable", capabilities)
        self.assertNotIn("creatable", capabilities)


if __name__ == '__main__':
    unittest.main()