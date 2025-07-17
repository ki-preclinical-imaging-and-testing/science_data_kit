"""
Credentials authentication mixin for Science Data Kit connections.

This module provides a mixin that implements username/password credentials
authentication for connections.
"""

from abc import abstractmethod
from typing import Any, Dict, Optional


class CredentialsMixin:
    """Mixin for connections that use username/password credentials."""
    
    def get_credentials(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get the credentials from the configuration.
        
        Args:
            config: Configuration dictionary containing credentials information
            
        Returns:
            Dictionary with username and password
        """
        username = config.get("username")
        password = config.get("password")
        
        if not username or not password:
            raise ValueError("Username or password not found in configuration")
            
        return {
            "username": username,
            "password": password
        }
    
    @abstractmethod
    def authenticate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with the service using credentials.
        
        Args:
            config: Configuration dictionary containing credentials information
            
        Returns:
            Dictionary containing authentication result
        """
        pass
    
    def get_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get authentication headers using the credentials.
        
        Args:
            config: Configuration dictionary containing credentials information
            
        Returns:
            Dictionary of authentication headers
        """
        # This is a default implementation that assumes a token-based auth
        # Implementations should override this method if they use a different approach
        auth_result = config.get("auth_result", {})
        token = auth_result.get("token")
        
        if not token:
            # Try to authenticate if no token is available
            auth_result = self.authenticate(config)
            token = auth_result.get("token")
            
            if not token:
                raise ValueError("Authentication failed: no token available")
                
            # Update config with auth result
            config["auth_result"] = auth_result
            
        header_name = config.get("auth_header", "Authorization")
        header_prefix = config.get("auth_prefix", "Bearer")
        
        if header_prefix:
            return {header_name: f"{header_prefix} {token}"}
        else:
            return {header_name: token}
    
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing credentials information
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Check if we have valid credentials
            self.get_credentials(config)
            
            # Check if we have a valid token
            auth_result = config.get("auth_result", {})
            if auth_result.get("token"):
                return True
                
            # Try to authenticate
            self.authenticate(config)
            return True
        except Exception:
            return False