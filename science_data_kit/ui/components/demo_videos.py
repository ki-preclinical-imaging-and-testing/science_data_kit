"""
Demo Videos Component for Science Data Kit

This module provides functionality for displaying demo videos in the Science Data Kit application.
It includes classes and functions for:
- Loading demo video metadata
- Displaying demo videos
- Providing information about available demos
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class DemoVideos:
    """
    Demo videos class for Science Data Kit.
    
    This class provides methods for loading and displaying demo videos.
    """
    
    def __init__(self):
        """Initialize the demo videos component."""
        self.demos = self._load_demos()
    
    def _load_demos(self) -> List[Dict[str, Any]]:
        """
        Load demo video metadata from JSON files.
        
        Returns:
            A list of dictionaries containing demo metadata.
        """
        demos = []
        
        # Path to the metadata directory
        metadata_dir = Path(__file__).parent.parent.parent.parent / "demos" / "videos" / "metadata"
        
        # Check if the directory exists
        if not metadata_dir.exists():
            # Create the directory structure if it doesn't exist
            metadata_dir.parent.mkdir(parents=True, exist_ok=True)
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a README file
            readme_path = metadata_dir.parent / "README.md"
            with open(readme_path, "w") as f:
                f.write("""# Science Data Kit Demo Videos

This directory contains scripts, metadata, and resources for the Science Data Kit demo videos. These demos provide visual demonstrations of key features and workflows in the Science Data Kit.

## Directory Structure

- `scripts/`: Contains the scripts used for recording the demo videos
- `metadata/`: Contains metadata files for each demo video, including descriptions, timestamps, and keywords
- `resources/`: Contains additional resources used in the demo videos, such as sample data files or images

## Available Demo Videos

1. **Clinical Trial Analysis Demo**: Demonstrates analysis of clinical trial data using the Science Data Kit
2. **Genomics Data Exploration Demo**: Shows exploration of genomics data using the Science Data Kit
3. **Dashboard Creation Demo**: Illustrates how to create interactive dashboards with the Science Data Kit
4. **Data Integration Demo**: Demonstrates integration of multiple data sources using the Science Data Kit

## Recording Guidelines

When recording demo videos, please follow these guidelines:

1. Use a screen resolution of 1920x1080 for recording
2. Speak clearly and at a moderate pace
3. Follow the script but feel free to add additional explanations where helpful
4. Keep videos between 3-10 minutes in length
5. Include captions for accessibility
6. Begin with an introduction and end with a summary
7. Include on-screen annotations to highlight important elements

## Usage

The demo videos are intended to showcase the capabilities of the Science Data Kit to potential users and workshop participants. They provide a visual demonstration of key features and workflows, making it easier for users to understand what the Science Data Kit can do.

Links to the demo videos are provided on the workshop page and in the documentation.
""")
            
            # Create the scripts directory
            scripts_dir = metadata_dir.parent / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the resources directory
            resources_dir = metadata_dir.parent / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            # Create sample metadata files
            demo_metadata = [
                {
                    "title": "Clinical Trial Analysis Demo",
                    "description": "This demo shows how to analyze clinical trial data using the Science Data Kit. It covers data loading, exploration, statistical analysis, and visualization of results.",
                    "duration": "8:30",
                    "categories": ["clinical", "analysis", "visualization"],
                    "order": 1,
                    "timestamps": [
                        {"time": "0:00", "description": "Introduction"},
                        {"time": "1:15", "description": "Loading clinical trial data"},
                        {"time": "3:00", "description": "Exploring patient demographics"},
                        {"time": "4:45", "description": "Analyzing treatment outcomes"},
                        {"time": "6:30", "description": "Visualizing results"},
                        {"time": "8:00", "description": "Summary and conclusion"}
                    ],
                    "resources": [
                        {"title": "Clinical Trial Dataset", "url": "https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/clinical_trial"},
                        {"title": "Clinical Trial Analysis Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/clinical_trial_analysis_tutorial.ipynb"}
                    ],
                    "status": "In preparation"
                },
                {
                    "title": "Genomics Data Exploration Demo",
                    "description": "This demo illustrates how to explore genomics data using the Science Data Kit. It covers data import, quality control, exploratory analysis, and visualization of genomic features.",
                    "duration": "7:15",
                    "categories": ["genomics", "exploration", "visualization"],
                    "order": 2,
                    "timestamps": [
                        {"time": "0:00", "description": "Introduction"},
                        {"time": "1:00", "description": "Importing genomics data"},
                        {"time": "2:30", "description": "Quality control and preprocessing"},
                        {"time": "4:00", "description": "Exploratory analysis"},
                        {"time": "5:30", "description": "Visualizing genomic features"},
                        {"time": "7:00", "description": "Summary and conclusion"}
                    ],
                    "resources": [
                        {"title": "Genomics Dataset", "url": "https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/genomics"},
                        {"title": "Genomics Analysis Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/genomics_analysis_tutorial.ipynb"}
                    ],
                    "status": "In preparation"
                },
                {
                    "title": "Dashboard Creation Demo",
                    "description": "This demo shows how to create interactive dashboards using the Science Data Kit. It covers dashboard design, component selection, data binding, and sharing options.",
                    "duration": "6:45",
                    "categories": ["dashboard", "visualization", "interactive"],
                    "order": 3,
                    "timestamps": [
                        {"time": "0:00", "description": "Introduction"},
                        {"time": "0:45", "description": "Dashboard design principles"},
                        {"time": "2:00", "description": "Adding visualization components"},
                        {"time": "3:30", "description": "Binding data to components"},
                        {"time": "5:00", "description": "Adding interactivity"},
                        {"time": "6:15", "description": "Sharing and exporting dashboards"}
                    ],
                    "resources": [
                        {"title": "NeoDash Documentation", "url": "http://localhost:5005/docs"},
                        {"title": "Dashboard Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/dashboard_tutorial.ipynb"}
                    ],
                    "status": "In preparation"
                },
                {
                    "title": "Data Integration Demo",
                    "description": "This demo illustrates how to integrate multiple data sources using the Science Data Kit. It covers connecting to different databases, merging datasets, and creating unified views.",
                    "duration": "9:00",
                    "categories": ["integration", "database", "connectivity"],
                    "order": 4,
                    "timestamps": [
                        {"time": "0:00", "description": "Introduction"},
                        {"time": "1:30", "description": "Connecting to Neo4j database"},
                        {"time": "3:00", "description": "Connecting to SQL database"},
                        {"time": "4:30", "description": "Importing data from APIs"},
                        {"time": "6:00", "description": "Merging datasets"},
                        {"time": "7:30", "description": "Creating unified views"},
                        {"time": "8:30", "description": "Summary and conclusion"}
                    ],
                    "resources": [
                        {"title": "Database Operations Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb"},
                        {"title": "API Integration Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/api_integration_tutorial.ipynb"}
                    ],
                    "status": "In preparation"
                }
            ]
            
            for i, demo in enumerate(demo_metadata):
                demo_id = demo["title"].lower().replace(" ", "_")
                metadata_path = metadata_dir / f"{demo_id}_metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(demo, f, indent=2)
                
                # Create a sample script file
                script_path = scripts_dir / f"{demo_id}_script.md"
                with open(script_path, "w") as f:
                    f.write(f"""# {demo['title']} Script

## Overview

{demo['description']}

## Script

### Introduction (0:00 - 1:00)

Hello and welcome to this demonstration of the Science Data Kit. In this video, we'll show you how to {demo['title'].lower().replace('demo', '')}.

### Main Content

{' '.join([f"#### {timestamp['description']} ({timestamp['time']})" for timestamp in demo['timestamps'][1:-1]])}

### Conclusion ({demo['timestamps'][-1]['time']})

That concludes our demonstration of {demo['title'].lower().replace('demo', '')} using the Science Data Kit. We've shown you how to [summary of key points].

Thank you for watching!
""")
            
            # Return the sample metadata
            for demo in demo_metadata:
                demo["demo_id"] = demo["title"].lower().replace(" ", "_")
                demos.append(demo)
            
            return demos
        
        # Load metadata files
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    
                    # Add the filename (without extension) as the demo_id
                    metadata["demo_id"] = metadata_file.stem.replace("_metadata", "")
                    
                    demos.append(metadata)
            except Exception as e:
                st.warning(f"Error loading demo metadata from {metadata_file}: {e}")
        
        # Sort demos by order if available, otherwise by title
        demos.sort(key=lambda x: x.get("order", 999) if "order" in x else x.get("title", ""))
        
        return demos
    
    def get_all_demos(self) -> List[Dict[str, Any]]:
        """
        Get all available demo videos.
        
        Returns:
            A list of dictionaries containing demo metadata.
        """
        return self.demos
    
    def get_demo_by_id(self, demo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific demo by ID.
        
        Args:
            demo_id: The ID of the demo to retrieve.
            
        Returns:
            A dictionary containing the demo metadata, or None if not found.
        """
        for demo in self.demos:
            if demo.get("demo_id") == demo_id:
                return demo
        return None
    
    def get_demos_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get demos by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A list of dictionaries containing demo metadata for the specified category.
        """
        return [demo for demo in self.demos if category in demo.get("categories", [])]

# Create a singleton instance of the demo videos
_demo_videos = None

def get_demo_videos() -> DemoVideos:
    """
    Get the singleton instance of the demo videos.
    
    Returns:
        The DemoVideos instance.
    """
    global _demo_videos
    if _demo_videos is None:
        _demo_videos = DemoVideos()
    return _demo_videos

def display_demo_video(demo_id: str) -> None:
    """
    Display a specific demo video.
    
    Args:
        demo_id: The ID of the demo to display.
    """
    demos = get_demo_videos()
    demo = demos.get_demo_by_id(demo_id)
    
    if not demo:
        st.warning(f"Demo not found: {demo_id}")
        return
    
    st.header(demo.get("title", "Untitled Demo"))
    
    # Display demo description
    st.markdown(demo.get("description", "No description available."))
    
    # Display demo status
    status = demo.get("status", "In preparation")
    if status == "In preparation":
        st.info("This demo video is currently in preparation. Check back soon for the completed demo.")
    elif status == "Available":
        # In a real implementation, this would embed the video
        st.video("https://example.com/path/to/video.mp4")
    else:
        st.warning(f"Demo status: {status}")
    
    # Display demo timestamps if available
    if "timestamps" in demo and demo["timestamps"]:
        st.subheader("Demo Sections")
        for timestamp in demo["timestamps"]:
            st.markdown(f"**{timestamp['time']}** - {timestamp['description']}")
    
    # Display demo resources if available
    if "resources" in demo and demo["resources"]:
        st.subheader("Additional Resources")
        for resource in demo["resources"]:
            st.markdown(f"- [{resource['title']}]({resource['url']})")

def display_demo_videos_section() -> None:
    """
    Display the demo videos section on the workshop page.
    
    This function creates a Streamlit UI for browsing and viewing demo videos.
    """
    st.header("Demo Videos")
    
    demos = get_demo_videos()
    all_demos = demos.get_all_demos()
    
    if not all_demos:
        st.info("No demo videos available yet. Check back soon!")
        return
    
    st.markdown("""
    These demo videos showcase the capabilities of the Science Data Kit through practical examples.
    Select a demo from the list below to learn more.
    """)
    
    # Create a selectbox for choosing a demo
    demo_options = [demo.get("title", "Untitled Demo") for demo in all_demos]
    selected_demo_title = st.selectbox("Select a Demo", demo_options, key="demo_selectbox")
    
    # Find the selected demo
    selected_demo = next((demo for demo in all_demos 
                         if demo.get("title") == selected_demo_title), None)
    
    if selected_demo:
        # Display the selected demo
        display_demo_video(selected_demo.get("demo_id"))