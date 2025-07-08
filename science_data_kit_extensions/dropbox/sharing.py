"""
Science Data Kit - Dropbox Extension
Sharing Module

This module provides functionality for working with Dropbox shared links,
shared folders, and collaboration metadata.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from dropbox import Dropbox
from dropbox.sharing import (
    SharedLinkMetadata,
    ListSharedLinksResult,
    SharedFolderMetadata,
    ListFoldersResult,
    MembershipInfo,
    AccessLevel,
    SharedFileMembers,
    SharedFolderMembers
)
from dropbox.exceptions import ApiError

from .connector import DropboxConnector

logger = logging.getLogger(__name__)

class DropboxSharingManager:
    """
    Class for managing Dropbox shared links and shared folders.
    
    This class provides methods for creating, listing, and managing shared links
    and shared folders, as well as extracting collaboration metadata.
    """
    
    def __init__(self, connector: DropboxConnector):
        """
        Initialize the sharing manager.
        
        Args:
            connector: DropboxConnector instance for API access
        """
        self.connector = connector
        
        # Ensure connector is connected
        if not connector.is_connected():
            raise ConnectionError("Dropbox connector is not connected")
            
        self.client = connector.client
    
    def list_shared_links(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List shared links.
        
        Args:
            path: Optional path to filter by
            
        Returns:
            List of shared link metadata dictionaries
        """
        try:
            # Ensure path starts with a slash if provided
            if path and not path.startswith('/'):
                path = f"/{path}"
                
            # List shared links
            result = self.client.sharing_list_shared_links(path)
            
            # Process shared links
            shared_links = []
            for link in result.links:
                shared_links.append(self._process_shared_link_metadata(link))
                
            # Continue fetching if there are more links
            while result.has_more:
                result = self.client.sharing_list_shared_links(path, result.cursor)
                
                for link in result.links:
                    shared_links.append(self._process_shared_link_metadata(link))
                    
            return shared_links
        except ApiError as e:
            logger.error(f"Error listing shared links: {e}")
            raise
            
    def _process_shared_link_metadata(self, link: SharedLinkMetadata) -> Dict[str, Any]:
        """
        Process shared link metadata into a dictionary.
        
        Args:
            link: SharedLinkMetadata object
            
        Returns:
            Dictionary with shared link metadata
        """
        metadata = {
            'url': link.url,
            'name': link.name,
            'path_lower': link.path_lower,
            'link_permissions': {
                'can_revoke': link.link_permissions.can_revoke,
                'resolved_visibility': link.link_permissions.resolved_visibility._tag,
                'requested_visibility': link.link_permissions.requested_visibility._tag if hasattr(link.link_permissions, 'requested_visibility') else None,
                'allow_download': link.link_permissions.allow_download
            },
            'expires': link.expires.strftime('%Y-%m-%d %H:%M:%S') if hasattr(link, 'expires') and link.expires else None
        }
        
        # Add team member info if available
        if hasattr(link, 'team_member_info') and link.team_member_info:
            metadata['team_member_info'] = {
                'team_member_id': link.team_member_info.team_member_id,
                'display_name': link.team_member_info.display_name
            }
            
        return metadata
    
    def create_shared_link(
        self, 
        path: str, 
        requested_visibility: str = "public", 
        allow_download: bool = True,
        expires: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a shared link for a file or folder.
        
        Args:
            path: Path to the file or folder
            requested_visibility: Requested visibility (public, team_only, or password)
            allow_download: Whether to allow downloads
            expires: Optional expiration date (format: YYYY-MM-DD)
            
        Returns:
            Shared link metadata dictionary
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            # Map visibility string to enum
            visibility_map = {
                "public": "public",
                "team_only": "team_only",
                "password": "password"
            }
            
            if requested_visibility not in visibility_map:
                raise ValueError(f"Invalid visibility: {requested_visibility}. Must be one of: {', '.join(visibility_map.keys())}")
                
            # Create settings
            settings = {
                "requested_visibility": visibility_map[requested_visibility],
                "audience": "public",
                "access": "viewer",
                "allow_download": allow_download
            }
            
            # Add expiration if provided
            if expires:
                from datetime import datetime
                try:
                    expiration = datetime.strptime(expires, '%Y-%m-%d')
                    settings["expires"] = expiration
                except ValueError:
                    raise ValueError("Invalid expiration date format. Use YYYY-MM-DD.")
            
            # Create shared link
            link = self.client.sharing_create_shared_link_with_settings(path, settings)
            
            return self._process_shared_link_metadata(link)
        except ApiError as e:
            logger.error(f"Error creating shared link: {e}")
            raise
            
    def revoke_shared_link(self, url: str) -> bool:
        """
        Revoke a shared link.
        
        Args:
            url: URL of the shared link
            
        Returns:
            True if successful
        """
        try:
            self.client.sharing_revoke_shared_link(url)
            return True
        except ApiError as e:
            logger.error(f"Error revoking shared link: {e}")
            raise
            
    def list_shared_folders(self) -> List[Dict[str, Any]]:
        """
        List shared folders.
        
        Returns:
            List of shared folder metadata dictionaries
        """
        try:
            # List shared folders
            result = self.client.sharing_list_folders()
            
            # Process shared folders
            shared_folders = []
            for folder in result.entries:
                shared_folders.append(self._process_shared_folder_metadata(folder))
                
            # Continue fetching if there are more folders
            while result.cursor:
                result = self.client.sharing_list_folders_continue(result.cursor)
                
                for folder in result.entries:
                    shared_folders.append(self._process_shared_folder_metadata(folder))
                    
            return shared_folders
        except ApiError as e:
            logger.error(f"Error listing shared folders: {e}")
            raise
            
    def _process_shared_folder_metadata(self, folder: SharedFolderMetadata) -> Dict[str, Any]:
        """
        Process shared folder metadata into a dictionary.
        
        Args:
            folder: SharedFolderMetadata object
            
        Returns:
            Dictionary with shared folder metadata
        """
        return {
            'shared_folder_id': folder.shared_folder_id,
            'name': folder.name,
            'path_lower': folder.path_lower if hasattr(folder, 'path_lower') else None,
            'access_type': folder.access_type._tag,
            'is_team_folder': folder.is_team_folder if hasattr(folder, 'is_team_folder') else False,
            'policy': {
                'acl_update_policy': folder.policy.acl_update_policy._tag,
                'shared_link_policy': folder.policy.shared_link_policy._tag,
                'member_policy': folder.policy.member_policy._tag if hasattr(folder.policy, 'member_policy') else None,
                'resolved_member_policy': folder.policy.resolved_member_policy._tag if hasattr(folder.policy, 'resolved_member_policy') else None
            },
            'owner_team': {
                'id': folder.owner_team.id,
                'name': folder.owner_team.name
            } if hasattr(folder, 'owner_team') and folder.owner_team else None,
            'parent_shared_folder_id': folder.parent_shared_folder_id if hasattr(folder, 'parent_shared_folder_id') else None
        }
    
    def get_shared_folder_metadata(self, shared_folder_id: str) -> Dict[str, Any]:
        """
        Get metadata for a shared folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            
        Returns:
            Shared folder metadata dictionary
        """
        try:
            # Get shared folder metadata
            folder = self.client.sharing_get_folder_metadata(shared_folder_id)
            
            return self._process_shared_folder_metadata(folder)
        except ApiError as e:
            logger.error(f"Error getting shared folder metadata: {e}")
            raise
            
    def create_shared_folder(
        self, 
        path: str, 
        acl_update_policy: str = "owner",
        force_async: bool = False
    ) -> Dict[str, Any]:
        """
        Create a shared folder.
        
        Args:
            path: Path to the folder
            acl_update_policy: ACL update policy (owner, editors)
            force_async: Whether to force asynchronous creation
            
        Returns:
            Shared folder metadata dictionary
        """
        try:
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = f"/{path}"
                
            # Map policy string to enum
            policy_map = {
                "owner": "owner",
                "editors": "editors"
            }
            
            if acl_update_policy not in policy_map:
                raise ValueError(f"Invalid ACL update policy: {acl_update_policy}. Must be one of: {', '.join(policy_map.keys())}")
                
            # Create shared folder
            result = self.client.sharing_share_folder(
                path,
                acl_update_policy=policy_map[acl_update_policy],
                force_async=force_async
            )
            
            # Check if complete or async job
            if result.is_complete():
                folder = result.get_complete()
                return self._process_shared_folder_metadata(folder)
            else:
                # Return async job ID
                return {
                    'async_job_id': result.get_async_job_id()
                }
        except ApiError as e:
            logger.error(f"Error creating shared folder: {e}")
            raise
            
    def unshare_folder(self, shared_folder_id: str, leave_a_copy: bool = False) -> bool:
        """
        Unshare a folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            leave_a_copy: Whether to leave a copy of the folder
            
        Returns:
            True if successful
        """
        try:
            # Unshare folder
            self.client.sharing_unshare_folder(shared_folder_id, leave_a_copy)
            return True
        except ApiError as e:
            logger.error(f"Error unsharing folder: {e}")
            raise
            
    def get_file_members(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get members with access to a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of member dictionaries
        """
        try:
            # Ensure path starts with a slash
            if not file_path.startswith('/'):
                file_path = f"/{file_path}"
                
            # Get file members
            result = self.client.sharing_list_file_members(file_path)
            
            # Process members
            return self._process_members(result)
        except ApiError as e:
            logger.error(f"Error getting file members: {e}")
            raise
            
    def get_folder_members(self, shared_folder_id: str) -> List[Dict[str, Any]]:
        """
        Get members with access to a shared folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            
        Returns:
            List of member dictionaries
        """
        try:
            # Get folder members
            result = self.client.sharing_list_folder_members(shared_folder_id)
            
            # Process members
            return self._process_members(result)
        except ApiError as e:
            logger.error(f"Error getting folder members: {e}")
            raise
            
    def _process_members(self, members_info: Union[SharedFileMembers, SharedFolderMembers]) -> List[Dict[str, Any]]:
        """
        Process members info into a list of dictionaries.
        
        Args:
            members_info: SharedFileMembers or SharedFolderMembers object
            
        Returns:
            List of member dictionaries
        """
        members = []
        
        # Process users
        for user in members_info.users:
            members.append({
                'type': 'user',
                'access_type': user.access_type._tag,
                'user': {
                    'account_id': user.user.account_id,
                    'email': user.user.email,
                    'display_name': user.user.display_name
                },
                'is_inherited': user.is_inherited if hasattr(user, 'is_inherited') else None,
                'time_invited': user.time_invited.strftime('%Y-%m-%d %H:%M:%S') if hasattr(user, 'time_invited') and user.time_invited else None
            })
            
        # Process groups
        if hasattr(members_info, 'groups'):
            for group in members_info.groups:
                members.append({
                    'type': 'group',
                    'access_type': group.access_type._tag,
                    'group': {
                        'group_id': group.group.group_id,
                        'group_name': group.group.group_name,
                        'group_type': group.group.group_type._tag if hasattr(group.group, 'group_type') else None
                    },
                    'is_inherited': group.is_inherited if hasattr(group, 'is_inherited') else None
                })
                
        # Process invitees
        if hasattr(members_info, 'invitees'):
            for invitee in members_info.invitees:
                members.append({
                    'type': 'invitee',
                    'access_type': invitee.access_type._tag,
                    'invitee': {
                        'email': invitee.invitee.email
                    },
                    'is_inherited': invitee.is_inherited if hasattr(invitee, 'is_inherited') else None
                })
                
        return members
        
    def add_folder_member(
        self, 
        shared_folder_id: str, 
        email: str, 
        access_level: str = "viewer",
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Add a member to a shared folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            email: Email of the user to add
            access_level: Access level (viewer, editor, owner)
            custom_message: Optional custom message
            
        Returns:
            True if successful
        """
        try:
            # Map access level string to enum
            access_map = {
                "viewer": "viewer",
                "editor": "editor",
                "owner": "owner"
            }
            
            if access_level not in access_map:
                raise ValueError(f"Invalid access level: {access_level}. Must be one of: {', '.join(access_map.keys())}")
                
            # Create member
            member = {
                ".tag": "email",
                "email": email
            }
            
            # Add member to folder
            self.client.sharing_add_folder_member(
                shared_folder_id,
                [{"member": member, "access_level": access_map[access_level]}],
                custom_message
            )
            
            return True
        except ApiError as e:
            logger.error(f"Error adding folder member: {e}")
            raise
            
    def remove_folder_member(
        self, 
        shared_folder_id: str, 
        email: str, 
        leave_a_copy: bool = False
    ) -> bool:
        """
        Remove a member from a shared folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            email: Email of the user to remove
            leave_a_copy: Whether to leave a copy of the folder
            
        Returns:
            True if successful
        """
        try:
            # Create member
            member = {
                ".tag": "email",
                "email": email
            }
            
            # Remove member from folder
            result = self.client.sharing_remove_folder_member(
                shared_folder_id,
                member,
                leave_a_copy
            )
            
            # Check if complete or async job
            if result.is_complete():
                return True
            else:
                # Return async job ID
                return {
                    'async_job_id': result.get_async_job_id()
                }
        except ApiError as e:
            logger.error(f"Error removing folder member: {e}")
            raise
            
    def update_folder_member(
        self, 
        shared_folder_id: str, 
        email: str, 
        access_level: str
    ) -> bool:
        """
        Update a member's access level in a shared folder.
        
        Args:
            shared_folder_id: ID of the shared folder
            email: Email of the user to update
            access_level: New access level (viewer, editor, owner)
            
        Returns:
            True if successful
        """
        try:
            # Map access level string to enum
            access_map = {
                "viewer": "viewer",
                "editor": "editor",
                "owner": "owner"
            }
            
            if access_level not in access_map:
                raise ValueError(f"Invalid access level: {access_level}. Must be one of: {', '.join(access_map.keys())}")
                
            # Create member
            member = {
                ".tag": "email",
                "email": email
            }
            
            # Update member access level
            self.client.sharing_update_folder_member(
                shared_folder_id,
                member,
                access_map[access_level]
            )
            
            return True
        except ApiError as e:
            logger.error(f"Error updating folder member: {e}")
            raise