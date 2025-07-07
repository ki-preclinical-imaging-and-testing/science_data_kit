"""
Test script for the feedback form component.

This script tests the functionality of the feedback form component,
including rendering the form, submitting feedback, and saving the feedback data.

Usage:
    streamlit run science_data_kit/ui/tests/test_feedback_form.py
"""

import streamlit as st
import os
import sys
import tempfile
import shutil
import json
import pandas as pd
from pathlib import Path

# Add the parent directory to the path to allow importing the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the feedback form component
from science_data_kit.ui.components.feedback_form import create_feedback_form

def test_feedback_form():
    """
    Test the feedback form component.
    """
    st.title("Feedback Form Component Test")
    
    # Create a temporary directory for saving feedback data
    temp_dir = tempfile.mkdtemp()
    st.write(f"Feedback data will be saved to: {temp_dir}")
    
    # Create tabs for different test scenarios
    tab1, tab2, tab3 = st.tabs(["Basic Form", "Form with Workshop Feedback", "Saved Data"])
    
    with tab1:
        st.header("Basic Feedback Form")
        st.write("This tab tests the basic functionality of the feedback form.")
        
        # Create a feedback form
        feedback_form = create_feedback_form(
            title="Test Feedback Form",
            description="This is a test feedback form for the Science Data Kit.",
            save_dir=temp_dir
        )
        
        # Display the form
        feedback_data = feedback_form.display()
        
        # Display the feedback data if submitted
        if feedback_data:
            st.subheader("Submitted Feedback Data")
            st.json(feedback_data)
    
    with tab2:
        st.header("Feedback Form with Workshop Feedback")
        st.write("This tab tests the feedback form with workshop feedback enabled.")
        
        # Create a feedback form
        feedback_form = create_feedback_form(
            title="Workshop Feedback Form",
            description="Please provide feedback on the Science Data Kit workshop.",
            save_dir=temp_dir
        )
        
        # Display the form
        feedback_data = feedback_form.display()
        
        # Display the feedback data if submitted
        if feedback_data:
            st.subheader("Submitted Feedback Data")
            st.json(feedback_data)
    
    with tab3:
        st.header("Saved Feedback Data")
        st.write("This tab displays the feedback data saved to the temporary directory.")
        
        # Check if any feedback data has been saved
        json_files = list(Path(temp_dir).glob("*.json"))
        csv_file = Path(temp_dir) / "all_feedback.csv"
        
        if json_files:
            st.subheader("JSON Files")
            for json_file in json_files:
                st.write(f"File: {json_file.name}")
                with open(json_file, "r") as f:
                    data = json.load(f)
                st.json(data)
        else:
            st.info("No JSON files found. Submit feedback in the other tabs to create some.")
        
        if csv_file.exists():
            st.subheader("CSV File")
            df = pd.read_csv(csv_file)
            st.dataframe(df)
        else:
            st.info("No CSV file found. Submit feedback in the other tabs to create one.")
    
    # Add a button to clean up the temporary directory
    if st.button("Clean Up Temporary Directory"):
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        st.success(f"Cleaned up temporary directory: {temp_dir}")

def main():
    """
    Main function to run the test.
    """
    # Set page config
    st.set_page_config(
        page_title="Feedback Form Test",
        page_icon="📝",
        layout="wide"
    )
    
    # Run the test
    test_feedback_form()

if __name__ == "__main__":
    main()