"""
Feedback Dashboard Page for Science Data Kit

This module provides a wrapper for the feedback dashboard component.
"""

import streamlit as st
from science_data_kit.ui.components.feedback_database import render_feedback_dashboard

# Page configuration
st.set_page_config(
    page_title="Feedback Dashboard - Science Data Kit",
    page_icon="📝",
    layout="wide"
)

# Render the feedback dashboard
render_feedback_dashboard()