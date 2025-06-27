"""
Microsoft Graph API Tutorial: User and Group Exploration

This tutorial demonstrates how to use the Microsoft Graph API integration
with the Science Data Kit (SDK) to explore users and groups in Microsoft 365.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from typing import Dict, Any, Optional, List

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.ui.components.msgraph_visualizations import render_organizational_chart


def connect_to_msgraph() -> Optional[MSGraphConnectionManager]:
    """
    Connect to Microsoft Graph API using configuration from environment variables or user input.
    
    Returns:
        MSGraphConnectionManager: The connection manager if connection is successful, None otherwise.
    """
    # Try to get configuration from environment variables
    tenant_id = os.environ.get("MSGRAPH_TENANT_ID")
    client_id = os.environ.get("MSGRAPH_CLIENT_ID")
    client_secret = os.environ.get("MSGRAPH_CLIENT_SECRET")
    auth_method = os.environ.get("MSGRAPH_AUTH_METHOD", "device_code")
    
    # If running in Streamlit, allow user input
    if st._is_running_with_streamlit:
        st.title("Microsoft Graph API: User and Group Exploration")
        
        st.header("Connect to Microsoft Graph API")
        
        # Authentication method selection
        auth_method = st.selectbox(
            "Authentication Method",
            ["device_code", "client_credentials", "interactive"],
            index=0 if auth_method not in ["client_credentials", "interactive"] else 
                  (1 if auth_method == "client_credentials" else 2)
        )
        
        # Tenant ID and Client ID
        tenant_id = st.text_input("Tenant ID", value=tenant_id or "")
        client_id = st.text_input("Client ID", value=client_id or "")
        
        # Client Secret (only for client_credentials)
        if auth_method == "client_credentials":
            client_secret = st.text_input("Client Secret", value=client_secret or "", type="password")
        
        # Connect button
        if not st.button("Connect to Microsoft Graph API"):
            st.info("Please enter your credentials and click 'Connect to Microsoft Graph API'")
            return None
    
    # Create connection manager
    connection_manager = MSGraphConnectionManager(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret if auth_method == "client_credentials" else None,
        auth_method=auth_method
    )
    
    # Connect to Microsoft Graph API
    if connection_manager.connect():
        if st._is_running_with_streamlit:
            st.success("Connected to Microsoft Graph API")
        else:
            print("Connected to Microsoft Graph API")
        return connection_manager
    else:
        if st._is_running_with_streamlit:
            st.error("Failed to connect to Microsoft Graph API")
        else:
            print("Failed to connect to Microsoft Graph API")
        return None


def explore_users(connection_manager: MSGraphConnectionManager) -> pd.DataFrame:
    """
    Explore users in Microsoft 365.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        
    Returns:
        pd.DataFrame: DataFrame containing user information.
    """
    # Get users
    users = connection_manager.query_to_dataframe('/users', {
        'select': 'id,displayName,mail,userPrincipalName,jobTitle,department,officeLocation',
        'top': 50  # Limit to 50 users for this tutorial
    })
    
    if st._is_running_with_streamlit:
        st.header("Users")
        st.write(f"Found {len(users)} users")
        st.dataframe(users)
        
        # User statistics
        st.subheader("User Statistics")
        
        # Department distribution
        if 'department' in users.columns and not users['department'].isna().all():
            dept_counts = users['department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(dept_counts['Department'], dept_counts['Count'])
            ax.set_xlabel('Department')
            ax.set_ylabel('Count')
            ax.set_title('User Distribution by Department')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
    else:
        print(f"Found {len(users)} users")
        print(users.head())
        
        # Department distribution
        if 'department' in users.columns and not users['department'].isna().all():
            dept_counts = users['department'].value_counts()
            print("\nUser Distribution by Department:")
            print(dept_counts)
    
    return users


def explore_groups(connection_manager: MSGraphConnectionManager) -> pd.DataFrame:
    """
    Explore groups in Microsoft 365.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        
    Returns:
        pd.DataFrame: DataFrame containing group information.
    """
    # Get groups
    groups = connection_manager.query_to_dataframe('/groups', {
        'select': 'id,displayName,description,mail,groupTypes,securityEnabled,mailEnabled',
        'top': 50  # Limit to 50 groups for this tutorial
    })
    
    if st._is_running_with_streamlit:
        st.header("Groups")
        st.write(f"Found {len(groups)} groups")
        st.dataframe(groups)
        
        # Group statistics
        st.subheader("Group Statistics")
        
        # Group types distribution
        if 'groupTypes' in groups.columns:
            # Extract group types (may be a list in each cell)
            group_types = []
            for types in groups['groupTypes']:
                if isinstance(types, list):
                    group_types.extend(types)
                elif isinstance(types, str):
                    group_types.append(types)
            
            if group_types:
                type_counts = pd.Series(group_types).value_counts().reset_index()
                type_counts.columns = ['Group Type', 'Count']
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(type_counts['Group Type'], type_counts['Count'])
                ax.set_xlabel('Group Type')
                ax.set_ylabel('Count')
                ax.set_title('Group Distribution by Type')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                st.pyplot(fig)
    else:
        print(f"\nFound {len(groups)} groups")
        print(groups.head())
        
        # Group types distribution
        if 'groupTypes' in groups.columns:
            # Extract group types (may be a list in each cell)
            group_types = []
            for types in groups['groupTypes']:
                if isinstance(types, list):
                    group_types.extend(types)
                elif isinstance(types, str):
                    group_types.append(types)
            
            if group_types:
                type_counts = pd.Series(group_types).value_counts()
                print("\nGroup Distribution by Type:")
                print(type_counts)
    
    return groups


def explore_group_members(connection_manager: MSGraphConnectionManager, groups: pd.DataFrame) -> None:
    """
    Explore members of groups in Microsoft 365.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        groups: DataFrame containing group information.
    """
    if groups.empty:
        if st._is_running_with_streamlit:
            st.warning("No groups found")
        else:
            print("No groups found")
        return
    
    # Select a group to explore
    if st._is_running_with_streamlit:
        st.header("Group Members")
        
        selected_group = st.selectbox(
            "Select a group to explore",
            groups['displayName'].tolist(),
            key="group_selector"
        )
        
        # Get the group ID
        group_id = groups.loc[groups['displayName'] == selected_group, 'id'].iloc[0]
    else:
        # For non-Streamlit usage, just use the first group
        group_id = groups['id'].iloc[0]
        selected_group = groups['displayName'].iloc[0]
        print(f"\nExploring members of group: {selected_group}")
    
    # Get group members
    try:
        members = connection_manager.query_to_dataframe(f'/groups/{group_id}/members')
        
        if st._is_running_with_streamlit:
            st.write(f"Found {len(members)} members in group '{selected_group}'")
            st.dataframe(members)
            
            # Create a network visualization of the group
            if not members.empty:
                st.subheader("Group Network Visualization")
                
                # Create a graph
                G = nx.Graph()
                
                # Add the group node
                G.add_node(group_id, name=selected_group, type='group')
                
                # Add member nodes and edges
                for _, member in members.iterrows():
                    member_id = member.get('id', '')
                    member_name = member.get('displayName', '')
                    
                    if member_id:
                        G.add_node(member_id, name=member_name, type='user')
                        G.add_edge(group_id, member_id)
                
                # Create a spring layout
                pos = nx.spring_layout(G, k=0.3, iterations=50)
                
                # Create the figure
                fig, ax = plt.subplots(figsize=(10, 8))
                
                # Draw nodes with different colors for group and users
                group_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'group']
                user_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'user']
                
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=group_nodes,
                    node_color='red',
                    node_size=500,
                    alpha=0.8,
                    label='Group'
                )
                
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=user_nodes,
                    node_color='blue',
                    node_size=300,
                    alpha=0.8,
                    label='Users'
                )
                
                # Draw edges
                nx.draw_networkx_edges(
                    G, pos,
                    width=1.5,
                    alpha=0.5
                )
                
                # Draw labels
                node_labels = {node: G.nodes[node]['name'] for node in G.nodes()}
                nx.draw_networkx_labels(
                    G, pos,
                    labels=node_labels,
                    font_size=8
                )
                
                plt.axis('off')
                plt.title(f"Members of Group: {selected_group}")
                plt.legend()
                
                st.pyplot(fig)
        else:
            print(f"Found {len(members)} members in group '{selected_group}'")
            print(members.head())
    
    except Exception as e:
        if st._is_running_with_streamlit:
            st.error(f"Error retrieving group members: {str(e)}")
        else:
            print(f"Error retrieving group members: {str(e)}")


def create_organizational_chart(connection_manager: MSGraphConnectionManager, users: pd.DataFrame) -> None:
    """
    Create an organizational chart based on user data.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        users: DataFrame containing user information.
    """
    if users.empty:
        if st._is_running_with_streamlit:
            st.warning("No users found")
        else:
            print("No users found")
        return
    
    if st._is_running_with_streamlit:
        st.header("Organizational Chart")
        
        # Get users with manager information
        try:
            # This requires additional permissions and may not work in all environments
            users_with_managers = connection_manager.query_to_dataframe('/users', {
                'select': 'id,displayName,jobTitle,department,manager',
                'expand': 'manager',
                'top': 50
            })
            
            if 'manager' in users_with_managers.columns and not users_with_managers['manager'].isna().all():
                # Render organizational chart
                render_organizational_chart(users_with_managers, manager_column='manager')
            else:
                st.warning("Manager information not available. This may require additional permissions.")
        except Exception as e:
            st.error(f"Error creating organizational chart: {str(e)}")
            st.info("This feature requires additional permissions and may not work in all environments.")
    else:
        print("\nOrganizational Chart:")
        print("This feature requires a graphical environment and additional permissions.")


def main():
    """Main function to run the tutorial."""
    # Connect to Microsoft Graph API
    connection_manager = connect_to_msgraph()
    
    if connection_manager:
        # Explore users
        users = explore_users(connection_manager)
        
        # Explore groups
        groups = explore_groups(connection_manager)
        
        # Explore group members
        explore_group_members(connection_manager, groups)
        
        # Create organizational chart
        create_organizational_chart(connection_manager, users)
        
        if not st._is_running_with_streamlit:
            print("\nTutorial completed successfully!")


if __name__ == "__main__":
    # Check if running with Streamlit
    if not hasattr(st, "_is_running_with_streamlit"):
        st._is_running_with_streamlit = False
    
    main()