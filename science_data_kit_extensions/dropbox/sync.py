"""
Science Data Kit - Dropbox Extension
Sync Module

This module provides functionality for real-time synchronization with Dropbox,
including change tracking and background sync services.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from queue import Queue, Empty

from dropbox import Dropbox
from dropbox.files import ListFolderResult, FileMetadata, FolderMetadata, DeletedMetadata
from dropbox.exceptions import ApiError, RateLimitError

from .connector import DropboxConnector
from .files import DropboxFileManager
from .entities import DropboxFile, DropboxFolder, create_entities_from_dropbox_items

logger = logging.getLogger(__name__)

class DropboxChangeTracker:
    """
    Class for tracking changes in Dropbox.
    
    This class provides methods for detecting and processing changes in Dropbox
    using the Dropbox API's longpoll and delta endpoints.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the change tracker.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        
        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")
            
        self.client = connector.client
        self.cursor = None
        self.file_manager = DropboxFileManager(connector)
        
    def get_latest_cursor(self, path: str = "") -> str:
        """
        Get the latest cursor for a path.
        
        Args:
            path: Path to get cursor for (empty for root)
            
        Returns:
            Cursor string for the path
        """
        try:
            # Ensure path starts with a slash if not empty
            if path and not path.startswith('/'):
                path = f"/{path}"
                
            # Get the latest cursor
            result = self.client.files_list_folder(path, recursive=True)
            self.cursor = result.cursor
            return self.cursor
        except ApiError as e:
            logger.error(f"Error getting cursor for {path}: {e}")
            raise
            
    def check_for_changes(self, timeout: int = 30) -> bool:
        """
        Check if there are changes since the last cursor.
        
        Args:
            timeout: Longpoll timeout in seconds
            
        Returns:
            True if changes are available, False otherwise
        """
        if not self.cursor:
            raise ValueError("No cursor available. Call get_latest_cursor first.")
            
        try:
            # Check for changes using longpoll
            result = self.client.files_list_folder_longpoll(self.cursor, timeout=timeout)
            return result.changes
        except ApiError as e:
            logger.error(f"Error checking for changes: {e}")
            raise
            
    def get_changes(self) -> List[Dict[str, Any]]:
        """
        Get changes since the last cursor.
        
        Returns:
            List of changes as dictionaries
        """
        if not self.cursor:
            raise ValueError("No cursor available. Call get_latest_cursor first.")
            
        try:
            # Get changes
            result = self.client.files_list_folder_continue(self.cursor)
            
            # Update cursor
            self.cursor = result.cursor
            
            # Process changes
            changes = []
            for entry in result.entries:
                if isinstance(entry, FileMetadata):
                    changes.append({
                        'type': 'file',
                        'action': 'add_or_update',
                        'id': entry.id,
                        'name': entry.name,
                        'path': entry.path_display,
                        'size': entry.size,
                        'modified': entry.client_modified,
                        'content_hash': entry.content_hash,
                        'sharing_info': entry.sharing_info._asdict() if hasattr(entry, 'sharing_info') and entry.sharing_info else None
                    })
                elif isinstance(entry, FolderMetadata):
                    changes.append({
                        'type': 'folder',
                        'action': 'add_or_update',
                        'id': entry.id,
                        'name': entry.name,
                        'path': entry.path_display,
                        'sharing_info': entry.sharing_info._asdict() if hasattr(entry, 'sharing_info') and entry.sharing_info else None
                    })
                elif isinstance(entry, DeletedMetadata):
                    changes.append({
                        'type': 'deleted',
                        'action': 'delete',
                        'name': entry.name,
                        'path': entry.path_display
                    })
                    
            return changes
        except ApiError as e:
            logger.error(f"Error getting changes: {e}")
            raise
            
    def process_changes(self, changes: List[Dict[str, Any]], callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> List[Union[DropboxFile, DropboxFolder]]:
        """
        Process changes and convert to entities.
        
        Args:
            changes: List of changes as dictionaries
            callback: Optional callback function to call for each change
            
        Returns:
            List of entities created from changes
        """
        # Filter out deletions for entity creation
        items = [item for item in changes if item.get('action') != 'delete']
        
        # Create entities
        entities = create_entities_from_dropbox_items(items)
        
        # Call callback for each change if provided
        if callback:
            for change in changes:
                callback(change)
                
        return entities
        
    def watch_for_changes(self, callback: Callable[[Dict[str, Any]], None], path: str = "", interval: int = 30, timeout: int = 30):
        """
        Watch for changes and call callback when changes occur.
        
        Args:
            callback: Callback function to call for each change
            path: Path to watch (empty for root)
            interval: Polling interval in seconds
            timeout: Longpoll timeout in seconds
        """
        # Get initial cursor
        if not self.cursor:
            self.get_latest_cursor(path)
            
        while True:
            try:
                # Check for changes
                has_changes = self.check_for_changes(timeout)
                
                if has_changes:
                    # Get and process changes
                    changes = self.get_changes()
                    self.process_changes(changes, callback)
                    
                # Sleep before next check
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error watching for changes: {e}")
                # Sleep before retry
                time.sleep(interval)

class DropboxSyncService:
    """
    Background service for Dropbox synchronization.
    
    This class provides a background service for synchronizing with Dropbox,
    including change detection and processing.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the sync service.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        self.change_tracker = DropboxChangeTracker(connector)
        self.running = False
        self.sync_thread = None
        self.change_queue = Queue()
        self.change_handlers = []
        
    def register_change_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """
        Register a handler for changes.
        
        Args:
            handler: Callback function to call for each change
        """
        self.change_handlers.append(handler)
        
    def _handle_change(self, change: Dict[str, Any]):
        """
        Handle a change by adding it to the queue and calling handlers.
        
        Args:
            change: Change dictionary
        """
        # Add to queue
        self.change_queue.put(change)
        
        # Call handlers
        for handler in self.change_handlers:
            try:
                handler(change)
            except Exception as e:
                logger.error(f"Error in change handler: {e}")
                
    def start(self, path: str = "", interval: int = 30, timeout: int = 30):
        """
        Start the sync service.
        
        Args:
            path: Path to watch (empty for root)
            interval: Polling interval in seconds
            timeout: Longpoll timeout in seconds
        """
        if self.running:
            logger.warning("Sync service is already running")
            return
            
        self.running = True
        
        # Start sync thread
        self.sync_thread = threading.Thread(
            target=self.change_tracker.watch_for_changes,
            args=(self._handle_change, path, interval, timeout),
            daemon=True
        )
        self.sync_thread.start()
        
        logger.info(f"Started Dropbox sync service watching {path or '/'}")
        
    def stop(self):
        """
        Stop the sync service.
        """
        if not self.running:
            logger.warning("Sync service is not running")
            return
            
        self.running = False
        
        # Thread will exit on next iteration
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1.0)
            
        logger.info("Stopped Dropbox sync service")
        
    def get_pending_changes(self, block: bool = False, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get pending changes from the queue.
        
        Args:
            block: Whether to block until a change is available
            timeout: Timeout in seconds if blocking
            
        Returns:
            Change dictionary or None if no changes are available
        """
        try:
            return self.change_queue.get(block=block, timeout=timeout)
        except Empty:
            return None
            
    def is_running(self) -> bool:
        """
        Check if the sync service is running.
        
        Returns:
            True if running, False otherwise
        """
        return self.running and self.sync_thread and self.sync_thread.is_alive()