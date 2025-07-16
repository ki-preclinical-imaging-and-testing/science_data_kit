"""
Notification Adapters for Science Data Kit

This package provides adapters for different frontend frameworks to interact with
the notification system. Each adapter implements the same interface but uses
different underlying UI frameworks.
"""

from science_data_kit.core.notifications.adapters.base_adapter import NotificationAdapter
from science_data_kit.core.notifications.adapters.streamlit_adapter import StreamlitNotificationAdapter
from science_data_kit.core.notifications.adapters.flask_adapter import FlaskNotificationAdapter

__all__ = [
    'NotificationAdapter',
    'StreamlitNotificationAdapter',
    'FlaskNotificationAdapter',
]