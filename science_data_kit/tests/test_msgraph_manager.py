"""
Unit tests for Microsoft Graph API Connection Manager

This module contains unit tests for the Microsoft Graph API connection manager.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from typing import Dict, Any

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager


class TestMSGraphConnectionManager(unittest.TestCase):
    """
    Test cases for the Microsoft Graph API connection manager.
    """
    
    def setUp(self):
        """
        Set up test environment.
        """
        # Create a mock configuration
        self.config = {
            "tenant_id": "test-tenant-id",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "auth_method": "client_credentials"
        }
        
        # Create a temporary config file
        self.config_file = "test_msgraph_config.json"
        with open(self.config_file, "w") as f:
            json.dump(self.config, f)
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        # Remove temporary config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_init_with_params(self, mock_graph_client, mock_credential):
        """
        Test initialization with parameters.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"displayName": "Test User"}
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(
            tenant_id=self.config["tenant_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_method=self.config["auth_method"]
        )
        
        # Verify initialization
        self.assertEqual(manager.tenant_id, self.config["tenant_id"])
        self.assertEqual(manager.client_id, self.config["client_id"])
        self.assertEqual(manager.client_secret, self.config["client_secret"])
        self.assertEqual(manager.auth_method, self.config["auth_method"])
        self.assertFalse(manager.connected)
        self.assertIsNone(manager.client)
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_init_with_config_file(self, mock_graph_client, mock_credential):
        """
        Test initialization with config file.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"displayName": "Test User"}
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(config_file=self.config_file)
        
        # Verify initialization
        self.assertEqual(manager.tenant_id, self.config["tenant_id"])
        self.assertEqual(manager.client_id, self.config["client_id"])
        self.assertEqual(manager.client_secret, self.config["client_secret"])
        self.assertEqual(manager.auth_method, self.config["auth_method"])
        self.assertFalse(manager.connected)
        self.assertIsNone(manager.client)
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_connect_success(self, mock_graph_client, mock_credential):
        """
        Test successful connection.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"displayName": "Test User"}
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(
            tenant_id=self.config["tenant_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_method=self.config["auth_method"]
        )
        
        # Connect
        result = manager.connect()
        
        # Verify connection
        self.assertTrue(result)
        self.assertTrue(manager.connected)
        self.assertIsNotNone(manager.client)
        mock_client.get.assert_called_once_with('/me')
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_connect_failure(self, mock_graph_client, mock_credential):
        """
        Test failed connection.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(
            tenant_id=self.config["tenant_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_method=self.config["auth_method"]
        )
        
        # Connect
        result = manager.connect()
        
        # Verify connection
        self.assertFalse(result)
        self.assertFalse(manager.connected)
        self.assertIsNotNone(manager.client)
        mock_client.get.assert_called_once_with('/me')
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_execute_query(self, mock_graph_client, mock_credential):
        """
        Test execute_query method.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"id": "1", "displayName": "Test User"}]}
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(
            tenant_id=self.config["tenant_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_method=self.config["auth_method"]
        )
        
        # Connect
        manager.connect()
        
        # Execute query
        result = manager.execute_query('/users')
        
        # Verify result
        self.assertEqual(result, {"value": [{"id": "1", "displayName": "Test User"}]})
        mock_client.get.assert_called_with('/users')
    
    @patch("science_data_kit.core.db.msgraph_manager.MSGRAPH_AVAILABLE", True)
    @patch("science_data_kit.core.db.msgraph_manager.ClientSecretCredential")
    @patch("science_data_kit.core.db.msgraph_manager.GraphClient")
    def test_query_to_dataframe(self, mock_graph_client, mock_credential):
        """
        Test query_to_dataframe method.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"id": "1", "displayName": "Test User"}]}
        
        # Configure the mock client
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_graph_client.return_value = mock_client
        
        # Create a connection manager
        manager = MSGraphConnectionManager(
            tenant_id=self.config["tenant_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_method=self.config["auth_method"]
        )
        
        # Connect
        manager.connect()
        
        # Execute query
        result = manager.query_to_dataframe('/users')
        
        # Verify result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['id'], "1")
        self.assertEqual(result.iloc[0]['displayName'], "Test User")
        mock_client.get.assert_called_with('/users')


if __name__ == '__main__':
    unittest.main()