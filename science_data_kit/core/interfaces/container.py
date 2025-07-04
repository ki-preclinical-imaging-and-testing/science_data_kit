"""
Container Interfaces for Science Data Kit

This module defines interfaces for container managers,
providing a standardized way to interact with different container systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, Tuple


class ContainerInterface(ABC):
    """
    Abstract base class for container interfaces.
    
    This interface defines the core methods that all container managers should implement,
    regardless of the specific container technology they interact with.
    """
    
    @abstractmethod
    def start_container(self) -> bool:
        """
        Start the container.
        
        Returns:
            True if container was started successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def stop_container(self) -> bool:
        """
        Stop the container.
        
        Returns:
            True if container was stopped successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the container.
        
        Returns:
            Dictionary containing container status information.
        """
        pass


class JupyterContainerInterface(ContainerInterface):
    """
    Interface for Jupyter container managers.
    
    This interface extends the base ContainerInterface with methods specific to Jupyter containers.
    """
    
    @abstractmethod
    def get_jupyter_url(self) -> str:
        """
        Get the URL for accessing the Jupyter notebook.
        
        Returns:
            URL string for accessing the Jupyter notebook.
        """
        pass
    
    @abstractmethod
    def get_token(self) -> str:
        """
        Get the authentication token for the Jupyter notebook.
        
        Returns:
            Authentication token string.
        """
        pass


class NeoDashContainerInterface(ContainerInterface):
    """
    Interface for NeoDash container managers.
    
    This interface extends the base ContainerInterface with methods specific to NeoDash containers.
    """
    
    @abstractmethod
    def get_neodash_url(self) -> str:
        """
        Get the URL for accessing the NeoDash dashboard.
        
        Returns:
            URL string for accessing the NeoDash dashboard.
        """
        pass
    
    @abstractmethod
    def set_neo4j_connection(self, uri: str, username: str, password: str) -> bool:
        """
        Set the Neo4j connection details for the NeoDash container.
        
        Args:
            uri: Neo4j connection URI.
            username: Neo4j username.
            password: Neo4j password.
            
        Returns:
            True if connection details were set successfully, False otherwise.
        """
        pass