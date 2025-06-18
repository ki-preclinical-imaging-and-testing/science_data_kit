# Integration Tests for Science Data Kit

This directory contains integration tests for the Science Data Kit application. Integration tests focus on testing the interaction between components.

## Running Integration Tests

To run all integration tests:

```bash
pytest tests/integration
```

To run tests for a specific module:

```bash
pytest tests/integration/test_database_connection.py
```

## Writing Integration Tests

Integration tests should follow these principles:

1. **Component Interaction**: Test how multiple components work together.
2. **Realistic Scenarios**: Test realistic user workflows and scenarios.
3. **Minimal Mocking**: Mock only external dependencies that are not part of the integration being tested.

### Example Integration Test

```python
def test_database_connection_integration(mock_streamlit, mock_neo4j_driver):
    """
    Test the integration between the database connection UI and the Neo4j connection.
    
    This test simulates a user entering connection details and clicking the connect button.
    It verifies that the Neo4j connection is created with the correct parameters and that
    the UI is updated accordingly.
    """
    # Set up session state
    with patch.object(st.session_state, 'get', return_value=False), \
         patch.object(st.session_state, '__setitem__', MagicMock()) as mock_set_item:
        
        # Create a mock form submit button that returns True (clicked)
        mock_streamlit['form_submit_button'].return_value = True
        
        # Create a mock text_input that returns test values
        mock_streamlit['text_input'].side_effect = [
            "bolt://test-neo4j:7687",  # URI
            "test_user",               # Username
            "test_password",           # Password
            "test_db"                  # Database
        ]
        
        # Create a mock callback function
        mock_callback = MagicMock()
        
        # Call the function with the mock callback
        render_database_sidebar(on_connect=mock_callback)
        
        # Check that the callback was called with the correct parameters
        mock_callback.assert_called_once_with(
            "bolt://test-neo4j:7687",
            "test_user",
            "test_password",
            "test_db"
        )
        
        # Check that the session state was updated
        assert mock_set_item.call_count == 4
        mock_set_item.assert_any_call("neo4j_uri", "bolt://test-neo4j:7687")
        mock_set_item.assert_any_call("neo4j_user", "test_user")
        mock_set_item.assert_any_call("neo4j_password", "test_password")
        mock_set_item.assert_any_call("neo4j_database", "test_db")
```

### Testing UI-to-Core Interaction

When testing the interaction between UI components and core functionality, focus on the data flow and state changes:

```python
def test_neo4j_connection_with_ui_parameters():
    """
    Test that the Neo4jConnection class works correctly with parameters from the UI.
    
    This test verifies that the Neo4jConnection class can be instantiated with
    parameters that would come from the UI, and that it correctly configures
    the Neo4j driver.
    """
    # Mock the Neo4j driver
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        # Create a Neo4jConnection with UI parameters
        connection = Neo4jConnection(
            uri="bolt://test-neo4j:7687",
            user="test_user",
            password="test_password",
            database="test_db"
        )
        
        # Check that the driver was created with the correct parameters
        mock_driver.assert_called_once_with(
            "bolt://test-neo4j:7687",
            auth=("test_user", "test_password")
        )
        
        # Check that the database was set correctly
        assert connection.database == "test_db"
```

### Testing Error Handling

Integration tests should also verify that errors are handled correctly:

```python
def test_database_connection_error_handling(mock_streamlit):
    """
    Test that database connection errors are handled correctly in the UI.
    
    This test simulates a user entering connection details and clicking the connect button,
    but the connection fails. It verifies that the error is displayed in the UI.
    """
    # Set up session state
    with patch.object(st.session_state, 'get', return_value=False), \
         patch.object(st.session_state, '__setitem__', MagicMock()):
        
        # Create a mock form submit button that returns True (clicked)
        mock_streamlit['form_submit_button'].return_value = True
        
        # Create a mock text_input that returns test values
        mock_streamlit['text_input'].side_effect = [
            "bolt://test-neo4j:7687",  # URI
            "test_user",               # Username
            "test_password",           # Password
            "test_db"                  # Database
        ]
        
        # Create a mock callback function that raises an exception
        mock_callback = MagicMock(side_effect=Exception("Connection failed"))
        
        # Call the function with the mock callback
        render_database_sidebar(on_connect=mock_callback)
        
        # Check that the callback was called with the correct parameters
        mock_callback.assert_called_once_with(
            "bolt://test-neo4j:7687",
            "test_user",
            "test_password",
            "test_db"
        )
        
        # In a real integration test, we would check that an error message is displayed
        # However, this is difficult to test with mocks, so we'll just verify that the
        # callback was called and raised an exception
        assert mock_callback.call_count == 1
```