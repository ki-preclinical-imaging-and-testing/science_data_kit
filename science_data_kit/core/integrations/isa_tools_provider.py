"""
ISA Tools Integration Provider for Science Data Kit

This module provides integration with the ISA Tools platform,
allowing users to access and analyze experimental metadata from ISA Tools
within the Science Data Kit environment.

ISA (Investigation, Study, Assay) is a framework for describing and managing
experimental metadata in life sciences.
"""

import os
import json
import requests
import rdflib
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

class ISAToolsProvider:
    """
    Provider for integrating with the ISA Tools platform.
    
    This class provides methods for importing RDF/OWL ontologies,
    selecting ontology subsets, retrieving experimental metadata,
    and importing data into Neo4j.
    
    Attributes:
        base_url: The base URL of the ISA Tools API (if applicable).
        api_key: The API key for authenticating with ISA Tools API (if applicable).
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
        self.session = requests.Session()
        
        # Set up authentication if credentials are provided
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
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
        try:
            # Check if the file exists
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return True, data
        
        except json.JSONDecodeError:
            return False, f"Invalid JSON file: {file_path}"
        except Exception as e:
            return False, f"Error importing ISA JSON file: {str(e)}"
    
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
        try:
            # Create nodes for investigations
            if "investigation" in data:
                investigation = data["investigation"]
                investigation_query = """
                MERGE (i:Investigation:ISA {id: $id})
                SET i.title = $title,
                    i.description = $description,
                    i.submissionDate = $submissionDate,
                    i.publicReleaseDate = $publicReleaseDate,
                    i.source = 'ISA Tools'
                RETURN i
                """
                investigation_params = {
                    "id": investigation.get("identifier", ""),
                    "title": investigation.get("title", ""),
                    "description": investigation.get("description", ""),
                    "submissionDate": investigation.get("submissionDate", ""),
                    "publicReleaseDate": investigation.get("publicReleaseDate", ""),
                }
                db_manager.execute_query(investigation_query, params=investigation_params)
                
                # Create nodes for studies and link to investigation
                if "studies" in investigation:
                    for study in investigation["studies"]:
                        study_query = """
                        MERGE (s:Study:ISA {id: $id})
                        SET s.title = $title,
                            s.description = $description,
                            s.submissionDate = $submissionDate,
                            s.publicReleaseDate = $publicReleaseDate,
                            s.source = 'ISA Tools'
                        WITH s
                        MATCH (i:Investigation:ISA {id: $investigationId})
                        MERGE (i)-[:HAS_STUDY]->(s)
                        RETURN s
                        """
                        study_params = {
                            "id": study.get("identifier", ""),
                            "title": study.get("title", ""),
                            "description": study.get("description", ""),
                            "submissionDate": study.get("submissionDate", ""),
                            "publicReleaseDate": study.get("publicReleaseDate", ""),
                            "investigationId": investigation.get("identifier", "")
                        }
                        db_manager.execute_query(study_query, params=study_params)
                        
                        # Create nodes for assays and link to study
                        if "assays" in study:
                            for assay in study["assays"]:
                                assay_query = """
                                MERGE (a:Assay:ISA {id: $id})
                                SET a.measurementType = $measurementType,
                                    a.technologyType = $technologyType,
                                    a.technologyPlatform = $technologyPlatform,
                                    a.source = 'ISA Tools'
                                WITH a
                                MATCH (s:Study:ISA {id: $studyId})
                                MERGE (s)-[:HAS_ASSAY]->(a)
                                RETURN a
                                """
                                assay_params = {
                                    "id": assay.get("identifier", ""),
                                    "measurementType": assay.get("measurementType", {}).get("annotationValue", ""),
                                    "technologyType": assay.get("technologyType", {}).get("annotationValue", ""),
                                    "technologyPlatform": assay.get("technologyPlatform", ""),
                                    "studyId": study.get("identifier", "")
                                }
                                db_manager.execute_query(assay_query, params=assay_params)
                                
                                # Create nodes for data files and link to assay
                                if "dataFiles" in assay:
                                    for data_file in assay["dataFiles"]:
                                        data_file_query = """
                                        MERGE (d:DataFile:ISA {id: $id})
                                        SET d.name = $name,
                                            d.type = $type,
                                            d.source = 'ISA Tools'
                                        WITH d
                                        MATCH (a:Assay:ISA {id: $assayId})
                                        MERGE (a)-[:HAS_DATA_FILE]->(d)
                                        RETURN d
                                        """
                                        data_file_params = {
                                            "id": data_file.get("identifier", ""),
                                            "name": data_file.get("name", ""),
                                            "type": data_file.get("type", ""),
                                            "assayId": assay.get("identifier", "")
                                        }
                                        db_manager.execute_query(data_file_query, params=data_file_params)
            
            return True, "ISA metadata imported successfully"
        
        except Exception as e:
            return False, f"Error importing ISA metadata: {str(e)}"
    
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
        try:
            # Count the number of triples in the graph
            triple_count = len(graph)
            
            # Create a batch of triples to import
            batch_size = 1000
            batches = [list(graph)[i:i + batch_size] for i in range(0, triple_count, batch_size)]
            
            # Import each batch
            for batch in batches:
                # Convert the batch to a format suitable for Neo4j
                neo4j_batch = []
                for s, p, o in batch:
                    # Convert URIs to strings
                    subject = str(s)
                    predicate = str(p)
                    
                    # Handle different types of objects
                    if isinstance(o, rdflib.URIRef):
                        object_type = "uri"
                        object_value = str(o)
                    elif isinstance(o, rdflib.Literal):
                        object_type = "literal"
                        object_value = str(o)
                        object_datatype = str(o.datatype) if o.datatype else None
                        object_language = o.language if o.language else None
                    else:
                        object_type = "other"
                        object_value = str(o)
                    
                    # Add the triple to the batch
                    neo4j_triple = {
                        "subject": subject,
                        "predicate": predicate,
                        "object_type": object_type,
                        "object_value": object_value
                    }
                    
                    # Add datatype and language if available
                    if object_type == "literal":
                        if object_datatype:
                            neo4j_triple["object_datatype"] = object_datatype
                        if object_language:
                            neo4j_triple["object_language"] = object_language
                    
                    neo4j_batch.append(neo4j_triple)
                
                # Import the batch into Neo4j
                for triple in neo4j_batch:
                    if triple["object_type"] == "uri":
                        # Create nodes for subject and object, and a relationship for predicate
                        query = """
                        MERGE (s:OntologyNode:ISA {uri: $subject})
                        MERGE (o:OntologyNode:ISA {uri: $object_value})
                        MERGE (s)-[r:ONTOLOGY_RELATION {uri: $predicate}]->(o)
                        RETURN s, r, o
                        """
                        params = {
                            "subject": triple["subject"],
                            "predicate": triple["predicate"],
                            "object_value": triple["object_value"]
                        }
                    else:
                        # Create a node for subject and set a property for the literal
                        query = """
                        MERGE (s:OntologyNode:ISA {uri: $subject})
                        SET s.`$predicate` = $object_value
                        RETURN s
                        """
                        params = {
                            "subject": triple["subject"],
                            "predicate": triple["predicate"],
                            "object_value": triple["object_value"]
                        }
                    
                    db_manager.execute_query(query, params=params)
            
            return True, f"Imported {triple_count} triples into Neo4j"
        
        except Exception as e:
            return False, f"Error importing ontology to Neo4j: {str(e)}"
    
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
        try:
            results = []
            
            # Search in investigations
            if "investigation" in data:
                investigation = data["investigation"]
                if (query.lower() in investigation.get("title", "").lower() or
                    query.lower() in investigation.get("description", "").lower()):
                    results.append({
                        "type": "investigation",
                        "id": investigation.get("identifier", ""),
                        "title": investigation.get("title", ""),
                        "description": investigation.get("description", "")
                    })
                
                # Search in studies
                if "studies" in investigation:
                    for study in investigation["studies"]:
                        if (query.lower() in study.get("title", "").lower() or
                            query.lower() in study.get("description", "").lower()):
                            results.append({
                                "type": "study",
                                "id": study.get("identifier", ""),
                                "title": study.get("title", ""),
                                "description": study.get("description", ""),
                                "investigation_id": investigation.get("identifier", "")
                            })
                        
                        # Search in assays
                        if "assays" in study:
                            for assay in study["assays"]:
                                measurement_type = assay.get("measurementType", {}).get("annotationValue", "")
                                technology_type = assay.get("technologyType", {}).get("annotationValue", "")
                                technology_platform = assay.get("technologyPlatform", "")
                                
                                if (query.lower() in measurement_type.lower() or
                                    query.lower() in technology_type.lower() or
                                    query.lower() in technology_platform.lower()):
                                    results.append({
                                        "type": "assay",
                                        "id": assay.get("identifier", ""),
                                        "measurement_type": measurement_type,
                                        "technology_type": technology_type,
                                        "technology_platform": technology_platform,
                                        "study_id": study.get("identifier", ""),
                                        "investigation_id": investigation.get("identifier", "")
                                    })
                                
                                # Search in data files
                                if "dataFiles" in assay:
                                    for data_file in assay["dataFiles"]:
                                        if query.lower() in data_file.get("name", "").lower():
                                            results.append({
                                                "type": "data_file",
                                                "id": data_file.get("identifier", ""),
                                                "name": data_file.get("name", ""),
                                                "type": data_file.get("type", ""),
                                                "assay_id": assay.get("identifier", ""),
                                                "study_id": study.get("identifier", ""),
                                                "investigation_id": investigation.get("identifier", "")
                                            })
            
            return True, results
        
        except Exception as e:
            return False, f"Error searching: {str(e)}"
    
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