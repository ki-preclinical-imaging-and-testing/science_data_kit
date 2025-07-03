"""
Example Usage of the Science Data Kit API Client Library

This script demonstrates how to use the Python client library for the Science Data Kit API.
It shows common operations such as authentication, session management, and database queries.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path to import the client module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client import APIClient, SDKClient, APIClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_low_level_api():
    """Example using the low-level APIClient."""
    logger.info("=== Low-Level API Client Example ===")
    
    # Initialize the client
    client = APIClient(base_url="http://localhost:8000")
    
    try:
        # Login
        logger.info("Logging in...")
        login_response = client.login(user_id="example_user")
        logger.info(f"Login successful: {login_response}")
        
        # Get session information
        logger.info("Getting session information...")
        session_info = client.get_session()
        logger.info(f"Session info: {session_info}")
        
        # Execute a query
        logger.info("Executing a query...")
        query_result = client.execute_query(
            query="MATCH (n) RETURN n LIMIT 10",
            params={}
        )
        logger.info(f"Query result: {query_result}")
        
        # Create a new session
        logger.info("Creating a new session...")
        new_session = client.create_session({
            "name": "Example Session",
            "description": "A session created from the API client example"
        })
        logger.info(f"New session: {new_session}")
        
        # Update the session
        logger.info("Updating the session...")
        updated_session = client.update_session({
            "name": "Updated Example Session",
            "description": "An updated session description"
        })
        logger.info(f"Updated session: {updated_session}")
        
        # Get database information
        logger.info("Getting database information...")
        db_info = client.get_database_info()
        logger.info(f"Database info: {db_info}")
        
        # Create a new database
        logger.info("Creating a new database...")
        new_db = client.create_database({
            "name": "example_db",
            "description": "An example database"
        })
        logger.info(f"New database: {new_db}")
        
        # Delete the session
        logger.info("Deleting the session...")
        delete_session_result = client.delete_session()
        logger.info(f"Delete session result: {delete_session_result}")
        
        # Logout
        logger.info("Logging out...")
        logout_result = client.logout()
        logger.info(f"Logout result: {logout_result}")
        
    except APIClientError as e:
        logger.error(f"API error: {e.message}")
        if e.status_code:
            logger.error(f"Status code: {e.status_code}")
        if e.response:
            logger.error(f"Response: {e.response}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


def example_high_level_sdk():
    """Example using the high-level SDKClient."""
    logger.info("=== High-Level SDK Client Example ===")
    
    try:
        # Initialize the client with automatic login
        logger.info("Initializing SDK client with automatic login...")
        client = SDKClient(
            base_url="http://localhost:8000",
            user_id="example_user"
        )
        
        # Get user information
        logger.info("Getting user information...")
        user_info = client.get_user_info()
        logger.info(f"User info: {user_info}")
        
        # Execute a simple query
        logger.info("Executing a simple query...")
        results = client.query("MATCH (n) RETURN n.name, n.type LIMIT 5")
        logger.info(f"Query results: {results}")
        
        # Create a session with a database
        logger.info("Creating a session with a database...")
        session = client.create_session_with_database(
            session_name="Example SDK Session",
            database_name="example_sdk_db"
        )
        logger.info(f"Created session: {session}")
        
        # Execute a parameterized query
        logger.info("Executing a parameterized query...")
        param_results = client.query(
            "MATCH (n) WHERE n.type = $type RETURN n.name, n.created_at LIMIT 10",
            params={"type": "Person"}
        )
        logger.info(f"Parameterized query results: {param_results}")
        
        # Logout
        logger.info("Logging out...")
        logout_result = client.logout()
        logger.info(f"Logout result: {logout_result}")
        
    except APIClientError as e:
        logger.error(f"API error: {e.message}")
        if e.status_code:
            logger.error(f"Status code: {e.status_code}")
        if e.response:
            logger.error(f"Response: {e.response}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


def main():
    """Run the examples."""
    try:
        # Run the low-level API client example
        example_low_level_api()
        
        print("\n" + "="*50 + "\n")
        
        # Run the high-level SDK client example
        example_high_level_sdk()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()