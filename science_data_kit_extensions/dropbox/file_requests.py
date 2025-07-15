"""
Science Data Kit - Dropbox Extension
File Requests Module

This module provides functionality for creating and managing Dropbox file requests,
which allow users to request files from others.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

from dropbox.file_requests import (
    CreateFileRequestArgs,
    FileRequestDeadline,
    FileRequestError,
    GracePeriod
)
from dropbox.exceptions import ApiError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxFileRequestManager:
    """
    Class for managing Dropbox file requests.

    This class provides methods for creating, updating, and managing file requests,
    which allow users to request files from others.
    """

    def __init__(self, connector: DropboxConnector):
        """
        Initialize the file request manager.

        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector

        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")

        self.client = connector.client

    def create_file_request(
        self,
        title: str,
        destination: str,
        deadline: Optional[datetime] = None,
        deadline_grace_period_days: int = 0,
        open: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new file request.

        Args:
            title: Title of the file request
            destination: Dropbox folder path where files will be collected
            deadline: Optional deadline for the file request
            deadline_grace_period_days: Grace period in days after the deadline
            open: Whether the file request is open for file submissions

        Returns:
            File request metadata
        """
        try:
            # Ensure destination starts with a slash
            if not destination.startswith('/'):
                destination = f"/{destination}"

            # Create file request arguments
            create_args = CreateFileRequestArgs(
                title=title,
                destination=destination,
                open=open
            )

            # Add deadline if specified
            if deadline:
                deadline_obj = FileRequestDeadline(
                    deadline=deadline.strftime("%Y-%m-%dT%H:%M:%SZ")
                )

                # Add grace period if specified
                if deadline_grace_period_days > 0:
                    deadline_obj.grace_period = GracePeriod.days(deadline_grace_period_days)

                create_args.deadline = deadline_obj

            # Create the file request
            result = self.client.file_requests_create(create_args)

            # Convert to dictionary
            return self._file_request_to_dict(result)
        except ApiError as e:
            logger.error(f"Error creating file request: {e}")
            raise

    def list_file_requests(self) -> List[Dict[str, Any]]:
        """
        List all file requests.

        Returns:
            List of file request metadata dictionaries
        """
        try:
            # Get all file requests
            result = self.client.file_requests_list()

            # Convert to dictionaries
            return [self._file_request_to_dict(fr) for fr in result.file_requests]
        except ApiError as e:
            logger.error(f"Error listing file requests: {e}")
            raise

    def get_file_request(self, file_request_id: str) -> Dict[str, Any]:
        """
        Get a specific file request by ID.

        Args:
            file_request_id: ID of the file request

        Returns:
            File request metadata
        """
        try:
            # Get the file request
            result = self.client.file_requests_get(file_request_id)

            # Convert to dictionary
            return self._file_request_to_dict(result)
        except ApiError as e:
            logger.error(f"Error getting file request {file_request_id}: {e}")
            raise

    def update_file_request(
        self,
        file_request_id: str,
        title: Optional[str] = None,
        destination: Optional[str] = None,
        deadline: Optional[datetime] = None,
        deadline_grace_period_days: Optional[int] = None,
        open: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a file request.

        Args:
            file_request_id: ID of the file request to update
            title: New title (None to keep current)
            destination: New destination path (None to keep current)
            deadline: New deadline (None to keep current)
            deadline_grace_period_days: New grace period (None to keep current)
            open: New open status (None to keep current)

        Returns:
            Updated file request metadata
        """
        try:
            # Get current file request
            current = self.client.file_requests_get(file_request_id)

            # Prepare update arguments
            update_args = {
                'id': file_request_id,
                'title': title or current.title
            }

            # Add destination if specified
            if destination:
                if not destination.startswith('/'):
                    destination = f"/{destination}"
                update_args['destination'] = destination

            # Add deadline if specified
            if deadline:
                deadline_obj = FileRequestDeadline(
                    deadline=deadline.strftime("%Y-%m-%dT%H:%M:%SZ")
                )

                # Add grace period if specified
                if deadline_grace_period_days is not None:
                    deadline_obj.grace_period = GracePeriod.days(deadline_grace_period_days)

                update_args['deadline'] = deadline_obj

            # Add open status if specified
            if open is not None:
                update_args['open'] = open

            # Update the file request
            result = self.client.file_requests_update(update_args)

            # Convert to dictionary
            return self._file_request_to_dict(result)
        except ApiError as e:
            logger.error(f"Error updating file request {file_request_id}: {e}")
            raise

    def delete_file_request(self, file_request_id: str) -> bool:
        """
        Delete a file request.

        Args:
            file_request_id: ID of the file request to delete

        Returns:
            True if successful
        """
        try:
            # Delete the file request
            self.client.file_requests_delete(file_request_id)
            return True
        except ApiError as e:
            logger.error(f"Error deleting file request {file_request_id}: {e}")
            raise

    def close_file_request(self, file_request_id: str) -> Dict[str, Any]:
        """
        Close a file request (disallow new submissions).

        Args:
            file_request_id: ID of the file request to close

        Returns:
            Updated file request metadata
        """
        try:
            # Update the file request to closed
            return self.update_file_request(file_request_id, open=False)
        except ApiError as e:
            logger.error(f"Error closing file request {file_request_id}: {e}")
            raise

    def reopen_file_request(self, file_request_id: str) -> Dict[str, Any]:
        """
        Reopen a file request (allow new submissions).

        Args:
            file_request_id: ID of the file request to reopen

        Returns:
            Updated file request metadata
        """
        try:
            # Update the file request to open
            return self.update_file_request(file_request_id, open=True)
        except ApiError as e:
            logger.error(f"Error reopening file request {file_request_id}: {e}")
            raise

    def count_file_requests(self) -> int:
        """
        Count the number of file requests.

        Returns:
            Number of file requests
        """
        try:
            # Get all file requests
            result = self.client.file_requests_list()

            # Return count
            return len(result.file_requests)
        except ApiError as e:
            logger.error(f"Error counting file requests: {e}")
            raise

    def _file_request_to_dict(self, file_request) -> Dict[str, Any]:
        """
        Convert a file request object to a dictionary.

        Args:
            file_request: File request object

        Returns:
            Dictionary representation
        """
        result = {
            'id': file_request.id,
            'url': file_request.url,
            'title': file_request.title,
            'destination': file_request.destination,
            'created': file_request.created,
            'is_open': file_request.is_open
        }

        # Add deadline if present
        if hasattr(file_request, 'deadline') and file_request.deadline:
            result['deadline'] = file_request.deadline.deadline

            if hasattr(file_request.deadline, 'grace_period') and file_request.deadline.grace_period:
                result['grace_period_days'] = file_request.deadline.grace_period.get_days()

        return result
