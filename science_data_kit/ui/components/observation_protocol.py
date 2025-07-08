"""
Observation Protocol Module for Science Data Kit

This module provides functionality for structured observation of workshop participants
and collection of data about their interactions with the Science Data Kit application.
It includes classes and functions for:
- Defining observation protocols
- Recording observations
- Analyzing observation data
- Generating observation reports
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

class ObservationProtocol:
    """
    Observation protocol class for Science Data Kit.
    
    This class provides methods for defining structured observation protocols,
    recording observations, and analyzing observation data.
    """
    
    def __init__(self):
        """Initialize the observation protocol and set up session state."""
        self._initialize_observation_state()
    
    def _initialize_observation_state(self) -> None:
        """Initialize observation-related session state variables."""
        if "observation_enabled" not in st.session_state:
            st.session_state["observation_enabled"] = False
            
        if "observation_session_id" not in st.session_state:
            st.session_state["observation_session_id"] = str(uuid.uuid4())
            
        if "observation_start_time" not in st.session_state:
            st.session_state["observation_start_time"] = None
            
        if "observation_end_time" not in st.session_state:
            st.session_state["observation_end_time"] = None
            
        if "observations" not in st.session_state:
            st.session_state["observations"] = []
            
        if "observation_protocol_template" not in st.session_state:
            st.session_state["observation_protocol_template"] = self._get_default_protocol_template()
            
        if "observation_storage_path" not in st.session_state:
            # Default to a directory in the user's home directory
            default_path = Path.home() / ".science_data_kit" / "observations"
            st.session_state["observation_storage_path"] = str(default_path)
            
        # Create storage directory if it doesn't exist
        storage_path = Path(st.session_state["observation_storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_default_protocol_template(self) -> Dict[str, Any]:
        """
        Get the default observation protocol template.
        
        Returns:
            A dictionary containing the default observation protocol template.
        """
        return {
            "sections": [
                {
                    "name": "Initial Setup",
                    "description": "Observe how participants set up and configure the Science Data Kit.",
                    "observation_points": [
                        "Time taken to load the preclinical research dataset",
                        "Difficulty level in verifying installation",
                        "Questions asked during setup",
                        "Navigation patterns during initial exploration"
                    ]
                },
                {
                    "name": "Data Exploration",
                    "description": "Observe how participants explore and understand the dataset.",
                    "observation_points": [
                        "Approach to exploring the dataset structure",
                        "Use of visualization tools",
                        "Questions asked about data meaning",
                        "Time spent on data exploration"
                    ]
                },
                {
                    "name": "Analysis Workflow",
                    "description": "Observe how participants perform analysis tasks.",
                    "observation_points": [
                        "Approach to analysis tasks",
                        "Tools and features used",
                        "Efficiency of workflow",
                        "Challenges encountered"
                    ]
                },
                {
                    "name": "Visualization",
                    "description": "Observe how participants create and interpret visualizations.",
                    "observation_points": [
                        "Types of visualizations created",
                        "Customization of visualizations",
                        "Interpretation of visualization results",
                        "Sharing and exporting visualizations"
                    ]
                },
                {
                    "name": "Help-Seeking Behavior",
                    "description": "Observe how participants seek help when needed.",
                    "observation_points": [
                        "Use of documentation",
                        "Questions asked to instructors",
                        "Use of help features",
                        "Collaboration with other participants"
                    ]
                }
            ],
            "rating_scale": [
                {"value": 1, "label": "Significant difficulty"},
                {"value": 2, "label": "Some difficulty"},
                {"value": 3, "label": "Neutral"},
                {"value": 4, "label": "Somewhat easy"},
                {"value": 5, "label": "Very easy"}
            ],
            "general_notes_template": "General observations about participant interaction with the Science Data Kit:"
        }
    
    def start_observation_session(self, participant_id: str, observer_name: str) -> None:
        """
        Start an observation session.
        
        Args:
            participant_id: Identifier for the participant being observed.
            observer_name: Name of the person conducting the observation.
        """
        st.session_state["observation_enabled"] = True
        st.session_state["observation_start_time"] = time.time()
        st.session_state["observation_session_id"] = str(uuid.uuid4())
        st.session_state["observation_participant_id"] = participant_id
        st.session_state["observation_observer_name"] = observer_name
        
        # Log the start of the observation session
        self._log_observation_event("session_start", {
            "participant_id": participant_id,
            "observer_name": observer_name
        })
    
    def end_observation_session(self) -> None:
        """End the current observation session."""
        if not st.session_state.get("observation_enabled", False):
            return
            
        st.session_state["observation_enabled"] = False
        st.session_state["observation_end_time"] = time.time()
        
        # Log the end of the observation session
        self._log_observation_event("session_end", {
            "session_duration": st.session_state["observation_end_time"] - st.session_state["observation_start_time"]
        })
        
        # Save the observation data
        self._save_observation_data()
    
    def record_observation(self, 
                          section: str, 
                          observation_point: str, 
                          notes: str, 
                          rating: Optional[int] = None) -> None:
        """
        Record an observation.
        
        Args:
            section: The section of the observation protocol.
            observation_point: The specific point being observed.
            notes: Notes about the observation.
            rating: Optional rating on the defined scale.
        """
        if not st.session_state.get("observation_enabled", False):
            return
            
        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()
        
        observation = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": st.session_state["observation_session_id"],
            "participant_id": st.session_state.get("observation_participant_id", "unknown"),
            "observer_name": st.session_state.get("observation_observer_name", "unknown"),
            "section": section,
            "observation_point": observation_point,
            "notes": notes,
            "rating": rating
        }
        
        st.session_state["observations"].append(observation)
        self._save_observation_data()
    
    def _log_observation_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an observation event.
        
        Args:
            event_type: The type of event (session_start, session_end, etc.).
            details: Details about the event.
        """
        timestamp = time.time()
        formatted_time = datetime.datetime.fromtimestamp(timestamp).isoformat()
        
        event = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "session_id": st.session_state.get("observation_session_id", str(uuid.uuid4())),
            "event_type": event_type,
            "details": details
        }
        
        if "observation_events" not in st.session_state:
            st.session_state["observation_events"] = []
            
        st.session_state["observation_events"].append(event)
    
    def get_observations(self) -> pd.DataFrame:
        """
        Get all recorded observations as a DataFrame.
        
        Returns:
            A pandas DataFrame containing all observation data.
        """
        if not st.session_state.get("observations"):
            return pd.DataFrame()
            
        return pd.DataFrame(st.session_state["observations"])
    
    def get_observation_events(self) -> pd.DataFrame:
        """
        Get all observation events as a DataFrame.
        
        Returns:
            A pandas DataFrame containing all observation event data.
        """
        if not st.session_state.get("observation_events"):
            return pd.DataFrame()
            
        return pd.DataFrame(st.session_state["observation_events"])
    
    def get_observation_summary(self) -> pd.DataFrame:
        """
        Get a summary of observations by section.
        
        Returns:
            A pandas DataFrame with observation statistics by section.
        """
        observations_df = self.get_observations()
        if observations_df.empty:
            return pd.DataFrame()
            
        # Group by section and calculate statistics
        if "rating" in observations_df.columns:
            summary = observations_df.groupby("section").agg({
                "observation_point": "count",
                "rating": ["mean", "min", "max"]
            })
            
            summary.columns = ["observation_count", "avg_rating", "min_rating", "max_rating"]
            return summary.reset_index()
        else:
            summary = observations_df.groupby("section").agg({
                "observation_point": "count"
            })
            
            summary.columns = ["observation_count"]
            return summary.reset_index()
    
    def export_observation_data(self, 
                              format: str = "csv", 
                              path: Optional[str] = None) -> Tuple[str, str]:
        """
        Export observation data to CSV or JSON.
        
        Args:
            format: The export format ("csv" or "json").
            path: Optional path to save the files. If None, uses the default storage path.
            
        Returns:
            A tuple of (observations_path, events_path) with the paths to the exported files.
        """
        storage_path = Path(path or st.session_state["observation_storage_path"])
        storage_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        observations_df = self.get_observations()
        events_df = self.get_observation_events()
        
        if format.lower() == "csv":
            observations_path = storage_path / f"observations_{timestamp}.csv"
            events_path = storage_path / f"observation_events_{timestamp}.csv"
            
            if not observations_df.empty:
                observations_df.to_csv(observations_path, index=False)
            
            if not events_df.empty:
                events_df.to_csv(events_path, index=False)
                
        elif format.lower() == "json":
            observations_path = storage_path / f"observations_{timestamp}.json"
            events_path = storage_path / f"observation_events_{timestamp}.json"
            
            if not observations_df.empty:
                observations_df.to_json(observations_path, orient="records")
            
            if not events_df.empty:
                events_df.to_json(events_path, orient="records")
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        return str(observations_path), str(events_path)
    
    def _save_observation_data(self) -> None:
        """
        Save observation data to disk.
        This is called automatically after recording observations.
        """
        # Save data every 5 observations to avoid excessive disk I/O
        if len(st.session_state.get("observations", [])) % 5 == 0:
            self.export_observation_data()
    
    def clear_observation_data(self) -> None:
        """Clear all observation data from session state."""
        st.session_state["observations"] = []
        st.session_state["observation_events"] = []
        
    def toggle_observation(self, enabled: bool) -> None:
        """
        Enable or disable observation recording.
        
        Args:
            enabled: Whether observation recording should be enabled.
        """
        st.session_state["observation_enabled"] = enabled

# Create a singleton instance of the observation protocol
_observation_protocol = None

def get_observation_protocol() -> ObservationProtocol:
    """
    Get the singleton instance of the observation protocol.
    
    Returns:
        The ObservationProtocol instance.
    """
    global _observation_protocol
    if _observation_protocol is None:
        _observation_protocol = ObservationProtocol()
    return _observation_protocol

def render_observation_dashboard():
    """
    Render an observation dashboard for workshop instructors.
    
    This function creates a Streamlit UI for managing observation sessions,
    recording observations, and viewing observation data.
    """
    st.title("Workshop Observation Dashboard")
    
    protocol = get_observation_protocol()
    
    # Session Management
    st.header("Observation Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        observation_enabled = st.session_state.get("observation_enabled", False)
        if observation_enabled:
            st.success("Observation session active")
            
            if st.button("End Observation Session"):
                protocol.end_observation_session()
                st.experimental_rerun()
        else:
            st.warning("No active observation session")
            
            with st.form("start_session_form"):
                participant_id = st.text_input("Participant ID")
                observer_name = st.text_input("Observer Name")
                start_session = st.form_submit_button("Start Observation Session")
                
                if start_session and participant_id and observer_name:
                    protocol.start_observation_session(participant_id, observer_name)
                    st.experimental_rerun()
    
    with col2:
        if observation_enabled:
            session_id = st.session_state.get("observation_session_id", "Unknown")
            start_time = st.session_state.get("observation_start_time", 0)
            current_time = time.time()
            session_duration = current_time - start_time if start_time else 0
            
            st.metric("Session ID", session_id[:8] + "...")
            st.metric("Session Duration", f"{session_duration:.1f} seconds")
            st.metric("Participant ID", st.session_state.get("observation_participant_id", "Unknown"))
            st.metric("Observer", st.session_state.get("observation_observer_name", "Unknown"))
    
    # Record Observations
    if observation_enabled:
        st.header("Record Observations")
        
        protocol_template = st.session_state.get("observation_protocol_template", {})
        sections = protocol_template.get("sections", [])
        rating_scale = protocol_template.get("rating_scale", [])
        
        with st.form("record_observation_form"):
            section = st.selectbox(
                "Section",
                options=[s["name"] for s in sections],
                key="observation_section"
            )
            
            # Get the selected section
            selected_section = next((s for s in sections if s["name"] == section), None)
            
            if selected_section:
                st.markdown(f"**Description**: {selected_section['description']}")
                
                observation_point = st.selectbox(
                    "Observation Point",
                    options=selected_section["observation_points"],
                    key="observation_point"
                )
                
                notes = st.text_area("Observation Notes")
                
                if rating_scale:
                    rating = st.select_slider(
                        "Rating",
                        options=[r["value"] for r in rating_scale],
                        format_func=lambda x: next((r["label"] for r in rating_scale if r["value"] == x), str(x)),
                        key="observation_rating"
                    )
                else:
                    rating = None
                
                submit_observation = st.form_submit_button("Record Observation")
                
                if submit_observation and section and observation_point:
                    protocol.record_observation(section, observation_point, notes, rating)
                    st.success("Observation recorded")
        
        # General Notes
        with st.form("general_notes_form"):
            st.subheader("General Notes")
            
            general_notes_template = protocol_template.get("general_notes_template", "")
            general_notes = st.text_area("Notes", value=general_notes_template)
            
            submit_notes = st.form_submit_button("Save General Notes")
            
            if submit_notes and general_notes:
                protocol.record_observation("General", "General Notes", general_notes)
                st.success("General notes saved")
    
    # Observation Data
    st.header("Observation Data")
    
    observations_df = protocol.get_observations()
    observation_summary = protocol.get_observation_summary()
    
    if observations_df.empty:
        st.info("No observation data available")
    else:
        st.subheader("Observation Summary")
        st.dataframe(observation_summary)
        
        st.subheader("Recent Observations")
        # Show the most recent observations first
        recent_observations = observations_df.sort_values("timestamp", ascending=False).head(10)
        st.dataframe(recent_observations)
        
        with st.expander("All Observations"):
            st.dataframe(observations_df)
    
    # Export and Settings
    with st.expander("Export and Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Data (CSV)"):
                observations_path, events_path = protocol.export_observation_data(format="csv")
                st.success(f"Data exported to:\n- {observations_path}\n- {events_path}")
        
        with col2:
            if st.button("Export Data (JSON)"):
                observations_path, events_path = protocol.export_observation_data(format="json")
                st.success(f"Data exported to:\n- {observations_path}\n- {events_path}")
        
        if st.button("Clear Observation Data", type="primary"):
            protocol.clear_observation_data()
            st.success("Observation data cleared")