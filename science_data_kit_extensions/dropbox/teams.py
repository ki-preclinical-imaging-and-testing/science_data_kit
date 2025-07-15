"""
Science Data Kit - Dropbox Extension
Teams Module

This module provides functionality for working with Dropbox team folders
and team management features.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from dropbox import Dropbox
from dropbox.team import (
    GroupsListResult,
    GroupsMembersListResult,
    MembersListResult,
    GroupMemberInfo,
    TeamFolderListResult,
    TeamFolderMetadata,
    TeamFolderListError
)
from dropbox.exceptions import ApiError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxTeamManager:
    """
    Class for managing Dropbox team folders and team members.

    This class provides methods for listing, creating, and managing team folders,
    as well as managing team members and their permissions.

    Note: Most methods require Dropbox Business/Team admin access.
    """

    def __init__(self, connector: DropboxConnector):
        """
        Initialize the team manager.

        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector

        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")

        self.client = connector.client

        # Check if this is a team account
        account_info = connector.get_account_info()
        self.is_team_account = account_info.get('team') is not None
        self.team_member_id = account_info.get('team_member_id')

        if not self.is_team_account:
            logger.warning("This is not a Dropbox Business/Team account. Team management features will be limited.")

    def list_team_folders(self) -> List[Dict[str, Any]]:
        """
        List all team folders.

        Returns:
            List of team folder metadata dictionaries
        """
        if not self.is_team_account:
            logger.warning("Team folder listing requires a Dropbox Business/Team account")
            return []

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # List team folders
            result = team_client.team_team_folder_list()

            # Process team folders
            team_folders = []
            for folder in result.team_folders:
                team_folders.append({
                    'id': folder.team_folder_id,
                    'name': folder.name,
                    'status': folder.status._tag,
                    'is_team_shared_dropbox': folder.is_team_shared_dropbox,
                    'sync_setting': folder.sync_setting._tag if hasattr(folder, 'sync_setting') else None,
                    'content_sync_settings': folder.content_sync_settings._tag if hasattr(folder, 'content_sync_settings') else None
                })

            return team_folders
        except ApiError as e:
            logger.error(f"Error listing team folders: {e}")
            raise

    def get_team_folder_metadata(self, team_folder_id: str) -> Dict[str, Any]:
        """
        Get metadata for a team folder.

        Args:
            team_folder_id: ID of the team folder

        Returns:
            Team folder metadata dictionary
        """
        if not self.is_team_account:
            logger.warning("Team folder operations require a Dropbox Business/Team account")
            raise ValueError("Team folder operations require a Dropbox Business/Team account")

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # Get team folder metadata
            result = team_client.team_team_folder_get_info([team_folder_id])

            if not result or not result[0].is_success():
                error = result[0].get_access_error() if result else "Unknown error"
                raise ValueError(f"Error getting team folder info: {error}")

            folder = result[0].get_success()

            return {
                'id': folder.team_folder_id,
                'name': folder.name,
                'status': folder.status._tag,
                'is_team_shared_dropbox': folder.is_team_shared_dropbox,
                'sync_setting': folder.sync_setting._tag if hasattr(folder, 'sync_setting') else None,
                'content_sync_settings': folder.content_sync_settings._tag if hasattr(folder, 'content_sync_settings') else None
            }
        except ApiError as e:
            logger.error(f"Error getting team folder metadata: {e}")
            raise

    def create_team_folder(self, name: str) -> Dict[str, Any]:
        """
        Create a new team folder.

        Args:
            name: Name for the new team folder

        Returns:
            Team folder metadata dictionary
        """
        if not self.is_team_account:
            logger.warning("Team folder creation requires a Dropbox Business/Team account")
            raise ValueError("Team folder creation requires a Dropbox Business/Team account")

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # Create team folder
            result = team_client.team_team_folder_create(name)

            return {
                'id': result.team_folder_id,
                'name': result.name,
                'status': result.status._tag,
                'is_team_shared_dropbox': result.is_team_shared_dropbox,
                'sync_setting': result.sync_setting._tag if hasattr(result, 'sync_setting') else None,
                'content_sync_settings': result.content_sync_settings._tag if hasattr(result, 'content_sync_settings') else None
            }
        except ApiError as e:
            logger.error(f"Error creating team folder: {e}")
            raise

    def archive_team_folder(self, team_folder_id: str) -> Dict[str, Any]:
        """
        Archive a team folder.

        Args:
            team_folder_id: ID of the team folder to archive

        Returns:
            Team folder metadata dictionary
        """
        if not self.is_team_account:
            logger.warning("Team folder operations require a Dropbox Business/Team account")
            raise ValueError("Team folder operations require a Dropbox Business/Team account")

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # Archive team folder
            result = team_client.team_team_folder_archive(team_folder_id)

            return {
                'id': result.team_folder_id,
                'name': result.name,
                'status': result.status._tag,
                'is_team_shared_dropbox': result.is_team_shared_dropbox,
                'sync_setting': result.sync_setting._tag if hasattr(result, 'sync_setting') else None,
                'content_sync_settings': result.content_sync_settings._tag if hasattr(result, 'content_sync_settings') else None
            }
        except ApiError as e:
            logger.error(f"Error archiving team folder: {e}")
            raise

    def permanently_delete_team_folder(self, team_folder_id: str) -> bool:
        """
        Permanently delete a team folder.

        Args:
            team_folder_id: ID of the team folder to delete

        Returns:
            True if successful
        """
        if not self.is_team_account:
            logger.warning("Team folder operations require a Dropbox Business/Team account")
            raise ValueError("Team folder operations require a Dropbox Business/Team account")

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # Permanently delete team folder
            team_client.team_team_folder_permanently_delete(team_folder_id)

            return True
        except ApiError as e:
            logger.error(f"Error permanently deleting team folder: {e}")
            raise

    def list_team_members(self) -> List[Dict[str, Any]]:
        """
        List all team members.

        Returns:
            List of team member dictionaries
        """
        if not self.is_team_account:
            logger.warning("Team member listing requires a Dropbox Business/Team account")
            return []

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # List team members
            result = team_client.team_members_list()

            # Process team members
            members = []
            for member in result.members:
                members.append({
                    'team_member_id': member.profile.team_member_id,
                    'email': member.profile.email,
                    'name': {
                        'given_name': member.profile.name.given_name,
                        'surname': member.profile.name.surname,
                        'display_name': member.profile.name.display_name
                    },
                    'role': member.role._tag,
                    'status': member.profile.status._tag
                })

            # Continue fetching if there are more members
            while result.has_more:
                result = team_client.team_members_list_continue(result.cursor)

                for member in result.members:
                    members.append({
                        'team_member_id': member.profile.team_member_id,
                        'email': member.profile.email,
                        'name': {
                            'given_name': member.profile.name.given_name,
                            'surname': member.profile.name.surname,
                            'display_name': member.profile.name.display_name
                        },
                        'role': member.role._tag,
                        'status': member.profile.status._tag
                    })

            return members
        except ApiError as e:
            logger.error(f"Error listing team members: {e}")
            raise

    def list_groups(self) -> List[Dict[str, Any]]:
        """
        List all groups in the team.

        Returns:
            List of group dictionaries
        """
        if not self.is_team_account:
            logger.warning("Group listing requires a Dropbox Business/Team account")
            return []

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # List groups
            result = team_client.team_groups_list()

            # Process groups
            groups = []
            for group in result.groups:
                groups.append({
                    'group_id': group.group_id,
                    'name': group.group_name,
                    'member_count': group.member_count,
                    'group_type': group.group_type._tag if hasattr(group, 'group_type') else None,
                    'group_external_id': group.group_external_id if hasattr(group, 'group_external_id') else None
                })

            # Continue fetching if there are more groups
            while result.has_more:
                result = team_client.team_groups_list_continue(result.cursor)

                for group in result.groups:
                    groups.append({
                        'group_id': group.group_id,
                        'name': group.group_name,
                        'member_count': group.member_count,
                        'group_type': group.group_type._tag if hasattr(group, 'group_type') else None,
                        'group_external_id': group.group_external_id if hasattr(group, 'group_external_id') else None
                    })

            return groups
        except ApiError as e:
            logger.error(f"Error listing groups: {e}")
            raise

    def list_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """
        List members of a group.

        Args:
            group_id: ID of the group

        Returns:
            List of group member dictionaries
        """
        if not self.is_team_account:
            logger.warning("Group member listing requires a Dropbox Business/Team account")
            return []

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # List group members
            result = team_client.team_groups_members_list(group_id)

            # Process group members
            members = []
            for member in result.members:
                if member.user:
                    members.append({
                        'team_member_id': member.user.team_member_id,
                        'email': member.user.email,
                        'name': {
                            'given_name': member.user.display_name.given_name,
                            'surname': member.user.display_name.surname,
                            'display_name': member.user.display_name.display_name
                        },
                        'access_type': member.access_type._tag
                    })

            # Continue fetching if there are more members
            while result.has_more:
                result = team_client.team_groups_members_list_continue(result.cursor)

                for member in result.members:
                    if member.user:
                        members.append({
                            'team_member_id': member.user.team_member_id,
                            'email': member.user.email,
                            'name': {
                                'given_name': member.user.display_name.given_name,
                                'surname': member.user.display_name.surname,
                                'display_name': member.user.display_name.display_name
                            },
                            'access_type': member.access_type._tag
                        })

            return members
        except ApiError as e:
            logger.error(f"Error listing group members: {e}")
            raise

    def get_team_folder_permissions(self, team_folder_id: str) -> List[Dict[str, Any]]:
        """
        Get permissions for a team folder.

        Args:
            team_folder_id: ID of the team folder

        Returns:
            List of permission dictionaries
        """
        if not self.is_team_account:
            logger.warning("Team folder operations require a Dropbox Business/Team account")
            raise ValueError("Team folder operations require a Dropbox Business/Team account")

        try:
            # Get team client
            team_client = self.client.with_path_root(Dropbox.PathRoot.team_member_id(self.team_member_id))

            # Get team folder permissions
            result = team_client.sharing_list_folder_members(team_folder_id)

            # Process permissions
            permissions = []

            # Process users
            for user in result.users:
                permissions.append({
                    'type': 'user',
                    'user_id': user.user.account_id,
                    'email': user.user.email,
                    'display_name': user.user.display_name,
                    'access_type': user.access_type._tag,
                    'is_inherited': user.is_inherited
                })

            # Process groups
            for group in result.groups:
                permissions.append({
                    'type': 'group',
                    'group_id': group.group.group_id,
                    'group_name': group.group.group_name,
                    'access_type': group.access_type._tag,
                    'is_inherited': group.is_inherited
                })

            # Process invitees
            for invitee in result.invitees:
                permissions.append({
                    'type': 'invitee',
                    'email': invitee.invitee.email,
                    'access_type': invitee.access_type._tag,
                    'is_inherited': invitee.is_inherited
                })

            return permissions
        except ApiError as e:
            logger.error(f"Error getting team folder permissions: {e}")
            raise
