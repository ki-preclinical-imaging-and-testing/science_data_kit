"""
Session Configuration for Science Data Kit

This module provides functionality for managing session configurations,
including loading, saving, and validating session configurations.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime


class SessionConfigError(Exception):
    """Exception raised for session configuration-related errors."""
    pass


@dataclass
class SessionConfig:
    """
    Class representing a session configuration.
    
    This class stores the configuration for a session, including metadata,
    resources, and connections.
    
    Attributes:
        name: The name of the session.
        description: A description of the session.
        created: The creation timestamp of the session.
        last_modified: The last modification timestamp of the session.
        version: The version of the session configuration format.
        resources: A dictionary of resources in the session.
        connections: A dictionary of connections in the session.
        metadata: Additional metadata for the session.
    """
    name: str
    description: str = ""
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    connections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the session configuration to a dictionary.
        
        Returns:
            A dictionary representation of the session configuration.
        """
        return asdict(self)
    
    def update_last_modified(self) -> None:
        """Update the last_modified timestamp to the current time."""
        self.last_modified = datetime.now().isoformat()
    
    def add_resource(self, resource_id: str, resource_type: str, resource_config: Dict[str, Any]) -> None:
        """
        Add a resource to the session configuration.
        
        Args:
            resource_id: The ID of the resource.
            resource_type: The type of the resource.
            resource_config: The configuration of the resource.
        """
        self.resources[resource_id] = {
            "type": resource_type,
            "config": resource_config
        }
        self.update_last_modified()
    
    def remove_resource(self, resource_id: str) -> None:
        """
        Remove a resource from the session configuration.
        
        Args:
            resource_id: The ID of the resource to remove.
            
        Raises:
            KeyError: If the resource does not exist.
        """
        if resource_id in self.resources:
            del self.resources[resource_id]
            self.update_last_modified()
        else:
            raise KeyError(f"Resource '{resource_id}' not found in session configuration")
    
    def add_connection(self, connection_id: str, connection_type: str, connection_config: Dict[str, Any]) -> None:
        """
        Add a connection to the session configuration.
        
        Args:
            connection_id: The ID of the connection.
            connection_type: The type of the connection.
            connection_config: The configuration of the connection.
        """
        self.connections[connection_id] = {
            "type": connection_type,
            "config": connection_config
        }
        self.update_last_modified()
    
    def remove_connection(self, connection_id: str) -> None:
        """
        Remove a connection from the session configuration.
        
        Args:
            connection_id: The ID of the connection to remove.
            
        Raises:
            KeyError: If the connection does not exist.
        """
        if connection_id in self.connections:
            del self.connections[connection_id]
            self.update_last_modified()
        else:
            raise KeyError(f"Connection '{connection_id}' not found in session configuration")


def load_session_config(config_file: Union[str, Path]) -> SessionConfig:
    """
    Load a session configuration from a file.
    
    Args:
        config_file: Path to the configuration file (YAML or JSON).
        
    Returns:
        A SessionConfig object.
        
    Raises:
        SessionConfigError: If there is an error loading the configuration.
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise SessionConfigError(f"Configuration file not found: {config_file}")
    
    try:
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        # Create a SessionConfig object from the loaded data
        return SessionConfig(**config_data)
    
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise SessionConfigError(f"Error parsing configuration file: {e}")
    except Exception as e:
        raise SessionConfigError(f"Error loading session configuration: {e}")


def save_session_config(config: SessionConfig, config_file: Union[str, Path]) -> None:
    """
    Save a session configuration to a file.
    
    Args:
        config: The SessionConfig object to save.
        config_file: Path to the configuration file (YAML or JSON).
        
    Raises:
        SessionConfigError: If there is an error saving the configuration.
    """
    config_path = Path(config_file)
    
    # Update the last_modified timestamp
    config.update_last_modified()
    
    try:
        # Create parent directories if they don't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert the SessionConfig object to a dictionary
        config_data = config.to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False)
            else:
                json.dump(config_data, f, indent=2)
    
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise SessionConfigError(f"Error serializing configuration: {e}")
    except Exception as e:
        raise SessionConfigError(f"Error saving session configuration: {e}")


def get_default_session_dir() -> Path:
    """
    Get the default directory for storing session configurations.
    
    Returns:
        The default session directory path.
    """
    # Use the user's home directory by default
    home_dir = Path.home()
    session_dir = home_dir / ".science_data_kit" / "sessions"
    
    # Create the directory if it doesn't exist
    session_dir.mkdir(parents=True, exist_ok=True)
    
    return session_dir


def list_available_sessions() -> List[Dict[str, Any]]:
    """
    List all available session configurations in the default session directory.
    
    Returns:
        A list of dictionaries containing session metadata.
    """
    session_dir = get_default_session_dir()
    sessions = []
    
    for file_path in session_dir.glob("*.yaml"):
        try:
            config = load_session_config(file_path)
            sessions.append({
                "name": config.name,
                "description": config.description,
                "created": config.created,
                "last_modified": config.last_modified,
                "file_path": str(file_path)
            })
        except SessionConfigError:
            # Skip invalid session files
            continue
    
    return sessions