"""
File Sharing Utilities for Science Data Kit

This module provides utilities for sharing files between users, including
creating and managing shared files, permissions, and user relationships.
"""

import os
import json
import uuid
from typing import List, Dict, Optional, Union, Any, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path

from science_data_kit.core.api.auth import APIPermission, APIToken


class FilePermission(Enum):
    """Permissions for shared files."""
    VIEW = "view"  # Can view the file but not modify it
    EDIT = "edit"  # Can view and modify the file
    MANAGE = "manage"  # Can view, modify, and manage sharing permissions


class SharedFile:
    """
    A class representing a shared file.
    
    This class contains information about a file that has been shared with other users,
    including the owner, the users it's shared with, and their permissions.
    
    Attributes:
        file_path (str): The path to the file.
        owner_id (str): The ID of the user who owns the file.
        shared_with (Dict[str, FilePermission]): A dictionary mapping user IDs to their permissions.
        created_at (datetime): When the file was first shared.
        updated_at (datetime): When the file's sharing settings were last updated.
        share_id (str): A unique identifier for this shared file.
    """
    
    def __init__(
        self, 
        file_path: str, 
        owner_id: str,
        shared_with: Optional[Dict[str, FilePermission]] = None,
        share_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a SharedFile.
        
        Args:
            file_path: The path to the file.
            owner_id: The ID of the user who owns the file.
            shared_with: A dictionary mapping user IDs to their permissions.
            share_id: A unique identifier for this shared file. If not provided, a new ID will be generated.
            created_at: When the file was first shared. If not provided, the current time will be used.
            updated_at: When the file's sharing settings were last updated. If not provided, the current time will be used.
        """
        self.file_path = file_path
        self.owner_id = owner_id
        self.shared_with = shared_with or {}
        self.share_id = share_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def add_user(self, user_id: str, permission: FilePermission) -> None:
        """
        Add a user to the shared file.
        
        Args:
            user_id: The ID of the user to add.
            permission: The permission to grant to the user.
        """
        self.shared_with[user_id] = permission
        self.updated_at = datetime.now()
    
    def remove_user(self, user_id: str) -> bool:
        """
        Remove a user from the shared file.
        
        Args:
            user_id: The ID of the user to remove.
            
        Returns:
            True if the user was removed, False if the user wasn't in the shared list.
        """
        if user_id in self.shared_with:
            del self.shared_with[user_id]
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_permission(self, user_id: str, permission: FilePermission) -> bool:
        """
        Update a user's permission.
        
        Args:
            user_id: The ID of the user to update.
            permission: The new permission to grant to the user.
            
        Returns:
            True if the permission was updated, False if the user wasn't in the shared list.
        """
        if user_id in self.shared_with:
            self.shared_with[user_id] = permission
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_user_permission(self, user_id: str) -> Optional[FilePermission]:
        """
        Get a user's permission.
        
        Args:
            user_id: The ID of the user to check.
            
        Returns:
            The user's permission, or None if the user doesn't have access.
        """
        return self.shared_with.get(user_id)
    
    def has_permission(self, user_id: str, required_permission: FilePermission) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: The ID of the user to check.
            required_permission: The permission to check for.
            
        Returns:
            True if the user has the required permission, False otherwise.
        """
        # The owner has all permissions
        if user_id == self.owner_id:
            return True
        
        user_permission = self.get_user_permission(user_id)
        if user_permission is None:
            return False
        
        # Check if the user's permission is sufficient
        if required_permission == FilePermission.VIEW:
            # Any permission allows viewing
            return True
        elif required_permission == FilePermission.EDIT:
            # EDIT or MANAGE permission allows editing
            return user_permission in [FilePermission.EDIT, FilePermission.MANAGE]
        elif required_permission == FilePermission.MANAGE:
            # Only MANAGE permission allows managing
            return user_permission == FilePermission.MANAGE
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the shared file to a dictionary.
        
        Returns:
            A dictionary representation of the shared file.
        """
        return {
            "file_path": self.file_path,
            "owner_id": self.owner_id,
            "shared_with": {user_id: perm.value for user_id, perm in self.shared_with.items()},
            "share_id": self.share_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SharedFile':
        """
        Create a SharedFile from a dictionary.
        
        Args:
            data: A dictionary representation of a shared file.
            
        Returns:
            A SharedFile instance.
        """
        shared_with = {
            user_id: FilePermission(perm) 
            for user_id, perm in data.get("shared_with", {}).items()
        }
        
        return cls(
            file_path=data["file_path"],
            owner_id=data["owner_id"],
            shared_with=shared_with,
            share_id=data.get("share_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None
        )


class FileSharingManager:
    """
    A manager for file sharing operations.
    
    This class provides methods for sharing files, managing permissions,
    and retrieving shared files.
    
    Attributes:
        storage_path (str): The path to the file where shared file data is stored.
        shared_files (Dict[str, SharedFile]): A dictionary mapping share IDs to SharedFile objects.
        user_files (Dict[str, List[str]]): A dictionary mapping user IDs to lists of share IDs they have access to.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the FileSharingManager.
        
        Args:
            storage_path: The path to the file where shared file data is stored.
                If not provided, a default path will be used.
        """
        self.storage_path = storage_path or os.path.join(os.path.expanduser("~"), ".sdk_shared_files.json")
        self.shared_files = {}  # share_id -> SharedFile
        self.user_files = {}  # user_id -> [share_id]
        
        # Load existing shared files if the storage file exists
        self._load_shared_files()
    
    def _load_shared_files(self) -> None:
        """Load shared files from the storage file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load shared files
                for share_data in data.get("shared_files", []):
                    shared_file = SharedFile.from_dict(share_data)
                    self.shared_files[shared_file.share_id] = shared_file
                
                # Build user_files index
                self._rebuild_user_files_index()
            except Exception as e:
                print(f"Error loading shared files: {e}")
    
    def _save_shared_files(self) -> None:
        """Save shared files to the storage file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.storage_path)), exist_ok=True)
            
            # Convert shared files to dictionaries
            shared_files_data = [sf.to_dict() for sf in self.shared_files.values()]
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump({"shared_files": shared_files_data}, f, indent=2)
        except Exception as e:
            print(f"Error saving shared files: {e}")
    
    def _rebuild_user_files_index(self) -> None:
        """Rebuild the user_files index from shared_files."""
        self.user_files = {}
        
        for share_id, shared_file in self.shared_files.items():
            # Add owner
            if shared_file.owner_id not in self.user_files:
                self.user_files[shared_file.owner_id] = []
            
            if share_id not in self.user_files[shared_file.owner_id]:
                self.user_files[shared_file.owner_id].append(share_id)
            
            # Add shared users
            for user_id in shared_file.shared_with:
                if user_id not in self.user_files:
                    self.user_files[user_id] = []
                
                if share_id not in self.user_files[user_id]:
                    self.user_files[user_id].append(share_id)
    
    def share_file(
        self, 
        file_path: str, 
        owner_id: str, 
        user_ids: List[str], 
        permission: FilePermission
    ) -> SharedFile:
        """
        Share a file with other users.
        
        Args:
            file_path: The path to the file to share.
            owner_id: The ID of the user who owns the file.
            user_ids: The IDs of the users to share the file with.
            permission: The permission to grant to the users.
            
        Returns:
            The created SharedFile object.
        """
        # Check if the file is already shared
        for shared_file in self.shared_files.values():
            if shared_file.file_path == file_path and shared_file.owner_id == owner_id:
                # Update existing shared file
                for user_id in user_ids:
                    shared_file.add_user(user_id, permission)
                
                self._save_shared_files()
                self._rebuild_user_files_index()
                return shared_file
        
        # Create a new shared file
        shared_with = {user_id: permission for user_id in user_ids}
        shared_file = SharedFile(file_path, owner_id, shared_with)
        
        # Add to shared_files
        self.shared_files[shared_file.share_id] = shared_file
        
        # Update user_files index
        if owner_id not in self.user_files:
            self.user_files[owner_id] = []
        
        self.user_files[owner_id].append(shared_file.share_id)
        
        for user_id in user_ids:
            if user_id not in self.user_files:
                self.user_files[user_id] = []
            
            self.user_files[user_id].append(shared_file.share_id)
        
        # Save changes
        self._save_shared_files()
        
        return shared_file
    
    def unshare_file(self, file_path: str, owner_id: str, user_id: Optional[str] = None) -> bool:
        """
        Unshare a file.
        
        Args:
            file_path: The path to the file to unshare.
            owner_id: The ID of the user who owns the file.
            user_id: The ID of the user to unshare the file with. If None, the file will be unshared with all users.
            
        Returns:
            True if the file was unshared, False otherwise.
        """
        # Find the shared file
        shared_file = None
        for sf in self.shared_files.values():
            if sf.file_path == file_path and sf.owner_id == owner_id:
                shared_file = sf
                break
        
        if shared_file is None:
            return False
        
        if user_id is None:
            # Unshare with all users
            shared_file.shared_with = {}
            
            # Remove from user_files index
            for uid in list(self.user_files.keys()):
                if uid != owner_id and shared_file.share_id in self.user_files[uid]:
                    self.user_files[uid].remove(shared_file.share_id)
                    
                    # Clean up empty user entries
                    if not self.user_files[uid]:
                        del self.user_files[uid]
        else:
            # Unshare with specific user
            if not shared_file.remove_user(user_id):
                return False
            
            # Remove from user_files index
            if user_id in self.user_files and shared_file.share_id in self.user_files[user_id]:
                self.user_files[user_id].remove(shared_file.share_id)
                
                # Clean up empty user entries
                if not self.user_files[user_id]:
                    del self.user_files[user_id]
        
        # Save changes
        self._save_shared_files()
        
        return True
    
    def update_permission(
        self, 
        file_path: str, 
        owner_id: str, 
        user_id: str, 
        permission: FilePermission
    ) -> bool:
        """
        Update a user's permission for a shared file.
        
        Args:
            file_path: The path to the file.
            owner_id: The ID of the user who owns the file.
            user_id: The ID of the user to update.
            permission: The new permission to grant to the user.
            
        Returns:
            True if the permission was updated, False otherwise.
        """
        # Find the shared file
        shared_file = None
        for sf in self.shared_files.values():
            if sf.file_path == file_path and sf.owner_id == owner_id:
                shared_file = sf
                break
        
        if shared_file is None:
            return False
        
        # Update the permission
        if not shared_file.update_permission(user_id, permission):
            return False
        
        # Save changes
        self._save_shared_files()
        
        return True
    
    def get_shared_file(self, file_path: str, owner_id: str) -> Optional[SharedFile]:
        """
        Get a shared file by path and owner.
        
        Args:
            file_path: The path to the file.
            owner_id: The ID of the user who owns the file.
            
        Returns:
            The SharedFile object, or None if the file is not shared.
        """
        for shared_file in self.shared_files.values():
            if shared_file.file_path == file_path and shared_file.owner_id == owner_id:
                return shared_file
        
        return None
    
    def get_shared_file_by_id(self, share_id: str) -> Optional[SharedFile]:
        """
        Get a shared file by ID.
        
        Args:
            share_id: The ID of the shared file.
            
        Returns:
            The SharedFile object, or None if the file is not found.
        """
        return self.shared_files.get(share_id)
    
    def get_user_shared_files(self, user_id: str) -> List[SharedFile]:
        """
        Get all files shared with a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A list of SharedFile objects.
        """
        if user_id not in self.user_files:
            return []
        
        return [
            self.shared_files[share_id] 
            for share_id in self.user_files[user_id] 
            if share_id in self.shared_files
        ]
    
    def get_user_owned_files(self, user_id: str) -> List[SharedFile]:
        """
        Get all files owned by a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A list of SharedFile objects.
        """
        return [
            shared_file 
            for shared_file in self.shared_files.values() 
            if shared_file.owner_id == user_id
        ]
    
    def check_permission(
        self, 
        file_path: str, 
        user_id: str, 
        required_permission: FilePermission
    ) -> bool:
        """
        Check if a user has a specific permission for a file.
        
        Args:
            file_path: The path to the file.
            user_id: The ID of the user to check.
            required_permission: The permission to check for.
            
        Returns:
            True if the user has the required permission, False otherwise.
        """
        # Check all shared files with this path
        for shared_file in self.shared_files.values():
            if shared_file.file_path == file_path:
                # If the user is the owner, they have all permissions
                if shared_file.owner_id == user_id:
                    return True
                
                # Check if the user has the required permission
                if shared_file.has_permission(user_id, required_permission):
                    return True
        
        return False
    
    def get_file_users(self, file_path: str, owner_id: str) -> Dict[str, FilePermission]:
        """
        Get all users who have access to a file.
        
        Args:
            file_path: The path to the file.
            owner_id: The ID of the user who owns the file.
            
        Returns:
            A dictionary mapping user IDs to their permissions.
        """
        shared_file = self.get_shared_file(file_path, owner_id)
        
        if shared_file is None:
            return {}
        
        return shared_file.shared_with.copy()


# API functions for file sharing

def share_file(
    file_path: str, 
    owner_id: str, 
    user_ids: List[str], 
    permission: FilePermission,
    sharing_manager: Optional[FileSharingManager] = None
) -> Tuple[bool, str]:
    """
    Share a file with other users.
    
    Args:
        file_path: The path to the file to share.
        owner_id: The ID of the user who owns the file.
        user_ids: The IDs of the users to share the file with.
        permission: The permission to grant to the users.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A tuple containing:
        - Success flag (True if the file was shared, False otherwise).
        - Message (success or error message).
    """
    try:
        # Validate file path
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Share the file
        shared_file = manager.share_file(file_path, owner_id, user_ids, permission)
        
        return True, f"File shared successfully with {len(user_ids)} user(s)"
    except Exception as e:
        return False, f"Error sharing file: {str(e)}"


def unshare_file(
    file_path: str, 
    owner_id: str, 
    user_id: Optional[str] = None,
    sharing_manager: Optional[FileSharingManager] = None
) -> Tuple[bool, str]:
    """
    Unshare a file.
    
    Args:
        file_path: The path to the file to unshare.
        owner_id: The ID of the user who owns the file.
        user_id: The ID of the user to unshare the file with. If None, the file will be unshared with all users.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A tuple containing:
        - Success flag (True if the file was unshared, False otherwise).
        - Message (success or error message).
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Unshare the file
        if manager.unshare_file(file_path, owner_id, user_id):
            if user_id is None:
                return True, "File unshared with all users"
            else:
                return True, f"File unshared with user {user_id}"
        else:
            return False, "File not found or not shared"
    except Exception as e:
        return False, f"Error unsharing file: {str(e)}"


def update_permission(
    file_path: str, 
    owner_id: str, 
    user_id: str, 
    permission: FilePermission,
    sharing_manager: Optional[FileSharingManager] = None
) -> Tuple[bool, str]:
    """
    Update a user's permission for a shared file.
    
    Args:
        file_path: The path to the file.
        owner_id: The ID of the user who owns the file.
        user_id: The ID of the user to update.
        permission: The new permission to grant to the user.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A tuple containing:
        - Success flag (True if the permission was updated, False otherwise).
        - Message (success or error message).
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Update the permission
        if manager.update_permission(file_path, owner_id, user_id, permission):
            return True, f"Permission updated to {permission.value} for user {user_id}"
        else:
            return False, "File not found or user not shared with"
    except Exception as e:
        return False, f"Error updating permission: {str(e)}"


def get_user_shared_files(
    user_id: str,
    sharing_manager: Optional[FileSharingManager] = None
) -> List[Dict[str, Any]]:
    """
    Get all files shared with a user.
    
    Args:
        user_id: The ID of the user.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A list of dictionaries containing information about each shared file.
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Get shared files
        shared_files = manager.get_user_shared_files(user_id)
        
        # Convert to dictionaries
        return [
            {
                "file_path": sf.file_path,
                "owner_id": sf.owner_id,
                "permission": sf.get_user_permission(user_id).value if sf.get_user_permission(user_id) else None,
                "share_id": sf.share_id,
                "created_at": sf.created_at.isoformat(),
                "updated_at": sf.updated_at.isoformat()
            }
            for sf in shared_files
        ]
    except Exception as e:
        print(f"Error getting shared files: {str(e)}")
        return []


def get_user_owned_files(
    user_id: str,
    sharing_manager: Optional[FileSharingManager] = None
) -> List[Dict[str, Any]]:
    """
    Get all files owned by a user.
    
    Args:
        user_id: The ID of the user.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A list of dictionaries containing information about each owned file.
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Get owned files
        owned_files = manager.get_user_owned_files(user_id)
        
        # Convert to dictionaries
        return [
            {
                "file_path": sf.file_path,
                "shared_with": {uid: perm.value for uid, perm in sf.shared_with.items()},
                "share_id": sf.share_id,
                "created_at": sf.created_at.isoformat(),
                "updated_at": sf.updated_at.isoformat()
            }
            for sf in owned_files
        ]
    except Exception as e:
        print(f"Error getting owned files: {str(e)}")
        return []


def check_permission(
    file_path: str, 
    user_id: str, 
    required_permission: FilePermission,
    sharing_manager: Optional[FileSharingManager] = None
) -> bool:
    """
    Check if a user has a specific permission for a file.
    
    Args:
        file_path: The path to the file.
        user_id: The ID of the user to check.
        required_permission: The permission to check for.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        True if the user has the required permission, False otherwise.
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Check permission
        return manager.check_permission(file_path, user_id, required_permission)
    except Exception as e:
        print(f"Error checking permission: {str(e)}")
        return False


def get_file_users(
    file_path: str, 
    owner_id: str,
    sharing_manager: Optional[FileSharingManager] = None
) -> Dict[str, str]:
    """
    Get all users who have access to a file.
    
    Args:
        file_path: The path to the file.
        owner_id: The ID of the user who owns the file.
        sharing_manager: The FileSharingManager to use. If None, a new one will be created.
        
    Returns:
        A dictionary mapping user IDs to their permission values.
    """
    try:
        # Create or use sharing manager
        manager = sharing_manager or FileSharingManager()
        
        # Get file users
        users = manager.get_file_users(file_path, owner_id)
        
        # Convert permissions to strings
        return {uid: perm.value for uid, perm in users.items()}
    except Exception as e:
        print(f"Error getting file users: {str(e)}")
        return {}