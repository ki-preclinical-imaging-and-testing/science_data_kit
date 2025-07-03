"""
Configuration Utilities for Science Data Kit

This module provides utilities for saving and loading configuration data
for various connections and services in the Science Data Kit.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import streamlit as st

# Default configuration directory
CONFIG_DIR = Path.home() / ".science_data_kit" / "config"

def ensure_config_dir() -> None:
    """
    Ensure the configuration directory exists.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_connections_config(config: Dict[str, Any], filename: str = "connections.yaml") -> bool:
    """
    Save connections configuration to a YAML file.

    Args:
        config: Dictionary containing the connections configuration.
        filename: Name of the YAML file to save to.

    Returns:
        True if the configuration was saved successfully, False otherwise.
    """
    try:
        ensure_config_dir()
        config_path = CONFIG_DIR / filename
        
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        return True
    except Exception as e:
        print(f"Error saving connections configuration: {e}")
        return False

def load_connections_config(filename: str = "connections.yaml") -> Dict[str, Any]:
    """
    Load connections configuration from a YAML file.

    Args:
        filename: Name of the YAML file to load from.

    Returns:
        Dictionary containing the connections configuration, or an empty dict if the file doesn't exist.
    """
    try:
        config_path = CONFIG_DIR / filename
        
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        return config or {}
    except Exception as e:
        print(f"Error loading connections configuration: {e}")
        return {}

def save_all_connections() -> bool:
    """
    Save all connection configurations from session state to YAML files.

    Returns:
        True if all configurations were saved successfully, False otherwise.
    """
    success = True
    
    # Save Neo4j connections
    if "db_connections" in st.session_state:
        neo4j_config = {
            "connections": st.session_state["db_connections"],
            "active_connection": st.session_state.get("active_connection")
        }
        if not save_connections_config(neo4j_config, "neo4j_connections.yaml"):
            success = False
    
    # Save PostgreSQL connections
    if "pg_connections" in st.session_state:
        pg_config = {
            "connections": st.session_state["pg_connections"],
            "active_connection": st.session_state.get("pg_active_connection")
        }
        if not save_connections_config(pg_config, "postgresql_connections.yaml"):
            success = False
    
    # Save Ollama configuration
    ollama_config = {
        "container_name": st.session_state.get("ollama_container_name", "dsk-ollama-instance"),
        "port": st.session_state.get("ollama_port", 11434),
        "version": st.session_state.get("ollama_version", "latest"),
        "url": st.session_state.get("ollama_url", "http://localhost:11434")
    }
    if not save_connections_config(ollama_config, "ollama_config.yaml"):
        success = False
    
    # Save Jupyter configuration
    jupyter_config = {
        "container_name": st.session_state.get("jupyter_container_name", "dsk-jupyter-instance"),
        "url": st.session_state.get("jupyter_url", ""),
        "token": st.session_state.get("jupyter_token", ""),
        "mode": st.session_state.get("jupyter_mode", "Single-user")
    }
    if not save_connections_config(jupyter_config, "jupyter_config.yaml"):
        success = False
    
    # Save NeoDash configuration
    neodash_config = {
        "url": st.session_state.get("neodash_url", "")
    }
    if not save_connections_config(neodash_config, "neodash_config.yaml"):
        success = False
    
    return success

def load_all_connections() -> bool:
    """
    Load all connection configurations from YAML files to session state.

    Returns:
        True if all configurations were loaded successfully, False otherwise.
    """
    success = True
    
    # Load Neo4j connections
    neo4j_config = load_connections_config("neo4j_connections.yaml")
    if neo4j_config:
        st.session_state["db_connections"] = neo4j_config.get("connections", {})
        if "active_connection" in neo4j_config:
            st.session_state["active_connection"] = neo4j_config["active_connection"]
    else:
        if "db_connections" not in st.session_state:
            st.session_state["db_connections"] = {}
        success = False
    
    # Load PostgreSQL connections
    pg_config = load_connections_config("postgresql_connections.yaml")
    if pg_config:
        st.session_state["pg_connections"] = pg_config.get("connections", {})
        if "active_connection" in pg_config:
            st.session_state["pg_active_connection"] = pg_config["active_connection"]
    else:
        if "pg_connections" not in st.session_state:
            st.session_state["pg_connections"] = {}
        success = False
    
    # Load Ollama configuration
    ollama_config = load_connections_config("ollama_config.yaml")
    if ollama_config:
        st.session_state["ollama_container_name"] = ollama_config.get("container_name", "dsk-ollama-instance")
        st.session_state["ollama_port"] = ollama_config.get("port", 11434)
        st.session_state["ollama_version"] = ollama_config.get("version", "latest")
        st.session_state["ollama_url"] = ollama_config.get("url", "http://localhost:11434")
    else:
        success = False
    
    # Load Jupyter configuration
    jupyter_config = load_connections_config("jupyter_config.yaml")
    if jupyter_config:
        st.session_state["jupyter_container_name"] = jupyter_config.get("container_name", "dsk-jupyter-instance")
        st.session_state["jupyter_url"] = jupyter_config.get("url", "")
        st.session_state["jupyter_token"] = jupyter_config.get("token", "")
        st.session_state["jupyter_mode"] = jupyter_config.get("mode", "Single-user")
    else:
        success = False
    
    # Load NeoDash configuration
    neodash_config = load_connections_config("neodash_config.yaml")
    if neodash_config:
        st.session_state["neodash_url"] = neodash_config.get("url", "")
    else:
        success = False
    
    return success