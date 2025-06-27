"""
Unit tests for Microsoft Graph API Utility Functions

This module contains unit tests for the Microsoft Graph API utility functions.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import networkx as nx
from typing import Dict, Any

from science_data_kit.core.utils.msgraph_utils import (
    msgraph_to_network,
    save_msgraph_response,
    load_msgraph_response,
    extract_user_data,
    extract_group_data,
    extract_message_data
)


class TestMSGraphUtils(unittest.TestCase):
    """
    Test cases for the Microsoft Graph API utility functions.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        # Sample user data
        self.user_data = {
            "id": "user-1",
            "displayName": "User 1",
            "mail": "user1@example.com",
            "userPrincipalName": "user1@example.com",
            "department": "Engineering",
            "jobTitle": "Software Engineer",
            "officeLocation": "Building A",
            "businessPhones": ["+1 123-456-7890"],
            "mobilePhone": "+1 234-567-8901"
        }
        
        # Sample users collection
        self.users_data = {
            "value": [
                self.user_data,
                {
                    "id": "user-2",
                    "displayName": "User 2",
                    "mail": "user2@example.com",
                    "userPrincipalName": "user2@example.com",
                    "department": "Marketing",
                    "jobTitle": "Marketing Manager"
                }
            ]
        }
        
        # Sample group data
        self.group_data = {
            "id": "group-1",
            "displayName": "Group 1",
            "description": "Test Group 1",
            "mail": "group1@example.com",
            "groupTypes": ["Unified"],
            "securityEnabled": True,
            "mailEnabled": True,
            "members@odata.bind": [
                "https://graph.microsoft.com/v1.0/directoryObjects/user-1",
                "https://graph.microsoft.com/v1.0/directoryObjects/user-2"
            ]
        }
        
        # Sample groups collection
        self.groups_data = {
            "value": [
                self.group_data,
                {
                    "id": "group-2",
                    "displayName": "Group 2",
                    "description": "Test Group 2",
                    "mail": "group2@example.com",
                    "groupTypes": ["Unified"],
                    "securityEnabled": True,
                    "mailEnabled": True
                }
            ]
        }
        
        # Sample message data
        self.message_data = {
            "id": "message-1",
            "subject": "Test Subject",
            "body": {
                "content": "Test Body",
                "contentType": "text"
            },
            "from": {
                "emailAddress": {
                    "address": "sender@example.com",
                    "name": "Sender"
                }
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient1@example.com",
                        "name": "Recipient 1"
                    }
                },
                {
                    "emailAddress": {
                        "address": "recipient2@example.com",
                        "name": "Recipient 2"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": "cc1@example.com",
                        "name": "CC 1"
                    }
                }
            ],
            "bccRecipients": [
                {
                    "emailAddress": {
                        "address": "bcc1@example.com",
                        "name": "BCC 1"
                    }
                }
            ],
            "receivedDateTime": "2023-01-01T12:00:00Z",
            "hasAttachments": True
        }
    
    def test_msgraph_to_network_users(self):
        """
        Test msgraph_to_network function with users data.
        """
        # Call the function
        graph = msgraph_to_network(self.users_data, "users")
        
        # Verify the result
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(len(graph.nodes), 2)
        self.assertIn("user-1", graph.nodes)
        self.assertIn("user-2", graph.nodes)
        self.assertEqual(graph.nodes["user-1"]["name"], "User 1")
        self.assertEqual(graph.nodes["user-1"]["email"], "user1@example.com")
        self.assertEqual(graph.nodes["user-1"]["department"], "Engineering")
        
        # Test with single user
        graph = msgraph_to_network(self.user_data, "users")
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(len(graph.nodes), 1)
        self.assertIn("user-1", graph.nodes)
    
    def test_msgraph_to_network_groups(self):
        """
        Test msgraph_to_network function with groups data.
        """
        # Call the function
        graph = msgraph_to_network(self.groups_data, "groups")
        
        # Verify the result
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(len(graph.nodes), 2)
        self.assertIn("group-1", graph.nodes)
        self.assertIn("group-2", graph.nodes)
        self.assertEqual(graph.nodes["group-1"]["name"], "Group 1")
        self.assertEqual(graph.nodes["group-1"]["description"], "Test Group 1")
        self.assertEqual(graph.nodes["group-1"]["email"], "group1@example.com")
        
        # Check edges for group-1
        self.assertEqual(len(graph.edges), 2)
        self.assertIn(("group-1", "user-1"), graph.edges)
        self.assertIn(("group-1", "user-2"), graph.edges)
        self.assertEqual(graph.edges[("group-1", "user-1")]["relationship"], "member")
        
        # Test with single group
        graph = msgraph_to_network(self.group_data, "groups")
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(len(graph.nodes), 1)
        self.assertIn("group-1", graph.nodes)
        self.assertEqual(len(graph.edges), 2)
    
    @patch("builtins.open", new_callable=mock_open)
    def test_save_msgraph_response(self, mock_file):
        """
        Test save_msgraph_response function.
        """
        # Call the function
        save_msgraph_response(self.user_data, "test_file.json")
        
        # Verify the result
        mock_file.assert_called_once_with("test_file.json", "w")
        handle = mock_file()
        handle.write.assert_called_once()
        
        # Test with IOError
        mock_file.side_effect = IOError("Test error")
        with self.assertRaises(IOError):
            save_msgraph_response(self.user_data, "test_file.json")
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"id": "user-1", "displayName": "User 1"}')
    def test_load_msgraph_response(self, mock_file):
        """
        Test load_msgraph_response function.
        """
        # Call the function
        result = load_msgraph_response("test_file.json")
        
        # Verify the result
        mock_file.assert_called_once_with("test_file.json", "r")
        self.assertEqual(result, {"id": "user-1", "displayName": "User 1"})
        
        # Test with FileNotFoundError
        mock_file.side_effect = FileNotFoundError("Test error")
        with self.assertRaises(FileNotFoundError):
            load_msgraph_response("test_file.json")
        
        # Test with IOError
        mock_file.side_effect = IOError("Test error")
        with self.assertRaises(IOError):
            load_msgraph_response("test_file.json")
        
        # Test with JSONDecodeError
        mock_file.side_effect = None
        with patch("json.load") as mock_json_load:
            mock_json_load.side_effect = json.JSONDecodeError("Test error", "", 0)
            with self.assertRaises(json.JSONDecodeError):
                load_msgraph_response("test_file.json")
    
    def test_extract_user_data(self):
        """
        Test extract_user_data function.
        """
        # Call the function
        result = extract_user_data(self.user_data)
        
        # Verify the result
        self.assertEqual(result["id"], "user-1")
        self.assertEqual(result["display_name"], "User 1")
        self.assertEqual(result["email"], "user1@example.com")
        self.assertEqual(result["user_principal_name"], "user1@example.com")
        self.assertEqual(result["department"], "Engineering")
        self.assertEqual(result["job_title"], "Software Engineer")
        self.assertEqual(result["office_location"], "Building A")
        self.assertEqual(result["business_phones"], ["+1 123-456-7890"])
        self.assertEqual(result["mobile_phone"], "+1 234-567-8901")
    
    def test_extract_group_data(self):
        """
        Test extract_group_data function.
        """
        # Call the function
        result = extract_group_data(self.group_data)
        
        # Verify the result
        self.assertEqual(result["id"], "group-1")
        self.assertEqual(result["display_name"], "Group 1")
        self.assertEqual(result["description"], "Test Group 1")
        self.assertEqual(result["mail"], "group1@example.com")
        self.assertEqual(result["group_types"], ["Unified"])
        self.assertEqual(result["security_enabled"], True)
        self.assertEqual(result["mail_enabled"], True)
    
    def test_extract_message_data(self):
        """
        Test extract_message_data function.
        """
        # Call the function
        result = extract_message_data(self.message_data)
        
        # Verify the result
        self.assertEqual(result["id"], "message-1")
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["body"], "Test Body")
        self.assertEqual(result["from_email"], "sender@example.com")
        self.assertEqual(result["to_recipients"], ["recipient1@example.com", "recipient2@example.com"])
        self.assertEqual(result["cc_recipients"], ["cc1@example.com"])
        self.assertEqual(result["bcc_recipients"], ["bcc1@example.com"])
        self.assertEqual(result["received_datetime"], "2023-01-01T12:00:00Z")
        self.assertEqual(result["has_attachments"], True)
        
        # Test with missing fields
        minimal_message = {
            "id": "message-2",
            "subject": "Minimal Subject"
        }
        result = extract_message_data(minimal_message)
        self.assertEqual(result["id"], "message-2")
        self.assertEqual(result["subject"], "Minimal Subject")
        self.assertEqual(result["body"], "")
        self.assertEqual(result["from_email"], "")
        self.assertEqual(result["to_recipients"], [])
        self.assertEqual(result["cc_recipients"], [])
        self.assertEqual(result["bcc_recipients"], [])
        self.assertEqual(result["received_datetime"], "")
        self.assertEqual(result["has_attachments"], False)


if __name__ == '__main__':
    unittest.main()