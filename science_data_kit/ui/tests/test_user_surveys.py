"""
Test script for the User Surveys component.

This script demonstrates the functionality of the user surveys component
by creating and displaying different types of surveys.

Run this script with:
streamlit run science_data_kit/ui/tests/test_user_surveys.py
"""

import streamlit as st
import sys
import os

# Add the parent directory to the path to import the user_surveys module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from science_data_kit.ui.components.user_surveys import (
    create_ui_experience_survey,
    create_workflow_survey,
    create_feature_survey,
    create_user_survey
)

def main():
    """Main function to demonstrate the user surveys component."""
    st.set_page_config(page_title="User Surveys Test", layout="wide")
    
    st.title("User Surveys Component Test")
    st.write("This page demonstrates the functionality of the user surveys component.")
    
    # Create tabs for different survey types
    tab1, tab2, tab3, tab4 = st.tabs([
        "UI Experience Survey", 
        "Workflow Survey", 
        "Feature Survey",
        "Custom Survey"
    ])
    
    with tab1:
        st.header("UI Experience Survey")
        st.write("This survey collects feedback on the user interface of the Science Data Kit.")
        
        if st.button("Show UI Experience Survey", key="show_ui_survey"):
            ui_survey = create_ui_experience_survey()
            survey_data = ui_survey.display()
            
            if survey_data:
                st.write("Survey data collected:")
                st.json(survey_data)
    
    with tab2:
        st.header("Workflow Survey")
        st.write("This survey collects feedback on specific workflows in the Science Data Kit.")
        
        if st.button("Show Workflow Survey", key="show_workflow_survey"):
            workflow_survey = create_workflow_survey()
            survey_data = workflow_survey.display()
            
            if survey_data:
                st.write("Survey data collected:")
                st.json(survey_data)
    
    with tab3:
        st.header("Feature Survey")
        st.write("This survey collects feedback on specific features of the Science Data Kit.")
        
        feature_name = st.text_input("Feature Name", value="Data Visualization")
        feature_description = st.text_area(
            "Feature Description", 
            value="This feature allows you to create interactive visualizations of your data."
        )
        
        if st.button("Show Feature Survey", key="show_feature_survey"):
            feature_survey = create_feature_survey(feature_name, feature_description)
            survey_data = feature_survey.display()
            
            if survey_data:
                st.write("Survey data collected:")
                st.json(survey_data)
    
    with tab4:
        st.header("Custom Survey")
        st.write("Create a custom survey with your own questions.")
        
        survey_id = st.text_input("Survey ID", value="custom_survey")
        survey_title = st.text_input("Survey Title", value="Custom Survey")
        survey_description = st.text_area(
            "Survey Description", 
            value="This is a custom survey with your own questions."
        )
        
        st.subheader("Questions")
        st.write("In a real application, you would define questions programmatically.")
        st.write("For this demo, we'll use a predefined set of questions.")
        
        questions = [
            {
                "id": "header_intro",
                "type": "header",
                "text": "Custom Survey"
            },
            {
                "id": "name",
                "type": "text",
                "text": "Your Name",
                "required": True
            },
            {
                "id": "email",
                "type": "text",
                "text": "Your Email",
                "required": True
            },
            {
                "id": "header_feedback",
                "type": "subheader",
                "text": "Your Feedback"
            },
            {
                "id": "rating",
                "type": "slider",
                "text": "How would you rate this custom survey?",
                "min_value": 1,
                "max_value": 5,
                "default_value": 3,
                "help": "1 = Poor, 5 = Excellent",
                "required": True
            },
            {
                "id": "comments",
                "type": "textarea",
                "text": "Any additional comments?",
                "height": 150
            }
        ]
        
        if st.button("Show Custom Survey", key="show_custom_survey"):
            custom_survey = create_user_survey(
                survey_id=survey_id,
                title=survey_title,
                description=survey_description,
                questions=questions
            )
            survey_data = custom_survey.display()
            
            if survey_data:
                st.write("Survey data collected:")
                st.json(survey_data)

if __name__ == "__main__":
    main()