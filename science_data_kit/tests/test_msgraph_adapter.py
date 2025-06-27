"""
Integration tests for Microsoft Graph API Adapter

This module contains integration tests for the Microsoft Graph API adapter.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from typing import Dict, Any

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter


class TestMSGraphAdapter(unittest.TestCase):
    """
    Test cases for the Microsoft Graph API adapter.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        # Create a mock connection manager
        self.mock_connection_manager = MagicMock(spec=MSGraphConnectionManager)
        self.mock_connection_manager.connected = True
        
        # Create a mock response for get_me
        self.mock_connection_manager.get_me.return_value = {
            "id": "test-user-id",
            "displayName": "Test User",
            "mail": "test.user@example.com",
            "userPrincipalName": "test.user@example.com"
        }
        
        # Create a mock response for get_users
        self.mock_connection_manager.get_users.return_value = pd.DataFrame([
            {
                "id": "user-1",
                "displayName": "User 1",
                "mail": "user1@example.com",
                "userPrincipalName": "user1@example.com"
            },
            {
                "id": "user-2",
                "displayName": "User 2",
                "mail": "user2@example.com",
                "userPrincipalName": "user2@example.com"
            }
        ])
        
        # Create a mock response for get_groups
        self.mock_connection_manager.get_groups.return_value = pd.DataFrame([
            {
                "id": "group-1",
                "displayName": "Group 1",
                "description": "Test Group 1",
                "mail": "group1@example.com"
            },
            {
                "id": "group-2",
                "displayName": "Group 2",
                "description": "Test Group 2",
                "mail": "group2@example.com"
            }
        ])
        
        # Create a mock response for execute_query
        self.mock_connection_manager.execute_query.return_value = {
            "value": [
                {
                    "id": "item-1",
                    "displayName": "Item 1"
                },
                {
                    "id": "item-2",
                    "displayName": "Item 2"
                }
            ]
        }
        
        # Create a mock response for query_to_dataframe
        self.mock_connection_manager.query_to_dataframe.return_value = pd.DataFrame([
            {
                "id": "item-1",
                "displayName": "Item 1"
            },
            {
                "id": "item-2",
                "displayName": "Item 2"
            }
        ])
        
        # Create the adapter
        self.adapter = MSGraphAdapter(connection_manager=self.mock_connection_manager)
    
    def test_connect(self):
        """
        Test connect method.
        """
        # Configure the mock
        self.mock_connection_manager.connect.return_value = True
        
        # Call the method
        result = self.adapter.connect()
        
        # Verify the result
        self.assertTrue(result)
        self.mock_connection_manager.connect.assert_called_once()
    
    def test_is_connected(self):
        """
        Test is_connected method.
        """
        # Call the method
        result = self.adapter.is_connected()
        
        # Verify the result
        self.assertTrue(result)
    
    def test_execute_query(self):
        """
        Test execute_query method.
        """
        # Call the method
        result = self.adapter.execute_query("/users")
        
        # Verify the result
        self.assertEqual(result, {
            "value": [
                {
                    "id": "item-1",
                    "displayName": "Item 1"
                },
                {
                    "id": "item-2",
                    "displayName": "Item 2"
                }
            ]
        })
        self.mock_connection_manager.execute_query.assert_called_once_with("/users", None)
    
    def test_query_to_dataframe(self):
        """
        Test query_to_dataframe method.
        """
        # Call the method
        result = self.adapter.query_to_dataframe("/users")
        
        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["id"], "item-1")
        self.assertEqual(result.iloc[0]["displayName"], "Item 1")
        self.mock_connection_manager.query_to_dataframe.assert_called_once_with("/users", None)
    
    def test_get_users(self):
        """
        Test get_users method.
        """
        # Call the method
        result = self.adapter.get_users()
        
        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["id"], "user-1")
        self.assertEqual(result.iloc[0]["displayName"], "User 1")
        self.mock_connection_manager.get_users.assert_called_once_with(None)
    
    def test_get_groups(self):
        """
        Test get_groups method.
        """
        # Call the method
        result = self.adapter.get_groups()
        
        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["id"], "group-1")
        self.assertEqual(result.iloc[0]["displayName"], "Group 1")
        self.mock_connection_manager.get_groups.assert_called_once_with(None)
    
    def test_get_me(self):
        """
        Test get_me method.
        """
        # Call the method
        result = self.adapter.get_me()
        
        # Verify the result
        self.assertEqual(result["id"], "test-user-id")
        self.assertEqual(result["displayName"], "Test User")
        self.assertEqual(result["mail"], "test.user@example.com")
        self.mock_connection_manager.get_me.assert_called_once()
    
    def test_fetch_labels(self):
        """
        Test fetch_labels method.
        """
        # Call the method
        result = self.adapter.fetch_labels()
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertIn("User", result)
        self.assertIn("Group", result)
        self.assertIn("Message", result)
        self.assertIn("Event", result)
        self.assertIn("DriveItem", result)
    
    def test_fetch_node_properties(self):
        """
        Test fetch_node_properties method.
        """
        # Call the method for User
        user_props = self.adapter.fetch_node_properties("User")
        
        # Verify the result
        self.assertIsInstance(user_props, list)
        self.assertIn("id", user_props)
        self.assertIn("display_name", user_props)
        self.assertIn("email", user_props)
        
        # Call the method for Group
        group_props = self.adapter.fetch_node_properties("Group")
        
        # Verify the result
        self.assertIsInstance(group_props, list)
        self.assertIn("id", group_props)
        self.assertIn("display_name", group_props)
        self.assertIn("mail", group_props)
        
        # Call the method for unknown label
        unknown_props = self.adapter.fetch_node_properties("Unknown")
        
        # Verify the result
        self.assertIsInstance(unknown_props, list)
        self.assertEqual(len(unknown_props), 0)
    
    def test_fetch_nodes(self):
        """
        Test fetch_nodes method.
        """
        # Call the method for User
        user_nodes = self.adapter.fetch_nodes("User")
        
        # Verify the result
        self.assertIsInstance(user_nodes, pd.DataFrame)
        self.assertEqual(len(user_nodes), 2)
        self.assertEqual(user_nodes.iloc[0]["id"], "user-1")
        self.assertEqual(user_nodes.iloc[0]["displayName"], "User 1")
        self.mock_connection_manager.get_users.assert_called_with({'top': 100})
        
        # Call the method for Group
        group_nodes = self.adapter.fetch_nodes("Group")
        
        # Verify the result
        self.assertIsInstance(group_nodes, pd.DataFrame)
        self.assertEqual(len(group_nodes), 2)
        self.assertEqual(group_nodes.iloc[0]["id"], "group-1")
        self.assertEqual(group_nodes.iloc[0]["displayName"], "Group 1")
        self.mock_connection_manager.get_groups.assert_called_with({'top': 100})
        
        # Call the method for unknown label
        unknown_nodes = self.adapter.fetch_nodes("Unknown")
        
        # Verify the result
        self.assertIsInstance(unknown_nodes, pd.DataFrame)
        self.assertEqual(len(unknown_nodes), 0)


if __name__ == '__main__':
    unittest.main()