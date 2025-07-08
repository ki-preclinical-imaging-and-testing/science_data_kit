"""
Observation Page Module for Science Data Kit

This module provides an observation page for workshop instructors to record
and analyze participant interactions with the Science Data Kit application.
It uses the observation protocol component to render a dashboard for managing
observation sessions, recording observations, and viewing observation data.
"""

import streamlit as st
from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.ui.components.observation_protocol import render_observation_dashboard
from science_data_kit.ui.components.analytics_tracking import track_page_view, track_interaction

class ObservationPage(BasePage):
    """
    Observation page for Science Data Kit.

    This page provides:
    - A dashboard for managing observation sessions
    - Tools for recording observations
    - Views for analyzing observation data
    - Export functionality for observation data
    """

    def __init__(self):
        """Initialize the observation page."""
        super().__init__("Observation", "Workshop Observation Dashboard")

    def render(self):
        """Render the observation page."""
        # Track page view
        track_page_view("Observation", "/observation")

        # Check if user has access to this page
        if not self._check_access():
            st.warning("This page is only accessible to workshop instructors.")
            return

        # Render the observation dashboard
        render_observation_dashboard()

    def _check_access(self):
        """
        Check if the user has access to the observation page.
        
        In a real application, this would check user roles or authentication.
        For now, we'll allow access to everyone for development purposes.
        
        Returns:
            True if the user has access, False otherwise.
        """
        # For development, always return True
        # In production, this would check user roles or authentication
        return True


def render_observation_page():
    """Render the observation page."""
    page = ObservationPage()
    page.render()


if __name__ == "__main__":
    render_observation_page()