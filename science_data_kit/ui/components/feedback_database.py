"""
Feedback Database Module for Science Data Kit

This module provides functionality for collecting, storing, and analyzing feedback
from workshop participants. It includes classes and functions for:
- Collecting structured feedback
- Storing feedback in a database
- Analyzing feedback data
- Generating feedback reports
"""

import streamlit as st
import pandas as pd
import json
import time
import datetime
import uuid
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

class FeedbackDatabase:
    """
    Feedback database class for Science Data Kit.
    
    This class provides methods for collecting, storing, and analyzing feedback
    from workshop participants.
    """
    
    def __init__(self):
        """Initialize the feedback database and set up session state."""
        self._initialize_feedback_state()
        self._initialize_database()
    
    def _initialize_feedback_state(self) -> None:
        """Initialize feedback-related session state variables."""
        if "feedback_db_path" not in st.session_state:
            # Default to a SQLite database in the user's home directory
            default_path = Path.home() / ".science_data_kit" / "feedback" / "feedback.db"
            st.session_state["feedback_db_path"] = str(default_path)
            
        # Create storage directory if it doesn't exist
        storage_path = Path(st.session_state["feedback_db_path"]).parent
        storage_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self) -> None:
        """Initialize the feedback database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create feedback table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            timestamp REAL,
            formatted_time TEXT,
            participant_id TEXT,
            workshop_id TEXT,
            feedback_type TEXT,
            rating INTEGER,
            comments TEXT,
            metadata TEXT
        )
        ''')
        
        # Create feedback_categories table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_categories (
            feedback_id TEXT,
            category TEXT,
            FOREIGN KEY (feedback_id) REFERENCES feedback (id),
            PRIMARY KEY (feedback_id, category)
        )
        ''')
        
        # Create feedback_tags table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_tags (
            feedback_id TEXT,
            tag TEXT,
            FOREIGN KEY (feedback_id) REFERENCES feedback (id),
            PRIMARY KEY (feedback_id, tag)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the feedback database.
        
        Returns:
            A connection to the SQLite database.
        """
        db_path = st.session_state["feedback_db_path"]
        return sqlite3.connect(db_path)
    
    def add_feedback(self, 
                    participant_id: str, 
                    workshop_id: str, 
                    feedback_type: str, 
                    rating: Optional[int] = None, 
                    comments: Optional[str] = None,
                    categories: Optional[List[str]] = None,
                    tags: Optional[List[str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add feedback to the database.
        
        Args:
            participant_id: Identifier for the participant providing feedback.
            workshop_id: Identifier for the workshop.
            feedback_type: Type of feedback (e.g., "workshop", "tutorial", "feature").
            rating: Optional numerical rating.
            comments: Optional text comments.
            categories: Optional list of categories for the feedback.
            tags: Optional list of tags for the feedback.
            metadata: Optional additional metadata about the feedback.
            
        Returns:
            The ID of the newly added feedback.
        """
        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()
        feedback_id = str(uuid.uuid4())
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Insert feedback
        cursor.execute('''
        INSERT INTO feedback (id, timestamp, formatted_time, participant_id, workshop_id, feedback_type, rating, comments, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_id,
            timestamp,
            formatted_time,
            participant_id,
            workshop_id,
            feedback_type,
            rating,
            comments,
            json.dumps(metadata or {})
        ))
        
        # Insert categories
        if categories:
            for category in categories:
                cursor.execute('''
                INSERT INTO feedback_categories (feedback_id, category)
                VALUES (?, ?)
                ''', (feedback_id, category))
        
        # Insert tags
        if tags:
            for tag in tags:
                cursor.execute('''
                INSERT INTO feedback_tags (feedback_id, tag)
                VALUES (?, ?)
                ''', (feedback_id, tag))
        
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_feedback(self, 
                    feedback_id: Optional[str] = None,
                    participant_id: Optional[str] = None,
                    workshop_id: Optional[str] = None,
                    feedback_type: Optional[str] = None,
                    category: Optional[str] = None,
                    tag: Optional[str] = None,
                    min_rating: Optional[int] = None,
                    max_rating: Optional[int] = None) -> pd.DataFrame:
        """
        Get feedback from the database.
        
        Args:
            feedback_id: Optional ID of specific feedback to retrieve.
            participant_id: Optional participant ID to filter by.
            workshop_id: Optional workshop ID to filter by.
            feedback_type: Optional feedback type to filter by.
            category: Optional category to filter by.
            tag: Optional tag to filter by.
            min_rating: Optional minimum rating to filter by.
            max_rating: Optional maximum rating to filter by.
            
        Returns:
            A pandas DataFrame containing the feedback data.
        """
        conn = self._get_connection()
        
        # Build the query
        query = "SELECT f.* FROM feedback f"
        params = []
        where_clauses = []
        
        # Add joins if filtering by category or tag
        if category:
            query += " JOIN feedback_categories fc ON f.id = fc.feedback_id"
            where_clauses.append("fc.category = ?")
            params.append(category)
        
        if tag:
            query += " JOIN feedback_tags ft ON f.id = ft.feedback_id"
            where_clauses.append("ft.tag = ?")
            params.append(tag)
        
        # Add where clauses for other filters
        if feedback_id:
            where_clauses.append("f.id = ?")
            params.append(feedback_id)
        
        if participant_id:
            where_clauses.append("f.participant_id = ?")
            params.append(participant_id)
        
        if workshop_id:
            where_clauses.append("f.workshop_id = ?")
            params.append(workshop_id)
        
        if feedback_type:
            where_clauses.append("f.feedback_type = ?")
            params.append(feedback_type)
        
        if min_rating is not None:
            where_clauses.append("f.rating >= ?")
            params.append(min_rating)
        
        if max_rating is not None:
            where_clauses.append("f.rating <= ?")
            params.append(max_rating)
        
        # Add where clause to query if there are any filters
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Execute the query
        df = pd.read_sql_query(query, conn, params=params)
        
        # Parse metadata JSON
        if not df.empty and 'metadata' in df.columns:
            df['metadata'] = df['metadata'].apply(lambda x: json.loads(x) if x else {})
        
        conn.close()
        
        return df
    
    def get_feedback_summary(self, 
                           group_by: Optional[str] = None,
                           feedback_type: Optional[str] = None,
                           workshop_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get a summary of feedback data.
        
        Args:
            group_by: Optional field to group by (e.g., "feedback_type", "workshop_id").
            feedback_type: Optional feedback type to filter by.
            workshop_id: Optional workshop ID to filter by.
            
        Returns:
            A pandas DataFrame containing the feedback summary.
        """
        conn = self._get_connection()
        
        # Build the query
        query = "SELECT "
        group_fields = []
        
        if group_by:
            if group_by in ["feedback_type", "workshop_id", "participant_id"]:
                query += f"{group_by}, "
                group_fields.append(group_by)
        
        query += "COUNT(*) as count, AVG(rating) as avg_rating, MIN(rating) as min_rating, MAX(rating) as max_rating"
        
        query += " FROM feedback"
        
        # Add where clauses for filters
        where_clauses = []
        params = []
        
        if feedback_type:
            where_clauses.append("feedback_type = ?")
            params.append(feedback_type)
        
        if workshop_id:
            where_clauses.append("workshop_id = ?")
            params.append(workshop_id)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Add group by clause
        if group_fields:
            query += " GROUP BY " + ", ".join(group_fields)
        
        # Execute the query
        df = pd.read_sql_query(query, conn, params=params)
        
        conn.close()
        
        return df
    
    def get_feedback_categories(self) -> List[str]:
        """
        Get all unique feedback categories.
        
        Returns:
            A list of unique category names.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM feedback_categories")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return categories
    
    def get_feedback_tags(self) -> List[str]:
        """
        Get all unique feedback tags.
        
        Returns:
            A list of unique tag names.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT tag FROM feedback_tags")
        tags = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return tags
    
    def export_feedback_data(self, format: str = "csv", path: Optional[str] = None) -> str:
        """
        Export feedback data to CSV or JSON.
        
        Args:
            format: The export format ("csv" or "json").
            path: Optional path to save the file. If None, uses a default path.
            
        Returns:
            The path to the exported file.
        """
        # Get all feedback data
        feedback_df = self.get_feedback()
        
        if feedback_df.empty:
            return "No feedback data to export"
        
        # Determine export path
        if path:
            export_path = Path(path)
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path(st.session_state["feedback_db_path"]).parent
            export_path = export_dir / f"feedback_export_{timestamp}.{format.lower()}"
        
        # Export data
        if format.lower() == "csv":
            feedback_df.to_csv(export_path, index=False)
        elif format.lower() == "json":
            feedback_df.to_json(export_path, orient="records")
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return str(export_path)
    
    def clear_feedback_data(self) -> None:
        """Clear all feedback data from the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM feedback_tags")
        cursor.execute("DELETE FROM feedback_categories")
        cursor.execute("DELETE FROM feedback")
        
        conn.commit()
        conn.close()

# Create a singleton instance of the feedback database
_feedback_database = None

def get_feedback_database() -> FeedbackDatabase:
    """
    Get the singleton instance of the feedback database.
    
    Returns:
        The FeedbackDatabase instance.
    """
    global _feedback_database
    if _feedback_database is None:
        _feedback_database = FeedbackDatabase()
    return _feedback_database

def render_feedback_dashboard():
    """
    Render a feedback dashboard for workshop instructors.
    
    This function creates a Streamlit UI for viewing and analyzing feedback data.
    """
    st.title("Workshop Feedback Dashboard")
    
    feedback_db = get_feedback_database()
    
    # Feedback Summary
    st.header("Feedback Summary")
    
    # Filters
    with st.expander("Filters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            feedback_type_filter = st.selectbox(
                "Feedback Type",
                options=["All"] + list(pd.unique(feedback_db.get_feedback()["feedback_type"].dropna())),
                key="feedback_type_filter"
            )
        
        with col2:
            workshop_id_filter = st.selectbox(
                "Workshop ID",
                options=["All"] + list(pd.unique(feedback_db.get_feedback()["workshop_id"].dropna())),
                key="workshop_id_filter"
            )
    
    # Apply filters
    feedback_type = None if feedback_type_filter == "All" else feedback_type_filter
    workshop_id = None if workshop_id_filter == "All" else workshop_id_filter
    
    # Get summary data
    summary_by_type = feedback_db.get_feedback_summary(group_by="feedback_type", workshop_id=workshop_id)
    summary_by_workshop = feedback_db.get_feedback_summary(group_by="workshop_id", feedback_type=feedback_type)
    
    # Display summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Feedback Type")
        if summary_by_type.empty:
            st.info("No feedback data available")
        else:
            st.dataframe(summary_by_type)
    
    with col2:
        st.subheader("By Workshop")
        if summary_by_workshop.empty:
            st.info("No feedback data available")
        else:
            st.dataframe(summary_by_workshop)
    
    # Feedback Details
    st.header("Feedback Details")
    
    # Get detailed feedback data
    feedback_df = feedback_db.get_feedback(
        feedback_type=feedback_type,
        workshop_id=workshop_id
    )
    
    if feedback_df.empty:
        st.info("No feedback data available")
    else:
        # Sort by timestamp (most recent first)
        feedback_df = feedback_df.sort_values("timestamp", ascending=False)
        
        # Display feedback
        for _, row in feedback_df.iterrows():
            with st.expander(f"{row['feedback_type']} Feedback - {row['formatted_time']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Participant", row["participant_id"])
                    st.metric("Workshop", row["workshop_id"])
                
                with col2:
                    if pd.notna(row["rating"]):
                        st.metric("Rating", f"{row['rating']}/5")
                    
                    # Get categories and tags
                    categories_df = pd.read_sql_query(
                        "SELECT category FROM feedback_categories WHERE feedback_id = ?",
                        feedback_db._get_connection(),
                        params=[row["id"]]
                    )
                    
                    tags_df = pd.read_sql_query(
                        "SELECT tag FROM feedback_tags WHERE feedback_id = ?",
                        feedback_db._get_connection(),
                        params=[row["id"]]
                    )
                    
                    if not categories_df.empty:
                        st.write("Categories: " + ", ".join(categories_df["category"]))
                    
                    if not tags_df.empty:
                        st.write("Tags: " + ", ".join(tags_df["tag"]))
                
                if pd.notna(row["comments"]):
                    st.subheader("Comments")
                    st.write(row["comments"])
                
                if row["metadata"] and row["metadata"] != "{}":
                    st.subheader("Additional Data")
                    st.json(row["metadata"])
    
    # Export and Settings
    with st.expander("Export and Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Data (CSV)"):
                export_path = feedback_db.export_feedback_data(format="csv")
                st.success(f"Data exported to: {export_path}")
        
        with col2:
            if st.button("Export Data (JSON)"):
                export_path = feedback_db.export_feedback_data(format="json")
                st.success(f"Data exported to: {export_path}")
        
        if st.button("Clear Feedback Data", type="primary"):
            feedback_db.clear_feedback_data()
            st.success("Feedback data cleared")
            st.experimental_rerun()

def collect_workshop_feedback(workshop_id: str, participant_id: Optional[str] = None):
    """
    Render a feedback form for workshop participants.
    
    Args:
        workshop_id: Identifier for the workshop.
        participant_id: Optional identifier for the participant.
    
    Returns:
        True if feedback was submitted, False otherwise.
    """
    st.header("Workshop Feedback")
    
    st.markdown("""
    Please take a moment to provide feedback on your workshop experience.
    Your feedback helps us improve the Science Data Kit and future workshops.
    """)
    
    feedback_db = get_feedback_database()
    
    with st.form("workshop_feedback_form"):
        if not participant_id:
            participant_id = st.text_input("Participant ID (optional)")
        
        rating = st.slider("Overall Rating", min_value=1, max_value=5, value=3,
                          help="1 = Poor, 5 = Excellent")
        
        content_rating = st.slider("Content Quality", min_value=1, max_value=5, value=3,
                                 help="1 = Poor, 5 = Excellent")
        
        usability_rating = st.slider("Usability", min_value=1, max_value=5, value=3,
                                   help="1 = Poor, 5 = Excellent")
        
        documentation_rating = st.slider("Documentation Quality", min_value=1, max_value=5, value=3,
                                      help="1 = Poor, 5 = Excellent")
        
        comments = st.text_area("Comments", 
                              help="Please share any additional feedback, suggestions, or issues you encountered.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            most_useful = st.text_area("Most Useful Features", 
                                     help="What features or aspects of the workshop did you find most useful?")
        
        with col2:
            least_useful = st.text_area("Areas for Improvement", 
                                      help="What features or aspects of the workshop could be improved?")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            # Prepare metadata
            metadata = {
                "content_rating": content_rating,
                "usability_rating": usability_rating,
                "documentation_rating": documentation_rating,
                "most_useful": most_useful,
                "least_useful": least_useful
            }
            
            # Add feedback to database
            feedback_db.add_feedback(
                participant_id=participant_id or "anonymous",
                workshop_id=workshop_id,
                feedback_type="workshop",
                rating=rating,
                comments=comments,
                categories=["workshop"],
                tags=["sdk", "workshop"],
                metadata=metadata
            )
            
            st.success("Thank you for your feedback!")
            return True
    
    return False