"""
Science Data Kit - Microsoft Graph Extension

This extension provides integration with Microsoft Graph API for the Science Data Kit.
It enables access to Microsoft 365 services including Microsoft Teams, SharePoint,
OneDrive, Outlook, and user/group information.
"""

from .connector import MSGraphConnector
from .files import MSGraphFileManager
from .sharepoint import SharePointFileManager

__version__ = "0.1.0"
__all__ = ["MSGraphConnector", "MSGraphFileManager", "SharePointFileManager"]
