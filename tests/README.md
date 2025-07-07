# Testing Framework for Science Data Kit

This directory contains tests for the Science Data Kit application. The tests are organized into unit tests and integration tests.

## Directory Structure

- **[unit/](unit/README.md)** - Unit tests for individual components
  - **[ui/](unit/ui/README.md)** - Tests for UI components
  - **[core/](unit/core/README.md)** - Tests for core functionality
- **[integration/](integration/README.md)** - Integration tests for component interactions
- **[end_to_end/](end_to_end/README.md)** - End-to-end tests for complete workflows

### Additional Test Locations

Some tests are also located within the package structure:

- **science_data_kit/tests/** - Package-specific tests
  - **science_data_kit/tests/core/** - Tests for core package functionality
  - **science_data_kit/tests/test_msgraph_*.py** - Tests for Microsoft Graph API integration

## Running Tests

To run all tests:

```bash
pytest
```

To run only unit tests:

```bash
pytest tests/unit
```

To run only integration tests:

```bash
pytest tests/integration
```

To run only end-to-end tests:

```bash
pytest tests/end_to_end
```

To run package-specific tests:

```bash
pytest science_data_kit/tests
```

To run Microsoft Graph API tests specifically:

```bash
pytest science_data_kit/tests/test_msgraph_*.py
```

To run tests with coverage:

```bash
pytest --cov=science_data_kit
```

## Writing Tests

### Unit Tests

Unit tests should test individual components in isolation. They should mock any dependencies to ensure that the test is focused on the component being tested.

Example:

```python
def test_render_sidebar_header(mock_streamlit):
    """Test that the sidebar header is rendered correctly."""
    # Call the function
    render_sidebar_header()

    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].image.assert_called_once()
    mock_streamlit['sidebar'].title.assert_called_once_with("Science Data Kit")
```

### Integration Tests

Integration tests should test the interaction between components. They may still mock some dependencies, but they should test the integration between multiple components.

Example:

```python
def test_database_connection_integration(mock_streamlit, mock_neo4j_driver):
    """
    Test the integration between the database connection UI and the Neo4j connection.
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
```

### End-to-End Tests

End-to-end tests should test complete workflows from start to finish. They should not mock any components unless absolutely necessary, as the goal is to test the entire system working together.

Example:

```python
def test_parallel_map_workflow():
    """
    Test a complete workflow using parallel_map.

    This test:
    1. Creates a dataset
    2. Processes it using parallel_map
    3. Verifies the results
    """
    # Create a dataset
    data = list(range(1, 11))  # [1, 2, 3, ..., 10]

    # Define a processing function that simulates some work
    def slow_square(x):
        time.sleep(0.01)  # Simulate work
        return x * x

    # Process the data using parallel processing
    results = parallel_map(slow_square, data)

    # Verify the results are correct
    assert results == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

## Test Fixtures

The `conftest.py` file contains fixtures that can be used in tests. These fixtures provide common functionality for tests, such as mocking Streamlit functions and Neo4j connections.

Example:

```python
@pytest.fixture
def mock_streamlit():
    """
    Fixture to mock Streamlit functions for testing UI components.
    """
    with patch('streamlit.text') as mock_text, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.header') as mock_header, \
         patch('streamlit.subheader') as mock_subheader, \
         patch('streamlit.sidebar') as mock_sidebar:

        # Return all mocks as a dictionary
        yield {
            'text': mock_text,
            'markdown': mock_markdown,
            'header': mock_header,
            'subheader': mock_subheader,
            'sidebar': mock_sidebar
        }
```
