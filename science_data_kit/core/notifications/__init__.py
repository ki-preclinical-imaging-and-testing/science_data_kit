"""
Framework-Agnostic Notification System for Science Data Kit

This module provides a unified notification system that works across different
frontend frameworks (Streamlit, Flask, React, etc.). It includes a core NotificationManager
class and framework-specific adapters.
"""

from science_data_kit.core.notifications.notification_manager import NotificationManager
from science_data_kit.core.notifications.notification_types import (
    Notification, NotificationType, NotificationLevel, NotificationPosition
)

__all__ = [
    'NotificationManager',
    'Notification',
    'NotificationType',
    'NotificationLevel',
    'NotificationPosition',
]