"""
API Usage Tutorial for Science Data Kit

This tutorial demonstrates how to use the API client libraries for the Science Data Kit,
including both the Python and JavaScript clients. It covers authentication, session management,
database operations, and error handling.
"""

import os
import sys
import logging
import json
import tempfile
import time
from typing import Dict, Any, List

# Import the Python client library
from science_data_kit.core.api.client import APIClient, SDKClient, APIClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a temporary directory for file examples
TEMP_DIR = tempfile.mkdtemp()


def example_python_low_level_api():
    """
    Example of using the low-level Python API client.

    This function demonstrates how to use the APIClient class to interact with
    the Science Data Kit API at a low level, including authentication, session
    management, and database operations.
    """
    print("\n=== Python Low-Level API Client Example ===\n")

    # Initialize the client
    # In a real application, you would use the actual URL of your SDK API server
    client = APIClient(base_url="http://localhost:8000")

    print("Initialized API client with base URL: http://localhost:8000")
    print()

    # Example of error handling
    print("Example of error handling:")
    try:
        # Try to get session information without logging in
        print("Attempting to get session information without logging in...")
        session_info = client.get_session()
        print(f"Session info: {session_info}")
    except APIClientError as e:
        print(f"Caught APIClientError: {e.message}")
        if e.status_code:
            print(f"Status code: {e.status_code}")
        if e.response:
            print(f"Response: {e.response}")
    print()

    # Login
    print("Example of authentication:")
    try:
        print("Logging in...")
        login_response = client.login(user_id="example_user")
        print(f"Login successful. Response: {json.dumps(login_response, indent=2)}")
        print(f"Token received and stored in client.")
    except APIClientError as e:
        print(f"Login failed: {e.message}")
    print()

    # Session management
    print("Example of session management:")
    try:
        # Get session information
        print("Getting session information...")
        session_info = client.get_session()
        print(f"Session info: {json.dumps(session_info, indent=2)}")

        # Create a new session
        print("Creating a new session...")
        new_session = client.create_session({
            "name": "Example Session",
            "description": "A session created from the API tutorial"
        })
        print(f"New session created: {json.dumps(new_session, indent=2)}")

        # Update the session
        print("Updating the session...")
        updated_session = client.update_session({
            "name": "Updated Example Session",
            "description": "An updated session description"
        })
        print(f"Session updated: {json.dumps(updated_session, indent=2)}")
    except APIClientError as e:
        print(f"Session management failed: {e.message}")
    print()

    # Database operations
    print("Example of database operations:")
    try:
        # Get database information
        print("Getting database information...")
        db_info = client.get_database_info()
        print(f"Database info: {json.dumps(db_info, indent=2)}")

        # Create a new database
        print("Creating a new database...")
        new_db = client.create_database({
            "name": "example_db",
            "description": "An example database"
        })
        print(f"New database created: {json.dumps(new_db, indent=2)}")

        # Execute a query
        print("Executing a query...")
        query_result = client.execute_query(
            query="MATCH (n) RETURN n.name, n.type LIMIT 5",
            params={}
        )
        print(f"Query result: {json.dumps(query_result, indent=2)}")

        # Execute a parameterized query
        print("Executing a parameterized query...")
        param_query_result = client.execute_query(
            query="MATCH (n) WHERE n.type = $type RETURN n.name, n.created_at LIMIT 5",
            params={"type": "Person"}
        )
        print(f"Parameterized query result: {json.dumps(param_query_result, indent=2)}")
    except APIClientError as e:
        print(f"Database operation failed: {e.message}")
    print()

    # Caching
    print("Example of caching:")
    try:
        # Enable caching
        print("Enabling caching...")
        client.enable_caching(True)
        print("Cache enabled.")

        # Execute a query (will be cached)
        print("Executing a query (first time, will be cached)...")
        start_time = time.time()
        query_result1 = client.execute_query(
            query="MATCH (n) RETURN n.name, n.type LIMIT 5",
            params={}
        )
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds.")

        # Execute the same query again (should use cache)
        print("Executing the same query again (should use cache)...")
        start_time = time.time()
        query_result2 = client.execute_query(
            query="MATCH (n) RETURN n.name, n.type LIMIT 5",
            params={}
        )
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds.")

        # Clear the cache
        print("Clearing the cache...")
        cleared_count = client.clear_cache()
        print(f"Cleared {cleared_count} cache entries.")

        # Execute the query again (will not use cache)
        print("Executing the query again after clearing cache...")
        start_time = time.time()
        query_result3 = client.execute_query(
            query="MATCH (n) RETURN n.name, n.type LIMIT 5",
            params={}
        )
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds.")
    except APIClientError as e:
        print(f"Caching example failed: {e.message}")
    print()

    # Cleanup
    print("Cleaning up:")
    try:
        # Delete the session
        print("Deleting the session...")
        delete_session_result = client.delete_session()
        print(f"Session deleted: {json.dumps(delete_session_result, indent=2)}")

        # Logout
        print("Logging out...")
        logout_result = client.logout()
        print(f"Logged out: {json.dumps(logout_result, indent=2)}")
    except APIClientError as e:
        print(f"Cleanup failed: {e.message}")
    print()

    return "Python low-level API example completed."


def example_python_high_level_sdk():
    """
    Example of using the high-level Python SDK client.

    This function demonstrates how to use the SDKClient class to interact with
    the Science Data Kit API at a high level, providing a more user-friendly
    interface for common operations.
    """
    print("\n=== Python High-Level SDK Client Example ===\n")

    # Initialize the client with automatic login
    # In a real application, you would use the actual URL of your SDK API server
    print("Initializing SDK client with automatic login...")
    client = SDKClient(
        base_url="http://localhost:8000",
        user_id="example_user"
    )
    print("SDK client initialized and logged in.")
    print()

    # Get user information
    print("Example of getting user information:")
    try:
        print("Getting user information...")
        user_info = client.get_user_info()
        print(f"User info: {json.dumps(user_info, indent=2)}")
    except APIClientError as e:
        print(f"Failed to get user info: {e.message}")
    print()

    # Execute queries
    print("Example of executing queries:")
    try:
        # Execute a simple query
        print("Executing a simple query...")
        results = client.query("MATCH (n) RETURN n.name, n.type LIMIT 5")
        print(f"Query results: {json.dumps(results, indent=2)}")

        # Execute a parameterized query
        print("Executing a parameterized query...")
        param_results = client.query(
            "MATCH (n) WHERE n.type = $type RETURN n.name, n.created_at LIMIT 5",
            params={"type": "Person"}
        )
        print(f"Parameterized query results: {json.dumps(param_results, indent=2)}")
    except APIClientError as e:
        print(f"Query execution failed: {e.message}")
    print()

    # Create a session with a database
    print("Example of creating a session with a database:")
    try:
        print("Creating a session with a database...")
        session = client.create_session_with_database(
            session_name="Example SDK Session",
            database_name="example_sdk_db"
        )
        print(f"Created session with database: {json.dumps(session, indent=2)}")
    except APIClientError as e:
        print(f"Failed to create session with database: {e.message}")
    print()

    # Caching with the high-level client
    print("Example of caching with the high-level client:")
    try:
        # Enable caching
        print("Enabling caching...")
        client.enable_caching(True)
        print("Cache enabled.")

        # Execute a query with cache
        print("Executing a query with cache...")
        results_with_cache = client.query_with_cache(
            "MATCH (n) RETURN n.name, n.type LIMIT 5"
        )
        print(f"Query results: {json.dumps(results_with_cache, indent=2)}")

        # Execute a query skipping cache
        print("Executing a query skipping cache...")
        results_skip_cache = client.query_with_cache(
            "MATCH (n) RETURN n.name, n.type LIMIT 5",
            skip_cache=True
        )
        print(f"Query results (skipped cache): {json.dumps(results_skip_cache, indent=2)}")

        # Clear the cache
        print("Clearing the cache...")
        cleared_count = client.clear_cache()
        print(f"Cleared {cleared_count} cache entries.")
    except APIClientError as e:
        print(f"Caching example failed: {e.message}")
    print()

    # Logout
    print("Logging out:")
    try:
        print("Logging out...")
        logout_result = client.logout()
        print(f"Logged out: {json.dumps(logout_result, indent=2)}")
    except APIClientError as e:
        print(f"Logout failed: {e.message}")
    print()

    return "Python high-level SDK example completed."


def example_javascript_client():
    """
    Example of using the JavaScript API client.

    This function demonstrates how to use the JavaScript client library in a web application
    or Node.js environment. Since we can't execute JavaScript directly in this Python tutorial,
    we'll provide the code as a string that can be copied and used in a JavaScript environment.
    """
    print("\n=== JavaScript API Client Example ===\n")

    print("The following is JavaScript code that demonstrates how to use the JavaScript API client.")
    print("This code can be copied and used in a web application or Node.js environment.")
    print()

    js_code = """
// Example of using the low-level JavaScript API client

// Initialize the client
// In a real application, you would use the actual URL of your SDK API server
const apiClient = new APIClient('http://localhost:8000');

// Example of error handling
console.log('Example of error handling:');
try {
  // Try to get session information without logging in
  console.log('Attempting to get session information without logging in...');
  apiClient.getSession()
    .then(sessionInfo => {
      console.log('Session info:', sessionInfo);
    })
    .catch(error => {
      console.error('Caught APIClientError:', error.message);
      if (error.statusCode) {
        console.error('Status code:', error.statusCode);
      }
      if (error.response) {
        console.error('Response:', error.response);
      }
    });
} catch (error) {
  console.error('Unexpected error:', error);
}

// Example of authentication
console.log('Example of authentication:');
apiClient.login('example_user')
  .then(response => {
    console.log('Login successful. Response:', JSON.stringify(response, null, 2));
    console.log('Token received and stored in client.');

    // Now that we're logged in, we can perform other operations

    // Example of session management
    console.log('Example of session management:');

    // Get session information
    apiClient.getSession()
      .then(sessionInfo => {
        console.log('Session info:', JSON.stringify(sessionInfo, null, 2));

        // Create a new session
        return apiClient.createSession({
          name: 'Example Session',
          description: 'A session created from the API tutorial'
        });
      })
      .then(newSession => {
        console.log('New session created:', JSON.stringify(newSession, null, 2));

        // Update the session
        return apiClient.updateSession({
          name: 'Updated Example Session',
          description: 'An updated session description'
        });
      })
      .then(updatedSession => {
        console.log('Session updated:', JSON.stringify(updatedSession, null, 2));

        // Example of database operations
        console.log('Example of database operations:');

        // Get database information
        return apiClient.getDatabaseInfo();
      })
      .then(dbInfo => {
        console.log('Database info:', JSON.stringify(dbInfo, null, 2));

        // Create a new database
        return apiClient.createDatabase({
          name: 'example_db',
          description: 'An example database'
        });
      })
      .then(newDb => {
        console.log('New database created:', JSON.stringify(newDb, null, 2));

        // Execute a query
        return apiClient.executeQuery(
          'MATCH (n) RETURN n.name, n.type LIMIT 5',
          {}
        );
      })
      .then(queryResult => {
        console.log('Query result:', JSON.stringify(queryResult, null, 2));

        // Execute a parameterized query
        return apiClient.executeQuery(
          'MATCH (n) WHERE n.type = $type RETURN n.name, n.created_at LIMIT 5',
          { type: 'Person' }
        );
      })
      .then(paramQueryResult => {
        console.log('Parameterized query result:', JSON.stringify(paramQueryResult, null, 2));

        // Cleanup
        console.log('Cleaning up:');

        // Delete the session
        return apiClient.deleteSession();
      })
      .then(deleteSessionResult => {
        console.log('Session deleted:', JSON.stringify(deleteSessionResult, null, 2));

        // Logout
        return apiClient.logout();
      })
      .then(logoutResult => {
        console.log('Logged out:', JSON.stringify(logoutResult, null, 2));
        console.log('JavaScript low-level API example completed.');
      })
      .catch(error => {
        console.error('Error:', error.message);
        if (error.statusCode) {
          console.error('Status code:', error.statusCode);
        }
        if (error.response) {
          console.error('Response:', error.response);
        }
      });
  })
  .catch(error => {
    console.error('Login failed:', error.message);
  });

// Example of using the high-level JavaScript SDK client

// Initialize the client with automatic login
// In a real application, you would use the actual URL of your SDK API server
console.log('Initializing SDK client with automatic login...');
const sdkClient = new SDKClient('http://localhost:8000', 'example_user');
console.log('SDK client initialized and logged in.');

// The SDKClient constructor will automatically log in, but we need to wait for that to complete
// before we can use the client. In a real application, you would use async/await or promises
// to handle this. For this example, we'll use a setTimeout to simulate waiting for the login to complete.
setTimeout(() => {
  // Example of getting user information
  console.log('Example of getting user information:');
  sdkClient.getUserInfo()
    .then(userInfo => {
      console.log('User info:', JSON.stringify(userInfo, null, 2));

      // Example of executing queries
      console.log('Example of executing queries:');

      // Execute a simple query
      return sdkClient.query('MATCH (n) RETURN n.name, n.type LIMIT 5');
    })
    .then(results => {
      console.log('Query results:', JSON.stringify(results, null, 2));

      // Execute a parameterized query
      return sdkClient.query(
        'MATCH (n) WHERE n.type = $type RETURN n.name, n.created_at LIMIT 5',
        { type: 'Person' }
      );
    })
    .then(paramResults => {
      console.log('Parameterized query results:', JSON.stringify(paramResults, null, 2));

      // Example of creating a session with a database
      console.log('Example of creating a session with a database:');
      return sdkClient.createSessionWithDatabase(
        'Example SDK Session',
        'example_sdk_db'
      );
    })
    .then(session => {
      console.log('Created session with database:', JSON.stringify(session, null, 2));

      // Logout
      console.log('Logging out:');
      return sdkClient.logout();
    })
    .then(logoutResult => {
      console.log('Logged out:', JSON.stringify(logoutResult, null, 2));
      console.log('JavaScript high-level SDK example completed.');
    })
    .catch(error => {
      console.error('Error:', error.message);
      if (error.statusCode) {
        console.error('Status code:', error.statusCode);
      }
      if (error.response) {
        console.error('Response:', error.response);
      }
    });
}, 1000);  // Wait 1 second for the login to complete
"""

    print(js_code)
    print()

    print("To use the JavaScript client in a web application, include the following script tag:")
    print('<script src="path/to/science_data_kit/core/api/client.js"></script>')
    print()

    print("To use the JavaScript client in a Node.js application, require it as follows:")
    print('const { APIClient, SDKClient, APIClientError } = require("path/to/science_data_kit/core/api/client.js");')
    print()

    return "JavaScript API client example provided."


def example_api_best_practices():
    """
    Example of API best practices.

    This function provides guidance on best practices for using the API client libraries,
    including error handling, performance optimization, and security considerations.
    """
    print("\n=== API Best Practices ===\n")

    print("1. Error Handling:")
    print("   - Always wrap API calls in try-except blocks to catch APIClientError exceptions.")
    print("   - Check the status_code and response properties of APIClientError for more details.")
    print("   - Implement retry logic for transient errors (e.g., network issues).")
    print()

    print("2. Authentication:")
    print("   - Store tokens securely and never expose them in client-side code.")
    print("   - Implement token refresh logic to handle token expiration.")
    print("   - Log out when the application is closed to invalidate the token.")
    print()

    print("3. Performance Optimization:")
    print("   - Use the caching functionality to reduce API calls for frequently accessed data.")
    print("   - Limit the amount of data returned by queries using LIMIT clauses.")
    print("   - Use parameterized queries to improve security and performance.")
    print()

    print("4. Security Considerations:")
    print("   - Validate all user input before sending it to the API.")
    print("   - Use HTTPS for all API communications.")
    print("   - Implement proper access controls and permissions in your application.")
    print()

    print("5. Resource Management:")
    print("   - Close sessions and connections when they are no longer needed.")
    print("   - Implement proper cleanup in case of errors or application shutdown.")
    print("   - Monitor resource usage to prevent leaks.")
    print()

    return "API best practices provided."


def run_tutorial():
    """Run all examples in the tutorial."""
    print("=== API Usage Tutorial ===")
    print("This tutorial demonstrates how to use the API client libraries for the Science Data Kit,")
    print("including both the Python and JavaScript clients. It covers authentication, session management,")
    print("database operations, and error handling.")
    print()

    # Run the examples
    try:
        example_python_low_level_api()
        example_python_high_level_sdk()
        example_javascript_client()
        example_api_best_practices()
    except Exception as e:
        print(f"Error in tutorial: {str(e)}")

    # Clean up
    print("\n=== Cleaning Up ===\n")
    import shutil
    shutil.rmtree(TEMP_DIR)
    print(f"Removed temporary directory: {TEMP_DIR}")
    print()

    print("Tutorial complete!")


if __name__ == "__main__":
    run_tutorial()
