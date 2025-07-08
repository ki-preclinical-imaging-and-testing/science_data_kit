"""
Science Data Kit - Dropbox Extension
Conflict Resolution Module

This module provides functionality for resolving conflicts during Dropbox
synchronization operations.
"""

import logging
import os
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from pathlib import Path
from datetime import datetime

from dropbox.files import FileMetadata, FolderMetadata
from dropbox.exceptions import ApiError

from .connector import DropboxConnector
from .files import DropboxFileManager

logger = logging.getLogger(__name__)

class ConflictResolutionStrategy(Enum):
    """Enumeration of conflict resolution strategies."""
    
    # Always use the remote (Dropbox) version
    REMOTE_WINS = "remote_wins"
    
    # Always use the local version
    LOCAL_WINS = "local_wins"
    
    # Keep both versions with a conflict suffix
    KEEP_BOTH = "keep_both"
    
    # Use the newest version based on modification time
    NEWEST_WINS = "newest_wins"
    
    # Ask the user to decide
    ASK_USER = "ask_user"

class DropboxConflictResolver:
    """
    Class for resolving conflicts during Dropbox synchronization.
    
    This class provides methods for detecting and resolving conflicts between
    local and remote (Dropbox) versions of files.
    """
    
    def __init__(
        self, 
        connector: DropboxConnector,
        default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.KEEP_BOTH,
        conflict_suffix: str = " (conflicted copy)"
    ):
        """
        Initialize the conflict resolver.
        
        Args:
            connector: DropboxConnector instance for API access
            default_strategy: Default conflict resolution strategy
            conflict_suffix: Suffix to add to conflicted files
        """
        self.connector = connector
        self.file_manager = DropboxFileManager(connector)
        self.default_strategy = default_strategy
        self.conflict_suffix = conflict_suffix
        self.user_resolver = None
        
    def set_user_resolver(self, resolver: Callable[[str, Dict[str, Any], Dict[str, Any]], ConflictResolutionStrategy]):
        """
        Set a user resolver function for the ASK_USER strategy.
        
        Args:
            resolver: Function that takes a path, local metadata, and remote metadata,
                     and returns a ConflictResolutionStrategy
        """
        self.user_resolver = resolver
        
    def detect_conflict(
        self, 
        path: str, 
        local_metadata: Dict[str, Any], 
        remote_metadata: Dict[str, Any]
    ) -> bool:
        """
        Detect if there is a conflict between local and remote versions.
        
        Args:
            path: Path to the file
            local_metadata: Local file metadata
            remote_metadata: Remote file metadata
            
        Returns:
            True if there is a conflict, False otherwise
        """
        # If either version doesn't exist, there's no conflict
        if not local_metadata or not remote_metadata:
            return False
            
        # If content hashes match, there's no conflict
        if local_metadata.get('content_hash') == remote_metadata.get('content_hash'):
            return False
            
        # If modification times match, there's no conflict
        local_modified = local_metadata.get('modified')
        remote_modified = remote_metadata.get('modified')
        
        if local_modified and remote_modified and local_modified == remote_modified:
            return False
            
        # Otherwise, there's a conflict
        return True
        
    def resolve_conflict(
        self, 
        path: str, 
        local_path: str,
        local_metadata: Dict[str, Any], 
        remote_metadata: Dict[str, Any],
        strategy: Optional[ConflictResolutionStrategy] = None
    ) -> Dict[str, Any]:
        """
        Resolve a conflict between local and remote versions.
        
        Args:
            path: Dropbox path to the file
            local_path: Local path to the file
            local_metadata: Local file metadata
            remote_metadata: Remote file metadata
            strategy: Conflict resolution strategy (uses default if None)
            
        Returns:
            Metadata of the resolved file
        """
        strategy = strategy or self.default_strategy
        
        logger.info(f"Resolving conflict for {path} using strategy {strategy.value}")
        
        if strategy == ConflictResolutionStrategy.REMOTE_WINS:
            # Use the remote version
            return self._resolve_remote_wins(path, local_path, remote_metadata)
            
        elif strategy == ConflictResolutionStrategy.LOCAL_WINS:
            # Use the local version
            return self._resolve_local_wins(path, local_path, local_metadata)
            
        elif strategy == ConflictResolutionStrategy.KEEP_BOTH:
            # Keep both versions
            return self._resolve_keep_both(path, local_path, local_metadata, remote_metadata)
            
        elif strategy == ConflictResolutionStrategy.NEWEST_WINS:
            # Use the newest version
            return self._resolve_newest_wins(path, local_path, local_metadata, remote_metadata)
            
        elif strategy == ConflictResolutionStrategy.ASK_USER:
            # Ask the user
            if not self.user_resolver:
                logger.warning("No user resolver set for ASK_USER strategy, falling back to default")
                return self.resolve_conflict(
                    path, local_path, local_metadata, remote_metadata, self.default_strategy
                )
                
            user_choice = self.user_resolver(path, local_metadata, remote_metadata)
            return self.resolve_conflict(
                path, local_path, local_metadata, remote_metadata, user_choice
            )
            
        else:
            raise ValueError(f"Unknown conflict resolution strategy: {strategy}")
            
    def _resolve_remote_wins(
        self, 
        path: str, 
        local_path: str,
        remote_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflict by using the remote version.
        
        Args:
            path: Dropbox path to the file
            local_path: Local path to the file
            remote_metadata: Remote file metadata
            
        Returns:
            Metadata of the resolved file
        """
        try:
            # Download the remote file
            content, metadata = self.file_manager.download_file(path)
            
            # Write to local path
            with open(local_path, 'wb') as f:
                f.write(content)
                
            logger.info(f"Resolved conflict for {path} by using remote version")
            return metadata
        except Exception as e:
            logger.error(f"Error resolving conflict for {path}: {e}")
            raise
            
    def _resolve_local_wins(
        self, 
        path: str, 
        local_path: str,
        local_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflict by using the local version.
        
        Args:
            path: Dropbox path to the file
            local_path: Local path to the file
            local_metadata: Local file metadata
            
        Returns:
            Metadata of the resolved file
        """
        try:
            # Upload the local file
            with open(local_path, 'rb') as f:
                metadata = self.file_manager.upload_file(f, path, overwrite=True)
                
            logger.info(f"Resolved conflict for {path} by using local version")
            return metadata
        except Exception as e:
            logger.error(f"Error resolving conflict for {path}: {e}")
            raise
            
    def _resolve_keep_both(
        self, 
        path: str, 
        local_path: str,
        local_metadata: Dict[str, Any], 
        remote_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflict by keeping both versions.
        
        Args:
            path: Dropbox path to the file
            local_path: Local path to the file
            local_metadata: Local file metadata
            remote_metadata: Remote file metadata
            
        Returns:
            Metadata of the resolved file
        """
        try:
            # Generate conflict paths
            filename = os.path.basename(path)
            dirname = os.path.dirname(path)
            name, ext = os.path.splitext(filename)
            
            # Create conflict path for local version
            conflict_name = f"{name}{self.conflict_suffix} (local){ext}"
            conflict_path = os.path.join(dirname, conflict_name)
            
            # Upload local version to conflict path
            with open(local_path, 'rb') as f:
                self.file_manager.upload_file(f, conflict_path)
                
            # Download remote version to local path
            content, metadata = self.file_manager.download_file(path)
            with open(local_path, 'wb') as f:
                f.write(content)
                
            logger.info(f"Resolved conflict for {path} by keeping both versions")
            return metadata
        except Exception as e:
            logger.error(f"Error resolving conflict for {path}: {e}")
            raise
            
    def _resolve_newest_wins(
        self, 
        path: str, 
        local_path: str,
        local_metadata: Dict[str, Any], 
        remote_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflict by using the newest version.
        
        Args:
            path: Dropbox path to the file
            local_path: Local path to the file
            local_metadata: Local file metadata
            remote_metadata: Remote file metadata
            
        Returns:
            Metadata of the resolved file
        """
        try:
            local_modified = local_metadata.get('modified')
            remote_modified = remote_metadata.get('modified')
            
            # If either doesn't have a modification time, fall back to KEEP_BOTH
            if not local_modified or not remote_modified:
                logger.warning("Missing modification time, falling back to KEEP_BOTH")
                return self._resolve_keep_both(path, local_path, local_metadata, remote_metadata)
                
            # Compare modification times
            if local_modified > remote_modified:
                logger.info(f"Local version of {path} is newer")
                return self._resolve_local_wins(path, local_path, local_metadata)
            else:
                logger.info(f"Remote version of {path} is newer")
                return self._resolve_remote_wins(path, local_path, remote_metadata)
        except Exception as e:
            logger.error(f"Error resolving conflict for {path}: {e}")
            raise
"""