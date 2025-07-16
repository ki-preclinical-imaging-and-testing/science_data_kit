"""
Tests for the core page classes.

This module contains tests for the framework-independent core page classes.
"""

import unittest
from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.models.page import PageData, DashboardPageData

class TestBasePage(unittest.TestCase):
    """Tests for the BasePage class."""
    
    def test_base_page_abstract(self):
        """Test that BasePage is an abstract class."""
        with self.assertRaises(TypeError):
            BasePage()
    
class TestDashboardPage(unittest.TestCase):
    """Tests for the DashboardPage class."""
    
    def test_dashboard_page_init(self):
        """Test that DashboardPage can be initialized."""
        page = DashboardPage()
        self.assertIsNotNone(page)
    
    def test_dashboard_page_get_page_data(self):
        """Test that DashboardPage.get_page_data returns a DashboardPageData instance."""
        page = DashboardPage()
        page_data = page.get_page_data()
        self.assertIsInstance(page_data, DashboardPageData)
        self.assertEqual(page_data.title, "Dashboard")
        self.assertTrue(page_data.requires_auth)
        self.assertIsNotNone(page_data.metrics)
        self.assertIsNotNone(page_data.charts)
        self.assertIsNotNone(page_data.tables)
        self.assertIsNotNone(page_data.status_items)
        self.assertIsNotNone(page_data.connected_services)
        self.assertIsNotNone(page_data.recent_activities)
        self.assertIsNotNone(page_data.feature_categories)
    
    def test_dashboard_page_connect_to_database(self):
        """Test that DashboardPage.connect_to_database returns a result dictionary."""
        page = DashboardPage()
        result = page.connect_to_database("uri", "username", "password", "database")
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("error", result)
    
    def test_dashboard_page_disconnect_from_database(self):
        """Test that DashboardPage.disconnect_from_database returns a result dictionary."""
        page = DashboardPage()
        result = page.disconnect_from_database()
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()