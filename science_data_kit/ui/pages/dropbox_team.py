"""
Dropbox Team Management Page for Science Data Kit

This module provides a Streamlit page for managing Dropbox team folders and team members.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime

from science_data_kit_extensions.dropbox.connector import DropboxConnector
from science_data_kit_extensions.dropbox.teams import DropboxTeamManager


def dropbox_team_page():
    """
    Render the Dropbox team management page.
    """
    st.title("Dropbox Team Management")

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

    # Initialize team manager
    try:
        team_manager = DropboxTeamManager(connector)
    except Exception as e:
        if "not a Dropbox Business/Team account" in str(e):
            st.error("Team management features require a Dropbox Business/Team account.")
            st.info("Please connect with a Dropbox Business/Team account to use these features.")
            return
        else:
            st.error(f"Error initializing team manager: {str(e)}")
            return

    # Create tabs for different team management features
    tab1, tab2, tab3, tab4 = st.tabs(["Team Folders", "Team Members", "Groups", "Permissions"])

    with tab1:
        st.header("Team Folders")

        # Refresh button for team folders
        if st.button("Refresh Team Folders"):
            st.experimental_rerun()

        try:
            # List team folders
            team_folders = team_manager.list_team_folders()

            if team_folders:
                # Convert to DataFrame for display
                folders_data = []
                for folder in team_folders:
                    folders_data.append({
                        "ID": folder["id"],
                        "Name": folder["name"],
                        "Status": folder["status"],
                        "Sync Setting": folder["sync_setting"] if folder["sync_setting"] else "Default",
                        "Team Shared Dropbox": "Yes" if folder["is_team_shared_dropbox"] else "No"
                    })

                folders_df = pd.DataFrame(folders_data)
                st.dataframe(folders_df, use_container_width=True)

                # Team folder actions
                st.subheader("Team Folder Actions")

                # Select a team folder
                selected_folder = st.selectbox(
                    "Select a team folder",
                    [folder["name"] for folder in team_folders],
                    key="selected_team_folder"
                )

                if selected_folder:
                    selected_folder_data = next((f for f in team_folders if f["name"] == selected_folder), None)

                    if selected_folder_data:
                        # Display folder details
                        st.subheader("Folder Details")
                        col1, col2 = st.columns(2)
                        col1.write(f"**ID:** {selected_folder_data['id']}")
                        col1.write(f"**Name:** {selected_folder_data['name']}")
                        col2.write(f"**Status:** {selected_folder_data['status']}")
                        col2.write(f"**Sync Setting:** {selected_folder_data['sync_setting'] if selected_folder_data['sync_setting'] else 'Default'}")

                        # Action buttons
                        st.subheader("Actions")
                        col1, col2 = st.columns(2)

                        # Archive button
                        if col1.button("Archive Folder"):
                            try:
                                result = team_manager.archive_team_folder(selected_folder_data["id"])
                                st.success(f"Team folder '{selected_folder_data['name']}' archived successfully.")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Error archiving team folder: {str(e)}")

                        # Delete button with confirmation
                        delete_confirmed = False
                        if col2.button("Delete Folder"):
                            delete_confirmed = True

                        if delete_confirmed:
                            st.warning(f"Are you sure you want to permanently delete the team folder '{selected_folder_data['name']}'? This action cannot be undone.")
                            col1, col2 = st.columns(2)
                            if col1.button("Yes, Delete"):
                                try:
                                    result = team_manager.permanently_delete_team_folder(selected_folder_data["id"])
                                    st.success(f"Team folder '{selected_folder_data['name']}' deleted successfully.")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Error deleting team folder: {str(e)}")
                            if col2.button("Cancel"):
                                st.experimental_rerun()

                # Create new team folder
                st.subheader("Create New Team Folder")
                new_folder_name = st.text_input("Folder Name", key="new_team_folder_name")
                if st.button("Create Folder"):
                    if new_folder_name:
                        try:
                            result = team_manager.create_team_folder(new_folder_name)
                            st.success(f"Team folder '{new_folder_name}' created successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating team folder: {str(e)}")
                    else:
                        st.warning("Please enter a folder name.")
            else:
                st.info("No team folders found.")
                
                # Create new team folder
                st.subheader("Create New Team Folder")
                new_folder_name = st.text_input("Folder Name", key="new_team_folder_name")
                if st.button("Create Folder"):
                    if new_folder_name:
                        try:
                            result = team_manager.create_team_folder(new_folder_name)
                            st.success(f"Team folder '{new_folder_name}' created successfully.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating team folder: {str(e)}")
                    else:
                        st.warning("Please enter a folder name.")
        except Exception as e:
            st.error(f"Error listing team folders: {str(e)}")

    with tab2:
        st.header("Team Members")

        # Refresh button for team members
        if st.button("Refresh Team Members"):
            st.experimental_rerun()

        try:
            # List team members
            team_members = team_manager.list_team_members()

            if team_members:
                # Convert to DataFrame for display
                members_data = []
                for member in team_members:
                    members_data.append({
                        "ID": member["team_member_id"],
                        "Email": member["email"],
                        "Name": member["name"]["display_name"],
                        "Role": member["role"],
                        "Status": member["status"]
                    })

                members_df = pd.DataFrame(members_data)
                st.dataframe(members_df, use_container_width=True)

                # Select a team member for details
                selected_member = st.selectbox(
                    "Select a team member for details",
                    [member["email"] for member in team_members],
                    key="selected_team_member"
                )

                if selected_member:
                    selected_member_data = next((m for m in team_members if m["email"] == selected_member), None)

                    if selected_member_data:
                        # Display member details
                        st.subheader("Member Details")
                        col1, col2 = st.columns(2)
                        col1.write(f"**ID:** {selected_member_data['team_member_id']}")
                        col1.write(f"**Email:** {selected_member_data['email']}")
                        col2.write(f"**Name:** {selected_member_data['name']['display_name']}")
                        col2.write(f"**Role:** {selected_member_data['role']}")
                        col2.write(f"**Status:** {selected_member_data['status']}")
            else:
                st.info("No team members found.")
        except Exception as e:
            st.error(f"Error listing team members: {str(e)}")

    with tab3:
        st.header("Groups")

        # Refresh button for groups
        if st.button("Refresh Groups"):
            st.experimental_rerun()

        try:
            # List groups
            groups = team_manager.list_groups()

            if groups:
                # Convert to DataFrame for display
                groups_data = []
                for group in groups:
                    groups_data.append({
                        "ID": group["group_id"],
                        "Name": group["name"],
                        "Member Count": group["member_count"],
                        "Type": group["group_type"] if group["group_type"] else "Standard",
                        "External ID": group["group_external_id"] if "group_external_id" in group and group["group_external_id"] else "N/A"
                    })

                groups_df = pd.DataFrame(groups_data)
                st.dataframe(groups_df, use_container_width=True)

                # Select a group for details
                selected_group = st.selectbox(
                    "Select a group to view members",
                    [group["name"] for group in groups],
                    key="selected_group"
                )

                if selected_group:
                    selected_group_data = next((g for g in groups if g["name"] == selected_group), None)

                    if selected_group_data:
                        st.subheader(f"Members of {selected_group}")
                        
                        try:
                            # List group members
                            group_members = team_manager.list_group_members(selected_group_data["group_id"])

                            if group_members:
                                # Convert to DataFrame for display
                                group_members_data = []
                                for member in group_members:
                                    group_members_data.append({
                                        "ID": member["team_member_id"],
                                        "Email": member["email"],
                                        "Name": member["name"]["display_name"],
                                        "Access Type": member["access_type"]
                                    })

                                group_members_df = pd.DataFrame(group_members_data)
                                st.dataframe(group_members_df, use_container_width=True)
                            else:
                                st.info(f"No members found in group '{selected_group}'.")
                        except Exception as e:
                            st.error(f"Error listing group members: {str(e)}")
            else:
                st.info("No groups found.")
        except Exception as e:
            st.error(f"Error listing groups: {str(e)}")

    with tab4:
        st.header("Folder Permissions")

        # Select a team folder for permissions
        try:
            team_folders = team_manager.list_team_folders()
            
            if team_folders:
                selected_folder_for_permissions = st.selectbox(
                    "Select a team folder to view permissions",
                    [folder["name"] for folder in team_folders],
                    key="selected_folder_for_permissions"
                )

                if selected_folder_for_permissions:
                    selected_folder_data = next((f for f in team_folders if f["name"] == selected_folder_for_permissions), None)

                    if selected_folder_data:
                        st.subheader(f"Permissions for {selected_folder_for_permissions}")
                        
                        try:
                            # Get folder permissions
                            permissions = team_manager.get_team_folder_permissions(selected_folder_data["id"])

                            if permissions:
                                # Separate by type
                                user_permissions = [p for p in permissions if p["type"] == "user"]
                                group_permissions = [p for p in permissions if p["type"] == "group"]
                                invitee_permissions = [p for p in permissions if p["type"] == "invitee"]

                                # Display user permissions
                                if user_permissions:
                                    st.subheader("User Permissions")
                                    user_permissions_data = []
                                    for perm in user_permissions:
                                        user_permissions_data.append({
                                            "Email": perm["email"],
                                            "Display Name": perm["display_name"],
                                            "Access Type": perm["access_type"],
                                            "Inherited": "Yes" if perm["is_inherited"] else "No"
                                        })

                                    user_permissions_df = pd.DataFrame(user_permissions_data)
                                    st.dataframe(user_permissions_df, use_container_width=True)

                                # Display group permissions
                                if group_permissions:
                                    st.subheader("Group Permissions")
                                    group_permissions_data = []
                                    for perm in group_permissions:
                                        group_permissions_data.append({
                                            "Group Name": perm["group_name"],
                                            "Access Type": perm["access_type"],
                                            "Inherited": "Yes" if perm["is_inherited"] else "No"
                                        })

                                    group_permissions_df = pd.DataFrame(group_permissions_data)
                                    st.dataframe(group_permissions_df, use_container_width=True)

                                # Display invitee permissions
                                if invitee_permissions:
                                    st.subheader("Invitee Permissions")
                                    invitee_permissions_data = []
                                    for perm in invitee_permissions:
                                        invitee_permissions_data.append({
                                            "Email": perm["email"],
                                            "Access Type": perm["access_type"],
                                            "Inherited": "Yes" if perm["is_inherited"] else "No"
                                        })

                                    invitee_permissions_df = pd.DataFrame(invitee_permissions_data)
                                    st.dataframe(invitee_permissions_df, use_container_width=True)

                                if not user_permissions and not group_permissions and not invitee_permissions:
                                    st.info("No permissions found for this folder.")
                            else:
                                st.info("No permissions found for this folder.")
                        except Exception as e:
                            st.error(f"Error getting folder permissions: {str(e)}")
            else:
                st.info("No team folders found.")
        except Exception as e:
            st.error(f"Error listing team folders: {str(e)}")


def render_dropbox_team_page():
    """Render the Dropbox team management page."""
    dropbox_team_page()


if __name__ == "__main__":
    render_dropbox_team_page()