"""
Science Data Kit - Dropbox Extension
Comments Module

This module provides functionality for extracting and managing comments on
Dropbox files.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from dropbox.exceptions import ApiError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxCommentManager:
    """
    Class for managing comments on Dropbox files.
    
    This class provides methods for extracting, adding, and managing comments
    on Dropbox files.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the comment manager.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        
        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")
            
        self.client = connector.client
        
    def list_comments(self, file_path: str) -> List[Dict[str, Any]]:
        """
        List comments on a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of comment metadata dictionaries
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # List comments on the file
            result = self.client.files_list_comments(file_id)
            
            # Convert to dictionaries
            comments = []
            for comment in result.comments:
                comments.append(self._comment_to_dict(comment))
                
            # Continue fetching if there are more comments
            while result.has_more:
                result = self.client.files_list_comments_continue(result.cursor)
                for comment in result.comments:
                    comments.append(self._comment_to_dict(comment))
                    
            return comments
        except ApiError as e:
            logger.error(f"Error listing comments for {file_path}: {e}")
            raise
            
    def add_comment(self, file_path: str, comment_text: str) -> Dict[str, Any]:
        """
        Add a comment to a file.
        
        Args:
            file_path: Path to the file
            comment_text: Text of the comment
            
        Returns:
            Comment metadata
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Add comment to the file
            result = self.client.files_add_comment(file_id, comment_text)
            
            # Convert to dictionary
            return self._comment_to_dict(result)
        except ApiError as e:
            logger.error(f"Error adding comment to {file_path}: {e}")
            raise
            
    def delete_comment(self, file_path: str, comment_id: str) -> bool:
        """
        Delete a comment from a file.
        
        Args:
            file_path: Path to the file
            comment_id: ID of the comment to delete
            
        Returns:
            True if successful
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Delete the comment
            self.client.files_delete_comment(file_id, comment_id)
            return True
        except ApiError as e:
            logger.error(f"Error deleting comment {comment_id} from {file_path}: {e}")
            raise
            
    def update_comment(self, file_path: str, comment_id: str, comment_text: str) -> Dict[str, Any]:
        """
        Update a comment on a file.
        
        Args:
            file_path: Path to the file
            comment_id: ID of the comment to update
            comment_text: New text for the comment
            
        Returns:
            Updated comment metadata
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Update the comment
            result = self.client.files_update_comment(file_id, comment_id, comment_text)
            
            # Convert to dictionary
            return self._comment_to_dict(result)
        except ApiError as e:
            logger.error(f"Error updating comment {comment_id} on {file_path}: {e}")
            raise
            
    def get_comment(self, file_path: str, comment_id: str) -> Dict[str, Any]:
        """
        Get a specific comment by ID.
        
        Args:
            file_path: Path to the file
            comment_id: ID of the comment
            
        Returns:
            Comment metadata
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Get the comment
            result = self.client.files_get_comment(file_id, comment_id)
            
            # Convert to dictionary
            return self._comment_to_dict(result)
        except ApiError as e:
            logger.error(f"Error getting comment {comment_id} from {file_path}: {e}")
            raise
            
    def resolve_comment(self, file_path: str, comment_id: str) -> Dict[str, Any]:
        """
        Mark a comment as resolved.
        
        Args:
            file_path: Path to the file
            comment_id: ID of the comment to resolve
            
        Returns:
            Updated comment metadata
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Resolve the comment
            result = self.client.files_resolve_comment(file_id, comment_id)
            
            # Convert to dictionary
            return self._comment_to_dict(result)
        except ApiError as e:
            logger.error(f"Error resolving comment {comment_id} on {file_path}: {e}")
            raise
            
    def unresolve_comment(self, file_path: str, comment_id: str) -> Dict[str, Any]:
        """
        Mark a comment as unresolved.
        
        Args:
            file_path: Path to the file
            comment_id: ID of the comment to unresolve
            
        Returns:
            Updated comment metadata
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file metadata to get the file ID
            file_metadata = self.client.files_get_metadata(file_path)
            file_id = file_metadata.id
            
            # Unresolve the comment
            result = self.client.files_unresolve_comment(file_id, comment_id)
            
            # Convert to dictionary
            return self._comment_to_dict(result)
        except ApiError as e:
            logger.error(f"Error unresolving comment {comment_id} on {file_path}: {e}")
            raise
            
    def count_comments(self, file_path: str) -> int:
        """
        Count the number of comments on a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of comments
        """
        try:
            comments = self.list_comments(file_path)
            return len(comments)
        except ApiError as e:
            logger.error(f"Error counting comments for {file_path}: {e}")
            raise
            
    def _comment_to_dict(self, comment) -> Dict[str, Any]:
        """
        Convert a comment object to a dictionary.
        
        Args:
            comment: Comment object
            
        Returns:
            Dictionary representation
        """
        result = {
            'id': comment.id,
            'text': comment.content.text if hasattr(comment.content, 'text') else None,
            'created': comment.created,
            'is_deleted': comment.is_deleted
        }
        
        # Add user information if available
        if hasattr(comment, 'user') and comment.user:
            result['user'] = {
                'account_id': comment.user.account_id,
                'display_name': comment.user.display_name,
                'email': comment.user.email
            }
            
        # Add resolved information if available
        if hasattr(comment, 'resolved'):
            result['resolved'] = comment.resolved
            
        return result
"""