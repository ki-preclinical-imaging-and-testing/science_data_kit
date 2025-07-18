"""
Map Visualization Page for Science Data Kit

This module defines the MapPage class, which provides functionality for
visualizing and manipulating graph data in a map-like interface.
"""

from typing import Dict, Any, List, Optional, Set, Union, Tuple
import pandas as pd
import json
from pathlib import Path
from io import BytesIO

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import MapPageData
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.db.graph_utils import Neo4jConnection
from science_data_kit.core.models.app_models import merge_nodes_with_existing

class MapPage(BasePage):
    """
    Map visualization page for the Science Data Kit.
    
    This page provides functionality for visualizing and manipulating graph data
    in a map-like interface. It supports loading entities from files and databases,
    creating relationships between entities, and visualizing the resulting graph.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the MapPage.
        
        Args:
            db_connection: Optional database connection to use.
        """
        super().__init__()
        self.page_data = MapPageData(title="Map Visualization")
        self.db_connection = db_connection
        
        # Initialize connection status
        self.page_data.connection_status = {"neo4j": False}
        self.page_data.connection_errors = {}
        
        # Initialize entity-related data
        self.page_data.entities = []
        self.page_data.relationships = []
        self.page_data.entity_labels = []
        self.page_data.entity_structures = {}
        self.page_data.taxonomy_keys = []
        
        # Initialize graph-related data
        self.page_data.node_classes = []
        self.page_data.properties = {}
        self.page_data.relationship_types = []
        
    def get_page_data(self) -> MapPageData:
        """
        Get the page data for the Map page.
        
        Returns:
            MapPageData: The page data for the Map page.
        """
        return self.page_data
    
    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: str = None) -> Dict[str, Any]:
        """
        Connect to a Neo4j database.
        
        Args:
            uri: The URI of the Neo4j database.
            username: The username for the Neo4j database.
            password: The password for the Neo4j database.
            database: The name of the Neo4j database.
            conn_name: Optional name for the connection.
            
        Returns:
            Dict[str, Any]: A dictionary with the connection result.
        """
        try:
            # Create a connection to the Neo4j database
            self.db_connection = Neo4jConnection(uri, username, password, database)
            
            # Test the connection
            result = self.db_connection.test_connection()
            
            if result["success"]:
                # Update connection status
                self.page_data.connection_status["neo4j"] = True
                self.page_data.connection_errors = {}
                
                # Get available node labels
                labels_query = "CALL db.labels()"
                labels_result = self.db_connection.execute_query(labels_query)
                self.page_data.node_classes = [record["label"] for record in labels_result]
                
                # Get available relationship types
                rel_query = "CALL db.relationshipTypes()"
                rel_result = self.db_connection.execute_query(rel_query)
                self.page_data.relationship_types = [record["relationshipType"] for record in rel_result]
                
                # Get properties for each node label
                self.page_data.properties = {}
                for label in self.page_data.node_classes:
                    prop_query = f"MATCH (n:{label}) RETURN keys(n) as props LIMIT 1"
                    prop_result = self.db_connection.execute_query(prop_query)
                    if prop_result:
                        self.page_data.properties[label] = prop_result[0]["props"]
                    else:
                        self.page_data.properties[label] = []
                
                return {"success": True, "message": "Connected to Neo4j database successfully"}
            else:
                self.page_data.connection_status["neo4j"] = False
                self.page_data.connection_errors["neo4j"] = result["message"]
                return {"success": False, "message": result["message"]}
        except Exception as e:
            self.page_data.connection_status["neo4j"] = False
            self.page_data.connection_errors["neo4j"] = str(e)
            return {"success": False, "message": str(e)}
    
    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the Neo4j database.
        
        Returns:
            Dict[str, Any]: A dictionary with the disconnection result.
        """
        try:
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
                
            # Update connection status
            self.page_data.connection_status["neo4j"] = False
            self.page_data.connection_errors = {}
            
            # Clear graph-related data
            self.page_data.node_classes = []
            self.page_data.properties = {}
            self.page_data.relationship_types = []
            
            return {"success": True, "message": "Disconnected from Neo4j database successfully"}
        except Exception as e:
            self.page_data.connection_errors["neo4j"] = str(e)
            return {"success": False, "message": str(e)}
    
    def load_entities_from_file(self, file_data, file_name: str = None, file_type: str = None, sheet_name: str = None) -> Dict[str, Any]:
        """
        Load entities from a file.
        
        Args:
            file_data: The file data as bytes or a file-like object.
            file_name: Optional name of the file.
            file_type: Optional type of the file (csv, excel, json).
            sheet_name: Optional name of the sheet (for Excel files).
            
        Returns:
            Dict[str, Any]: A dictionary with the loading result.
        """
        try:
            # Determine file type if not provided
            if not file_type:
                if file_name:
                    if file_name.endswith('.csv'):
                        file_type = 'csv'
                    elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                        file_type = 'excel'
                    elif file_name.endswith('.json'):
                        file_type = 'json'
                    else:
                        file_type = 'csv'  # Default to CSV
                else:
                    file_type = 'csv'  # Default to CSV
            
            # Load the data based on file type
            if file_type == 'csv':
                entity_data = pd.read_csv(BytesIO(file_data))
            elif file_type == 'excel':
                if sheet_name:
                    entity_data = pd.read_excel(BytesIO(file_data), sheet_name=sheet_name)
                else:
                    entity_data = pd.read_excel(BytesIO(file_data))
            elif file_type == 'json':
                # For JSON, we need to parse it first
                json_data = json.loads(file_data.decode('utf-8'))
                entity_data = pd.DataFrame(json_data)
            else:
                return {"success": False, "message": f"Unsupported file type: {file_type}"}
            
            # Store the loaded entities
            self.page_data.entities = entity_data.to_dict('records')
            
            # Extract entity labels (assuming there's a 'label' column)
            if 'label' in entity_data.columns:
                self.page_data.entity_labels = entity_data['label'].unique().tolist()
            
            return {
                "success": True, 
                "message": f"Loaded {len(self.page_data.entities)} entities from file",
                "entities": self.page_data.entities,
                "entity_labels": self.page_data.entity_labels
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def load_entities_from_database(self, label: str) -> Dict[str, Any]:
        """
        Load entities from the Neo4j database.
        
        Args:
            label: The label of the entities to load.
            
        Returns:
            Dict[str, Any]: A dictionary with the loading result.
        """
        try:
            if not self.db_connection:
                return {"success": False, "message": "Not connected to a database"}
            
            if not self.page_data.connection_status.get("neo4j", False):
                return {"success": False, "message": "Not connected to a Neo4j database"}
            
            # Query to get all nodes with the given label
            query = f"MATCH (n:{label}) RETURN n"
            result = self.db_connection.execute_query(query)
            
            # Convert the result to a list of dictionaries
            entities = []
            for record in result:
                node = record["n"]
                entity = dict(node)
                entity["label"] = label
                entities.append(entity)
            
            # Store the loaded entities
            self.page_data.entities = entities
            
            # Update entity labels
            if label not in self.page_data.entity_labels:
                self.page_data.entity_labels.append(label)
            
            return {
                "success": True, 
                "message": f"Loaded {len(entities)} entities with label '{label}' from database",
                "entities": entities
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def create_entity_structure(self, entity_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a structure for the entities.
        
        Args:
            entity_data: A list of dictionaries representing entities.
            
        Returns:
            Dict[str, Any]: A dictionary with the structure creation result.
        """
        try:
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(entity_data)
            
            # Get unique labels
            if 'label' in df.columns:
                labels = df['label'].unique().tolist()
            else:
                # If no label column, assume all entities have the same label
                labels = ['Entity']
                df['label'] = 'Entity'
            
            # Create a structure for each label
            structures = {}
            for label in labels:
                label_df = df[df['label'] == label]
                
                # Get all columns except 'label'
                columns = [col for col in label_df.columns if col != 'label']
                
                # Create a structure with column names as keys and data types as values
                structure = {}
                for col in columns:
                    # Determine the data type based on the column values
                    if label_df[col].dtype == 'int64':
                        structure[col] = 'Integer'
                    elif label_df[col].dtype == 'float64':
                        structure[col] = 'Float'
                    elif label_df[col].dtype == 'bool':
                        structure[col] = 'Boolean'
                    else:
                        structure[col] = 'String'
                
                structures[label] = structure
            
            # Store the entity structures
            self.page_data.entity_structures = structures
            
            return {
                "success": True, 
                "message": f"Created structure for {len(labels)} entity labels",
                "structures": structures
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def push_entities_to_neo4j(self, entity_data: List[Dict[str, Any]], label: str, structure: Dict[str, str]) -> Dict[str, Any]:
        """
        Push entities to the Neo4j database.
        
        Args:
            entity_data: A list of dictionaries representing entities.
            label: The label to use for the entities.
            structure: A dictionary mapping property names to data types.
            
        Returns:
            Dict[str, Any]: A dictionary with the push result.
        """
        try:
            if not self.db_connection:
                return {"success": False, "message": "Not connected to a database"}
            
            if not self.page_data.connection_status.get("neo4j", False):
                return {"success": False, "message": "Not connected to a Neo4j database"}
            
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(entity_data)
            
            # Add the label column if it doesn't exist
            if 'label' not in df.columns:
                df['label'] = label
            
            # Create Cypher queries to create the nodes
            count = 0
            for _, row in df.iterrows():
                # Create a dictionary of properties
                properties = {}
                for prop, prop_type in structure.items():
                    if prop in row and pd.notna(row[prop]):
                        # Convert the value based on the property type
                        if prop_type == 'Integer':
                            properties[prop] = int(row[prop])
                        elif prop_type == 'Float':
                            properties[prop] = float(row[prop])
                        elif prop_type == 'Boolean':
                            properties[prop] = bool(row[prop])
                        else:
                            properties[prop] = str(row[prop])
                
                # Create the Cypher query
                props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
                query = f"CREATE (n:{label} {{{props_str}}})"
                
                # Execute the query
                self.db_connection.execute_query(query, properties)
                count += 1
            
            return {
                "success": True, 
                "message": f"Pushed {count} entities with label '{label}' to Neo4j database"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def create_relationships(self, source_label: str, target_label: str, relationship_type: str, source_property: str, target_property: str) -> Dict[str, Any]:
        """
        Create relationships between entities in the Neo4j database.
        
        Args:
            source_label: The label of the source entities.
            target_label: The label of the target entities.
            relationship_type: The type of relationship to create.
            source_property: The property of the source entities to match on.
            target_property: The property of the target entities to match on.
            
        Returns:
            Dict[str, Any]: A dictionary with the relationship creation result.
        """
        try:
            if not self.db_connection:
                return {"success": False, "message": "Not connected to a database"}
            
            if not self.page_data.connection_status.get("neo4j", False):
                return {"success": False, "message": "Not connected to a Neo4j database"}
            
            # Create the Cypher query to create relationships
            query = f"""
            MATCH (source:{source_label}), (target:{target_label})
            WHERE source.{source_property} = target.{target_property}
            CREATE (source)-[r:{relationship_type}]->(target)
            RETURN count(r) as count
            """
            
            # Execute the query
            result = self.db_connection.execute_query(query)
            count = result[0]["count"] if result else 0
            
            # Store the relationship information
            relationship = {
                "source_label": source_label,
                "target_label": target_label,
                "relationship_type": relationship_type,
                "source_property": source_property,
                "target_property": target_property,
                "count": count
            }
            self.page_data.relationships.append(relationship)
            
            return {
                "success": True, 
                "message": f"Created {count} relationships of type '{relationship_type}' between '{source_label}' and '{target_label}'",
                "relationship": relationship
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def load_ontology(self, ontology_data) -> Dict[str, Any]:
        """
        Load ontology data.
        
        Args:
            ontology_data: The ontology data as a JSON string or dictionary.
            
        Returns:
            Dict[str, Any]: A dictionary with the loading result.
        """
        try:
            # Parse the ontology data if it's a string
            if isinstance(ontology_data, str):
                ontology = json.loads(ontology_data)
            elif isinstance(ontology_data, bytes):
                ontology = json.loads(ontology_data.decode('utf-8'))
            else:
                ontology = ontology_data
            
            # Store the ontology data
            self.page_data.ontology_data = ontology
            
            return {
                "success": True, 
                "message": "Loaded ontology data successfully",
                "ontology": ontology
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def push_ontology_to_neo4j(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Push ontology data to the Neo4j database.
        
        Args:
            ontology_data: A dictionary representing the ontology.
            
        Returns:
            Dict[str, Any]: A dictionary with the push result.
        """
        try:
            if not self.db_connection:
                return {"success": False, "message": "Not connected to a database"}
            
            if not self.page_data.connection_status.get("neo4j", False):
                return {"success": False, "message": "Not connected to a Neo4j database"}
            
            # Process the ontology data and create nodes and relationships
            # This is a simplified implementation; the actual implementation would depend on the structure of the ontology data
            
            # Assume the ontology data has a 'terms' key with a list of terms
            if 'terms' in ontology_data:
                terms = ontology_data['terms']
                
                # Create nodes for each term
                for term in terms:
                    # Create a dictionary of properties
                    properties = {}
                    for key, value in term.items():
                        if key != 'id' and key != 'relationships':
                            properties[key] = value
                    
                    # Create the Cypher query to create the node
                    props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
                    query = f"CREATE (n:OntologyTerm {{id: '{term['id']}', {props_str}}})"
                    
                    # Execute the query
                    self.db_connection.execute_query(query, properties)
                
                # Create relationships between terms
                for term in terms:
                    if 'relationships' in term:
                        for rel in term['relationships']:
                            # Create the Cypher query to create the relationship
                            query = f"""
                            MATCH (source:OntologyTerm {{id: '{term['id']}'}}), (target:OntologyTerm {{id: '{rel['target_id']}'}})
                            CREATE (source)-[r:{rel['type']}]->(target)
                            """
                            
                            # Execute the query
                            self.db_connection.execute_query(query)
            
            return {
                "success": True, 
                "message": "Pushed ontology data to Neo4j database successfully"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def create_taxonomy(self, entity_data: List[Dict[str, Any]], taxonomy_keys: List[str]) -> Dict[str, Any]:
        """
        Create a taxonomy from entity data.
        
        Args:
            entity_data: A list of dictionaries representing entities.
            taxonomy_keys: A list of keys to use for the taxonomy.
            
        Returns:
            Dict[str, Any]: A dictionary with the taxonomy creation result.
        """
        try:
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(entity_data)
            
            # Create a taxonomy DataFrame
            taxonomy_df = df[taxonomy_keys].drop_duplicates()
            
            # Store the taxonomy keys
            self.page_data.taxonomy_keys = taxonomy_keys
            
            return {
                "success": True, 
                "message": f"Created taxonomy with {len(taxonomy_df)} entries",
                "taxonomy": taxonomy_df.to_dict('records')
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def push_taxonomy_to_neo4j(self, taxonomy_df: pd.DataFrame, taxonomy_keys: List[str], entity_label: str, match_columns: List[str], relationship_type: str) -> Dict[str, Any]:
        """
        Push a taxonomy to the Neo4j database.
        
        Args:
            taxonomy_df: A DataFrame representing the taxonomy.
            taxonomy_keys: A list of keys used for the taxonomy.
            entity_label: The label of the entities to match.
            match_columns: The columns to use for matching entities.
            relationship_type: The type of relationship to create.
            
        Returns:
            Dict[str, Any]: A dictionary with the push result.
        """
        try:
            if not self.db_connection:
                return {"success": False, "message": "Not connected to a database"}
            
            if not self.page_data.connection_status.get("neo4j", False):
                return {"success": False, "message": "Not connected to a Neo4j database"}
            
            # Create nodes for each taxonomy entry
            for _, row in taxonomy_df.iterrows():
                # Create a dictionary of properties
                properties = {}
                for key in taxonomy_keys:
                    if pd.notna(row[key]):
                        properties[key] = row[key]
                
                # Create the Cypher query to create the node
                props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
                query = f"CREATE (n:Taxonomy {{{props_str}}})"
                
                # Execute the query
                self.db_connection.execute_query(query, properties)
            
            # Create relationships between taxonomy nodes and entities
            for _, row in taxonomy_df.iterrows():
                # Create match conditions for the taxonomy node
                taxonomy_match = " AND ".join([f"t.{key} = '{row[key]}'" for key in taxonomy_keys if pd.notna(row[key])])
                
                # Create match conditions for the entity
                entity_match = " AND ".join([f"e.{col} = '{row[col]}'" for col in match_columns if pd.notna(row[col])])
                
                # Create the Cypher query to create the relationship
                query = f"""
                MATCH (t:Taxonomy), (e:{entity_label})
                WHERE {taxonomy_match} AND {entity_match}
                CREATE (t)-[r:{relationship_type}]->(e)
                """
                
                # Execute the query
                self.db_connection.execute_query(query)
            
            return {
                "success": True, 
                "message": f"Pushed taxonomy to Neo4j database and created relationships to {entity_label} entities"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def filter_entity_data(self, entity_data: List[Dict[str, Any]], filter_column: str, filter_operation: str, filter_value: str) -> Dict[str, Any]:
        """
        Filter entity data.
        
        Args:
            entity_data: A list of dictionaries representing entities.
            filter_column: The column to filter on.
            filter_operation: The operation to use for filtering (equals, contains, greater_than, less_than).
            filter_value: The value to filter against.
            
        Returns:
            Dict[str, Any]: A dictionary with the filtering result.
        """
        try:
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(entity_data)
            
            # Apply the filter based on the operation
            if filter_operation == 'equals':
                filtered_df = df[df[filter_column] == filter_value]
            elif filter_operation == 'contains':
                filtered_df = df[df[filter_column].astype(str).str.contains(filter_value)]
            elif filter_operation == 'greater_than':
                filtered_df = df[df[filter_column] > float(filter_value)]
            elif filter_operation == 'less_than':
                filtered_df = df[df[filter_column] < float(filter_value)]
            else:
                return {"success": False, "message": f"Unsupported filter operation: {filter_operation}"}
            
            # Convert the filtered DataFrame back to a list of dictionaries
            filtered_entities = filtered_df.to_dict('records')
            
            return {
                "success": True, 
                "message": f"Filtered entities from {len(entity_data)} to {len(filtered_entities)}",
                "entities": filtered_entities
            }
        except Exception as e:
            return {"success": False, "message": str(e)}