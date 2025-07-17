"""
Test script for the Microsoft 365 plugin.

This script tests the Microsoft 365 plugin implementation and connection pooling.
"""

import os
import logging
from typing import Dict, Any

from science_data_kit.core.connections.manager import manager, ConnectionPoolConfig
from science_data_kit.plugins.cloud_storage.microsoft365 import Microsoft365Plugin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_microsoft365_plugin():
    """Test the Microsoft 365 plugin."""
    logger.info("Testing Microsoft 365 plugin...")
    
    # Create a plugin instance
    plugin = Microsoft365Plugin()
    
    # Check plugin properties
    logger.info(f"Plugin name: {plugin.name}")
    logger.info(f"Plugin version: {plugin.version}")
    logger.info(f"Plugin description: {plugin.description}")
    logger.info(f"Plugin capabilities: {plugin.capabilities}")
    
    # Get configuration from environment variables
    config = {
        "client_id": os.environ.get("MSGRAPH_CLIENT_ID"),
        "tenant_id": os.environ.get("MSGRAPH_TENANT_ID"),
        "client_secret": os.environ.get("MSGRAPH_CLIENT_SECRET"),
        "auth_method": "client_credentials",
        "scopes": ["https://graph.microsoft.com/.default"],
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
    
    # Connect to Microsoft Graph API
    try:
        plugin.connect(config)
        logger.info("Connected to Microsoft Graph API")
    except Exception as e:
        logger.error(f"Failed to connect to Microsoft Graph API: {e}")
        return
    
    # Test connection
    if not plugin.test_connection():
        logger.error("Connection test failed")
        return
    
    logger.info("Connection test passed")
    
    # Test API operations
    try:
        # Get current user info
        me = plugin.get_me()
        logger.info(f"Current user: {me.get('displayName', 'Unknown')}")
        
        # Get users
        users = plugin.get_users()
        logger.info(f"Users: {len(users)}")
        for user in users[:5]:  # Show first 5 users
            logger.info(f"  {user.get('displayName', 'Unknown')} ({user.get('userPrincipalName', 'Unknown')})")
        
        # Get groups
        groups = plugin.get_groups()
        logger.info(f"Groups: {len(groups)}")
        for group in groups[:5]:  # Show first 5 groups
            logger.info(f"  {group.get('displayName', 'Unknown')}")
        
        # Get teams
        teams = plugin.get_teams()
        logger.info(f"Teams: {len(teams)}")
        for team in teams[:5]:  # Show first 5 teams
            logger.info(f"  {team.get('displayName', 'Unknown')}")
            
        # Get SharePoint sites
        sites = plugin.get_sharepoint_sites()
        logger.info(f"SharePoint sites: {len(sites)}")
        for site in sites[:5]:  # Show first 5 sites
            logger.info(f"  {site.get('displayName', 'Unknown')}")
            
        # Get OneDrive files
        files = plugin.get_onedrive_files()
        logger.info(f"OneDrive files: {len(files)}")
        for file in files[:5]:  # Show first 5 files
            logger.info(f"  {file.get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"Failed to test API operations: {e}")
    
    # Disconnect
    plugin.disconnect()
    logger.info("Disconnected from Microsoft Graph API")

def test_connection_pooling():
    """Test connection pooling with the Microsoft 365 plugin."""
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
    
    manager.configure_pool("cloud_storage", "microsoft365", pool_config)
    
    # Get configuration from environment variables
    config = {
        "client_id": os.environ.get("MSGRAPH_CLIENT_ID"),
        "tenant_id": os.environ.get("MSGRAPH_TENANT_ID"),
        "client_secret": os.environ.get("MSGRAPH_CLIENT_SECRET"),
        "auth_method": "client_credentials",
        "scopes": ["https://graph.microsoft.com/.default"],
    }
    
    # Get connections from the pool
    connections = []
    for i in range(3):
        logger.info(f"Getting connection {i+1}...")
        connection = manager.get_pooled_connection("cloud_storage", "microsoft365", config)
        if connection:
            connections.append(connection)
            logger.info(f"Got connection {i+1}")
        else:
            logger.error(f"Failed to get connection {i+1}")
    
    # Get pool stats
    stats = manager.get_pool_stats("cloud_storage", "microsoft365")
    logger.info(f"Pool stats: {stats}")
    
    # Return connections to the pool
    for i, connection in enumerate(connections):
        logger.info(f"Returning connection {i+1}...")
        manager.return_pooled_connection("cloud_storage", "microsoft365", connection)
    
    # Get pool stats again
    stats = manager.get_pool_stats("cloud_storage", "microsoft365")
    logger.info(f"Pool stats after returning connections: {stats}")
    
    # Close the pool
    manager.close_pool("cloud_storage", "microsoft365")
    logger.info("Closed connection pool")

if __name__ == "__main__":
    test_microsoft365_plugin()
    test_connection_pooling()