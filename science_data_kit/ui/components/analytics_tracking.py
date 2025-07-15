"""
Analytics Tracking Module for Science Data Kit

This module provides functionality for tracking user interactions and page views
in the Science Data Kit application. It includes classes and functions for:
- Recording page views
- Tracking user interactions
- Storing analytics data
- Analyzing usage patterns
"""

import streamlit as st
import pandas as pd
import json
import time
import datetime
import uuid
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

class AnalyticsTracker:
    """
    Analytics tracking class for Science Data Kit.

    This class provides methods for tracking page views, user interactions,
    and other analytics data. It stores the data in session state and
    can export it to CSV or JSON for further analysis.
    """

    def __init__(self):
        """Initialize the analytics tracker and set up session state."""
        self._initialize_analytics_state()

    def _initialize_analytics_state(self) -> None:
        """Initialize analytics-related session state variables."""
        if "analytics_enabled" not in st.session_state:
            st.session_state["analytics_enabled"] = True

        if "analytics_session_id" not in st.session_state:
            st.session_state["analytics_session_id"] = str(uuid.uuid4())

        if "analytics_session_start" not in st.session_state:
            st.session_state["analytics_session_start"] = time.time()

        if "analytics_page_views" not in st.session_state:
            st.session_state["analytics_page_views"] = []

        if "analytics_interactions" not in st.session_state:
            st.session_state["analytics_interactions"] = []

        if "analytics_storage_path" not in st.session_state:
            # Default to a directory in the user's home directory
            default_path = Path.home() / ".science_data_kit" / "analytics"
            st.session_state["analytics_storage_path"] = str(default_path)

        # Create storage directory if it doesn't exist
        storage_path = Path(st.session_state["analytics_storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)

    def track_page_view(self, page_name: str, page_path: Optional[str] = None) -> None:
        """
        Track a page view.

        Args:
            page_name: The name of the page being viewed.
            page_path: Optional path to the page.
        """
        if not st.session_state.get("analytics_enabled", True):
            return

        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()

        page_view = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": st.session_state["analytics_session_id"],
            "page_name": page_name,
            "page_path": page_path or page_name.lower(),
            "session_duration": timestamp - st.session_state["analytics_session_start"]
        }

        st.session_state["analytics_page_views"].append(page_view)
        self._save_analytics_data()

    def track_interaction(self, 
                         interaction_type: str, 
                         component_id: str, 
                         component_type: str,
                         page_name: str,
                         details: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a user interaction.

        Args:
            interaction_type: The type of interaction (click, input, etc.).
            component_id: The ID of the component being interacted with.
            component_type: The type of component (button, input, etc.).
            page_name: The name of the page where the interaction occurred.
            details: Optional additional details about the interaction.
        """
        if not st.session_state.get("analytics_enabled", True):
            return

        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()

        interaction = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": st.session_state["analytics_session_id"],
            "interaction_type": interaction_type,
            "component_id": component_id,
            "component_type": component_type,
            "page_name": page_name,
            "details": details or {},
            "session_duration": timestamp - st.session_state["analytics_session_start"]
        }

        st.session_state["analytics_interactions"].append(interaction)
        self._save_analytics_data()

    def get_page_views(self) -> pd.DataFrame:
        """
        Get all tracked page views as a DataFrame.

        Returns:
            A pandas DataFrame containing all page view data.
        """
        if not st.session_state.get("analytics_page_views"):
            return pd.DataFrame()

        return pd.DataFrame(st.session_state["analytics_page_views"])

    def get_interactions(self) -> pd.DataFrame:
        """
        Get all tracked interactions as a DataFrame.

        Returns:
            A pandas DataFrame containing all interaction data.
        """
        if not st.session_state.get("analytics_interactions"):
            return pd.DataFrame()

        return pd.DataFrame(st.session_state["analytics_interactions"])

    def get_page_view_summary(self) -> pd.DataFrame:
        """
        Get a summary of page views.

        Returns:
            A pandas DataFrame with page view statistics.
        """
        page_views_df = self.get_page_views()
        if page_views_df.empty:
            return pd.DataFrame()

        summary = page_views_df.groupby("page_name").agg({
            "page_name": "count",
            "session_duration": ["min", "max", "mean"]
        })

        summary.columns = ["view_count", "min_duration", "max_duration", "avg_duration"]
        return summary.reset_index()

    def get_interaction_summary(self) -> pd.DataFrame:
        """
        Get a summary of user interactions.

        Returns:
            A pandas DataFrame with interaction statistics.
        """
        interactions_df = self.get_interactions()
        if interactions_df.empty:
            return pd.DataFrame()

        summary = interactions_df.groupby(["page_name", "interaction_type"]).agg({
            "interaction_type": "count"
        })

        summary.columns = ["interaction_count"]
        return summary.reset_index()

    def export_analytics_data(self, 
                             format: str = "csv", 
                             path: Optional[str] = None) -> Tuple[str, str]:
        """
        Export analytics data to CSV or JSON.

        Args:
            format: The export format ("csv" or "json").
            path: Optional path to save the files. If None, uses the default storage path.

        Returns:
            A tuple of (page_views_path, interactions_path) with the paths to the exported files.
        """
        storage_path = Path(path or st.session_state["analytics_storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        page_views_df = self.get_page_views()
        interactions_df = self.get_interactions()

        if format.lower() == "csv":
            page_views_path = storage_path / f"page_views_{timestamp}.csv"
            interactions_path = storage_path / f"interactions_{timestamp}.csv"

            if not page_views_df.empty:
                page_views_df.to_csv(page_views_path, index=False)

            if not interactions_df.empty:
                interactions_df.to_csv(interactions_path, index=False)

        elif format.lower() == "json":
            page_views_path = storage_path / f"page_views_{timestamp}.json"
            interactions_path = storage_path / f"interactions_{timestamp}.json"

            if not page_views_df.empty:
                page_views_df.to_json(page_views_path, orient="records")

            if not interactions_df.empty:
                interactions_df.to_json(interactions_path, orient="records")
        else:
            raise ValueError(f"Unsupported export format: {format}")

        return str(page_views_path), str(interactions_path)

    def _save_analytics_data(self) -> None:
        """
        Save analytics data to disk.
        This is called automatically after tracking page views or interactions.
        """
        # Check if auto-save is enabled in user preferences
        if not st.session_state.get("user_preferences", {}).get("auto_save", True):
            return

        # Save data every 10 page views or interactions to avoid excessive disk I/O
        total_events = (len(st.session_state.get("analytics_page_views", [])) + 
                       len(st.session_state.get("analytics_interactions", [])))

        if total_events % 10 == 0:
            self.export_analytics_data()

    def clear_analytics_data(self) -> None:
        """Clear all analytics data from session state."""
        st.session_state["analytics_page_views"] = []
        st.session_state["analytics_interactions"] = []

    def toggle_analytics(self, enabled: bool) -> None:
        """
        Enable or disable analytics tracking.

        Args:
            enabled: Whether analytics tracking should be enabled.
        """
        st.session_state["analytics_enabled"] = enabled

# Create a singleton instance of the analytics tracker
_analytics_tracker = None

def get_analytics_tracker() -> AnalyticsTracker:
    """
    Get the singleton instance of the analytics tracker.

    Returns:
        The AnalyticsTracker instance.
    """
    global _analytics_tracker
    if _analytics_tracker is None:
        _analytics_tracker = AnalyticsTracker()
    return _analytics_tracker

# Convenience functions for tracking
def track_page_view(page_name: str, page_path: Optional[str] = None) -> None:
    """
    Track a page view.

    Args:
        page_name: The name of the page being viewed.
        page_path: Optional path to the page.
    """
    tracker = get_analytics_tracker()
    tracker.track_page_view(page_name, page_path)

def track_interaction(interaction_type: str, 
                     component_id: str, 
                     component_type: str,
                     page_name: str,
                     details: Optional[Dict[str, Any]] = None) -> None:
    """
    Track a user interaction.

    Args:
        interaction_type: The type of interaction (click, input, etc.).
        component_id: The ID of the component being interacted with.
        component_type: The type of component (button, input, etc.).
        page_name: The name of the page where the interaction occurred.
        details: Optional additional details about the interaction.
    """
    tracker = get_analytics_tracker()
    tracker.track_interaction(interaction_type, component_id, component_type, page_name, details)

def render_analytics_dashboard():
    """
    Render an analytics dashboard with visualizations of usage data.

    This function creates a Streamlit UI for viewing analytics data,
    including page view statistics and user interaction patterns.
    """
    st.title("Analytics Dashboard")

    tracker = get_analytics_tracker()

    # Display analytics settings
    with st.expander("Analytics Settings", expanded=False):
        analytics_enabled = st.checkbox(
            "Enable Analytics Tracking", 
            value=st.session_state.get("analytics_enabled", True),
            key="analytics_enabled_checkbox"
        )

        if analytics_enabled != st.session_state.get("analytics_enabled", True):
            tracker.toggle_analytics(analytics_enabled)
            st.success(f"Analytics tracking {'enabled' if analytics_enabled else 'disabled'}")

        storage_path = st.text_input(
            "Analytics Storage Path",
            value=st.session_state.get("analytics_storage_path", ""),
            key="analytics_storage_path_input"
        )

        if storage_path != st.session_state.get("analytics_storage_path", ""):
            st.session_state["analytics_storage_path"] = storage_path
            st.success(f"Analytics storage path updated to: {storage_path}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Data (CSV)"):
                page_views_path, interactions_path = tracker.export_analytics_data(format="csv")
                st.success(f"Data exported to:\n- {page_views_path}\n- {interactions_path}")

        with col2:
            if st.button("Export Data (JSON)"):
                page_views_path, interactions_path = tracker.export_analytics_data(format="json")
                st.success(f"Data exported to:\n- {page_views_path}\n- {interactions_path}")

        if st.button("Clear Analytics Data", type="primary"):
            tracker.clear_analytics_data()
            st.success("Analytics data cleared")

    # Page Views Summary
    st.header("Page Views")
    page_views_df = tracker.get_page_views()
    page_views_summary = tracker.get_page_view_summary()

    if page_views_df.empty:
        st.info("No page view data available")
    else:
        st.subheader("Page View Summary")
        st.dataframe(page_views_summary)

        st.subheader("Page View Timeline")
        # Convert timestamp to datetime for better display
        timeline_df = page_views_df.copy()
        if "timestamp" in timeline_df.columns:
            timeline_df["datetime"] = pd.to_datetime(timeline_df["timestamp"], unit="s")
            timeline_df = timeline_df.sort_values("datetime")

            # Create a simple timeline chart
            st.line_chart(timeline_df.groupby(timeline_df["datetime"].dt.floor("h")).size())

        with st.expander("Raw Page View Data"):
            st.dataframe(page_views_df)

    # Interactions Summary
    st.header("User Interactions")
    interactions_df = tracker.get_interactions()
    interactions_summary = tracker.get_interaction_summary()

    if interactions_df.empty:
        st.info("No interaction data available")
    else:
        st.subheader("Interaction Summary")
        st.dataframe(interactions_summary)

        st.subheader("Interaction Types")
        if "interaction_type" in interactions_df.columns:
            interaction_counts = interactions_df["interaction_type"].value_counts()
            st.bar_chart(interaction_counts)

        with st.expander("Raw Interaction Data"):
            st.dataframe(interactions_df)

    # Session Information
    st.header("Session Information")
    session_id = st.session_state.get("analytics_session_id", "Unknown")
    session_start = st.session_state.get("analytics_session_start", 0)
    session_duration = time.time() - session_start if session_start else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Session ID", session_id[:8] + "...")
    with col2:
        st.metric("Session Duration", f"{session_duration:.1f} seconds")
