# Science Data Kit Testing Strategy

## Overview

This document outlines the testing strategy for the Science Data Kit (SDK) project. It explains the approach to testing different components of the SDK, the types of tests used, and best practices for writing and running tests.

## Testing Philosophy

The Science Data Kit follows a comprehensive testing approach that aims to:

1. **Ensure Correctness**: Verify that all components work as expected
2. **Prevent Regressions**: Catch issues before they affect users
3. **Document Behavior**: Tests serve as executable documentation
4. **Support Refactoring**: Enable safe code changes and improvements
5. **Validate Integration**: Ensure components work together correctly

## Test Types

The SDK uses a multi-layered testing approach:

### 1. Unit Tests

Unit tests focus on testing individual components in isolation. They verify that each function, method, or class behaves correctly on its own.

**Characteristics**:
- Fast execution
- Isolated (dependencies are mocked)
- High coverage of code paths
- Focus on a single component

**Location**: `tests/unit/` directory

**Example**:
```python
def test_render_sidebar_header(mock_streamlit):
    """Test that the sidebar header is rendered correctly."""
    # Call the function
    render_sidebar_header()

    # Check that the correct Streamlit functions were called
    mock_streamlit['sidebar'].image.assert_called_once()
    mock_streamlit['sidebar'].title.assert_called_once_with("Science Data Kit")
```

### 2. Integration Tests

Integration tests verify that multiple components work together correctly. They test the interactions between components and ensure they integrate properly.

**Characteristics**:
- Test component interactions
- May still mock some external dependencies
- Focus on interfaces between components
- Verify correct data flow between components

**Location**: `tests/integration/` directory

**Example**:
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

### 3. End-to-End Tests

End-to-end tests verify complete workflows from start to finish. They test the entire system working together as a whole.

**Characteristics**:
- Test complete workflows
- Minimal mocking (only external services if necessary)
- Slower execution
- Focus on user scenarios

**Location**: `tests/end_to_end/` directory

**Example**:
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

## Test Organization

The tests are organized into the following directory structure:

```
tests/
├── conftest.py                 # Common fixtures and configuration
├── README.md                   # Testing documentation
├── unit/                       # Unit tests
│   ├── app/                    # Tests for app components
│   ├── core/                   # Tests for core functionality
│   │   ├── api/                # Tests for API components
│   │   ├── db/                 # Tests for database components
│   │   ├── models/             # Tests for data models
│   │   ├── ontology/           # Tests for ontology components
│   │   └── providers/          # Tests for data providers
│   └── ui/                     # Tests for UI components
│       ├── components/         # Tests for UI components
│       └── pages/              # Tests for UI pages
├── integration/                # Integration tests
│   ├── README.md               # Integration testing documentation
│   └── ...                     # Various integration tests
└── end_to_end/                 # End-to-end tests
    └── ...                     # Various end-to-end tests
```

## Test Fixtures

Test fixtures provide common functionality for tests, such as mocking dependencies and setting up test environments. They are defined in the `conftest.py` file.

**Example**:
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

## Running Tests

Tests can be run using the pytest framework:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run only end-to-end tests
pytest tests/end_to_end

# Run tests with coverage
pytest --cov=science_data_kit
```

## Code Coverage

Code coverage is measured using the pytest-cov plugin. It generates reports showing which parts of the code are covered by tests.

```bash
# Generate a coverage report
pytest --cov=science_data_kit

# Generate an HTML coverage report
pytest --cov=science_data_kit --cov-report=html
```

## Best Practices

### Writing Tests

1. **Test one thing per test**: Each test should focus on testing a single aspect of the code.
2. **Use descriptive test names**: Test names should clearly describe what is being tested.
3. **Follow the AAA pattern**: Arrange, Act, Assert.
4. **Keep tests independent**: Tests should not depend on each other.
5. **Mock external dependencies**: Use mocks to isolate the code being tested.
6. **Test edge cases**: Include tests for boundary conditions and error cases.
7. **Keep tests simple**: Tests should be easy to understand and maintain.

### Test-Driven Development (TDD)

When implementing new features, consider following the TDD approach:

1. Write a failing test that defines the expected behavior
2. Implement the minimum code needed to make the test pass
3. Refactor the code while keeping the tests passing

## Continuous Integration

Tests are automatically run as part of the continuous integration (CI) pipeline using GitHub Actions. The CI pipeline:

1. Runs all tests on each pull request
2. Generates a coverage report
3. Fails if tests fail or if coverage drops below a threshold

## Component-Specific Testing Strategies

### UI Components

UI components are tested using mocked Streamlit functions to verify that the correct Streamlit API calls are made.

### Database Operations

Database operations are tested using mocked Neo4j drivers to verify that the correct queries are executed.

### API Integrations

API integrations are tested using mocked HTTP responses to verify that the correct API calls are made and responses are handled correctly.

### Data Processing

Data processing functions are tested with various input data to verify that they produce the expected output.

## Conclusion

This testing strategy ensures that the Science Data Kit is thoroughly tested at multiple levels, from individual components to complete workflows. By following this strategy, we can maintain high code quality, prevent regressions, and ensure that the SDK works correctly for users.