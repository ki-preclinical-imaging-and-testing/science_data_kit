"""
Test script for Dropbox Integration API endpoints

This script tests the Flask API endpoints for the Dropbox connection and browser pages.
It verifies that the endpoints return the expected responses.
"""

import unittest
import json
import os
import sys
from flask import Flask, session
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from science_data_kit.web.routes import main_bp
from science_data_kit.core.pages.dropbox_connect import DropboxConnectPage
from science_data_kit.core.pages.dropbox_browser import DropboxBrowserPage

class DropboxAPITest(unittest.TestCase):
    """Test case for Dropbox Integration API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.register_blueprint(main_bp)
        
        # Create a test client
        self.client = self.app.test_client()
        
        # Create a test context
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        # Set up session for login_required decorator
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'test_user'

    def tearDown(self):
        """Tear down the test environment."""
        self.ctx.pop()

    def test_dropbox_connect_page(self):
        """Test the Dropbox connection page endpoint."""
        response = self.client.get('/dropbox-connect')
        self.assertEqual(response.status_code, 200)

    def test_dropbox_browser_page(self):
        """Test the Dropbox browser page endpoint."""
        # Mock the session to include dropbox_connected
        with self.client.session_transaction() as sess:
            sess['dropbox_connected'] = True
        
        response = self.client.get('/dropbox')
        self.assertEqual(response.status_code, 200)

    def test_connect_to_dropbox_endpoint(self):
        """Test the connect to Dropbox API endpoint."""
        mock_result = {
            "success": True
        }
        
        with patch.object(DropboxConnectPage, 'connect', return_value=mock_result):
            response = self.client.post('/api/dropbox/connect', data={
                'app_key': 'test_key',
                'app_secret': 'test_secret',
                'refresh_token': 'test_token',
                'save_config': 'true',
                'config_file': 'test_config.json'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])

    def test_connect_to_dropbox_oauth_endpoint(self):
        """Test the connect to Dropbox API endpoint with OAuth flow."""
        mock_result = {
            "success": False,
            "auth_url": "https://www.dropbox.com/oauth2/authorize?test=1"
        }
        
        with patch.object(DropboxConnectPage, 'connect', return_value=mock_result):
            response = self.client.post('/api/dropbox/connect', data={
                'app_key': 'test_key',
                'app_secret': 'test_secret'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['auth_url'], "https://www.dropbox.com/oauth2/authorize?test=1")

    def test_complete_dropbox_auth_endpoint(self):
        """Test the complete Dropbox OAuth authentication API endpoint."""
        mock_result = {
            "success": True
        }
        
        with patch.object(DropboxConnectPage, 'complete_authentication', return_value=mock_result):
            response = self.client.post('/api/dropbox/complete-auth', data={
                'auth_code': 'test_auth_code'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])

    def test_disconnect_from_dropbox_endpoint(self):
        """Test the disconnect from Dropbox API endpoint."""
        mock_result = {
            "success": True
        }
        
        with patch.object(DropboxConnectPage, 'disconnect', return_value=mock_result):
            response = self.client.post('/api/dropbox/disconnect')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])

    def test_get_dropbox_status_endpoint(self):
        """Test the get Dropbox status API endpoint."""
        # Mock the DropboxConnectPage instance
        mock_page = MagicMock()
        mock_page.connection_status = {"dropbox": True}
        mock_page.account_info = {"name": "Test User", "email": "test@example.com"}
        mock_page.connection_errors = {}
        
        with patch('science_data_kit.web.routes.DropboxConnectPage', return_value=mock_page):
            response = self.client.get('/api/dropbox/status')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['connected'])
            self.assertEqual(data['account_info'], {"name": "Test User", "email": "test@example.com"})
            self.assertEqual(data['errors'], {})

    def test_load_dropbox_config_endpoint(self):
        """Test the load Dropbox config API endpoint."""
        mock_result = {
            "success": True,
            "config": {
                "app_key": "test_key",
                "app_secret": "test_secret",
                "refresh_token": "test_token"
            }
        }
        
        with patch.object(DropboxConnectPage, 'load_config', return_value=mock_result):
            response = self.client.post('/api/dropbox/load-config', data={
                'config_file': 'test_config.json'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['config'], {
                "app_key": "test_key",
                "app_secret": "test_secret",
                "refresh_token": "test_token"
            })

    def test_save_dropbox_config_endpoint(self):
        """Test the save Dropbox config API endpoint."""
        mock_result = {
            "success": True,
            "message": "Configuration saved successfully"
        }
        
        with patch.object(DropboxConnectPage, 'save_config', return_value=mock_result):
            response = self.client.post('/api/dropbox/save-config', data={
                'config_file': 'test_config.json'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], "Configuration saved successfully")

    def test_get_dropbox_files_endpoint(self):
        """Test the get Dropbox files API endpoint."""
        mock_page = MagicMock()
        mock_page.current_path = "/test_folder"
        mock_page.files = [
            {"name": "test_file.txt", "path": "/test_folder/test_file.txt", "size": 1024, "modified": "2023-01-01T12:00:00Z"}
        ]
        mock_page.directories = [
            {"name": "test_subfolder", "path": "/test_folder/test_subfolder"}
        ]
        
        with patch('science_data_kit.web.routes.DropboxBrowserPage', return_value=mock_page):
            with patch.object(DropboxBrowserPage, 'navigate_to', return_value=True):
                response = self.client.get('/api/dropbox/files?path=/test_folder')
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['current_path'], "/test_folder")
                self.assertEqual(len(data['files']), 1)
                self.assertEqual(len(data['directories']), 1)

    def test_get_dropbox_file_details_endpoint(self):
        """Test the get Dropbox file details API endpoint."""
        mock_file = {
            "name": "test_file.txt",
            "path": "/test_folder/test_file.txt",
            "size": 1024,
            "modified": "2023-01-01T12:00:00Z",
            "id": "id:test123"
        }
        
        with patch.object(DropboxBrowserPage, 'select_file', return_value=True):
            mock_page = MagicMock()
            mock_page.selected_file = mock_file
            
            with patch('science_data_kit.web.routes.DropboxBrowserPage', return_value=mock_page):
                response = self.client.get('/api/dropbox/file?path=/test_folder/test_file.txt')
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertEqual(data['file'], mock_file)

    def test_download_dropbox_file_endpoint(self):
        """Test the download Dropbox file API endpoint."""
        mock_result = {
            "success": True,
            "content": b"Test file content",
            "metadata": {
                "name": "test_file.txt",
                "path": "/test_folder/test_file.txt",
                "size": 17,
                "modified": "2023-01-01T12:00:00Z"
            }
        }
        
        with patch.object(DropboxBrowserPage, 'download_file', return_value=mock_result):
            response = self.client.get('/api/dropbox/download?path=/test_folder/test_file.txt')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b"Test file content")
            self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename=test_file.txt')

    def test_search_dropbox_files_endpoint(self):
        """Test the search Dropbox files API endpoint."""
        mock_results = [
            {"name": "test_file.txt", "path": "/test_folder/test_file.txt", "type": "file", "size": 1024, "modified": "2023-01-01T12:00:00Z"},
            {"name": "test_subfolder", "path": "/test_folder/test_subfolder", "type": "folder", "modified": "2023-01-01T12:00:00Z"}
        ]
        
        with patch.object(DropboxBrowserPage, 'search', return_value=True):
            mock_page = MagicMock()
            mock_page.search_results = mock_results
            
            with patch('science_data_kit.web.routes.DropboxBrowserPage', return_value=mock_page):
                response = self.client.get('/api/dropbox/search?query=test&path=/test_folder&extensions=txt')
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertEqual(data['results'], mock_results)

if __name__ == '__main__':
    unittest.main()