"""
Workshop Application Module for Science Data Kit

This module provides a workshop-specific version of the Science Data Kit application.
It simplifies the UI and focuses on features relevant to workshop attendees.
"""

import streamlit as st
import os
import shutil
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path

from science_data_kit.ui.app import ScienceDataKitApp
from science_data_kit.ui.config import configure_page, DEFAULT_PAGE_CONFIG

class WorkshopApp(ScienceDataKitApp):
    """
    Workshop-specific application class for Science Data Kit.

    This class extends the main ScienceDataKitApp class and customizes it for workshop use:
    - Simplifies the navigation by including only the most relevant pages
    - Provides a more guided experience
    - Includes prominent links to the tutorial and documentation
    """

    def __init__(self):
        """Initialize the Workshop application."""
        # Apply workshop-specific Streamlit configuration
        self._apply_workshop_config()

        # Call the parent class constructor
        super().__init__()

        # Add workshop-specific session state variables
        self._initialize_workshop_state()

    def _apply_workshop_config(self):
        """Apply workshop-specific Streamlit configuration."""
        # Path to the workshop config file
        workshop_config_path = Path(__file__).parent / ".streamlit" / "config_workshop.toml"
        streamlit_config_path = Path.home() / ".streamlit" / "config.toml"

        # Create .streamlit directory in home if it doesn't exist
        os.makedirs(Path.home() / ".streamlit", exist_ok=True)

        # Copy the workshop config to the Streamlit config location
        shutil.copy(workshop_config_path, streamlit_config_path)

    def _initialize_workshop_state(self):
        """Initialize workshop-specific session state variables."""
        if "workshop_mode" not in st.session_state:
            st.session_state["workshop_mode"] = True

        if "tutorial_step" not in st.session_state:
            st.session_state["tutorial_step"] = 1

        if "tutorial_completed" not in st.session_state:
            st.session_state["tutorial_completed"] = False

    def _setup_pages(self):
        """Set up the application pages with a workshop-specific subset."""
        # Import page modules
        try:
            # Import page render functions from the pages package
            from science_data_kit.ui.pages import (
                render_dashboard_page,
                render_server_page,
                render_explore_page,
                render_about_page
            )

            # Register pages
            self.page_adapter.register_page("Dashboard", render_dashboard_page)
            self.page_adapter.register_page("Server", render_server_page)
            self.page_adapter.register_page("Explore", render_explore_page)
            self.page_adapter.register_page("About", render_about_page)

            # Workshop page (custom page for workshop)
            from science_data_kit.ui.pages.workshop import render_workshop_page
            self.page_adapter.register_page("Workshop", render_workshop_page)

        except ImportError as e:
            st.error(f"Error importing page modules: {e}")
            st.error("Please make sure all required modules are installed.")

    def _setup_navigation(self):
        """Set up the application navigation with workshop-specific pages."""
        # Create a list of Page objects
        pages = []

        # Add workshop-specific pages with icons
        if "Workshop" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Workshop"], title="workshop", icon="🧪"))
        if "Dashboard" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Dashboard"], title="dashboard", icon="📊"))
        if "Explore" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Explore"], title="explore", icon="🔍"))
        if "Server" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["Server"], title="server", icon="🖥️"))
        if "About" in self.page_adapter.pages:
            pages.append(st.Page(self.page_adapter.pages["About"], title="help", icon="❓"))

        # Check if there are any pages to display
        if not pages:
            st.error("No pages available for navigation. Please check the logs for import errors.")
            st.stop()
            return None

        # Use Streamlit's navigation
        pg = st.navigation(pages)

        return pg

    def run(self):
        """Run the Workshop application with additional UI elements."""
        try:
            # Add workshop header
            st.markdown("""
            <div style='background-color:#1E88E5; padding:10px; border-radius:5px; margin-bottom:20px'>
                <h1 style='color:white; text-align:center'>Science Data Kit Workshop</h1>
                <p style='color:white; text-align:center'>
                    Welcome to the Science Data Kit Workshop! This simplified interface is designed 
                    to help you learn the basics of the Science Data Kit.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Set up navigation
            pg = self._setup_navigation()

            # Run the selected page
            pg.run()

            # Add workshop footer
            st.markdown("""
            <div style='background-color:#F0F2F6; padding:10px; border-radius:5px; margin-top:20px'>
                <p style='text-align:center'>
                    <b>Need help?</b> Check the <a href='?page=help'>Help page</a> or ask a workshop instructor.
                </p>
                <p style='text-align:center'>
                    <a href='https://github.com/your-org/science_data_kit'>GitHub</a> | 
                    <a href='https://your-org.github.io/science_data_kit/'>Documentation</a>
                </p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error running application: {e}")
            st.error("Please check the logs for more information.")
            import traceback
            st.error(traceback.format_exc())

def run_workshop_app():
    """Run the Science Data Kit Workshop application."""
    app = WorkshopApp()
    app.run()

if __name__ == "__main__":
    run_workshop_app()
