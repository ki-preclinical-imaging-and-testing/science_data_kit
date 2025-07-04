# End-to-End Tests for Science Data Kit

This directory contains end-to-end tests for the Science Data Kit application. End-to-end tests test complete workflows from start to finish, ensuring that all components work together correctly.

## Running End-to-End Tests

To run all end-to-end tests:

```bash
pytest tests/end_to_end
```

To run a specific end-to-end test:

```bash
pytest tests/end_to_end/test_parallel_processing_workflow.py
```

## Writing End-to-End Tests

End-to-end tests should test complete workflows from start to finish. They should not mock any components unless absolutely necessary, as the goal is to test the entire system working together.

Example:

```python
def test_parallel_processing_workflow():
    """
    Test a complete workflow using parallel processing.
    
    This test:
    1. Creates a dataset
    2. Processes it using parallel processing
    3. Verifies the results
    """
    # Create a dataset
    data = [1, 2, 3, 4, 5]
    
    # Define a processing function
    def square(x):
        return x * x
    
    # Process the data using parallel processing
    from science_data_kit.core.utils.parallel_processing import parallel_map
    results = parallel_map(square, data)
    
    # Verify the results
    assert results == [1, 4, 9, 16, 25]
```

## Test Organization

End-to-end tests should be organized by workflow or feature. Each test file should focus on a specific workflow or feature and test it thoroughly.

For example:
- `test_parallel_processing_workflow.py` - Tests for parallel processing workflows
- `test_data_import_export_workflow.py` - Tests for data import and export workflows
- `test_database_query_workflow.py` - Tests for database query workflows