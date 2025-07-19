"""
Observation Page Module for Science Data Kit

This module provides an observation page for workshop instructors to record
and analyze participant interactions with the Science Data Kit application.
It uses the observation protocol to manage observation sessions, record
observations, and view observation data.
"""

import time
import datetime
import uuid
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import ObservationPageData


class ObservationPage(BasePage):
    """
    Observation page for Science Data Kit.

    This page provides:
    - A dashboard for managing observation sessions
    - Tools for recording observations
    - Views for analyzing observation data
    - Export functionality for observation data
    """

    def __init__(self):
        """Initialize the observation page."""
        super().__init__()
        self._initialize_observation_state()

    def _initialize_observation_state(self) -> None:
        """Initialize observation-related state variables."""
        self.page_data = ObservationPageData()
        self.page_data.observation_protocol_template = self._get_default_protocol_template()
        
        # Default to a directory in the user's home directory
        default_path = Path.home() / ".science_data_kit" / "observations"
        self.page_data.observation_storage_path = str(default_path)
        
        # Create storage directory if it doesn't exist
        storage_path = Path(self.page_data.observation_storage_path)
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

    def get_page_data(self) -> ObservationPageData:
        """
        Get the page data for the observation page.
        
        Returns:
            ObservationPageData: The page data for the observation page.
        """
        return self.page_data

    def start_observation_session(self, participant_id: str, observer_name: str) -> Dict[str, Any]:
        """
        Start an observation session.
        
        Args:
            participant_id: Identifier for the participant being observed.
            observer_name: Name of the person conducting the observation.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            self.page_data.observation_enabled = True
            self.page_data.observation_start_time = time.time()
            self.page_data.observation_session_id = str(uuid.uuid4())
            self.page_data.participant_id = participant_id
            self.page_data.observer_name = observer_name
            
            # Log the start of the session
            self._log_observation_event("session_start", {
                "participant_id": participant_id,
                "observer_name": observer_name,
                "timestamp": time.time()
            })
            
            return {"success": True, "message": "Observation session started", "session_id": self.page_data.observation_session_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def end_observation_session(self) -> Dict[str, Any]:
        """
        End the current observation session.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            if not self.page_data.observation_enabled:
                return {"success": False, "error": "No active observation session"}
            
            self.page_data.observation_enabled = False
            self.page_data.observation_end_time = time.time()
            
            # Log the end of the session
            self._log_observation_event("session_end", {
                "participant_id": self.page_data.participant_id,
                "observer_name": self.page_data.observer_name,
                "duration": self.page_data.observation_end_time - self.page_data.observation_start_time,
                "timestamp": time.time()
            })
            
            # Save the observation data
            self._save_observation_data()
            
            return {"success": True, "message": "Observation session ended"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def record_observation(self, section: str, observation_point: str, notes: str, rating: Optional[int] = None) -> Dict[str, Any]:
        """
        Record an observation.
        
        Args:
            section: The section of the observation protocol.
            observation_point: The specific observation point.
            notes: Notes about the observation.
            rating: Optional rating (1-5) for the observation.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            if not self.page_data.observation_enabled:
                return {"success": False, "error": "No active observation session"}
            
            # Create the observation record
            observation = {
                "id": str(uuid.uuid4()),
                "session_id": self.page_data.observation_session_id,
                "participant_id": self.page_data.participant_id,
                "observer_name": self.page_data.observer_name,
                "section": section,
                "observation_point": observation_point,
                "notes": notes,
                "rating": rating,
                "timestamp": time.time(),
                "datetime": datetime.datetime.now().isoformat()
            }
            
            # Add the observation to the list
            self.page_data.observations.append(observation)
            
            # Log the observation event
            self._log_observation_event("observation_recorded", {
                "observation_id": observation["id"],
                "section": section,
                "observation_point": observation_point,
                "timestamp": time.time()
            })
            
            return {"success": True, "message": "Observation recorded", "observation": observation}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _log_observation_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an observation event.
        
        Args:
            event_type: Type of event (e.g., session_start, observation_recorded).
            details: Details about the event.
        """
        event = {
            "id": str(uuid.uuid4()),
            "session_id": self.page_data.observation_session_id,
            "event_type": event_type,
            "details": details,
            "timestamp": time.time(),
            "datetime": datetime.datetime.now().isoformat()
        }
        
        self.page_data.observation_events.append(event)

    def get_observations(self) -> List[Dict[str, Any]]:
        """
        Get all recorded observations.
        
        Returns:
            List[Dict[str, Any]]: List of observation records.
        """
        return self.page_data.observations

    def get_observation_events(self) -> List[Dict[str, Any]]:
        """
        Get all observation events.
        
        Returns:
            List[Dict[str, Any]]: List of observation event records.
        """
        return self.page_data.observation_events

    def get_observation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the observation data.
        
        Returns:
            Dict[str, Any]: Summary of observation data.
        """
        if not self.page_data.observations:
            return {"sections": {}, "ratings": {}, "total_observations": 0}
        
        # Count observations by section
        section_counts = {}
        for obs in self.page_data.observations:
            section = obs["section"]
            if section not in section_counts:
                section_counts[section] = 0
            section_counts[section] += 1
        
        # Calculate average ratings by section
        section_ratings = {}
        for obs in self.page_data.observations:
            if obs["rating"] is not None:
                section = obs["section"]
                if section not in section_ratings:
                    section_ratings[section] = {"sum": 0, "count": 0}
                section_ratings[section]["sum"] += obs["rating"]
                section_ratings[section]["count"] += 1
        
        # Calculate averages
        section_avg_ratings = {}
        for section, data in section_ratings.items():
            if data["count"] > 0:
                section_avg_ratings[section] = data["sum"] / data["count"]
        
        summary = {
            "sections": section_counts,
            "ratings": section_avg_ratings,
            "total_observations": len(self.page_data.observations)
        }
        
        self.page_data.observation_summary = summary
        return summary

    def export_observation_data(self, format: str = "csv", path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export observation data to a file.
        
        Args:
            format: Export format (csv or json).
            path: Path to save the file. If None, uses the default storage path.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            if not self.page_data.observations:
                return {"success": False, "error": "No observations to export"}
            
            # Create a DataFrame from the observations
            df = pd.DataFrame(self.page_data.observations)
            
            # Determine the file path
            if path is None:
                storage_path = Path(self.page_data.observation_storage_path)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"observations_{timestamp}.{format}"
                file_path = storage_path / filename
            else:
                file_path = Path(path)
            
            # Create the directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export the data
            if format.lower() == "csv":
                df.to_csv(file_path, index=False)
            elif format.lower() == "json":
                df.to_json(file_path, orient="records", indent=2)
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            return {"success": True, "message": f"Observation data exported to {file_path}", "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_observation_data(self) -> None:
        """Save observation data to the storage path."""
        try:
            storage_path = Path(self.page_data.observation_storage_path)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"observations_{self.page_data.observation_session_id}_{timestamp}.json"
            file_path = storage_path / filename
            
            data = {
                "session_id": self.page_data.observation_session_id,
                "participant_id": self.page_data.participant_id,
                "observer_name": self.page_data.observer_name,
                "start_time": self.page_data.observation_start_time,
                "end_time": self.page_data.observation_end_time,
                "observations": self.page_data.observations,
                "events": self.page_data.observation_events
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving observation data: {e}")

    def clear_observation_data(self) -> Dict[str, Any]:
        """
        Clear all observation data.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            self.page_data.observations = []
            self.page_data.observation_events = []
            self.page_data.observation_summary = None
            return {"success": True, "message": "Observation data cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_observation(self, enabled: bool) -> Dict[str, Any]:
        """
        Toggle observation mode.
        
        Args:
            enabled: Whether to enable or disable observation mode.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            self.page_data.observation_enabled = enabled
            return {"success": True, "message": f"Observation mode {'enabled' if enabled else 'disabled'}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_observation_storage_path(self, path: str) -> Dict[str, Any]:
        """
        Update the observation storage path.
        
        Args:
            path: New storage path.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Validate the path
            storage_path = Path(path)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
            
            self.page_data.observation_storage_path = str(storage_path)
            return {"success": True, "message": f"Observation storage path updated to {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}