"""
Instructor Notes Module for Science Data Kit

This module provides functionality for displaying instructor notes and guidance
for workshop facilitators. It includes classes and functions for:
- Displaying instructor notes
- Providing guidance on workshop facilitation
- Highlighting common issues and solutions
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class InstructorNotes:
    """
    Instructor notes class for Science Data Kit.
    
    This class provides methods for displaying instructor notes and guidance
    for workshop facilitators.
    """
    
    def __init__(self):
        """Initialize the instructor notes."""
        self._load_notes()
    
    def _load_notes(self) -> None:
        """Load instructor notes from JSON file or use default notes."""
        notes_path = Path(__file__).parent.parent.parent.parent / "docs" / "workshop" / "instructor_notes.json"
        
        if notes_path.exists():
            try:
                with open(notes_path, "r") as f:
                    self.notes = json.load(f)
            except Exception as e:
                st.warning(f"Error loading instructor notes: {e}")
                self.notes = self._get_default_notes()
        else:
            self.notes = self._get_default_notes()
            
            # Save default notes to file
            notes_dir = notes_path.parent
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(notes_path, "w") as f:
                    json.dump(self.notes, f, indent=2)
            except Exception as e:
                st.warning(f"Error saving default instructor notes: {e}")
    
    def _get_default_notes(self) -> Dict[str, Any]:
        """
        Get default instructor notes.
        
        Returns:
            A dictionary containing default instructor notes.
        """
        return {
            "workshop_overview": {
                "title": "Workshop Overview",
                "content": """
                # Science Data Kit Workshop - Instructor Guide
                
                This guide provides instructions and tips for facilitating the Science Data Kit workshop.
                The workshop is designed to introduce participants to the Science Data Kit and guide them
                through hands-on exercises using realistic scientific datasets.
                
                ## Workshop Objectives
                
                By the end of this workshop, participants should be able to:
                
                1. Understand the core components of the Science Data Kit
                2. Load and explore scientific datasets
                3. Perform basic data analysis and visualization
                4. Use the Science Data Kit to answer research questions
                
                ## Workshop Structure
                
                The workshop is structured in progressive steps:
                
                1. **Introduction and Setup** (30 minutes)
                   - Introduction to the Science Data Kit
                   - Installation and configuration
                   - Loading the preclinical research dataset
                
                2. **Guided Exploration** (45 minutes)
                   - Exploring the dataset structure
                   - Running basic queries
                   - Creating simple visualizations
                
                3. **30-Minute Challenge** (45 minutes)
                   - Analyzing experimental design
                   - Analyzing tumor growth
                   - Analyzing survival outcomes
                   - Identifying effective treatments
                
                4. **Advanced Topics** (30 minutes)
                   - Custom visualizations
                   - Integration with other tools
                   - Building dashboards
                
                5. **Q&A and Wrap-up** (30 minutes)
                   - Addressing questions
                   - Discussing next steps
                   - Collecting feedback
                """
            },
            "preparation": {
                "title": "Preparation",
                "content": """
                # Workshop Preparation
                
                ## Before the Workshop
                
                1. **Environment Setup**
                   - Ensure all participants have access to the Science Data Kit
                   - Test the installation on different operating systems
                   - Prepare backup installation methods (Docker, virtual environment)
                
                2. **Materials**
                   - Review all workshop materials
                   - Prepare printed handouts (optional)
                   - Set up a shared repository for code examples
                
                3. **Technical Setup**
                   - Test the projector and screen
                   - Ensure stable internet connection
                   - Set up a communication channel for questions (Slack, Discord)
                
                ## Day of the Workshop
                
                1. **Arrival**
                   - Arrive at least 30 minutes early
                   - Test all equipment
                   - Greet participants as they arrive
                
                2. **Introduction**
                   - Start with a brief introduction of yourself and the workshop
                   - Set expectations for the day
                   - Explain the workshop structure
                
                3. **Technical Support**
                   - Have a designated person for technical support
                   - Prepare for common installation issues
                   - Have backup plans for technical failures
                """
            },
            "facilitation_tips": {
                "title": "Facilitation Tips",
                "content": """
                # Facilitation Tips
                
                ## General Tips
                
                1. **Pace**
                   - Start slow and build momentum
                   - Check in regularly with participants
                   - Be prepared to adjust the pace based on participant feedback
                
                2. **Engagement**
                   - Ask questions to keep participants engaged
                   - Encourage participants to help each other
                   - Use real-world examples to illustrate concepts
                
                3. **Troubleshooting**
                   - Address common issues proactively
                   - Have participants work in pairs to troubleshoot
                   - Document new issues for future workshops
                
                ## Specific Workshop Sections
                
                1. **Introduction and Setup**
                   - Be patient with installation issues
                   - Have pre-configured environments ready as backup
                   - Use this time to understand participants' backgrounds
                
                2. **Guided Exploration**
                   - Demonstrate each step clearly
                   - Explain the purpose of each query or visualization
                   - Allow time for questions after each section
                
                3. **30-Minute Challenge**
                   - Encourage participants to work at their own pace
                   - Provide hints rather than solutions
                   - Celebrate small victories
                
                4. **Advanced Topics**
                   - Tailor this section to participant interests
                   - Provide resources for further learning
                   - Connect concepts to participants' work
                
                5. **Q&A and Wrap-up**
                   - Address all questions, even if briefly
                   - Summarize key learnings
                   - Provide clear next steps
                """
            },
            "common_issues": {
                "title": "Common Issues",
                "content": """
                # Common Issues and Solutions
                
                ## Installation Issues
                
                1. **Neo4j Connection Problems**
                   - **Issue**: Participants cannot connect to Neo4j
                   - **Solution**: Check Neo4j service status, verify connection settings, restart Neo4j
                
                2. **Python Package Conflicts**
                   - **Issue**: Package version conflicts during installation
                   - **Solution**: Use a clean virtual environment, provide requirements.txt
                
                3. **Permission Errors**
                   - **Issue**: Permission denied when installing packages
                   - **Solution**: Use `--user` flag, check directory permissions
                
                ## Dataset Issues
                
                1. **Dataset Loading Failures**
                   - **Issue**: Preclinical dataset fails to load
                   - **Solution**: Check Neo4j connection, verify database is empty, check disk space
                
                2. **Missing Data**
                   - **Issue**: Expected data is missing from queries
                   - **Solution**: Verify dataset loading completed, check query syntax
                
                3. **Performance Issues**
                   - **Issue**: Queries or visualizations are slow
                   - **Solution**: Optimize queries, reduce data size, check system resources
                
                ## UI Issues
                
                1. **Streamlit App Crashes**
                   - **Issue**: Streamlit app crashes or freezes
                   - **Solution**: Restart the app, check logs, reduce complexity of operations
                
                2. **Visualization Rendering Problems**
                   - **Issue**: Visualizations don't render correctly
                   - **Solution**: Check browser compatibility, update packages, simplify visualization
                
                3. **UI Element Alignment**
                   - **Issue**: UI elements are misaligned or overlapping
                   - **Solution**: Adjust column widths, use containers, check responsive design
                """
            },
            "faq": {
                "title": "FAQ",
                "content": """
                # Frequently Asked Questions
                
                ## General Questions
                
                1. **What is the Science Data Kit?**
                   - The Science Data Kit is a comprehensive tool for scientific data analysis and visualization, providing a unified interface for working with various data sources.
                
                2. **Is the Science Data Kit free to use?**
                   - Yes, the Science Data Kit is open-source and free to use under the MIT license.
                
                3. **Can I contribute to the Science Data Kit?**
                   - Yes, contributions are welcome! Check the GitHub repository for contribution guidelines.
                
                ## Technical Questions
                
                1. **What databases does the Science Data Kit support?**
                   - The Science Data Kit primarily supports Neo4j, but also has connectors for SQL databases, Elasticsearch, and RESTful APIs.
                
                2. **Can I use the Science Data Kit with my existing data?**
                   - Yes, the Science Data Kit provides tools for importing data from various formats, including CSV, Excel, and JSON.
                
                3. **Does the Science Data Kit work offline?**
                   - Yes, once installed, the Science Data Kit can work offline with local databases.
                
                ## Workshop Questions
                
                1. **Will the workshop materials be available after the workshop?**
                   - Yes, all workshop materials will be available in the GitHub repository.
                
                2. **Do I need prior experience with Neo4j?**
                   - No, the workshop is designed for beginners and will cover the basics of Neo4j.
                
                3. **Can I use my own dataset in the workshop?**
                   - The workshop is designed around the provided datasets, but you can apply the same techniques to your own data afterward.
                """
            },
            "resources": {
                "title": "Resources",
                "content": """
                # Additional Resources
                
                ## Documentation
                
                - [Science Data Kit Documentation](https://your-org.github.io/science_data_kit/)
                - [Neo4j Documentation](https://neo4j.com/docs/)
                - [Streamlit Documentation](https://docs.streamlit.io/)
                
                ## Tutorials
                
                - [Preclinical Challenge Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/preclinical_challenge_tutorial.ipynb)
                - [Database Operations Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/database_operations_tutorial.ipynb)
                - [Data Transformation Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/data_transformation_tutorial.ipynb)
                - [Data Visualization Tutorial](https://github.com/your-org/science_data_kit/blob/main/tutorials/data_visualization_tutorial.ipynb)
                
                ## Sample Datasets
                
                - [Preclinical Research Dataset](https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/preclinical)
                - [Clinical Trial Dataset](https://github.com/your-org/science_data_kit/tree/main/science_data_kit/data/samples/datasets/clinical_trial)
                
                ## Community
                
                - [GitHub Repository](https://github.com/your-org/science_data_kit)
                - [Issue Tracker](https://github.com/your-org/science_data_kit/issues)
                - [Discussion Forum](https://github.com/your-org/science_data_kit/discussions)
                """
            }
        }
    
    def get_section(self, section_key: str) -> Dict[str, str]:
        """
        Get a specific section of the instructor notes.
        
        Args:
            section_key: The key of the section to retrieve.
            
        Returns:
            A dictionary containing the section title and content.
        """
        return self.notes.get(section_key, {"title": "Section Not Found", "content": "The requested section was not found."})
    
    def get_all_sections(self) -> List[Dict[str, str]]:
        """
        Get all sections of the instructor notes.
        
        Returns:
            A list of dictionaries containing all section titles and contents.
        """
        return [{"key": key, **section} for key, section in self.notes.items()]

# Create a singleton instance of the instructor notes
_instructor_notes = None

def get_instructor_notes() -> InstructorNotes:
    """
    Get the singleton instance of the instructor notes.
    
    Returns:
        The InstructorNotes instance.
    """
    global _instructor_notes
    if _instructor_notes is None:
        _instructor_notes = InstructorNotes()
    return _instructor_notes

def render_instructor_notes():
    """
    Render the instructor notes dashboard.
    
    This function creates a Streamlit UI for viewing instructor notes and guidance.
    """
    st.title("Workshop Instructor Notes")
    
    notes = get_instructor_notes()
    sections = notes.get_all_sections()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    selected_section = st.sidebar.radio(
        "Select Section",
        options=[section["title"] for section in sections],
        key="instructor_notes_section"
    )
    
    # Display selected section
    selected_section_data = next((section for section in sections if section["title"] == selected_section), None)
    
    if selected_section_data:
        st.markdown(selected_section_data["content"])
    else:
        st.error("Section not found.")
    
    # Export options
    with st.sidebar.expander("Export Options"):
        if st.button("Export as Markdown"):
            # Create a markdown file with all sections
            markdown_content = ""
            for section in sections:
                markdown_content += f"# {section['title']}\n\n{section['content']}\n\n---\n\n"
            
            # Save to file
            export_path = Path.home() / "instructor_notes.md"
            with open(export_path, "w") as f:
                f.write(markdown_content)
            
            st.success(f"Instructor notes exported to {export_path}")
        
        if st.button("Export as PDF"):
            st.warning("PDF export not implemented yet. Please use the Markdown export and convert to PDF using a tool like Pandoc.")

def add_instructor_notes_to_workshop(workshop_id: str):
    """
    Add instructor notes to a workshop page.
    
    Args:
        workshop_id: Identifier for the workshop.
    """
    notes = get_instructor_notes()
    
    with st.expander("Instructor Notes", expanded=False):
        st.info("These notes are only visible to workshop instructors. They provide guidance on facilitating the workshop.")
        
        # Quick reference
        st.subheader("Quick Reference")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Workshop Structure
            1. Introduction and Setup (30 min)
            2. Guided Exploration (45 min)
            3. 30-Minute Challenge (45 min)
            4. Advanced Topics (30 min)
            5. Q&A and Wrap-up (30 min)
            """)
        
        with col2:
            st.markdown("""
            ### Common Issues
            - Neo4j Connection Problems
            - Dataset Loading Failures
            - Streamlit App Crashes
            - Visualization Rendering Problems
            """)
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Facilitation Tips", "Common Issues", "FAQ"])
        
        with tab1:
            st.markdown(notes.get_section("facilitation_tips")["content"])
        
        with tab2:
            st.markdown(notes.get_section("common_issues")["content"])
        
        with tab3:
            st.markdown(notes.get_section("faq")["content"])
        
        # Link to full instructor notes
        st.markdown("[View Full Instructor Notes](/observation)")