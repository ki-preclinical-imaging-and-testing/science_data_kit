"""
Test script for ISA Browser API endpoints

This script tests the Flask API endpoints for the ISA browser page.
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
from science_data_kit.core.pages.isa_browser import IsaBrowserPage

class IsaAPITest(unittest.TestCase):
    """Test case for ISA Browser API endpoints."""

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

    def test_isa_browser_page(self):
        """Test the ISA browser page endpoint."""
        response = self.client.get('/isa-browser')
        self.assertEqual(response.status_code, 200)

    def test_connect_to_neo4j_endpoint(self):
        """Test the connect to Neo4j API endpoint."""
        mock_result = {
            "success": True
        }
        
        with patch.object(IsaBrowserPage, 'connect_to_database', return_value=mock_result):
            response = self.client.post('/api/isa/connect', data={
                'uri': 'bolt://localhost:7687',
                'username': 'neo4j',
                'password': 'password',
                'database': 'neo4j',
                'conn_name': 'test_connection'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_disconnect_from_neo4j_endpoint(self):
        """Test the disconnect from Neo4j API endpoint."""
        mock_result = {
            "success": True
        }
        
        with patch.object(IsaBrowserPage, 'disconnect_from_database', return_value=mock_result):
            response = self.client.post('/api/isa/disconnect')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_standard_isa_terms_endpoint(self):
        """Test the standard ISA terms API endpoint."""
        mock_terms = [
            MagicMock(term="organism", term_accession="http://purl.obolibrary.org/obo/OBI_0100026", term_source=MagicMock(name="ISA")),
            MagicMock(term="organism part", term_accession="http://purl.obolibrary.org/obo/OBI_0000257", term_source=MagicMock(name="ISA"))
        ]
        
        with patch.object(IsaBrowserPage, '_get_standard_isa_terms', return_value=mock_terms):
            response = self.client.get('/api/isa/standard-terms')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['term'], "organism")
            self.assertEqual(data[1]['term'], "organism part")

    def test_cancer_types_endpoint(self):
        """Test the cancer types API endpoint."""
        mock_cancer_types = [
            {"cancerTypeId": "acc", "name": "Adrenocortical Carcinoma"},
            {"cancerTypeId": "blca", "name": "Bladder Urothelial Carcinoma"}
        ]
        
        with patch.object(IsaBrowserPage, '_get_cancer_types', return_value=mock_cancer_types):
            response = self.client.get('/api/isa/cancer-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_cancer_types)

    def test_tumor_types_endpoint(self):
        """Test the tumor types API endpoint."""
        mock_tumor_types = [
            {"code": "ACPG", "name": "Acinar Cell Carcinoma, Pancreas"},
            {"code": "ACN", "name": "Acinar Cell Neoplasm"}
        ]
        
        with patch.object(IsaBrowserPage, '_get_oncotree_tumor_types', return_value=mock_tumor_types):
            response = self.client.get('/api/isa/tumor-types')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_tumor_types)

    def test_studies_endpoint(self):
        """Test the studies API endpoint."""
        mock_studies = [
            {"studyId": "acc_tcga", "name": "Adrenocortical Carcinoma (TCGA)"},
            {"studyId": "blca_tcga", "name": "Bladder Urothelial Carcinoma (TCGA)"}
        ]
        
        with patch.object(IsaBrowserPage, '_get_cbioportal_studies', return_value=mock_studies):
            response = self.client.get('/api/isa/studies')
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
        
        with patch.object(IsaBrowserPage, '_load_cbioportal_study_data', return_value=mock_study):
            response = self.client.get('/api/isa/study/acc_tcga')
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
        
        with patch.object(IsaBrowserPage, 'add_cancer_types_to_terms', return_value=mock_result):
            response = self.client.post('/api/isa/add-cancer-types')
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
        
        with patch.object(IsaBrowserPage, 'add_tumor_types_to_terms', return_value=mock_result):
            response = self.client.post('/api/isa/add-tumor-types')
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
        
        with patch.object(IsaBrowserPage, 'add_study_data_to_terms', return_value=mock_result):
            response = self.client.post('/api/isa/add-study-data', data={
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
        
        with patch.object(IsaBrowserPage, 'add_term_manually', return_value=mock_result):
            response = self.client.post('/api/isa/add-term', data={
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
        
        with patch.object(IsaBrowserPage, 'clear_terms', return_value=mock_result):
            response = self.client.post('/api/isa/clear-terms')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

    def test_terms_endpoint(self):
        """Test the terms API endpoint."""
        mock_page = MagicMock()
        mock_page.terms = [
            MagicMock(term="organism", term_accession="http://purl.obolibrary.org/obo/OBI_0100026", term_source=MagicMock(name="ISA")),
            MagicMock(term="organism part", term_accession="http://purl.obolibrary.org/obo/OBI_0000257", term_source=MagicMock(name="ISA"))
        ]
        mock_page.existing_term_accessions = set(["http://purl.obolibrary.org/obo/OBI_0100026", "http://purl.obolibrary.org/obo/OBI_0000257"])
        
        with patch('science_data_kit.web.routes.IsaBrowserPage', return_value=mock_page):
            response = self.client.get('/api/isa/terms')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data['terms']), 2)
            self.assertEqual(len(data['existing_term_accessions']), 2)

    def test_process_isa_file_endpoint(self):
        """Test the process ISA file API endpoint."""
        mock_result = {
            "success": True,
            "message": "ISA file processed successfully.",
            "node_classes": ["Investigation", "Study", "Assay"],
            "relationships": [{"source": "Investigation", "target": "Study", "type": "HAS_STUDY"}]
        }
        
        with patch.object(IsaBrowserPage, 'process_isa_file', return_value=mock_result):
            # Create a mock file
            mock_file = MagicMock()
            mock_file.filename = 'test.json'
            
            # Mock the request.files dictionary
            with patch('flask.request.files', {'file': mock_file}):
                response = self.client.post('/api/isa/process-file')
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data, mock_result)

    def test_load_terms_to_neo4j_endpoint(self):
        """Test the load terms to Neo4j API endpoint."""
        mock_result = {
            "success": True,
            "message": "Successfully loaded ontology terms into Neo4j. Created 5 relationships.",
            "relationships_created": 5
        }
        
        with patch.object(IsaBrowserPage, 'load_ontology_terms_to_neo4j', return_value=mock_result):
            response = self.client.post('/api/isa/load-to-neo4j', data={
                'create_source_nodes': 'true',
                'relationship_type': 'HAS_TERM'
            })
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data, mock_result)

if __name__ == '__main__':
    unittest.main()