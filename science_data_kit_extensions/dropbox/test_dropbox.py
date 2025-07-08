"""
Science Data Kit - Dropbox Extension
Test Script

This script demonstrates the basic functionality of the Dropbox extension.
It can be used to verify that the implementation works correctly.

Usage:
    python -m science_data_kit_extensions.dropbox.test_dropbox

Environment variables:
    DROPBOX_APP_KEY: Dropbox API app key
    DROPBOX_APP_SECRET: Dropbox API app secret
    DROPBOX_REFRESH_TOKEN: OAuth2 refresh token for authentication
    NEO4J_URI: Neo4j database URI (default: bolt://localhost:7687)
    NEO4J_USER: Neo4j database username (default: neo4j)
    NEO4J_PASSWORD: Neo4j database password (default: password)
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List

from science_data_kit.core.database import DatabaseManager

from science_data_kit_extensions.dropbox import (
    DropboxConnector,
    DropboxFileManager,
    DropboxNeo4jIntegration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_authentication():
    """Test authentication with Dropbox API."""
    logger.info("Testing Dropbox authentication...")
    
    # Get credentials from environment variables
    app_key = os.environ.get("DROPBOX_APP_KEY")
    app_secret = os.environ.get("DROPBOX_APP_SECRET")
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")
    
    if not app_key or not app_secret:
        logger.error("Missing Dropbox API credentials. Set DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables.")
        return False
    
    try:
        # Initialize connector
        connector = DropboxConnector(
            app_key=app_key,
            app_secret=app_secret,
            refresh_token=refresh_token
        )
        
        # If no refresh token is available, start OAuth flow
        if not refresh_token:
            auth_url = connector.authenticate()
            logger.info(f"Please visit this URL to authorize the application: {auth_url}")
            auth_code = input("Enter the authorization code: ")
            
            if connector.complete_authentication(auth_code):
                logger.info(f"Authentication successful. Refresh token: {connector.refresh_token}")
                logger.info("Save this token as DROPBOX_REFRESH_TOKEN environment variable for future use.")
            else:
                logger.error("Authentication failed.")
                return False
        
        # Test connection
        if connector.is_connected():
            account_info = connector.get_account_info()
            logger.info(f"Connected to Dropbox as {account_info['name']} ({account_info['email']})")
            return True
        else:
            logger.error("Connection test failed.")
            return False
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False

def test_file_operations(connector: DropboxConnector):
    """Test basic file operations."""
    logger.info("Testing file operations...")
    
    try:
        # Initialize file manager
        file_manager = DropboxFileManager(connector)
        
        # List files in root folder
        logger.info("Listing files in root folder...")
        items = file_manager.list_folder("/", limit=10)
        
        if not items:
            logger.info("No files found in root folder.")
        else:
            logger.info(f"Found {len(items)} items in root folder:")
            for item in items:
                item_type = item.get('type', 'unknown')
                name = item.get('name', 'unnamed')
                path = item.get('path', '')
                logger.info(f"  {item_type.upper()}: {name} ({path})")
        
        return True
        
    except Exception as e:
        logger.error(f"File operations error: {e}")
        return False

def test_neo4j_integration(connector: DropboxConnector):
    """Test Neo4j integration."""
    logger.info("Testing Neo4j integration...")
    
    # Get Neo4j credentials from environment variables
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Connect to Neo4j
        logger.info(f"Connecting to Neo4j at {neo4j_uri}...")
        if not db_manager.connect_to_neo4j(uri=neo4j_uri, username=neo4j_user, password=neo4j_password):
            logger.error("Failed to connect to Neo4j.")
            return False
            
        logger.info("Connected to Neo4j.")
        
        # Initialize file manager
        file_manager = DropboxFileManager(connector)
        
        # Initialize Neo4j integration
        neo4j_integration = DropboxNeo4jIntegration(db_manager)
        
        # Import a small folder for testing
        folder_path = "/"  # Use root folder or specify a small folder
        logger.info(f"Importing folder contents from {folder_path}...")
        
        # List only a few items to avoid importing too much data
        items = file_manager.list_folder(folder_path, limit=5)
        
        if not items:
            logger.info("No items found in the folder.")
            return True
            
        # Create entities
        from science_data_kit_extensions.dropbox import create_entities_from_dropbox_items
        entities = create_entities_from_dropbox_items(items)
        
        # Import entities to Neo4j
        for entity in entities:
            logger.info(f"Importing {entity.entity_type}: {entity.name}...")
            node_id = neo4j_integration.import_dropbox_entity(entity)
            logger.info(f"Imported as Neo4j node {node_id}")
        
        # Get Cypher templates
        templates = neo4j_integration.get_cypher_templates()
        logger.info(f"Available Cypher templates: {', '.join(templates.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"Neo4j integration error: {e}")
        return False
    finally:
        # Disconnect from Neo4j
        if 'db_manager' in locals() and db_manager.is_connected():
            db_manager.disconnect()
            logger.info("Disconnected from Neo4j.")

def main():
    """Main test function."""
    logger.info("Starting Dropbox extension tests...")
    
    # Test authentication
    if not test_authentication():
        logger.error("Authentication test failed. Exiting.")
        return 1
        
    # Get credentials from environment variables
    app_key = os.environ.get("DROPBOX_APP_KEY")
    app_secret = os.environ.get("DROPBOX_APP_SECRET")
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")
    
    # Initialize connector
    connector = DropboxConnector(
        app_key=app_key,
        app_secret=app_secret,
        refresh_token=refresh_token
    )
    
    # Test file operations
    if not test_file_operations(connector):
        logger.error("File operations test failed.")
    
    # Test Neo4j integration
    if not test_neo4j_integration(connector):
        logger.error("Neo4j integration test failed.")
    
    logger.info("Tests completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())