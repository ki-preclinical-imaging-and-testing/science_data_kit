"""
Instructor Page Module for Science Data Kit Core

This module provides the core functionality for the Instructor page,
allowing workshop facilitators to access instructor notes and guidance.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import InstructorPageData

class InstructorPage(BasePage):
    """
    Core functionality for the Instructor page.
    
    This class provides the backend functionality for displaying instructor notes
    and guidance for workshop facilitators.
    """
    
    def __init__(self):
        """Initialize the Instructor page."""
        super().__init__()
        self.title = "Instructor Notes"
        self.icon = "👨‍🏫"
        
        # Initialize notes
        self.notes = {}
        self.selected_section = None
        self.notes_path = None
        
        # Load notes
        self._load_notes()
    
    def _load_notes(self) -> None:
        """Load instructor notes from JSON file or use default notes."""
        notes_path = Path(__file__).parent.parent.parent.parent / "docs" / "workshop" / "instructor_notes.json"
        self.notes_path = str(notes_path)
        
        if notes_path.exists():
            try:
                with open(notes_path, "r") as f:
                    self.notes = json.load(f)
            except Exception as e:
                self.notes = self._get_default_notes()
        else:
            self.notes = self._get_default_notes()
            
            # Save default notes to file
            notes_dir = notes_path.parent
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(notes_path, "w") as f:
                    json.dump(self.notes, f, indent=2)
            except Exception:
                pass
    
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
    
    def get_page_data(self) -> InstructorPageData:
        """
        Return data needed to render the Instructor page.
        
        Returns:
            An instance of InstructorPageData containing the data needed
            to render the page.
        """
        # Get all sections
        sections = self.get_all_sections()
        
        # Create page data
        page_data = InstructorPageData(
            title=self.title,
            notes=self.notes,
            sections=sections,
            selected_section=self.selected_section,
            notes_path=self.notes_path
        )
        
        return page_data
    
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
    
    def set_selected_section(self, section_key: str) -> Dict[str, Any]:
        """
        Set the selected section.
        
        Args:
            section_key: The key of the section to select.
            
        Returns:
            A dictionary with the result of the operation.
        """
        if section_key in self.notes:
            self.selected_section = section_key
            return {"success": True, "message": f"Selected section: {section_key}"}
        else:
            return {"success": False, "error": f"Section not found: {section_key}"}
    
    def export_notes(self, format: str = "markdown", path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export instructor notes to a file.
        
        Args:
            format: The export format ("markdown" or "pdf").
            path: Optional path to save the file. If None, uses a default path.
            
        Returns:
            A dictionary with the result of the operation.
        """
        try:
            if format.lower() == "markdown":
                # Create a markdown file with all sections
                markdown_content = ""
                for section in self.get_all_sections():
                    markdown_content += f"# {section['title']}\n\n{section['content']}\n\n---\n\n"
                
                # Determine export path
                if path:
                    export_path = Path(path)
                else:
                    export_path = Path.home() / "instructor_notes.md"
                
                # Save to file
                with open(export_path, "w") as f:
                    f.write(markdown_content)
                
                return {"success": True, "message": f"Instructor notes exported to {export_path}", "path": str(export_path)}
            elif format.lower() == "pdf":
                return {"success": False, "error": "PDF export not implemented yet. Please use the Markdown export and convert to PDF using a tool like Pandoc."}
            else:
                return {"success": False, "error": f"Unsupported export format: {format}"}
        except Exception as e:
            return {"success": False, "error": f"Error exporting instructor notes: {str(e)}"}