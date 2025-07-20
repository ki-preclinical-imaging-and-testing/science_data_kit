"""
Dropbox Sharing Management Page for Science Data Kit

This module provides a Streamlit page for managing Dropbox shared links and shared folders.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.sharing import DropboxSharingManager


def dropbox_sharing_page():
    """
    Render the Dropbox sharing management page.
    """
    st.title("Dropbox Sharing Management")

    # Check if connected to Dropbox
    if "dropbox_connector" not in st.session_state:
        st.warning("Not connected to Dropbox. Please connect first.")
        st.info("Go to the Dropbox Connect page to set up your connection.")
        return

    connector = st.session_state["dropbox_connector"]
    if not connector.is_connected():
        st.error("Dropbox connection lost. Please reconnect.")
        st.info("Go to the Dropbox Connect page to set up your connection.")
        return

    # Initialize sharing manager
    try:
        sharing_manager = DropboxSharingManager(connector)
    except Exception as e:
        st.error(f"Error initializing sharing manager: {str(e)}")
        return

    # Create tabs for different sharing management features
    tab1, tab2 = st.tabs(["Shared Links", "Shared Folders"])

    with tab1:
        st.header("Shared Links")

        # Refresh button for shared links
        if st.button("Refresh Shared Links"):
            st.experimental_rerun()

        # Path filter for shared links
        path_filter = st.text_input("Filter by path (optional)", key="shared_links_path_filter")

        try:
            # List shared links
            shared_links = sharing_manager.list_shared_links(path_filter if path_filter else None)

            if shared_links:
                # Convert to DataFrame for display
                links_data = []
                for link in shared_links:
                    links_data.append({
                        "Name": link["name"],
                        "Path": link["path_lower"],
                        "URL": link["url"],
                        "Visibility": link["link_permissions"]["resolved_visibility"],
                        "Allow Download": "Yes" if link["link_permissions"]["allow_download"] else "No",
                        "Expires": link["expires"] if link["expires"] else "Never"
                    })

                links_df = pd.DataFrame(links_data)
                st.dataframe(links_df, use_container_width=True)

                # Shared link actions
                st.subheader("Shared Link Actions")

                # Select a shared link
                selected_link = st.selectbox(
                    "Select a shared link",
                    [link["name"] for link in shared_links],
                    key="selected_shared_link"
                )

                if selected_link:
                    selected_link_data = next((l for l in shared_links if l["name"] == selected_link), None)

                    if selected_link_data:
                        # Display link details
                        st.subheader("Link Details")
                        col1, col2 = st.columns(2)
                        col1.write(f"**Name:** {selected_link_data['name']}")
                        col1.write(f"**Path:** {selected_link_data['path_lower']}")
                        col1.write(f"**URL:** {selected_link_data['url']}")
                        col2.write(f"**Visibility:** {selected_link_data['link_permissions']['resolved_visibility']}")
                        col2.write(f"**Allow Download:** {'Yes' if selected_link_data['link_permissions']['allow_download'] else 'No'}")
                        col2.write(f"**Expires:** {selected_link_data['expires'] if selected_link_data['expires'] else 'Never'}")

                        # Copy URL button
                        st.text_input("Copy URL", value=selected_link_data["url"], key="copy_url")

                        # Action buttons
                        st.subheader("Actions")
                        col1, col2 = st.columns(2)

                        # Revoke button with confirmation
                        revoke_confirmed = False
                        if col1.button("Revoke Link"):
                            revoke_confirmed = True

                        if revoke_confirmed:
                            st.warning(f"Are you sure you want to revoke the shared link for '{selected_link_data['name']}'? This action cannot be undone.")
                            col1, col2 = st.columns(2)
                            if col1.button("Yes, Revoke"):
                                try:
                                    result = sharing_manager.revoke_shared_link(selected_link_data["url"])
                                    st.success(f"Shared link for '{selected_link_data['name']}' revoked successfully.")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Error revoking shared link: {str(e)}")
                            if col2.button("Cancel"):
                                st.experimental_rerun()

                # Create new shared link
                st.subheader("Create New Shared Link")
                new_link_path = st.text_input("Path", key="new_shared_link_path")
                
                col1, col2 = st.columns(2)
                visibility = col1.selectbox(
                    "Visibility",
                    ["public", "team_only", "password"],
                    key="new_shared_link_visibility"
                )
                allow_download = col2.checkbox("Allow Download", value=True, key="new_shared_link_allow_download")
                
                expires = st.text_input(
                    "Expiration Date (YYYY-MM-DD, optional)",
                    key="new_shared_link_expires"
                )
                
                if st.button("Create Link"):
                    if new_link_path:
                        try:
                            result = sharing_manager.create_shared_link(
                                new_link_path,
                                requested_visibility=visibility,
                                allow_download=allow_download,
                                expires=expires if expires else None
                            )
                            st.success(f"Shared link created successfully: {result['url']}")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating shared link: {str(e)}")
                    else:
                        st.warning("Please enter a path.")
            else:
                st.info("No shared links found.")
                
                # Create new shared link
                st.subheader("Create New Shared Link")
                new_link_path = st.text_input("Path", key="new_shared_link_path")
                
                col1, col2 = st.columns(2)
                visibility = col1.selectbox(
                    "Visibility",
                    ["public", "team_only", "password"],
                    key="new_shared_link_visibility"
                )
                allow_download = col2.checkbox("Allow Download", value=True, key="new_shared_link_allow_download")
                
                expires = st.text_input(
                    "Expiration Date (YYYY-MM-DD, optional)",
                    key="new_shared_link_expires"
                )
                
                if st.button("Create Link"):
                    if new_link_path:
                        try:
                            result = sharing_manager.create_shared_link(
                                new_link_path,
                                requested_visibility=visibility,
                                allow_download=allow_download,
                                expires=expires if expires else None
                            )
                            st.success(f"Shared link created successfully: {result['url']}")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating shared link: {str(e)}")
                    else:
                        st.warning("Please enter a path.")
        except Exception as e:
            st.error(f"Error listing shared links: {str(e)}")

    with tab2:
        st.header("Shared Folders")

        # Refresh button for shared folders
        if st.button("Refresh Shared Folders"):
            st.experimental_rerun()

        try:
            # List shared folders
            shared_folders = sharing_manager.list_shared_folders()

            if shared_folders:
                # Convert to DataFrame for display
                folders_data = []
                for folder in shared_folders:
                    folders_data.append({
                        "Name": folder["name"],
                        "Path": folder["path_lower"] if folder["path_lower"] else "N/A",
                        "Access Type": folder["access_type"],
                        "Is Team Folder": "Yes" if folder["is_team_folder"] else "No",
                        "ACL Update Policy": folder["policy"]["acl_update_policy"]
                    })

                folders_df = pd.DataFrame(folders_data)
                st.dataframe(folders_df, use_container_width=True)

                # Shared folder actions
                st.subheader("Shared Folder Actions")

                # Select a shared folder
                selected_folder = st.selectbox(
                    "Select a shared folder",
                    [folder["name"] for folder in shared_folders],
                    key="selected_shared_folder"
                )

                if selected_folder:
                    selected_folder_data = next((f for f in shared_folders if f["name"] == selected_folder), None)

                    if selected_folder_data:
                        # Display folder details
                        st.subheader("Folder Details")
                        col1, col2 = st.columns(2)
                        col1.write(f"**ID:** {selected_folder_data['shared_folder_id']}")
                        col1.write(f"**Name:** {selected_folder_data['name']}")
                        col1.write(f"**Path:** {selected_folder_data['path_lower'] if selected_folder_data['path_lower'] else 'N/A'}")
                        col2.write(f"**Access Type:** {selected_folder_data['access_type']}")
                        col2.write(f"**Is Team Folder:** {'Yes' if selected_folder_data['is_team_folder'] else 'No'}")
                        col2.write(f"**ACL Update Policy:** {selected_folder_data['policy']['acl_update_policy']}")

                        # Folder members
                        st.subheader("Folder Members")
                        
                        try:
                            # Get folder members
                            folder_members = sharing_manager.get_folder_members(selected_folder_data["shared_folder_id"])
                            
                            if folder_members:
                                # Separate by type
                                user_members = [m for m in folder_members if m["type"] == "user"]
                                group_members = [m for m in folder_members if m["type"] == "group"]
                                invitee_members = [m for m in folder_members if m["type"] == "invitee"]
                                
                                # Display user members
                                if user_members:
                                    st.subheader("Users")
                                    user_members_data = []
                                    for member in user_members:
                                        user_members_data.append({
                                            "Email": member["user"]["email"],
                                            "Display Name": member["user"]["display_name"],
                                            "Access Type": member["access_type"],
                                            "Inherited": "Yes" if member["is_inherited"] else "No"
                                        })
                                    
                                    user_members_df = pd.DataFrame(user_members_data)
                                    st.dataframe(user_members_df, use_container_width=True)
                                
                                # Display group members
                                if group_members:
                                    st.subheader("Groups")
                                    group_members_data = []
                                    for member in group_members:
                                        group_members_data.append({
                                            "Group Name": member["group"]["group_name"],
                                            "Access Type": member["access_type"],
                                            "Inherited": "Yes" if member["is_inherited"] else "No"
                                        })
                                    
                                    group_members_df = pd.DataFrame(group_members_data)
                                    st.dataframe(group_members_df, use_container_width=True)
                                
                                # Display invitee members
                                if invitee_members:
                                    st.subheader("Invitees")
                                    invitee_members_data = []
                                    for member in invitee_members:
                                        invitee_members_data.append({
                                            "Email": member["invitee"]["email"],
                                            "Access Type": member["access_type"],
                                            "Inherited": "Yes" if member["is_inherited"] else "No"
                                        })
                                    
                                    invitee_members_df = pd.DataFrame(invitee_members_data)
                                    st.dataframe(invitee_members_df, use_container_width=True)
                                
                                # Add member form
                                st.subheader("Add Member")
                                new_member_email = st.text_input("Email", key="new_member_email")
                                new_member_access = st.selectbox(
                                    "Access Level",
                                    ["viewer", "editor", "owner"],
                                    key="new_member_access"
                                )
                                new_member_message = st.text_area("Custom Message (optional)", key="new_member_message")
                                
                                if st.button("Add Member"):
                                    if new_member_email:
                                        try:
                                            result = sharing_manager.add_folder_member(
                                                selected_folder_data["shared_folder_id"],
                                                new_member_email,
                                                access_level=new_member_access,
                                                custom_message=new_member_message if new_member_message else None
                                            )
                                            st.success(f"Member '{new_member_email}' added successfully.")
                                            st.experimental_rerun()
                                        except Exception as e:
                                            st.error(f"Error adding member: {str(e)}")
                                    else:
                                        st.warning("Please enter an email address.")
                                
                                # Remove member form
                                if user_members:
                                    st.subheader("Remove Member")
                                    remove_member_email = st.selectbox(
                                        "Select Member to Remove",
                                        [member["user"]["email"] for member in user_members],
                                        key="remove_member_email"
                                    )
                                    leave_copy = st.checkbox("Leave a copy", value=False, key="leave_copy")
                                    
                                    if st.button("Remove Member"):
                                        if remove_member_email:
                                            try:
                                                result = sharing_manager.remove_folder_member(
                                                    selected_folder_data["shared_folder_id"],
                                                    remove_member_email,
                                                    leave_a_copy=leave_copy
                                                )
                                                st.success(f"Member '{remove_member_email}' removed successfully.")
                                                st.experimental_rerun()
                                            except Exception as e:
                                                st.error(f"Error removing member: {str(e)}")
                                
                                # Update member form
                                if user_members:
                                    st.subheader("Update Member Access")
                                    update_member_email = st.selectbox(
                                        "Select Member to Update",
                                        [member["user"]["email"] for member in user_members],
                                        key="update_member_email"
                                    )
                                    update_member_access = st.selectbox(
                                        "New Access Level",
                                        ["viewer", "editor", "owner"],
                                        key="update_member_access"
                                    )
                                    
                                    if st.button("Update Access"):
                                        if update_member_email:
                                            try:
                                                result = sharing_manager.update_folder_member(
                                                    selected_folder_data["shared_folder_id"],
                                                    update_member_email,
                                                    access_level=update_member_access
                                                )
                                                st.success(f"Member '{update_member_email}' access updated successfully.")
                                                st.experimental_rerun()
                                            except Exception as e:
                                                st.error(f"Error updating member access: {str(e)}")
                            else:
                                st.info("No members found for this folder.")
                                
                                # Add member form
                                st.subheader("Add Member")
                                new_member_email = st.text_input("Email", key="new_member_email")
                                new_member_access = st.selectbox(
                                    "Access Level",
                                    ["viewer", "editor", "owner"],
                                    key="new_member_access"
                                )
                                new_member_message = st.text_area("Custom Message (optional)", key="new_member_message")
                                
                                if st.button("Add Member"):
                                    if new_member_email:
                                        try:
                                            result = sharing_manager.add_folder_member(
                                                selected_folder_data["shared_folder_id"],
                                                new_member_email,
                                                access_level=new_member_access,
                                                custom_message=new_member_message if new_member_message else None
                                            )
                                            st.success(f"Member '{new_member_email}' added successfully.")
                                            st.experimental_rerun()
                                        except Exception as e:
                                            st.error(f"Error adding member: {str(e)}")
                                    else:
                                        st.warning("Please enter an email address.")
                        except Exception as e:
                            st.error(f"Error getting folder members: {str(e)}")
                        
                        # Action buttons
                        st.subheader("Actions")
                        col1, col2 = st.columns(2)
                        
                        # Unshare button with confirmation
                        unshare_confirmed = False
                        if col1.button("Unshare Folder"):
                            unshare_confirmed = True
                            
                        if unshare_confirmed:
                            st.warning(f"Are you sure you want to unshare the folder '{selected_folder_data['name']}'? This action cannot be undone.")
                            leave_copy = st.checkbox("Leave a copy", value=False, key="unshare_leave_copy")
                            col1, col2 = st.columns(2)
                            if col1.button("Yes, Unshare"):
                                try:
                                    result = sharing_manager.unshare_folder(
                                        selected_folder_data["shared_folder_id"],
                                        leave_a_copy=leave_copy
                                    )
                                    st.success(f"Folder '{selected_folder_data['name']}' unshared successfully.")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Error unsharing folder: {str(e)}")
                            if col2.button("Cancel"):
                                st.experimental_rerun()

                # Create new shared folder
                st.subheader("Create New Shared Folder")
                new_folder_path = st.text_input("Path", key="new_shared_folder_path")
                acl_policy = st.selectbox(
                    "ACL Update Policy",
                    ["owner", "editors"],
                    key="new_shared_folder_acl_policy"
                )
                force_async = st.checkbox("Force Async", value=False, key="new_shared_folder_force_async")
                
                if st.button("Create Shared Folder"):
                    if new_folder_path:
                        try:
                            result = sharing_manager.create_shared_folder(
                                new_folder_path,
                                acl_update_policy=acl_policy,
                                force_async=force_async
                            )
                            if "async_job_id" in result:
                                st.success(f"Shared folder creation started. Async job ID: {result['async_job_id']}")
                            else:
                                st.success(f"Shared folder '{result['name']}' created successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating shared folder: {str(e)}")
                    else:
                        st.warning("Please enter a path.")
            else:
                st.info("No shared folders found.")
                
                # Create new shared folder
                st.subheader("Create New Shared Folder")
                new_folder_path = st.text_input("Path", key="new_shared_folder_path")
                acl_policy = st.selectbox(
                    "ACL Update Policy",
                    ["owner", "editors"],
                    key="new_shared_folder_acl_policy"
                )
                force_async = st.checkbox("Force Async", value=False, key="new_shared_folder_force_async")
                
                if st.button("Create Shared Folder"):
                    if new_folder_path:
                        try:
                            result = sharing_manager.create_shared_folder(
                                new_folder_path,
                                acl_update_policy=acl_policy,
                                force_async=force_async
                            )
                            if "async_job_id" in result:
                                st.success(f"Shared folder creation started. Async job ID: {result['async_job_id']}")
                            else:
                                st.success(f"Shared folder '{result['name']}' created successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating shared folder: {str(e)}")
                    else:
                        st.warning("Please enter a path.")
        except Exception as e:
            st.error(f"Error listing shared folders: {str(e)}")


def render_dropbox_sharing_page():
    """Render the Dropbox sharing management page."""
    dropbox_sharing_page()


if __name__ == "__main__":
    render_dropbox_sharing_page()