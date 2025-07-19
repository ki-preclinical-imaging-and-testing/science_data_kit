#!/usr/bin/env python
"""
End-to-end test for file explorer workflow.

This module contains tests that simulate real-world user interactions with the
file explorer page and verify that they work correctly.
"""

import os
import tempfile
import unittest
import json
from flask import Flask, session
from unittest.mock import patch, MagicMock
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from science_data_kit.web.routes import main_bp
from science_data_kit.core.pages.file_explorer import FileExplorerPage


class FileExplorerWorkflowTest(unittest.TestCase):
    """Test case for file explorer workflow."""

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
        
        # Create a temporary directory for file operations
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create some test files and directories
        os.makedirs(os.path.join(self.temp_dir.name, 'test_dir'))
        with open(os.path.join(self.temp_dir.name, 'test_file.txt'), 'w') as f:
            f.write('This is a test file.')

    def tearDown(self):
        """Tear down the test environment."""
        self.ctx.pop()
        self.temp_dir.cleanup()

    def test_file_explorer_page_loads(self):
        """Test that the file explorer page loads successfully."""
        with patch.object(FileExplorerPage, 'get_page_data', return_value=MagicMock()):
            response = self.client.get('/file-explorer')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'File Explorer', response.data)

    def test_navigate_directory(self):
        """Test navigating through directories."""
        with patch.object(FileExplorerPage, 'get_directory_contents', return_value={
            'success': True,
            'path': self.temp_dir.name,
            'files': [
                {'name': 'test_file.txt', 'type': 'file', 'size': 19, 'modified': '2023-01-01 00:00:00'},
                {'name': 'test_dir', 'type': 'directory', 'size': 0, 'modified': '2023-01-01 00:00:00'}
            ]
        }):
            response = self.client.get(f'/api/file-explorer/list?path={self.temp_dir.name}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['path'], self.temp_dir.name)
            self.assertEqual(len(data['files']), 2)
            self.assertEqual(data['files'][0]['name'], 'test_file.txt')
            self.assertEqual(data['files'][1]['name'], 'test_dir')

    def test_create_directory(self):
        """Test creating a new directory."""
        with patch.object(FileExplorerPage, 'create_directory', return_value={
            'success': True,
            'message': 'Directory created successfully'
        }):
            response = self.client.post('/api/file-explorer/create-directory', json={
                'path': self.temp_dir.name,
                'name': 'new_dir'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Directory created successfully')

    def test_upload_file(self):
        """Test uploading a file."""
        with patch.object(FileExplorerPage, 'upload_file', return_value={
            'success': True,
            'message': 'File uploaded successfully'
        }):
            response = self.client.post('/api/file-explorer/upload', data={
                'path': self.temp_dir.name,
                'file': (open(os.path.join(self.temp_dir.name, 'test_file.txt'), 'rb'), 'new_file.txt')
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'File uploaded successfully')

    def test_delete_file(self):
        """Test deleting a file."""
        with patch.object(FileExplorerPage, 'delete_file', return_value={
            'success': True,
            'message': 'File deleted successfully'
        }):
            response = self.client.post('/api/file-explorer/delete', json={
                'path': os.path.join(self.temp_dir.name, 'test_file.txt')
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'File deleted successfully')

    def test_rename_file(self):
        """Test renaming a file."""
        with patch.object(FileExplorerPage, 'rename_file', return_value={
            'success': True,
            'message': 'File renamed successfully'
        }):
            response = self.client.post('/api/file-explorer/rename', json={
                'path': os.path.join(self.temp_dir.name, 'test_file.txt'),
                'new_name': 'renamed_file.txt'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'File renamed successfully')

    def test_preview_file(self):
        """Test previewing a file."""
        with patch.object(FileExplorerPage, 'preview_file', return_value={
            'success': True,
            'content': 'This is a test file.',
            'file_type': 'text'
        }):
            response = self.client.get(f'/api/file-explorer/preview?path={os.path.join(self.temp_dir.name, "test_file.txt")}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['content'], 'This is a test file.')
            self.assertEqual(data['file_type'], 'text')

    def test_download_file(self):
        """Test downloading a file."""
        with patch.object(FileExplorerPage, 'get_file_for_download', return_value=os.path.join(self.temp_dir.name, 'test_file.txt')):
            response = self.client.get(f'/api/file-explorer/download?path={os.path.join(self.temp_dir.name, "test_file.txt")}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename=test_file.txt')

    def test_complete_workflow(self):
        """Test a complete workflow of file operations."""
        # Step 1: Navigate to the root directory
        with patch.object(FileExplorerPage, 'get_directory_contents', return_value={
            'success': True,
            'path': self.temp_dir.name,
            'files': [
                {'name': 'test_file.txt', 'type': 'file', 'size': 19, 'modified': '2023-01-01 00:00:00'},
                {'name': 'test_dir', 'type': 'directory', 'size': 0, 'modified': '2023-01-01 00:00:00'}
            ]
        }):
            response = self.client.get(f'/api/file-explorer/list?path={self.temp_dir.name}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # Step 2: Create a new directory
            with patch.object(FileExplorerPage, 'create_directory', return_value={
                'success': True,
                'message': 'Directory created successfully'
            }):
                response = self.client.post('/api/file-explorer/create-directory', json={
                    'path': self.temp_dir.name,
                    'name': 'new_dir'
                })
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                
                # Step 3: Upload a file to the new directory
                with patch.object(FileExplorerPage, 'upload_file', return_value={
                    'success': True,
                    'message': 'File uploaded successfully'
                }):
                    response = self.client.post('/api/file-explorer/upload', data={
                        'path': os.path.join(self.temp_dir.name, 'new_dir'),
                        'file': (open(os.path.join(self.temp_dir.name, 'test_file.txt'), 'rb'), 'new_file.txt')
                    })
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertTrue(data['success'])
                    
                    # Step 4: Navigate to the new directory
                    with patch.object(FileExplorerPage, 'get_directory_contents', return_value={
                        'success': True,
                        'path': os.path.join(self.temp_dir.name, 'new_dir'),
                        'files': [
                            {'name': 'new_file.txt', 'type': 'file', 'size': 19, 'modified': '2023-01-01 00:00:00'}
                        ]
                    }):
                        response = self.client.get(f'/api/file-explorer/list?path={os.path.join(self.temp_dir.name, "new_dir")}')
                        self.assertEqual(response.status_code, 200)
                        data = json.loads(response.data)
                        self.assertTrue(data['success'])
                        self.assertEqual(len(data['files']), 1)
                        self.assertEqual(data['files'][0]['name'], 'new_file.txt')


if __name__ == '__main__':
    unittest.main()