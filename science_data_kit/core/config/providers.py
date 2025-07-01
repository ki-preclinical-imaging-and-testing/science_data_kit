"""
Provider Configuration for Science Data Kit

This module provides configuration management for data source providers,
including loading configuration from environment variables and configuration files.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


def load_provider_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load provider configuration from environment variables and/or a configuration file.
    
    Args:
        config_file: Optional path to a JSON configuration file
        
    Returns:
        Dictionary containing provider configuration
    """
    config = {}
    
    # Load from configuration file if provided
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading provider configuration from file: {str(e)}")
    
    # Load from environment variables
    _load_from_env(config)
    
    return config


def _load_from_env(config: Dict[str, Any]) -> None:
    """
    Load provider configuration from environment variables.
    
    This function updates the provided config dictionary with values from environment variables.
    
    Args:
        config: Configuration dictionary to update
    """
    # Dropbox configuration
    if os.getenv("DROPBOX_ACCESS_TOKEN"):
        config.setdefault("storage", {}).setdefault("dropbox", {})["access_token"] = \
            os.getenv("DROPBOX_ACCESS_TOKEN")
    
    # Google Sheets configuration
    if os.getenv("GOOGLE_CREDENTIALS_FILE"):
        config.setdefault("storage", {}).setdefault("google_sheets", {})["credentials_file"] = \
            os.getenv("GOOGLE_CREDENTIALS_FILE")
    
    if os.getenv("GOOGLE_CLIENT_ID"):
        config.setdefault("storage", {}).setdefault("google_sheets", {})["client_id"] = \
            os.getenv("GOOGLE_CLIENT_ID")
    
    if os.getenv("GOOGLE_CLIENT_SECRET"):
        config.setdefault("storage", {}).setdefault("google_sheets", {})["client_secret"] = \
            os.getenv("GOOGLE_CLIENT_SECRET")
    
    if os.getenv("GOOGLE_TOKEN_FILE"):
        config.setdefault("storage", {}).setdefault("google_sheets", {})["token_file"] = \
            os.getenv("GOOGLE_TOKEN_FILE")
    
    # Microsoft Graph configuration (for reference, already implemented elsewhere)
    if os.getenv("MSGRAPH_TENANT_ID"):
        config.setdefault("api", {}).setdefault("msgraph", {})["tenant_id"] = \
            os.getenv("MSGRAPH_TENANT_ID")
    
    if os.getenv("MSGRAPH_CLIENT_ID"):
        config.setdefault("api", {}).setdefault("msgraph", {})["client_id"] = \
            os.getenv("MSGRAPH_CLIENT_ID")
    
    if os.getenv("MSGRAPH_CLIENT_SECRET"):
        config.setdefault("api", {}).setdefault("msgraph", {})["client_secret"] = \
            os.getenv("MSGRAPH_CLIENT_SECRET")
    
    if os.getenv("MSGRAPH_AUTH_METHOD"):
        config.setdefault("api", {}).setdefault("msgraph", {})["auth_method"] = \
            os.getenv("MSGRAPH_AUTH_METHOD")