"""
Test script for cBioPortal Browser API endpoints

This script tests the Flask API endpoints for the cBioPortal browser page.
It verifies that the endpoints return the expected responses.
"""

import unittest
import json
import os
import sys
from flask import Flask, session
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from science_data_kit.web.routes import main_bp
from science_data_kit.core.pages.cbioportal_browser import CbioportalBrowserPage

class CbioportalAPITest(unittest.TestCase):
    """Test case for cBioPortal Browser API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.register_blueprint(main_bp)
        
        # Create a test client
        self.client = self.app.test_client()
        
        # Create a test context
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        # Set up session for login_required decorator
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'test_user'

    def tearDown(self):
        """Tear down the test environment."""
        self.ctx.pop()

    def test_cbioportal_browser_page(self):
        """Test the cBioPortal browser page endpoint."""
        response = self.client.get('/cbioportal')
        self.assertEqual(response.status_code, 200)

    def test_cancer_types_endpoint(self):
        """Test the cancer types API endpoint."""
        mock_cancer_types = [
            {"cancerTypeId": "acc", "name": "Adrenocortical Carcinoma"},
            {"cancerTypeId": "blca", "name": "Bladder Urothelial Carcinoma"}
        ]
        
        with patch.object(CbioportalBrowserPage, '_get_cancer_types', return_value=mock_cancer_types):
            response = self.client.get('/api/cbioportal/cancer-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_cancer_types)

    def test_tumor_types_endpoint(self):
        """Test the tumor types API endpoint."""
        mock_tumor_types = [
            {"code": "ACPG", "name": "Acinar Cell Carcinoma, Pancreas"},
            {"code": "ACN", "name": "Acinar Cell Neoplasm"}
        ]
        
        with patch.object(CbioportalBrowserPage, '_get_oncotree_tumor_types', return_value=mock_tumor_types):
            response = self.client.get('/api/cbioportal/tumor-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_tumor_types)

    def test_studies_endpoint(self):
        """Test the studies API endpoint."""
        mock_studies = [
            {"studyId": "acc_tcga", "name": "Adrenocortical Carcinoma (TCGA)"},
            {"studyId": "blca_tcga", "name": "Bladder Urothelial Carcinoma (TCGA)"}
        ]
        
        with patch.object(CbioportalBrowserPage, '_get_cbioportal_studies', return_value=mock_studies):
            response = self.client.get('/api/cbioportal/studies')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_studies)

    def test_study_endpoint(self):
        """Test the study API endpoint."""
        mock_study = {
            "studyId": "acc_tcga",
            "name": "Adrenocortical Carcinoma (TCGA)",
            "description": "TCGA Adrenocortical Carcinoma",
            "cancerType": {"cancerTypeId": "acc", "name": "Adrenocortical Carcinoma"},
            "referenceGenome": "hg19"
        }
        
        with patch.object(CbioportalBrowserPage, '_load_cbioportal_study_data', return_value=mock_study):
            response = self.client.get('/api/cbioportal/study/acc_tcga')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_study)

    def test_add_cancer_types_endpoint(self):
        """Test the add cancer types API endpoint."""
        mock_result = {
            "success": True,
            "message": "Added 2 cancer type terms.",
            "added_count": 2
        }
        
        with patch.object(CbioportalBrowserPage, 'add_cancer_types_to_terms', return_value=mock_result):
            response = self.client.post('/api/cbioportal/add-cancer-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_add_tumor_types_endpoint(self):
        """Test the add tumor types API endpoint."""
        mock_result = {
            "success": True,
            "message": "Added 2 tumor type terms.",
            "added_count": 2
        }
        
        with patch.object(CbioportalBrowserPage, 'add_tumor_types_to_terms', return_value=mock_result):
            response = self.client.post('/api/cbioportal/add-tumor-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_add_study_data_endpoint(self):
        """Test the add study data API endpoint."""
        mock_result = {
            "success": True,
            "message": "Added 2 terms from study.",
            "added_count": 2
        }
        
        with patch.object(CbioportalBrowserPage, 'add_study_data_to_terms', return_value=mock_result):
            response = self.client.post('/api/cbioportal/add-study-data', data={
                'study_id': 'acc_tcga'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_add_term_endpoint(self):
        """Test the add term API endpoint."""
        mock_result = {
            "success": True,
            "message": "Added term: Test Term"
        }
        
        with patch.object(CbioportalBrowserPage, 'add_term_manually', return_value=mock_result):
            response = self.client.post('/api/cbioportal/add-term', data={
                'term_name': 'Test Term',
                'term_uri': 'http://example.com/terms/test',
                'ontology_source': 'Test Source'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_clear_terms_endpoint(self):
        """Test the clear terms API endpoint."""
        mock_result = {
            "success": True,
            "message": "Cleared 5 terms."
        }
        
        with patch.object(CbioportalBrowserPage, 'clear_terms', return_value=mock_result):
            response = self.client.post('/api/cbioportal/clear-terms')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_terms_endpoint(self):
        """Test the terms API endpoint."""
        mock_terms = [
            {"term": "Adrenocortical Carcinoma", "term_accession": "acc", "term_source": "cBioPortal"},
            {"term": "Bladder Urothelial Carcinoma", "term_accession": "blca", "term_source": "cBioPortal"}
        ]
        
        mock_page = MagicMock()
        mock_page.terms = mock_terms
        
        with patch('science_data_kit.web.routes.CbioportalBrowserPage', return_value=mock_page):
            response = self.client.get('/api/cbioportal/terms')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['terms'], mock_terms)

if __name__ == '__main__':
    unittest.main()