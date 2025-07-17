"""
cBioPortal Browser Page Module for Science Data Kit Core

This module provides the cBioPortal Browser page for the Science Data Kit application.
It defines the framework-independent core functionality for the cBioPortal Browser page.
"""

from typing import Dict, Any, List, Optional, Set
import requests

from science_data_kit.core.pages.base import BasePage
from science_data_kit.core.models.page import CbioportalBrowserPageData
from science_data_kit.core.db.db_manager import db_manager

# Constants
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
ONCOTREE_API_URL = "http://oncotree.mskcc.org/api"

class CbioportalBrowserPage(BasePage):
    """
    cBioPortal Browser page for browsing and managing ontology terms.

    This class provides the core business logic for the cBioPortal Browser page,
    independent of any UI framework.
    """

    def __init__(self, db_connection=None):
        """Initialize the cBioPortal Browser page."""
        super().__init__(db_connection)
        self.db_manager = db_manager
        self.terms = []
        self.existing_term_accessions = set()
        self.connection_status = {"neo4j": False}
        self.connection_errors = {}

    def get_page_data(self) -> CbioportalBrowserPageData:
        """
        Return data needed to render the cBioPortal Browser page.

        Returns:
            An instance of CbioportalBrowserPageData containing the data needed
            to render the cBioPortal Browser page.
        """
        return CbioportalBrowserPageData(
            title="cBioPortal Browser",
            requires_auth=True,
            cancer_types=self._get_cancer_types(),
            tumor_types=self._get_oncotree_tumor_types(),
            studies=self._get_cbioportal_studies(),
            terms=self.terms,
            existing_term_accessions=self.existing_term_accessions,
            connection_status=self.connection_status,
            connection_errors=self.connection_errors
        )

    def connect_to_database(self, uri: str, username: str, password: str, database: str, conn_name: str = None) -> Dict[str, Any]:
        """
        Connect to a database.

        Args:
            uri: The URI of the Neo4j server.
            username: The username for authentication.
            password: The password for authentication.
            database: The name of the database to connect to.
            conn_name: The name of the connection (optional).

        Returns:
            A dictionary with connection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }

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
                result["error"] = f"Failed to connect to Neo4j: {error_msg}"
                self.connection_errors["neo4j"] = error_msg
                return result

            # Update connection status
            self.connection_status["neo4j"] = True

            result["success"] = True
            return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to connect to Neo4j: {error_msg}"
            self.connection_errors["neo4j"] = error_msg
            return result

    def disconnect_from_database(self) -> Dict[str, Any]:
        """
        Disconnect from the database.

        Returns:
            A dictionary with disconnection status and error message if any.
        """
        result = {
            "success": False,
            "error": None
        }

        try:
            # Close the connection
            self.db_manager.close()

            # Update connection status
            self.connection_status["neo4j"] = False

            result["success"] = True
            return result
        except Exception as e:
            error_msg = str(e)
            result["error"] = f"Failed to disconnect from Neo4j: {error_msg}"
            self.connection_errors["neo4j"] = error_msg
            return result

    def _get_cancer_types(self) -> List[Dict[str, Any]]:
        """
        Get the list of cancer types from cBioPortal API.

        Returns:
            List of dictionaries containing cancer type information.
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/cancer-types")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def _get_oncotree_tumor_types(self) -> List[Dict[str, Any]]:
        """
        Get the list of tumor types from OncoTree API.

        Returns:
            List of dictionaries containing tumor type information.
        """
        try:
            response = requests.get(f"{ONCOTREE_API_URL}/tumorTypes")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def _get_cbioportal_studies(self) -> List[Dict[str, Any]]:
        """
        Get the list of studies from cBioPortal API.

        Returns:
            List of dictionaries containing study information.
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def _load_cbioportal_study_data(self, study_id: str) -> Dict[str, Any]:
        """
        Load study data from cBioPortal API.

        Args:
            study_id: The ID of the study to load

        Returns:
            Dictionary containing study data
        """
        try:
            response = requests.get(f"{CBIOPORTAL_API_URL}/studies/{study_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {}

    def add_cancer_types_to_terms(self) -> Dict[str, Any]:
        """
        Add cancer types to terms.

        Returns:
            Dictionary with status and message.
        """
        result = {
            "success": False,
            "message": "",
            "added_count": 0
        }

        cancer_types = self._get_cancer_types()
        if not cancer_types:
            result["message"] = "Failed to load cancer types."
            return result

        # Add cancer types to terms
        added_count = 0
        for cancer_type in cancer_types:
            if "name" in cancer_type and "cancerTypeId" in cancer_type:
                term = {
                    "term": cancer_type["name"],
                    "term_accession": cancer_type["cancerTypeId"],
                    "term_source": "cBioPortal"
                }
                if term["term_accession"] not in self.existing_term_accessions:
                    self.terms.append(term)
                    self.existing_term_accessions.add(term["term_accession"])
                    added_count += 1

        result["added_count"] = added_count
        if added_count > 0:
            result["success"] = True
            result["message"] = f"Added {added_count} cancer type terms."
        else:
            result["message"] = "All cancer type terms are already loaded."

        return result

    def add_tumor_types_to_terms(self) -> Dict[str, Any]:
        """
        Add tumor types to terms.

        Returns:
            Dictionary with status and message.
        """
        result = {
            "success": False,
            "message": "",
            "added_count": 0
        }

        tumor_types = self._get_oncotree_tumor_types()
        if not tumor_types:
            result["message"] = "Failed to load tumor types."
            return result

        # Add tumor types to terms
        added_count = 0
        for tumor_type in tumor_types:
            if "name" in tumor_type and "code" in tumor_type:
                term = {
                    "term": tumor_type["name"],
                    "term_accession": tumor_type["code"],
                    "term_source": "OncoTree"
                }
                if term["term_accession"] not in self.existing_term_accessions:
                    self.terms.append(term)
                    self.existing_term_accessions.add(term["term_accession"])
                    added_count += 1

        result["added_count"] = added_count
        if added_count > 0:
            result["success"] = True
            result["message"] = f"Added {added_count} tumor type terms."
        else:
            result["message"] = "All tumor type terms are already loaded."

        return result

    def add_study_data_to_terms(self, study_id: str) -> Dict[str, Any]:
        """
        Add study data to terms.

        Args:
            study_id: The ID of the study to load

        Returns:
            Dictionary with status and message.
        """
        result = {
            "success": False,
            "message": "",
            "added_count": 0
        }

        study_data = self._load_cbioportal_study_data(study_id)
        if not study_data:
            result["message"] = "Failed to load study data."
            return result

        # Extract relevant terms from study data
        new_terms = []

        # Add cancer type as a term
        if "cancerType" in study_data:
            new_terms.append({
                "term": study_data["cancerType"].get("name", ""),
                "term_accession": study_data["cancerType"].get("cancerTypeId", ""),
                "term_source": "cBioPortal"
            })

        # Add other relevant terms
        if "referenceGenome" in study_data:
            new_terms.append({
                "term": f"Reference Genome: {study_data['referenceGenome']}",
                "term_accession": f"genome:{study_data['referenceGenome']}",
                "term_source": "cBioPortal"
            })

        # Add only new terms that don't exist yet
        added_count = 0
        for term in new_terms:
            if term["term_accession"] and term["term_accession"] not in self.existing_term_accessions:
                self.terms.append(term)
                self.existing_term_accessions.add(term["term_accession"])
                added_count += 1

        result["added_count"] = added_count
        if added_count > 0:
            result["success"] = True
            result["message"] = f"Added {added_count} terms from study."
        else:
            result["message"] = "No new terms found in study."

        return result

    def add_term_manually(self, term_name: str, term_uri: str, ontology_source: str) -> Dict[str, Any]:
        """
        Add a term manually.

        Args:
            term_name: The name of the term
            term_uri: The URI of the term
            ontology_source: The source of the ontology

        Returns:
            Dictionary with status and message.
        """
        result = {
            "success": False,
            "message": ""
        }

        if not term_name or not term_uri or not ontology_source:
            result["message"] = "Term name, URI, and ontology source are required."
            return result

        # Create new term
        new_term = {
            "term": term_name,
            "term_accession": term_uri,
            "term_source": ontology_source
        }

        # Check if term already exists
        if new_term["term_accession"] not in self.existing_term_accessions:
            self.terms.append(new_term)
            self.existing_term_accessions.add(new_term["term_accession"])
            result["success"] = True
            result["message"] = f"Added term: {term_name}"
        else:
            result["message"] = f"Term with URI {term_uri} already exists."

        return result

    def clear_terms(self) -> Dict[str, Any]:
        """
        Clear all terms.

        Returns:
            Dictionary with status and message.
        """
        result = {
            "success": True,
            "message": f"Cleared {len(self.terms)} terms."
        }

        self.terms = []
        self.existing_term_accessions = set()

        return result