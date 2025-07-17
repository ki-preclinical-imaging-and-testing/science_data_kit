"""
Test script for the Dropbox plugin.

This script tests the Dropbox plugin implementation and connection pooling.
"""

import os
import logging
from typing import Dict, Any

from science_data_kit.core.connections.manager import manager, ConnectionPoolConfig
from science_data_kit.plugins.cloud_storage.dropbox import DropboxPlugin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dropbox_plugin():
    """Test the Dropbox plugin."""
    logger.info("Testing Dropbox plugin...")
    
    # Create a plugin instance
    plugin = DropboxPlugin()
    
    # Check plugin properties
    logger.info(f"Plugin name: {plugin.name}")
    logger.info(f"Plugin version: {plugin.version}")
    logger.info(f"Plugin description: {plugin.description}")
    logger.info(f"Plugin capabilities: {plugin.capabilities}")
    
    # Get configuration from environment variables
    config = {
        "app_key": os.environ.get("DROPBOX_APP_KEY"),
        "app_secret": os.environ.get("DROPBOX_APP_SECRET"),
        "refresh_token": os.environ.get("DROPBOX_REFRESH_TOKEN"),
        "root_path": "",
    }
    
    # Validate configuration
    if not plugin.validate_config(config):
        logger.error("Invalid configuration")
        return
    
    # Initialize the plugin
    if not plugin.initialize(config):
        logger.error("Failed to initialize plugin")
        return
    
    logger.info("Plugin initialized successfully")
    
    # Connect to Dropbox
    try:
        plugin.connect(config)
        logger.info("Connected to Dropbox")
    except Exception as e:
        logger.error(f"Failed to connect to Dropbox: {e}")
        return
    
    # Test connection
    if not plugin.test_connection():
        logger.error("Connection test failed")
        return
    
    logger.info("Connection test passed")
    
    # List files in root directory
    try:
        files = plugin.list_directory("/")
        logger.info(f"Files in root directory: {len(files)}")
        for file in files[:5]:  # Show first 5 files
            logger.info(f"  {file['name']} ({'Directory' if file['is_dir'] else 'File'})")
    except Exception as e:
        logger.error(f"Failed to list directory: {e}")
    
    # Disconnect
    plugin.disconnect()
    logger.info("Disconnected from Dropbox")

def test_connection_pooling():
    """Test connection pooling with the Dropbox plugin."""
    logger.info("Testing connection pooling...")
    
    # Configure the connection pool
    pool_config = ConnectionPoolConfig(
        max_pool_size=5,
        min_idle=1,
        max_idle=3,
        idle_timeout=60.0,  # 1 minute
        max_lifetime=300.0,  # 5 minutes
        connection_timeout=10.0,
        validation_interval=30.0,  # 30 seconds
    )
    
    manager.configure_pool("cloud_storage", "dropbox", pool_config)
    
    # Get configuration from environment variables
    config = {
        "app_key": os.environ.get("DROPBOX_APP_KEY"),
        "app_secret": os.environ.get("DROPBOX_APP_SECRET"),
        "refresh_token": os.environ.get("DROPBOX_REFRESH_TOKEN"),
        "root_path": "",
    }
    
    # Get connections from the pool
    connections = []
    for i in range(3):
        logger.info(f"Getting connection {i+1}...")
        connection = manager.get_pooled_connection("cloud_storage", "dropbox", config)
        if connection:
            connections.append(connection)
            logger.info(f"Got connection {i+1}")
        else:
            logger.error(f"Failed to get connection {i+1}")
    
    # Get pool stats
    stats = manager.get_pool_stats("cloud_storage", "dropbox")
    logger.info(f"Pool stats: {stats}")
    
    # Return connections to the pool
    for i, connection in enumerate(connections):
        logger.info(f"Returning connection {i+1}...")
        manager.return_pooled_connection("cloud_storage", "dropbox", connection)
    
    # Get pool stats again
    stats = manager.get_pool_stats("cloud_storage", "dropbox")
    logger.info(f"Pool stats after returning connections: {stats}")
    
    # Close the pool
    manager.close_pool("cloud_storage", "dropbox")
    logger.info("Closed connection pool")

if __name__ == "__main__":
    test_dropbox_plugin()
    test_connection_pooling()