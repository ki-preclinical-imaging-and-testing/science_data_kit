"""
Test script for Flask API endpoints

This script tests the Flask API endpoints for the connect, dashboard, and explore pages.
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
from science_data_kit.core.pages.connect import ConnectPage
from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.explore import ExplorePage

class FlaskAPITest(unittest.TestCase):
    """Test case for Flask API endpoints."""

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

    def test_connect_api_endpoints(self):
        """Test the connect page API endpoints."""
        # Test available connections endpoint
        with patch.object(ConnectPage, '_get_available_connections', return_value=[{'id': 'test'}]):
            response = self.client.get('/api/connect/available')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, [{'id': 'test'}])
        
        # Test active connections endpoint
        with patch.object(ConnectPage, '_get_active_connections', return_value=[{'id': 'test_conn'}]):
            response = self.client.get('/api/connect/active')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, [{'id': 'test_conn'}])
        
        # Test connect endpoint
        with patch.object(ConnectPage, 'connect', return_value=True):
            response = self.client.post('/api/connect/connect', data={
                'connection_type': 'test_type',
                'name': 'Test Connection',
                'param1': 'value1'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
        
        # Test disconnect endpoint
        with patch.object(ConnectPage, 'disconnect', return_value=True):
            response = self.client.post('/api/connect/disconnect', data={
                'connection_id': 'test_conn_id'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
        
        # Test test connection endpoint
        with patch.object(ConnectPage, 'test_connection', return_value={'success': True, 'message': 'Connected'}):
            response = self.client.post('/api/connect/test', data={
                'connection_type': 'test_type',
                'param1': 'value1'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Connected')

    def test_dashboard_api_endpoints(self):
        """Test the dashboard page API endpoints."""
        # Mock DashboardPage.get_page_data
        mock_page_data = MagicMock()
        mock_page_data.metrics = [{'title': 'Test Metric'}]
        mock_page_data.charts = [{'title': 'Test Chart'}]
        mock_page_data.tables = [{'title': 'Test Table'}]
        mock_page_data.status_items = [{'name': 'Test Status'}]
        mock_page_data.connected_services = {'test_service': True}
        mock_page_data.recent_activities = [{'Activity': 'Test Activity'}]
        mock_page_data.feature_categories = {'test_category': [{'Feature': 'Test Feature'}]}
        
        # Test dashboard data endpoint
        with patch.object(DashboardPage, 'get_page_data', return_value=mock_page_data):
            response = self.client.get('/api/dashboard/data')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['metrics'], [{'title': 'Test Metric'}])
            self.assertEqual(data['charts'], [{'title': 'Test Chart'}])
            self.assertEqual(data['tables'], [{'title': 'Test Table'}])
            self.assertEqual(data['status_items'], [{'name': 'Test Status'}])
            self.assertEqual(data['connected_services'], {'test_service': True})
            self.assertEqual(data['recent_activities'], [{'Activity': 'Test Activity'}])
            self.assertEqual(data['feature_categories'], {'test_category': [{'Feature': 'Test Feature'}]})
        
        # Test connect to database endpoint
        with patch.object(DashboardPage, 'connect_to_database', return_value={'success': True}):
            response = self.client.post('/api/dashboard/connect-database', data={
                'uri': 'test_uri',
                'username': 'test_user',
                'password': 'test_pass',
                'database': 'test_db',
                'conn_name': 'Test Connection'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
        
        # Test disconnect from database endpoint
        with patch.object(DashboardPage, 'disconnect_from_database', return_value={'success': True}):
            response = self.client.post('/api/dashboard/disconnect-database')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])

    def test_explore_api_endpoints(self):
        """Test the explore page API endpoints."""
        # Test data sources endpoint
        with patch.object(ExplorePage, '_get_available_data_sources', return_value=[{'id': 'test_source'}]):
            response = self.client.get('/api/explore/data-sources')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, [{'id': 'test_source'}])
        
        # Test set data source endpoint
        mock_explore_page = MagicMock()
        mock_explore_page.set_data_source.return_value = True
        mock_explore_page.schema_info = {'test': 'schema'}
        
        with patch('science_data_kit.web.routes.ExplorePage', return_value=mock_explore_page):
            response = self.client.post('/api/explore/set-data-source', data={
                'data_source_id': 'test_source'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['schema_info'], {'test': 'schema'})
        
        # Test execute query endpoint
        mock_explore_page = MagicMock()
        mock_explore_page.set_data_source.return_value = True
        mock_explore_page.execute_query.return_value = True
        mock_explore_page.query_results = {'columns': ['col1'], 'data': [['val1']]}
        mock_explore_page.visualizations = [{'id': 'test_viz'}]
        
        with patch('science_data_kit.web.routes.ExplorePage', return_value=mock_explore_page):
            response = self.client.post('/api/explore/execute-query', data={
                'query': 'SELECT * FROM test',
                'data_source_id': 'test_source'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['query_results'], {'columns': ['col1'], 'data': [['val1']]})
            self.assertEqual(data['visualizations'], [{'id': 'test_viz'}])
        
        # Test schema info endpoint
        with patch.object(ExplorePage, '_get_schema_info', return_value={'test': 'schema'}):
            response = self.client.get('/api/explore/schema-info?data_source_id=test_source')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['schema_info'], {'test': 'schema'})

if __name__ == '__main__':
    unittest.main()