"""
Streamlit Notification Adapter for Science Data Kit

This module provides a notification adapter for Streamlit that uses Streamlit's
UI components to display notifications.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from science_data_kit.core.notifications.adapters.base_adapter import NotificationAdapter
from science_data_kit.core.notifications.notification_types import (
    Notification, NotificationType, NotificationLevel, NotificationPosition
)

logger = logging.getLogger(__name__)

class StreamlitNotificationAdapter(NotificationAdapter):
    """
    A notification adapter for Streamlit that uses Streamlit's UI components
    to display notifications.
    
    This adapter uses Streamlit's st.success, st.info, st.warning, and st.error
    functions to display notifications, and stores them in session state for
    persistence across reruns.
    """
    
    def __init__(self):
        """Initialize the Streamlit notification adapter."""
        try:
            import streamlit as st
            self._st = st
        except ImportError:
            raise ImportError("Streamlit is not installed. Please install it with 'pip install streamlit'.")
        
        # Initialize notifications in session state
        if "notifications" not in self._st.session_state:
            self._st.session_state.notifications = {}
        
        # Initialize toast container in session state
        if "toast_container" not in self._st.session_state:
            self._st.session_state.toast_container = None
    
    def display(self, notification: Notification) -> None:
        """
        Display a notification to the user.
        
        Args:
            notification: The notification to display
        """
        # Store the notification in session state
        self._st.session_state.notifications[notification.id] = notification
        
        # Display the notification based on its type
        if notification.type == NotificationType.TOAST:
            self._display_toast(notification)
        elif notification.type == NotificationType.ALERT:
            self._display_alert(notification)
        elif notification.type == NotificationType.BANNER:
            self._display_banner(notification)
        elif notification.type == NotificationType.MODAL:
            self._display_modal(notification)
        elif notification.type == NotificationType.SNACKBAR:
            self._display_snackbar(notification)
    
    def update(self, notification: Notification) -> None:
        """
        Update an existing notification.
        
        Args:
            notification: The notification to update
        """
        # Update the notification in session state
        self._st.session_state.notifications[notification.id] = notification
        
        # Re-display the notification
        self.display(notification)
    
    def remove(self, notification_id: str) -> None:
        """
        Remove a notification from the UI.
        
        Args:
            notification_id: The ID of the notification to remove
        """
        # Remove the notification from session state
        if notification_id in self._st.session_state.notifications:
            del self._st.session_state.notifications[notification_id]
    
    def clear(self, type: Optional[NotificationType] = None) -> None:
        """
        Clear all notifications of a specific type, or all notifications if type is None.
        
        Args:
            type: The type of notifications to clear, or None to clear all notifications
        """
        if type is None:
            # Clear all notifications
            self._st.session_state.notifications = {}
        else:
            # Clear notifications of the specified type
            for notification_id in list(self._st.session_state.notifications.keys()):
                notification = self._st.session_state.notifications[notification_id]
                if notification.type == type:
                    del self._st.session_state.notifications[notification_id]
    
    def mark_all_as_read(self) -> None:
        """Mark all notifications as read."""
        for notification_id, notification in self._st.session_state.notifications.items():
            notification.read = True
            self._st.session_state.notifications[notification_id] = notification
    
    def _display_toast(self, notification: Notification) -> None:
        """
        Display a toast notification.
        
        Args:
            notification: The notification to display
        """
        # Map notification level to Streamlit function
        level_map = {
            NotificationLevel.SUCCESS: self._st.success,
            NotificationLevel.INFO: self._st.info,
            NotificationLevel.WARNING: self._st.warning,
            NotificationLevel.ERROR: self._st.error,
            NotificationLevel.DEBUG: self._st.info,
        }
        
        # Get the appropriate function
        func = level_map.get(notification.level, self._st.info)
        
        # Create the message
        message = notification.message
        if notification.title:
            message = f"**{notification.title}**\n\n{message}"
        
        # Display the notification
        with self._st.container():
            func(message)
    
    def _display_alert(self, notification: Notification) -> None:
        """
        Display an alert notification.
        
        Args:
            notification: The notification to display
        """
        # Map notification level to Streamlit function
        level_map = {
            NotificationLevel.SUCCESS: self._st.success,
            NotificationLevel.INFO: self._st.info,
            NotificationLevel.WARNING: self._st.warning,
            NotificationLevel.ERROR: self._st.error,
            NotificationLevel.DEBUG: self._st.info,
        }
        
        # Get the appropriate function
        func = level_map.get(notification.level, self._st.info)
        
        # Create the message
        message = notification.message
        if notification.title:
            message = f"**{notification.title}**\n\n{message}"
        if notification.details:
            message = f"{message}\n\n{notification.details}"
        
        # Display the notification
        with self._st.container():
            func(message)
            
            # Display actions if any
            if notification.actions:
                cols = self._st.columns(len(notification.actions))
                for i, action in enumerate(notification.actions):
                    with cols[i]:
                        if self._st.button(action.get("label", "Action"), key=f"{notification.id}_{i}"):
                            if "callback" in action and callable(action["callback"]):
                                action["callback"]()
    
    def _display_banner(self, notification: Notification) -> None:
        """
        Display a banner notification.
        
        Args:
            notification: The notification to display
        """
        # Map notification level to CSS class
        level_map = {
            NotificationLevel.SUCCESS: "success",
            NotificationLevel.INFO: "info",
            NotificationLevel.WARNING: "warning",
            NotificationLevel.ERROR: "danger",
            NotificationLevel.DEBUG: "info",
        }
        
        # Get the appropriate CSS class
        css_class = level_map.get(notification.level, "info")
        
        # Create the message
        message = notification.message
        if notification.title:
            message = f"**{notification.title}**\n\n{message}"
        
        # Display the notification
        self._st.markdown(
            f"""
            <div class="alert alert-{css_class}" role="alert">
                {message}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _display_modal(self, notification: Notification) -> None:
        """
        Display a modal notification.
        
        Args:
            notification: The notification to display
        """
        # Create the message
        message = notification.message
        if notification.details:
            message = f"{message}\n\n{notification.details}"
        
        # Display the notification
        with self._st.expander(notification.title or "Notification", expanded=True):
            self._st.markdown(message)
            
            # Display actions if any
            if notification.actions:
                cols = self._st.columns(len(notification.actions))
                for i, action in enumerate(notification.actions):
                    with cols[i]:
                        if self._st.button(action.get("label", "Action"), key=f"{notification.id}_{i}"):
                            if "callback" in action and callable(action["callback"]):
                                action["callback"]()
    
    def _display_snackbar(self, notification: Notification) -> None:
        """
        Display a snackbar notification.
        
        Args:
            notification: The notification to display
        """
        # Snackbars are not natively supported in Streamlit, so we'll use a toast instead
        self._display_toast(notification)