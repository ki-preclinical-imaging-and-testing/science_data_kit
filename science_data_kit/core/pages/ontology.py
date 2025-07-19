"""
Ontology Page Module for Science Data Kit

This module provides the core functionality for the Ontology browser page,
allowing users to browse, manage, and upload ontology terms.
"""

from typing import Dict, Any, Optional, List, Union
import pandas as pd
from pathlib import Path

from science_data_kit.core.db.db_manager import Neo4jManager, load_db_config
from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation, OntologySource, get_isa_objects
from science_data_kit.core.ontology.browser import OntologyBrowser
from science_data_kit.core.pages.base import BasePage

class OntologyPage(BasePage):
    """
    Core functionality for the Ontology browser page.

    This class provides the backend functionality for browsing and managing
    ontology terms, including connecting to Neo4j, loading terms, and
    visualizing ontology hierarchies.
    """

    def __init__(self):
        """Initialize the Ontology page."""
        super().__init__(title="Ontology Browser", icon="🧬")

        # Initialize state
        self.terms = []
        self.neo4j_manager = None
        self.neo4j_connected = False
        self.available_labels = []
        self.ontology_browser = None
        self.existing_term_accessions = set()

    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to a Neo4j database.

        Args:
            uri: The URI of the Neo4j database
            username: The username for authentication
            password: The password for authentication
            database: The name of the database
            conn_name: Optional name for the connection

        Returns:
            A dictionary with the result of the connection attempt
        """
        try:
            neo4j_config = {
                "uri": uri,
                "user": username,
                "password": password,
                "database": database
            }

            # Create a new connection
            manager = Neo4jManager(**neo4j_config)

            # Test the connection
            if manager.test_connection():
                self.neo4j_manager = manager
                self.neo4j_connected = True

                # Store connection info for session
                self.neo4j_connection = {
                    "uri": uri,
                    "user": username,
                    "password": password,
                    "database": database,
                    "conn_name": conn_name or "Neo4j"
                }

                # Fetch available labels from Neo4j
                try:
                    labels = manager.fetch_labels()
                    self.available_labels = labels

                    # Add Neo4j labels to terms as a "Local" ontology
                    self._add_labels_as_terms(labels)
                except Exception as e:
                    return {"success": True, "warning": f"Connected, but couldn't fetch labels: {str(e)}"}

                # Create ontology browser
                self.ontology_browser = OntologyBrowser(manager)

                return {"success": True}
            else:
                return {"success": False, "error": "Failed to connect to Neo4j"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the Neo4j database.

        Returns:
            A dictionary with the result of the disconnection attempt
        """
        try:
            if self.neo4j_manager:
                self.neo4j_manager.close()
                self.neo4j_manager = None
                self.neo4j_connected = False
                self.neo4j_connection = None
                self.ontology_browser = None
                return {"success": True}
            return {"success": True, "warning": "No active connection"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the ontologies in the database.

        Returns:
            A dictionary containing statistics about the ontologies
        """
        if not self.neo4j_connected or not self.ontology_browser:
            return {"success": False, "error": "Not connected to Neo4j"}

        try:
            stats = self.ontology_browser.get_statistics()
            return {"success": True, "statistics": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_terms(self, search_term: str) -> Dict[str, Any]:
        """
        Search for ontology terms in the database.

        Args:
            search_term: The term to search for

        Returns:
            A dictionary with the search results
        """
        if not self.neo4j_connected or not self.ontology_browser:
            return {"success": False, "error": "Not connected to Neo4j"}

        try:
            results = self.ontology_browser.search_terms(search_term)
            return {"success": True, "results": results.to_dict(orient="records")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_term_hierarchy(self, term: str) -> Dict[str, Any]:
        """
        Get the hierarchy for a specific ontology term.

        Args:
            term: The term to get the hierarchy for

        Returns:
            A dictionary with the hierarchy data
        """
        if not self.neo4j_connected or not self.ontology_browser:
            return {"success": False, "error": "Not connected to Neo4j"}

        try:
            hierarchy = self.ontology_browser.get_term_hierarchy(term)
            return {"success": True, "hierarchy": hierarchy.to_dict(orient="records")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_standard_isa_terms(self) -> List[OntologyAnnotation]:
        """
        Get standard ISA terms.

        Returns:
            List of OntologyAnnotation objects
        """
        # Create OBI ontology source
        obi_source = OntologySource(
            name="OBI",
            file="http://purl.obolibrary.org/obo/obi.owl",
            version="2021-10-11",
            description="Ontology for Biomedical Investigations"
        )

        # Create PATO ontology source
        pato_source = OntologySource(
            name="PATO",
            file="http://purl.obolibrary.org/obo/pato.owl",
            version="2021-10-11",
            description="Phenotype And Trait Ontology"
        )

        # Create standard terms
        terms = [
            # Study design terms
            OntologyAnnotation(term="intervention design", term_accession="http://purl.obolibrary.org/obo/OBI_0000115", term_source=obi_source),
            OntologyAnnotation(term="observational design", term_accession="http://purl.obolibrary.org/obo/OBI_0000071", term_source=obi_source),
            OntologyAnnotation(term="cross-over design", term_accession="http://purl.obolibrary.org/obo/OBI_0000684", term_source=obi_source),
            OntologyAnnotation(term="parallel group design", term_accession="http://purl.obolibrary.org/obo/OBI_0000685", term_source=obi_source),

            # Material type terms
            OntologyAnnotation(term="organism", term_accession="http://purl.obolibrary.org/obo/OBI_0100026", term_source=obi_source),
            OntologyAnnotation(term="specimen", term_accession="http://purl.obolibrary.org/obo/OBI_0100051", term_source=obi_source),
            OntologyAnnotation(term="extract", term_accession="http://purl.obolibrary.org/obo/OBI_0000423", term_source=obi_source),

            # Characteristic categories
            OntologyAnnotation(term="age", term_accession="http://purl.obolibrary.org/obo/PATO_0000011", term_source=pato_source),
            OntologyAnnotation(term="sex", term_accession="http://purl.obolibrary.org/obo/PATO_0000047", term_source=pato_source),
            OntologyAnnotation(term="organism part", term_accession="http://purl.obolibrary.org/obo/OBI_0000066", term_source=obi_source),

            # Protocol type terms
            OntologyAnnotation(term="sample collection", term_accession="http://purl.obolibrary.org/obo/OBI_0000659", term_source=obi_source),
        ]

        return terms

    def add_standard_isa_terms(self) -> Dict[str, Any]:
        """
        Add standard ISA terms to the terms list.

        Returns:
            A dictionary with the result of the operation
        """
        try:
            standard_terms = self._get_standard_isa_terms()

            # Add only new terms that don't exist yet
            added_count = 0
            for term in standard_terms:
                if term.term_accession not in self.existing_term_accessions:
                    self.terms.append(term)
                    self.existing_term_accessions.add(term.term_accession)
                    added_count += 1

            if added_count > 0:
                return {"success": True, "message": f"Added {added_count} standard ISA terms."}
            else:
                return {"success": True, "message": "All standard terms are already loaded."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _add_labels_as_terms(self, labels: List[str]) -> None:
        """
        Add Neo4j labels to terms as a "Local" ontology.

        Args:
            labels: List of Neo4j labels
        """
        try:
            # Create a proper OntologySource object for Neo4j labels
            local_source = None
            try:
                # Check if we already have a Local ontology source
                for term in self.terms:
                    if hasattr(term.term_source, 'name') and term.term_source.name == "Local":
                        local_source = term.term_source
                        break

                # If not found, create a new one
                if not local_source:
                    local_source = OntologySource(
                        name="Local",
                        file="",
                        version="1.0",
                        description="Neo4j database labels and local terms"
                    )
            except Exception:
                # Fallback to string if OntologySource creation fails
                local_source = "Local"

            # Add Neo4j labels to terms as a "Local" ontology
            local_terms = []
            for label in labels:
                if label and isinstance(label, str):
                    local_terms.append(OntologyAnnotation(
                        term=label,
                        term_accession=f"neo4j:label:{label}",
                        term_source=local_source
                    ))

            # Add local terms to terms list if they don't exist yet
            added_count = 0
            for term in local_terms:
                if term.term_accession not in self.existing_term_accessions:
                    self.terms.append(term)
                    self.existing_term_accessions.add(term.term_accession)
                    added_count += 1
        except Exception:
            pass  # Silently fail, this is not critical

    def add_term(self, term_name: str, term_uri: str, ontology_source: str) -> Dict[str, Any]:
        """
        Add a new term to the terms list.

        Args:
            term_name: The name of the term
            term_uri: The URI of the term
            ontology_source: The source of the term

        Returns:
            A dictionary with the result of the operation
        """
        try:
            if not term_name or not term_uri or not ontology_source:
                return {"success": False, "error": "Term name, URI, and source are required"}

            new_term = OntologyAnnotation(
                term=term_name,
                term_accession=term_uri,
                term_source=ontology_source
            )

            # Check if term already exists
            if term_uri not in self.existing_term_accessions:
                self.terms.append(new_term)
                self.existing_term_accessions.add(term_uri)
                return {"success": True, "message": f"Added new term: {term_name}"}
            else:
                return {"success": False, "error": f"Term with URI {term_uri} already exists."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def push_terms_to_neo4j(self) -> Dict[str, Any]:
        """
        Push terms to Neo4j.

        Returns:
            A dictionary with the result of the operation
        """
        if not self.neo4j_connected or not self.neo4j_manager:
            return {"success": False, "error": "Not connected to Neo4j"}

        if not self.terms:
            return {"success": False, "error": "No terms to push to Neo4j"}

        try:
            # Use the Neo4j manager to load ontology relationships
            self.neo4j_manager.load_ontology_relationships(
                self.terms,
                create_source_nodes=True
            )
            return {"success": True, "message": f"Successfully pushed {len(self.terms)} terms to Neo4j."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def clear_terms(self) -> Dict[str, Any]:
        """
        Clear all terms from the terms list.

        Returns:
            A dictionary with the result of the operation
        """
        try:
            count = len(self.terms)
            self.terms = []
            self.existing_term_accessions = set()
            return {"success": True, "message": f"Cleared {count} terms."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_terms(self) -> Dict[str, Any]:
        """
        Get all terms.

        Returns:
            A dictionary with the terms
        """
        try:
            # Convert terms to dictionaries for JSON serialization
            terms_data = []
            for term in self.terms:
                source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
                terms_data.append({
                    "term": term.term,
                    "term_accession": term.term_accession,
                    "term_source": source_name
                })

            return {"success": True, "terms": terms_data}
        except Exception as e:
            return {"success": False, "error": str(e)}
