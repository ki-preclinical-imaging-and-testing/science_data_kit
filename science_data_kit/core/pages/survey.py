"""
Survey Page Module for Science Data Kit

This module provides a survey page for scanning and analyzing file systems.
It includes functionality for locating and scanning datasets, viewing scan results,
labeling entities, and pushing data to Neo4j.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import SurveyPageData
from science_data_kit.core.db.db_manager import db_manager
from science_data_kit.core.models.file_models import Folder, File


class SurveyPage(BasePage):
    """
    Survey page for scanning and analyzing file systems.

    This page provides functionality for:
    - Locating and scanning datasets
    - Viewing scan results
    - Labeling entities
    - Pushing data to Neo4j
    """

    def __init__(self):
        """Initialize the Survey page."""
        super().__init__()
        self.db_manager = db_manager
        self._initialize_survey_state()

    def _initialize_survey_state(self) -> None:
        """Initialize survey-related state variables."""
        self.page_data = SurveyPageData()
        
        # Set default ncdu_json_path
        self.page_data.ncdu_json_path = str(Path.home() / "ncdu_scan.json")

    def get_page_data(self) -> SurveyPageData:
        """
        Get the page data for the survey page.
        
        Returns:
            SurveyPageData: The page data for the survey page.
        """
        return self.page_data

    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to a Neo4j database.
        
        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            conn_name: Optional name for the connection.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Update connection details
            self.db_manager.uri = uri
            self.db_manager.user = username
            self.db_manager.password = password
            self.db_manager.database = database
            
            # Connect to the database with the specified connection name
            connection_successful = self.db_manager._connect(conn_name)
            
            if not connection_successful:
                error_msg = self.db_manager._connection_error or "Unknown connection error"
                return {"success": False, "error": f"Failed to connect to Neo4j: {error_msg}"}
            
            # Update page data
            self.page_data.connection_status["neo4j"] = True
            self.page_data.neo4j_uri = uri
            self.page_data.neo4j_user = username
            self.page_data.neo4j_password = password
            self.page_data.neo4j_database = database
            self.page_data.active_connection = conn_name
            
            return {"success": True, "message": f"Connected to Neo4j database at {uri}"}
        except Exception as e:
            self.page_data.connection_status["neo4j"] = False
            self.page_data.connection_errors["neo4j"] = str(e)
            return {"success": False, "error": f"Failed to connect to Neo4j: {str(e)}"}

    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the Neo4j database.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Close the connection
            self.db_manager.close()
            
            # Update page data
            self.page_data.connection_status["neo4j"] = False
            self.page_data.active_connection = None
            
            return {"success": True, "message": "Disconnected from Neo4j database"}
        except Exception as e:
            return {"success": False, "error": f"Failed to disconnect from Neo4j: {str(e)}"}

    def scan_directory(self, folder_path: str) -> Dict[str, Any]:
        """
        Scan a directory and return the results.
        
        Args:
            folder_path: The path to the directory to scan.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            results = []
            
            # Check if the path exists
            if not os.path.exists(folder_path):
                return {"success": False, "error": f"Path does not exist: {folder_path}"}
            
            # Update page data
            self.page_data.folder_path = folder_path
            
            # Walk through the directory
            for root, dirs, files in os.walk(folder_path):
                # Add directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    rel_path = os.path.relpath(dir_path, folder_path)
                    
                    results.append({
                        "path": dir_path,
                        "rel_path": rel_path,
                        "name": dir_name,
                        "type": "directory",
                        "size": 0,
                        "label": self.page_data.directory_label
                    })
                
                # Add files
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, folder_path)
                    
                    try:
                        size = os.path.getsize(file_path)
                    except:
                        size = 0
                    
                    results.append({
                        "path": file_path,
                        "rel_path": rel_path,
                        "name": file_name,
                        "type": "file",
                        "size": size,
                        "label": self.page_data.file_label
                    })
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Update page data
            self.page_data.scan_results = results
            self.page_data.scanned_files = df
            self.page_data.scan_completed = True
            
            return {
                "success": True,
                "message": f"Scanned {len(results)} items in {folder_path}",
                "results": results,
                "dataframe": df.to_dict(orient="records")
            }
        except Exception as e:
            return {"success": False, "error": f"Error scanning directory: {str(e)}"}

    def run_ncdu_scan(self, folder_path: str, output_json_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run an ncdu scan on a directory and save the results to a JSON file.
        
        Args:
            folder_path: The path to the directory to scan.
            output_json_path: The path to save the JSON output. If None, uses the default path.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Check if the path exists
            if not os.path.exists(folder_path):
                return {"success": False, "error": f"Path does not exist: {folder_path}"}
            
            # Update page data
            self.page_data.folder_path = folder_path
            
            # Set output path
            if output_json_path:
                self.page_data.ncdu_json_path = output_json_path
            
            # Check if ncdu is installed
            try:
                subprocess.run(["ncdu", "--version"], capture_output=True, check=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                return {"success": False, "error": "ncdu is not installed or not in PATH"}
            
            # Run ncdu scan
            try:
                cmd = ["ncdu", "-o", self.page_data.ncdu_json_path, "-f", "json", "-x", folder_path]
                process = subprocess.run(cmd, capture_output=True, text=True, check=True)
                output = process.stdout + process.stderr
            except subprocess.CalledProcessError as e:
                return {"success": False, "error": f"ncdu scan failed: {e.stderr}"}
            
            # Update page data
            self.page_data.ncdu_output = output
            self.page_data.scan_completed = True
            
            # Parse the JSON file
            try:
                with open(self.page_data.ncdu_json_path, 'r') as f:
                    ncdu_data = json.load(f)
                
                # Parse the ncdu JSON into a DataFrame
                results = []
                self._parse_ncdu_json(ncdu_data, results)
                
                # Convert to DataFrame
                df = pd.DataFrame(results)
                
                # Update page data
                self.page_data.scan_results = results
                self.page_data.scanned_files = df
                
                return {
                    "success": True,
                    "message": f"Completed ncdu scan of {folder_path}",
                    "results": results,
                    "dataframe": df.to_dict(orient="records"),
                    "output": output
                }
            except Exception as e:
                return {"success": False, "error": f"Error parsing ncdu output: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Error running ncdu scan: {str(e)}"}

    def _parse_ncdu_json(self, node: Dict[str, Any], results: List[Dict[str, Any]], parent_path: str = "") -> None:
        """
        Parse the ncdu JSON output recursively.
        
        Args:
            node: The current node in the ncdu JSON.
            results: The list to append results to.
            parent_path: The path of the parent directory.
        """
        # Skip the first element which is metadata
        if isinstance(node, list) and len(node) > 0:
            # First element is metadata, rest are children
            metadata = node[0]
            children = node[1:]
            
            for child in children:
                name = child.get("name", "")
                path = os.path.join(parent_path, name)
                
                if "children" in child:
                    # This is a directory
                    results.append({
                        "path": path,
                        "rel_path": path,
                        "name": name,
                        "type": "directory",
                        "size": child.get("dsize", 0),
                        "label": self.page_data.directory_label
                    })
                    
                    # Process children
                    self._parse_ncdu_json(child["children"], results, path)
                else:
                    # This is a file
                    results.append({
                        "path": path,
                        "rel_path": path,
                        "name": name,
                        "type": "file",
                        "size": child.get("dsize", 0),
                        "label": self.page_data.file_label
                    })

    def push_to_neo4j(self, include_files: bool = False) -> Dict[str, Any]:
        """
        Push the scan results to Neo4j.
        
        Args:
            include_files: Whether to include files in the push.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Check if connected to Neo4j
            if not self.db_manager.is_connected():
                return {"success": False, "error": "Not connected to Neo4j"}
            
            # Check if scan results exist
            if self.page_data.scanned_files is None or len(self.page_data.scanned_files) == 0:
                return {"success": False, "error": "No scan results to push"}
            
            # Filter results based on include_files
            df = self.page_data.scanned_files
            if not include_files:
                df = df[df["type"] == "directory"]
            
            # Create nodes for each item
            created_nodes = 0
            created_relationships = 0
            
            # Create a dictionary to store nodes by path
            nodes_by_path = {}
            
            # Create nodes for each item
            for _, row in df.iterrows():
                path = row["path"]
                name = row["name"]
                item_type = row["type"]
                size = row["size"]
                label = row["label"]
                
                # Create Cypher query for the node
                query = f"""
                MERGE (n:{label} {{path: $path}})
                SET n.name = $name,
                    n.type = $type,
                    n.size = $size
                RETURN n
                """
                
                params = {
                    "path": path,
                    "name": name,
                    "type": item_type,
                    "size": size
                }
                
                # Execute query
                result = self.db_manager.query(query, params)
                
                if result:
                    created_nodes += 1
                    nodes_by_path[path] = result[0]["n"]
            
            # Create relationships between nodes
            for path, node in nodes_by_path.items():
                parent_path = os.path.dirname(path)
                
                if parent_path in nodes_by_path:
                    # Create Cypher query for the relationship
                    query = f"""
                    MATCH (parent:{self.page_data.directory_label} {{path: $parent_path}})
                    MATCH (child {{path: $child_path}})
                    MERGE (parent)-[r:CONTAINS]->(child)
                    RETURN r
                    """
                    
                    params = {
                        "parent_path": parent_path,
                        "child_path": path
                    }
                    
                    # Execute query
                    result = self.db_manager.query(query, params)
                    
                    if result:
                        created_relationships += 1
            
            return {
                "success": True,
                "message": f"Pushed {created_nodes} nodes and {created_relationships} relationships to Neo4j",
                "nodes_created": created_nodes,
                "relationships_created": created_relationships
            }
        except Exception as e:
            return {"success": False, "error": f"Error pushing to Neo4j: {str(e)}"}

    def update_entity_labels(self, directory_label: str, file_label: str) -> Dict[str, Any]:
        """
        Update the entity labels used for Neo4j nodes.
        
        Args:
            directory_label: The label to use for directories.
            file_label: The label to use for files.
            
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            self.page_data.directory_label = directory_label
            self.page_data.file_label = file_label
            
            # Update labels in scan results if they exist
            if self.page_data.scanned_files is not None and len(self.page_data.scanned_files) > 0:
                self.page_data.scanned_files.loc[self.page_data.scanned_files["type"] == "directory", "label"] = directory_label
                self.page_data.scanned_files.loc[self.page_data.scanned_files["type"] == "file", "label"] = file_label
            
            return {
                "success": True,
                "message": f"Updated entity labels: Directory={directory_label}, File={file_label}"
            }
        except Exception as e:
            return {"success": False, "error": f"Error updating entity labels: {str(e)}"}

    def prepare_for_map_page(self) -> Dict[str, Any]:
        """
        Prepare data for the map page.
        
        Returns:
            Dict[str, Any]: Result of the operation.
        """
        try:
            # Check if connected to Neo4j
            if not self.db_manager.is_connected():
                return {"success": False, "error": "Not connected to Neo4j"}
            
            # Get all nodes and relationships
            query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n, r, m
            """
            
            result = self.db_manager.query(query)
            
            if not result:
                return {"success": False, "error": "No data found in Neo4j"}
            
            # Process nodes
            nodes = []
            relationships = []
            node_ids = {}
            
            for record in result:
                # Process source node
                source_node = record.get("n")
                if source_node and source_node.id not in node_ids:
                    node_ids[source_node.id] = len(nodes)
                    nodes.append({
                        "id": source_node.id,
                        "labels": list(source_node.labels),
                        "properties": dict(source_node)
                    })
                
                # Process target node
                target_node = record.get("m")
                if target_node and target_node.id not in node_ids:
                    node_ids[target_node.id] = len(nodes)
                    nodes.append({
                        "id": target_node.id,
                        "labels": list(target_node.labels),
                        "properties": dict(target_node)
                    })
                
                # Process relationship
                rel = record.get("r")
                if rel and source_node and target_node:
                    relationships.append({
                        "id": rel.id,
                        "type": rel.type,
                        "properties": dict(rel),
                        "source": source_node.id,
                        "target": target_node.id
                    })
            
            return {
                "success": True,
                "message": f"Prepared data for map page: {len(nodes)} nodes and {len(relationships)} relationships",
                "nodes": nodes,
                "relationships": relationships
            }
        except Exception as e:
            return {"success": False, "error": f"Error preparing data for map page: {str(e)}"}