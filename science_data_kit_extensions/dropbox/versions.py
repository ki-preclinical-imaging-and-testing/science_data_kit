"""
Science Data Kit - Dropbox Extension
Versions Module

This module provides functionality for extracting and managing version history
of Dropbox files.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime

from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxVersionManager:
    """
    Class for managing version history of Dropbox files.

    This class provides methods for extracting, restoring, and managing versions
    of Dropbox files.
    """

    def __init__(self, connector: DropboxConnector):
        """
        Initialize the version manager.

        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector

        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")

        self.client = connector.client

    def list_revisions(self, path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List revisions of a file.

        Args:
            path: Path to the file
            limit: Maximum number of revisions to return

        Returns:
            List of revision metadata dictionaries
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"

            # List revisions
            result = self.client.files_list_revisions(path, limit=limit)

            # Convert to dictionaries
            revisions = []
            for entry in result.entries:
                revisions.append(self._revision_to_dict(entry))

            return revisions
        except ApiError as e:
            logger.error(f"Error listing revisions for {path}: {e}")
            raise

    def get_revision(self, path: str, rev: str) -> Dict[str, Any]:
        """
        Get metadata for a specific revision.

        Args:
            path: Path to the file
            rev: Revision ID

        Returns:
            Revision metadata
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"

            # Get revision metadata
            result = self.client.files_get_metadata(path, rev=rev)

            # Convert to dictionary
            return self._revision_to_dict(result)
        except ApiError as e:
            logger.error(f"Error getting revision {rev} for {path}: {e}")
            raise

    def download_revision(self, path: str, rev: str) -> Tuple[bytes, Dict[str, Any]]:
        """
        Download a specific revision of a file.

        Args:
            path: Path to the file
            rev: Revision ID

        Returns:
            Tuple of (file_content, metadata)
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"

            # Download the revision
            metadata, response = self.client.files_download(path, rev=rev)

            # Convert metadata to dictionary
            metadata_dict = self._revision_to_dict(metadata)

            return response.content, metadata_dict
        except ApiError as e:
            logger.error(f"Error downloading revision {rev} for {path}: {e}")
            raise

    def restore_revision(self, path: str, rev: str) -> Dict[str, Any]:
        """
        Restore a file to a specific revision.

        Args:
            path: Path to the file
            rev: Revision ID to restore

        Returns:
            Metadata for the restored file
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"

            # Restore the revision
            result = self.client.files_restore(path, rev)

            # Convert to dictionary
            return self._revision_to_dict(result)
        except ApiError as e:
            logger.error(f"Error restoring revision {rev} for {path}: {e}")
            raise

    def delete_revision(self, path: str, rev: str) -> bool:
        """
        Permanently delete a specific revision of a file.

        Args:
            path: Path to the file
            rev: Revision ID to delete

        Returns:
            True if successful
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"

            # Delete the revision
            self.client.files_permanently_delete(path, rev=rev)
            return True
        except ApiError as e:
            logger.error(f"Error deleting revision {rev} for {path}: {e}")
            raise

    def compare_revisions(self, path: str, rev1: str, rev2: str) -> Dict[str, Any]:
        """
        Compare two revisions of a file.

        Args:
            path: Path to the file
            rev1: First revision ID
            rev2: Second revision ID

        Returns:
            Dictionary with comparison information
        """
        try:
            # Get metadata for both revisions
            metadata1 = self.get_revision(path, rev1)
            metadata2 = self.get_revision(path, rev2)

            # Compare basic metadata
            comparison = {
                'path': path,
                'rev1': rev1,
                'rev2': rev2,
                'size_diff': metadata2['size'] - metadata1['size'],
                'time_diff': (metadata2['modified'] - metadata1['modified']).total_seconds() if isinstance(metadata2['modified'], datetime) and isinstance(metadata1['modified'], datetime) else None,
                'content_hash_changed': metadata1['content_hash'] != metadata2['content_hash']
            }

            # Download content for both revisions if they're different
            if comparison['content_hash_changed']:
                content1, _ = self.download_revision(path, rev1)
                content2, _ = self.download_revision(path, rev2)

                # Simple content comparison (could be enhanced with diff algorithm)
                comparison['content_diff'] = {
                    'bytes_changed': sum(1 for a, b in zip(content1, content2) if a != b),
                    'length_diff': len(content2) - len(content1)
                }

            return comparison
        except ApiError as e:
            logger.error(f"Error comparing revisions for {path}: {e}")
            raise

    def get_latest_revision(self, path: str) -> Dict[str, Any]:
        """
        Get the latest revision of a file.

        Args:
            path: Path to the file

        Returns:
            Latest revision metadata
        """
        try:
            # List revisions (latest first)
            revisions = self.list_revisions(path, limit=1)

            if not revisions:
                raise ValueError(f"No revisions found for {path}")

            return revisions[0]
        except ApiError as e:
            logger.error(f"Error getting latest revision for {path}: {e}")
            raise

    def count_revisions(self, path: str) -> int:
        """
        Count the number of revisions for a file.

        Args:
            path: Path to the file

        Returns:
            Number of revisions
        """
        try:
            # List all revisions (Dropbox API doesn't provide a direct count method)
            revisions = self.list_revisions(path, limit=100)  # Use a high limit
            return len(revisions)
        except ApiError as e:
            logger.error(f"Error counting revisions for {path}: {e}")
            raise

    def _revision_to_dict(self, revision: FileMetadata) -> Dict[str, Any]:
        """
        Convert a revision object to a dictionary.

        Args:
            revision: Revision object (FileMetadata)

        Returns:
            Dictionary representation
        """
        result = {
            'id': revision.id,
            'name': revision.name,
            'path': revision.path_display,
            'size': revision.size,
            'modified': revision.client_modified,
            'server_modified': revision.server_modified,
            'rev': revision.rev,
            'content_hash': revision.content_hash
        }

        # Add sharing info if available
        if hasattr(revision, 'sharing_info') and revision.sharing_info:
            result['sharing_info'] = revision.sharing_info._asdict()

        return result
