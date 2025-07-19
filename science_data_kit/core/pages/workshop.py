"""
Workshop Page Module for Science Data Kit

This module provides a workshop-specific landing page for the Science Data Kit application.
It includes an introduction to the workshop, links to tutorials and documentation,
and guides users through the workshop steps.
"""

import os
import sys
import subprocess
import datetime
import uuid
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import WorkshopPageData
from science_data_kit.data.samples.load_preclinical_dataset import main as load_preclinical_dataset


class WorkshopPage(BasePage):
    """
    Workshop page for Science Data Kit.

    This page provides:
    - An introduction to the workshop
    - Links to tutorials and documentation
    - A guide through the workshop steps
    - A way to load the preclinical research dataset
    """

    def __init__(self):
        """Initialize the workshop page."""
        super().__init__()
        self._initialize_workshop_state()

    def _initialize_workshop_state(self) -> None:
        """Initialize workshop-related state variables."""
        self.page_data = WorkshopPageData(title="Workshop")
        
        # Generate workshop ID if not already set
        if not self.page_data.workshop_id:
            self.page_data.workshop_id = f"workshop_{datetime.datetime.now().strftime('%Y%m%d')}"
        
        # Generate participant ID if not already set
        if not self.page_data.participant_id:
            self.page_data.participant_id = f"participant_{uuid.uuid4().hex[:8]}"
        
        # Initialize resources
        self._initialize_resources()

    def _initialize_resources(self) -> None:
        """Initialize workshop resources."""
        # Documentation resources
        self.page_data.resources["documentation"] = [
            {
                "title": "Science Data Kit Documentation",
                "url": "https://your-org.github.io/science_data_kit/"
            },
            {
                "title": "Neo4j Documentation",
                "url": "https://neo4j.com/docs/"
            },
            {
                "title": "Cypher Query Language Reference",
                "url": "https://neo4j.com/docs/cypher-manual/current/"
            }
        ]
        
        # Jupyter notebook tutorials
        self.page_data.resources["jupyter_tutorials"] = [
            {
                "title": "Preclinical Challenge Tutorial",
                "url": "http://localhost:8888/lab/tree/tutorials/preclinical_challenge_tutorial.ipynb",
                "description": "Analyze a preclinical cancer research dataset"
            },
            {
                "title": "Database Operations Tutorial",
                "url": "http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb",
                "description": "Learn database operations with Neo4j"
            },
            {
                "title": "Data Transformation Tutorial",
                "url": "http://localhost:8888/lab/tree/tutorials/data_transformation_tutorial.ipynb",
                "description": "Transform data between different formats"
            },
            {
                "title": "Data Visualization Tutorial",
                "url": "http://localhost:8888/lab/tree/tutorials/data_visualization_tutorial.ipynb",
                "description": "Create static and interactive visualizations"
            }
        ]
        
        # Python script tutorials
        self.page_data.resources["python_tutorials"] = [
            {
                "title": "Preclinical Challenge Tutorial",
                "url": "https://github.com/your-org/science_data_kit/blob/main/tutorials/preclinical_challenge_tutorial.py"
            },
            {
                "title": "Database Operations Tutorial",
                "url": "https://github.com/your-org/science_data_kit/blob/main/tutorials/database_operations_tutorial.py"
            },
            {
                "title": "Data Transformation Tutorial",
                "url": "https://github.com/your-org/science_data_kit/blob/main/tutorials/data_transformation_tutorial.py"
            },
            {
                "title": "Data Visualization Tutorial",
                "url": "https://github.com/your-org/science_data_kit/blob/main/tutorials/data_visualization_tutorial.py"
            }
        ]
        
        # Sample datasets
        self.page_data.resources["sample_datasets"] = [
            {
                "title": "Preclinical Research Dataset",
                "url": "https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/preclinical"
            },
            {
                "title": "Other Sample Datasets",
                "url": "https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples"
            }
        ]
        
        # Tools
        self.page_data.resources["tools"] = [
            {
                "title": "Jupyter Lab",
                "url": "http://localhost:8888/lab",
                "description": "Interactive notebooks"
            },
            {
                "title": "NeoDash",
                "url": "http://localhost:5005",
                "description": "Neo4j dashboards"
            },
            {
                "title": "Neo4j Browser",
                "url": "http://localhost:7474",
                "description": "Neo4j database browser"
            }
        ]
        
        # Initialize video tutorials, demo videos, reference cards, and interactive demos
        self._initialize_video_tutorials()
        self._initialize_demo_videos()
        self._initialize_reference_cards()
        self._initialize_interactive_demos()

    def _initialize_video_tutorials(self) -> None:
        """Initialize video tutorials."""
        self.page_data.video_tutorials = [
            {
                "title": "Getting Started with Science Data Kit",
                "url": "https://www.youtube.com/watch?v=example1",
                "thumbnail": "https://img.youtube.com/vi/example1/0.jpg",
                "duration": "10:15",
                "description": "Learn the basics of the Science Data Kit and how to get started."
            },
            {
                "title": "Neo4j Integration Tutorial",
                "url": "https://www.youtube.com/watch?v=example2",
                "thumbnail": "https://img.youtube.com/vi/example2/0.jpg",
                "duration": "15:30",
                "description": "Learn how to integrate Neo4j with the Science Data Kit."
            },
            {
                "title": "Data Visualization with Science Data Kit",
                "url": "https://www.youtube.com/watch?v=example3",
                "thumbnail": "https://img.youtube.com/vi/example3/0.jpg",
                "duration": "12:45",
                "description": "Learn how to create visualizations with the Science Data Kit."
            }
        ]

    def _initialize_demo_videos(self) -> None:
        """Initialize demo videos."""
        self.page_data.demo_videos = [
            {
                "title": "Preclinical Research Analysis Demo",
                "url": "https://www.youtube.com/watch?v=example4",
                "thumbnail": "https://img.youtube.com/vi/example4/0.jpg",
                "duration": "20:00",
                "description": "See a complete analysis of a preclinical research dataset."
            },
            {
                "title": "Knowledge Graph Creation Demo",
                "url": "https://www.youtube.com/watch?v=example5",
                "thumbnail": "https://img.youtube.com/vi/example5/0.jpg",
                "duration": "18:30",
                "description": "See how to create a knowledge graph from scratch."
            }
        ]

    def _initialize_reference_cards(self) -> None:
        """Initialize reference cards."""
        self.page_data.reference_cards = [
            {
                "title": "Cypher Quick Reference",
                "url": "https://neo4j.com/docs/cypher-refcard/current/",
                "thumbnail": "/static/images/cypher_refcard.png",
                "description": "Quick reference for Cypher query language."
            },
            {
                "title": "Science Data Kit API Reference",
                "url": "https://your-org.github.io/science_data_kit/api/",
                "thumbnail": "/static/images/sdk_api_refcard.png",
                "description": "API reference for the Science Data Kit."
            }
        ]

    def _initialize_interactive_demos(self) -> None:
        """Initialize interactive demos."""
        self.page_data.interactive_demos = [
            {
                "title": "Neo4j Graph Visualization",
                "url": "http://localhost:7474/browser/",
                "thumbnail": "/static/images/neo4j_browser_demo.png",
                "description": "Interactive Neo4j graph visualization."
            },
            {
                "title": "NeoDash Dashboard",
                "url": "http://localhost:5005/",
                "thumbnail": "/static/images/neodash_demo.png",
                "description": "Interactive NeoDash dashboard."
            }
        ]

    def get_page_data(self) -> WorkshopPageData:
        """
        Get the page data for the workshop page.
        
        Returns:
            WorkshopPageData: The page data for the workshop page.
        """
        return self.page_data

    def load_preclinical_dataset(self) -> Dict[str, Any]:
        """
        Load the preclinical research dataset.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Load the dataset
            load_preclinical_dataset()
            
            # Update page data
            self.page_data.dataset_loaded = True
            
            return {"success": True, "message": "Dataset loaded successfully!"}
        except Exception as e:
            return {"success": False, "error": f"Error loading dataset: {str(e)}"}

    def verify_installation(self) -> Dict[str, Any]:
        """
        Verify the Science Data Kit installation.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Run the verification script
            result = subprocess.run(
                [sys.executable, "-m", "science_data_kit.verify"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Update page data
                self.page_data.installation_verified = True
                
                return {
                    "success": True,
                    "message": "Installation verified successfully!",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": "Installation verification failed.",
                    "output": result.stderr
                }
        except Exception as e:
            return {"success": False, "error": f"Error verifying installation: {str(e)}"}

    def run_challenge_script(self) -> Dict[str, Any]:
        """
        Run the challenge script.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Run the challenge script
            result = subprocess.run(
                [sys.executable, "-m", "tutorials.preclinical_challenge_tutorial"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Update page data
                self.page_data.challenge_completed = True
                
                return {
                    "success": True,
                    "message": "Challenge script completed successfully!",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": "Challenge script failed.",
                    "output": result.stderr
                }
        except Exception as e:
            return {"success": False, "error": f"Error running challenge script: {str(e)}"}

    def verify_checkpoint(self, checkpoint_num: int = 0) -> Dict[str, Any]:
        """
        Verify a checkpoint in the challenge.
        
        Args:
            checkpoint_num: The checkpoint number to verify (0 for all checkpoints).
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Build the command
            cmd = [sys.executable, "-m", "tutorials.checkpoint_verification"]
            if checkpoint_num > 0:
                cmd.append(str(checkpoint_num))
            
            # Run the verification script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if "ALL CHECKPOINTS PASSED" in result.stdout:
                # Update page data
                self.page_data.checkpoints_passed = [1, 2, 3, 4, 5]
                
                return {
                    "success": True,
                    "message": "All checkpoints passed!",
                    "output": result.stdout
                }
            elif "PASSED" in result.stdout:
                # Update page data
                if checkpoint_num > 0 and checkpoint_num not in self.page_data.checkpoints_passed:
                    self.page_data.checkpoints_passed.append(checkpoint_num)
                
                return {
                    "success": True,
                    "message": f"Checkpoint {checkpoint_num} passed!",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "warning": "Some checkpoints failed. Keep working on the challenge!",
                    "output": result.stdout
                }
        except Exception as e:
            return {"success": False, "error": f"Error verifying checkpoint: {str(e)}"}

    def submit_help_request(self, name: str, email: str, issue: str) -> Dict[str, Any]:
        """
        Submit a help request.
        
        Args:
            name: The name of the person requesting help.
            email: The email of the person requesting help.
            issue: The issue description.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Create the help request
            help_request = {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "issue": issue,
                "timestamp": datetime.datetime.now().isoformat(),
                "workshop_id": self.page_data.workshop_id,
                "participant_id": self.page_data.participant_id,
                "status": "pending"
            }
            
            # Add the help request to the list
            self.page_data.help_requests.append(help_request)
            
            return {
                "success": True,
                "message": "Your request has been submitted. An instructor will assist you shortly.",
                "help_request": help_request
            }
        except Exception as e:
            return {"success": False, "error": f"Error submitting help request: {str(e)}"}

    def submit_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit workshop feedback.
        
        Args:
            feedback_data: The feedback data.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Add workshop and participant IDs to the feedback data
            feedback_data["workshop_id"] = self.page_data.workshop_id
            feedback_data["participant_id"] = self.page_data.participant_id
            feedback_data["timestamp"] = datetime.datetime.now().isoformat()
            
            # Update page data
            self.page_data.feedback_submitted = True
            
            # In a real implementation, this would save the feedback to a database
            # For now, we'll just return success
            
            return {
                "success": True,
                "message": "Thank you for your feedback!",
                "feedback_data": feedback_data
            }
        except Exception as e:
            return {"success": False, "error": f"Error submitting feedback: {str(e)}"}