"""
Reference Cards Component for Science Data Kit

This module provides functionality for displaying reference cards in the Science Data Kit application.
It includes classes and functions for:
- Loading reference card metadata
- Displaying reference cards
- Providing information about available reference cards
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class ReferenceCards:
    """
    Reference cards class for Science Data Kit.
    
    This class provides methods for loading and displaying reference cards.
    """
    
    def __init__(self):
        """Initialize the reference cards component."""
        self.cards = self._load_cards()
    
    def _load_cards(self) -> List[Dict[str, Any]]:
        """
        Load reference card metadata from JSON files.
        
        Returns:
            A list of dictionaries containing card metadata.
        """
        cards = []
        
        # Path to the metadata directory
        metadata_dir = Path(__file__).parent.parent.parent.parent / "reference_cards" / "metadata"
        
        # Check if the directory exists
        if not metadata_dir.exists():
            # Create the directory structure if it doesn't exist
            metadata_dir.parent.mkdir(parents=True, exist_ok=True)
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a README file
            readme_path = metadata_dir.parent / "README.md"
            with open(readme_path, "w") as f:
                f.write("""# Science Data Kit Reference Cards

This directory contains metadata and resources for the Science Data Kit reference cards. These cards provide quick reference information for key features, workflows, and concepts in the Science Data Kit.

## Directory Structure

- `metadata/`: Contains metadata files for each reference card, including titles, descriptions, and content
- `resources/`: Contains additional resources used in the reference cards, such as images or diagrams
- `templates/`: Contains templates for creating new reference cards

## Available Reference Cards

1. **Database Operations Card**: Quick reference for common database operations
2. **Data Visualization Card**: Quick reference for data visualization options
3. **Analysis Workflows Card**: Quick reference for common analysis workflows
4. **Cypher Query Card**: Quick reference for Cypher query language
5. **Keyboard Shortcuts Card**: Quick reference for keyboard shortcuts

## Usage Guidelines

Reference cards are designed to be:

1. **Concise**: Each card focuses on a specific topic and provides only essential information
2. **Visual**: Cards use diagrams, icons, and color-coding to enhance understanding
3. **Practical**: Cards emphasize practical usage rather than theoretical concepts
4. **Accessible**: Cards are available in both digital and printable formats

## Creating New Reference Cards

To create a new reference card:

1. Use the template in the `templates/` directory
2. Focus on a single topic or workflow
3. Limit content to what fits on a standard 5x7 card
4. Include visual elements where appropriate
5. Add metadata to the `metadata/` directory

## Usage

The reference cards are accessible through the workshop page and can be printed for physical distribution during workshops.
""")
            
            # Create the resources directory
            resources_dir = metadata_dir.parent / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the templates directory
            templates_dir = metadata_dir.parent / "templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a template file
            template_path = templates_dir / "reference_card_template.md"
            with open(template_path, "w") as f:
                f.write("""# Reference Card Template

## Front Side

### Title
[Card Title]

### Subtitle
[Brief description of what this card covers]

### Main Content
- Key point 1
- Key point 2
- Key point 3

### Visual Element
[Description of diagram or visual element]

## Back Side

### Examples
```
[Code or command example]
```

### Tips
- Tip 1
- Tip 2
- Tip 3

### Related Resources
- [Resource 1]
- [Resource 2]
""")
            
            # Create sample metadata files
            card_metadata = [
                {
                    "title": "Database Operations Card",
                    "description": "Quick reference for common database operations in the Science Data Kit.",
                    "categories": ["database", "operations", "reference"],
                    "order": 1,
                    "front_content": {
                        "title": "Database Operations",
                        "subtitle": "Common operations for working with Neo4j databases",
                        "main_points": [
                            "Connect to database: sdk.db.connect(uri, username, password)",
                            "Execute query: sdk.db.query(cypher_query, parameters)",
                            "Import data: sdk.db.import_csv(file_path, node_label)",
                            "Export data: sdk.db.export_results(results, format='csv')",
                            "Create index: sdk.db.create_index(label, property)"
                        ],
                        "visual": "Database connection workflow diagram"
                    },
                    "back_content": {
                        "examples": [
                            "# Connect to database\ndb = sdk.db.connect('neo4j://localhost:7687', 'neo4j', 'password')",
                            "# Execute query\nresults = db.query('MATCH (n:Person) RETURN n.name, n.age')",
                            "# Import data\ndb.import_csv('data.csv', 'Person')"
                        ],
                        "tips": [
                            "Use connection pooling for better performance",
                            "Always parameterize queries to prevent injection",
                            "Close connections when finished to free resources",
                            "Use transactions for multiple operations"
                        ],
                        "related_resources": [
                            {"title": "Database Operations Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb"},
                            {"title": "Neo4j Documentation", "url": "https://neo4j.com/docs/"}
                        ]
                    },
                    "status": "Ready for printing"
                },
                {
                    "title": "Data Visualization Card",
                    "description": "Quick reference for data visualization options in the Science Data Kit.",
                    "categories": ["visualization", "charts", "reference"],
                    "order": 2,
                    "front_content": {
                        "title": "Data Visualization",
                        "subtitle": "Common visualization types and when to use them",
                        "main_points": [
                            "Bar charts: Compare values across categories",
                            "Line charts: Show trends over time",
                            "Scatter plots: Examine relationships between variables",
                            "Pie charts: Show composition of a whole",
                            "Heatmaps: Visualize matrix data and correlations"
                        ],
                        "visual": "Decision tree for selecting visualization types"
                    },
                    "back_content": {
                        "examples": [
                            "# Create bar chart\nsdk.viz.bar_chart(data, x='category', y='value')",
                            "# Create line chart\nsdk.viz.line_chart(data, x='date', y='value')",
                            "# Create scatter plot\nsdk.viz.scatter_plot(data, x='variable1', y='variable2')"
                        ],
                        "tips": [
                            "Choose the right chart for your data type",
                            "Keep visualizations simple and focused",
                            "Use color consistently and meaningfully",
                            "Include clear labels and legends"
                        ],
                        "related_resources": [
                            {"title": "Data Visualization Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/data_visualization_tutorial.ipynb"},
                            {"title": "Visualization Best Practices", "url": "https://your-org.github.io/science_data_kit/visualization_best_practices.html"}
                        ]
                    },
                    "status": "Ready for printing"
                },
                {
                    "title": "Analysis Workflows Card",
                    "description": "Quick reference for common analysis workflows in the Science Data Kit.",
                    "categories": ["analysis", "workflows", "reference"],
                    "order": 3,
                    "front_content": {
                        "title": "Analysis Workflows",
                        "subtitle": "Common analysis patterns for scientific data",
                        "main_points": [
                            "Data preparation: Clean, transform, and validate data",
                            "Exploratory analysis: Summarize and visualize data",
                            "Statistical testing: Hypothesis testing and p-values",
                            "Predictive modeling: Train and evaluate models",
                            "Results interpretation: Contextualize findings"
                        ],
                        "visual": "Analysis workflow diagram with decision points"
                    },
                    "back_content": {
                        "examples": [
                            "# Data preparation\nclean_data = sdk.prep.clean(data, handle_missing='mean')",
                            "# Exploratory analysis\nsdk.explore.summary_statistics(data)",
                            "# Statistical testing\nresults = sdk.stats.t_test(group1, group2)"
                        ],
                        "tips": [
                            "Document your analysis steps for reproducibility",
                            "Validate assumptions before applying statistical tests",
                            "Use cross-validation for model evaluation",
                            "Consider multiple testing correction for p-values"
                        ],
                        "related_resources": [
                            {"title": "Preclinical Challenge Tutorial", "url": "http://localhost:8888/lab/tree/tutorials/preclinical_challenge_tutorial.ipynb"},
                            {"title": "Statistical Analysis Guide", "url": "https://your-org.github.io/science_data_kit/statistical_analysis.html"}
                        ]
                    },
                    "status": "Ready for printing"
                },
                {
                    "title": "Cypher Query Card",
                    "description": "Quick reference for Cypher query language used in Neo4j.",
                    "categories": ["database", "cypher", "reference"],
                    "order": 4,
                    "front_content": {
                        "title": "Cypher Query Language",
                        "subtitle": "Essential Cypher syntax for Neo4j queries",
                        "main_points": [
                            "MATCH: Pattern matching in the graph",
                            "WHERE: Filter results based on conditions",
                            "RETURN: Specify what to include in results",
                            "CREATE/MERGE: Create nodes and relationships",
                            "DELETE/REMOVE: Delete nodes or properties"
                        ],
                        "visual": "Cypher query structure diagram"
                    },
                    "back_content": {
                        "examples": [
                            "# Find all people\nMATCH (p:Person) RETURN p.name, p.age",
                            "# Find connections\nMATCH (p:Person)-[:KNOWS]->(f:Person) RETURN p.name, f.name",
                            "# Create relationship\nMATCH (a:Person), (b:Person) WHERE a.name='Alice' AND b.name='Bob' CREATE (a)-[:KNOWS]->(b)"
                        ],
                        "tips": [
                            "Use parameters instead of string concatenation",
                            "Start with specific nodes to improve performance",
                            "Use EXPLAIN/PROFILE to analyze query performance",
                            "Use LIMIT to restrict result size during development"
                        ],
                        "related_resources": [
                            {"title": "Cypher Reference Card", "url": "https://neo4j.com/docs/cypher-refcard/current/"},
                            {"title": "Neo4j Browser", "url": "http://localhost:7474"}
                        ]
                    },
                    "status": "Ready for printing"
                },
                {
                    "title": "Keyboard Shortcuts Card",
                    "description": "Quick reference for keyboard shortcuts in the Science Data Kit applications.",
                    "categories": ["interface", "shortcuts", "reference"],
                    "order": 5,
                    "front_content": {
                        "title": "Keyboard Shortcuts",
                        "subtitle": "Essential keyboard shortcuts for increased productivity",
                        "main_points": [
                            "Navigation: Tab (next), Shift+Tab (previous), Esc (cancel)",
                            "Jupyter: Shift+Enter (run cell), Ctrl+Enter (run without advancing)",
                            "Neo4j Browser: Ctrl+Enter (execute query), Esc (cancel)",
                            "NeoDash: Ctrl+S (save dashboard), Ctrl+R (refresh all)",
                            "Streamlit: R (rerun app), Ctrl+F (find)"
                        ],
                        "visual": "Keyboard layout with highlighted shortcut keys"
                    },
                    "back_content": {
                        "examples": [
                            "# Jupyter Notebook\nCtrl+S: Save notebook\nCtrl+Shift+P: Command palette\nA/B: Insert cell above/below",
                            "# Neo4j Browser\nCtrl+/: Toggle comment\nCtrl+L: Clear editor\nCtrl+Up/Down: Command history",
                            "# General\nCtrl+C/Ctrl+V: Copy/Paste\nCtrl+Z: Undo\nCtrl+F: Find"
                        ],
                        "tips": [
                            "Learn a few shortcuts at a time and practice them",
                            "Focus on shortcuts for your most common tasks",
                            "Create custom keyboard shortcuts where supported",
                            "Use keyboard navigation for accessibility"
                        ],
                        "related_resources": [
                            {"title": "Jupyter Shortcuts", "url": "https://jupyter-notebook.readthedocs.io/en/stable/shortcuts.html"},
                            {"title": "Neo4j Browser Guide", "url": "https://neo4j.com/developer/neo4j-browser/"}
                        ]
                    },
                    "status": "Ready for printing"
                }
            ]
            
            for i, card in enumerate(card_metadata):
                card_id = card["title"].lower().replace(" ", "_")
                metadata_path = metadata_dir / f"{card_id}_metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(card, f, indent=2)
            
            # Return the sample metadata
            for card in card_metadata:
                card["card_id"] = card["title"].lower().replace(" ", "_")
                cards.append(card)
            
            return cards
        
        # Load metadata files
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    
                    # Add the filename (without extension) as the card_id
                    metadata["card_id"] = metadata_file.stem.replace("_metadata", "")
                    
                    cards.append(metadata)
            except Exception as e:
                st.warning(f"Error loading card metadata from {metadata_file}: {e}")
        
        # Sort cards by order if available, otherwise by title
        cards.sort(key=lambda x: x.get("order", 999) if "order" in x else x.get("title", ""))
        
        return cards
    
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """
        Get all available reference cards.
        
        Returns:
            A list of dictionaries containing card metadata.
        """
        return self.cards
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific card by ID.
        
        Args:
            card_id: The ID of the card to retrieve.
            
        Returns:
            A dictionary containing the card metadata, or None if not found.
        """
        for card in self.cards:
            if card.get("card_id") == card_id:
                return card
        return None
    
    def get_cards_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get cards by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A list of dictionaries containing card metadata for the specified category.
        """
        return [card for card in self.cards if category in card.get("categories", [])]

# Create a singleton instance of the reference cards
_reference_cards = None

def get_reference_cards() -> ReferenceCards:
    """
    Get the singleton instance of the reference cards.
    
    Returns:
        The ReferenceCards instance.
    """
    global _reference_cards
    if _reference_cards is None:
        _reference_cards = ReferenceCards()
    return _reference_cards

def display_reference_card(card_id: str) -> None:
    """
    Display a specific reference card.
    
    Args:
        card_id: The ID of the card to display.
    """
    cards = get_reference_cards()
    card = cards.get_card_by_id(card_id)
    
    if not card:
        st.warning(f"Reference card not found: {card_id}")
        return
    
    st.header(card.get("title", "Untitled Card"))
    
    # Display card description
    st.markdown(card.get("description", "No description available."))
    
    # Display card status
    status = card.get("status", "In preparation")
    if status == "In preparation":
        st.info("This reference card is currently in preparation.")
    elif status == "Ready for printing":
        st.success("This reference card is ready for printing and distribution.")
    else:
        st.info(f"Card status: {status}")
    
    # Create tabs for front and back of card
    front_tab, back_tab = st.tabs(["Front Side", "Back Side"])
    
    with front_tab:
        front_content = card.get("front_content", {})
        
        st.subheader(front_content.get("title", "Card Title"))
        st.markdown(f"*{front_content.get('subtitle', 'Card Subtitle')}*")
        
        st.markdown("#### Key Points")
        for point in front_content.get("main_points", []):
            st.markdown(f"- {point}")
        
        if "visual" in front_content:
            st.markdown("#### Visual Element")
            st.info(front_content.get("visual", "Visual element placeholder"))
    
    with back_tab:
        back_content = card.get("back_content", {})
        
        if "examples" in back_content and back_content["examples"]:
            st.markdown("#### Examples")
            for example in back_content["examples"]:
                st.code(example)
        
        if "tips" in back_content and back_content["tips"]:
            st.markdown("#### Tips")
            for tip in back_content["tips"]:
                st.markdown(f"- {tip}")
        
        if "related_resources" in back_content and back_content["related_resources"]:
            st.markdown("#### Related Resources")
            for resource in back_content["related_resources"]:
                st.markdown(f"- [{resource['title']}]({resource['url']})")

def display_reference_cards_section() -> None:
    """
    Display the reference cards section on the workshop page.
    
    This function creates a Streamlit UI for browsing and viewing reference cards.
    """
    st.header("Reference Cards")
    
    cards = get_reference_cards()
    all_cards = cards.get_all_cards()
    
    if not all_cards:
        st.info("No reference cards available yet. Check back soon!")
        return
    
    st.markdown("""
    These reference cards provide quick access to key information about the Science Data Kit.
    Select a card from the list below to view its content. Cards are designed to be printed
    and used as physical reference materials during workshops.
    """)
    
    # Create a selectbox for choosing a card
    card_options = [card.get("title", "Untitled Card") for card in all_cards]
    selected_card_title = st.selectbox("Select a Reference Card", card_options, key="reference_card_selectbox")
    
    # Find the selected card
    selected_card = next((card for card in all_cards 
                         if card.get("title") == selected_card_title), None)
    
    if selected_card:
        # Display the selected card
        display_reference_card(selected_card.get("card_id"))
        
        # Add a download button for printing
        st.download_button(
            label="Download for Printing",
            data="This is a placeholder. In a real implementation, this would generate a PDF version of the card.",
            file_name=f"{selected_card.get('card_id')}.pdf",
            mime="application/pdf",
            key="download_reference_card"
        )