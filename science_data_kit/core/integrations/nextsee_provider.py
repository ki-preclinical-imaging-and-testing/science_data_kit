"""
NExtSEEK Integration Provider for Science Data Kit

This module provides integration with the NExtSEEK platform, allowing users to
access and analyze data from NExtSEEK within the Science Data Kit environment.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

class NExtSEEKProvider:
    """
    Provider for integrating with the NExtSEEK platform.

    This class provides methods for authenticating with NExtSEEK, retrieving data,
    and performing operations on NExtSEEK resources.

    Attributes:
        base_url: The base URL of the NExtSEEK API.
        api_key: The API key for authenticating with NExtSEEK.
        session: The requests session for making API calls.
    """

    def __init__(
        self, 
        base_url: str = "https://nextsee.org/api/v1",
        api_key: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Initialize the NExtSEEK provider.

        Args:
            base_url: The base URL of the NExtSEEK API.
            api_key: The API key for authenticating with NExtSEEK.
            token: An authentication token, if already obtained.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.token = token
        self.session = requests.Session()

        # Set up authentication if credentials are provided
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate with NExtSEEK using username and password.

        Args:
            username: The username for NExtSEEK.
            password: The password for NExtSEEK.

        Returns:
            A tuple containing (success, message).
            - success: True if authentication was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
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

    def get_projects(self) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of projects from NExtSEEK.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of projects if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/projects")

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get projects: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting projects: {str(e)}"

    def get_project_data(self, project_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific project from NExtSEEK.

        Args:
            project_id: The ID of the project to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The project data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}")

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get project data: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting project data: {str(e)}"

    def get_experiments(self, project_id: Optional[str] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Get a list of experiments from NExtSEEK.

        Args:
            project_id: Optional project ID to filter experiments by project.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: A list of experiments if successful, or an error message if not.
        """
        try:
            url = f"{self.base_url}/experiments"
            if project_id:
                url += f"?project_id={project_id}"

            response = self.session.get(url)

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get experiments: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting experiments: {str(e)}"

    def get_experiment_data(self, experiment_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Get data for a specific experiment from NExtSEEK.

        Args:
            experiment_id: The ID of the experiment to retrieve.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The experiment data if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/experiments/{experiment_id}")

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get experiment data: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error getting experiment data: {str(e)}"

    def search(self, query: str) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Search for resources in NExtSEEK.

        Args:
            query: The search query.

        Returns:
            A tuple containing (success, result).
            - success: True if the request was successful, False otherwise.
            - result: The search results if successful, or an error message if not.
        """
        try:
            response = self.session.get(f"{self.base_url}/search?q={query}")

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to search: {response.status_code} - {response.text}"

        except Exception as e:
            return False, f"Error searching: {str(e)}"

    def import_to_neo4j(self, data: Dict[str, Any], db_manager: Any) -> Tuple[bool, str]:
        """
        Import data from NExtSEEK into Neo4j.

        Args:
            data: The data to import.
            db_manager: The Neo4j database manager to use for importing.

        Returns:
            A tuple containing (success, message).
            - success: True if the import was successful, False otherwise.
            - message: A message describing the result.
        """
        try:
            # Create nodes for projects
            if "projects" in data:
                for project in data["projects"]:
                    query = """
                    MERGE (p:Project:NExtSEEK {id: $id})
                    SET p.name = $name,
                        p.description = $description,
                        p.created_at = $created_at,
                        p.updated_at = $updated_at,
                        p.source = 'NExtSEEK'
                    RETURN p
                    """
                    db_manager.execute_query(query, params=project)

            # Create nodes for experiments and link to projects
            if "experiments" in data:
                for experiment in data["experiments"]:
                    query = """
                    MERGE (e:Experiment:NExtSEEK {id: $id})
                    SET e.name = $name,
                        e.description = $description,
                        e.created_at = $created_at,
                        e.updated_at = $updated_at,
                        e.source = 'NExtSEEK'
                    WITH e
                    MATCH (p:Project:NExtSEEK {id: $project_id})
                    MERGE (p)-[:CONTAINS]->(e)
                    RETURN e
                    """
                    db_manager.execute_query(query, params=experiment)

            # Create nodes for samples and link to experiments
            if "samples" in data:
                for sample in data["samples"]:
                    query = """
                    MERGE (s:Sample:NExtSEEK {id: $id})
                    SET s.name = $name,
                        s.description = $description,
                        s.created_at = $created_at,
                        s.updated_at = $updated_at,
                        s.source = 'NExtSEEK'
                    WITH s
                    MATCH (e:Experiment:NExtSEEK {id: $experiment_id})
                    MERGE (e)-[:CONTAINS]->(s)
                    RETURN s
                    """
                    db_manager.execute_query(query, params=sample)

            return True, "Data imported successfully"

        except Exception as e:
            return False, f"Error importing data: {str(e)}"
