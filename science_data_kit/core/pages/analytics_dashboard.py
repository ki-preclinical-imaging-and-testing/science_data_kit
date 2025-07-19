"""
Analytics Dashboard Page Module for Science Data Kit

This module provides the core functionality for the Analytics Dashboard page,
allowing users to view analytics data for the application.
"""

import time
import datetime
import uuid
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import json

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import AnalyticsDashboardPageData

class AnalyticsDashboardPage(BasePage):
    """
    Core functionality for the Analytics Dashboard page.
    
    This class provides the backend functionality for viewing analytics data,
    including page views, user interactions, and session information.
    """
    
    def __init__(self):
        """Initialize the Analytics Dashboard page."""
        super().__init__()
        self.title = "Analytics Dashboard"
        self.icon = "📈"
        
        # Initialize analytics storage path
        self.analytics_storage_path = str(Path.home() / ".science_data_kit" / "analytics")
        Path(self.analytics_storage_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize session data
        self.session_id = str(uuid.uuid4())
        self.session_start = time.time()
        self.analytics_enabled = True
        
        # Initialize analytics data
        self.page_views = []
        self.interactions = []
        
    def get_page_data(self) -> AnalyticsDashboardPageData:
        """
        Return data needed to render the Analytics Dashboard page.
        
        Returns:
            An instance of AnalyticsDashboardPageData containing the data needed
            to render the page.
        """
        # Calculate session duration
        session_duration = time.time() - self.session_start
        
        # Get page views and interactions
        page_views = self.get_page_views()
        interactions = self.get_interactions()
        
        # Get summaries
        page_views_summary = self.get_page_view_summary()
        interactions_summary = self.get_interaction_summary()
        
        # Create page data
        page_data = AnalyticsDashboardPageData(
            title=self.title,
            analytics_enabled=self.analytics_enabled,
            analytics_storage_path=self.analytics_storage_path,
            page_views=page_views,
            page_views_summary=page_views_summary,
            interactions=interactions,
            interactions_summary=interactions_summary,
            session_id=self.session_id,
            session_start=self.session_start,
            session_duration=session_duration
        )
        
        return page_data
    
    def track_page_view(self, page_name: str, page_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Track a page view.
        
        Args:
            page_name: The name of the page being viewed.
            page_path: Optional path to the page.
            
        Returns:
            A dictionary with the result of the operation.
        """
        if not self.analytics_enabled:
            return {"success": False, "message": "Analytics tracking is disabled."}
        
        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()
        
        page_view = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": self.session_id,
            "page_name": page_name,
            "page_path": page_path or page_name.lower(),
            "session_duration": timestamp - self.session_start
        }
        
        self.page_views.append(page_view)
        self._save_analytics_data()
        
        return {"success": True, "message": "Page view tracked successfully."}
    
    def track_interaction(self, 
                         interaction_type: str, 
                         component_id: str, 
                         component_type: str,
                         page_name: str,
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track a user interaction.
        
        Args:
            interaction_type: The type of interaction (click, input, etc.).
            component_id: The ID of the component being interacted with.
            component_type: The type of component (button, input, etc.).
            page_name: The name of the page where the interaction occurred.
            details: Optional additional details about the interaction.
            
        Returns:
            A dictionary with the result of the operation.
        """
        if not self.analytics_enabled:
            return {"success": False, "message": "Analytics tracking is disabled."}
        
        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()
        
        interaction = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": self.session_id,
            "interaction_type": interaction_type,
            "component_id": component_id,
            "component_type": component_type,
            "page_name": page_name,
            "details": details or {},
            "session_duration": timestamp - self.session_start
        }
        
        self.interactions.append(interaction)
        self._save_analytics_data()
        
        return {"success": True, "message": "Interaction tracked successfully."}
    
    def get_page_views(self) -> List[Dict[str, Any]]:
        """
        Get all tracked page views.
        
        Returns:
            A list of dictionaries containing page view data.
        """
        return self.page_views
    
    def get_interactions(self) -> List[Dict[str, Any]]:
        """
        Get all tracked interactions.
        
        Returns:
            A list of dictionaries containing interaction data.
        """
        return self.interactions
    
    def get_page_view_summary(self) -> Dict[str, Any]:
        """
        Get a summary of page views.
        
        Returns:
            A dictionary with page view statistics.
        """
        if not self.page_views:
            return {}
        
        # Convert to DataFrame for easier analysis
        page_views_df = pd.DataFrame(self.page_views)
        
        # Group by page_name and calculate statistics
        summary = page_views_df.groupby("page_name").agg({
            "page_name": "count",
            "session_duration": ["min", "max", "mean"]
        }).reset_index()
        
        # Rename columns for clarity
        summary.columns = ["page_name", "view_count", "min_duration", "max_duration", "avg_duration"]
        
        # Convert to dictionary for API response
        return summary.to_dict(orient="records")
    
    def get_interaction_summary(self) -> Dict[str, Any]:
        """
        Get a summary of user interactions.
        
        Returns:
            A dictionary with interaction statistics.
        """
        if not self.interactions:
            return {}
        
        # Convert to DataFrame for easier analysis
        interactions_df = pd.DataFrame(self.interactions)
        
        # Group by page_name and interaction_type and calculate statistics
        summary = interactions_df.groupby(["page_name", "interaction_type"]).agg({
            "interaction_type": "count"
        }).reset_index()
        
        # Rename columns for clarity
        summary.columns = ["page_name", "interaction_type", "interaction_count"]
        
        # Convert to dictionary for API response
        return summary.to_dict(orient="records")
    
    def export_analytics_data(self, 
                             format: str = "csv", 
                             path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export analytics data to CSV or JSON.
        
        Args:
            format: The export format ("csv" or "json").
            path: Optional path to save the files. If None, uses the default storage path.
            
        Returns:
            A dictionary with the result of the operation.
        """
        storage_path = Path(path or self.analytics_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if format.lower() == "csv":
                # Export page views
                page_views_path = storage_path / f"page_views_{timestamp}.csv"
                if self.page_views:
                    pd.DataFrame(self.page_views).to_csv(page_views_path, index=False)
                
                # Export interactions
                interactions_path = storage_path / f"interactions_{timestamp}.csv"
                if self.interactions:
                    pd.DataFrame(self.interactions).to_csv(interactions_path, index=False)
                
            elif format.lower() == "json":
                # Export page views
                page_views_path = storage_path / f"page_views_{timestamp}.json"
                if self.page_views:
                    with open(page_views_path, 'w') as f:
                        json.dump(self.page_views, f)
                
                # Export interactions
                interactions_path = storage_path / f"interactions_{timestamp}.json"
                if self.interactions:
                    with open(interactions_path, 'w') as f:
                        json.dump(self.interactions, f)
                
            else:
                return {"success": False, "error": f"Unsupported export format: {format}"}
            
            return {
                "success": True, 
                "message": "Analytics data exported successfully.",
                "page_views_path": str(page_views_path),
                "interactions_path": str(interactions_path)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_analytics_data(self) -> None:
        """
        Save analytics data to disk.
        This is called automatically after tracking page views or interactions.
        """
        # Save data every 10 page views or interactions to avoid excessive disk I/O
        total_events = len(self.page_views) + len(self.interactions)
        
        if total_events % 10 == 0:
            self.export_analytics_data()
    
    def clear_analytics_data(self) -> Dict[str, Any]:
        """
        Clear all analytics data.
        
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.page_views = []
            self.interactions = []
            return {"success": True, "message": "Analytics data cleared successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_analytics(self, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable analytics tracking.
        
        Args:
            enabled: Whether analytics tracking should be enabled.
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.analytics_enabled = enabled
            return {"success": True, "message": f"Analytics tracking {'enabled' if enabled else 'disabled'}."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_storage_path(self, path: str) -> Dict[str, Any]:
        """
        Update the analytics storage path.
        
        Args:
            path: The new storage path.
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            storage_path = Path(path)
            storage_path.mkdir(parents=True, exist_ok=True)
            self.analytics_storage_path = str(storage_path)
            return {"success": True, "message": f"Analytics storage path updated to: {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}