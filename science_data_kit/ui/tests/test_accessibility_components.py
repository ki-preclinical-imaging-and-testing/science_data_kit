"""
Test script for accessibility components in Science Data Kit.

This script demonstrates the use of the terminology standardization, breadcrumbs,
screen reader support, and high contrast mode components.
"""

import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import the components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.terminology import get_term, get_category_terms
from components.breadcrumbs import create_breadcrumb_trail
from components.screen_reader import initialize_screen_reader_support, add_screen_reader_text, announce_page_load
from components.high_contrast import initialize_high_contrast_mode

def main():
    """Main function to demonstrate accessibility components."""
    # Initialize screen reader support
    initialize_screen_reader_support()
    
    # Initialize high contrast mode
    initialize_high_contrast_mode()
    
    # Announce page load to screen readers
    announce_page_load("Accessibility Components Test", "This page demonstrates the accessibility components of the Science Data Kit.")
    
    # Set up page title
    st.title("Accessibility Components Test")
    st.markdown("This page demonstrates the accessibility components of the Science Data Kit.")
    
    # Create breadcrumb trail
    create_breadcrumb_trail([
        {"label": "Home", "url": "/"},
        {"label": "Tests", "url": "/tests"},
        {"label": "Accessibility Components Test", "active": True}
    ])
    
    # Demonstrate terminology standardization
    st.header("Terminology Standardization")
    st.markdown("The following demonstrates the use of standardized terminology across the application.")
    
    # Display some standardized terms
    st.subheader("Data Terminology")
    data_terms = get_category_terms("DATA")
    for key, value in list(data_terms.items())[:5]:  # Show first 5 terms
        st.write(f"**{key}**: {value}")
    
    st.subheader("UI Terminology")
    ui_terms = get_category_terms("UI")
    for key, value in list(ui_terms.items())[:5]:  # Show first 5 terms
        st.write(f"**{key}**: {value}")
    
    # Example of using get_term in the UI
    st.markdown(f"This is a {get_term('BUTTON')} that performs a {get_term('FILTER')} operation.")
    
    # Demonstrate breadcrumbs
    st.header("Breadcrumbs")
    st.markdown("The breadcrumbs at the top of the page provide navigation context and allow users to navigate back to previous pages.")
    
    # Demonstrate screen reader support
    st.header("Screen Reader Support")
    st.markdown("The following demonstrates screen reader support features.")
    
    # Add screen reader only text
    st.markdown(add_screen_reader_text("This text is only visible to screen readers."), unsafe_allow_html=True)
    
    # Create a button with an accessible label
    st.button("Click Me", help="This button has screen reader support")
    
    # Demonstrate high contrast mode
    st.header("High Contrast Mode")
    st.markdown("High contrast mode can be toggled using the checkbox in the sidebar under 'Accessibility'.")
    st.markdown("When enabled, the application will use high contrast colors to improve visibility for users with visual impairments.")
    
    # Show a sample table to demonstrate high contrast styling
    st.subheader("Sample Table")
    st.table({
        "Column 1": [1, 2, 3],
        "Column 2": ["A", "B", "C"],
        "Column 3": [True, False, True]
    })
    
    # Show a sample chart to demonstrate high contrast styling
    st.subheader("Sample Chart")
    chart_data = {
        "Category": ["A", "B", "C", "D"],
        "Value": [10, 25, 15, 30]
    }
    st.bar_chart(chart_data)
    
    # Conclusion
    st.header("Conclusion")
    st.markdown("""
    These accessibility components help make the Science Data Kit more accessible to all users, including those with disabilities.
    
    The components implemented include:
    - Terminology standardization for consistent naming
    - Breadcrumbs for improved navigation
    - Screen reader support for visually impaired users
    - High contrast mode for users with visual impairments
    """)

if __name__ == "__main__":
    main()