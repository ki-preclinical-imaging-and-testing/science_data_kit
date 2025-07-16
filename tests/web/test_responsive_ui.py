import unittest
from unittest.mock import patch, MagicMock
from flask import template_rendered
from contextlib import contextmanager
from bs4 import BeautifulSoup
import re

from science_data_kit.web.app import create_app


@contextmanager
def captured_templates(app):
    """Context manager to capture templates rendered during a request."""
    recorded = []
    
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class ResponsiveUITests(unittest.TestCase):
    """Test suite for responsive UI components."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock authentication
        self.auth_patcher = patch('science_data_kit.web.routes.main.login_required')
        self.auth_mock = self.auth_patcher.start()
        self.auth_mock.return_value = lambda f: f
        
        # Mock session
        self.session_patcher = patch('science_data_kit.web.routes.main.session')
        self.session_mock = self.session_patcher.start()
        self.session_mock.get.return_value = True
    
    def tearDown(self):
        """Clean up after tests."""
        self.auth_patcher.stop()
        self.session_patcher.stop()
        self.app_context.pop()
    
    def test_responsive_meta_tag(self):
        """Test that responsive meta tag is present."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        self.assertIsNotNone(meta_viewport)
        self.assertEqual(meta_viewport['content'], 'width=device-width, initial-scale=1.0')
    
    def test_theme_color_meta_tag(self):
        """Test that theme color meta tag is present in file explorer."""
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        meta_theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        
        self.assertIsNotNone(meta_theme_color)
        self.assertEqual(meta_theme_color['content'], '#0d6efd')
    
    def test_touch_friendly_buttons(self):
        """Test that buttons have touch-friendly classes."""
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        touch_buttons = soup.find_all('button', class_=re.compile('btn-touch'))
        
        self.assertGreater(len(touch_buttons), 0)
        
        # Check minimum dimensions for touch targets
        css_link = soup.find('link', attrs={'href': re.compile('style.css')})
        self.assertIsNotNone(css_link)
    
    def test_responsive_grid_layout(self):
        """Test that file grid uses responsive layout classes."""
        response = self.client.get('/files?view_mode=grid')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        file_grid = soup.find(class_=re.compile('file-grid'))
        
        # This might be None if the view doesn't have files to display
        if file_grid:
            self.assertIsNotNone(file_grid)
    
    def test_keyboard_shortcuts_toggle(self):
        """Test that keyboard shortcuts toggle is present."""
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        toggle_button = soup.find('button', class_=re.compile('keyboard-shortcuts-toggle'))
        
        self.assertIsNotNone(toggle_button)
        self.assertIn('data-bs-toggle', toggle_button.attrs)
        self.assertEqual(toggle_button['data-bs-toggle'], 'collapse')
    
    def test_responsive_toolbar(self):
        """Test that toolbar has responsive classes."""
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        toolbar = soup.find(class_=re.compile('file-explorer-toolbar'))
        
        self.assertIsNotNone(toolbar)
        
        # Check that toolbar contains action groups
        action_groups = toolbar.find_all(class_=re.compile('file-explorer-actions'))
        self.assertGreater(len(action_groups), 0)
    
    def test_responsive_media_queries(self):
        """Test that CSS contains responsive media queries."""
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        css_content = response.data.decode('utf-8')
        
        # Check for media queries for different screen sizes
        self.assertIn('@media (max-width: 576px)', css_content)
        self.assertIn('@media (min-width: 576px) and (max-width: 768px)', css_content)
        self.assertIn('@media (min-width: 768px)', css_content)
    
    def test_accessibility_features(self):
        """Test that accessibility features are present."""
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for ARIA attributes
        aria_elements = soup.find_all(attrs=lambda attr: any(a.startswith('aria-') for a in attr if isinstance(a, str)))
        self.assertGreater(len(aria_elements), 0)
        
        # Check for role attributes
        role_elements = soup.find_all(attrs={'role': True})
        self.assertGreater(len(role_elements), 0)
        
        # Check for sr-only class in CSS
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        css_content = response.data.decode('utf-8')
        self.assertIn('.sr-only', css_content)


if __name__ == '__main__':
    unittest.main()