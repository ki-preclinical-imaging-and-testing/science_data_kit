"""
ISA Browser Page for Science Data Kit

This module defines the core functionality for the ISA Browser page,
which allows users to browse and manage ISA (Investigation, Study, Assay) data
and ontology terms, and integrate them with Neo4j.
"""

from typing import Dict, Any, List, Optional, Set, Union
import requests
from pathlib import Path
import json
from io import BytesIO

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import IsaBrowserPageData
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.db.graph_utils import Neo4jConnection

# Constants
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
ONCOTREE_API_URL = "http://oncotree.mskcc.org/api"

# Import isatools classes through our compatibility layer
try:
    from isatools import isatab
    from isatools.model import Investigation, Study, Assay, Process, Material, DataFile
    from isatools.model import OntologyAnnotation, OntologySource
    ISATOOLS_AVAILABLE = True
except ImportError:
    from science_data_kit.core.utils.isa_compatibility import get_isa_objects
    Investigation, Study, Assay, Process, Material, DataFile, OntologyAnnotation, OntologySource = get_isa_objects()
    ISATOOLS_AVAILABLE = False

class IsaBrowserPage(BasePage):
    """
    Core implementation of the ISA Browser page.
    
    This class provides functionality for browsing and managing ISA data
    and ontology terms, and integrating them with Neo4j.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the ISA Browser page.
        
        Args:
            db_connection: Optional Neo4j database connection
        """
        super().__init__()
        self.title = "ISA Browser"
        self.terms = []
        self.existing_term_accessions = set()
        self.available_labels = []
        self.connection_status = {"neo4j": False}
        self.connection_errors = {}
        self.account_info = {}
        self.node_classes = []
        self.properties = []
        self.relationships = []
        self.neo4j_connection = db_connection
        
    def get_page_data(self) -> IsaBrowserPageData:
        """
        Get the page data for rendering.
        
        Returns:
            IsaBrowserPageData: The page data
        """
        # Convert terms to dictionaries for JSON serialization
        terms_data = []
        for term in self.terms:
            source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
            terms_data.append({
                "term": term.term,
                "term_accession": term.term_accession,
                "term_source": source_name
            })
            
        return IsaBrowserPageData(
            title=self.title,
            terms=terms_data,
            existing_term_accessions=self.existing_term_accessions,
            available_labels=self.available_labels,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors,
            account_info=self.account_info,
            node_classes=self.node_classes,
            properties=self.properties,
            relationships=self.relationships
        )
        
    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: str = None) -> Dict[str, Any]:
        """
        Connect to a Neo4j database.
        
        Args:
            uri: The Neo4j URI
            username: The Neo4j username
            password: The Neo4j password
            database: The Neo4j database name
            conn_name: Optional connection name
            
        Returns:
            Dict[str, Any]: Result of the connection attempt
        """
        try:
            # Create a Neo4j connection
            self.neo4j_connection = Neo4jConnection(
                uri=uri,
                username=username,
                password=password,
                database=database
            )
            
            # Test the connection
            if self.neo4j_connection.test_connection():
                self.connection_status["neo4j"] = True
                
                # Get all labels
                all_labels_query = "MATCH (n) RETURN DISTINCT labels(n) as labels"
                label_results = self.neo4j_connection.execute_query(all_labels_query)
                all_labels = sorted(set([label for result in label_results for labels_list in result["labels"] for label in labels_list]))
                self.available_labels = all_labels
                
                # Save the connection in the db_manager if a name is provided
                if conn_name:
                    db_manager.add_connection(
                        conn_name,
                        {
                            "uri": uri,
                            "username": username,
                            "password": password,
                            "database": database,
                            "type": "neo4j"
                        }
                    )
                
                return {"success": True}
            else:
                self.connection_errors["neo4j"] = "Failed to connect to Neo4j"
                return {"success": False, "error": "Failed to connect to Neo4j"}
        except Exception as e:
            self.connection_errors["neo4j"] = str(e)
            return {"success": False, "error": str(e)}
            
    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the Neo4j database.
        
        Returns:
            Dict[str, Any]: Result of the disconnection attempt
        """
        try:
            if self.neo4j_connection:
                self.neo4j_connection.close()
                self.neo4j_connection = None
                self.connection_status["neo4j"] = False
                self.available_labels = []
                return {"success": True}
            else:
                return {"success": False, "error": "Not connected to Neo4j"}
        except Exception as e:
            self.connection_errors["neo4j"] = str(e)
            return {"success": False, "error": str(e)}
            
    def _extract_node_classes(self, inv: Investigation) -> List[str]:
        """
        Extract node classes from an Investigation object.
        
        Args:
            inv: The Investigation object
            
        Returns:
            List[str]: List of node classes
        """
        node_classes = set()
        
        # Add Investigation
        node_classes.add("Investigation")
        
        # Add Studies
        if hasattr(inv, 'studies') and inv.studies:
            node_classes.add("Study")
            
            for study in inv.studies:
                # Add Assays
                if hasattr(study, 'assays') and study.assays:
                    node_classes.add("Assay")
                
                # Add Materials
                if hasattr(study, 'materials') and study.materials:
                    for material in study.materials.get('samples', []):
                        node_classes.add(material.__class__.__name__)
                        
                # Add Processes
                if hasattr(study, 'process_sequence') and study.process_sequence:
                    node_classes.add("Process")
                    
                    for process in study.process_sequence:
                        # Add inputs and outputs
                        if hasattr(process, 'inputs') and process.inputs:
                            for input_material in process.inputs:
                                node_classes.add(input_material.__class__.__name__)
                                
                        if hasattr(process, 'outputs') and process.outputs:
                            for output_material in process.outputs:
                                node_classes.add(output_material.__class__.__name__)
                                
                        # Add protocol
                        if hasattr(process, 'protocol') and process.protocol:
                            node_classes.add("Protocol")
        
        self.node_classes = sorted(list(node_classes))
        return self.node_classes
        
    def _extract_relationships(self, inv: Investigation) -> List[Dict[str, Any]]:
        """
        Extract relationships from an Investigation object.
        
        Args:
            inv: The Investigation object
            
        Returns:
            List[Dict[str, Any]]: List of relationships
        """
        relationships = []
        
        # Investigation to Study relationships
        if hasattr(inv, 'studies') and inv.studies:
            for study in inv.studies:
                relationships.append({
                    "source": "Investigation",
                    "target": "Study",
                    "type": "HAS_STUDY"
                })
                
                # Study to Assay relationships
                if hasattr(study, 'assays') and study.assays:
                    for assay in study.assays:
                        relationships.append({
                            "source": "Study",
                            "target": "Assay",
                            "type": "HAS_ASSAY"
                        })
                        
                # Study to Material relationships
                if hasattr(study, 'materials') and study.materials:
                    for material_type, materials in study.materials.items():
                        for material in materials:
                            relationships.append({
                                "source": "Study",
                                "target": material.__class__.__name__,
                                "type": f"HAS_{material_type.upper()}"
                            })
                            
                # Process relationships
                if hasattr(study, 'process_sequence') and study.process_sequence:
                    for process in study.process_sequence:
                        # Process to Protocol relationship
                        if hasattr(process, 'protocol') and process.protocol:
                            relationships.append({
                                "source": "Process",
                                "target": "Protocol",
                                "type": "USES_PROTOCOL"
                            })
                            
                        # Input relationships
                        if hasattr(process, 'inputs') and process.inputs:
                            for input_material in process.inputs:
                                relationships.append({
                                    "source": input_material.__class__.__name__,
                                    "target": "Process",
                                    "type": "INPUT_TO"
                                })
                                
                        # Output relationships
                        if hasattr(process, 'outputs') and process.outputs:
                            for output_material in process.outputs:
                                relationships.append({
                                    "source": "Process",
                                    "target": output_material.__class__.__name__,
                                    "type": "OUTPUT_TO"
                                })
        
        self.relationships = relationships
        return relationships
        
    def _extract_properties(self, inv: Investigation, class_name: str) -> List[Dict[str, Any]]:
        """
        Extract properties from an Investigation object for a specific class.
        
        Args:
            inv: The Investigation object
            class_name: The class name to extract properties for
            
        Returns:
            List[Dict[str, Any]]: List of properties
        """
        properties = []
        
        if class_name == "Investigation":
            # Extract Investigation properties
            if hasattr(inv, 'title') and inv.title:
                properties.append({"name": "title", "value": inv.title})
            if hasattr(inv, 'description') and inv.description:
                properties.append({"name": "description", "value": inv.description})
            if hasattr(inv, 'identifier') and inv.identifier:
                properties.append({"name": "identifier", "value": inv.identifier})
                
        elif class_name == "Study" and hasattr(inv, 'studies') and inv.studies:
            # Extract Study properties from the first study
            study = inv.studies[0]
            if hasattr(study, 'title') and study.title:
                properties.append({"name": "title", "value": study.title})
            if hasattr(study, 'description') and study.description:
                properties.append({"name": "description", "value": study.description})
            if hasattr(study, 'identifier') and study.identifier:
                properties.append({"name": "identifier", "value": study.identifier})
                
        elif class_name == "Assay" and hasattr(inv, 'studies') and inv.studies:
            # Extract Assay properties from the first assay of the first study
            if hasattr(inv.studies[0], 'assays') and inv.studies[0].assays:
                assay = inv.studies[0].assays[0]
                if hasattr(assay, 'measurement_type') and assay.measurement_type:
                    properties.append({"name": "measurement_type", "value": assay.measurement_type.term})
                if hasattr(assay, 'technology_type') and assay.technology_type:
                    properties.append({"name": "technology_type", "value": assay.technology_type.term})
                if hasattr(assay, 'filename') and assay.filename:
                    properties.append({"name": "filename", "value": assay.filename})
        
        self.properties = properties
        return properties
        
    def _get_standard_isa_terms(self) -> List[OntologyAnnotation]:
        """
        Get standard ISA terms.
        
        Returns:
            List[OntologyAnnotation]: List of standard ISA terms
        """
        # Create a proper OntologySource for ISA terms
        isa_source = OntologySource(
            name="ISA",
            file="",
            version="1.0",
            description="Standard ISA ontology terms"
        )
        
        # Create standard ISA terms
        standard_terms = [
            OntologyAnnotation(
                term="organism",
                term_accession="http://purl.obolibrary.org/obo/OBI_0100026",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="organism part",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000257",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="biological material",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000251",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="data transformation",
                term_accession="http://purl.obolibrary.org/obo/OBI_0200000",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="data acquisition",
                term_accession="http://purl.obolibrary.org/obo/OBI_0600013",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="normalization",
                term_accession="http://purl.obolibrary.org/obo/OBI_0200169",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="metabolite profiling",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000366",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="transcription profiling",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000424",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="protein expression profiling",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000615",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="mass spectrometry",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000470",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="NMR spectroscopy",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000623",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="DNA microarray",
                term_accession="http://purl.obolibrary.org/obo/OBI_0400148",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="RNA-seq",
                term_accession="http://purl.obolibrary.org/obo/OBI_0001271",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="sample collection",
                term_accession="http://purl.obolibrary.org/obo/OBI_0000659",
                term_source=isa_source
            ),
            OntologyAnnotation(
                term="extraction",
                term_accession="http://purl.obolibrary.org/obo/OBI_0302884",
                term_source=isa_source
            )
        ]
        
        return standard_terms
        
    def _get_cancer_types(self) -> List[Dict[str, Any]]:
        """
        Get cancer types from cBioPortal API.
        
        Returns:
            List[Dict[str, Any]]: List of cancer types
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/cancer-types")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.connection_errors["cbioportal"] = str(e)
            return []
            
    def _get_oncotree_tumor_types(self) -> List[Dict[str, Any]]:
        """
        Get tumor types from OncoTree API.
        
        Returns:
            List[Dict[str, Any]]: List of tumor types
        """
        try:
            response = requests.get(f"{ONCOTREE_API_URL}/tumorTypes")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.connection_errors["oncotree"] = str(e)
            return []
            
    def _convert_to_ontology_annotations(self, data: List[Dict[str, Any]], term_key: str, accession_key: str, source: str) -> List[OntologyAnnotation]:
        """
        Convert data to ontology annotations.
        
        Args:
            data: The data to convert
            term_key: The key for the term
            accession_key: The key for the accession
            source: The source name
            
        Returns:
            List[OntologyAnnotation]: List of ontology annotations
        """
        # Create a proper OntologySource for the source
        ontology_source = OntologySource(
            name=source,
            file="",
            version="1.0",
            description=f"Terms from {source}"
        )
        
        # Convert data to ontology annotations
        annotations = []
        for item in data:
            if term_key in item and accession_key in item:
                annotations.append(OntologyAnnotation(
                    term=item[term_key],
                    term_accession=item[accession_key],
                    term_source=ontology_source
                ))
                
        return annotations
        
    def _get_cbioportal_studies(self) -> List[Dict[str, Any]]:
        """
        Get studies from cBioPortal API.
        
        Returns:
            List[Dict[str, Any]]: List of studies
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.connection_errors["cbioportal"] = str(e)
            return []
            
    def _load_cbioportal_study_data(self, study_id: str) -> Dict[str, Any]:
        """
        Load study data from cBioPortal API.
        
        Args:
            study_id: The study ID
            
        Returns:
            Dict[str, Any]: The study data
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies/{study_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.connection_errors["cbioportal"] = str(e)
            return {}
            
    def add_cancer_types_to_terms(self) -> Dict[str, Any]:
        """
        Add cancer types to terms.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            cancer_types = self._get_cancer_types()
            if cancer_types:
                new_terms = self._convert_to_ontology_annotations(
                    cancer_types, 
                    "name", 
                    "cancerTypeId", 
                    "cBioPortal"
                )
                
                # Add only new terms that don't exist yet
                added_count = 0
                for term in new_terms:
                    if term.term_accession not in self.existing_term_accessions:
                        self.terms.append(term)
                        self.existing_term_accessions.add(term.term_accession)
                        added_count += 1
                        
                return {
                    "success": True,
                    "added_count": added_count,
                    "message": f"Added {added_count} cancer type terms."
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to load cancer types."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading cancer types: {str(e)}"
            }
            
    def add_tumor_types_to_terms(self) -> Dict[str, Any]:
        """
        Add tumor types to terms.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            tumor_types = self._get_oncotree_tumor_types()
            if tumor_types:
                new_terms = self._convert_to_ontology_annotations(
                    tumor_types, 
                    "name", 
                    "code", 
                    "OncoTree"
                )
                
                # Add only new terms that don't exist yet
                added_count = 0
                for term in new_terms:
                    if term.term_accession not in self.existing_term_accessions:
                        self.terms.append(term)
                        self.existing_term_accessions.add(term.term_accession)
                        added_count += 1
                        
                return {
                    "success": True,
                    "added_count": added_count,
                    "message": f"Added {added_count} tumor type terms."
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to load tumor types."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading tumor types: {str(e)}"
            }
            
    def add_study_data_to_terms(self, study_id: str) -> Dict[str, Any]:
        """
        Add study data to terms.
        
        Args:
            study_id: The study ID
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            study_data = self._load_cbioportal_study_data(study_id)
            if study_data:
                terms = []
                
                # Add cancer type as a term
                if "cancerType" in study_data:
                    terms.append(OntologyAnnotation(
                        term=study_data["cancerType"].get("name", ""),
                        term_accession=study_data["cancerType"].get("cancerTypeId", ""),
                        term_source="cBioPortal"
                    ))
                    
                # Add other relevant terms
                if "referenceGenome" in study_data:
                    terms.append(OntologyAnnotation(
                        term=f"Reference Genome: {study_data['referenceGenome']}",
                        term_accession=f"genome:{study_data['referenceGenome']}",
                        term_source="cBioPortal"
                    ))
                    
                # Add only new terms that don't exist yet
                added_count = 0
                for term in terms:
                    if term.term_accession and term.term_accession not in self.existing_term_accessions:
                        self.terms.append(term)
                        self.existing_term_accessions.add(term.term_accession)
                        added_count += 1
                        
                return {
                    "success": True,
                    "added_count": added_count,
                    "message": f"Added {added_count} terms from study."
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to load study data."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading study data: {str(e)}"
            }
            
    def add_term_manually(self, term_name: str, term_uri: str, ontology_source: str) -> Dict[str, Any]:
        """
        Add a term manually.
        
        Args:
            term_name: The term name
            term_uri: The term URI
            ontology_source: The ontology source
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            # Check if term already exists
            if term_uri in self.existing_term_accessions:
                return {
                    "success": False,
                    "message": f"Term with URI {term_uri} already exists."
                }
                
            # Create a proper OntologySource for the source
            source = OntologySource(
                name=ontology_source,
                file="",
                version="1.0",
                description=f"Terms from {ontology_source}"
            )
            
            # Create the new term
            new_term = OntologyAnnotation(
                term=term_name,
                term_accession=term_uri,
                term_source=source
            )
            
            # Add the term
            self.terms.append(new_term)
            self.existing_term_accessions.add(term_uri)
            
            return {
                "success": True,
                "message": f"Added term: {term_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error adding term: {str(e)}"
            }
            
    def clear_terms(self) -> Dict[str, Any]:
        """
        Clear all terms.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            term_count = len(self.terms)
            self.terms = []
            self.existing_term_accessions = set()
            
            return {
                "success": True,
                "message": f"Cleared {term_count} terms."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error clearing terms: {str(e)}"
            }
            
    def process_isa_file(self, file_path_or_buffer) -> Dict[str, Any]:
        """
        Process an ISA file.
        
        Args:
            file_path_or_buffer: The file path or buffer
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            if not ISATOOLS_AVAILABLE:
                return {
                    "success": False,
                    "message": "The isatools package is not available in this Python environment."
                }
                
            # Load the ISA file
            inv = isatab.load(file_path_or_buffer)
            
            # Extract node classes, relationships, and properties
            self.node_classes = self._extract_node_classes(inv)
            self.relationships = self._extract_relationships(inv)
            
            return {
                "success": True,
                "message": "ISA file processed successfully.",
                "node_classes": self.node_classes,
                "relationships": self.relationships
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing ISA file: {str(e)}"
            }
            
    def load_ontology_terms_to_neo4j(self, create_source_nodes: bool = True, relationship_type: str = "HAS_TERM") -> Dict[str, Any]:
        """
        Load ontology terms to Neo4j.
        
        Args:
            create_source_nodes: Whether to create ontology source nodes
            relationship_type: The relationship type
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            if not self.neo4j_connection:
                return {
                    "success": False,
                    "message": "Not connected to Neo4j."
                }
                
            if not self.terms:
                return {
                    "success": False,
                    "message": "No ontology terms to load."
                }
                
            # Load terms into Neo4j
            relationships_created = 0
            
            for term in self.terms:
                source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
                
                # Create source node if needed
                if create_source_nodes:
                    source_query = """
                    MERGE (s:OntologySource {name: $name})
                    ON CREATE SET s.description = $description
                    RETURN s
                    """
                    source_params = {
                        "name": source_name,
                        "description": f"Ontology source: {source_name}"
                    }
                    self.neo4j_connection.execute_query(source_query, source_params)
                    
                # Create term node
                term_query = """
                MERGE (t:OntologyTerm {accession: $accession})
                ON CREATE SET t.term = $term
                RETURN t
                """
                term_params = {
                    "accession": term.term_accession,
                    "term": term.term
                }
                self.neo4j_connection.execute_query(term_query, term_params)
                
                # Create relationship
                rel_query = f"""
                MATCH (s:OntologySource {{name: $source_name}}), (t:OntologyTerm {{accession: $accession}})
                MERGE (s)-[r:{relationship_type}]->(t)
                RETURN r
                """
                rel_params = {
                    "source_name": source_name,
                    "accession": term.term_accession
                }
                self.neo4j_connection.execute_query(rel_query, rel_params)
                relationships_created += 1
                
            return {
                "success": True,
                "message": f"Successfully loaded ontology terms into Neo4j. Created {relationships_created} relationships.",
                "relationships_created": relationships_created
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error loading ontology terms into Neo4j: {str(e)}"
            }