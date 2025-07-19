#!/usr/bin/env python
"""
End-to-end test for connect page workflow.

This module contains tests that simulate real-world user interactions with the
connect page and verify that they work correctly.
"""

import os
import unittest
import json
from flask import Flask, session
from unittest.mock import patch, MagicMock
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from science_data_kit.web.routes import main_bp
from science_data_kit.core.pages.connect import ConnectPage


class ConnectWorkflowTest(unittest.TestCase):
    """Test case for connect page workflow."""

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

    def test_connect_page_loads(self):
        """Test that the connect page loads successfully."""
        with patch.object(ConnectPage, 'get_page_data', return_value=MagicMock()):
            response = self.client.get('/connect')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Connect', response.data)

    def test_get_available_connections(self):
        """Test getting available connections."""
        with patch.object(ConnectPage, 'get_available_connections', return_value={
            'success': True,
            'connections': [
                {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'available'},
                {'id': 'neo4j', 'name': 'Neo4j', 'type': 'graph', 'status': 'available'},
                {'id': 'dropbox', 'name': 'Dropbox', 'type': 'cloud', 'status': 'available'}
            ]
        }):
            response = self.client.get('/api/connect/available')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['connections']), 3)
            self.assertEqual(data['connections'][0]['id'], 'sqlite')
            self.assertEqual(data['connections'][1]['id'], 'neo4j')
            self.assertEqual(data['connections'][2]['id'], 'dropbox')

    def test_get_active_connections(self):
        """Test getting active connections."""
        with patch.object(ConnectPage, 'get_active_connections', return_value={
            'success': True,
            'connections': [
                {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'connected', 'details': {'path': ':memory:'}}
            ]
        }):
            response = self.client.get('/api/connect/active')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['connections']), 1)
            self.assertEqual(data['connections'][0]['id'], 'sqlite')
            self.assertEqual(data['connections'][0]['status'], 'connected')

    def test_connect_to_sqlite(self):
        """Test connecting to SQLite database."""
        with patch.object(ConnectPage, 'connect_to_database', return_value={
            'success': True,
            'message': 'Connected to SQLite database',
            'connection': {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'connected', 'details': {'path': ':memory:'}}
        }):
            response = self.client.post('/api/connect/database', json={
                'type': 'sqlite',
                'path': ':memory:'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connected to SQLite database')
            self.assertEqual(data['connection']['id'], 'sqlite')
            self.assertEqual(data['connection']['status'], 'connected')

    def test_connect_to_neo4j(self):
        """Test connecting to Neo4j database."""
        with patch.object(ConnectPage, 'connect_to_graph', return_value={
            'success': True,
            'message': 'Connected to Neo4j database',
            'connection': {'id': 'neo4j', 'name': 'Neo4j', 'type': 'graph', 'status': 'connected', 'details': {'uri': 'bolt://localhost:7687'}}
        }):
            response = self.client.post('/api/connect/graph', json={
                'type': 'neo4j',
                'uri': 'bolt://localhost:7687',
                'username': 'neo4j',
                'password': 'password'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connected to Neo4j database')
            self.assertEqual(data['connection']['id'], 'neo4j')
            self.assertEqual(data['connection']['status'], 'connected')

    def test_connect_to_dropbox(self):
        """Test connecting to Dropbox."""
        with patch.object(ConnectPage, 'connect_to_cloud', return_value={
            'success': True,
            'message': 'Connected to Dropbox',
            'connection': {'id': 'dropbox', 'name': 'Dropbox', 'type': 'cloud', 'status': 'connected', 'details': {'token': 'test_token'}}
        }):
            response = self.client.post('/api/connect/cloud', json={
                'type': 'dropbox',
                'token': 'test_token'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connected to Dropbox')
            self.assertEqual(data['connection']['id'], 'dropbox')
            self.assertEqual(data['connection']['status'], 'connected')

    def test_disconnect(self):
        """Test disconnecting from a data source."""
        with patch.object(ConnectPage, 'disconnect', return_value={
            'success': True,
            'message': 'Disconnected from SQLite database'
        }):
            response = self.client.post('/api/connect/disconnect', json={
                'id': 'sqlite'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Disconnected from SQLite database')

    def test_test_connection(self):
        """Test testing a connection."""
        with patch.object(ConnectPage, 'test_connection', return_value={
            'success': True,
            'message': 'Connection test successful',
            'details': {'status': 'connected', 'version': '3.0.0'}
        }):
            response = self.client.post('/api/connect/test', json={
                'id': 'sqlite'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connection test successful')
            self.assertEqual(data['details']['status'], 'connected')

    def test_complete_workflow(self):
        """Test a complete workflow of connection operations."""
        # Step 1: Get available connections
        with patch.object(ConnectPage, 'get_available_connections', return_value={
            'success': True,
            'connections': [
                {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'available'},
                {'id': 'neo4j', 'name': 'Neo4j', 'type': 'graph', 'status': 'available'}
            ]
        }):
            response = self.client.get('/api/connect/available')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # Step 2: Connect to SQLite
            with patch.object(ConnectPage, 'connect_to_database', return_value={
                'success': True,
                'message': 'Connected to SQLite database',
                'connection': {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'connected', 'details': {'path': ':memory:'}}
            }):
                response = self.client.post('/api/connect/database', json={
                    'type': 'sqlite',
                    'path': ':memory:'
                })
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                
                # Step 3: Get active connections
                with patch.object(ConnectPage, 'get_active_connections', return_value={
                    'success': True,
                    'connections': [
                        {'id': 'sqlite', 'name': 'SQLite', 'type': 'database', 'status': 'connected', 'details': {'path': ':memory:'}}
                    ]
                }):
                    response = self.client.get('/api/connect/active')
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertTrue(data['success'])
                    self.assertEqual(len(data['connections']), 1)
                    
                    # Step 4: Test the connection
                    with patch.object(ConnectPage, 'test_connection', return_value={
                        'success': True,
                        'message': 'Connection test successful',
                        'details': {'status': 'connected', 'version': '3.0.0'}
                    }):
                        response = self.client.post('/api/connect/test', json={
                            'id': 'sqlite'
                        })
                        self.assertEqual(response.status_code, 200)
                        data = json.loads(response.data)
                        self.assertTrue(data['success'])
                        
                        # Step 5: Disconnect
                        with patch.object(ConnectPage, 'disconnect', return_value={
                            'success': True,
                            'message': 'Disconnected from SQLite database'
                        }):
                            response = self.client.post('/api/connect/disconnect', json={
                                'id': 'sqlite'
                            })
                            self.assertEqual(response.status_code, 200)
                            data = json.loads(response.data)
                            self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()