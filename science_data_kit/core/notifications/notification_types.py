"""
Type definitions for the notification system.

This module defines the types used in the notification system, including
the Notification class and related enums.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid

class NotificationType(str, Enum):
    """Types of notifications."""
    TOAST = "toast"  # Temporary popup notification
    ALERT = "alert"  # Inline alert that stays visible
    BANNER = "banner"  # Full-width banner at the top of the page
    MODAL = "modal"  # Modal dialog
    SNACKBAR = "snackbar"  # Small notification at the bottom of the screen

class NotificationLevel(str, Enum):
    """Severity levels for notifications."""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"

class NotificationPosition(str, Enum):
    """Position for toast notifications."""
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"

@dataclass
class Notification:
    """
    A notification to be displayed to the user.
    
    Attributes:
        id: Unique identifier for the notification
        message: The message to display
        level: The severity level of the notification
        type: The type of notification
        title: Optional title for the notification
        details: Optional additional details
        duration: Duration in milliseconds (for toast notifications)
        position: Position for toast notifications
        dismissible: Whether the notification can be dismissed by the user
        actions: Optional actions that can be taken on the notification
        created_at: When the notification was created
        read: Whether the notification has been read
        metadata: Additional metadata for the notification
    """
    message: str
    level: NotificationLevel = NotificationLevel.INFO
    type: NotificationType = NotificationType.TOAST
    title: Optional[str] = None
    details: Optional[str] = None
    duration: int = 5000  # 5 seconds
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    dismissible: bool = True
    actions: List[Dict[str, Any]] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notification to a dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level,
            "type": self.type,
            "title": self.title,
            "details": self.details,
            "duration": self.duration,
            "position": self.position,
            "dismissible": self.dismissible,
            "actions": self.actions,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create a notification from a dictionary."""
        # Convert string values to enum values
        if "level" in data and isinstance(data["level"], str):
            data["level"] = NotificationLevel(data["level"])
        if "type" in data and isinstance(data["type"], str):
            data["type"] = NotificationType(data["type"])
        if "position" in data and isinstance(data["position"], str):
            data["position"] = NotificationPosition(data["position"])
        
        # Convert ISO format string to datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)