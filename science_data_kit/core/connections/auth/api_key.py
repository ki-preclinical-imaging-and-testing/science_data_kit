"""
API Key authentication mixin for Science Data Kit connections.

This module provides a mixin that implements API key authentication for connections.
"""

from typing import Any, Dict, Optional


class APIKeyMixin:
    """Mixin for connections that use API key authentication."""
    
    def get_api_key(self, config: Dict[str, Any]) -> str:
        """
        Get the API key from the configuration.
        
        Args:
            config: Configuration dictionary containing API key information
            
        Returns:
            API key as a string
        """
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("API key not found in configuration")
        return api_key
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers using the API key.
        
        Args:
            config: Configuration dictionary containing API key information
            
        Returns:
            Dictionary of authentication headers
        """
        api_key = self.get_api_key(config)
        header_name = config.get("api_key_header", "Authorization")
        header_prefix = config.get("api_key_prefix", "Bearer")
        
        if header_prefix:
            return {header_name: f"{header_prefix} {api_key}"}
        else:
            return {header_name: api_key}
    
    def get_auth_params(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication query parameters using the API key.
        
        Args:
            config: Configuration dictionary containing API key information
            
        Returns:
            Dictionary of authentication query parameters
        """
        if config.get("api_key_in_params", False):
            api_key = self.get_api_key(config)
            param_name = config.get("api_key_param_name", "api_key")
            return {param_name: api_key}
        return {}
    
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing API key information
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            self.get_api_key(config)
            return True
        except ValueError:
            return False