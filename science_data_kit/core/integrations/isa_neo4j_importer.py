"""
ISA Neo4j Importer for Science Data Kit

This module provides functionality for importing ISA metadata and ontologies into Neo4j,
allowing users to store and query ISA data in a graph database.
"""

import rdflib
from typing import Dict, List, Optional, Any, Tuple, Union

class ISANeo4jImporter:
    """
    Importer for Neo4j operations in the ISA Tools integration.
    
    This class provides methods for importing ISA metadata and ontologies into Neo4j.
    """
    
    def __init__(self):
        """
        Initialize the ISA Neo4j Importer.
        """
        pass
    
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