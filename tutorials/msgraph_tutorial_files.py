"""
Microsoft Graph API Tutorial: File Exploration

This tutorial demonstrates how to use the Microsoft Graph API integration
with the Science Data Kit (SDK) to explore files in Microsoft 365.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
from collections import Counter
import io
import base64

from science_data_kit.core.db.msgraph_manager import MSGraphConnectionManager
from science_data_kit.core.db.msgraph_adapter import MSGraphAdapter
from science_data_kit.ui.components.msgraph_visualizations import render_document_collaboration_graph


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
        st.title("Microsoft Graph API: File Exploration")
        
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


def get_drive_items(connection_manager: MSGraphConnectionManager, folder_path: str = "/", top: int = 100) -> pd.DataFrame:
    """
    Get drive items (files and folders) from the specified folder.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        folder_path: Path to the folder to explore (default is root).
        top: Maximum number of items to retrieve.
        
    Returns:
        pd.DataFrame: DataFrame containing drive item information.
    """
    # Determine the API path based on the folder path
    if folder_path == "/" or folder_path == "":
        api_path = "/me/drive/root/children"
    else:
        # Handle both item ID and path formats
        if folder_path.startswith("/"):
            # Path format
            folder_path = folder_path.strip("/")
            api_path = f"/me/drive/root:/{folder_path}:/children"
        else:
            # Item ID format
            api_path = f"/me/drive/items/{folder_path}/children"
    
    # Get drive items
    drive_items = connection_manager.query_to_dataframe(api_path, {
        'select': 'id,name,size,createdDateTime,lastModifiedDateTime,file,folder,webUrl,createdBy,lastModifiedBy',
        'top': top
    })
    
    if st._is_running_with_streamlit:
        st.header("Drive Items")
        st.write(f"Found {len(drive_items)} items in folder '{folder_path if folder_path != '/' else 'root'}'")
        
        # Allow user to navigate to a different folder
        with st.expander("Navigate to a Different Folder"):
            new_folder_path = st.text_input("Folder Path", value=folder_path)
            
            if st.button("Navigate") and new_folder_path != folder_path:
                return get_drive_items(connection_manager, new_folder_path, top)
    else:
        print(f"Found {len(drive_items)} items in folder '{folder_path if folder_path != '/' else 'root'}'")
    
    return drive_items


def analyze_drive_items(drive_items: pd.DataFrame) -> None:
    """
    Analyze drive items (files and folders).
    
    Args:
        drive_items: DataFrame containing drive item information.
    """
    if drive_items.empty:
        if st._is_running_with_streamlit:
            st.warning("No drive items found")
        else:
            print("No drive items found")
        return
    
    # Separate files and folders
    files = drive_items[drive_items['file'].notna()]
    folders = drive_items[drive_items['folder'].notna()]
    
    if st._is_running_with_streamlit:
        st.header("Drive Items Analysis")
        
        # Display files and folders
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Files")
            st.write(f"Found {len(files)} files")
            
            if not files.empty:
                # Display file information
                file_info = files[['name', 'size', 'lastModifiedDateTime']].copy()
                
                # Convert size to human-readable format
                def format_size(size):
                    if pd.isna(size):
                        return "N/A"
                    
                    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                        if size < 1024.0:
                            return f"{size:.2f} {unit}"
                        size /= 1024.0
                    return f"{size:.2f} PB"
                
                file_info['size'] = file_info['size'].apply(format_size)
                
                # Convert datetime to string
                if 'lastModifiedDateTime' in file_info.columns:
                    if not pd.api.types.is_datetime64_any_dtype(file_info['lastModifiedDateTime']):
                        file_info['lastModifiedDateTime'] = pd.to_datetime(file_info['lastModifiedDateTime'])
                    file_info['lastModifiedDateTime'] = file_info['lastModifiedDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(file_info)
        
        with col2:
            st.subheader("Folders")
            st.write(f"Found {len(folders)} folders")
            
            if not folders.empty:
                # Display folder information
                folder_info = folders[['name', 'lastModifiedDateTime']].copy()
                
                # Convert datetime to string
                if 'lastModifiedDateTime' in folder_info.columns:
                    if not pd.api.types.is_datetime64_any_dtype(folder_info['lastModifiedDateTime']):
                        folder_info['lastModifiedDateTime'] = pd.to_datetime(folder_info['lastModifiedDateTime'])
                    folder_info['lastModifiedDateTime'] = folder_info['lastModifiedDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                st.dataframe(folder_info)
        
        # File type distribution
        if not files.empty:
            st.subheader("File Type Distribution")
            
            # Extract file extensions
            def get_extension(filename):
                if not isinstance(filename, str):
                    return "Unknown"
                
                parts = filename.split('.')
                if len(parts) > 1:
                    return parts[-1].lower()
                return "No Extension"
            
            files['extension'] = files['name'].apply(get_extension)
            
            # Count file types
            extension_counts = files['extension'].value_counts().reset_index()
            extension_counts.columns = ['Extension', 'Count']
            
            # Display as table
            st.dataframe(extension_counts)
            
            # Display as chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(extension_counts['Extension'], extension_counts['Count'])
            ax.set_xlabel('File Extension')
            ax.set_ylabel('Count')
            ax.set_title('File Type Distribution')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # File size distribution
            if 'size' in files.columns:
                st.subheader("File Size Distribution")
                
                # Create size categories
                def categorize_size(size):
                    if pd.isna(size):
                        return "Unknown"
                    
                    if size < 10 * 1024:  # < 10 KB
                        return "< 10 KB"
                    elif size < 100 * 1024:  # < 100 KB
                        return "10-100 KB"
                    elif size < 1024 * 1024:  # < 1 MB
                        return "100 KB - 1 MB"
                    elif size < 10 * 1024 * 1024:  # < 10 MB
                        return "1-10 MB"
                    elif size < 100 * 1024 * 1024:  # < 100 MB
                        return "10-100 MB"
                    else:  # >= 100 MB
                        return "> 100 MB"
                
                files['size_category'] = files['size'].apply(categorize_size)
                
                # Define the order of size categories
                size_order = ["< 10 KB", "10-100 KB", "100 KB - 1 MB", "1-10 MB", "10-100 MB", "> 100 MB", "Unknown"]
                
                # Count size categories
                size_counts = files['size_category'].value_counts().reindex(size_order).reset_index()
                size_counts.columns = ['Size Category', 'Count']
                
                # Remove categories with zero count
                size_counts = size_counts[size_counts['Count'] > 0]
                
                # Display as table
                st.dataframe(size_counts)
                
                # Display as chart
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(size_counts['Size Category'], size_counts['Count'])
                ax.set_xlabel('File Size')
                ax.set_ylabel('Count')
                ax.set_title('File Size Distribution')
                plt.tight_layout()
                
                st.pyplot(fig)
            
            # File creation/modification time distribution
            if 'createdDateTime' in files.columns or 'lastModifiedDateTime' in files.columns:
                st.subheader("File Timeline")
                
                # Convert datetime columns
                for col in ['createdDateTime', 'lastModifiedDateTime']:
                    if col in files.columns:
                        if not pd.api.types.is_datetime64_any_dtype(files[col]):
                            files[col] = pd.to_datetime(files[col])
                
                # Group by month
                if 'createdDateTime' in files.columns:
                    files['creation_month'] = files['createdDateTime'].dt.to_period('M')
                    creation_counts = files['creation_month'].value_counts().sort_index().reset_index()
                    creation_counts.columns = ['Month', 'Count']
                    creation_counts['Month'] = creation_counts['Month'].astype(str)
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(creation_counts['Month'], creation_counts['Count'], marker='o', label='Created')
                    ax.set_xlabel('Month')
                    ax.set_ylabel('Number of Files')
                    ax.set_title('File Creation Timeline')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                
                if 'lastModifiedDateTime' in files.columns:
                    files['modified_month'] = files['lastModifiedDateTime'].dt.to_period('M')
                    modified_counts = files['modified_month'].value_counts().sort_index().reset_index()
                    modified_counts.columns = ['Month', 'Count']
                    modified_counts['Month'] = modified_counts['Month'].astype(str)
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(modified_counts['Month'], modified_counts['Count'], marker='o', color='orange', label='Modified')
                    ax.set_xlabel('Month')
                    ax.set_ylabel('Number of Files')
                    ax.set_title('File Modification Timeline')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    
                    st.pyplot(fig)
    else:
        print("\nDrive Items Analysis:")
        print(f"Found {len(files)} files and {len(folders)} folders")
        
        # File type distribution
        if not files.empty:
            # Extract file extensions
            def get_extension(filename):
                if not isinstance(filename, str):
                    return "Unknown"
                
                parts = filename.split('.')
                if len(parts) > 1:
                    return parts[-1].lower()
                return "No Extension"
            
            files['extension'] = files['name'].apply(get_extension)
            
            # Count file types
            extension_counts = files['extension'].value_counts()
            
            print("\nFile Type Distribution:")
            print(extension_counts)
            
            # File size distribution
            if 'size' in files.columns:
                # Create size categories
                def categorize_size(size):
                    if pd.isna(size):
                        return "Unknown"
                    
                    if size < 10 * 1024:  # < 10 KB
                        return "< 10 KB"
                    elif size < 100 * 1024:  # < 100 KB
                        return "10-100 KB"
                    elif size < 1024 * 1024:  # < 1 MB
                        return "100 KB - 1 MB"
                    elif size < 10 * 1024 * 1024:  # < 10 MB
                        return "1-10 MB"
                    elif size < 100 * 1024 * 1024:  # < 100 MB
                        return "10-100 MB"
                    else:  # >= 100 MB
                        return "> 100 MB"
                
                files['size_category'] = files['size'].apply(categorize_size)
                
                # Define the order of size categories
                size_order = ["< 10 KB", "10-100 KB", "100 KB - 1 MB", "1-10 MB", "10-100 MB", "> 100 MB", "Unknown"]
                
                # Count size categories
                size_counts = files['size_category'].value_counts().reindex(size_order)
                
                print("\nFile Size Distribution:")
                print(size_counts)


def analyze_file_collaborators(connection_manager: MSGraphConnectionManager, drive_items: pd.DataFrame) -> None:
    """
    Analyze file collaborators.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        drive_items: DataFrame containing drive item information.
    """
    if drive_items.empty:
        if st._is_running_with_streamlit:
            st.warning("No drive items found")
        else:
            print("No drive items found")
        return
    
    # Get users for collaboration graph
    users = connection_manager.get_users()
    
    if st._is_running_with_streamlit:
        st.header("File Collaboration Analysis")
        
        # Extract creator and modifier information
        creators = []
        modifiers = []
        
        for _, item in drive_items.iterrows():
            if isinstance(item.get('createdBy'), dict) and 'user' in item['createdBy']:
                creator = item['createdBy']['user'].get('displayName', '')
                if creator:
                    creators.append(creator)
            
            if isinstance(item.get('lastModifiedBy'), dict) and 'user' in item['lastModifiedBy']:
                modifier = item['lastModifiedBy']['user'].get('displayName', '')
                if modifier:
                    modifiers.append(modifier)
        
        # Count creators and modifiers
        creator_counts = Counter(creators)
        modifier_counts = Counter(modifiers)
        
        # Display top creators
        if creators:
            st.subheader("Top File Creators")
            top_creators = pd.DataFrame(creator_counts.most_common(10), columns=['Creator', 'Count'])
            st.dataframe(top_creators)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_creators['Creator'], top_creators['Count'])
            ax.set_xlabel('Creator')
            ax.set_ylabel('Number of Files')
            ax.set_title('Top File Creators')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
        
        # Display top modifiers
        if modifiers:
            st.subheader("Top File Modifiers")
            top_modifiers = pd.DataFrame(modifier_counts.most_common(10), columns=['Modifier', 'Count'])
            st.dataframe(top_modifiers)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top_modifiers['Modifier'], top_modifiers['Count'])
            ax.set_xlabel('Modifier')
            ax.set_ylabel('Number of Files')
            ax.set_title('Top File Modifiers')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
        
        # Create document collaboration graph
        st.subheader("Document Collaboration Graph")
        
        try:
            # Use the visualization component from the SDK
            render_document_collaboration_graph(drive_items, users)
        except Exception as e:
            st.error(f"Error creating document collaboration graph: {str(e)}")
            
            # Fallback to manual graph creation
            st.info("Creating a simplified document collaboration graph...")
            
            # Create a graph
            G = nx.Graph()
            
            # Add file nodes
            for _, item in drive_items.iterrows():
                file_id = item.get('id', '')
                file_name = item.get('name', '')
                
                if file_id and file_name:
                    G.add_node(file_id, name=file_name, type='file')
                    
                    # Add creator edge
                    if isinstance(item.get('createdBy'), dict) and 'user' in item['createdBy']:
                        creator_id = item['createdBy']['user'].get('id', '')
                        creator_name = item['createdBy']['user'].get('displayName', '')
                        
                        if creator_id and creator_name:
                            if creator_id not in G:
                                G.add_node(creator_id, name=creator_name, type='user')
                            
                            G.add_edge(creator_id, file_id, relationship='created')
                    
                    # Add modifier edge
                    if isinstance(item.get('lastModifiedBy'), dict) and 'user' in item['lastModifiedBy']:
                        modifier_id = item['lastModifiedBy']['user'].get('id', '')
                        modifier_name = item['lastModifiedBy']['user'].get('displayName', '')
                        
                        if modifier_id and modifier_name:
                            if modifier_id not in G:
                                G.add_node(modifier_id, name=modifier_name, type='user')
                            
                            G.add_edge(modifier_id, file_id, relationship='modified')
            
            # Check if graph has nodes
            if not G.nodes():
                st.warning("No valid collaboration data found for graph visualization.")
                return
            
            # Create a spring layout
            pos = nx.spring_layout(G, k=0.3, iterations=50)
            
            # Create the figure
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Draw nodes with different colors for users and files
            user_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'user']
            file_nodes = [node for node, attr in G.nodes(data=True) if attr.get('type') == 'file']
            
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=user_nodes,
                node_color='green',
                node_size=300,
                alpha=0.8,
                label='Users'
            )
            
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=file_nodes,
                node_color='orange',
                node_size=200,
                alpha=0.8,
                label='Files'
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
            plt.title('Document Collaboration Graph')
            plt.legend()
            
            st.pyplot(fig)
    else:
        print("\nFile Collaboration Analysis:")
        
        # Extract creator and modifier information
        creators = []
        modifiers = []
        
        for _, item in drive_items.iterrows():
            if isinstance(item.get('createdBy'), dict) and 'user' in item['createdBy']:
                creator = item['createdBy']['user'].get('displayName', '')
                if creator:
                    creators.append(creator)
            
            if isinstance(item.get('lastModifiedBy'), dict) and 'user' in item['lastModifiedBy']:
                modifier = item['lastModifiedBy']['user'].get('displayName', '')
                if modifier:
                    modifiers.append(modifier)
        
        # Count creators and modifiers
        creator_counts = Counter(creators)
        modifier_counts = Counter(modifiers)
        
        # Display top creators
        if creators:
            print("\nTop File Creators:")
            for creator, count in creator_counts.most_common(10):
                print(f"{creator}: {count}")
        
        # Display top modifiers
        if modifiers:
            print("\nTop File Modifiers:")
            for modifier, count in modifier_counts.most_common(10):
                print(f"{modifier}: {count}")
        
        print("\nDocument Collaboration Graph:")
        print("This feature requires a graphical environment.")


def search_files(connection_manager: MSGraphConnectionManager, query: str) -> pd.DataFrame:
    """
    Search for files using the specified query.
    
    Args:
        connection_manager: The Microsoft Graph API connection manager.
        query: Search query.
        
    Returns:
        pd.DataFrame: DataFrame containing search results.
    """
    if not query:
        return pd.DataFrame()
    
    # Execute search query
    search_results = connection_manager.query_to_dataframe(f"/me/drive/root/search(q='{query}')")
    
    if st._is_running_with_streamlit:
        st.header("Search Results")
        st.write(f"Found {len(search_results)} items matching '{query}'")
        
        if not search_results.empty:
            # Display search results
            result_info = search_results[['name', 'size', 'lastModifiedDateTime']].copy()
            
            # Convert size to human-readable format
            def format_size(size):
                if pd.isna(size):
                    return "N/A"
                
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size < 1024.0:
                        return f"{size:.2f} {unit}"
                    size /= 1024.0
                return f"{size:.2f} PB"
            
            if 'size' in result_info.columns:
                result_info['size'] = result_info['size'].apply(format_size)
            
            # Convert datetime to string
            if 'lastModifiedDateTime' in result_info.columns:
                if not pd.api.types.is_datetime64_any_dtype(result_info['lastModifiedDateTime']):
                    result_info['lastModifiedDateTime'] = pd.to_datetime(result_info['lastModifiedDateTime'])
                result_info['lastModifiedDateTime'] = result_info['lastModifiedDateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(result_info)
    else:
        print(f"\nSearch Results for '{query}':")
        print(f"Found {len(search_results)} items")
        
        if not search_results.empty:
            print(search_results[['name', 'size', 'lastModifiedDateTime']].head())
    
    return search_results


def main():
    """Main function to run the tutorial."""
    # Connect to Microsoft Graph API
    connection_manager = connect_to_msgraph()
    
    if connection_manager:
        # Get drive items
        drive_items = get_drive_items(connection_manager)
        
        # Analyze drive items
        analyze_drive_items(drive_items)
        
        # Analyze file collaborators
        analyze_file_collaborators(connection_manager, drive_items)
        
        # Search for files
        if st._is_running_with_streamlit:
            st.header("Search Files")
            query = st.text_input("Search Query")
            
            if st.button("Search") and query:
                search_results = search_files(connection_manager, query)
        else:
            print("\nFile Search:")
            query = input("Enter search query (or press Enter to skip): ")
            
            if query:
                search_results = search_files(connection_manager, query)
        
        if not st._is_running_with_streamlit:
            print("\nTutorial completed successfully!")


if __name__ == "__main__":
    # Check if running with Streamlit
    if not hasattr(st, "_is_running_with_streamlit"):
        st._is_running_with_streamlit = False
    
    main()