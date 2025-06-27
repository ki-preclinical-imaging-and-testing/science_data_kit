"""
Database Factory for Science Data Kit

This module provides a factory for creating database connections,
allowing the Science Data Kit to work with different database types.
"""

from typing import Dict, Any, Optional, Union

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter


class DatabaseFactory:
    """
    Factory for creating database connections.
    
    This class provides methods for creating and managing connections to
    different types of databases, including Neo4j and Microsoft Graph API.
    """
    
    @staticmethod
    def create_connection(db_type: str, config: Optional[Dict[str, Any]] = None, config_file: Optional[str] = None) -> Union[Neo4jManager, MSGraphAdapter]:
        """
        Create a connection to a database.
        
        Args:
            db_type: The type of database to connect to. Options are:
                - "neo4j": Connect to a Neo4j database
                - "msgraph": Connect to Microsoft Graph API
            config: Optional configuration dictionary.
            config_file: Optional path to a configuration file.
            
        Returns:
            A database connection manager or adapter.
            
        Raises:
            ValueError: If the database type is not supported.
        """
        if db_type == "neo4j":
            return Neo4jManager(config=config, config_file=config_file)
        elif db_type == "msgraph":
            # Extract Microsoft Graph API configuration
            if config:
                tenant_id = config.get("tenant_id")
                client_id = config.get("client_id")
                client_secret = config.get("client_secret")
                auth_method = config.get("auth_method", "device_code")
                
                # Create connection manager
                connection_manager = MSGraphConnectionManager(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret,
                    auth_method=auth_method,
                    config_file=config_file
                )
                
                # Create adapter
                return MSGraphAdapter(connection_manager=connection_manager)
            else:
                # Create adapter with config file
                return MSGraphAdapter(config_file=config_file)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def get_supported_db_types() -> Dict[str, str]:
        """
        Get a dictionary of supported database types.
        
        Returns:
            A dictionary mapping database type codes to human-readable names.
        """
        return {
            "neo4j": "Neo4j Graph Database",
            "msgraph": "Microsoft Graph API"
        }