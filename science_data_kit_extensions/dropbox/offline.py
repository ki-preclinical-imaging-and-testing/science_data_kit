"""
Science Data Kit - Dropbox Extension
Offline Mode Module

This module provides functionality for detecting when the application is offline
and handling Dropbox operations gracefully in offline mode.
"""

import logging
import time
import socket
import threading
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta

from dropbox.exceptions import ApiError, AuthError, HttpError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    """Enumeration of connection statuses."""

    # Connected to Dropbox API
    CONNECTED = "connected"

    # Disconnected from Dropbox API
    DISCONNECTED = "disconnected"

    # Connection is being checked
    CHECKING = "checking"

    # Connection is degraded (intermittent failures)
    DEGRADED = "degraded"

class DropboxOfflineDetector:
    """
    Class for detecting offline mode and handling operations gracefully.

    This class provides methods for detecting when the application is offline,
    queuing operations for later execution, and handling errors gracefully.
    """

    def __init__(
        self, 
        connector: DropboxConnector,
        check_interval: int = 60,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize the offline detector.

        Args:
            connector: DropboxConnector instance for API access
            check_interval: Interval in seconds between connection checks
            timeout: Timeout in seconds for connection checks
            max_retries: Maximum number of retries for operations
        """
        self.connector = connector
        self.check_interval = check_interval
        self.timeout = timeout
        self.max_retries = max_retries
        self.status = ConnectionStatus.CHECKING
        self.last_check_time = None
        self.last_online_time = None
        self.last_offline_time = None
        self.status_listeners = []
        self.operation_queue = []
        self.lock = threading.RLock()
        self.check_thread = None
        self.running = False

    def register_status_listener(self, listener: Callable[[ConnectionStatus], None]):
        """
        Register a listener for connection status changes.

        Args:
            listener: Callback function to call when status changes
        """
        with self.lock:
            self.status_listeners.append(listener)

    def start_monitoring(self):
        """
        Start monitoring the connection status.
        """
        with self.lock:
            if self.running:
                logger.warning("Connection monitoring is already running")
                return

            self.running = True

            # Start monitoring thread
            self.check_thread = threading.Thread(
                target=self._monitor_connection,
                daemon=True
            )
            self.check_thread.start()

            logger.info("Started Dropbox connection monitoring")

    def stop_monitoring(self):
        """
        Stop monitoring the connection status.
        """
        with self.lock:
            if not self.running:
                logger.warning("Connection monitoring is not running")
                return

            self.running = False

            # Thread will exit on next iteration
            if self.check_thread and self.check_thread.is_alive():
                self.check_thread.join(timeout=1.0)

            logger.info("Stopped Dropbox connection monitoring")

    def check_connection(self) -> ConnectionStatus:
        """
        Check the connection to Dropbox API.

        Returns:
            Current connection status
        """
        with self.lock:
            self.status = ConnectionStatus.CHECKING
            self.last_check_time = datetime.now()

            # Notify listeners
            self._notify_status_change()

        try:
            # Check internet connectivity first
            if not self._check_internet_connection():
                logger.warning("No internet connection detected")
                return self._set_status(ConnectionStatus.DISCONNECTED)

            # Check Dropbox API connectivity
            if not self.connector.is_connected():
                logger.warning("Not connected to Dropbox API")
                return self._set_status(ConnectionStatus.DISCONNECTED)

            # Try a simple API call
            try:
                self.connector.client.check_user()
                return self._set_status(ConnectionStatus.CONNECTED)
            except (ApiError, AuthError, HttpError) as e:
                logger.error(f"Error checking Dropbox API connection: {e}")
                return self._set_status(ConnectionStatus.DISCONNECTED)
        except Exception as e:
            logger.error(f"Unexpected error checking connection: {e}")
            return self._set_status(ConnectionStatus.DISCONNECTED)

    def is_online(self) -> bool:
        """
        Check if the application is online.

        Returns:
            True if online, False if offline
        """
        # If we haven't checked yet, check now
        if self.status == ConnectionStatus.CHECKING or self.last_check_time is None:
            self.check_connection()

        return self.status == ConnectionStatus.CONNECTED

    def queue_operation(self, operation: Callable, *args, **kwargs):
        """
        Queue an operation for later execution when online.

        Args:
            operation: Function to call
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        """
        with self.lock:
            self.operation_queue.append((operation, args, kwargs))
            logger.info(f"Queued operation {operation.__name__} for later execution")

    def execute_queued_operations(self):
        """
        Execute queued operations if online.

        Returns:
            Number of operations executed
        """
        if not self.is_online():
            logger.warning("Cannot execute queued operations while offline")
            return 0

        executed = 0
        with self.lock:
            # Make a copy of the queue and clear it
            queue = list(self.operation_queue)
            self.operation_queue = []

        # Execute operations
        for operation, args, kwargs in queue:
            try:
                logger.info(f"Executing queued operation {operation.__name__}")
                operation(*args, **kwargs)
                executed += 1
            except Exception as e:
                logger.error(f"Error executing queued operation {operation.__name__}: {e}")
                # Re-queue the operation
                with self.lock:
                    self.operation_queue.append((operation, args, kwargs))

        return executed

    def with_offline_handling(self, operation: Callable) -> Callable:
        """
        Decorator for handling operations in offline mode.

        Args:
            operation: Function to decorate

        Returns:
            Decorated function
        """
        def wrapper(*args, **kwargs):
            if not self.is_online():
                logger.warning(f"Offline mode detected, queuing operation {operation.__name__}")
                self.queue_operation(operation, *args, **kwargs)
                return None

            try:
                return operation(*args, **kwargs)
            except (ApiError, AuthError, HttpError) as e:
                # Check if it's a connectivity issue
                if self._is_connectivity_error(e):
                    logger.warning(f"Connectivity error detected, queuing operation {operation.__name__}")
                    self.queue_operation(operation, *args, **kwargs)
                    # Update status
                    self.check_connection()
                    return None
                else:
                    # Not a connectivity issue, re-raise
                    raise

        return wrapper

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current connection status information.

        Returns:
            Dictionary with status information
        """
        with self.lock:
            return {
                'status': self.status,
                'last_check_time': self.last_check_time,
                'last_online_time': self.last_online_time,
                'last_offline_time': self.last_offline_time,
                'queued_operations': len(self.operation_queue)
            }

    def _set_status(self, status: ConnectionStatus) -> ConnectionStatus:
        """
        Set the connection status and notify listeners.

        Args:
            status: New connection status

        Returns:
            The new status
        """
        with self.lock:
            old_status = self.status
            self.status = status

            # Update timestamps
            if status == ConnectionStatus.CONNECTED:
                self.last_online_time = datetime.now()
            elif status == ConnectionStatus.DISCONNECTED:
                self.last_offline_time = datetime.now()

            # Notify listeners if status changed
            if old_status != status:
                self._notify_status_change()

            return status

    def _notify_status_change(self):
        """
        Notify listeners of a status change.
        """
        for listener in self.status_listeners:
            try:
                listener(self.status)
            except Exception as e:
                logger.error(f"Error in status listener: {e}")

    def _monitor_connection(self):
        """
        Monitor the connection status in a background thread.
        """
        while self.running:
            try:
                # Check connection
                self.check_connection()

                # If online, try to execute queued operations
                if self.status == ConnectionStatus.CONNECTED:
                    self.execute_queued_operations()

                # Sleep until next check
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}")
                time.sleep(self.check_interval)

    def _check_internet_connection(self) -> bool:
        """
        Check if there is an internet connection.

        Returns:
            True if connected to the internet, False otherwise
        """
        try:
            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=self.timeout)
            return True
        except OSError:
            return False

    def _is_connectivity_error(self, error: Exception) -> bool:
        """
        Check if an error is related to connectivity issues.

        Args:
            error: Exception to check

        Returns:
            True if it's a connectivity error, False otherwise
        """
        # Check for specific error types or messages
        if isinstance(error, (socket.timeout, socket.error, ConnectionError, TimeoutError)):
            return True

        if isinstance(error, HttpError):
            # HTTP errors that might indicate connectivity issues
            return error.status_code in [408, 429, 500, 502, 503, 504]

        # Check error message for connectivity-related terms
        error_str = str(error).lower()
        connectivity_terms = ['timeout', 'connection', 'network', 'unreachable', 'dns']
        return any(term in error_str for term in connectivity_terms)
