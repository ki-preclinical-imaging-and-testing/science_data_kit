"""
Base Notification Adapter Interface for Science Data Kit

This module defines the interface that all notification adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from science_data_kit.core.notifications.notification_types import (
    Notification, NotificationType
)

class NotificationAdapter(ABC):
    """
    Abstract base class for notification adapters.
    
    All notification adapters must implement these methods to provide a consistent
    interface for the notification manager.
    """
    
    @abstractmethod
    def display(self, notification: Notification) -> None:
        """
        Display a notification to the user.
        
        Args:
            notification: The notification to display
        """
        pass
    
    @abstractmethod
    def update(self, notification: Notification) -> None:
        """
        Update an existing notification.
        
        Args:
            notification: The notification to update
        """
        pass
    
    @abstractmethod
    def remove(self, notification_id: str) -> None:
        """
        Remove a notification from the UI.
        
        Args:
            notification_id: The ID of the notification to remove
        """
        pass
    
    @abstractmethod
    def clear(self, type: Optional[NotificationType] = None) -> None:
        """
        Clear all notifications of a specific type, or all notifications if type is None.
        
        Args:
            type: The type of notifications to clear, or None to clear all notifications
        """
        pass
    
    @abstractmethod
    def mark_all_as_read(self) -> None:
        """Mark all notifications as read."""
        pass