import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import networkx as nx

from science_data_kit.core.ontology.browser import OntologyBrowser
from science_data_kit.core.db.db_manager import Neo4jManager


class TestOntologyBrowser(unittest.TestCase):
    """Test cases for the OntologyBrowser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = MagicMock(spec=Neo4jManager)
        self.browser = OntologyBrowser(self.db_manager)

    def test_initialization(self):
        """Test that the OntologyBrowser initializes correctly."""
        self.assertEqual(self.browser.db_manager, self.db_manager)

    @patch('science_data_kit.core.ontology.browser.get_ontology_statistics')
    def test_get_statistics(self, mock_get_statistics):
        """Test getting ontology statistics."""
        # Mock the get_ontology_statistics function
        mock_stats = {"term_count": 100, "source_count": 5, "relationship_count": 200}
        mock_get_statistics.return_value = mock_stats
        
        # Call the method
        result = self.browser.get_statistics()
        
        # Check the result
        self.assertEqual(result, mock_stats)
        mock_get_statistics.assert_called_once_with(self.db_manager)

    @patch('science_data_kit.core.ontology.browser.search_ontology_terms')
    def test_search_terms(self, mock_search_terms):
        """Test searching for ontology terms."""
        # Mock the search_ontology_terms function
        mock_results = [
            {"term": "Metabolomics", "term_accession": "http://example.org/term1"},
            {"term": "Metabolism", "term_accession": "http://example.org/term2"}
        ]
        mock_search_terms.return_value = mock_results
        
        # Call the method
        result = self.browser.search_terms("meta")
        
        # Check the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_search_terms.assert_called_once_with(self.db_manager, "meta")

    @patch('science_data_kit.core.ontology.browser.get_ontology_hierarchy')
    def test_get_term_hierarchy(self, mock_get_hierarchy):
        """Test getting the hierarchy for a specific term."""
        # Mock the get_ontology_hierarchy function
        mock_results = [
            {
                "term": "Dog",
                "term_accession": "http://example.org/dog",
                "parent_terms": ["Mammal", "Animal"],
                "parent_accessions": ["http://example.org/mammal", "http://example.org/animal"],
                "distance": 2
            }
        ]
        mock_get_hierarchy.return_value = mock_results
        
        # Call the method
        result = self.browser.get_term_hierarchy("Dog")
        
        # Check the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        mock_get_hierarchy.assert_called_once_with(self.db_manager, "Dog")

    @patch('science_data_kit.core.ontology.browser.get_ontology_hierarchy')
    @patch('science_data_kit.core.ontology.browser.Network')
    def test_visualize_term_hierarchy(self, mock_network, mock_get_hierarchy):
        """Test visualizing the hierarchy for a specific term."""
        # Mock the get_ontology_hierarchy function
        mock_results = [
            {
                "term": "Dog",
                "term_accession": "http://example.org/dog",
                "parent_terms": ["Mammal", "Animal"],
                "parent_accessions": ["http://example.org/mammal", "http://example.org/animal"],
                "distance": 2
            }
        ]
        mock_get_hierarchy.return_value = mock_results
        
        # Mock the Network class
        mock_network_instance = MagicMock()
        mock_network.return_value = mock_network_instance
        
        # Call the method
        result = self.browser.visualize_term_hierarchy("Dog")
        
        # Check the result
        self.assertEqual(result, mock_network_instance)
        mock_get_hierarchy.assert_called_once_with(self.db_manager, "Dog")
        mock_network.assert_called_once()
        mock_network_instance.from_nx.assert_called_once()
        mock_network_instance.set_options.assert_called_once()

    @patch('science_data_kit.core.ontology.browser.get_ontology_sources')
    @patch('science_data_kit.core.ontology.browser.get_ontology_relationships')
    @patch('science_data_kit.core.ontology.browser.Network')
    def test_visualize_ontology_sources(self, mock_network, mock_get_relationships, mock_get_sources):
        """Test visualizing ontology sources and their relationships."""
        # Mock the get_ontology_sources function
        mock_sources = [
            {"name": "GO", "description": "Gene Ontology"},
            {"name": "CHEBI", "description": "Chemical Entities of Biological Interest"}
        ]
        mock_get_sources.return_value = mock_sources
        
        # Mock the get_ontology_relationships function
        mock_relationships = [
            {"source_name": "GO", "term": "Metabolism", "term_accession": "GO:0008152", "relationship_type": "HAS_TERM"},
            {"source_name": "CHEBI", "term": "Water", "term_accession": "CHEBI:15377", "relationship_type": "HAS_TERM"}
        ]
        mock_get_relationships.return_value = mock_relationships
        
        # Mock the Network class
        mock_network_instance = MagicMock()
        mock_network.return_value = mock_network_instance
        
        # Call the method
        result = self.browser.visualize_ontology_sources()
        
        # Check the result
        self.assertEqual(result, mock_network_instance)
        mock_get_sources.assert_called_once_with(self.db_manager)
        mock_get_relationships.assert_called_once_with(self.db_manager)
        mock_network.assert_called_once()
        mock_network_instance.from_nx.assert_called_once()
        mock_network_instance.set_options.assert_called_once()


if __name__ == '__main__':
    unittest.main()