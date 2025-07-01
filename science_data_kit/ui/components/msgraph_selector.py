"""
Microsoft Graph Selector Component for Science Data Kit

This module provides a Streamlit component for selecting and previewing
data from Microsoft Graph API.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple

from ...core.providers.registry import ProviderType
from ...core.providers.api.msgraph_provider import MSGraphProvider
from ...core.config.providers import load_provider_config


def render_msgraph_selector() -> Optional[Dict[str, Any]]:
    """
    Render a Microsoft Graph selection UI component.
    
    Returns:
        Dictionary containing selected data and metadata, or None if no data is selected
    """
    st.subheader("Microsoft Graph Data Import")
    
    # Check if provider is configured
    config = load_provider_config()
    msgraph_config = config.get("api", {}).get("msgraph", {})
    
    if not msgraph_config or "tenant_id" not in msgraph_config or "client_id" not in msgraph_config:
        return _render_setup_instructions()
    
    # Initialize provider if not already in session state
    if "msgraph_provider" not in st.session_state:
        _initialize_provider(msgraph_config)
    
    # If provider failed to initialize, show setup instructions
    if not st.session_state.get("msgraph_provider_initialized", False):
        return _render_setup_instructions()
    
    # Get provider from session state
    provider = st.session_state["msgraph_provider"]
    
    # Create UI for data type selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("Data Types:")
        
        # Data type selection
        data_types = [
            ("Files", "files"),
            ("Spreadsheets", "spreadsheets"),
            ("Users", "users"),
            ("Groups", "groups"),
            ("Messages", "messages"),
            ("Events", "events")
        ]
        
        selected_type = st.radio("Select Data Type", [dt[0] for dt in data_types])
        selected_type_key = next(dt[1] for dt in data_types if dt[0] == selected_type)
        
        # Store the selected type in session state
        if "msgraph_selected_type" not in st.session_state or st.session_state["msgraph_selected_type"] != selected_type_key:
            st.session_state["msgraph_selected_type"] = selected_type_key
            st.session_state["msgraph_selected_item"] = None
            st.session_state["msgraph_preview_data"] = None
    
    # Handle different data types
    if selected_type_key == "files":
        return _render_files_selector(provider, col1, col2)
    elif selected_type_key == "spreadsheets":
        return _render_spreadsheets_selector(provider, col1, col2)
    elif selected_type_key in ["users", "groups", "messages", "events"]:
        return _render_entity_selector(provider, selected_type_key, col1, col2)
    
    return None


def _render_files_selector(provider: MSGraphProvider, col1, col2) -> Optional[Dict[str, Any]]:
    """
    Render the files selector UI.
    
    Args:
        provider: Microsoft Graph provider
        col1: First column for UI elements
        col2: Second column for UI elements
        
    Returns:
        Dictionary containing selected file data and metadata, or None if no file is selected
    """
    with col1:
        # Refresh button
        if st.button("Refresh Files"):
            st.session_state["msgraph_files"] = _list_files(provider)
            st.session_state["msgraph_selected_item"] = None
            st.session_state["msgraph_preview_data"] = None
    
    # Display files and handle selection
    files = st.session_state.get("msgraph_files", [])
    
    if not files:
        st.session_state["msgraph_files"] = _list_files(provider)
        files = st.session_state.get("msgraph_files", [])
    
    with col1:
        # Group files by type
        folders = [f for f in files if f.get("type") == "folder"]
        csv_files = [f for f in files if f.get("type") == "csv"]
        excel_files = [f for f in files if f.get("type") in ["xlsx", "xls"]]
        text_files = [f for f in files if f.get("type") == "txt"]
        
        # Display folders first
        for folder in folders:
            if st.button(f"📁 {folder['name']}", key=f"folder_{folder['id']}"):
                # In a real implementation, you would navigate to the folder
                pass
        
        # Display CSV files
        for file in csv_files:
            if st.button(f"📄 {file['name']}", key=f"file_{file['id']}"):
                st.session_state["msgraph_selected_item"] = file
                st.session_state["msgraph_preview_data"] = _get_file_preview_data(provider, file["id"])
        
        # Display Excel files
        for file in excel_files:
            if st.button(f"📊 {file['name']}", key=f"file_{file['id']}"):
                st.session_state["msgraph_selected_item"] = file
                st.session_state["msgraph_preview_data"] = _get_file_preview_data(provider, file["id"])
        
        # Display text files
        for file in text_files:
            if st.button(f"📝 {file['name']}", key=f"file_{file['id']}"):
                st.session_state["msgraph_selected_item"] = file
                st.session_state["msgraph_preview_data"] = _get_file_preview_data(provider, file["id"])
    
    # Display file preview and import button
    with col2:
        selected_item = st.session_state.get("msgraph_selected_item")
        preview_data = st.session_state.get("msgraph_preview_data")
        
        if selected_item and preview_data is not None:
            st.write(f"Selected: **{selected_item['name']}**")
            
            # Display file metadata
            st.write(f"Type: {selected_item.get('type', 'Unknown')}")
            st.write(f"Size: {selected_item.get('size', 'Unknown')} bytes")
            st.write(f"Modified: {selected_item.get('modified', 'Unknown')}")
            
            # Display data preview
            st.write("Data Preview:")
            st.dataframe(preview_data)
            
            # Import button
            if st.button("Import Data"):
                full_data = _get_full_file_data(provider, selected_item["id"])
                
                if full_data is not None:
                    return {
                        "data": full_data,
                        "metadata": selected_item,
                        "source": "msgraph",
                        "path": selected_item["path"]
                    }
        else:
            st.write("Select a file to preview")
    
    return None


def _render_spreadsheets_selector(provider: MSGraphProvider, col1, col2) -> Optional[Dict[str, Any]]:
    """
    Render the spreadsheets selector UI.
    
    Args:
        provider: Microsoft Graph provider
        col1: First column for UI elements
        col2: Second column for UI elements
        
    Returns:
        Dictionary containing selected spreadsheet data and metadata, or None if no spreadsheet is selected
    """
    with col1:
        # Refresh button
        if st.button("Refresh Spreadsheets"):
            st.session_state["msgraph_spreadsheets"] = _list_spreadsheets(provider)
            st.session_state["msgraph_selected_spreadsheet"] = None
            st.session_state["msgraph_sheets"] = []
            st.session_state["msgraph_selected_sheet"] = None
            st.session_state["msgraph_preview_data"] = None
    
    # Display spreadsheets and handle selection
    spreadsheets = st.session_state.get("msgraph_spreadsheets", [])
    
    if not spreadsheets:
        st.session_state["msgraph_spreadsheets"] = _list_spreadsheets(provider)
        spreadsheets = st.session_state.get("msgraph_spreadsheets", [])
    
    with col1:
        # Display spreadsheets
        for spreadsheet in spreadsheets:
            if st.button(f"📊 {spreadsheet['name']}", key=f"spreadsheet_{spreadsheet['id']}"):
                st.session_state["msgraph_selected_spreadsheet"] = spreadsheet
                st.session_state["msgraph_sheets"] = _list_sheets(provider, spreadsheet["id"])
                st.session_state["msgraph_selected_sheet"] = None
                st.session_state["msgraph_preview_data"] = None
    
    # Display sheets if a spreadsheet is selected
    selected_spreadsheet = st.session_state.get("msgraph_selected_spreadsheet")
    sheets = st.session_state.get("msgraph_sheets", [])
    
    if selected_spreadsheet:
        with col1:
            st.write(f"Selected: **{selected_spreadsheet['name']}**")
            st.write("Sheets:")
            
            # Display sheets
            for sheet in sheets:
                if st.button(f"📄 {sheet['name']}", key=f"sheet_{sheet['id']}"):
                    st.session_state["msgraph_selected_sheet"] = sheet
                    st.session_state["msgraph_preview_data"] = _get_sheet_preview_data(
                        provider, selected_spreadsheet["id"], sheet["name"])
    
    # Display sheet preview and import button
    with col2:
        selected_sheet = st.session_state.get("msgraph_selected_sheet")
        preview_data = st.session_state.get("msgraph_preview_data")
        
        if selected_spreadsheet and selected_sheet and preview_data is not None:
            st.write(f"Selected: **{selected_spreadsheet['name']} / {selected_sheet['name']}**")
            
            # Display sheet metadata
            st.write(f"Rows: {selected_sheet.get('rows', 'Unknown')}")
            st.write(f"Columns: {selected_sheet.get('columns', 'Unknown')}")
            
            # Display data preview
            st.write("Data Preview:")
            st.dataframe(preview_data)
            
            # Import button
            if st.button("Import Data"):
                full_data = _get_full_sheet_data(provider, selected_spreadsheet["id"], selected_sheet["name"])
                
                if full_data is not None:
                    return {
                        "data": full_data,
                        "metadata": {
                            "spreadsheet_id": selected_spreadsheet["id"],
                            "spreadsheet_name": selected_spreadsheet["name"],
                            "sheet_id": selected_sheet["id"],
                            "sheet_name": selected_sheet["name"],
                        },
                        "source": "msgraph",
                        "path": f"{selected_spreadsheet['name']}/{selected_sheet['name']}"
                    }
        else:
            st.write("Select a spreadsheet and sheet to preview")
    
    return None


def _render_entity_selector(provider: MSGraphProvider, entity_type: str, col1, col2) -> Optional[Dict[str, Any]]:
    """
    Render the entity selector UI for users, groups, messages, or events.
    
    Args:
        provider: Microsoft Graph provider
        entity_type: Type of entity to display (users, groups, messages, events)
        col1: First column for UI elements
        col2: Second column for UI elements
        
    Returns:
        Dictionary containing selected entity data and metadata, or None if no entity is selected
    """
    with col1:
        # Refresh button
        if st.button(f"Refresh {entity_type.capitalize()}"):
            st.session_state[f"msgraph_{entity_type}"] = _get_entities(provider, entity_type)
            st.session_state["msgraph_selected_item"] = None
            st.session_state["msgraph_preview_data"] = None
    
    # Display entities and handle selection
    entities = st.session_state.get(f"msgraph_{entity_type}", [])
    
    if not entities:
        st.session_state[f"msgraph_{entity_type}"] = _get_entities(provider, entity_type)
        entities = st.session_state.get(f"msgraph_{entity_type}", [])
    
    with col1:
        # Display entities
        for entity in entities:
            display_name = entity.get("displayName", entity.get("subject", entity.get("id", "Unknown")))
            if st.button(f"{display_name}", key=f"entity_{entity['id']}"):
                st.session_state["msgraph_selected_item"] = entity
                st.session_state["msgraph_preview_data"] = pd.DataFrame([entity])
    
    # Display entity preview and import button
    with col2:
        selected_item = st.session_state.get("msgraph_selected_item")
        preview_data = st.session_state.get("msgraph_preview_data")
        
        if selected_item and preview_data is not None:
            display_name = selected_item.get("displayName", selected_item.get("subject", selected_item.get("id", "Unknown")))
            st.write(f"Selected: **{display_name}**")
            
            # Display data preview
            st.write("Data Preview:")
            st.dataframe(preview_data)
            
            # Import button
            if st.button("Import Data"):
                if preview_data is not None:
                    return {
                        "data": preview_data,
                        "metadata": {
                            "id": selected_item["id"],
                            "type": entity_type
                        },
                        "source": "msgraph",
                        "path": f"{entity_type}/{selected_item['id']}"
                    }
        else:
            st.write(f"Select a {entity_type[:-1]} to preview")
    
    return None


def _render_setup_instructions() -> None:
    """Render instructions for setting up Microsoft Graph integration."""
    st.warning("Microsoft Graph integration is not configured.")
    
    st.write("""
    ### Setup Instructions
    
    To connect to Microsoft Graph API, you need to provide authentication details:
    
    1. Go to [Azure Portal](https://portal.azure.com/)
    2. Create a new app registration or use an existing one
    3. Note down the Tenant ID and Client ID
    4. For client credentials flow, create a client secret
    5. Enter the details below
    """)
    
    # Authentication method selection
    auth_method = st.selectbox(
        "Authentication Method",
        ["device_code", "client_credentials", "interactive"],
        format_func=lambda x: {
            "device_code": "Device Code Flow",
            "client_credentials": "Client Credentials Flow",
            "interactive": "Interactive Browser Flow"
        }.get(x, x)
    )
    
    # Common fields
    tenant_id = st.text_input("Tenant ID")
    client_id = st.text_input("Client ID")
    
    # Client secret for client credentials flow
    client_secret = None
    if auth_method == "client_credentials":
        client_secret = st.text_input("Client Secret", type="password")
    
    if st.button("Connect to Microsoft Graph"):
        if auth_method == "client_credentials" and not client_secret:
            st.error("Client Secret is required for Client Credentials Flow")
        elif tenant_id and client_id:
            setup_msgraph_provider(tenant_id, client_id, client_secret, auth_method)
            st.experimental_rerun()
        else:
            st.error("Tenant ID and Client ID are required")
    
    return None


def setup_msgraph_provider(tenant_id: str, client_id: str, client_secret: Optional[str] = None,
                          auth_method: str = "device_code") -> bool:
    """
    Set up the Microsoft Graph provider with the provided credentials.
    
    Args:
        tenant_id: Tenant ID for the Microsoft 365 account
        client_id: Client ID for the application
        client_secret: Client secret for the application (required for client_credentials)
        auth_method: Authentication method to use
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Create configuration
    config = {
        "api": {
            "msgraph": {
                "tenant_id": tenant_id,
                "client_id": client_id,
                "auth_method": auth_method
            }
        }
    }
    
    # Add client secret if provided
    if client_secret:
        config["api"]["msgraph"]["client_secret"] = client_secret
    
    # Initialize provider
    return _initialize_provider(config["api"]["msgraph"])


def _initialize_provider(config: Dict[str, Any]) -> bool:
    """
    Initialize the Microsoft Graph provider.
    
    Args:
        config: Microsoft Graph configuration dictionary
        
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Create provider
        provider = MSGraphProvider(config)
        
        # Initialize provider (run async function in sync context)
        import asyncio
        success = asyncio.run(provider.initialize())
        
        if success:
            # Store provider in session state
            st.session_state["msgraph_provider"] = provider
            st.session_state["msgraph_provider_initialized"] = True
            st.session_state["msgraph_files"] = []
            st.session_state["msgraph_spreadsheets"] = []
            st.session_state["msgraph_selected_spreadsheet"] = None
            st.session_state["msgraph_sheets"] = []
            st.session_state["msgraph_selected_sheet"] = None
            st.session_state["msgraph_users"] = []
            st.session_state["msgraph_groups"] = []
            st.session_state["msgraph_messages"] = []
            st.session_state["msgraph_events"] = []
            st.session_state["msgraph_selected_item"] = None
            st.session_state["msgraph_preview_data"] = None
            return True
        else:
            st.error("Failed to initialize Microsoft Graph provider. Please check your credentials.")
            st.session_state["msgraph_provider_initialized"] = False
            return False
    
    except Exception as e:
        st.error(f"Error initializing Microsoft Graph provider: {str(e)}")
        st.session_state["msgraph_provider_initialized"] = False
        return False


def _list_files(provider: MSGraphProvider) -> List[Dict[str, Any]]:
    """
    List files from OneDrive.
    
    Args:
        provider: Microsoft Graph provider
        
    Returns:
        List of file metadata dictionaries
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.list_files())
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []


def _get_file_preview_data(provider: MSGraphProvider, file_id: str) -> Optional[pd.DataFrame]:
    """
    Get a preview of the file data.
    
    Args:
        provider: Microsoft Graph provider
        file_id: ID of the file
        
    Returns:
        Pandas DataFrame containing a preview of the file data
    """
    try:
        # Run async function in sync context
        import asyncio
        df = asyncio.run(provider.download_file_data(file_id))
        
        # Return first 10 rows for preview
        return df.head(10) if df is not None else None
    except Exception as e:
        st.error(f"Error getting file preview: {str(e)}")
        return None


def _get_full_file_data(provider: MSGraphProvider, file_id: str) -> Optional[pd.DataFrame]:
    """
    Get the full file data.
    
    Args:
        provider: Microsoft Graph provider
        file_id: ID of the file
        
    Returns:
        Pandas DataFrame containing the full file data
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.download_file_data(file_id))
    except Exception as e:
        st.error(f"Error downloading file data: {str(e)}")
        return None


def _list_spreadsheets(provider: MSGraphProvider) -> List[Dict[str, Any]]:
    """
    List spreadsheets from OneDrive.
    
    Args:
        provider: Microsoft Graph provider
        
    Returns:
        List of spreadsheet metadata dictionaries
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.list_spreadsheets())
    except Exception as e:
        st.error(f"Error listing spreadsheets: {str(e)}")
        return []


def _list_sheets(provider: MSGraphProvider, spreadsheet_id: str) -> List[Dict[str, Any]]:
    """
    List sheets in a spreadsheet.
    
    Args:
        provider: Microsoft Graph provider
        spreadsheet_id: ID of the spreadsheet
        
    Returns:
        List of sheet metadata dictionaries
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.list_sheets(spreadsheet_id))
    except Exception as e:
        st.error(f"Error listing sheets: {str(e)}")
        return []


def _get_sheet_preview_data(provider: MSGraphProvider, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Get a preview of the sheet data.
    
    Args:
        provider: Microsoft Graph provider
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        
    Returns:
        Pandas DataFrame containing a preview of the sheet data
    """
    try:
        # Run async function in sync context
        import asyncio
        df = asyncio.run(provider.get_sheet_data(spreadsheet_id, sheet_name))
        
        # Return first 10 rows for preview
        return df.head(10) if df is not None else None
    except Exception as e:
        st.error(f"Error getting sheet preview: {str(e)}")
        return None


def _get_full_sheet_data(provider: MSGraphProvider, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Get the full sheet data.
    
    Args:
        provider: Microsoft Graph provider
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet
        
    Returns:
        Pandas DataFrame containing the full sheet data
    """
    try:
        # Run async function in sync context
        import asyncio
        return asyncio.run(provider.get_sheet_data(spreadsheet_id, sheet_name))
    except Exception as e:
        st.error(f"Error downloading sheet data: {str(e)}")
        return None


def _get_entities(provider: MSGraphProvider, entity_type: str) -> List[Dict[str, Any]]:
    """
    Get entities from Microsoft Graph API.
    
    Args:
        provider: Microsoft Graph provider
        entity_type: Type of entity to get (users, groups, messages, events)
        
    Returns:
        List of entity dictionaries
    """
    try:
        # Get the manager from the provider
        manager = provider.manager
        
        # Call the appropriate method based on entity type
        if entity_type == "users":
            df = manager.get_users()
        elif entity_type == "groups":
            df = manager.get_groups()
        elif entity_type == "messages":
            df = manager.get_my_messages()
        elif entity_type == "events":
            df = manager.get_my_events()
        else:
            return []
        
        # Convert DataFrame to list of dictionaries
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error getting {entity_type}: {str(e)}")
        return []