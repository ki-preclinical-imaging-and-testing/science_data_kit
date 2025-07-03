"""
Main Application Module for Science Data Kit

This module provides the main entry point for the Science Data Kit application.
It handles initializing the application, setting up the UI, and routing to the appropriate pages.
"""

import streamlit as st
import importlib
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import sys
import os

from science_data_kit.ui.config import configure_page, DEFAULT_PAGE_CONFIG
from science_data_kit.ui.state import initialize_session_state
from science_data_kit.ui.adapters.page_adapter import PageAdapter

class ScienceDataKitApp:
    """
    Main application class for Science Data Kit.

    This class handles:
    - Application initialization
    - UI setup
    - Page routing
    - Session state management
    """

    def __init__(self):
        """Initialize the Science Data Kit application."""
        # Configure the page
        configure_page(
            title=DEFAULT_PAGE_CONFIG["page_title"],
            icon=DEFAULT_PAGE_CONFIG["page_icon"]
        )

        # Initialize session state
        initialize_session_state()

        # Create page adapter
        self.page_adapter = PageAdapter()

        # Set up pages
        self._setup_pages()

    def _setup_pages(self):
        """Set up the application pages."""
        # Import page modules
        try:
            # Dashboard page
            from science_data_kit.ui.pages.dashboard import render_dashboard_page
            self.page_adapter.register_page("Dashboard", render_dashboard_page)

            # Server page
            from science_data_kit.ui.pages.connect import render_server_page
            self.page_adapter.register_page("Server", render_server_page)

            # Survey page
            from science_data_kit.ui.pages.survey import render_survey_page
            self.page_adapter.register_page("Survey", render_survey_page)

            # Map page
            from science_data_kit.ui.pages.map import render_map_page
            self.page_adapter.register_page("Map", render_map_page)

            # Explore page
            from science_data_kit.ui.pages.explore import render_explore_page
            self.page_adapter.register_page("Explore", render_explore_page)

            # Ontology page
            from science_data_kit.ui.pages.ontology import render_ontology_page
            self.page_adapter.register_page("Ontology", render_ontology_page)

            # Chat page
            from science_data_kit.ui.pages.chat import render_chat_page
            self.page_adapter.register_page("Chat", render_chat_page)

            # File Browser page
            from science_data_kit.ui.pages.file_browser import render_file_browser_page
            self.page_adapter.register_page("Files", render_file_browser_page)

            # About/Learn page
            from science_data_kit.ui.pages.about import render_about_page
            self.page_adapter.register_page("About", render_about_page)

        except ImportError as e:
            st.error(f"Error importing page modules: {e}")
            st.error("Please make sure all required modules are installed.")

    def _setup_navigation(self):
        """Set up the application navigation using Streamlit's built-in pages system."""
        # Create a list of Page objects
        pages = []

        # Add pages with icons
        if "Dashboard" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Dashboard"], title="dashboard", icon="📊"))
        if "Server" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Server"], title="server", icon="🖥️"))
        if "Survey" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Survey"], title="survey", icon="🔭"))
        if "Map" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Map"], title="map", icon="🗺"))
        if "Explore" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Explore"], title="explore", icon="🏞"))
        if "Ontology" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Ontology"], title="ontology", icon="🧬"))
        if "Chat" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Chat"], title="chat", icon="💬"))
        if "Files" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Files"], title="files", icon="📁"))
        if "About" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["About"], title="learn", icon="📖"))

        # Check if there are any pages to display
        if not pages:
            st.error("No pages available for navigation. Please check the logs for import errors.")
            st.stop()
            return None

        # Use Streamlit's navigation
        pg = st.navigation(pages)

        return pg

    def run(self):
        """Run the Science Data Kit application."""
        try:
            # Set up navigation
            pg = self._setup_navigation()

            # Run the selected page
            pg.run()

        except Exception as e:
            st.error(f"Error running application: {e}")
            st.error("Please check the logs for more information.")
            import traceback
            st.error(traceback.format_exc())

def run_app():
    """Run the Science Data Kit application."""
    app = ScienceDataKitApp()
    app.run()

if __name__ == "__main__":
    run_app()
