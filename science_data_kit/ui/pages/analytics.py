"""
Analytics Dashboard Page for Science Data Kit

This module provides a wrapper for the analytics dashboard component.
"""

import streamlit as st
from science_data_kit.ui.components.analytics_tracking import render_analytics_dashboard

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard - Science Data Kit",
    page_icon="📈",
    layout="wide"
)

# Render the analytics dashboard
render_analytics_dashboard()