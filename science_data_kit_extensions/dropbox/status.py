"""
Science Data Kit - Dropbox Extension
Sync Status Module

This module provides functionality for tracking and displaying the status of
Dropbox synchronization operations.
"""

import logging
import time
import threading
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Enumeration of sync statuses."""
    
    # Sync is idle (no operations in progress)
    IDLE = "idle"
    
    # Sync is in progress
    SYNCING = "syncing"
    
    # Sync completed successfully
    COMPLETED = "completed"
    
    # Sync failed with errors
    FAILED = "failed"
    
    # Sync is paused
    PAUSED = "paused"
    
    # Sync is disconnected
    DISCONNECTED = "disconnected"

class SyncOperation(Enum):
    """Enumeration of sync operations."""
    
    # Uploading a file to Dropbox
    UPLOAD = "upload"
    
    # Downloading a file from Dropbox
    DOWNLOAD = "download"
    
    # Deleting a file or folder
    DELETE = "delete"
    
    # Creating a folder
    CREATE_FOLDER = "create_folder"
    
    # Listing folder contents
    LIST_FOLDER = "list_folder"
    
    # Checking for changes
    CHECK_CHANGES = "check_changes"
    
    # Processing changes
    PROCESS_CHANGES = "process_changes"
    
    # Resolving conflicts
    RESOLVE_CONFLICT = "resolve_conflict"

class DropboxSyncStatus:
    """
    Class for tracking and displaying Dropbox sync status.
    
    This class provides methods for tracking the status of sync operations,
    calculating progress, and notifying listeners of status changes.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the sync status tracker.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        self.status = SyncStatus.IDLE
        self.operations = {}
        self.operation_counts = defaultdict(int)
        self.start_time = None
        self.end_time = None
        self.total_bytes = 0
        self.processed_bytes = 0
        self.total_files = 0
        self.processed_files = 0
        self.errors = []
        self.status_listeners = []
        self.progress_listeners = []
        self.lock = threading.RLock()
        
    def register_status_listener(self, listener: Callable[[SyncStatus], None]):
        """
        Register a listener for status changes.
        
        Args:
            listener: Callback function to call when status changes
        """
        with self.lock:
            self.status_listeners.append(listener)
        
    def register_progress_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """
        Register a listener for progress updates.
        
        Args:
            listener: Callback function to call when progress updates
        """
        with self.lock:
            self.progress_listeners.append(listener)
        
    def set_status(self, status: SyncStatus):
        """
        Set the current sync status.
        
        Args:
            status: New sync status
        """
        with self.lock:
            old_status = self.status
            self.status = status
            
            # Update timestamps
            if status == SyncStatus.SYNCING and old_status != SyncStatus.SYNCING:
                self.start_time = datetime.now()
                self.end_time = None
            elif status in [SyncStatus.COMPLETED, SyncStatus.FAILED] and old_status == SyncStatus.SYNCING:
                self.end_time = datetime.now()
                
            # Notify listeners
            for listener in self.status_listeners:
                try:
                    listener(status)
                except Exception as e:
                    logger.error(f"Error in status listener: {e}")
        
    def get_status(self) -> SyncStatus:
        """
        Get the current sync status.
        
        Returns:
            Current sync status
        """
        with self.lock:
            return self.status
        
    def start_operation(self, operation: SyncOperation, path: str, size: Optional[int] = None) -> str:
        """
        Start tracking a sync operation.
        
        Args:
            operation: Type of operation
            path: Path being operated on
            size: Size of the file (for uploads/downloads)
            
        Returns:
            Operation ID
        """
        with self.lock:
            # Generate operation ID
            operation_id = f"{operation.value}_{path}_{int(time.time() * 1000)}"
            
            # Record operation
            self.operations[operation_id] = {
                'id': operation_id,
                'operation': operation,
                'path': path,
                'size': size,
                'start_time': datetime.now(),
                'end_time': None,
                'status': SyncStatus.SYNCING,
                'progress': 0,
                'error': None
            }
            
            # Update counts
            self.operation_counts[operation] += 1
            
            # Update totals
            if size:
                self.total_bytes += size
            if operation in [SyncOperation.UPLOAD, SyncOperation.DOWNLOAD, SyncOperation.DELETE]:
                self.total_files += 1
                
            # Set overall status to syncing
            if self.status != SyncStatus.SYNCING:
                self.set_status(SyncStatus.SYNCING)
                
            # Notify progress listeners
            self._notify_progress()
                
            return operation_id
        
    def update_operation_progress(self, operation_id: str, progress: float, bytes_processed: Optional[int] = None):
        """
        Update the progress of an operation.
        
        Args:
            operation_id: Operation ID
            progress: Progress as a percentage (0-100)
            bytes_processed: Number of bytes processed
        """
        with self.lock:
            if operation_id not in self.operations:
                logger.warning(f"Unknown operation ID: {operation_id}")
                return
                
            # Update operation progress
            operation = self.operations[operation_id]
            old_progress = operation['progress']
            operation['progress'] = progress
            
            # Update processed bytes
            if bytes_processed is not None:
                size = operation['size'] or 0
                old_bytes = size * (old_progress / 100)
                new_bytes = size * (progress / 100)
                self.processed_bytes += (new_bytes - old_bytes)
                
            # Notify progress listeners
            self._notify_progress()
        
    def complete_operation(self, operation_id: str, error: Optional[Exception] = None):
        """
        Mark an operation as completed.
        
        Args:
            operation_id: Operation ID
            error: Exception if operation failed
        """
        with self.lock:
            if operation_id not in self.operations:
                logger.warning(f"Unknown operation ID: {operation_id}")
                return
                
            # Update operation
            operation = self.operations[operation_id]
            operation['end_time'] = datetime.now()
            operation['status'] = SyncStatus.FAILED if error else SyncStatus.COMPLETED
            operation['progress'] = 100
            operation['error'] = str(error) if error else None
            
            # Update processed counts
            if operation['operation'] in [SyncOperation.UPLOAD, SyncOperation.DOWNLOAD, SyncOperation.DELETE]:
                self.processed_files += 1
            if operation['size']:
                self.processed_bytes += operation['size']
                
            # Record error
            if error:
                self.errors.append({
                    'operation_id': operation_id,
                    'operation': operation['operation'],
                    'path': operation['path'],
                    'time': datetime.now(),
                    'error': str(error)
                })
                
            # Check if all operations are complete
            active_operations = [op for op in self.operations.values() if op['status'] == SyncStatus.SYNCING]
            if not active_operations:
                if self.errors:
                    self.set_status(SyncStatus.FAILED)
                else:
                    self.set_status(SyncStatus.COMPLETED)
                    
            # Notify progress listeners
            self._notify_progress()
        
    def get_progress(self) -> Dict[str, Any]:
        """
        Get the current sync progress.
        
        Returns:
            Dictionary with progress information
        """
        with self.lock:
            # Calculate overall progress
            if self.total_files > 0:
                file_progress = (self.processed_files / self.total_files) * 100
            else:
                file_progress = 100
                
            if self.total_bytes > 0:
                byte_progress = (self.processed_bytes / self.total_bytes) * 100
            else:
                byte_progress = 100
                
            # Calculate time remaining
            remaining_seconds = None
            if self.start_time and self.status == SyncStatus.SYNCING:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                if byte_progress > 0:
                    remaining_seconds = (elapsed / byte_progress) * (100 - byte_progress)
                    
            # Build progress info
            return {
                'status': self.status,
                'file_progress': file_progress,
                'byte_progress': byte_progress,
                'total_files': self.total_files,
                'processed_files': self.processed_files,
                'total_bytes': self.total_bytes,
                'processed_bytes': self.processed_bytes,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'elapsed_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'remaining_seconds': remaining_seconds,
                'operation_counts': dict(self.operation_counts),
                'active_operations': [op for op in self.operations.values() if op['status'] == SyncStatus.SYNCING],
                'error_count': len(self.errors),
                'last_error': self.errors[-1] if self.errors else None
            }
        
    def reset(self):
        """
        Reset the sync status.
        """
        with self.lock:
            self.status = SyncStatus.IDLE
            self.operations = {}
            self.operation_counts = defaultdict(int)
            self.start_time = None
            self.end_time = None
            self.total_bytes = 0
            self.processed_bytes = 0
            self.total_files = 0
            self.processed_files = 0
            self.errors = []
            
            # Notify listeners
            for listener in self.status_listeners:
                try:
                    listener(SyncStatus.IDLE)
                except Exception as e:
                    logger.error(f"Error in status listener: {e}")
                    
            self._notify_progress()
        
    def _notify_progress(self):
        """
        Notify progress listeners of current progress.
        """
        progress = self.get_progress()
        for listener in self.progress_listeners:
            try:
                listener(progress)
            except Exception as e:
                logger.error(f"Error in progress listener: {e}")
"""