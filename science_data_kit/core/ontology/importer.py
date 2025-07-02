"""
Ontology importer for Science Data Kit.

This module provides functionality for importing ontologies into Neo4j using the neosemantics (n10s) plugin.
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from pathlib import Path
import urllib.request
import urllib.parse
import os
import tempfile
import logging
import rdflib
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology.models import OntologySource, OntologyAnnotation

logger = logging.getLogger(__name__)


class OntologyImporter:
    """
    A class for importing ontologies into Neo4j using the neosemantics (n10s) plugin.

    This class provides functionality for importing ontologies from various sources
    (local files, URLs) and in various formats (OWL, Turtle, RDF/XML, JSON-LD) into Neo4j.
    It uses the neosemantics (n10s) plugin to import RDF data into Neo4j.

    Attributes:
        db_manager: The Neo4j database manager to use for importing ontologies.
        n10s_available: Whether the neosemantics plugin is available.
    """

    def __init__(self, db_manager: Neo4jManager):
        """
        Initialize the OntologyImporter.

        Args:
            db_manager: The Neo4j database manager to use for importing ontologies.
        """
        self.db_manager = db_manager
        self.n10s_available = self._check_n10s_available()

    def _check_n10s_available(self) -> bool:
        """
        Check if the neosemantics (n10s) plugin is available in the Neo4j instance.

        Returns:
            True if the plugin is available, False otherwise.
        """
        try:
            # Check if the n10s.version procedure is available
            query = "CALL n10s.version()"
            result = self.db_manager.execute_query(query)

            if result and len(result) > 0:
                version = result[0].get("version", "")
                logger.info(f"Neosemantics (n10s) plugin version {version} is available")
                return True
            else:
                logger.warning("Neosemantics (n10s) plugin is not available")
                return False
        except Exception as e:
            logger.warning(f"Error checking for neosemantics plugin: {e}")
            return False

    def _initialize_n10s(self) -> bool:
        """
        Initialize the neosemantics (n10s) plugin.

        This method creates the necessary constraints and indexes for the neosemantics plugin.

        Returns:
            True if the initialization was successful, False otherwise.
        """
        if not self.n10s_available:
            logger.warning("Cannot initialize neosemantics plugin: Plugin is not available")
            return False

        try:
            # Create constraint on resource URI
            query = "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE"
            self.db_manager.execute_query(query)

            # Initialize the graph configuration
            query = """
            CALL n10s.graphconfig.init({
                handleVocabUris: 'MAP',
                handleMultival: 'ARRAY',
                keepLangTag: true,
                handleRDFTypes: 'LABELS'
            })
            """
            self.db_manager.execute_query(query)

            logger.info("Neosemantics plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing neosemantics plugin: {e}")
            return False

    def load_ontology(self, source: Union[str, Path]) -> bool:
        """
        Load an ontology from a file or URL into Neo4j.

        Args:
            source: The path to the ontology file or URL.

        Returns:
            True if the ontology was loaded successfully, False otherwise.

        Raises:
            FileNotFoundError: If the source file does not exist.
            ValueError: If the source format is not supported.
        """
        # Convert Path to string if needed
        if isinstance(source, Path):
            source = str(source)

        # Check if source is a URL or a local file
        if source.startswith(('http://', 'https://')):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)

    def _load_from_file(self, file_path: str) -> bool:
        """
        Load an ontology from a local file.

        Args:
            file_path: The path to the ontology file.

        Returns:
            True if the ontology was loaded successfully, False otherwise.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file format based on extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Check if neosemantics plugin is available
        if not self.n10s_available:
            logger.warning("Neosemantics plugin is not available. Using fallback method.")
            return self._load_from_file_fallback(file_path, ext)

        # Initialize neosemantics plugin
        if not self._initialize_n10s():
            logger.warning("Failed to initialize neosemantics plugin. Using fallback method.")
            return self._load_from_file_fallback(file_path, ext)

        try:
            # Determine RDF format based on file extension
            rdf_format = self._get_rdf_format(ext)

            # Import the ontology using neosemantics
            query = """
            CALL n10s.onto.import.fetch($file, $format)
            YIELD terminationStatus, triplesLoaded, triplesParsed, namespaces, extraInfo
            RETURN terminationStatus, triplesLoaded, triplesParsed, namespaces, extraInfo
            """

            params = {
                "file": f"file://{os.path.abspath(file_path)}",
                "format": rdf_format
            }

            result = self.db_manager.execute_query(query, params)

            if result and len(result) > 0:
                status = result[0].get("terminationStatus", "")
                triples_loaded = result[0].get("triplesLoaded", 0)
                triples_parsed = result[0].get("triplesParsed", 0)

                logger.info(f"Ontology loaded from file: {file_path}")
                logger.info(f"Status: {status}, Triples loaded: {triples_loaded}, Triples parsed: {triples_parsed}")

                # Create an OntologySource object for the imported ontology
                source_name = os.path.basename(file_path)
                self._create_ontology_source(source_name, file_path)

                return status == "OK" and triples_loaded > 0
            else:
                logger.warning(f"Failed to load ontology from file: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Error loading ontology from file: {e}")
            return False

    def _load_from_url(self, url: str) -> bool:
        """
        Load an ontology from a URL.

        Args:
            url: The URL of the ontology.

        Returns:
            True if the ontology was loaded successfully, False otherwise.

        Raises:
            ValueError: If the URL format is not supported.
        """
        # Check if neosemantics plugin is available
        if not self.n10s_available:
            logger.warning("Neosemantics plugin is not available. Using fallback method.")
            return self._load_from_url_fallback(url)

        # Initialize neosemantics plugin
        if not self._initialize_n10s():
            logger.warning("Failed to initialize neosemantics plugin. Using fallback method.")
            return self._load_from_url_fallback(url)

        try:
            # Determine RDF format based on URL extension or content type
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            _, ext = os.path.splitext(path)
            ext = ext.lower()

            rdf_format = self._get_rdf_format(ext)

            # Import the ontology using neosemantics
            query = """
            CALL n10s.onto.import.fetch($url, $format)
            YIELD terminationStatus, triplesLoaded, triplesParsed, namespaces, extraInfo
            RETURN terminationStatus, triplesLoaded, triplesParsed, namespaces, extraInfo
            """

            params = {
                "url": url,
                "format": rdf_format
            }

            result = self.db_manager.execute_query(query, params)

            if result and len(result) > 0:
                status = result[0].get("terminationStatus", "")
                triples_loaded = result[0].get("triplesLoaded", 0)
                triples_parsed = result[0].get("triplesParsed", 0)

                logger.info(f"Ontology loaded from URL: {url}")
                logger.info(f"Status: {status}, Triples loaded: {triples_loaded}, Triples parsed: {triples_parsed}")

                # Create an OntologySource object for the imported ontology
                source_name = os.path.basename(path) or parsed_url.netloc
                self._create_ontology_source(source_name, url)

                return status == "OK" and triples_loaded > 0
            else:
                logger.warning(f"Failed to load ontology from URL: {url}")
                return False

        except Exception as e:
            logger.error(f"Error loading ontology from URL: {e}")
            return False

    def _get_rdf_format(self, ext: str) -> str:
        """
        Get the RDF format based on the file extension.

        Args:
            ext: The file extension.

        Returns:
            The RDF format string for neosemantics.
        """
        formats = {
            ".owl": "RDF/XML",
            ".rdf": "RDF/XML",
            ".ttl": "Turtle",
            ".nt": "N-Triples",
            ".n3": "N3",
            ".jsonld": "JSON-LD"
        }

        return formats.get(ext, "RDF/XML")

    def _create_ontology_source(self, name: str, file: str) -> None:
        """
        Create an OntologySource object for the imported ontology.

        Args:
            name: The name of the ontology source.
            file: The file path or URL of the ontology source.
        """
        # Create a query to store the ontology source information
        query = """
        MERGE (s:OntologySource {name: $name})
        ON CREATE SET s.created = timestamp()
        SET s.file = $file,
            s.last_updated = timestamp()
        RETURN s
        """

        params = {
            "name": name,
            "file": file
        }

        self.db_manager.execute_query(query, params)

    def _load_from_file_fallback(self, file_path: str, ext: str) -> bool:
        """
        Fallback method for loading an ontology from a file when neosemantics is not available.

        Args:
            file_path: The path to the ontology file.
            ext: The file extension.

        Returns:
            True if the ontology was loaded successfully, False otherwise.
        """
        logger.info(f"Using fallback method to load ontology from file: {file_path}")

        try:
            # Parse the ontology file using rdflib
            g = Graph()
            rdf_format = self._get_rdflib_format(ext)
            g.parse(file_path, format=rdf_format)

            # Extract ontology information
            ontology_classes = self._extract_ontology_classes(g)
            ontology_properties = self._extract_ontology_properties(g)

            # Create nodes and relationships in Neo4j
            self._create_ontology_nodes(g, ontology_classes, ontology_properties)

            # Create an OntologySource object for the imported ontology
            source_name = os.path.basename(file_path)
            self._create_ontology_source(source_name, file_path)

            return True

        except Exception as e:
            logger.error(f"Error in fallback method for loading ontology from file: {e}")
            return False

    def _load_from_url_fallback(self, url: str) -> bool:
        """
        Fallback method for loading an ontology from a URL when neosemantics is not available.

        Args:
            url: The URL of the ontology.

        Returns:
            True if the ontology was loaded successfully, False otherwise.
        """
        logger.info(f"Using fallback method to load ontology from URL: {url}")

        try:
            # Download the ontology file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                urllib.request.urlretrieve(url, temp_file.name)

                # Determine file format based on URL extension
                parsed_url = urllib.parse.urlparse(url)
                path = parsed_url.path
                _, ext = os.path.splitext(path)
                ext = ext.lower()

                # Load the ontology from the temporary file
                result = self._load_from_file_fallback(temp_file.name, ext)

                # Clean up the temporary file
                os.unlink(temp_file.name)

                return result

        except Exception as e:
            logger.error(f"Error in fallback method for loading ontology from URL: {e}")
            return False

    def _get_rdflib_format(self, ext: str) -> str:
        """
        Get the RDF format for rdflib based on the file extension.

        Args:
            ext: The file extension.

        Returns:
            The RDF format string for rdflib.
        """
        formats = {
            ".owl": "xml",
            ".rdf": "xml",
            ".ttl": "turtle",
            ".nt": "nt",
            ".n3": "n3",
            ".jsonld": "json-ld"
        }

        return formats.get(ext, "xml")

    def _extract_ontology_classes(self, g: Graph) -> List[Dict[str, Any]]:
        """
        Extract ontology classes from an RDF graph.

        Args:
            g: The RDF graph.

        Returns:
            A list of dictionaries containing class information.
        """
        classes = []

        # Find all classes (owl:Class or rdfs:Class)
        for s in g.subjects(RDF.type, OWL.Class):
            class_info = {
                "uri": str(s),
                "label": self._get_label(g, s),
                "comment": self._get_comment(g, s),
                "subClassOf": [str(o) for o in g.objects(s, RDFS.subClassOf)]
            }
            classes.append(class_info)

        for s in g.subjects(RDF.type, RDFS.Class):
            if not any(c["uri"] == str(s) for c in classes):
                class_info = {
                    "uri": str(s),
                    "label": self._get_label(g, s),
                    "comment": self._get_comment(g, s),
                    "subClassOf": [str(o) for o in g.objects(s, RDFS.subClassOf)]
                }
                classes.append(class_info)

        return classes

    def _extract_ontology_properties(self, g: Graph) -> List[Dict[str, Any]]:
        """
        Extract ontology properties from an RDF graph.

        Args:
            g: The RDF graph.

        Returns:
            A list of dictionaries containing property information.
        """
        properties = []

        # Find all properties (owl:ObjectProperty, owl:DatatypeProperty, rdf:Property)
        for prop_type in [OWL.ObjectProperty, OWL.DatatypeProperty, RDF.Property]:
            for s in g.subjects(RDF.type, prop_type):
                prop_info = {
                    "uri": str(s),
                    "label": self._get_label(g, s),
                    "comment": self._get_comment(g, s),
                    "domain": [str(o) for o in g.objects(s, RDFS.domain)],
                    "range": [str(o) for o in g.objects(s, RDFS.range)],
                    "type": str(prop_type)
                }
                properties.append(prop_info)

        return properties

    def _get_label(self, g: Graph, s: URIRef) -> str:
        """
        Get the label of a resource from an RDF graph.

        Args:
            g: The RDF graph.
            s: The resource URI.

        Returns:
            The label of the resource, or the local name if no label is found.
        """
        labels = list(g.objects(s, RDFS.label))
        if labels:
            return str(labels[0])
        else:
            # Extract local name from URI
            uri = str(s)
            if '#' in uri:
                return uri.split('#')[-1]
            else:
                return uri.split('/')[-1]

    def _get_comment(self, g: Graph, s: URIRef) -> str:
        """
        Get the comment of a resource from an RDF graph.

        Args:
            g: The RDF graph.
            s: The resource URI.

        Returns:
            The comment of the resource, or an empty string if no comment is found.
        """
        comments = list(g.objects(s, RDFS.comment))
        if comments:
            return str(comments[0])
        else:
            return ""

    def _create_ontology_nodes(self, g: Graph, classes: List[Dict[str, Any]], properties: List[Dict[str, Any]]) -> None:
        """
        Create nodes and relationships in Neo4j for the ontology.

        Args:
            g: The RDF graph.
            classes: A list of dictionaries containing class information.
            properties: A list of dictionaries containing property information.
        """
        # Create class nodes
        for class_info in classes:
            query = """
            MERGE (c:OntologyClass {uri: $uri})
            ON CREATE SET c.created = timestamp()
            SET c.label = $label,
                c.comment = $comment,
                c.last_updated = timestamp()
            RETURN c
            """

            params = {
                "uri": class_info["uri"],
                "label": class_info["label"],
                "comment": class_info["comment"]
            }

            self.db_manager.execute_query(query, params)

            # Create subclass relationships
            for superclass_uri in class_info["subClassOf"]:
                query = """
                MATCH (c:OntologyClass {uri: $uri})
                MERGE (s:OntologyClass {uri: $superclass_uri})
                MERGE (c)-[r:SUBCLASS_OF]->(s)
                RETURN r
                """

                params = {
                    "uri": class_info["uri"],
                    "superclass_uri": superclass_uri
                }

                self.db_manager.execute_query(query, params)

        # Create property nodes
        for prop_info in properties:
            query = """
            MERGE (p:OntologyProperty {uri: $uri})
            ON CREATE SET p.created = timestamp()
            SET p.label = $label,
                p.comment = $comment,
                p.type = $type,
                p.last_updated = timestamp()
            RETURN p
            """

            params = {
                "uri": prop_info["uri"],
                "label": prop_info["label"],
                "comment": prop_info["comment"],
                "type": prop_info["type"]
            }

            self.db_manager.execute_query(query, params)

            # Create domain relationships
            for domain_uri in prop_info["domain"]:
                query = """
                MATCH (p:OntologyProperty {uri: $uri})
                MERGE (c:OntologyClass {uri: $domain_uri})
                MERGE (p)-[r:HAS_DOMAIN]->(c)
                RETURN r
                """

                params = {
                    "uri": prop_info["uri"],
                    "domain_uri": domain_uri
                }

                self.db_manager.execute_query(query, params)

            # Create range relationships
            for range_uri in prop_info["range"]:
                query = """
                MATCH (p:OntologyProperty {uri: $uri})
                MERGE (c:OntologyClass {uri: $range_uri})
                MERGE (p)-[r:HAS_RANGE]->(c)
                RETURN r
                """

                params = {
                    "uri": prop_info["uri"],
                    "range_uri": range_uri
                }

                self.db_manager.execute_query(query, params)
