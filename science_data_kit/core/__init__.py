"""
Core Module for Science Data Kit

This package provides the core functionality for the Science Data Kit,
including database management, session management, and ontology integration.
"""

# Import and expose session management
from .session import (
    Session, create_session, load_session, list_sessions,
    Resource, ResourceRegistry
)

# Import and expose database management
from .db import (
    Neo4jManager, DatabaseError, ConnectionError,
    load_db_config, update_db_config_auto
)

# Import and expose ontology integration
from .ontology import (
    OntologyImporter, OntologyBrowser,
    OntologySource, OntologyAnnotation
)

__all__ = [
    # Session management
    'Session', 'create_session', 'load_session', 'list_sessions',
    'Resource', 'ResourceRegistry',
    
    # Database management
    'Neo4jManager', 'DatabaseError', 'ConnectionError',
    'load_db_config', 'update_db_config_auto',
    
    # Ontology integration
    'OntologyImporter', 'OntologyBrowser',
    'OntologySource', 'OntologyAnnotation'
]
