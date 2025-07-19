"""
Test script for Analytics Dashboard API endpoints

This script tests the Flask API endpoints for the analytics dashboard page.
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
from science_data_kit.core.pages.analytics_dashboard import AnalyticsDashboardPage
from science_data_kit.core.models.page import AnalyticsDashboardPageData

class AnalyticsAPITest(unittest.TestCase):
    """Test case for Analytics Dashboard API endpoints."""

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
            sess['analytics_session_id'] = 'test_session_id'
            sess['analytics_session_start'] = 1625000000.0
            sess['analytics_enabled'] = True

    def tearDown(self):
        """Tear down the test environment."""
        self.ctx.pop()

    def test_analytics_dashboard_page(self):
        """Test the analytics dashboard page."""
        with patch('science_data_kit.web.routes.render_page_html', return_value='analytics_dashboard.html'):
            response = self.client.get('/analytics')
            self.assertEqual(response.status_code, 200)

    def test_analytics_data_endpoint(self):
        """Test the analytics data endpoint."""
        # Mock AnalyticsDashboardPage.get_page_data
        mock_page_data = MagicMock(spec=AnalyticsDashboardPageData)
        mock_page_data.page_views = [{'page_name': 'Test Page'}]
        mock_page_data.page_views_summary = [{'page_name': 'Test Page', 'view_count': 1}]
        mock_page_data.interactions = [{'interaction_type': 'Test Interaction'}]
        mock_page_data.interactions_summary = [{'interaction_type': 'Test Interaction', 'interaction_count': 1}]
        mock_page_data.session_id = 'test_session_id'
        mock_page_data.session_start = 1625000000.0
        mock_page_data.session_duration = 3600.0
        mock_page_data.analytics_enabled = True
        mock_page_data.analytics_storage_path = '/test/path'
        
        with patch.object(AnalyticsDashboardPage, 'get_page_data', return_value=mock_page_data):
            response = self.client.get('/api/analytics/data')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['page_views'], [{'page_name': 'Test Page'}])
            self.assertEqual(data['page_views_summary'], [{'page_name': 'Test Page', 'view_count': 1}])
            self.assertEqual(data['interactions'], [{'interaction_type': 'Test Interaction'}])
            self.assertEqual(data['interactions_summary'], [{'interaction_type': 'Test Interaction', 'interaction_count': 1}])
            self.assertEqual(data['session_id'], 'test_session_id')
            self.assertEqual(data['session_start'], 1625000000.0)
            self.assertEqual(data['session_duration'], 3600.0)
            self.assertTrue(data['analytics_enabled'])
            self.assertEqual(data['analytics_storage_path'], '/test/path')

    def test_toggle_analytics_endpoint(self):
        """Test the toggle analytics endpoint."""
        with patch.object(AnalyticsDashboardPage, 'toggle_analytics', return_value={'success': True, 'message': 'Analytics tracking enabled.'}):
            response = self.client.post('/api/analytics/toggle', json={'enabled': True})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Analytics tracking enabled.')
            
            # Check that the session was updated
            self.assertTrue(session['analytics_enabled'])

    def test_update_storage_path_endpoint(self):
        """Test the update storage path endpoint."""
        with patch.object(AnalyticsDashboardPage, 'update_storage_path', return_value={'success': True, 'message': 'Analytics storage path updated.'}):
            response = self.client.post('/api/analytics/storage-path', json={'path': '/new/path'})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Analytics storage path updated.')
            
            # Check that the session was updated
            self.assertEqual(session['analytics_storage_path'], '/new/path')

    def test_export_analytics_data_endpoint(self):
        """Test the export analytics data endpoint."""
        with patch.object(AnalyticsDashboardPage, 'export_analytics_data', return_value={'success': True, 'message': 'Analytics data exported.', 'page_views_path': '/test/page_views.csv', 'interactions_path': '/test/interactions.csv'}):
            response = self.client.post('/api/analytics/export', json={'format': 'csv'})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Analytics data exported.')
            self.assertEqual(data['page_views_path'], '/test/page_views.csv')
            self.assertEqual(data['interactions_path'], '/test/interactions.csv')

    def test_clear_analytics_data_endpoint(self):
        """Test the clear analytics data endpoint."""
        with patch.object(AnalyticsDashboardPage, 'clear_analytics_data', return_value={'success': True, 'message': 'Analytics data cleared.'}):
            response = self.client.post('/api/analytics/clear')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Analytics data cleared.')

    def test_track_page_view_endpoint(self):
        """Test the track page view endpoint."""
        with patch.object(AnalyticsDashboardPage, 'track_page_view', return_value={'success': True, 'message': 'Page view tracked successfully.'}):
            response = self.client.post('/api/analytics/track-page-view', json={'page_name': 'Test Page', 'page_path': '/test/page'})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Page view tracked successfully.')

    def test_track_interaction_endpoint(self):
        """Test the track interaction endpoint."""
        with patch.object(AnalyticsDashboardPage, 'track_interaction', return_value={'success': True, 'message': 'Interaction tracked successfully.'}):
            response = self.client.post('/api/analytics/track-interaction', json={
                'interaction_type': 'click',
                'component_id': 'test_button',
                'component_type': 'button',
                'page_name': 'Test Page',
                'details': {'extra': 'info'}
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Interaction tracked successfully.')

    def test_track_page_view_endpoint_missing_page_name(self):
        """Test the track page view endpoint with missing page name."""
        response = self.client.post('/api/analytics/track-page-view', json={'page_path': '/test/page'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Page name is required')

    def test_track_interaction_endpoint_missing_parameters(self):
        """Test the track interaction endpoint with missing parameters."""
        response = self.client.post('/api/analytics/track-interaction', json={
            'interaction_type': 'click',
            'component_id': 'test_button',
            # Missing component_type and page_name
            'details': {'extra': 'info'}
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Interaction type, component ID, component type, and page name are required')

if __name__ == '__main__':
    unittest.main()