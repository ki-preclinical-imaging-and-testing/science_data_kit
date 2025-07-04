"""
NC3Rs EDA Tool Integration Provider for Science Data Kit

This module provides integration with the NC3Rs Experimental Design Assistant (EDA) tool,
allowing users to access and analyze data from the NC3Rs EDA tool within the Science Data Kit environment.

The NC3Rs (National Centre for the Replacement, Refinement and Reduction of Animals in Research)
EDA tool is a free online resource that helps researchers design robust and reproducible animal experiments.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

class NC3RsEDAProvider:
    """
    Provider for integrating with the NC3Rs Experimental Design Assistant (EDA) tool.
    
    This class provides methods for importing data from NC3Rs EDA tool JSON files,
    mapping the data to the Science Data Kit's data model, and importing it into Neo4j.
    
    Attributes:
        base_url: The base URL of the NC3Rs EDA tool API (if applicable).
        api_key: The API key for authenticating with NC3Rs EDA tool (if applicable).
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the NC3Rs EDA tool provider.
        
        Args:
            base_url: The base URL of the NC3Rs EDA tool API (if applicable).
            api_key: The API key for authenticating with NC3Rs EDA tool (if applicable).
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up authentication if credentials are provided
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def import_json_file(self, file_path: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Import data from a NC3Rs EDA tool JSON file.
        
        Args:
            file_path: The path to the JSON file.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the import was successful, False otherwise.
            - result: The imported data if successful, or an error message if not.
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
            return False, f"Error importing JSON file: {str(e)}"
    
    def map_data(self, data: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Map NC3Rs EDA tool data to the Science Data Kit's data model.
        
        Args:
            data: The data to map.
            
        Returns:
            A tuple containing (success, result).
            - success: True if the mapping was successful, False otherwise.
            - result: The mapped data if successful, or an error message if not.
        """
        try:
            # Initialize the mapped data structure
            mapped_data = {
                "experiments": [],
                "designs": [],
                "variables": [],
                "outcomes": [],
                "sample_size_calculations": []
            }
            
            # Map experiment data
            if "experiment" in data:
                experiment = data["experiment"]
                mapped_experiment = {
                    "id": experiment.get("id", ""),
                    "name": experiment.get("name", ""),
                    "description": experiment.get("description", ""),
                    "created_at": experiment.get("created_at", ""),
                    "updated_at": experiment.get("updated_at", ""),
                    "source": "NC3Rs EDA"
                }
                mapped_data["experiments"].append(mapped_experiment)
            
            # Map design data
            if "design" in data:
                design = data["design"]
                mapped_design = {
                    "id": design.get("id", ""),
                    "name": design.get("name", ""),
                    "description": design.get("description", ""),
                    "type": design.get("type", ""),
                    "blinding": design.get("blinding", False),
                    "randomization": design.get("randomization", False),
                    "experiment_id": data.get("experiment", {}).get("id", ""),
                    "source": "NC3Rs EDA"
                }
                mapped_data["designs"].append(mapped_design)
            
            # Map variables data
            if "variables" in data:
                for variable in data["variables"]:
                    mapped_variable = {
                        "id": variable.get("id", ""),
                        "name": variable.get("name", ""),
                        "type": variable.get("type", ""),
                        "values": variable.get("values", []),
                        "design_id": data.get("design", {}).get("id", ""),
                        "source": "NC3Rs EDA"
                    }
                    mapped_data["variables"].append(mapped_variable)
            
            # Map outcomes data
            if "outcomes" in data:
                for outcome in data["outcomes"]:
                    mapped_outcome = {
                        "id": outcome.get("id", ""),
                        "name": outcome.get("name", ""),
                        "description": outcome.get("description", ""),
                        "type": outcome.get("type", ""),
                        "design_id": data.get("design", {}).get("id", ""),
                        "source": "NC3Rs EDA"
                    }
                    mapped_data["outcomes"].append(mapped_outcome)
            
            # Map sample size calculations data
            if "sample_size_calculations" in data:
                for calculation in data["sample_size_calculations"]:
                    mapped_calculation = {
                        "id": calculation.get("id", ""),
                        "method": calculation.get("method", ""),
                        "effect_size": calculation.get("effect_size", ""),
                        "alpha": calculation.get("alpha", ""),
                        "power": calculation.get("power", ""),
                        "sample_size": calculation.get("sample_size", ""),
                        "design_id": data.get("design", {}).get("id", ""),
                        "source": "NC3Rs EDA"
                    }
                    mapped_data["sample_size_calculations"].append(mapped_calculation)
            
            return True, mapped_data
        
        except Exception as e:
            return False, f"Error mapping data: {str(e)}"
    
    def import_to_neo4j(self, data: Dict[str, Any], db_manager: Any) -> Tuple[bool, str]:
        """
        Import NC3Rs EDA tool data into Neo4j.
        
        Args:
            data: The data to import.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            # Create nodes for experiments
            if "experiments" in data:
                for experiment in data["experiments"]:
                    query = """
                    MERGE (e:Experiment:NC3RsEDA {id: $id})
                    SET e.name = $name,
                        e.description = $description,
                        e.created_at = $created_at,
                        e.updated_at = $updated_at,
                        e.source = $source
                    RETURN e
                    """
                    db_manager.execute_query(query, params=experiment)
            
            # Create nodes for designs and link to experiments
            if "designs" in data:
                for design in data["designs"]:
                    query = """
                    MERGE (d:Design:NC3RsEDA {id: $id})
                    SET d.name = $name,
                        d.description = $description,
                        d.type = $type,
                        d.blinding = $blinding,
                        d.randomization = $randomization,
                        d.source = $source
                    WITH d
                    MATCH (e:Experiment:NC3RsEDA {id: $experiment_id})
                    MERGE (e)-[:HAS_DESIGN]->(d)
                    RETURN d
                    """
                    db_manager.execute_query(query, params=design)
            
            # Create nodes for variables and link to designs
            if "variables" in data:
                for variable in data["variables"]:
                    query = """
                    MERGE (v:Variable:NC3RsEDA {id: $id})
                    SET v.name = $name,
                        v.type = $type,
                        v.values = $values,
                        v.source = $source
                    WITH v
                    MATCH (d:Design:NC3RsEDA {id: $design_id})
                    MERGE (d)-[:HAS_VARIABLE]->(v)
                    RETURN v
                    """
                    db_manager.execute_query(query, params=variable)
            
            # Create nodes for outcomes and link to designs
            if "outcomes" in data:
                for outcome in data["outcomes"]:
                    query = """
                    MERGE (o:Outcome:NC3RsEDA {id: $id})
                    SET o.name = $name,
                        o.description = $description,
                        o.type = $type,
                        o.source = $source
                    WITH o
                    MATCH (d:Design:NC3RsEDA {id: $design_id})
                    MERGE (d)-[:HAS_OUTCOME]->(o)
                    RETURN o
                    """
                    db_manager.execute_query(query, params=outcome)
            
            # Create nodes for sample size calculations and link to designs
            if "sample_size_calculations" in data:
                for calculation in data["sample_size_calculations"]:
                    query = """
                    MERGE (s:SampleSizeCalculation:NC3RsEDA {id: $id})
                    SET s.method = $method,
                        s.effect_size = $effect_size,
                        s.alpha = $alpha,
                        s.power = $power,
                        s.sample_size = $sample_size,
                        s.source = $source
                    WITH s
                    MATCH (d:Design:NC3RsEDA {id: $design_id})
                    MERGE (d)-[:HAS_SAMPLE_SIZE_CALCULATION]->(s)
                    RETURN s
                    """
                    db_manager.execute_query(query, params=calculation)
            
            return True, "Data imported successfully"
        
        except Exception as e:
            return False, f"Error importing data: {str(e)}"
    
    def search(self, query: str, data: Dict[str, Any]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Search for resources in NC3Rs EDA tool data.
        
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
            
            # Search in experiments
            if "experiments" in data:
                for experiment in data["experiments"]:
                    if (query.lower() in experiment.get("name", "").lower() or
                        query.lower() in experiment.get("description", "").lower()):
                        results.append({
                            "type": "experiment",
                            "id": experiment.get("id", ""),
                            "name": experiment.get("name", ""),
                            "description": experiment.get("description", "")
                        })
            
            # Search in designs
            if "designs" in data:
                for design in data["designs"]:
                    if (query.lower() in design.get("name", "").lower() or
                        query.lower() in design.get("description", "").lower() or
                        query.lower() in design.get("type", "").lower()):
                        results.append({
                            "type": "design",
                            "id": design.get("id", ""),
                            "name": design.get("name", ""),
                            "description": design.get("description", "")
                        })
            
            # Search in variables
            if "variables" in data:
                for variable in data["variables"]:
                    if query.lower() in variable.get("name", "").lower():
                        results.append({
                            "type": "variable",
                            "id": variable.get("id", ""),
                            "name": variable.get("name", ""),
                            "type": variable.get("type", "")
                        })
            
            # Search in outcomes
            if "outcomes" in data:
                for outcome in data["outcomes"]:
                    if (query.lower() in outcome.get("name", "").lower() or
                        query.lower() in outcome.get("description", "").lower()):
                        results.append({
                            "type": "outcome",
                            "id": outcome.get("id", ""),
                            "name": outcome.get("name", ""),
                            "description": outcome.get("description", "")
                        })
            
            return True, results
        
        except Exception as e:
            return False, f"Error searching: {str(e)}"
    
    def process_and_import(self, file_path: str, db_manager: Any) -> Tuple[bool, str]:
        """
        Process a NC3Rs EDA tool JSON file and import it into Neo4j.
        
        This is a convenience method that combines import_json_file, map_data, and import_to_neo4j.
        
        Args:
            file_path: The path to the JSON file.
            db_manager: The Neo4j database manager to use for importing.
            
        Returns:
            A tuple containing (success, message).
            - success: True if the process was successful, False otherwise.
            - message: A message describing the result.
        """
        # Import the JSON file
        success, result = self.import_json_file(file_path)
        if not success:
            return False, result
        
        # Map the data
        success, mapped_data = self.map_data(result)
        if not success:
            return False, mapped_data
        
        # Import the data into Neo4j
        return self.import_to_neo4j(mapped_data, db_manager)