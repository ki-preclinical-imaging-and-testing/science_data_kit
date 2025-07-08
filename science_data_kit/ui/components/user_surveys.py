"""
User Surveys Component for Science Data Kit

This module provides a user survey component for collecting targeted feedback
on specific features or workflows of the Science Data Kit. The surveys are designed
to be more focused than the general feedback form, allowing for detailed evaluation
of specific aspects of the user experience.
"""

import streamlit as st
import pandas as pd
import datetime
import json
import os
from typing import Dict, List, Optional, Union, Any, Callable

class UserSurvey:
    """
    A user survey component for collecting targeted feedback on specific features
    or workflows of the Science Data Kit.
    
    This class provides methods for creating, displaying, and processing user surveys.
    Survey data can be saved to CSV, JSON, or a database for later analysis.
    """
    
    def __init__(
        self, 
        survey_id: str,
        title: str,
        description: str,
        questions: List[Dict[str, Any]],
        save_dir: str = "survey_data",
        db_connection: Optional[Any] = None,
        on_complete: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize a new user survey.
        
        Args:
            survey_id: Unique identifier for the survey
            title: The title of the survey
            description: A description or instructions for the survey
            questions: List of question dictionaries defining the survey content
            save_dir: Directory to save survey data (if using file storage)
            db_connection: Database connection object (if using database storage)
            on_complete: Optional callback function to execute when survey is completed
        """
        self.survey_id = survey_id
        self.title = title
        self.description = description
        self.questions = questions
        self.save_dir = save_dir
        self.db_connection = db_connection
        self.on_complete = on_complete
        self.survey_data = {}
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def display(self) -> Dict[str, Any]:
        """
        Display the user survey in a Streamlit app.
        
        Returns:
            A dictionary containing the survey data if the form was submitted,
            otherwise an empty dictionary.
        """
        st.title(self.title)
        st.write(self.description)
        
        # Initialize responses dictionary
        responses = {}
        
        # Display each question based on its type
        for question in self.questions:
            q_id = question["id"]
            q_text = question["text"]
            q_type = question["type"]
            q_required = question.get("required", False)
            q_options = question.get("options", [])
            q_help = question.get("help", "")
            
            # Add required indicator if needed
            display_text = f"{q_text} {'*' if q_required else ''}"
            
            # Display different input types based on question type
            if q_type == "text":
                responses[q_id] = st.text_input(
                    display_text,
                    help=q_help
                )
            
            elif q_type == "textarea":
                responses[q_id] = st.text_area(
                    display_text,
                    height=question.get("height", 100),
                    help=q_help
                )
            
            elif q_type == "select":
                responses[q_id] = st.selectbox(
                    display_text,
                    options=q_options,
                    help=q_help
                )
            
            elif q_type == "multiselect":
                responses[q_id] = st.multiselect(
                    display_text,
                    options=q_options,
                    help=q_help
                )
            
            elif q_type == "radio":
                responses[q_id] = st.radio(
                    display_text,
                    options=q_options,
                    help=q_help
                )
            
            elif q_type == "checkbox":
                responses[q_id] = st.checkbox(
                    display_text,
                    help=q_help
                )
            
            elif q_type == "slider":
                min_val = question.get("min_value", 1)
                max_val = question.get("max_value", 5)
                default_val = question.get("default_value", (min_val + max_val) // 2)
                
                responses[q_id] = st.slider(
                    display_text,
                    min_value=min_val,
                    max_value=max_val,
                    value=default_val,
                    help=q_help
                )
            
            elif q_type == "rating":
                # Create a row of radio buttons for rating
                st.write(display_text)
                cols = st.columns(5)
                rating_value = None
                
                for i, col in enumerate(cols, 1):
                    with col:
                        if st.button(f"{i}", key=f"{q_id}_{i}"):
                            rating_value = i
                
                responses[q_id] = rating_value
            
            elif q_type == "date":
                responses[q_id] = st.date_input(
                    display_text,
                    help=q_help
                )
                if isinstance(responses[q_id], datetime.date):
                    responses[q_id] = responses[q_id].strftime("%Y-%m-%d")
            
            elif q_type == "time":
                responses[q_id] = st.time_input(
                    display_text,
                    help=q_help
                )
                if isinstance(responses[q_id], datetime.time):
                    responses[q_id] = responses[q_id].strftime("%H:%M:%S")
            
            elif q_type == "header":
                st.header(q_text)
                responses[q_id] = None
            
            elif q_type == "subheader":
                st.subheader(q_text)
                responses[q_id] = None
            
            elif q_type == "divider":
                st.divider()
                responses[q_id] = None
            
            # Add a small space between questions
            st.write("")
        
        # Submit Button
        submit_button = st.button("Submit Survey")
        
        if submit_button:
            # Validate required fields
            missing_required = [q["text"] for q in self.questions 
                               if q.get("required", False) and 
                               q["id"] in responses and 
                               not responses[q["id"]]]
            
            if missing_required:
                st.error(f"Please fill in the following required fields: {', '.join(missing_required)}")
                return {}
            
            # Collect all survey data
            self.survey_data = {
                "survey_id": self.survey_id,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "responses": responses
            }
            
            # Save the survey data
            self.save_survey()
            
            # Execute callback if provided
            if self.on_complete:
                self.on_complete(self.survey_data)
            
            # Show success message
            st.success("Thank you for completing the survey! Your feedback is valuable to us.")
            
            return self.survey_data
        
        return {}
    
    def save_survey(self) -> None:
        """
        Save the survey data to the specified storage (file or database).
        """
        if not self.survey_data:
            return
        
        # Generate a unique filename based on survey_id and timestamp
        timestamp = self.survey_data["timestamp"].replace(" ", "_").replace(":", "-")
        
        # Save as JSON
        json_path = os.path.join(self.save_dir, f"survey_{self.survey_id}_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump(self.survey_data, f, indent=2)
        
        # Save to CSV (append to existing or create new)
        csv_path = os.path.join(self.save_dir, f"survey_{self.survey_id}_responses.csv")
        
        # Flatten the nested dictionary for CSV storage
        flat_data = self._flatten_dict(self.survey_data)
        
        df = pd.DataFrame([flat_data])
        
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(csv_path, index=False)
        
        # Save to database if connection provided
        if self.db_connection:
            try:
                # Implementation depends on the database being used
                # This is a placeholder for database storage
                pass
            except Exception as e:
                st.error(f"Error saving to database: {str(e)}")
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flatten a nested dictionary for CSV storage.
        
        Args:
            d: The dictionary to flatten
            parent_key: The parent key for nested dictionaries
            sep: Separator between keys
            
        Returns:
            A flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, ", ".join(map(str, v))))
            else:
                items.append((new_key, v))
                
        return dict(items)

def create_user_survey(
    survey_id: str,
    title: str,
    description: str,
    questions: List[Dict[str, Any]],
    save_dir: str = "survey_data",
    db_connection: Optional[Any] = None,
    on_complete: Optional[Callable[[Dict[str, Any]], None]] = None
) -> UserSurvey:
    """
    Create a new user survey.
    
    Args:
        survey_id: Unique identifier for the survey
        title: The title of the survey
        description: A description or instructions for the survey
        questions: List of question dictionaries defining the survey content
        save_dir: Directory to save survey data (if using file storage)
        db_connection: Database connection object (if using database storage)
        on_complete: Optional callback function to execute when survey is completed
        
    Returns:
        A UserSurvey instance
    """
    return UserSurvey(survey_id, title, description, questions, save_dir, db_connection, on_complete)

# Predefined survey templates
def create_ui_experience_survey() -> UserSurvey:
    """
    Create a predefined survey for UI experience feedback.
    
    Returns:
        A UserSurvey instance configured for UI experience feedback
    """
    questions = [
        {
            "id": "header_intro",
            "type": "header",
            "text": "UI Experience Survey"
        },
        {
            "id": "user_role",
            "type": "select",
            "text": "What is your primary role?",
            "options": [
                "Select your role",
                "Researcher",
                "Data Scientist",
                "Software Developer",
                "Student",
                "Professor/Teacher",
                "Industry Professional",
                "Other"
            ],
            "required": True
        },
        {
            "id": "header_navigation",
            "type": "subheader",
            "text": "Navigation and Layout"
        },
        {
            "id": "nav_ease",
            "type": "slider",
            "text": "How easy is it to navigate through the application?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Difficult, 5 = Very Easy",
            "required": True
        },
        {
            "id": "layout_clarity",
            "type": "slider",
            "text": "How clear and organized is the layout?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Confusing, 5 = Very Clear",
            "required": True
        },
        {
            "id": "nav_improvements",
            "type": "textarea",
            "text": "What improvements would you suggest for navigation?",
            "height": 100
        },
        {
            "id": "header_visuals",
            "type": "subheader",
            "text": "Visual Design"
        },
        {
            "id": "color_scheme",
            "type": "slider",
            "text": "How would you rate the color scheme?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Poor, 5 = Excellent",
            "required": True
        },
        {
            "id": "typography",
            "type": "slider",
            "text": "How readable is the text throughout the application?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Difficult to Read, 5 = Very Easy to Read",
            "required": True
        },
        {
            "id": "visual_improvements",
            "type": "textarea",
            "text": "What visual design improvements would you suggest?",
            "height": 100
        },
        {
            "id": "header_interactions",
            "type": "subheader",
            "text": "Interactions and Responsiveness"
        },
        {
            "id": "responsiveness",
            "type": "slider",
            "text": "How responsive is the application?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Slow, 5 = Very Fast",
            "required": True
        },
        {
            "id": "interaction_intuitiveness",
            "type": "slider",
            "text": "How intuitive are the interactions?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Confusing, 5 = Very Intuitive",
            "required": True
        },
        {
            "id": "interaction_improvements",
            "type": "textarea",
            "text": "What interaction improvements would you suggest?",
            "height": 100
        },
        {
            "id": "header_overall",
            "type": "subheader",
            "text": "Overall Experience"
        },
        {
            "id": "overall_rating",
            "type": "slider",
            "text": "Overall, how would you rate the user interface?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Poor, 5 = Excellent",
            "required": True
        },
        {
            "id": "most_liked_feature",
            "type": "textarea",
            "text": "What aspect of the UI do you like the most?",
            "height": 100
        },
        {
            "id": "least_liked_feature",
            "type": "textarea",
            "text": "What aspect of the UI do you like the least?",
            "height": 100
        },
        {
            "id": "additional_comments",
            "type": "textarea",
            "text": "Any additional comments or suggestions?",
            "height": 150
        }
    ]
    
    return create_user_survey(
        survey_id="ui_experience",
        title="UI Experience Survey",
        description="Please provide your feedback on the user interface of the Science Data Kit. Your input will help us improve the user experience.",
        questions=questions
    )

def create_workflow_survey() -> UserSurvey:
    """
    Create a predefined survey for workflow feedback.
    
    Returns:
        A UserSurvey instance configured for workflow feedback
    """
    questions = [
        {
            "id": "header_intro",
            "type": "header",
            "text": "Workflow Experience Survey"
        },
        {
            "id": "workflow_type",
            "type": "select",
            "text": "Which workflow are you evaluating?",
            "options": [
                "Select a workflow",
                "Data Import",
                "Data Preprocessing",
                "Data Analysis",
                "Data Visualization",
                "Report Generation",
                "Complete Analysis Pipeline",
                "Other"
            ],
            "required": True
        },
        {
            "id": "workflow_frequency",
            "type": "select",
            "text": "How often do you use this workflow?",
            "options": [
                "Select an option",
                "Daily",
                "Several times a week",
                "Once a week",
                "Several times a month",
                "Once a month",
                "Less than once a month",
                "First time"
            ],
            "required": True
        },
        {
            "id": "header_efficiency",
            "type": "subheader",
            "text": "Workflow Efficiency"
        },
        {
            "id": "steps_clarity",
            "type": "slider",
            "text": "How clear are the steps in this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Unclear, 5 = Very Clear",
            "required": True
        },
        {
            "id": "steps_count",
            "type": "slider",
            "text": "How appropriate is the number of steps in this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Too Many Steps, 5 = Perfect Number of Steps",
            "required": True
        },
        {
            "id": "efficiency_rating",
            "type": "slider",
            "text": "How efficient is this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Inefficient, 5 = Very Efficient",
            "required": True
        },
        {
            "id": "efficiency_improvements",
            "type": "textarea",
            "text": "How could we make this workflow more efficient?",
            "height": 100
        },
        {
            "id": "header_usability",
            "type": "subheader",
            "text": "Workflow Usability"
        },
        {
            "id": "intuitiveness",
            "type": "slider",
            "text": "How intuitive is this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Confusing, 5 = Very Intuitive",
            "required": True
        },
        {
            "id": "error_handling",
            "type": "slider",
            "text": "How well does the workflow handle errors or invalid inputs?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Poorly, 5 = Very Well",
            "required": True
        },
        {
            "id": "guidance_quality",
            "type": "slider",
            "text": "How helpful is the guidance provided during the workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Not Helpful, 5 = Very Helpful",
            "required": True
        },
        {
            "id": "usability_improvements",
            "type": "textarea",
            "text": "How could we improve the usability of this workflow?",
            "height": 100
        },
        {
            "id": "header_outcomes",
            "type": "subheader",
            "text": "Workflow Outcomes"
        },
        {
            "id": "results_quality",
            "type": "slider",
            "text": "How satisfied are you with the results of this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Dissatisfied, 5 = Very Satisfied",
            "required": True
        },
        {
            "id": "results_usefulness",
            "type": "slider",
            "text": "How useful are the results for your work?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Not Useful, 5 = Very Useful",
            "required": True
        },
        {
            "id": "outcome_improvements",
            "type": "textarea",
            "text": "How could we improve the outcomes of this workflow?",
            "height": 100
        },
        {
            "id": "header_overall",
            "type": "subheader",
            "text": "Overall Experience"
        },
        {
            "id": "overall_rating",
            "type": "slider",
            "text": "Overall, how would you rate this workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Poor, 5 = Excellent",
            "required": True
        },
        {
            "id": "most_liked_aspect",
            "type": "textarea",
            "text": "What aspect of this workflow do you like the most?",
            "height": 100
        },
        {
            "id": "least_liked_aspect",
            "type": "textarea",
            "text": "What aspect of this workflow do you like the least?",
            "height": 100
        },
        {
            "id": "additional_comments",
            "type": "textarea",
            "text": "Any additional comments or suggestions?",
            "height": 150
        }
    ]
    
    return create_user_survey(
        survey_id="workflow_experience",
        title="Workflow Experience Survey",
        description="Please provide your feedback on a specific workflow in the Science Data Kit. Your input will help us improve the workflow experience.",
        questions=questions
    )

def create_feature_survey(feature_name: str, feature_description: str) -> UserSurvey:
    """
    Create a survey for a specific feature.
    
    Args:
        feature_name: The name of the feature being evaluated
        feature_description: A brief description of the feature
        
    Returns:
        A UserSurvey instance configured for feature feedback
    """
    questions = [
        {
            "id": "header_intro",
            "type": "header",
            "text": f"{feature_name} Feature Survey"
        },
        {
            "id": "feature_usage",
            "type": "select",
            "text": f"How often do you use the {feature_name} feature?",
            "options": [
                "Select an option",
                "Daily",
                "Several times a week",
                "Once a week",
                "Several times a month",
                "Once a month",
                "Less than once a month",
                "First time"
            ],
            "required": True
        },
        {
            "id": "header_usability",
            "type": "subheader",
            "text": "Feature Usability"
        },
        {
            "id": "ease_of_use",
            "type": "slider",
            "text": "How easy is this feature to use?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Difficult, 5 = Very Easy",
            "required": True
        },
        {
            "id": "intuitiveness",
            "type": "slider",
            "text": "How intuitive is this feature?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Confusing, 5 = Very Intuitive",
            "required": True
        },
        {
            "id": "learning_curve",
            "type": "slider",
            "text": "How would you rate the learning curve for this feature?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Steep, 5 = Very Gentle",
            "required": True
        },
        {
            "id": "usability_improvements",
            "type": "textarea",
            "text": "How could we improve the usability of this feature?",
            "height": 100
        },
        {
            "id": "header_functionality",
            "type": "subheader",
            "text": "Feature Functionality"
        },
        {
            "id": "completeness",
            "type": "slider",
            "text": "How complete is this feature's functionality?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Missing Essential Functions, 5 = Complete",
            "required": True
        },
        {
            "id": "reliability",
            "type": "slider",
            "text": "How reliable is this feature?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Unreliable, 5 = Very Reliable",
            "required": True
        },
        {
            "id": "performance",
            "type": "slider",
            "text": "How would you rate the performance of this feature?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Slow, 5 = Very Fast",
            "required": True
        },
        {
            "id": "missing_functionality",
            "type": "textarea",
            "text": "What functionality is missing from this feature?",
            "height": 100
        },
        {
            "id": "header_integration",
            "type": "subheader",
            "text": "Feature Integration"
        },
        {
            "id": "workflow_integration",
            "type": "slider",
            "text": "How well does this feature integrate with your workflow?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Poorly, 5 = Very Well",
            "required": True
        },
        {
            "id": "other_features_integration",
            "type": "slider",
            "text": "How well does this feature integrate with other features?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Very Poorly, 5 = Very Well",
            "required": True
        },
        {
            "id": "integration_improvements",
            "type": "textarea",
            "text": "How could we improve the integration of this feature?",
            "height": 100
        },
        {
            "id": "header_overall",
            "type": "subheader",
            "text": "Overall Experience"
        },
        {
            "id": "overall_rating",
            "type": "slider",
            "text": f"Overall, how would you rate the {feature_name} feature?",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "help": "1 = Poor, 5 = Excellent",
            "required": True
        },
        {
            "id": "most_liked_aspect",
            "type": "textarea",
            "text": "What aspect of this feature do you like the most?",
            "height": 100
        },
        {
            "id": "least_liked_aspect",
            "type": "textarea",
            "text": "What aspect of this feature do you like the least?",
            "height": 100
        },
        {
            "id": "additional_comments",
            "type": "textarea",
            "text": "Any additional comments or suggestions?",
            "height": 150
        }
    ]
    
    return create_user_survey(
        survey_id=f"{feature_name.lower().replace(' ', '_')}_feature",
        title=f"{feature_name} Feature Survey",
        description=f"Please provide your feedback on the {feature_name} feature. {feature_description} Your input will help us improve this feature.",
        questions=questions
    )

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="SDK User Survey", layout="wide")
    
    # Create and display a UI experience survey
    ui_survey = create_ui_experience_survey()
    survey_data = ui_survey.display()
    
    # You can process the survey_data further if needed
    if survey_data:
        st.write("Survey data collected successfully!")