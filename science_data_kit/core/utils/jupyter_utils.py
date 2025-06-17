"""
Jupyter Utilities for Science Data Kit

This module provides utilities for managing Jupyter Lab containers using Docker.
It includes functions for starting, stopping, and connecting to Jupyter Lab containers.
"""

import os
import time
import socket
import docker
from typing import Optional, Dict, Any, Tuple, Union
from pathlib import Path
from docker.errors import NotFound

# Initialize Docker client
client = docker.from_env()

def is_port_in_use(port: int, host: str = 'localhost') -> bool:
    """
    Check if a port is in use.
    
    Args:
        port: The port number to check.
        host: The host to check the port on.
        
    Returns:
        True if the port is in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

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

def find_free_port(start: int = 8888) -> int:
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

def get_container_port_binding(container: Any, internal_port: str = "8888/tcp") -> Optional[int]:
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

class JupyterManager:
    """
    A manager for Jupyter Lab containers.
    
    This class provides methods for starting, stopping, and connecting to Jupyter Lab containers.
    
    Attributes:
        container_name: The name of the Jupyter container.
        port: The port to use for the Jupyter container.
        token: The token to use for authentication.
        host_mountpoint: The host directory to mount in the container.
    """
    
    def __init__(
        self, 
        container_name: str = "dsk-jupyter-instance", 
        port: int = 8888, 
        token: str = "letmein",
        host_mountpoint: Optional[str] = None
    ):
        """
        Initialize the JupyterManager.
        
        Args:
            container_name: The name of the Jupyter container.
            port: The port to use for the Jupyter container.
            token: The token to use for authentication.
            host_mountpoint: The host directory to mount in the container.
        """
        self.container_name = container_name
        self.port = port
        self.token = token
        self.host_mountpoint = host_mountpoint or os.path.abspath('../')
    
    def start_container(self) -> Tuple[bool, str, Optional[str]]:
        """
        Start a Jupyter Lab container or connect to an existing one.
        
        This method will:
        1. Check if a container with the configured name already exists
        2. If it exists, start it if it's not running and return the URL
        3. If it doesn't exist, create a new container and return the URL
        
        Returns:
            A tuple containing (success, message, url).
            - success: True if the container was started successfully, False otherwise.
            - message: A message describing the result.
            - url: The URL to access Jupyter Lab, or None if there was an error.
        """
        try:
            # Try to get an existing container
            container = client.containers.get(self.container_name)
            bound_port = get_container_port_binding(container)
            
            if not bound_port:
                return False, f"Container '{self.container_name}' exists but has no bound port.", None
            
            # Update the port
            self.port = bound_port
            
            # Get the container IP
            jupyter_host_ip = get_container_ip(container)
            
            # Start the container if it's not running
            if container.status != "running":
                container.start()
                time.sleep(2)  # Give it a moment to start up
                message = f"Started container '{self.container_name}'."
            else:
                message = f"Container '{self.container_name}' is already running."
            
            # Generate the URL
            url = f"http://{jupyter_host_ip}:{bound_port}/?token={self.token}"
            
            return True, message, url
            
        except NotFound:
            # Container does not exist yet — create a new one
            port = find_free_port(self.port)
            self.port = port
            
            # Create and start the container
            try:
                volumes = {}
                if self.host_mountpoint:
                    volumes[self.host_mountpoint] = {
                        "bind": "/home/jovyan/work",
                        "mode": "rw"
                    }
                
                container = client.containers.run(
                    "jupyter/base-notebook",
                    name=self.container_name,
                    ports={"8888/tcp": port},
                    environment={"JUPYTER_TOKEN": self.token},
                    volumes=volumes,
                    detach=True,
                    tty=True,
                )
                
                # Get the container IP
                jupyter_host_ip = get_container_ip(container)
                time.sleep(2)  # Give it a moment to start up
                
                # Generate the URL
                url = f"http://{jupyter_host_ip}:{port}/?token={self.token}"
                
                return True, f"Started new Jupyter container on port {port}.", url
                
            except Exception as e:
                return False, f"Failed to start Jupyter container: {e}", None
                
        except Exception as e:
            return False, f"Error handling Jupyter container: {e}", None
    
    def stop_container(self) -> Tuple[bool, str]:
        """
        Stop the Jupyter container.
        
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
        Get the status of the Jupyter container.
        
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

# Convenience functions that use the JupyterManager class

def start_jupyter_container(
    container_name: str = "dsk-jupyter-instance", 
    port: int = 8888, 
    token: str = "letmein",
    host_mountpoint: Optional[str] = None
) -> Tuple[bool, str, Optional[str]]:
    """
    Start a Jupyter Lab container or connect to an existing one.
    
    Args:
        container_name: The name of the Jupyter container.
        port: The port to use for the Jupyter container.
        token: The token to use for authentication.
        host_mountpoint: The host directory to mount in the container.
        
    Returns:
        A tuple containing (success, message, url).
        - success: True if the container was started successfully, False otherwise.
        - message: A message describing the result.
        - url: The URL to access Jupyter Lab, or None if there was an error.
    """
    manager = JupyterManager(container_name, port, token, host_mountpoint)
    return manager.start_container()

def stop_jupyter_container(container_name: str = "dsk-jupyter-instance") -> Tuple[bool, str]:
    """
    Stop the Jupyter container.
    
    Args:
        container_name: The name of the Jupyter container.
        
    Returns:
        A tuple containing (success, message).
        - success: True if the container was stopped successfully, False otherwise.
        - message: A message describing the result.
    """
    manager = JupyterManager(container_name)
    return manager.stop_container()

def get_jupyter_container_status(container_name: str = "dsk-jupyter-instance") -> Tuple[bool, str]:
    """
    Get the status of the Jupyter container.
    
    Args:
        container_name: The name of the Jupyter container.
        
    Returns:
        A tuple containing (exists, status).
        - exists: True if the container exists, False otherwise.
        - status: The status of the container, or "not found" if it doesn't exist.
    """
    manager = JupyterManager(container_name)
    return manager.get_container_status()