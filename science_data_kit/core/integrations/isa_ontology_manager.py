"""
ISA Ontology Manager for Science Data Kit

This module provides functionality for managing ontologies in the ISA Tools integration,
allowing users to import, export, and manipulate RDF/OWL ontologies.
"""

import requests
import rdflib
from typing import Dict, List, Optional, Any, Tuple, Union

class ISAOntologyManager:
    """
    Manager for ontology-related operations in the ISA Tools integration.

    This class provides methods for importing RDF/OWL ontologies,
    selecting ontology subsets, and exporting ontologies.

    Attributes:
        session: The requests session for making HTTP requests.
    """

    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize the ISA Ontology Manager.

        Args:
            session: Optional requests session to use for HTTP requests.
                    If not provided, a new session will be created.
        """
        self.session = session if session is not None else requests.Session()

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
        try:
            # Download the ontology
            response = self.session.get(url)

            if response.status_code != 200:
                return False, f"Failed to download ontology: {response.status_code} - {response.text}"

            # Save the ontology to a file if a destination path is provided
            if destination_path:
                with open(destination_path, 'wb') as f:
                    f.write(response.content)

            # Parse the ontology into an RDF graph
            g = rdflib.Graph()
            g.parse(data=response.content, format="xml")

            return True, g

        except Exception as e:
            return False, f"Error importing ontology: {str(e)}"

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
        try:
            # Create a new graph for the subset
            subset = rdflib.Graph()

            # Add the root nodes to the subset
            for root_node in root_nodes:
                # Convert string to URIRef
                root_uri = rdflib.URIRef(root_node)

                # Add all triples where the root node is the subject
                self._add_node_with_depth(graph, subset, root_uri, max_depth)

            return True, subset

        except Exception as e:
            return False, f"Error selecting ontology subset: {str(e)}"

    def _add_node_with_depth(self, source_graph: rdflib.Graph, target_graph: rdflib.Graph, node: rdflib.URIRef, depth: int, visited: Optional[set] = None) -> None:
        """
        Recursively add a node and its relationships to the target graph up to a specified depth.

        Args:
            source_graph: The source ontology graph.
            target_graph: The target ontology graph.
            node: The node to add.
            depth: The maximum depth of relationships to include.
            visited: Set of already visited nodes to prevent cycles.
        """
        if depth <= 0:
            return

        if visited is None:
            visited = set()

        if node in visited:
            return

        visited.add(node)

        # Add all triples where the node is the subject
        for s, p, o in source_graph.triples((node, None, None)):
            target_graph.add((s, p, o))

            # If the object is a URI, recursively add it
            if isinstance(o, rdflib.URIRef):
                self._add_node_with_depth(source_graph, target_graph, o, depth - 1, visited)

        # Add all triples where the node is the object
        for s, p, o in source_graph.triples((None, None, node)):
            target_graph.add((s, p, o))

            # If the subject is a URI, recursively add it
            if isinstance(s, rdflib.URIRef):
                self._add_node_with_depth(source_graph, target_graph, s, depth - 1, visited)

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
        try:
            # Serialize the graph to the specified format
            graph.serialize(destination=destination_path, format=format)

            return True, f"Ontology exported to {destination_path} in {format} format"

        except Exception as e:
            return False, f"Error exporting ontology: {str(e)}"
