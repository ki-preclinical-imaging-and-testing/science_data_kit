"""
Feedback Page Module for Science Data Kit Core

This module provides the core functionality for the Feedback page,
allowing users to submit feedback and administrators to view and analyze feedback data.
"""

import time
import datetime
import uuid
import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import FeedbackPageData

class FeedbackPage(BasePage):
    """
    Core functionality for the Feedback page.
    
    This class provides the backend functionality for collecting, storing,
    and analyzing feedback from users.
    """
    
    def __init__(self):
        """Initialize the Feedback page."""
        super().__init__()
        self.title = "Feedback"
        self.icon = "📝"
        
        # Initialize feedback database path
        self.feedback_db_path = str(Path.home() / ".science_data_kit" / "feedback" / "feedback.db")
        
        # Create storage directory if it doesn't exist
        storage_path = Path(self.feedback_db_path).parent
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        # Initialize connection status
        self.connection_status = {}
        self.connection_errors = {}
        
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
        return sqlite3.connect(self.feedback_db_path)
    
    def get_page_data(self) -> FeedbackPageData:
        """
        Return data needed to render the Feedback page.
        
        Returns:
            An instance of FeedbackPageData containing the data needed
            to render the page.
        """
        # Get feedback data
        feedback_data = self.get_feedback()
        
        # Get feedback summary
        feedback_summary = self.get_feedback_summary()
        
        # Get feedback categories and tags
        feedback_categories = self.get_feedback_categories()
        feedback_tags = self.get_feedback_tags()
        
        # Get feedback types and workshop IDs
        feedback_types = self.get_feedback_types()
        workshop_ids = self.get_workshop_ids()
        
        # Create page data
        page_data = FeedbackPageData(
            title=self.title,
            feedback_db_path=self.feedback_db_path,
            feedback_data=feedback_data,
            feedback_summary=feedback_summary,
            feedback_categories=feedback_categories,
            feedback_tags=feedback_tags,
            feedback_types=feedback_types,
            workshop_ids=workshop_ids,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors
        )
        
        return page_data
    
    def add_feedback(self, 
                    participant_id: str, 
                    workshop_id: str, 
                    feedback_type: str, 
                    rating: Optional[int] = None, 
                    comments: Optional[str] = None,
                    categories: Optional[List[str]] = None,
                    tags: Optional[List[str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            A dictionary with the result of the operation.
        """
        try:
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
            
            return {"success": True, "message": "Feedback added successfully", "feedback_id": feedback_id}
        except Exception as e:
            return {"success": False, "error": f"Error adding feedback: {str(e)}"}
    
    def get_feedback(self, 
                    feedback_id: Optional[str] = None,
                    participant_id: Optional[str] = None,
                    workshop_id: Optional[str] = None,
                    feedback_type: Optional[str] = None,
                    category: Optional[str] = None,
                    tag: Optional[str] = None,
                    min_rating: Optional[int] = None,
                    max_rating: Optional[int] = None) -> List[Dict[str, Any]]:
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
            A list of dictionaries containing the feedback data.
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
        
        # Convert DataFrame to list of dictionaries
        return df.to_dict(orient="records")
    
    def get_feedback_summary(self, 
                           group_by: Optional[str] = None,
                           feedback_type: Optional[str] = None,
                           workshop_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of feedback data.
        
        Args:
            group_by: Optional field to group by (e.g., "feedback_type", "workshop_id").
            feedback_type: Optional feedback type to filter by.
            workshop_id: Optional workshop ID to filter by.
            
        Returns:
            A dictionary containing the feedback summary.
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
        
        # Create summary dictionary
        summary = {
            "total_count": len(df),
            "by_type": {},
            "by_workshop": {}
        }
        
        # Add summary by type
        type_summary = self.get_feedback_summary(group_by="feedback_type")
        if isinstance(type_summary, pd.DataFrame) and not type_summary.empty:
            summary["by_type"] = type_summary.to_dict(orient="records")
        
        # Add summary by workshop
        workshop_summary = self.get_feedback_summary(group_by="workshop_id")
        if isinstance(workshop_summary, pd.DataFrame) and not workshop_summary.empty:
            summary["by_workshop"] = workshop_summary.to_dict(orient="records")
        
        return summary
    
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
    
    def get_feedback_types(self) -> List[str]:
        """
        Get all unique feedback types.
        
        Returns:
            A list of unique feedback types.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT feedback_type FROM feedback")
        types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return types
    
    def get_workshop_ids(self) -> List[str]:
        """
        Get all unique workshop IDs.
        
        Returns:
            A list of unique workshop IDs.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT workshop_id FROM feedback")
        workshop_ids = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return workshop_ids
    
    def export_feedback_data(self, format: str = "csv", path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export feedback data to CSV or JSON.
        
        Args:
            format: The export format ("csv" or "json").
            path: Optional path to save the file. If None, uses a default path.
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            # Get all feedback data
            feedback_data = self.get_feedback()
            
            if not feedback_data:
                return {"success": False, "error": "No feedback data to export"}
            
            # Convert to DataFrame
            feedback_df = pd.DataFrame(feedback_data)
            
            # Determine export path
            if path:
                export_path = Path(path)
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                export_dir = Path(self.feedback_db_path).parent
                export_path = export_dir / f"feedback_export_{timestamp}.{format.lower()}"
            
            # Export data
            if format.lower() == "csv":
                feedback_df.to_csv(export_path, index=False)
            elif format.lower() == "json":
                feedback_df.to_json(export_path, orient="records")
            else:
                return {"success": False, "error": f"Unsupported export format: {format}"}
            
            return {"success": True, "message": f"Data exported to: {str(export_path)}", "path": str(export_path)}
        except Exception as e:
            return {"success": False, "error": f"Error exporting feedback data: {str(e)}"}
    
    def clear_feedback_data(self) -> Dict[str, Any]:
        """
        Clear all feedback data from the database.
        
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM feedback_tags")
            cursor.execute("DELETE FROM feedback_categories")
            cursor.execute("DELETE FROM feedback")
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Feedback data cleared successfully"}
        except Exception as e:
            return {"success": False, "error": f"Error clearing feedback data: {str(e)}"}
    
    def update_feedback_db_path(self, path: str) -> Dict[str, Any]:
        """
        Update the feedback database path.
        
        Args:
            path: The new path for the feedback database.
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            # Validate the path
            new_path = Path(path)
            
            # Create the directory if it doesn't exist
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update the path
            self.feedback_db_path = str(new_path)
            
            # Initialize the database at the new location
            self._initialize_database()
            
            return {"success": True, "message": f"Feedback database path updated to: {path}"}
        except Exception as e:
            return {"success": False, "error": f"Error updating feedback database path: {str(e)}"}