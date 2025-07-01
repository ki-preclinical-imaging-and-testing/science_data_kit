"""
Google Sheets Selector Component for Science Data Kit

This module provides a Streamlit component for selecting and previewing
data from Google Sheets.
"""

import os
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple

from ...core.providers.registry import ProviderType
from ...core.providers.storage.google_sheets_provider import GoogleSheetsProvider
from ...core.config.providers import load_provider_config


def render_google_sheets_selector() -> Optional[Dict[str, Any]]:
    """
    Render a Google Sheets selection UI component.
    
    Returns:
        Dictionary containing selected sheet data and metadata, or None if no sheet is selected
    """
    st.subheader("Google Sheets Data Import")
    
    # Check if provider is configured
    config = load_provider_config()
    google_sheets_config = config.get("spreadsheet", {}).get("google_sheets", {})
    
    if not google_sheets_config or "credentials_file" not in google_sheets_config:
        return _render_setup_instructions()
    
    # Initialize provider if not already in session state
    if "google_sheets_provider" not in st.session_state:
        _initialize_provider(google_sheets_config)
    
    # If provider failed to initialize, show setup instructions
    if not st.session_state.get("google_sheets_provider_initialized", False):
        return _render_setup_instructions()
    
    # Get provider from session state
    provider = st.session_state["google_sheets_provider"]
    
    # Create UI for spreadsheet and sheet selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("Spreadsheets:")
        
        # Refresh button
        if st.button("Refresh Spreadsheets"):
            st.session_state["google_sheets_spreadsheets"] = _list_spreadsheets(provider)
            st.session_state["google_sheets_selected_spreadsheet"] = None
            st.session_state["google_sheets_sheets"] = []
            st.session_state["google_sheets_selected_sheet"] = None
            st.session_state["google_sheets_preview_data"] = None
    
    # Display spreadsheets and handle selection
    spreadsheets = st.session_state.get("google_sheets_spreadsheets", [])
    
    if not spreadsheets:
        st.session_state["google_sheets_spreadsheets"] = _list_spreadsheets(provider)
        spreadsheets = st.session_state.get("google_sheets_spreadsheets", [])
    
    with col1:
        # Display spreadsheets
        for spreadsheet in spreadsheets:
            if st.button(f"📊 {spreadsheet['name']}", key=f"spreadsheet_{spreadsheet['id']}"):
                st.session_state["google_sheets_selected_spreadsheet"] = spreadsheet
                st.session_state["google_sheets_sheets"] = _list_sheets(provider, spreadsheet["id"])
                st.session_state["google_sheets_selected_sheet"] = None
                st.session_state["google_sheets_preview_data"] = None
    
    # Display sheets if a spreadsheet is selected
    selected_spreadsheet = st.session_state.get("google_sheets_selected_spreadsheet")
    sheets = st.session_state.get("google_sheets_sheets", [])
    
    if selected_spreadsheet:
        with col1:
            st.write(f"Selected: **{selected_spreadsheet['name']}**")
            st.write("Sheets:")
            
            # Display sheets
            for sheet in sheets:
                if st.button(f"📄 {sheet['name']}", key=f"sheet_{sheet['id']}"):
                    st.session_state["google_sheets_selected_sheet"] = sheet
                    st.session_state["google_sheets_preview_data"] = _get_preview_data(
                        provider, selected_spreadsheet["id"], sheet["name"])
    
    # Display sheet preview and import button
    with col2:
        selected_sheet = st.session_state.get("google_sheets_selected_sheet")
        preview_data = st.session_state.get("google_sheets_preview_data")
        
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
                full_data = _get_full_data(provider, selected_spreadsheet["id"], selected_sheet["name"])
                
                if full_data is not None:
                    return {
                        "data": full_data,
                        "metadata": {
                            "spreadsheet_id": selected_spreadsheet["id"],
                            "spreadsheet_name": selected_spreadsheet["name"],
                            "sheet_id": selected_sheet["id"],
                            "sheet_name": selected_sheet["name"],
                        },
                        "source": "google_sheets",
                        "path": f"{selected_spreadsheet['name']}/{selected_sheet['name']}"
                    }
        else:
            st.write("Select a spreadsheet and sheet to preview")
    
    return None


def _render_setup_instructions() -> None:
    """Render instructions for setting up Google Sheets integration."""
    st.warning("Google Sheets integration is not configured.")
    
    st.write("""
    ### Setup Instructions
    
    To connect to Google Sheets, you need to provide OAuth2 credentials:
    
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Create a new project or select an existing one
    3. Enable the Google Sheets API and Google Drive API
    4. Create OAuth2 credentials (Desktop application)
    5. Download the credentials JSON file
    6. Enter the path to the credentials file below
    """)
    
    credentials_file = st.text_input("Path to credentials.json file")
    
    if st.button("Connect to Google Sheets") and credentials_file:
        if os.path.exists(credentials_file):
            setup_google_sheets_provider(credentials_file)
            st.experimental_rerun()
        else:
            st.error(f"File not found: {credentials_file}")
    
    return None


def setup_google_sheets_provider(credentials_file: str) -> bool:
    """
    Set up the Google Sheets provider with the provided credentials file.
    
    Args:
        credentials_file: Path to the credentials file
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Create configuration
    config = {
        "spreadsheet": {
            "google_sheets": {
                "credentials_file": credentials_file,
                "token_file": "google_sheets_token.json"
            }
        }
    }
    
    # Initialize provider
    return _initialize_provider(config["spreadsheet"]["google_sheets"])


def _initialize_provider(config: Dict[str, Any]) -> bool:
    """
    Initialize the Google Sheets provider.
    
    Args:
        config: Google Sheets configuration dictionary
        
    Returns:
        True if initialization was successful, False otherwise
    """
    try:
        # Create provider
        provider = GoogleSheetsProvider(config)
        
        # Initialize provider (run async function in sync context)
        import asyncio
        success = asyncio.run(provider.initialize())
        
        if success:
            # Store provider in session state
            st.session_state["google_sheets_provider"] = provider
            st.session_state["google_sheets_provider_initialized"] = True
            st.session_state["google_sheets_spreadsheets"] = []
            st.session_state["google_sheets_selected_spreadsheet"] = None
            st.session_state["google_sheets_sheets"] = []
            st.session_state["google_sheets_selected_sheet"] = None
            st.session_state["google_sheets_preview_data"] = None
            return True
        else:
            st.error("Failed to initialize Google Sheets provider. Please check your credentials.")
            st.session_state["google_sheets_provider_initialized"] = False
            return False
    
    except Exception as e:
        st.error(f"Error initializing Google Sheets provider: {str(e)}")
        st.session_state["google_sheets_provider_initialized"] = False
        return False


def _list_spreadsheets(provider: GoogleSheetsProvider) -> List[Dict[str, Any]]:
    """
    List available Google Sheets spreadsheets.
    
    Args:
        provider: Google Sheets provider
        
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


def _list_sheets(provider: GoogleSheetsProvider, spreadsheet_id: str) -> List[Dict[str, Any]]:
    """
    List sheets in a Google Sheets spreadsheet.
    
    Args:
        provider: Google Sheets provider
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


def _get_preview_data(provider: GoogleSheetsProvider, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Get a preview of the sheet data.
    
    Args:
        provider: Google Sheets provider
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
        return df.head(10)
    except Exception as e:
        st.error(f"Error getting sheet preview: {str(e)}")
        return None


def _get_full_data(provider: GoogleSheetsProvider, spreadsheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
    """
    Get the full sheet data.
    
    Args:
        provider: Google Sheets provider
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