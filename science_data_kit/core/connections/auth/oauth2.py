"""
OAuth2 authentication mixin for Science Data Kit connections.

This module provides a mixin that implements OAuth2 authentication for connections.
"""

import time
from abc import abstractmethod
from typing import Any, Dict, Optional


class OAuth2Mixin:
    """Mixin for connections that use OAuth2 authentication."""
    
    @abstractmethod
    def get_auth_url(self) -> str:
        """
        Get the authorization URL for OAuth2 authentication.
        
        Returns:
            Authorization URL as a string
        """
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for an access token.
        
        Args:
            code: Authorization code from the OAuth2 flow
            
        Returns:
            Dictionary containing token information
        """
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token from a previous authentication
            
        Returns:
            Dictionary containing new token information
        """
        pass
    
    def get_valid_token(self, config: Dict[str, Any]) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            config: Configuration dictionary containing token information
            
        Returns:
            Valid access token as a string
        """
        token_info = config.get("token_info", {})
        
        # Check if token exists and is still valid
        if token_info and "access_token" in token_info:
            # Check if token is expired
            expires_at = token_info.get("expires_at", 0)
            if expires_at > time.time() + 60:  # 60 seconds buffer
                return token_info["access_token"]
            
            # Token is expired, try to refresh
            if "refresh_token" in token_info:
                try:
                    new_token_info = self.refresh_token(token_info["refresh_token"])
                    # Update expiration time if not provided
                    if "expires_at" not in new_token_info and "expires_in" in new_token_info:
                        new_token_info["expires_at"] = time.time() + new_token_info["expires_in"]
                    
                    # Update config with new token info
                    config["token_info"] = new_token_info
                    return new_token_info["access_token"]
                except Exception as e:
                    raise ValueError(f"Failed to refresh token: {e}")
        
        # No valid token available
        raise ValueError("No valid access token available. Authentication required.")
    
    def is_authenticated(self, config: Dict[str, Any]) -> bool:
        """
        Check if the connection is authenticated.
        
        Args:
            config: Configuration dictionary containing token information
            
        Returns:
            True if authenticated, False otherwise
        """
        try:
            self.get_valid_token(config)
            return True
        except ValueError:
            return False