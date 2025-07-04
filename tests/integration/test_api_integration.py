"""
Integration tests for API functionality.

This module contains tests that verify the interaction between
the API endpoints and the underlying functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from science_data_kit.core.api.endpoints import DatabaseEndpoint, SessionEndpoint
from science_data_kit.core.api.auth import APIAuth, APIToken, APIPermission


@pytest.fixture
def mock_auth():
    """Mock authentication for testing."""
    auth = MagicMock(spec=APIAuth)
    
    # Configure the mock auth to return a token
    token = APIToken(
        user_id="test_user",
        roles=None,
        permissions={APIPermission.READ, APIPermission.WRITE, APIPermission.DELETE}
    )
    auth.authenticate_and_authorize.return_value = token
    
    return auth


def test_database_endpoint_get_info(mock_auth):
    """
    Test the GET method of DatabaseEndpoint for retrieving database information.
    
    This test verifies that the DatabaseEndpoint correctly handles GET requests
    for database information and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a GET request
    response = endpoint.handle_request(
        method="GET",
        path="/api/database",
        params={},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.READ
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.data["name"] == "neo4j"
    assert response.data["version"] == "4.4.0"
    assert response.data["status"] == "running"


def test_database_endpoint_execute_query(mock_auth):
    """
    Test the GET method of DatabaseEndpoint for executing a query.
    
    This test verifies that the DatabaseEndpoint correctly handles GET requests
    for executing a query and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a GET request for a query
    response = endpoint.handle_request(
        method="GET",
        path="/api/database/query",
        params={"query": "MATCH (n) RETURN n"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.READ
    )
    
    # Check the response
    assert response.status_code == 200
    assert "results" in response.data
    assert "count" in response.data
    assert "execution_time" in response.data


def test_database_endpoint_create_database(mock_auth):
    """
    Test the POST method of DatabaseEndpoint for creating a database.
    
    This test verifies that the DatabaseEndpoint correctly handles POST requests
    for creating a database and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a POST request
    response = endpoint.handle_request(
        method="POST",
        path="/api/database",
        params={},
        body={"name": "new_db"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed with WRITE permission
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.WRITE
    )
    
    # Check the response
    assert response.status_code == 201
    assert response.data["message"] == "Database created"
    assert "database_id" in response.data


def test_database_endpoint_update_database(mock_auth):
    """
    Test the PUT method of DatabaseEndpoint for updating a database.
    
    This test verifies that the DatabaseEndpoint correctly handles PUT requests
    for updating a database and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a PUT request
    response = endpoint.handle_request(
        method="PUT",
        path="/api/database",
        params={},
        body={"name": "updated_db"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed with WRITE permission
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.WRITE
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.data["message"] == "Database updated"


def test_database_endpoint_delete_database(mock_auth):
    """
    Test the DELETE method of DatabaseEndpoint for deleting a database.
    
    This test verifies that the DatabaseEndpoint correctly handles DELETE requests
    for deleting a database and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a DELETE request
    response = endpoint.handle_request(
        method="DELETE",
        path="/api/database",
        params={"database_id": "123456"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed with DELETE permission
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.DELETE
    )
    
    # Check the response
    assert response.status_code == 200
    assert response.data["message"] == "Database deleted"


def test_database_endpoint_execute_query_post(mock_auth):
    """
    Test the POST method of DatabaseEndpoint for executing a query.
    
    This test verifies that the DatabaseEndpoint correctly handles POST requests
    for executing a query and returns the expected response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with a POST request for a query
    response = endpoint.handle_request(
        method="POST",
        path="/api/database/query",
        params={},
        body={"query": "MATCH (n) RETURN n"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check that authentication was performed with WRITE permission
    mock_auth.authenticate_and_authorize.assert_called_once_with(
        {"Authorization": "Bearer test_token"},
        APIPermission.WRITE
    )
    
    # Check the response
    assert response.status_code == 200
    assert "results" in response.data
    assert "count" in response.data
    assert "execution_time" in response.data


def test_database_endpoint_method_not_allowed(mock_auth):
    """
    Test handling of unsupported HTTP methods.
    
    This test verifies that the DatabaseEndpoint correctly handles requests with
    unsupported HTTP methods and returns an appropriate error response.
    """
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method with an unsupported method
    response = endpoint.handle_request(
        method="PATCH",
        path="/api/database",
        params={},
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Check the response
    assert response.status_code == 405
    assert "error" in response.data
    assert "Method PATCH not allowed" in response.data["error"]["message"]


def test_database_endpoint_authentication_error(mock_auth):
    """
    Test handling of authentication errors.
    
    This test verifies that the DatabaseEndpoint correctly handles authentication errors
    and returns an appropriate error response.
    """
    # Configure the mock auth to raise an exception
    mock_auth.authenticate_and_authorize.side_effect = Exception("Authentication failed")
    
    # Create a DatabaseEndpoint with the mock auth
    endpoint = DatabaseEndpoint(auth=mock_auth)
    
    # Call the handle_request method
    response = endpoint.handle_request(
        method="GET",
        path="/api/database",
        params={},
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    # Check the response
    assert response.status_code != 200
    assert "error" in response.data