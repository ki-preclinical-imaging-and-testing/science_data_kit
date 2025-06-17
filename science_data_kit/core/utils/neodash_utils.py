"""
NeoDash Utilities for Science Data Kit

This module provides utilities for managing NeoDash containers using Docker.
It includes functions for starting, stopping, and connecting to NeoDash containers.
"""

import time
import socket
import docker
from typing import Optional, Dict, Any, Tuple, Union
from docker.errors import NotFound

# Initialize Docker client
client = docker.from_env()

def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: The port number to check.
        host: The host to check the port on.
        
    Returns:
        True if the port is available, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def find_free_port(start: int = 5005) -> int:
    """
    Find a free port starting from the given port number.
    
    Args:
        start: The port number to start searching from.
        
    Returns:
        A free port number.
    """
    port = start
    while not is_port_available(port):
        port += 1
    return port

def get_container_port_binding(container: Any, internal_port: str = "5005/tcp") -> Optional[int]:
    """
    Get the port binding for a container.
    
    Args:
        container: The Docker container object.
        internal_port: The internal port to get the binding for.
        
    Returns:
        The port number if found, None otherwise.
    """
    try:
        return int(container.attrs["HostConfig"]["PortBindings"][internal_port][0]["HostPort"])
    except (KeyError, IndexError, TypeError):
        return None

def get_container_ip(container: Any) -> str:
    """
    Get the IP address of a container.
    
    Args:
        container: The Docker container object.
        
    Returns:
        The IP address of the container, or "localhost" if not available.
    """
    return container.attrs["NetworkSettings"]["IPAddress"] or "localhost"

class NeoDashManager:
    """
    A manager for NeoDash containers.
    
    This class provides methods for starting, stopping, and connecting to NeoDash containers.
    
    Attributes:
        container_name: The name of the NeoDash container.
        port: The port to use for the NeoDash container.
        neo4j_uri: The URI of the Neo4j database to connect to.
        neo4j_user: The username for the Neo4j database.
        neo4j_password: The password for the Neo4j database.
    """
    
    def __init__(
        self, 
        container_name: str = "dsk-neodash-instance", 
        port: int = 5005, 
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "neo4jiscool"
    ):
        """
        Initialize the NeoDashManager.
        
        Args:
            container_name: The name of the NeoDash container.
            port: The port to use for the NeoDash container.
            neo4j_uri: The URI of the Neo4j database to connect to.
            neo4j_user: The username for the Neo4j database.
            neo4j_password: The password for the Neo4j database.
        """
        self.container_name = container_name
        self.port = port
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
    
    def start_container(self) -> Tuple[bool, str, Optional[str]]:
        """
        Start a NeoDash container or connect to an existing one.
        
        This method will:
        1. Check if a container with the configured name already exists
        2. If it exists, start it if it's not running and return the URL
        3. If it doesn't exist, create a new container and return the URL
        
        Returns:
            A tuple containing (success, message, url).
            - success: True if the container was started successfully, False otherwise.
            - message: A message describing the result.
            - url: The URL to access NeoDash, or None if there was an error.
        """
        try:
            # Try to get an existing container
            container = client.containers.get(self.container_name)
            bound_port = get_container_port_binding(container)
            
            if not bound_port:
                return False, f"Container '{self.container_name}' exists but has no bound port.", None
            
            # Update the port
            self.port = bound_port
            
            # Start the container if it's not running
            if container.status != "running":
                container.start()
                time.sleep(2)  # Give it a moment to start up
                message = f"Started container '{self.container_name}'."
            else:
                message = f"Container '{self.container_name}' is already running."
            
            # Get the container IP
            neodash_host_ip = get_container_ip(container)
            
            # Generate the URL
            url = f"http://{neodash_host_ip}:{bound_port}"
            
            return True, message, url
            
        except NotFound:
            # Container does not exist yet — create a new one
            port = find_free_port(self.port)
            self.port = port
            
            # Create and start the container
            try:
                container = client.containers.run(
                    "neo4jlabs/neodash:latest",
                    name=self.container_name,
                    ports={"5005/tcp": port},
                    environment={
                        "NEO4J_URI": self.neo4j_uri,
                        "NEO4J_USER": self.neo4j_user,
                        "NEO4J_PASSWORD": self.neo4j_password
                    },
                    detach=True,
                    tty=True,
                )
                
                # Get the container IP
                neodash_host_ip = get_container_ip(container)
                time.sleep(2)  # Give it a moment to start up
                
                # Generate the URL
                url = f"http://{neodash_host_ip}:{port}"
                
                return True, f"Started new NeoDash container on port {port}.", url
                
            except Exception as e:
                return False, f"Failed to start NeoDash container: {e}", None
                
        except Exception as e:
            return False, f"Error handling NeoDash container: {e}", None
    
    def stop_container(self) -> Tuple[bool, str]:
        """
        Stop the NeoDash container.
        
        Returns:
            A tuple containing (success, message).
            - success: True if the container was stopped successfully, False otherwise.
            - message: A message describing the result.
        """
        try:
            container = client.containers.get(self.container_name)
            if container.status == "running":
                container.stop()
                return True, f"Stopped container '{self.container_name}'."
            else:
                return False, f"Container '{self.container_name}' is not running."
        except NotFound:
            return False, f"Container '{self.container_name}' not found."
        except Exception as e:
            return False, f"Error stopping container: {e}"
    
    def get_container_status(self) -> Tuple[bool, str]:
        """
        Get the status of the NeoDash container.
        
        Returns:
            A tuple containing (exists, status).
            - exists: True if the container exists, False otherwise.
            - status: The status of the container, or "not found" if it doesn't exist.
        """
        try:
            container = client.containers.get(self.container_name)
            return True, container.status
        except NotFound:
            return False, "not found"
        except Exception:
            return False, "error"

# Convenience functions that use the NeoDashManager class

def start_neodash_container(
    container_name: str = "dsk-neodash-instance", 
    port: int = 5005, 
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "neo4jiscool"
) -> Tuple[bool, str, Optional[str]]:
    """
    Start a NeoDash container or connect to an existing one.
    
    Args:
        container_name: The name of the NeoDash container.
        port: The port to use for the NeoDash container.
        neo4j_uri: The URI of the Neo4j database to connect to.
        neo4j_user: The username for the Neo4j database.
        neo4j_password: The password for the Neo4j database.
        
    Returns:
        A tuple containing (success, message, url).
        - success: True if the container was started successfully, False otherwise.
        - message: A message describing the result.
        - url: The URL to access NeoDash, or None if there was an error.
    """
    manager = NeoDashManager(container_name, port, neo4j_uri, neo4j_user, neo4j_password)
    return manager.start_container()

def stop_neodash_container(container_name: str = "dsk-neodash-instance") -> Tuple[bool, str]:
    """
    Stop the NeoDash container.
    
    Args:
        container_name: The name of the NeoDash container.
        
    Returns:
        A tuple containing (success, message).
        - success: True if the container was stopped successfully, False otherwise.
        - message: A message describing the result.
    """
    manager = NeoDashManager(container_name)
    return manager.stop_container()

def get_neodash_container_status(container_name: str = "dsk-neodash-instance") -> Tuple[bool, str]:
    """
    Get the status of the NeoDash container.
    
    Args:
        container_name: The name of the NeoDash container.
        
    Returns:
        A tuple containing (exists, status).
        - exists: True if the container exists, False otherwise.
        - status: The status of the container, or "not found" if it doesn't exist.
    """
    manager = NeoDashManager(container_name)
    return manager.get_container_status()