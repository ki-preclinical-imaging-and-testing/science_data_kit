"""
ISA Tools Integration Provider for Science Data Kit

This module provides integration with the ISA Tools platform,
allowing users to access and analyze experimental metadata from ISA Tools
within the Science Data Kit environment.

ISA (Investigation, Study, Assay) is a framework for describing and managing
experimental metadata in life sciences.
"""

import requests
import rdflib
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

from science_data_kit.core.integrations.isa_ontology_manager import ISAOntologyManager
from science_data_kit.core.integrations.isa_json_handler import ISAJSONHandler
from science_data_kit.core.integrations.isa_neo4j_importer import ISANeo4jImporter

class ISAToolsProvider:
    """
    Provider for integrating with the ISA Tools platform.
    
    This class provides a unified interface for working with ISA Tools data,
    delegating specific functionality to specialized modules.
    
    Attributes:
        base_url: The base URL of the ISA Tools API (if applicable).
        api_key: The API key for authenticating with ISA Tools API (if applicable).
        ontology_manager: Manager for ontology-related operations.
        json_handler: Handler for ISA JSON operations.
        neo4j_importer: Importer for Neo4j operations.
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the ISA Tools provider.
        
        Args:
            base_url: The base URL of the ISA Tools API (if applicable).
            api_key: The API key for authenticating with ISA Tools API (if applicable).
        """
        self.base_url = base_url
        self.api_key = api_key
        
        # Set up session
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        
        # Initialize specialized components
        self.ontology_manager = ISAOntologyManager(session=self.session)
        self.json_handler = ISAJSONHandler()
        self.neo4j_importer = ISANeo4jImporter()
    
    # Ontology management methods
    
    def import_ontology(self, url: str, destination_path: Optional[str] = None) -> Tuple[bool, Union[rdflib.Graph, str]]:
        """
        Import an RDF/OWL ontology from a URL.
        
        Args:
            url: The URL of the ontology to import.
            destination_path: Optional path to save the ontology file.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the import was successful, False otherwise.
            - result: The imported ontology graph if successful, or an error message if not.
        """
        return self.ontology_manager.import_ontology(url, destination_path)
    
    def select_ontology_subset(self, graph: rdflib.Graph, root_nodes: List[str], max_depth: int = 3) -> Tuple[bool, Union[rdflib.Graph, str]]:
        """
        Select a subset of an ontology based on root nodes and maximum depth.
        
        Args:
            graph: The ontology graph.
            root_nodes: List of root node URIs to include in the subset.
            max_depth: Maximum depth of relationships to include.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the selection was successful, False otherwise.
            - result: The selected ontology subset if successful, or an error message if not.
        """
        return self.ontology_manager.select_ontology_subset(graph, root_nodes, max_depth)
    
    def export_ontology(self, graph: rdflib.Graph, destination_path: str, format: str = "xml") -> Tuple[bool, str]:
        """
        Export an ontology graph to a file.
        
        Args:
            graph: The ontology graph to export.
            destination_path: Path to save the ontology file.
            format: Format to use for the export (xml, turtle, n3, etc.).
            
        Returns:
            A tuple containing (success, message).
            - success: True if the export was successful, False otherwise.
            - message: A message describing the result.
        """
        return self.ontology_manager.export_ontology(graph, destination_path, format)
    
    # ISA JSON handling methods
    
    def import_isa_json(self, file_path: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Import ISA metadata from a JSON file.
        
        Args:
            file_path: The path to the ISA JSON file.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the import was successful, False otherwise.
            - result: The imported metadata if successful, or an error message if not.
        """
        return self.json_handler.import_isa_json(file_path)
    
    def search(self, query: str, data: Dict[str, Any]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Search for resources in ISA metadata.
        
        Args:
            query: The search query.
            data: The data to search in.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the search was successful, False otherwise.
            - result: The search results if successful, or an error message if not.
        """
        return self.json_handler.search(query, data)
    
    # Neo4j integration methods
    
    def import_to_neo4j(self, data: Dict[str, Any], db_manager: Any) -> Tuple[bool, str]:
        """
        Import ISA metadata into Neo4j.
        
        Args:
            data: The ISA metadata to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        return self.neo4j_importer.import_to_neo4j(data, db_manager)
    
    def import_ontology_to_neo4j(self, graph: rdflib.Graph, db_manager: Any) -> Tuple[bool, str]:
        """
        Import an ontology graph into Neo4j.
        
        Args:
            graph: The ontology graph to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        return self.neo4j_importer.import_ontology_to_neo4j(graph, db_manager)
    
    # Convenience methods
    
    def process_and_import(self, file_path: str, db_manager: Any) -> Tuple[bool, str]:
        """
        Process an ISA JSON file and import it into Neo4j.
        
        This is a convenience method that combines import_isa_json and import_to_neo4j.
        
        Args:
            file_path: The path to the ISA JSON file.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the process was successful, False otherwise.
            - message: A message describing the result.
        """
        # Import the ISA JSON file
        success, result = self.import_isa_json(file_path)
        if not success:
            return False, result
        
        # Import the data into Neo4j
        return self.import_to_neo4j(result, db_manager)