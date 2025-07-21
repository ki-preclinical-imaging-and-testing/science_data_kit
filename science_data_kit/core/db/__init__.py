"""
Database Management Module for Science Data Kit

This package provides database management functionality for the Science Data Kit,
including connection management, query execution, data manipulation, and database optimization.
"""

from .db_manager import (
    Neo4jManager, DatabaseError, ConnectionError,
    load_db_config, update_db_config_auto
)

from .neo4j_config import (
    Neo4jConfigManager, config_manager
)

from .database_connector_base import (
    DatabaseConnectorBase, GraphDatabaseConnector, RelationalDatabaseConnector
)

from .msgraph_neo4j import MSGraphNeo4jIntegration

__all__ = [
    'Neo4jManager', 'DatabaseError', 'ConnectionError',
    'load_db_config', 'update_db_config_auto',
    'Neo4jConfigManager', 'config_manager',
    'DatabaseConnectorBase', 'GraphDatabaseConnector', 'RelationalDatabaseConnector',
    'MSGraphNeo4jIntegration'
]
