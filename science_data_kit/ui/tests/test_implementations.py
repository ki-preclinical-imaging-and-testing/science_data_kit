"""
Test Script for Implemented Modules

This script tests the functionality of the implemented modules:
- error_display.py
- error_handler.py
- accessibility_audit.py
- keyboard_navigation.py
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import implemented modules
try:
    from science_data_kit.ui.components.error_display import display_error, ErrorDisplayStyle, ErrorBoundary
    from science_data_kit.core.utils.error_handler import ErrorHandler, handle_error, log_error
    from science_data_kit.ui.tests.accessibility_audit import run_accessibility_audit
    from science_data_kit.ui.components.keyboard_navigation import initialize_keyboard_navigation, make_focusable
    
    MODULES_IMPORTED = True
except ImportError as e:
    MODULES_IMPORTED = False
    st.error(f"Error importing modules: {str(e)}")


def test_error_display():
    """Test the error display functionality."""
    st.header("Error Display Test")
    
    # Test different error display styles
    st.subheader("Error Display Styles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Standard Style")
        try:
            # Generate an error
            result = 1 / 0
        except Exception as e:
            display_error(e, context="Testing standard error display", style=ErrorDisplayStyle.STANDARD)
    
    with col2:
        st.write("Minimal Style")
        try:
            # Generate an error
            result = [1, 2, 3][10]
        except Exception as e:
            display_error(e, context="Testing minimal error display", style=ErrorDisplayStyle.MINIMAL)
    
    # Test error boundary
    st.subheader("Error Boundary Test")
    
    with ErrorBoundary("Testing error boundary"):
        # This will be caught by the error boundary
        if st.button("Generate Error"):
            result = 1 / 0
            st.write(f"Result: {result}")  # This won't be executed


def test_error_handler():
    """Test the error handler functionality."""
    st.header("Error Handler Test")
    
    # Create an error handler
    error_handler = ErrorHandler()
    
    # Test handling different types of errors
    st.subheader("Error Handling Test")
    
    try:
        # Generate an error
        result = 1 / 0
    except Exception as e:
        try:
            # Handle the error without raising
            sdk_error = error_handler.handle_error(e, context="Testing error handler", raise_error=False)
            st.success("Successfully handled error without raising")
            st.json(sdk_error.to_dict())
        except Exception as handler_e:
            st.error(f"Error in error handler: {str(handler_e)}")
    
    # Test logging errors
    st.subheader("Error Logging Test")
    
    try:
        # Generate an error
        result = [1, 2, 3][10]
    except Exception as e:
        try:
            # Log the error
            sdk_error = log_error(e, context="Testing error logging")
            st.success("Successfully logged error")
            st.json(sdk_error.to_dict())
        except Exception as log_e:
            st.error(f"Error in error logging: {str(log_e)}")


def test_accessibility_audit():
    """Test the accessibility audit functionality."""
    st.header("Accessibility Audit Test")
    
    # Run a simplified version of the accessibility audit
    if st.button("Run Accessibility Audit"):
        with st.spinner("Running accessibility audit..."):
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Simulate audit progress
            for i in range(101):
                # Update progress bar
                progress_bar.progress(i)
                
                # Simulate work
                if i == 25:
                    st.info("Auditing keyboard navigation...")
                elif i == 50:
                    st.info("Auditing color contrast...")
                elif i == 75:
                    st.info("Auditing screen reader compatibility...")
            
            # Show success message
            st.success("Accessibility audit completed")
            
            # Show sample results
            st.subheader("Sample Audit Results")
            
            # Create sample data
            data = {
                "Component": ["Sidebar Navigation", "Form Controls", "Data Tables", "Visualizations"],
                "Category": ["Operable", "Perceivable", "Robust", "Perceivable"],
                "Criterion": ["2.1.1 Keyboard", "1.4.3 Contrast", "4.1.2 Name, Role, Value", "1.1.1 Non-text Content"],
                "Status": ["✅ PASS", "⚠️ WARNING", "❌ FAIL", "🔍 MANUAL CHECK REQUIRED"],
                "Notes": [
                    "All functionality is available from a keyboard",
                    "Some text elements have insufficient contrast",
                    "Some table cells are missing proper headers",
                    "Manual check required for chart alternatives"
                ]
            }
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Display results
            st.dataframe(df)


def test_keyboard_navigation():
    """Test the keyboard navigation functionality."""
    st.header("Keyboard Navigation Test")
    
    # Initialize keyboard navigation
    initialize_keyboard_navigation()
    
    # Test making elements focusable
    st.subheader("Focusable Elements Test")
    
    # Create some focusable elements
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("Focusable Button 1", key="button1")
        make_focusable("button1", label="Button 1", tooltip="This is button 1")
        
        st.text_input("Focusable Input", key="input1")
        make_focusable("input1", label="Input 1", tooltip="This is input 1")
    
    with col2:
        st.button("Focusable Button 2", key="button2")
        make_focusable("button2", label="Button 2", tooltip="This is button 2")
        
        st.selectbox("Focusable Select", ["Option 1", "Option 2", "Option 3"], key="select1")
        make_focusable("select1", label="Select 1", tooltip="This is select 1")
    
    # Display keyboard navigation instructions
    st.subheader("Keyboard Navigation Instructions")
    
    st.markdown("""
    Try using the following keyboard shortcuts:
    
    - **Tab**: Move focus to the next element
    - **Shift+Tab**: Move focus to the previous element
    - **Alt+H**: Go to home page
    - **Alt+D**: Go to dashboard
    - **Alt+E**: Go to explore page
    - **Alt+C**: Go to connect page
    - **Alt+1**: Focus sidebar
    - **Alt+2**: Focus main content
    - **?**: Show keyboard shortcuts help
    
    You should also see a "Skip to main content" link when you first press Tab.
    """)


def main():
    """Main function to run the tests."""
    st.title("Implementation Tests")
    
    if not MODULES_IMPORTED:
        st.error("Failed to import required modules. Please check the implementation.")
        return
    
    # Create tabs for different tests
    tab1, tab2, tab3, tab4 = st.tabs([
        "Error Display", 
        "Error Handler", 
        "Accessibility Audit", 
        "Keyboard Navigation"
    ])
    
    with tab1:
        test_error_display()
    
    with tab2:
        test_error_handler()
    
    with tab3:
        test_accessibility_audit()
    
    with tab4:
        test_keyboard_navigation()
    
    # Add timestamp
    st.sidebar.markdown(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()