# Science Data Kit UI Tests

This directory contains tests for the Science Data Kit UI components.

## Database Connectivity Tests

The `database_connectivity_tests.py` file contains tests for validating database connectivity in the Science Data Kit application. These tests ensure that the application can connect to a Neo4j database and perform basic operations.

### Running the Tests

To run the database connectivity tests, use the following command:

```bash
python science_data_kit/ui/tests/database_connectivity_tests.py
```

### Neo4j Container Management

The tests automatically manage a Neo4j Docker container for testing:

1. **Starting the Container**: The tests start a Neo4j container using the `start_container` method from the `Neo4jManager` class.
2. **Waiting for Initialization**: The tests wait for the Neo4j container to initialize, checking every 5 seconds if it's ready.
3. **Running the Tests**: Once the container is ready, the tests run against the Neo4j instance.
4. **Stopping the Container**: After the tests are complete, the container is stopped.

This approach ensures that the tests can run in any environment without requiring a pre-configured Neo4j instance.

### Test Components

The database connectivity tests validate the following components:

1. **Neo4j Connection**: Tests basic connection to the Neo4j database.
2. **Neo4j Manager**: Tests the `Neo4jManager` class functionality.
3. **DB Manager**: Tests the `db_manager` singleton.
4. **Database Sidebar**: Tests the database sidebar UI component.

### Test Results

The tests generate two CSV files with the results:

1. `science_data_kit/ui/tests/results/database_connectivity_test_results.csv`: Contains all test results.
2. `science_data_kit/ui/tests/results/database_connectivity_test_issues.csv`: Contains only the issues found during testing.

## Other Tests

(Add documentation for other tests as they are implemented)