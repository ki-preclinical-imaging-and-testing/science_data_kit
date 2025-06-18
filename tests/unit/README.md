# Unit Tests for Science Data Kit

This directory contains unit tests for the Science Data Kit application. Unit tests focus on testing individual components in isolation.

## Directory Structure

- **[ui/](ui/README.md)** - Tests for UI components
  - **[components/](ui/components/README.md)** - Tests for UI components
  - **[pages/](ui/pages/README.md)** - Tests for UI pages
- **[core/](core/README.md)** - Tests for core functionality

## Running Unit Tests

To run all unit tests:

```bash
pytest tests/unit
```

To run tests for a specific module:

```bash
pytest tests/unit/ui/components/test_sidebar.py
```

## Writing Unit Tests

Unit tests should follow these principles:

1. **Isolation**: Test one component at a time, mocking all dependencies.
2. **Clarity**: Each test should have a clear purpose and assertion.
3. **Completeness**: Cover all code paths, including edge cases and error handling.

### Example Unit Test

```python
def test_render_sidebar_header(mock_streamlit):
    """Test that the sidebar header is rendered correctly."""
    # Call the function
    render_sidebar_header()
    
    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].image.assert_called_once()
    mock_streamlit['sidebar'].title.assert_called_once_with("Science Data Kit")
```

### Testing UI Components

When testing UI components, use the `mock_streamlit` fixture to mock Streamlit functions:

```python
def test_render_database_sidebar_not_connected(mock_streamlit):
    """Test that the database sidebar is rendered correctly when not connected."""
    # Set up session state
    with patch.object(st.session_state, 'get', return_value=False):
        # Call the function
        render_database_sidebar()
        
        # Check that the correct Streamlit functions were called
        mock_streamlit['sidebar'].header.assert_called_once_with("Database Connection")
        mock_streamlit['sidebar'].warning.assert_called_once_with("Not connected to Neo4j")
        mock_streamlit['sidebar'].form.assert_called_once_with("neo4j_connection_form")
```

### Testing Core Functionality

When testing core functionality, mock external dependencies like database connections:

```python
def test_neo4j_connection():
    """Test that the Neo4jConnection class works correctly."""
    # Mock the Neo4j driver
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        # Create a Neo4jConnection
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
```