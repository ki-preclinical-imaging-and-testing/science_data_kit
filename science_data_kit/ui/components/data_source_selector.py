"""
Data Source Selector Component for Science Data Kit

This module provides a Streamlit component for selecting data from various sources
like Microsoft Graph, Dropbox, and Google Sheets.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Tuple

from ...core.providers.registry import ProviderType, registry
from .dropbox_selector import render_dropbox_selector
from .google_sheets_selector import render_google_sheets_selector
from .msgraph_selector import render_msgraph_selector


def render_data_source_selector() -> Optional[Dict[str, Any]]:
    """
    Render a unified data source selection UI component.

    Returns:
        Dictionary containing selected data and metadata, or None if no data is selected
    """
    st.header("Data Source Selection")

    # Get available provider types
    provider_types = {
        ProviderType.API: "Microsoft 365 (MS Graph)",
        ProviderType.STORAGE: "File Storage (Dropbox)",
        ProviderType.SPREADSHEET: "Spreadsheets (Google Sheets)"
    }

    # Create tabs for different provider types
    tabs = st.tabs(list(provider_types.values()))

    # Microsoft Graph tab
    with tabs[0]:
        msgraph_data = render_msgraph_selector()
        if msgraph_data:
            return {
                "source": "msgraph",
                "data": msgraph_data.get("data"),
                "metadata": msgraph_data.get("metadata"),
                "path": msgraph_data.get("path")
            }

    # Dropbox tab
    with tabs[1]:
        dropbox_data = render_dropbox_selector()
        if dropbox_data:
            return {
                "source": "dropbox",
                "data": dropbox_data.get("data"),
                "metadata": {
                    "file_path": dropbox_data.get("file_path"),
                    "file_name": dropbox_data.get("file_name"),
                    "file_type": dropbox_data.get("file_type")
                }
            }

    # Google Sheets tab
    with tabs[2]:
        sheets_data = render_google_sheets_selector()
        if sheets_data:
            return {
                "source": "google_sheets",
                "data": sheets_data.get("data"),
                "metadata": {
                    "spreadsheet_id": sheets_data.get("spreadsheet_id"),
                    "spreadsheet_name": sheets_data.get("spreadsheet_name"),
                    "sheet_name": sheets_data.get("sheet_name")
                }
            }

    return None
