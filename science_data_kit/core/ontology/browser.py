"""
Ontology browser for Science Data Kit.

This module provides a simple ontology browser/search capability.
"""

from typing import Optional, List, Dict, Any, Union
import pandas as pd
import networkx as nx
from pyvis.network import Network

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology.queries import (
    get_ontology_terms, get_ontology_sources, get_ontology_relationships,
    get_ontology_hierarchy, search_ontology_terms, get_ontology_statistics
)


class OntologyBrowser:
    """
    A class for browsing and visualizing ontologies in Neo4j.
    
    This class provides functionality for browsing and visualizing ontologies
    stored in Neo4j, including term hierarchies and relationships.
    
    Attributes:
        db_manager: The Neo4j database manager to use for querying ontologies.
    """
    
    def __init__(self, db_manager: Neo4jManager):
        """
        Initialize the OntologyBrowser.
        
        Args:
            db_manager: The Neo4j database manager to use for querying ontologies.
        """
        self.db_manager = db_manager
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ontologies in the database.
        
        Returns:
            A dictionary containing statistics about the ontologies.
        """
        return get_ontology_statistics(self.db_manager)
    
    def search_terms(self, search_term: str) -> pd.DataFrame:
        """
        Search for ontology terms in the database.
        
        Args:
            search_term: The term to search for.
            
        Returns:
            A pandas DataFrame containing the matching ontology terms.
        """
        results = search_ontology_terms(self.db_manager, search_term)
        return pd.DataFrame(results)
    
    def get_term_hierarchy(self, term: str) -> pd.DataFrame:
        """
        Get the hierarchy for a specific ontology term.
        
        Args:
            term: The term to get the hierarchy for.
            
        Returns:
            A pandas DataFrame containing the ontology hierarchy.
        """
        results = get_ontology_hierarchy(self.db_manager, term)
        return pd.DataFrame(results)
    
    def visualize_term_hierarchy(self, term: str, height: str = "500px", width: str = "100%") -> Network:
        """
        Visualize the hierarchy for a specific ontology term.
        
        Args:
            term: The term to visualize the hierarchy for.
            height: The height of the visualization.
            width: The width of the visualization.
            
        Returns:
            A pyvis Network object containing the visualization.
        """
        # Get the hierarchy data
        hierarchy_data = get_ontology_hierarchy(self.db_manager, term)
        
        # Create a NetworkX graph
        G = nx.DiGraph()
        
        # Add the main term
        if hierarchy_data:
            main_term = hierarchy_data[0]["term"]
            main_accession = hierarchy_data[0]["term_accession"]
            G.add_node(main_term, title=f"{main_term} ({main_accession})", group=1)
            
            # Add parent terms and relationships
            for record in hierarchy_data:
                parent_terms = record.get("parent_terms", [])
                parent_accessions = record.get("parent_accessions", [])
                
                for i, parent_term in enumerate(parent_terms):
                    parent_accession = parent_accessions[i] if i < len(parent_accessions) else ""
                    G.add_node(parent_term, title=f"{parent_term} ({parent_accession})", group=2)
                    G.add_edge(main_term, parent_term, title="SUBCLASS_OF")
        
        # Create a pyvis network from the NetworkX graph
        net = Network(height=height, width=width, directed=True)
        net.from_nx(G)
        
        # Set options for the visualization
        net.set_options("""
        {
            "nodes": {
                "shape": "dot",
                "size": 20,
                "font": {
                    "size": 14
                }
            },
            "edges": {
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.5
                    }
                },
                "color": {
                    "inherit": true
                },
                "smooth": {
                    "enabled": false
                }
            },
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 0.0,
                    "springLength": 100,
                    "springConstant": 0.01,
                    "nodeDistance": 120,
                    "damping": 0.09
                },
                "solver": "hierarchicalRepulsion"
            }
        }
        """)
        
        return net
    
    def visualize_ontology_sources(self, height: str = "500px", width: str = "100%") -> Network:
        """
        Visualize the ontology sources and their relationships.
        
        Args:
            height: The height of the visualization.
            width: The width of the visualization.
            
        Returns:
            A pyvis Network object containing the visualization.
        """
        # Get the sources and relationships data
        sources_data = get_ontology_sources(self.db_manager)
        relationships_data = get_ontology_relationships(self.db_manager)
        
        # Create a NetworkX graph
        G = nx.DiGraph()
        
        # Add source nodes
        for source in sources_data:
            source_name = source["name"]
            source_description = source.get("description", "")
            G.add_node(source_name, title=source_description, group=1)
        
        # Add term nodes and relationships
        for rel in relationships_data:
            source_name = rel["source_name"]
            term = rel["term"]
            term_accession = rel.get("term_accession", "")
            relationship_type = rel.get("relationship_type", "HAS_TERM")
            
            G.add_node(term, title=f"{term} ({term_accession})", group=2)
            G.add_edge(source_name, term, title=relationship_type)
        
        # Create a pyvis network from the NetworkX graph
        net = Network(height=height, width=width, directed=True)
        net.from_nx(G)
        
        # Set options for the visualization
        net.set_options("""
        {
            "nodes": {
                "shape": "dot",
                "size": 20,
                "font": {
                    "size": 14
                }
            },
            "edges": {
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 0.5
                    }
                },
                "color": {
                    "inherit": true
                },
                "smooth": {
                    "enabled": false
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "solver": "forceAtlas2Based"
            }
        }
        """)
        
        return net