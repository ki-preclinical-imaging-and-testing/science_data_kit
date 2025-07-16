"""
Notification Manager for Science Data Kit

This module provides a framework-agnostic notification system that can be used
with different frontend frameworks (Streamlit, Flask, React, etc.).
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union, Callable
from datetime import datetime, timedelta

from science_data_kit.core.notifications.notification_types import (
    Notification, NotificationType, NotificationLevel, NotificationPosition
)
from science_data_kit.core.state.state_manager import StateManager

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    A framework-agnostic notification manager that provides a unified API for
    managing notifications across different frontend frameworks.
    
    This class uses adapters to interact with the underlying UI framework
    (e.g., Streamlit, Flask, React, etc.).
    """
    
    def __init__(self, adapter=None, state_manager: Optional[StateManager] = None):
        """
        Initialize the notification manager with a specific adapter.
        
        Args:
            adapter: The adapter to use for displaying notifications. If None, notifications
                    will be stored but not displayed.
            state_manager: The state manager to use for storing notifications. If None,
                          a new state manager will be created.
        """
        self._adapter = adapter
        self._state_manager = state_manager or StateManager()
        self._callbacks: Dict[str, List[Callable[[Notification], None]]] = {
            "create": [],
            "update": [],
            "delete": [],
            "read": [],
        }
        
        # Initialize notifications in state
        if not self._state_manager.has("notifications"):
            self._state_manager.set("notifications", [])
    
    def create(self, 
               message: str,
               level: Union[NotificationLevel, str] = NotificationLevel.INFO,
               type: Union[NotificationType, str] = NotificationType.TOAST,
               title: Optional[str] = None,
               details: Optional[str] = None,
               duration: int = 5000,
               position: Union[NotificationPosition, str] = NotificationPosition.TOP_RIGHT,
               dismissible: bool = True,
               actions: Optional[List[Dict[str, Any]]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> Notification:
        """
        Create a new notification.
        
        Args:
            message: The message to display
            level: The severity level of the notification
            type: The type of notification
            title: Optional title for the notification
            details: Optional additional details
            duration: Duration in milliseconds (for toast notifications)
            position: Position for toast notifications
            dismissible: Whether the notification can be dismissed by the user
            actions: Optional actions that can be taken on the notification
            metadata: Additional metadata for the notification
            
        Returns:
            The created notification.
        """
        # Convert string enums to enum values if needed
        if isinstance(level, str):
            level = NotificationLevel(level)
        if isinstance(type, str):
            type = NotificationType(type)
        if isinstance(position, str):
            position = NotificationPosition(position)
        
        # Create the notification
        notification = Notification(
            message=message,
            level=level,
            type=type,
            title=title,
            details=details,
            duration=duration,
            position=position,
            dismissible=dismissible,
            actions=actions or [],
            metadata=metadata or {},
        )
        
        # Store the notification
        self._add_notification(notification)
        
        # Display the notification if an adapter is available
        if self._adapter:
            self._adapter.display(notification)
        
        # Trigger callbacks
        for callback in self._callbacks["create"]:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Error in notification create callback: {e}")
        
        return notification
    
    def success(self, message: str, **kwargs) -> Notification:
        """
        Create a success notification.
        
        Args:
            message: The message to display
            **kwargs: Additional arguments to pass to create()
            
        Returns:
            The created notification.
        """
        return self.create(message, level=NotificationLevel.SUCCESS, **kwargs)
    
    def info(self, message: str, **kwargs) -> Notification:
        """
        Create an info notification.
        
        Args:
            message: The message to display
            **kwargs: Additional arguments to pass to create()
            
        Returns:
            The created notification.
        """
        return self.create(message, level=NotificationLevel.INFO, **kwargs)
    
    def warning(self, message: str, **kwargs) -> Notification:
        """
        Create a warning notification.
        
        Args:
            message: The message to display
            **kwargs: Additional arguments to pass to create()
            
        Returns:
            The created notification.
        """
        return self.create(message, level=NotificationLevel.WARNING, **kwargs)
    
    def error(self, message: str, **kwargs) -> Notification:
        """
        Create an error notification.
        
        Args:
            message: The message to display
            **kwargs: Additional arguments to pass to create()
            
        Returns:
            The created notification.
        """
        return self.create(message, level=NotificationLevel.ERROR, **kwargs)
    
    def debug(self, message: str, **kwargs) -> Notification:
        """
        Create a debug notification.
        
        Args:
            message: The message to display
            **kwargs: Additional arguments to pass to create()
            
        Returns:
            The created notification.
        """
        return self.create(message, level=NotificationLevel.DEBUG, **kwargs)
    
    def update(self, notification_id: str, **kwargs) -> Optional[Notification]:
        """
        Update an existing notification.
        
        Args:
            notification_id: The ID of the notification to update
            **kwargs: The attributes to update
            
        Returns:
            The updated notification, or None if the notification doesn't exist.
        """
        notifications = self._get_notifications()
        
        # Find the notification
        for i, notification in enumerate(notifications):
            if notification.id == notification_id:
                # Update the notification
                for key, value in kwargs.items():
                    if hasattr(notification, key):
                        # Convert string enums to enum values if needed
                        if key == "level" and isinstance(value, str):
                            value = NotificationLevel(value)
                        elif key == "type" and isinstance(value, str):
                            value = NotificationType(value)
                        elif key == "position" and isinstance(value, str):
                            value = NotificationPosition(value)
                        
                        setattr(notification, key, value)
                
                # Update the notification in the state
                notifications[i] = notification
                self._state_manager.set("notifications", notifications)
                
                # Update the notification in the UI if an adapter is available
                if self._adapter:
                    self._adapter.update(notification)
                
                # Trigger callbacks
                for callback in self._callbacks["update"]:
                    try:
                        callback(notification)
                    except Exception as e:
                        logger.error(f"Error in notification update callback: {e}")
                
                return notification
        
        return None
    
    def delete(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: The ID of the notification to delete
            
        Returns:
            True if the notification was deleted, False otherwise.
        """
        notifications = self._get_notifications()
        
        # Find the notification
        for i, notification in enumerate(notifications):
            if notification.id == notification_id:
                # Remove the notification from the state
                deleted_notification = notifications.pop(i)
                self._state_manager.set("notifications", notifications)
                
                # Remove the notification from the UI if an adapter is available
                if self._adapter:
                    self._adapter.remove(notification_id)
                
                # Trigger callbacks
                for callback in self._callbacks["delete"]:
                    try:
                        callback(deleted_notification)
                    except Exception as e:
                        logger.error(f"Error in notification delete callback: {e}")
                
                return True
        
        return False
    
    def clear(self, type: Optional[Union[NotificationType, str]] = None) -> None:
        """
        Clear all notifications of a specific type, or all notifications if type is None.
        
        Args:
            type: The type of notifications to clear, or None to clear all notifications
        """
        if type is None:
            # Clear all notifications
            self._state_manager.set("notifications", [])
            
            # Clear all notifications in the UI if an adapter is available
            if self._adapter:
                self._adapter.clear()
        else:
            # Convert string enum to enum value if needed
            if isinstance(type, str):
                type = NotificationType(type)
            
            # Get all notifications
            notifications = self._get_notifications()
            
            # Filter out notifications of the specified type
            filtered_notifications = [n for n in notifications if n.type != type]
            
            # Update the state
            self._state_manager.set("notifications", filtered_notifications)
            
            # Clear notifications of the specified type in the UI if an adapter is available
            if self._adapter:
                self._adapter.clear(type)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: The ID of the notification to mark as read
            
        Returns:
            True if the notification was marked as read, False otherwise.
        """
        return self.update(notification_id, read=True) is not None
    
    def mark_all_as_read(self) -> None:
        """Mark all notifications as read."""
        notifications = self._get_notifications()
        
        # Mark all notifications as read
        for notification in notifications:
            notification.read = True
        
        # Update the state
        self._state_manager.set("notifications", notifications)
        
        # Update the UI if an adapter is available
        if self._adapter:
            self._adapter.mark_all_as_read()
    
    def get(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification by ID.
        
        Args:
            notification_id: The ID of the notification to get
            
        Returns:
            The notification, or None if it doesn't exist.
        """
        notifications = self._get_notifications()
        
        # Find the notification
        for notification in notifications:
            if notification.id == notification_id:
                return notification
        
        return None
    
    def get_all(self, 
                type: Optional[Union[NotificationType, str]] = None,
                level: Optional[Union[NotificationLevel, str]] = None,
                read: Optional[bool] = None,
                since: Optional[datetime] = None) -> List[Notification]:
        """
        Get all notifications, optionally filtered by type, level, read status, and time.
        
        Args:
            type: Filter by notification type
            level: Filter by notification level
            read: Filter by read status
            since: Filter by creation time
            
        Returns:
            A list of notifications.
        """
        # Convert string enums to enum values if needed
        if isinstance(type, str):
            type = NotificationType(type)
        if isinstance(level, str):
            level = NotificationLevel(level)
        
        # Get all notifications
        notifications = self._get_notifications()
        
        # Apply filters
        if type is not None:
            notifications = [n for n in notifications if n.type == type]
        if level is not None:
            notifications = [n for n in notifications if n.level == level]
        if read is not None:
            notifications = [n for n in notifications if n.read == read]
        if since is not None:
            notifications = [n for n in notifications if n.created_at >= since]
        
        return notifications
    
    def count(self, 
              type: Optional[Union[NotificationType, str]] = None,
              level: Optional[Union[NotificationLevel, str]] = None,
              read: Optional[bool] = None,
              since: Optional[datetime] = None) -> int:
        """
        Count notifications, optionally filtered by type, level, read status, and time.
        
        Args:
            type: Filter by notification type
            level: Filter by notification level
            read: Filter by read status
            since: Filter by creation time
            
        Returns:
            The number of notifications.
        """
        return len(self.get_all(type, level, read, since))
    
    def on(self, event: str, callback: Callable[[Notification], None]) -> None:
        """
        Register a callback for a notification event.
        
        Args:
            event: The event to listen for ("create", "update", "delete", "read")
            callback: The callback function to call when the event occurs
        """
        if event not in self._callbacks:
            raise ValueError(f"Invalid event: {event}")
        
        self._callbacks[event].append(callback)
    
    def off(self, event: str, callback: Callable[[Notification], None]) -> None:
        """
        Remove a callback for a notification event.
        
        Args:
            event: The event to stop listening for
            callback: The callback function to remove
        """
        if event not in self._callbacks:
            raise ValueError(f"Invalid event: {event}")
        
        if callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
    
    def set_adapter(self, adapter) -> None:
        """
        Set a new adapter for displaying notifications.
        
        Args:
            adapter: The adapter to use
        """
        self._adapter = adapter
    
    def _get_notifications(self) -> List[Notification]:
        """Get all notifications from the state."""
        notifications_data = self._state_manager.get("notifications", [])
        
        # Convert dictionaries to Notification objects if needed
        notifications = []
        for item in notifications_data:
            if isinstance(item, dict):
                notifications.append(Notification.from_dict(item))
            else:
                notifications.append(item)
        
        return notifications
    
    def _add_notification(self, notification: Notification) -> None:
        """Add a notification to the state."""
        notifications = self._get_notifications()
        notifications.append(notification)
        self._state_manager.set("notifications", notifications)
    
    def cleanup(self, max_age: Optional[timedelta] = None) -> int:
        """
        Remove old notifications.
        
        Args:
            max_age: The maximum age of notifications to keep. If None, uses 30 days.
            
        Returns:
            The number of notifications removed.
        """
        if max_age is None:
            max_age = timedelta(days=30)
        
        # Get all notifications
        notifications = self._get_notifications()
        
        # Calculate the cutoff time
        cutoff_time = datetime.now() - max_age
        
        # Filter out old notifications
        old_count = len(notifications)
        notifications = [n for n in notifications if n.created_at >= cutoff_time]
        new_count = len(notifications)
        
        # Update the state
        self._state_manager.set("notifications", notifications)
        
        return old_count - new_count