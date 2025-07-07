"""
Feedback Form Component for Science Data Kit

This module provides a feedback form component for collecting user feedback
on the Science Data Kit. The form includes fields for rating different aspects
of the SDK, providing comments, and suggesting improvements.
"""

import streamlit as st
import pandas as pd
import datetime
import json
import os
from typing import Dict, List, Optional, Union, Any

class FeedbackForm:
    """
    A feedback form component for collecting user feedback on the Science Data Kit.
    
    This class provides methods for creating, displaying, and processing feedback forms.
    Feedback data can be saved to CSV, JSON, or a database for later analysis.
    """
    
    def __init__(
        self, 
        title: str = "Science Data Kit Feedback",
        description: str = "Please provide your feedback to help us improve the Science Data Kit.",
        save_dir: str = "feedback_data",
        db_connection: Optional[Any] = None
    ):
        """
        Initialize a new feedback form.
        
        Args:
            title: The title of the feedback form
            description: A description or instructions for the feedback form
            save_dir: Directory to save feedback data (if using file storage)
            db_connection: Database connection object (if using database storage)
        """
        self.title = title
        self.description = description
        self.save_dir = save_dir
        self.db_connection = db_connection
        self.feedback_data = {}
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def display(self) -> Dict[str, Any]:
        """
        Display the feedback form in a Streamlit app.
        
        Returns:
            A dictionary containing the feedback data if the form was submitted,
            otherwise an empty dictionary.
        """
        st.title(self.title)
        st.write(self.description)
        
        # User Information Section
        st.header("User Information")
        name = st.text_input("Name (Optional)")
        email = st.text_input("Email (Optional)")
        role = st.selectbox(
            "Your Role",
            options=[
                "Select your role",
                "Researcher",
                "Data Scientist",
                "Software Developer",
                "Student",
                "Professor/Teacher",
                "Industry Professional",
                "Other"
            ]
        )
        
        if role == "Other":
            role_other = st.text_input("Please specify your role")
            role = role_other if role_other else role
        
        experience_level = st.select_slider(
            "Experience with data analysis tools",
            options=["Beginner", "Intermediate", "Advanced", "Expert"]
        )
        
        # SDK Usage Section
        st.header("SDK Usage")
        usage_duration = st.selectbox(
            "How long have you been using the Science Data Kit?",
            options=[
                "Select an option",
                "Just started",
                "Less than a month",
                "1-3 months",
                "3-6 months",
                "6-12 months",
                "More than a year"
            ]
        )
        
        usage_frequency = st.selectbox(
            "How often do you use the Science Data Kit?",
            options=[
                "Select an option",
                "Daily",
                "Several times a week",
                "Once a week",
                "Several times a month",
                "Once a month",
                "Less than once a month"
            ]
        )
        
        primary_use = st.multiselect(
            "What do you primarily use the Science Data Kit for?",
            options=[
                "Data import/export",
                "Data cleaning/preprocessing",
                "Statistical analysis",
                "Machine learning",
                "Data visualization",
                "Report generation",
                "Teaching/education",
                "Research",
                "Other"
            ]
        )
        
        if "Other" in primary_use:
            primary_use_other = st.text_input("Please specify your primary use case")
            if primary_use_other:
                primary_use = [use if use != "Other" else primary_use_other for use in primary_use]
        
        # Rating Section
        st.header("Ratings")
        st.write("Please rate the following aspects of the Science Data Kit:")
        
        ease_of_use = st.slider(
            "Ease of Use",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Very Difficult, 5 = Very Easy"
        )
        
        documentation = st.slider(
            "Documentation Quality",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Poor, 5 = Excellent"
        )
        
        features = st.slider(
            "Feature Completeness",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Missing Essential Features, 5 = Has All Needed Features"
        )
        
        performance = st.slider(
            "Performance",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Very Slow, 5 = Very Fast"
        )
        
        reliability = st.slider(
            "Reliability",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Frequent Errors, 5 = Very Reliable"
        )
        
        ui_design = st.slider(
            "UI Design",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Poor, 5 = Excellent"
        )
        
        # Specific Features Section
        st.header("Feature Feedback")
        
        feature_ratings = {}
        features_to_rate = [
            "Data Import/Export",
            "Data Preprocessing",
            "Statistical Analysis",
            "Machine Learning",
            "Data Visualization",
            "Report Generation",
            "User Interface",
            "Documentation",
            "Performance",
            "Error Handling"
        ]
        
        for feature in features_to_rate:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(feature)
            with col2:
                feature_ratings[feature] = st.selectbox(
                    f"Rate {feature}",
                    options=["N/A", "1", "2", "3", "4", "5"],
                    key=f"feature_{feature}",
                    label_visibility="collapsed"
                )
        
        # Open-ended Feedback Section
        st.header("Detailed Feedback")
        
        likes = st.text_area(
            "What do you like most about the Science Data Kit?",
            height=100
        )
        
        dislikes = st.text_area(
            "What do you like least about the Science Data Kit?",
            height=100
        )
        
        missing_features = st.text_area(
            "What features would you like to see added to the Science Data Kit?",
            height=100
        )
        
        improvements = st.text_area(
            "How could we improve the Science Data Kit?",
            height=100
        )
        
        bugs = st.text_area(
            "Have you encountered any bugs or issues? Please describe them.",
            height=100
        )
        
        # Workshop-specific Feedback (if applicable)
        workshop_feedback = None
        if st.checkbox("I attended a Science Data Kit workshop"):
            st.subheader("Workshop Feedback")
            
            workshop_date = st.date_input(
                "Workshop Date",
                value=datetime.date.today()
            )
            
            workshop_location = st.text_input("Workshop Location/Platform")
            
            workshop_rating = st.slider(
                "Overall Workshop Rating",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Poor, 5 = Excellent"
            )
            
            workshop_comments = st.text_area(
                "Workshop Comments",
                height=100
            )
            
            workshop_feedback = {
                "date": workshop_date.strftime("%Y-%m-%d"),
                "location": workshop_location,
                "rating": workshop_rating,
                "comments": workshop_comments
            }
        
        # Submit Button
        submit_button = st.button("Submit Feedback")
        
        if submit_button:
            # Collect all feedback data
            self.feedback_data = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_info": {
                    "name": name,
                    "email": email,
                    "role": role,
                    "experience_level": experience_level
                },
                "sdk_usage": {
                    "duration": usage_duration,
                    "frequency": usage_frequency,
                    "primary_use": primary_use
                },
                "ratings": {
                    "ease_of_use": ease_of_use,
                    "documentation": documentation,
                    "features": features,
                    "performance": performance,
                    "reliability": reliability,
                    "ui_design": ui_design
                },
                "feature_ratings": feature_ratings,
                "detailed_feedback": {
                    "likes": likes,
                    "dislikes": dislikes,
                    "missing_features": missing_features,
                    "improvements": improvements,
                    "bugs": bugs
                }
            }
            
            if workshop_feedback:
                self.feedback_data["workshop_feedback"] = workshop_feedback
            
            # Save the feedback
            self.save_feedback()
            
            # Show success message
            st.success("Thank you for your feedback! Your input helps us improve the Science Data Kit.")
            
            return self.feedback_data
        
        return {}
    
    def save_feedback(self) -> None:
        """
        Save the feedback data to the specified storage (file or database).
        """
        if not self.feedback_data:
            return
        
        # Generate a unique filename based on timestamp
        timestamp = self.feedback_data["timestamp"].replace(" ", "_").replace(":", "-")
        
        # Save as JSON
        json_path = os.path.join(self.save_dir, f"feedback_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump(self.feedback_data, f, indent=2)
        
        # Save to CSV (append to existing or create new)
        csv_path = os.path.join(self.save_dir, "all_feedback.csv")
        
        # Flatten the nested dictionary for CSV storage
        flat_data = self._flatten_dict(self.feedback_data)
        
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

def create_feedback_form(
    title: str = "Science Data Kit Feedback",
    description: str = "Please provide your feedback to help us improve the Science Data Kit.",
    save_dir: str = "feedback_data",
    db_connection: Optional[Any] = None
) -> FeedbackForm:
    """
    Create a new feedback form.
    
    Args:
        title: The title of the feedback form
        description: A description or instructions for the feedback form
        save_dir: Directory to save feedback data (if using file storage)
        db_connection: Database connection object (if using database storage)
        
    Returns:
        A FeedbackForm instance
    """
    return FeedbackForm(title, description, save_dir, db_connection)

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="SDK Feedback Form", layout="wide")
    
    feedback_form = create_feedback_form()
    feedback_data = feedback_form.display()
    
    # You can process the feedback_data further if needed
    if feedback_data:
        st.write("Feedback data collected successfully!")