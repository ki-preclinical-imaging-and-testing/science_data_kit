"""
About/Learn Page Module for Science Data Kit

This module provides the About/Learn page for the Science Data Kit application.
It offers resources and educational materials about the toolkit, knowledge graphs, and FAIR data practices.
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union

from science_data_kit.ui.pages.base_page import BasePage

class AboutPage(BasePage):
    """
    About/Learn page for providing resources and educational materials.
    """

    def __init__(self):
        """Initialize the About/Learn page."""
        super().__init__(title="Learn: Resources and Community", icon="📖")

    def render_sidebar(self):
        """Render the sidebar for the About/Learn page."""
        super().render_sidebar()
        
        # Additional sidebar content can be added here if needed
        st.sidebar.markdown("### Quick Links")
        st.sidebar.markdown("""
        - [Documentation](#documentation-and-tutorials)
        - [Knowledge Graph Basics](#knowledge-graph-basics)
        - [Community and Support](#community-and-support)
        - [Video Tutorials](#video-tutorials)
        """)

    def render_content(self):
        """Render the main content for the About/Learn page."""
        st.title("Learn: Resources and Community")
        st.markdown(
            """
            Welcome to the **Learn** page! Here, you'll find resources to deepen your understanding of this toolkit, knowledge graphs, and FAIR data practices.
        
            Use the links below to explore further:
            """
        )

        # Sections with links
        st.subheader("📘 Documentation and Tutorials")
        st.markdown(
            """
            - [**Official Documentation**](https://example.com/docs) - Comprehensive guide to using the Science Data Toolkit.
            - [**Repository README**](https://github.com/your-repo/science-data-toolkit) - Quickstart and installation instructions.
            - [**Getting Started with Python Driver**](https://example.com/driver-tutorial) - Learn how to use the Python API effectively.
            """
        )

        st.subheader("🌐 Knowledge Graph Basics")
        st.markdown(
            """
            - [**What are Knowledge Graphs?**](https://neo4j.com/graphacademy/) - Explore how knowledge graphs are used in data management and AI.
            - [**FAIR Data Principles**](https://www.go-fair.org/fair-principles/) - Understand the importance of Findable, Accessible, Interoperable, and Reusable data.
            """
        )

        st.subheader("🏛️ Community and Support")
        st.markdown(
            """
            - [**Our Facility Website**](https://example.com/facility) - Learn about our mission and services.
            - [**Join the Community Forum**](https://example.com/forum) - Connect with other users and share insights.
            - [**Report an Issue or Suggest a Feature**](https://github.com/your-repo/science-data-toolkit/issues) - Contribute to the toolkit's development.
            """
        )

        st.subheader("🎥 Video Tutorials")
        st.markdown(
            """
            - [**Intro to Science Data Toolkit**](https://example.com/intro-video) - Watch a walkthrough of the core features.
            - [**Advanced Graph Queries**](https://example.com/graph-video) - Learn how to query and visualize data effectively.
            """
        )

        # Closing remarks
        st.markdown(
            """
            ---
            **We value your feedback!** If you have suggestions, questions, or want to contribute, check out the [GitHub repository](https://github.com/your-repo/science-data-toolkit) or reach out to our [community forum](https://example.com/forum).
            """
        )

def render_about_page():
    """Render the About/Learn page."""
    page = AboutPage()
    page.render()