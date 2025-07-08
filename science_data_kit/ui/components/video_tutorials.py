"""
Video Tutorials Component for Science Data Kit

This module provides functionality for displaying video tutorials in the Science Data Kit application.
It includes classes and functions for:
- Loading video tutorial metadata
- Displaying video tutorials
- Providing information about available tutorials
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class VideoTutorials:
    """
    Video tutorials class for Science Data Kit.
    
    This class provides methods for loading and displaying video tutorials.
    """
    
    def __init__(self):
        """Initialize the video tutorials component."""
        self.tutorials = self._load_tutorials()
    
    def _load_tutorials(self) -> List[Dict[str, Any]]:
        """
        Load video tutorial metadata from JSON files.
        
        Returns:
            A list of dictionaries containing tutorial metadata.
        """
        tutorials = []
        
        # Path to the metadata directory
        metadata_dir = Path(__file__).parent.parent.parent.parent / "tutorials" / "videos" / "metadata"
        
        # Check if the directory exists
        if not metadata_dir.exists():
            st.warning(f"Video tutorial metadata directory not found: {metadata_dir}")
            return tutorials
        
        # Load metadata files
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    
                    # Add the filename (without extension) as the tutorial_id
                    metadata["tutorial_id"] = metadata_file.stem.replace("_metadata", "")
                    
                    tutorials.append(metadata)
            except Exception as e:
                st.warning(f"Error loading tutorial metadata from {metadata_file}: {e}")
        
        # Sort tutorials by order if available, otherwise by title
        tutorials.sort(key=lambda x: x.get("order", 999) if "order" in x else x.get("title", ""))
        
        return tutorials
    
    def get_all_tutorials(self) -> List[Dict[str, Any]]:
        """
        Get all available video tutorials.
        
        Returns:
            A list of dictionaries containing tutorial metadata.
        """
        return self.tutorials
    
    def get_tutorial_by_id(self, tutorial_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tutorial by ID.
        
        Args:
            tutorial_id: The ID of the tutorial to retrieve.
            
        Returns:
            A dictionary containing the tutorial metadata, or None if not found.
        """
        for tutorial in self.tutorials:
            if tutorial.get("tutorial_id") == tutorial_id:
                return tutorial
        return None
    
    def get_tutorials_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tutorials by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A list of dictionaries containing tutorial metadata for the specified category.
        """
        return [tutorial for tutorial in self.tutorials if category in tutorial.get("categories", [])]

# Create a singleton instance of the video tutorials
_video_tutorials = None

def get_video_tutorials() -> VideoTutorials:
    """
    Get the singleton instance of the video tutorials.
    
    Returns:
        The VideoTutorials instance.
    """
    global _video_tutorials
    if _video_tutorials is None:
        _video_tutorials = VideoTutorials()
    return _video_tutorials

def display_video_tutorial(tutorial_id: str) -> None:
    """
    Display a specific video tutorial.
    
    Args:
        tutorial_id: The ID of the tutorial to display.
    """
    tutorials = get_video_tutorials()
    tutorial = tutorials.get_tutorial_by_id(tutorial_id)
    
    if not tutorial:
        st.warning(f"Tutorial not found: {tutorial_id}")
        return
    
    st.header(tutorial.get("title", "Untitled Tutorial"))
    
    # Display tutorial description
    st.markdown(tutorial.get("description", "No description available."))
    
    # Display tutorial video (placeholder for now)
    st.info("Video recording in progress. Check back soon for the completed tutorial.")
    
    # Display tutorial timestamps if available
    if "timestamps" in tutorial and tutorial["timestamps"]:
        st.subheader("Tutorial Sections")
        for timestamp in tutorial["timestamps"]:
            st.markdown(f"**{timestamp['time']}** - {timestamp['description']}")
    
    # Display tutorial resources if available
    if "resources" in tutorial and tutorial["resources"]:
        st.subheader("Additional Resources")
        for resource in tutorial["resources"]:
            st.markdown(f"- [{resource['title']}]({resource['url']})")

def display_video_tutorials_section() -> None:
    """
    Display the video tutorials section on the workshop page.
    
    This function creates a Streamlit UI for browsing and viewing video tutorials.
    """
    st.header("Video Tutorials")
    
    tutorials = get_video_tutorials()
    all_tutorials = tutorials.get_all_tutorials()
    
    if not all_tutorials:
        st.info("No video tutorials available yet. Check back soon!")
        return
    
    st.markdown("""
    These video tutorials provide visual demonstrations of key features and workflows in the Science Data Kit.
    Select a tutorial from the list below to learn more.
    """)
    
    # Create a selectbox for choosing a tutorial
    tutorial_options = [tutorial.get("title", "Untitled Tutorial") for tutorial in all_tutorials]
    selected_tutorial_title = st.selectbox("Select a Tutorial", tutorial_options)
    
    # Find the selected tutorial
    selected_tutorial = next((tutorial for tutorial in all_tutorials 
                             if tutorial.get("title") == selected_tutorial_title), None)
    
    if selected_tutorial:
        # Display the selected tutorial
        display_video_tutorial(selected_tutorial.get("tutorial_id"))