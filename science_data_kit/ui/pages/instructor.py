"""
Instructor Notes Page for Science Data Kit

This module provides a wrapper for the instructor notes component.
"""

import streamlit as st
from science_data_kit.ui.components.instructor_notes import render_instructor_notes

# Page configuration
st.set_page_config(
    page_title="Instructor Notes - Science Data Kit",
    page_icon="👨‍🏫",
    layout="wide"
)

# Render the instructor notes
render_instructor_notes()