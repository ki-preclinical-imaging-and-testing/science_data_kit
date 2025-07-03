"""
Authentication and Authorization for Science Data Kit API Layer

This module provides authentication and authorization mechanisms for the Science Data Kit API layer,
including token-based authentication and role-based access control.
"""

from typing import Any, Dict, List, Optional, Set, Union
import time
import uuid
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from enum import Enum

from .base import APIError, APIErrorCode

logger = logging.getLogger(__name__)


class APIRole(Enum):
    """Roles for API users."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class APIPermission(Enum):
    """Permissions for API endpoints."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class APIToken:
    """Class for API tokens."""
    
    def __init__(self, user_id: str, roles: Optional[List[APIRole]] = None, 
                 expires_at: Optional[datetime] = None, token_id: Optional[str] = None,
                 permissions: Optional[Set[APIPermission]] = None):
        """
        Initialize the API token.
        
        Args:
            user_id: The ID of the user.
            roles: The roles assigned to the token.
            expires_at: The expiration date of the token.
            token_id: The ID of the token. If not provided, a new ID will be generated.
            permissions: The permissions assigned to the token.
        """
        self.user_id = user_id
        self.roles = roles or [APIRole.USER]
        self.token_id = token_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.expires_at = expires_at or (self.created_at + timedelta(days=30))
        self.permissions = permissions or {APIPermission.READ}
        self._token_value = None
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the token is expired.
        
        Returns:
            True if the token is expired, False otherwise.
        """
        return datetime.now() > self.expires_at
    
    def has_role(self, role: APIRole) -> bool:
        """
        Check if the token has a specific role.
        
        Args:
            role: The role to check.
            
        Returns:
            True if the token has the role, False otherwise.
        """
        return role in self.roles
    
    def has_permission(self, permission: APIPermission) -> bool:
        """
        Check if the token has a specific permission.
        
        Args:
            permission: The permission to check.
            
        Returns:
            True if the token has the permission, False otherwise.
        """
        # Admin role has all permissions
        if APIRole.ADMIN in self.roles:
            return True
        
        return permission in self.permissions
    
    def generate_token(self) -> str:
        """
        Generate a token value.
        
        Returns:
            The token value.
        """
        if self._token_value is None:
            # Generate a secure token
            token_base = f"{self.user_id}:{self.token_id}:{time.time()}:{secrets.token_hex(32)}"
            self._token_value = hashlib.sha256(token_base.encode()).hexdigest()
        
        return self._token_value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the token to a dictionary.
        
        Returns:
            A dictionary representation of the token.
        """
        return {
            "token_id": self.token_id,
            "user_id": self.user_id,
            "roles": [role.value for role in self.roles],
            "permissions": [perm.value for perm in self.permissions],
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "token": self.generate_token()
        }


class APIAuth:
    """Class for API authentication and authorization."""
    
    def __init__(self):
        """Initialize the API authentication and authorization."""
        self.tokens = {}  # token_value -> APIToken
        self.user_tokens = {}  # user_id -> [token_value]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_token(self, user_id: str, roles: Optional[List[APIRole]] = None,
                     expires_in: Optional[int] = None,
                     permissions: Optional[Set[APIPermission]] = None) -> APIToken:
        """
        Create a new token for a user.
        
        Args:
            user_id: The ID of the user.
            roles: The roles assigned to the token.
            expires_in: The number of days until the token expires.
            permissions: The permissions assigned to the token.
            
        Returns:
            The created token.
        """
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now() + timedelta(days=expires_in)
        
        token = APIToken(user_id=user_id, roles=roles, expires_at=expires_at, permissions=permissions)
        token_value = token.generate_token()
        
        self.tokens[token_value] = token
        
        if user_id not in self.user_tokens:
            self.user_tokens[user_id] = []
        
        self.user_tokens[user_id].append(token_value)
        
        return token
    
    def validate_token(self, token_value: str) -> Optional[APIToken]:
        """
        Validate a token.
        
        Args:
            token_value: The token value to validate.
            
        Returns:
            The token if valid, None otherwise.
        """
        token = self.tokens.get(token_value)
        
        if token is None:
            return None
        
        if token.is_expired:
            self.revoke_token(token_value)
            return None
        
        return token
    
    def revoke_token(self, token_value: str) -> bool:
        """
        Revoke a token.
        
        Args:
            token_value: The token value to revoke.
            
        Returns:
            True if the token was revoked, False otherwise.
        """
        token = self.tokens.get(token_value)
        
        if token is None:
            return False
        
        # Remove from tokens dict
        del self.tokens[token_value]
        
        # Remove from user_tokens dict
        if token.user_id in self.user_tokens:
            if token_value in self.user_tokens[token.user_id]:
                self.user_tokens[token.user_id].remove(token_value)
            
            # Clean up empty user entries
            if not self.user_tokens[token.user_id]:
                del self.user_tokens[token.user_id]
        
        return True
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            The number of tokens revoked.
        """
        if user_id not in self.user_tokens:
            return 0
        
        token_values = self.user_tokens[user_id].copy()
        count = 0
        
        for token_value in token_values:
            if self.revoke_token(token_value):
                count += 1
        
        return count
    
    def authenticate_request(self, headers: Dict[str, str]) -> Optional[APIToken]:
        """
        Authenticate a request using the Authorization header.
        
        Args:
            headers: The request headers.
            
        Returns:
            The token if authentication is successful, None otherwise.
        """
        auth_header = headers.get("Authorization")
        
        if auth_header is None:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token_value = parts[1]
        
        return self.validate_token(token_value)
    
    def authorize_request(self, token: APIToken, required_permission: APIPermission) -> bool:
        """
        Authorize a request.
        
        Args:
            token: The token to check.
            required_permission: The required permission.
            
        Returns:
            True if the token has the required permission, False otherwise.
        """
        return token.has_permission(required_permission)
    
    def authenticate_and_authorize(self, headers: Dict[str, str], 
                                  required_permission: APIPermission) -> APIToken:
        """
        Authenticate and authorize a request.
        
        Args:
            headers: The request headers.
            required_permission: The required permission.
            
        Returns:
            The token if authentication and authorization are successful.
            
        Raises:
            APIError: If authentication or authorization fails.
        """
        token = self.authenticate_request(headers)
        
        if token is None:
            raise APIError(
                message="Authentication required",
                code=APIErrorCode.AUTHENTICATION_ERROR,
                status_code=401
            )
        
        if not self.authorize_request(token, required_permission):
            raise APIError(
                message="Insufficient permissions",
                code=APIErrorCode.AUTHORIZATION_ERROR,
                status_code=403
            )
        
        return token