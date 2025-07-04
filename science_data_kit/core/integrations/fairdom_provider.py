"""
FAIRDOM-Hub Integration Provider for Science Data Kit

This module provides integration with the FAIRDOM-Hub platform, allowing users to
access and analyze data from FAIRDOM-Hub within the Science Data Kit environment.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

class FAIRDOMProvider:
    """
    Provider for integrating with the FAIRDOM-Hub platform.

    This class provides methods for authenticating with FAIRDOM-Hub, retrieving data,
    and performing operations on FAIRDOM-Hub resources.

    Attributes:
        base_url: The base URL of the FAIRDOM-Hub API.
        api_key: The API key for authenticating with FAIRDOM-Hub.
        session: The requests session for making API calls.
    """

    def __init__(
        self, 
        base_url: str = "https://fairdomhub.org/api",
        api_key: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Initialize the FAIRDOM-Hub provider.

        Args:
            base_url: The base URL of the FAIRDOM-Hub API.
            api_key: The API key for authenticating with FAIRDOM-Hub.
            token: An authentication token, if already obtained.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.token = token
        self.session = requests.Session()

        # Set up authentication if credentials are provided
        if api_key:
            self.session.headers.update({"Authorization": f"Token {api_key}"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate with FAIRDOM-Hub using username and password.

        Args:
            username: The username for FAIRDOM-Hub.
            password: The password for FAIRDOM-Hub.

        Returns:
            A tuple containing (success, message).
            - success: True if authentication was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/authenticate",
                json={"login": username, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    return True, "Authentication successful"
                else:
                    return False, "Authentication failed: No token received"
            else:
                return False, f"Authentication failed: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    def get_investigations(self) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of investigations from FAIRDOM-Hub.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of investigations if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/investigations")

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get investigations: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting investigations: {str(e)}"

    def get_investigation(self, investigation_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific investigation from FAIRDOM-Hub.

        Args:
            investigation_id: The ID of the investigation to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The investigation data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/investigations/{investigation_id}")

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get investigation: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting investigation: {str(e)}"

    def get_studies(self, investigation_id: Optional[str] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of studies from FAIRDOM-Hub.

        Args:
            investigation_id: Optional investigation ID to filter studies by investigation.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of studies if successful, or an error message if not.
        """
        try:
            url = f"{self.base_url}/studies"
            if investigation_id:
                url += f"?investigation_id={investigation_id}"

            response = self.session.get(url)

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get studies: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting studies: {str(e)}"

    def get_study(self, study_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific study from FAIRDOM-Hub.

        Args:
            study_id: The ID of the study to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The study data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/studies/{study_id}")

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get study: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting study: {str(e)}"

    def get_assays(self, study_id: Optional[str] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of assays from FAIRDOM-Hub.

        Args:
            study_id: Optional study ID to filter assays by study.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of assays if successful, or an error message if not.
        """
        try:
            url = f"{self.base_url}/assays"
            if study_id:
                url += f"?study_id={study_id}"

            response = self.session.get(url)

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get assays: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting assays: {str(e)}"

    def get_assay(self, assay_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific assay from FAIRDOM-Hub.

        Args:
            assay_id: The ID of the assay to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The assay data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/assays/{assay_id}")

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get assay: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting assay: {str(e)}"

    def get_data_files(self, assay_id: Optional[str] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of data files from FAIRDOM-Hub.

        Args:
            assay_id: Optional assay ID to filter data files by assay.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of data files if successful, or an error message if not.
        """
        try:
            url = f"{self.base_url}/data_files"
            if assay_id:
                url += f"?assay_id={assay_id}"

            response = self.session.get(url)

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get data files: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting data files: {str(e)}"

    def get_data_file(self, data_file_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific data file from FAIRDOM-Hub.

        Args:
            data_file_id: The ID of the data file to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The data file data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/data_files/{data_file_id}")

            if response.status_code == 200:
                return True, response.json()["data"]
            else:
                return False, f"Failed to get data file: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting data file: {str(e)}"

    def download_data_file(self, data_file_id: str, destination: str) -> Tuple[bool, str]:
        """
        Download a data file from FAIRDOM-Hub.

        Args:
            data_file_id: The ID of the data file to download.
            destination: The path where the file should be saved.

        Returns:
            A tuple containing (success, message).
            - success: True if the download was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            response = self.session.get(
                f"{self.base_url}/data_files/{data_file_id}/download",
                stream=True
            )

            if response.status_code == 200:
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True, f"File downloaded successfully to {destination}"
            else:
                return False, f"Failed to download file: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error downloading file: {str(e)}"

    def import_to_neo4j(self, data: Dict[str, Any], db_manager: Any) -> Tuple[bool, str]:
        """
        Import data from FAIRDOM-Hub into Neo4j.

        Args:
            data: The data to import.
            db_manager: The Neo4j database manager to use for importing.

        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            # Create nodes for investigations
            if "investigations" in data:
                for investigation in data["investigations"]:
                    query = """
                    MERGE (i:Investigation:FAIRDOM {id: $id})
                    SET i.title = $attributes.title,
                        i.description = $attributes.description,
                        i.created_at = $attributes.created_at,
                        i.updated_at = $attributes.updated_at,
                        i.source = 'FAIRDOM-Hub'
                    RETURN i
                    """
                    db_manager.execute_query(query, params=investigation)

            # Create nodes for studies and link to investigations
            if "studies" in data:
                for study in data["studies"]:
                    query = """
                    MERGE (s:Study:FAIRDOM {id: $id})
                    SET s.title = $attributes.title,
                        s.description = $attributes.description,
                        s.created_at = $attributes.created_at,
                        s.updated_at = $attributes.updated_at,
                        s.source = 'FAIRDOM-Hub'
                    WITH s
                    MATCH (i:Investigation:FAIRDOM {id: $relationships.investigation.data.id})
                    MERGE (i)-[:CONTAINS]->(s)
                    RETURN s
                    """
                    db_manager.execute_query(query, params=study)

            # Create nodes for assays and link to studies
            if "assays" in data:
                for assay in data["assays"]:
                    query = """
                    MERGE (a:Assay:FAIRDOM {id: $id})
                    SET a.title = $attributes.title,
                        a.description = $attributes.description,
                        a.assay_type = $attributes.assay_type,
                        a.technology_type = $attributes.technology_type,
                        a.created_at = $attributes.created_at,
                        a.updated_at = $attributes.updated_at,
                        a.source = 'FAIRDOM-Hub'
                    WITH a
                    MATCH (s:Study:FAIRDOM {id: $relationships.study.data.id})
                    MERGE (s)-[:CONTAINS]->(a)
                    RETURN a
                    """
                    db_manager.execute_query(query, params=assay)

            # Create nodes for data files and link to assays
            if "data_files" in data:
                for data_file in data["data_files"]:
                    query = """
                    MERGE (d:DataFile:FAIRDOM {id: $id})
                    SET d.title = $attributes.title,
                        d.description = $attributes.description,
                        d.content_type = $attributes.content_type,
                        d.file_size = $attributes.file_size,
                        d.created_at = $attributes.created_at,
                        d.updated_at = $attributes.updated_at,
                        d.source = 'FAIRDOM-Hub'
                    WITH d
                    MATCH (a:Assay:FAIRDOM {id: $relationships.assay.data.id})
                    MERGE (a)-[:CONTAINS]->(d)
                    RETURN d
                    """
                    db_manager.execute_query(query, params=data_file)

            return True, "Data imported successfully"

        except Exception as e:
            return False, f"Error importing data: {str(e)}"
