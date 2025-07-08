"""
Workshop Page Module for Science Data Kit

This module provides a workshop-specific landing page for the Science Data Kit application.
It includes an introduction to the workshop, links to tutorials and documentation,
and guides users through the workshop steps.
"""

import streamlit as st
import os
import sys
import subprocess
import datetime
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable

from science_data_kit.ui.pages.base_page import BasePage
from science_data_kit.data.samples.load_preclinical_dataset import main as load_preclinical_dataset
from science_data_kit.ui.components.analytics_tracking import track_page_view, track_interaction
from science_data_kit.ui.components.feedback_database import collect_workshop_feedback
from science_data_kit.ui.components.instructor_notes import add_instructor_notes_to_workshop
from science_data_kit.ui.components.video_tutorials import display_video_tutorials_section
from science_data_kit.ui.components.demo_videos import display_demo_videos_section

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
        super().__init__("Workshop", "Science Data Kit Workshop")

    def render(self):
        """Render the workshop page."""
        # Track page view
        track_page_view("Workshop", "/workshop")

        # Workshop header
        st.title("🧪 Science Data Kit Workshop")
        st.markdown("""
        Welcome to the Science Data Kit Workshop! This page will guide you through the workshop
        activities and help you get started with the Science Data Kit.
        """)

        # Add instructor notes
        # Generate a workshop ID if not already in session state
        if "workshop_id" not in st.session_state:
            st.session_state["workshop_id"] = f"workshop_{datetime.datetime.now().strftime('%Y%m%d')}"

        add_instructor_notes_to_workshop(st.session_state["workshop_id"])

        # Workshop tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Getting Started", "30-Minute Challenge", "Resources", "Help", "Feedback"])

        with tab1:
            self._render_getting_started()

        with tab2:
            self._render_challenge()

        with tab3:
            self._render_resources()

        with tab4:
            self._render_help()

        with tab5:
            self._render_feedback()

    def _render_getting_started(self):
        """Render the Getting Started section."""
        st.header("Getting Started")

        st.markdown("""
        ### Welcome to the Science Data Kit Workshop!

        The Science Data Kit (SDK) is a comprehensive tool for scientific data analysis and visualization.
        It provides a unified interface for working with various data sources, including Neo4j, SQL databases,
        and RESTful APIs.

        In this workshop, you will:
        1. Learn the basics of the Science Data Kit
        2. Explore a realistic preclinical cancer research dataset
        3. Perform data analysis and visualization
        4. Answer research questions using the dataset

        ### Workshop Environment

        This workshop environment has been pre-configured with:
        - Science Data Kit installed and ready to use
        - Neo4j database running with sample data
        - Jupyter Lab for interactive analysis
        - NeoDash for creating dashboards

        ### First Steps

        1. **Load the preclinical research dataset**: Click the button below to load the dataset into Neo4j
        2. **Explore the dataset**: Use the Explore page to run queries and visualize the data
        3. **Take the 30-Minute Challenge**: Follow the guided tutorial to analyze the dataset
        """)

        # Button to load the preclinical research dataset
        if st.button("Load Preclinical Research Dataset", key="load_dataset_button"):
            # Track interaction
            track_interaction(
                interaction_type="click",
                component_id="load_dataset_button",
                component_type="button",
                page_name="Workshop",
                details={"action": "load_preclinical_dataset"}
            )

            with st.spinner("Loading dataset..."):
                try:
                    load_preclinical_dataset()
                    st.success("Dataset loaded successfully!")
                    # Track successful outcome
                    track_interaction(
                        interaction_type="success",
                        component_id="load_dataset_button",
                        component_type="button",
                        page_name="Workshop",
                        details={"outcome": "dataset_loaded_successfully"}
                    )
                except Exception as e:
                    st.error(f"Error loading dataset: {e}")
                    # Track error outcome
                    track_interaction(
                        interaction_type="error",
                        component_id="load_dataset_button",
                        component_type="button",
                        page_name="Workshop",
                        details={"error": str(e)}
                    )

        # Button to verify installation
        if st.button("Verify Installation", key="verify_installation_button"):
            # Track interaction
            track_interaction(
                interaction_type="click",
                component_id="verify_installation_button",
                component_type="button",
                page_name="Workshop",
                details={"action": "verify_installation"}
            )

            with st.spinner("Verifying installation..."):
                try:
                    # Run the verification script
                    result = subprocess.run(
                        [sys.executable, "-m", "science_data_kit.verify"],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        st.success("Installation verified successfully!")
                        st.code(result.stdout)
                        # Track successful outcome
                        track_interaction(
                            interaction_type="success",
                            component_id="verify_installation_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"outcome": "installation_verified_successfully"}
                        )
                    else:
                        st.error("Installation verification failed.")
                        st.code(result.stderr)
                        # Track error outcome
                        track_interaction(
                            interaction_type="error",
                            component_id="verify_installation_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"outcome": "installation_verification_failed", "stderr": result.stderr}
                        )
                except Exception as e:
                    st.error(f"Error verifying installation: {e}")
                    # Track exception
                    track_interaction(
                        interaction_type="error",
                        component_id="verify_installation_button",
                        component_type="button",
                        page_name="Workshop",
                        details={"error": str(e)}
                    )

    def _render_challenge(self):
        """Render the 30-Minute Challenge section."""
        st.header("30-Minute Challenge")

        st.markdown("""
        ### Preclinical Research Challenge

        The 30-Minute Preclinical Research Challenge is a guided tutorial that will help you learn
        how to use the Science Data Kit to analyze a realistic preclinical cancer research dataset.

        The challenge is structured in progressive steps, each building on the previous one:
        1. **Loading the Dataset**: Load and explore the preclinical research dataset
        2. **Analyzing Experiments**: Analyze experimental design and animal groups
        3. **Tumor Growth Analysis**: Analyze tumor volume changes over time
        4. **Survival Analysis**: Analyze survival outcomes and tumor responses
        5. **Answering Research Questions**: Identify the most effective treatment

        ### Running the Challenge

        You can run the challenge in two ways:
        1. **Jupyter Notebook**: Open the challenge notebook in Jupyter Lab
        2. **Python Script**: Run the challenge script directly

        Choose the option that works best for you:
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Jupyter Notebook")
            st.markdown("""
            Open the challenge notebook in Jupyter Lab:
            1. Click the button below to open Jupyter Lab
            2. Navigate to `tutorials/preclinical_challenge_tutorial.ipynb`
            3. Follow the instructions in the notebook
            """)

            if st.button("Open Jupyter Lab", key="open_jupyter_lab_button"):
                # Track interaction
                track_interaction(
                    interaction_type="click",
                    component_id="open_jupyter_lab_button",
                    component_type="button",
                    page_name="Workshop",
                    details={"action": "open_jupyter_lab"}
                )

                # Open Jupyter Lab in a new browser tab
                jupyter_url = "http://localhost:8888/lab"
                html = f'<script>window.open("{jupyter_url}", "_blank");</script>'
                st.markdown(html, unsafe_allow_html=True)
                st.success(f"Jupyter Lab opened at {jupyter_url}")

                # Track successful outcome
                track_interaction(
                    interaction_type="success",
                    component_id="open_jupyter_lab_button",
                    component_type="button",
                    page_name="Workshop",
                    details={"outcome": "jupyter_lab_opened", "url": jupyter_url}
                )

        with col2:
            st.markdown("#### Python Script")
            st.markdown("""
            Run the challenge script directly:
            1. Click the button below to run the challenge script
            2. Follow the instructions in the terminal
            3. Use the checkpoint verification script to check your progress
            """)

            if st.button("Run Challenge Script", key="run_challenge_script_button"):
                # Track interaction
                track_interaction(
                    interaction_type="click",
                    component_id="run_challenge_script_button",
                    component_type="button",
                    page_name="Workshop",
                    details={"action": "run_challenge_script"}
                )

                with st.spinner("Running challenge script..."):
                    try:
                        # Run the challenge script
                        result = subprocess.run(
                            [sys.executable, "-m", "tutorials.preclinical_challenge_tutorial"],
                            capture_output=True,
                            text=True
                        )

                        if result.returncode == 0:
                            st.success("Challenge script completed successfully!")
                            st.code(result.stdout)
                            # Track successful outcome
                            track_interaction(
                                interaction_type="success",
                                component_id="run_challenge_script_button",
                                component_type="button",
                                page_name="Workshop",
                                details={"outcome": "challenge_script_completed_successfully"}
                            )
                        else:
                            st.error("Challenge script failed.")
                            st.code(result.stderr)
                            # Track error outcome
                            track_interaction(
                                interaction_type="error",
                                component_id="run_challenge_script_button",
                                component_type="button",
                                page_name="Workshop",
                                details={"outcome": "challenge_script_failed", "stderr": result.stderr}
                            )
                    except Exception as e:
                        st.error(f"Error running challenge script: {e}")
                        # Track exception
                        track_interaction(
                            interaction_type="error",
                            component_id="run_challenge_script_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"error": str(e)}
                        )

        # Checkpoint verification
        st.markdown("### Checkpoint Verification")
        st.markdown("""
        You can verify your progress through the challenge by running the checkpoint verification script.
        This script will check if you have completed each step of the challenge correctly.
        """)

        checkpoint = st.selectbox(
            "Select checkpoint to verify:",
            [
                "All checkpoints",
                "Checkpoint 1: Dataset loading and exploration",
                "Checkpoint 2: Analyzing experiments and animal groups",
                "Checkpoint 3: Tumor growth analysis",
                "Checkpoint 4: Survival analysis",
                "Checkpoint 5: Answering research questions"
            ]
        )

        if st.button("Verify Checkpoint", key="verify_checkpoint_button"):
            # Track interaction
            track_interaction(
                interaction_type="click",
                component_id="verify_checkpoint_button",
                component_type="button",
                page_name="Workshop",
                details={"action": "verify_checkpoint", "checkpoint": checkpoint}
            )

            with st.spinner("Verifying checkpoint..."):
                try:
                    # Determine checkpoint number
                    checkpoint_num = 0  # All checkpoints
                    if checkpoint.startswith("Checkpoint"):
                        checkpoint_num = int(checkpoint.split(":")[0].split(" ")[1])

                    # Run the verification script
                    cmd = [sys.executable, "-m", "tutorials.checkpoint_verification"]
                    if checkpoint_num > 0:
                        cmd.append(str(checkpoint_num))

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True
                    )

                    if "ALL CHECKPOINTS PASSED" in result.stdout:
                        st.success("All checkpoints passed!")
                        st.code(result.stdout)
                        # Track successful outcome
                        track_interaction(
                            interaction_type="success",
                            component_id="verify_checkpoint_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"outcome": "all_checkpoints_passed", "checkpoint": checkpoint}
                        )
                    elif "PASSED" in result.stdout:
                        st.success(f"Checkpoint {checkpoint_num} passed!")
                        st.code(result.stdout)
                        # Track successful outcome
                        track_interaction(
                            interaction_type="success",
                            component_id="verify_checkpoint_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"outcome": "checkpoint_passed", "checkpoint_num": checkpoint_num}
                        )
                    else:
                        st.warning("Some checkpoints failed. Keep working on the challenge!")
                        st.code(result.stdout)
                        # Track warning outcome
                        track_interaction(
                            interaction_type="warning",
                            component_id="verify_checkpoint_button",
                            component_type="button",
                            page_name="Workshop",
                            details={"outcome": "checkpoints_failed", "checkpoint": checkpoint}
                        )
                except Exception as e:
                    st.error(f"Error verifying checkpoint: {e}")
                    # Track error outcome
                    track_interaction(
                        interaction_type="error",
                        component_id="verify_checkpoint_button",
                        component_type="button",
                        page_name="Workshop",
                        details={"error": str(e)}
                    )

    def _render_resources(self):
        """Render the Resources section."""
        st.header("Resources")

        st.markdown("""
        ### Documentation

        - [Science Data Kit Documentation](https://your-org.github.io/science_data_kit/)
        - [Neo4j Documentation](https://neo4j.com/docs/)
        - [Cypher Query Language Reference](https://neo4j.com/docs/cypher-manual/current/)

        ### Jupyter Notebook Tutorials

        Interactive Jupyter notebook tutorials that you can run and modify:

        - [Preclinical Challenge Tutorial](http://localhost:8888/lab/tree/tutorials/preclinical_challenge_tutorial.ipynb) - Analyze a preclinical cancer research dataset
        - [Database Operations Tutorial](http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb) - Learn database operations with Neo4j
        - [Data Transformation Tutorial](http://localhost:8888/lab/tree/tutorials/data_transformation_tutorial.ipynb) - Transform data between different formats
        - [Data Visualization Tutorial](http://localhost:8888/lab/tree/tutorials/data_visualization_tutorial.ipynb) - Create static and interactive visualizations

        ### Python Script Tutorials

        Python script versions of the tutorials:

        - [Preclinical Challenge Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/preclinical_challenge_tutorial.py)
        - [Database Operations Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/database_operations_tutorial.py)
        - [Data Transformation Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/data_transformation_tutorial.py)
        - [Data Visualization Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/data_visualization_tutorial.py)

        ### Sample Datasets

        - [Preclinical Research Dataset](https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/preclinical)
        - [Other Sample Datasets](https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples)

        ### Tools

        - [Jupyter Lab](http://localhost:8888/lab) - Interactive notebooks
        - [NeoDash](http://localhost:5005) - Neo4j dashboards
        - [Neo4j Browser](http://localhost:7474) - Neo4j database browser
        """)

        # Display video tutorials section
        st.markdown("---")
        display_video_tutorials_section()

        # Display demo videos section
        st.markdown("---")
        display_demo_videos_section()

    def _render_help(self):
        """Render the Help section."""
        st.header("Help")

        st.markdown("""
        ### Common Issues

        #### Database Connection Issues

        If you're having trouble connecting to the Neo4j database:
        1. Check that the Neo4j container is running
        2. Verify the connection settings on the Server page
        3. Try restarting the Neo4j container

        #### Dataset Loading Issues

        If you're having trouble loading the preclinical research dataset:
        1. Check that the Neo4j database is running and accessible
        2. Verify that you have the necessary permissions
        3. Try reloading the dataset from the Getting Started tab

        #### Tutorial Issues

        If you're having trouble with the 30-Minute Challenge:
        1. Make sure the preclinical research dataset is loaded
        2. Check that you're running the correct version of the tutorial
        3. Verify your progress using the checkpoint verification script

        ### Getting Help

        If you're still having issues:
        1. Ask a workshop instructor for help
        2. Check the [GitHub repository](https://github.com/your-org/science_data_kit) for known issues
        3. Consult the [documentation](https://your-org.github.io/science_data_kit/)
        """)

        # Contact form
        st.markdown("### Contact Form")
        st.markdown("""
        If you need additional help, please fill out this form:
        """)

        with st.form("help_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            issue = st.text_area("Describe your issue")
            submitted = st.form_submit_button("Submit")

            if submitted:
                # Track form submission
                track_interaction(
                    interaction_type="form_submit",
                    component_id="help_form",
                    component_type="form",
                    page_name="Workshop",
                    details={
                        "action": "submit_help_request",
                        "has_name": bool(name),
                        "has_email": bool(email),
                        "has_issue": bool(issue),
                        "issue_length": len(issue)
                    }
                )

                st.success("Your request has been submitted. An instructor will assist you shortly.")

    def _render_feedback(self):
        """Render the Feedback section."""
        st.header("Workshop Feedback")

        st.markdown("""
        ### Your Feedback Matters

        We value your feedback on the Science Data Kit Workshop. Your input helps us improve the workshop experience
        and the Science Data Kit itself. Please take a moment to share your thoughts and suggestions.
        """)

        # Generate a workshop ID if not already in session state
        if "workshop_id" not in st.session_state:
            st.session_state["workshop_id"] = f"workshop_{datetime.datetime.now().strftime('%Y%m%d')}"

        # Get participant ID from session state or generate a new one
        if "participant_id" not in st.session_state:
            st.session_state["participant_id"] = f"participant_{uuid.uuid4().hex[:8]}"

        # Display the workshop and participant IDs
        st.info(f"Workshop ID: {st.session_state['workshop_id']} | Participant ID: {st.session_state['participant_id']}")

        # Collect feedback
        feedback_submitted = collect_workshop_feedback(
            workshop_id=st.session_state["workshop_id"],
            participant_id=st.session_state["participant_id"]
        )

        # Track feedback submission
        if feedback_submitted:
            track_interaction(
                interaction_type="form_submit",
                component_id="workshop_feedback_form",
                component_type="form",
                page_name="Workshop",
                details={
                    "action": "submit_workshop_feedback",
                    "workshop_id": st.session_state["workshop_id"],
                    "participant_id": st.session_state["participant_id"]
                }
            )


def render_workshop_page():
    """Render the workshop page."""
    page = WorkshopPage()
    page.render()

if __name__ == "__main__":
    render_workshop_page()
