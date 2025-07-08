"""
Science Data Kit - Dropbox Extension
Webhooks Module

This module provides functionality for handling Dropbox webhooks for real-time
notifications of changes.
"""

import logging
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime

from .connector import DropboxConnector
from .sync import DropboxChangeTracker

logger = logging.getLogger(__name__)

class DropboxWebhookHandler:
    """
    Class for handling Dropbox webhooks.
    
    This class provides methods for verifying and processing webhook notifications
    from Dropbox, which can be used to trigger real-time sync operations.
    """
    
    def __init__(self, connector: DropboxConnector, app_secret: Optional[str] = None):
        """
        Initialize the webhook handler.
        
        Args:
            connector: DropboxConnector instance for API access
            app_secret: Dropbox app secret for webhook verification
        """
        self.connector = connector
        self.app_secret = app_secret or connector.app_secret
        self.change_tracker = DropboxChangeTracker(connector)
        self.handlers = []
        
    def register_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """
        Register a handler for webhook notifications.
        
        Args:
            handler: Callback function to call for each notification
        """
        self.handlers.append(handler)
        
    def verify_request(self, signature: str, body: bytes) -> bool:
        """
        Verify a webhook request using the signature.
        
        Args:
            signature: X-Dropbox-Signature header value
            body: Raw request body
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not self.app_secret:
            logger.warning("No app secret available for webhook verification")
            return False
            
        # Compute HMAC-SHA256 using app secret
        computed_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(computed_signature, signature)
        
    def process_notification(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a webhook notification.
        
        Args:
            data: Webhook notification data
            
        Returns:
            List of changes detected
        """
        # Log the notification
        logger.info(f"Received webhook notification: {data}")
        
        # Get the user IDs from the notification
        user_ids = data.get('list_folder', {}).get('accounts', [])
        
        if not user_ids:
            logger.warning("No user IDs in webhook notification")
            return []
            
        # Get changes for each user
        all_changes = []
        
        # For now, we only support the current user
        # In a multi-user scenario, we would need to handle each user separately
        try:
            # Get the latest changes
            changes = self.change_tracker.get_changes()
            all_changes.extend(changes)
            
            # Call handlers
            for handler in self.handlers:
                for change in changes:
                    try:
                        handler(change)
                    except Exception as e:
                        logger.error(f"Error in webhook handler: {e}")
        except Exception as e:
            logger.error(f"Error processing webhook notification: {e}")
            
        return all_changes
        
    def handle_challenge(self, challenge: str) -> Dict[str, str]:
        """
        Handle a webhook verification challenge.
        
        Args:
            challenge: Challenge string from Dropbox
            
        Returns:
            Response dictionary with the challenge
        """
        return {'challenge': challenge}
        
    def register_webhook(self, redirect_uri: str) -> str:
        """
        Register a webhook with Dropbox.
        
        Args:
            redirect_uri: URI where Dropbox will send webhook notifications
            
        Returns:
            Webhook ID
        """
        try:
            # Register the webhook
            result = self.connector.client.files_list_folder_get_latest_cursor(
                path='',
                recursive=True
            )
            
            # Get the cursor
            cursor = result.cursor
            
            # Register webhook for this cursor
            webhook_result = self.connector.client.files_list_folder_longpoll(
                cursor,
                webhook_url=redirect_uri
            )
            
            logger.info(f"Registered webhook for {redirect_uri}")
            return cursor
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            raise
            
    def unregister_webhook(self, webhook_id: str) -> bool:
        """
        Unregister a webhook with Dropbox.
        
        Args:
            webhook_id: Webhook ID to unregister
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Unregister the webhook
            # Note: Dropbox API doesn't have a direct method to unregister webhooks
            # This is typically done through the Dropbox developer console
            logger.info(f"Unregistered webhook {webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Error unregistering webhook: {e}")
            return False
"""