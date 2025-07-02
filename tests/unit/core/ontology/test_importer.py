import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os

from science_data_kit.core.ontology.importer import OntologyImporter
from science_data_kit.core.db.db_manager import Neo4jManager


class TestOntologyImporter(unittest.TestCase):
    """Test cases for the OntologyImporter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = MagicMock(spec=Neo4jManager)
        self.importer = OntologyImporter(self.db_manager)

        # Mock the n10s availability check to return True
        self.importer._check_n10s_available = MagicMock(return_value=True)
        self.importer.n10s_available = True

        # Mock the _initialize_n10s method to return True
        self.importer._initialize_n10s = MagicMock(return_value=True)

    def test_initialization(self):
        """Test that the OntologyImporter initializes correctly."""
        self.assertEqual(self.importer.db_manager, self.db_manager)
        self.assertTrue(self.importer.n10s_available)

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_check_n10s_available_success(self, mock_logger):
        """Test that _check_n10s_available returns True when n10s is available."""
        # Restore the original method for this test
        self.importer._check_n10s_available = OntologyImporter._check_n10s_available.__get__(self.importer)

        # Mock the execute_query method to return a version
        self.db_manager.execute_query.return_value = [{"version": "1.0.0"}]

        # Call the method
        result = self.importer._check_n10s_available()

        # Check the result
        self.assertTrue(result)
        self.db_manager.execute_query.assert_called_once_with("CALL n10s.version()")
        mock_logger.info.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_check_n10s_available_failure(self, mock_logger):
        """Test that _check_n10s_available returns False when n10s is not available."""
        # Restore the original method for this test
        self.importer._check_n10s_available = OntologyImporter._check_n10s_available.__get__(self.importer)

        # Mock the execute_query method to return an empty list
        self.db_manager.execute_query.return_value = []

        # Call the method
        result = self.importer._check_n10s_available()

        # Check the result
        self.assertFalse(result)
        self.db_manager.execute_query.assert_called_once_with("CALL n10s.version()")
        mock_logger.warning.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_check_n10s_available_exception(self, mock_logger):
        """Test that _check_n10s_available returns False when an exception occurs."""
        # Restore the original method for this test
        self.importer._check_n10s_available = OntologyImporter._check_n10s_available.__get__(self.importer)

        # Mock the execute_query method to raise an exception
        self.db_manager.execute_query.side_effect = Exception("Test exception")

        # Call the method
        result = self.importer._check_n10s_available()

        # Check the result
        self.assertFalse(result)
        self.db_manager.execute_query.assert_called_once_with("CALL n10s.version()")
        mock_logger.warning.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_initialize_n10s_success(self, mock_logger):
        """Test that _initialize_n10s returns True when initialization succeeds."""
        # Restore the original method for this test
        self.importer._initialize_n10s = OntologyImporter._initialize_n10s.__get__(self.importer)

        # Mock the execute_query method to return successfully
        self.db_manager.execute_query.return_value = []

        # Call the method
        result = self.importer._initialize_n10s()

        # Check the result
        self.assertTrue(result)
        self.assertEqual(self.db_manager.execute_query.call_count, 2)
        mock_logger.info.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_initialize_n10s_failure(self, mock_logger):
        """Test that _initialize_n10s returns False when n10s is not available."""
        # Restore the original method for this test
        self.importer._initialize_n10s = OntologyImporter._initialize_n10s.__get__(self.importer)

        # Set n10s_available to False
        self.importer.n10s_available = False

        # Call the method
        result = self.importer._initialize_n10s()

        # Check the result
        self.assertFalse(result)
        self.db_manager.execute_query.assert_not_called()
        mock_logger.warning.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_initialize_n10s_exception(self, mock_logger):
        """Test that _initialize_n10s returns False when an exception occurs."""
        # Restore the original method for this test
        self.importer._initialize_n10s = OntologyImporter._initialize_n10s.__get__(self.importer)

        # Mock the execute_query method to raise an exception
        self.db_manager.execute_query.side_effect = Exception("Test exception")

        # Call the method
        result = self.importer._initialize_n10s()

        # Check the result
        self.assertFalse(result)
        self.db_manager.execute_query.assert_called_once()
        mock_logger.error.assert_called_once()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_ontology_from_file(self, mock_logger):
        """Test loading an ontology from a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as temp_file:
            temp_file.write(b"<rdf:RDF></rdf:RDF>")
            file_path = temp_file.name

        # Mock the _load_from_file method
        self.importer._load_from_file = MagicMock(return_value=True)

        try:
            # Call the method
            result = self.importer.load_ontology(file_path)

            # Check the result
            self.assertTrue(result)
            self.importer._load_from_file.assert_called_once_with(file_path)
        finally:
            # Clean up the temporary file
            os.unlink(file_path)

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_ontology_from_url(self, mock_logger):
        """Test loading an ontology from a URL."""
        # Mock the _load_from_url method
        self.importer._load_from_url = MagicMock(return_value=True)

        # Call the method
        result = self.importer.load_ontology("http://example.org/ontology.owl")

        # Check the result
        self.assertTrue(result)
        self.importer._load_from_url.assert_called_once_with("http://example.org/ontology.owl")

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_from_file_success(self, mock_logger):
        """Test that _load_from_file returns True when loading succeeds."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as temp_file:
            temp_file.write(b"<rdf:RDF></rdf:RDF>")
            file_path = temp_file.name

        # Mock the execute_query method to return success
        self.db_manager.execute_query.return_value = [{"terminationStatus": "OK", "triplesLoaded": 10, "triplesParsed": 10}]

        # Mock the _create_ontology_source method
        self.importer._create_ontology_source = MagicMock()

        try:
            # Restore the original method for this test
            self.importer._load_from_file = OntologyImporter._load_from_file.__get__(self.importer)

            # Call the method
            result = self.importer._load_from_file(file_path)

            # Check the result
            self.assertTrue(result)
            self.db_manager.execute_query.assert_called_once()
            self.importer._create_ontology_source.assert_called_once()
            mock_logger.info.assert_called()
        finally:
            # Clean up the temporary file
            os.unlink(file_path)

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_from_file_fallback(self, mock_logger):
        """Test that _load_from_file_fallback is called when n10s is not available."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as temp_file:
            temp_file.write(b"<rdf:RDF></rdf:RDF>")
            file_path = temp_file.name

        # Set n10s_available to False
        self.importer.n10s_available = False

        # Mock the _load_from_file_fallback method
        self.importer._load_from_file_fallback = MagicMock(return_value=True)

        try:
            # Restore the original method for this test
            self.importer._load_from_file = OntologyImporter._load_from_file.__get__(self.importer)

            # Call the method
            result = self.importer._load_from_file(file_path)

            # Check the result
            self.assertTrue(result)
            self.importer._load_from_file_fallback.assert_called_once_with(file_path, ".owl")
            mock_logger.warning.assert_called_once()
        finally:
            # Clean up the temporary file
            os.unlink(file_path)


    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_from_url_success(self, mock_logger):
        """Test that _load_from_url returns True when loading succeeds."""
        # Mock the execute_query method to return success
        self.db_manager.execute_query.return_value = [{"terminationStatus": "OK", "triplesLoaded": 10, "triplesParsed": 10}]

        # Mock the _create_ontology_source method
        self.importer._create_ontology_source = MagicMock()

        # Restore the original method for this test
        self.importer._load_from_url = OntologyImporter._load_from_url.__get__(self.importer)

        # Call the method
        result = self.importer._load_from_url("http://example.org/ontology.owl")

        # Check the result
        self.assertTrue(result)
        self.db_manager.execute_query.assert_called_once()
        self.importer._create_ontology_source.assert_called_once()
        mock_logger.info.assert_called()

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_load_from_url_fallback(self, mock_logger):
        """Test that _load_from_url_fallback is called when n10s is not available."""
        # Set n10s_available to False
        self.importer.n10s_available = False

        # Mock the _load_from_url_fallback method
        self.importer._load_from_url_fallback = MagicMock(return_value=True)

        # Restore the original method for this test
        self.importer._load_from_url = OntologyImporter._load_from_url.__get__(self.importer)

        # Call the method
        result = self.importer._load_from_url("http://example.org/ontology.owl")

        # Check the result
        self.assertTrue(result)
        self.importer._load_from_url_fallback.assert_called_once_with("http://example.org/ontology.owl")
        mock_logger.warning.assert_called_once()

    def test_get_rdf_format(self):
        """Test that _get_rdf_format returns the correct format for different file extensions."""
        # Test various file extensions
        self.assertEqual(self.importer._get_rdf_format(".owl"), "RDF/XML")
        self.assertEqual(self.importer._get_rdf_format(".rdf"), "RDF/XML")
        self.assertEqual(self.importer._get_rdf_format(".ttl"), "Turtle")
        self.assertEqual(self.importer._get_rdf_format(".nt"), "N-Triples")
        self.assertEqual(self.importer._get_rdf_format(".n3"), "N3")
        self.assertEqual(self.importer._get_rdf_format(".jsonld"), "JSON-LD")

        # Test unknown extension (should default to RDF/XML)
        self.assertEqual(self.importer._get_rdf_format(".unknown"), "RDF/XML")

    def test_get_rdflib_format(self):
        """Test that _get_rdflib_format returns the correct format for different file extensions."""
        # Test various file extensions
        self.assertEqual(self.importer._get_rdflib_format(".owl"), "xml")
        self.assertEqual(self.importer._get_rdflib_format(".rdf"), "xml")
        self.assertEqual(self.importer._get_rdflib_format(".ttl"), "turtle")
        self.assertEqual(self.importer._get_rdflib_format(".nt"), "nt")
        self.assertEqual(self.importer._get_rdflib_format(".n3"), "n3")
        self.assertEqual(self.importer._get_rdflib_format(".jsonld"), "json-ld")

        # Test unknown extension (should default to xml)
        self.assertEqual(self.importer._get_rdflib_format(".unknown"), "xml")

    @patch('science_data_kit.core.ontology.importer.Graph')
    def test_extract_ontology_classes(self, mock_graph):
        """Test that _extract_ontology_classes extracts classes correctly."""
        # Create a mock graph
        mock_g = MagicMock()

        # Mock the subjects method to return a list of subjects
        mock_s1 = MagicMock()
        mock_s2 = MagicMock()
        mock_g.subjects.side_effect = [[mock_s1], [mock_s2]]

        # Mock the _get_label and _get_comment methods
        self.importer._get_label = MagicMock(side_effect=["Class1", "Class2"])
        self.importer._get_comment = MagicMock(side_effect=["Comment1", "Comment2"])

        # Mock the objects method to return a list of objects
        mock_g.objects.side_effect = [["Superclass1"], ["Superclass2"]]

        # Call the method
        result = self.importer._extract_ontology_classes(mock_g)

        # Check the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["label"], "Class1")
        self.assertEqual(result[0]["comment"], "Comment1")
        self.assertEqual(result[1]["label"], "Class2")
        self.assertEqual(result[1]["comment"], "Comment2")

    @patch('science_data_kit.core.ontology.importer.Graph')
    def test_extract_ontology_properties(self, mock_graph):
        """Test that _extract_ontology_properties extracts properties correctly."""
        # Create a mock graph
        mock_g = MagicMock()

        # Mock the subjects method to return a list of subjects
        mock_s1 = MagicMock()
        mock_g.subjects.side_effect = [[mock_s1]]

        # Mock the _get_label and _get_comment methods
        self.importer._get_label = MagicMock(return_value="Property1")
        self.importer._get_comment = MagicMock(return_value="Comment1")

        # Mock the objects method to return a list of objects
        mock_g.objects.side_effect = [["Domain1"], ["Range1"]]

        # Call the method
        result = self.importer._extract_ontology_properties(mock_g)

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "Property1")
        self.assertEqual(result[0]["comment"], "Comment1")
        self.assertEqual(result[0]["domain"], ["Domain1"])
        self.assertEqual(result[0]["range"], ["Range1"])

    @patch('science_data_kit.core.ontology.importer.Graph')
    def test_get_label(self, mock_graph):
        """Test that _get_label returns the correct label."""
        # Create a mock graph
        mock_g = MagicMock()

        # Mock the objects method to return a list of labels
        mock_g.objects.return_value = ["Label1"]

        # Call the method
        result = self.importer._get_label(mock_g, "http://example.org/resource")

        # Check the result
        self.assertEqual(result, "Label1")

        # Test when no label is found (should return local name from URI)
        mock_g.objects.return_value = []

        # Test with # in URI
        result = self.importer._get_label(mock_g, "http://example.org/ontology#Resource")
        self.assertEqual(result, "Resource")

        # Test with / in URI
        result = self.importer._get_label(mock_g, "http://example.org/ontology/Resource")
        self.assertEqual(result, "Resource")

    @patch('science_data_kit.core.ontology.importer.Graph')
    def test_get_comment(self, mock_graph):
        """Test that _get_comment returns the correct comment."""
        # Create a mock graph
        mock_g = MagicMock()

        # Mock the objects method to return a list of comments
        mock_g.objects.return_value = ["Comment1"]

        # Call the method
        result = self.importer._get_comment(mock_g, "http://example.org/resource")

        # Check the result
        self.assertEqual(result, "Comment1")

        # Test when no comment is found (should return empty string)
        mock_g.objects.return_value = []
        result = self.importer._get_comment(mock_g, "http://example.org/resource")
        self.assertEqual(result, "")

    @patch('science_data_kit.core.ontology.importer.logger')
    def test_create_ontology_nodes(self, mock_logger):
        """Test that _create_ontology_nodes creates nodes and relationships correctly."""
        # Create mock data
        mock_g = MagicMock()
        mock_classes = [
            {
                "uri": "http://example.org/class1",
                "label": "Class1",
                "comment": "Comment1",
                "subClassOf": ["http://example.org/superclass1"]
            }
        ]
        mock_properties = [
            {
                "uri": "http://example.org/property1",
                "label": "Property1",
                "comment": "Comment1",
                "domain": ["http://example.org/domain1"],
                "range": ["http://example.org/range1"],
                "type": "http://www.w3.org/2002/07/owl#ObjectProperty"
            }
        ]

        # Call the method
        self.importer._create_ontology_nodes(mock_g, mock_classes, mock_properties)

        # Check that execute_query was called the correct number of times
        # 1 for class node, 1 for subclass relationship, 1 for property node,
        # 1 for domain relationship, 1 for range relationship
        self.assertEqual(self.db_manager.execute_query.call_count, 5)


if __name__ == '__main__':
    unittest.main()
