"""
ISA JSON Handler for Science Data Kit

This module provides functionality for handling ISA JSON files in the ISA Tools integration,
allowing users to import and process ISA metadata.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple, Union

class ISAJSONHandler:
    """
    Handler for ISA JSON operations in the ISA Tools integration.
    
    This class provides methods for importing and processing ISA metadata from JSON files.
    """
    
    def __init__(self):
        """
        Initialize the ISA JSON Handler.
        """
        pass
    
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