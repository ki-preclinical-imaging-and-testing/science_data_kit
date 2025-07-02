import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology.queries import (
    get_ontology_terms, get_ontology_sources, get_ontology_relationships,
    get_ontology_hierarchy, search_ontology_terms, get_ontology_statistics,
    ontology_terms_to_dataframe, ontology_sources_to_dataframe, ontology_relationships_to_dataframe
)


class TestOntologyQueries(unittest.TestCase):
    """Test cases for the ontology queries module."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = MagicMock(spec=Neo4jManager)

    def test_get_ontology_terms_no_label(self):
        """Test getting all ontology terms without a label filter."""
        # Mock the execute_query method
        mock_results = [
            {"term": "Metabolomics", "term_accession": "http://example.org/term1"},
            {"term": "Proteomics", "term_accession": "http://example.org/term2"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_terms(self.db_manager)
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query doesn't include a label parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {})

    def test_get_ontology_terms_with_label(self):
        """Test getting ontology terms with a label filter."""
        # Mock the execute_query method
        mock_results = [
            {"term": "Metabolomics", "term_accession": "http://example.org/term1"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_terms(self.db_manager, "meta")
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query includes the label parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {"label": "meta"})

    def test_get_ontology_sources(self):
        """Test getting all ontology sources."""
        # Mock the execute_query method
        mock_results = [
            {"name": "GO", "file": "http://example.org/go.owl", "version": "1.0", "description": "Gene Ontology"},
            {"name": "CHEBI", "file": "http://example.org/chebi.owl", "version": "2.0", "description": "Chemical Entities of Biological Interest"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_sources(self.db_manager)
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()

    def test_get_ontology_relationships_no_source(self):
        """Test getting all ontology relationships without a source filter."""
        # Mock the execute_query method
        mock_results = [
            {"source_name": "GO", "term": "Metabolism", "term_accession": "GO:0008152", "relationship_type": "HAS_TERM"},
            {"source_name": "CHEBI", "term": "Water", "term_accession": "CHEBI:15377", "relationship_type": "HAS_TERM"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_relationships(self.db_manager)
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query doesn't include a source_name parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {})

    def test_get_ontology_relationships_with_source(self):
        """Test getting ontology relationships with a source filter."""
        # Mock the execute_query method
        mock_results = [
            {"source_name": "GO", "term": "Metabolism", "term_accession": "GO:0008152", "relationship_type": "HAS_TERM"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_relationships(self.db_manager, "GO")
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query includes the source_name parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {"source_name": "GO"})

    def test_get_ontology_hierarchy(self):
        """Test getting the hierarchy for a specific term."""
        # Mock the execute_query method
        mock_results = [
            {
                "term": "Dog",
                "term_accession": "http://example.org/dog",
                "parent_terms": ["Mammal", "Animal"],
                "parent_accessions": ["http://example.org/mammal", "http://example.org/animal"],
                "distance": 2
            }
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_hierarchy(self.db_manager, "Dog")
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query includes the term parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {"term": "Dog"})

    def test_search_ontology_terms(self):
        """Test searching for ontology terms."""
        # Mock the execute_query method
        mock_results = [
            {"term": "Metabolomics", "term_accession": "http://example.org/term1"},
            {"term": "Metabolism", "term_accession": "http://example.org/term2"}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = search_ontology_terms(self.db_manager, "meta")
        
        # Check the result
        self.assertEqual(result, mock_results)
        self.db_manager.execute_query.assert_called_once()
        # Check that the query includes the search_term parameter
        self.assertEqual(self.db_manager.execute_query.call_args[0][1], {"search_term": "meta"})

    def test_get_ontology_statistics(self):
        """Test getting statistics about the ontologies in the database."""
        # Mock the execute_query method
        mock_results = [
            {"term_count": 100, "source_count": 5, "relationship_count": 200}
        ]
        self.db_manager.execute_query.return_value = mock_results
        
        # Call the function
        result = get_ontology_statistics(self.db_manager)
        
        # Check the result
        self.assertEqual(result, mock_results[0])
        self.db_manager.execute_query.assert_called_once()

    def test_get_ontology_statistics_empty(self):
        """Test getting statistics when the database is empty."""
        # Mock the execute_query method to return an empty list
        self.db_manager.execute_query.return_value = []
        
        # Call the function
        result = get_ontology_statistics(self.db_manager)
        
        # Check the result
        self.assertEqual(result, {"term_count": 0, "source_count": 0, "relationship_count": 0})
        self.db_manager.execute_query.assert_called_once()

    @patch('science_data_kit.core.ontology.queries.get_ontology_terms')
    def test_ontology_terms_to_dataframe(self, mock_get_terms):
        """Test converting ontology terms to a DataFrame."""
        # Mock the get_ontology_terms function
        mock_results = [
            {"term": "Metabolomics", "term_accession": "http://example.org/term1"},
            {"term": "Proteomics", "term_accession": "http://example.org/term2"}
        ]
        mock_get_terms.return_value = mock_results
        
        # Call the function
        result = ontology_terms_to_dataframe(self.db_manager)
        
        # Check the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_get_terms.assert_called_once_with(self.db_manager, None)

    @patch('science_data_kit.core.ontology.queries.get_ontology_sources')
    def test_ontology_sources_to_dataframe(self, mock_get_sources):
        """Test converting ontology sources to a DataFrame."""
        # Mock the get_ontology_sources function
        mock_results = [
            {"name": "GO", "file": "http://example.org/go.owl", "version": "1.0", "description": "Gene Ontology"},
            {"name": "CHEBI", "file": "http://example.org/chebi.owl", "version": "2.0", "description": "Chemical Entities of Biological Interest"}
        ]
        mock_get_sources.return_value = mock_results
        
        # Call the function
        result = ontology_sources_to_dataframe(self.db_manager)
        
        # Check the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_get_sources.assert_called_once_with(self.db_manager)

    @patch('science_data_kit.core.ontology.queries.get_ontology_relationships')
    def test_ontology_relationships_to_dataframe(self, mock_get_relationships):
        """Test converting ontology relationships to a DataFrame."""
        # Mock the get_ontology_relationships function
        mock_results = [
            {"source_name": "GO", "term": "Metabolism", "term_accession": "GO:0008152", "relationship_type": "HAS_TERM"},
            {"source_name": "CHEBI", "term": "Water", "term_accession": "CHEBI:15377", "relationship_type": "HAS_TERM"}
        ]
        mock_get_relationships.return_value = mock_results
        
        # Call the function
        result = ontology_relationships_to_dataframe(self.db_manager)
        
        # Check the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_get_relationships.assert_called_once_with(self.db_manager, None)


if __name__ == '__main__':
    unittest.main()