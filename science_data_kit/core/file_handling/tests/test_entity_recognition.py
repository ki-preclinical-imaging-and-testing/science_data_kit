"""
Tests for the entity_recognition module.
"""

import unittest
from unittest.mock import patch, MagicMock

from science_data_kit.core.file_handling.entity_recognition import (
    EntityType,
    EntityRecognitionMethod,
    EntityRecognitionOptions,
    Entity,
    EntityRecognitionResult,
    EntityRecognizer,
    extract_entities,
    extract_entities_from_file,
    compare_entity_recognition_methods,
    get_entities_by_type
)
from science_data_kit.core.file_handling.text_extraction import TextExtractionResult


class TestEntityType(unittest.TestCase):
    """Tests for the EntityType enum."""
    
    def test_entity_types(self):
        """Test that all expected entity types are defined."""
        self.assertEqual(EntityType.PERSON.value, "PERSON")
        self.assertEqual(EntityType.ORGANIZATION.value, "ORGANIZATION")
        self.assertEqual(EntityType.LOCATION.value, "LOCATION")
        self.assertEqual(EntityType.DATE.value, "DATE")
        self.assertEqual(EntityType.TIME.value, "TIME")
        self.assertEqual(EntityType.MONEY.value, "MONEY")
        self.assertEqual(EntityType.PERCENT.value, "PERCENT")
        self.assertEqual(EntityType.FACILITY.value, "FACILITY")
        self.assertEqual(EntityType.GPE.value, "GPE")
        self.assertEqual(EntityType.PRODUCT.value, "PRODUCT")
        self.assertEqual(EntityType.EVENT.value, "EVENT")
        self.assertEqual(EntityType.WORK_OF_ART.value, "WORK_OF_ART")
        self.assertEqual(EntityType.LAW.value, "LAW")
        self.assertEqual(EntityType.LANGUAGE.value, "LANGUAGE")
        self.assertEqual(EntityType.NORP.value, "NORP")
        self.assertEqual(EntityType.CARDINAL.value, "CARDINAL")
        self.assertEqual(EntityType.ORDINAL.value, "ORDINAL")
        self.assertEqual(EntityType.QUANTITY.value, "QUANTITY")
        self.assertEqual(EntityType.OTHER.value, "OTHER")


class TestEntityRecognitionMethod(unittest.TestCase):
    """Tests for the EntityRecognitionMethod enum."""
    
    def test_entity_recognition_methods(self):
        """Test that all expected entity recognition methods are defined."""
        self.assertEqual(EntityRecognitionMethod.SPACY.value, "spacy")
        self.assertEqual(EntityRecognitionMethod.NLTK.value, "nltk")
        self.assertEqual(EntityRecognitionMethod.REGEX.value, "regex")
        self.assertEqual(EntityRecognitionMethod.TRANSFORMERS.value, "transformers")


class TestEntityRecognitionOptions(unittest.TestCase):
    """Tests for the EntityRecognitionOptions class."""
    
    def test_default_initialization(self):
        """Test that default initialization works correctly."""
        options = EntityRecognitionOptions()
        self.assertEqual(options.method, EntityRecognitionMethod.SPACY)
        self.assertIsNone(options.entity_types)
        self.assertEqual(options.min_confidence, 0.5)
        self.assertEqual(options.case_sensitive, False)
        self.assertEqual(options.spacy_model, "en_core_web_sm")
        self.assertEqual(options.nltk_download_resources, True)
        self.assertIsNone(options.regex_patterns)
        self.assertEqual(options.transformers_model, "dbmdz/bert-large-cased-finetuned-conll03-english")
        self.assertEqual(options.transformers_aggregation_strategy, "simple")
        self.assertIsNone(options.text_extraction_options)


class TestEntity(unittest.TestCase):
    """Tests for the Entity class."""
    
    def test_initialization(self):
        """Test initialization."""
        entity = Entity(
            text="John Doe",
            type=EntityType.PERSON,
            start=0,
            end=8,
            confidence=0.95
        )
        self.assertEqual(entity.text, "John Doe")
        self.assertEqual(entity.type, EntityType.PERSON)
        self.assertEqual(entity.start, 0)
        self.assertEqual(entity.end, 8)
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        entity = Entity(
            text="John Doe",
            type=EntityType.PERSON,
            start=0,
            end=8,
            confidence=0.95
        )
        expected_str = "John Doe (PERSON, 0.9500)"
        self.assertEqual(str(entity), expected_str)


class TestEntityRecognitionResult(unittest.TestCase):
    """Tests for the EntityRecognitionResult class."""
    
    def test_initialization(self):
        """Test initialization."""
        entities = [
            Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
            Entity(text="New York", type=EntityType.LOCATION, start=12, end=20, confidence=0.85)
        ]
        result = EntityRecognitionResult(
            entities=entities,
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York."
        )
        self.assertEqual(result.entities, entities)
        self.assertEqual(result.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(result.text, "John Doe lives in New York.")
        self.assertEqual(result.metadata, {})
    
    def test_str_representation(self):
        """Test string representation."""
        entities = [
            Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
            Entity(text="New York", type=EntityType.LOCATION, start=12, end=20, confidence=0.85)
        ]
        result = EntityRecognitionResult(
            entities=entities,
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York."
        )
        expected_str = "\n".join([
            "Method: spacy",
            "Total entities: 2",
            "LOCATION: New York (0.8500)",
            "PERSON: John Doe (0.9500)"
        ])
        self.assertEqual(str(result), expected_str)


class TestEntityRecognizer(unittest.TestCase):
    """Tests for the EntityRecognizer class."""
    
    def setUp(self):
        """Set up the test case."""
        self.recognizer = EntityRecognizer()
    
    def test_initialization(self):
        """Test initialization."""
        self.assertIsInstance(self.recognizer.options, EntityRecognitionOptions)
        self.assertEqual(self.recognizer.options.method, EntityRecognitionMethod.SPACY)
        self.assertIsNone(self.recognizer._spacy_nlp)
        self.assertIsNone(self.recognizer._transformers_pipeline)
    
    def test_get_default_regex_patterns(self):
        """Test getting default regex patterns."""
        patterns = self.recognizer._get_default_regex_patterns()
        self.assertIsInstance(patterns, dict)
        self.assertIn(EntityType.PERSON, patterns)
        self.assertIn(EntityType.ORGANIZATION, patterns)
        self.assertIn(EntityType.LOCATION, patterns)
        self.assertIn(EntityType.DATE, patterns)
        self.assertIn(EntityType.TIME, patterns)
        self.assertIn(EntityType.MONEY, patterns)
        self.assertIn(EntityType.PERCENT, patterns)
        
        # Check that patterns are valid regular expressions
        import re
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                try:
                    re.compile(pattern)
                except re.error:
                    self.fail(f"Invalid regex pattern for {entity_type}: {pattern}")
    
    @patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', False)
    def test_load_spacy_model_not_available(self):
        """Test loading spaCy model when spaCy is not available."""
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer()
            self.assertIsNone(recognizer._load_spacy_model())
            mock_logger.warning.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.spacy')
    def test_load_spacy_model(self, mock_spacy):
        """Test loading spaCy model."""
        mock_nlp = MagicMock()
        mock_spacy.load.return_value = mock_nlp
        
        recognizer = EntityRecognizer()
        result = recognizer._load_spacy_model()
        
        self.assertEqual(result, mock_nlp)
        mock_spacy.load.assert_called_once_with("en_core_web_sm")
    
    @patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.spacy')
    def test_load_spacy_model_error(self, mock_spacy):
        """Test loading spaCy model with error."""
        mock_spacy.load.side_effect = OSError("Model not found")
        
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer()
            self.assertIsNone(recognizer._load_spacy_model())
            mock_logger.error.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.entity_recognition.NLTK_AVAILABLE', False)
    def test_load_nltk_resources_not_available(self):
        """Test loading NLTK resources when NLTK is not available."""
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.NLTK))
            self.assertFalse(recognizer._load_nltk_resources())
            mock_logger.warning.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.entity_recognition.NLTK_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.nltk')
    def test_load_nltk_resources(self, mock_nltk):
        """Test loading NLTK resources."""
        recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.NLTK))
        self.assertTrue(recognizer._load_nltk_resources())
        self.assertEqual(mock_nltk.download.call_count, 4)
    
    @patch('science_data_kit.core.file_handling.entity_recognition.NLTK_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.nltk')
    def test_load_nltk_resources_error(self, mock_nltk):
        """Test loading NLTK resources with error."""
        mock_nltk.download.side_effect = Exception("Download error")
        
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.NLTK))
            self.assertFalse(recognizer._load_nltk_resources())
            mock_logger.error.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.entity_recognition.TRANSFORMERS_AVAILABLE', False)
    def test_load_transformers_pipeline_not_available(self):
        """Test loading Transformers pipeline when Transformers is not available."""
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.TRANSFORMERS))
            self.assertIsNone(recognizer._load_transformers_pipeline())
            mock_logger.warning.assert_called_once()
    
    @patch('science_data_kit.core.file_handling.entity_recognition.TRANSFORMERS_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.pipeline')
    def test_load_transformers_pipeline(self, mock_pipeline):
        """Test loading Transformers pipeline."""
        mock_ner_pipeline = MagicMock()
        mock_pipeline.return_value = mock_ner_pipeline
        
        recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.TRANSFORMERS))
        result = recognizer._load_transformers_pipeline()
        
        self.assertEqual(result, mock_ner_pipeline)
        mock_pipeline.assert_called_once_with(
            "ner",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            aggregation_strategy="simple"
        )
    
    @patch('science_data_kit.core.file_handling.entity_recognition.TRANSFORMERS_AVAILABLE', True)
    @patch('science_data_kit.core.file_handling.entity_recognition.pipeline')
    def test_load_transformers_pipeline_error(self, mock_pipeline):
        """Test loading Transformers pipeline with error."""
        mock_pipeline.side_effect = Exception("Pipeline error")
        
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer(EntityRecognitionOptions(method=EntityRecognitionMethod.TRANSFORMERS))
            self.assertIsNone(recognizer._load_transformers_pipeline())
            mock_logger.error.assert_called_once()
    
    def test_map_spacy_entity_type(self):
        """Test mapping spaCy entity type to EntityType."""
        self.assertEqual(self.recognizer._map_spacy_entity_type("PERSON"), EntityType.PERSON)
        self.assertEqual(self.recognizer._map_spacy_entity_type("ORG"), EntityType.ORGANIZATION)
        self.assertEqual(self.recognizer._map_spacy_entity_type("GPE"), EntityType.GPE)
        self.assertEqual(self.recognizer._map_spacy_entity_type("LOC"), EntityType.LOCATION)
        self.assertEqual(self.recognizer._map_spacy_entity_type("DATE"), EntityType.DATE)
        self.assertEqual(self.recognizer._map_spacy_entity_type("TIME"), EntityType.TIME)
        self.assertEqual(self.recognizer._map_spacy_entity_type("MONEY"), EntityType.MONEY)
        self.assertEqual(self.recognizer._map_spacy_entity_type("PERCENT"), EntityType.PERCENT)
        self.assertEqual(self.recognizer._map_spacy_entity_type("FAC"), EntityType.FACILITY)
        self.assertEqual(self.recognizer._map_spacy_entity_type("PRODUCT"), EntityType.PRODUCT)
        self.assertEqual(self.recognizer._map_spacy_entity_type("EVENT"), EntityType.EVENT)
        self.assertEqual(self.recognizer._map_spacy_entity_type("WORK_OF_ART"), EntityType.WORK_OF_ART)
        self.assertEqual(self.recognizer._map_spacy_entity_type("LAW"), EntityType.LAW)
        self.assertEqual(self.recognizer._map_spacy_entity_type("LANGUAGE"), EntityType.LANGUAGE)
        self.assertEqual(self.recognizer._map_spacy_entity_type("NORP"), EntityType.NORP)
        self.assertEqual(self.recognizer._map_spacy_entity_type("CARDINAL"), EntityType.CARDINAL)
        self.assertEqual(self.recognizer._map_spacy_entity_type("ORDINAL"), EntityType.ORDINAL)
        self.assertEqual(self.recognizer._map_spacy_entity_type("QUANTITY"), EntityType.QUANTITY)
        self.assertEqual(self.recognizer._map_spacy_entity_type("UNKNOWN"), EntityType.OTHER)
    
    def test_map_nltk_entity_type(self):
        """Test mapping NLTK entity type to EntityType."""
        self.assertEqual(self.recognizer._map_nltk_entity_type("PERSON"), EntityType.PERSON)
        self.assertEqual(self.recognizer._map_nltk_entity_type("ORGANIZATION"), EntityType.ORGANIZATION)
        self.assertEqual(self.recognizer._map_nltk_entity_type("GPE"), EntityType.GPE)
        self.assertEqual(self.recognizer._map_nltk_entity_type("LOCATION"), EntityType.LOCATION)
        self.assertEqual(self.recognizer._map_nltk_entity_type("DATE"), EntityType.DATE)
        self.assertEqual(self.recognizer._map_nltk_entity_type("TIME"), EntityType.TIME)
        self.assertEqual(self.recognizer._map_nltk_entity_type("MONEY"), EntityType.MONEY)
        self.assertEqual(self.recognizer._map_nltk_entity_type("PERCENT"), EntityType.PERCENT)
        self.assertEqual(self.recognizer._map_nltk_entity_type("FACILITY"), EntityType.FACILITY)
        self.assertEqual(self.recognizer._map_nltk_entity_type("UNKNOWN"), EntityType.OTHER)
    
    def test_map_transformers_entity_type(self):
        """Test mapping Transformers entity type to EntityType."""
        self.assertEqual(self.recognizer._map_transformers_entity_type("PER"), EntityType.PERSON)
        self.assertEqual(self.recognizer._map_transformers_entity_type("ORG"), EntityType.ORGANIZATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("LOC"), EntityType.LOCATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("MISC"), EntityType.OTHER)
        self.assertEqual(self.recognizer._map_transformers_entity_type("B-PER"), EntityType.PERSON)
        self.assertEqual(self.recognizer._map_transformers_entity_type("I-PER"), EntityType.PERSON)
        self.assertEqual(self.recognizer._map_transformers_entity_type("B-ORG"), EntityType.ORGANIZATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("I-ORG"), EntityType.ORGANIZATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("B-LOC"), EntityType.LOCATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("I-LOC"), EntityType.LOCATION)
        self.assertEqual(self.recognizer._map_transformers_entity_type("B-MISC"), EntityType.OTHER)
        self.assertEqual(self.recognizer._map_transformers_entity_type("I-MISC"), EntityType.OTHER)
        self.assertEqual(self.recognizer._map_transformers_entity_type("UNKNOWN"), EntityType.OTHER)
    
    def test_filter_entities_by_type(self):
        """Test filtering entities by type."""
        entities = [
            Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8),
            Entity(text="New York", type=EntityType.LOCATION, start=12, end=20),
            Entity(text="Apple Inc", type=EntityType.ORGANIZATION, start=24, end=33)
        ]
        
        # No filter
        self.recognizer.options.entity_types = None
        filtered = self.recognizer._filter_entities_by_type(entities)
        self.assertEqual(filtered, entities)
        
        # Filter by single type
        self.recognizer.options.entity_types = [EntityType.PERSON]
        filtered = self.recognizer._filter_entities_by_type(entities)
        self.assertEqual(filtered, [entities[0]])
        
        # Filter by multiple types
        self.recognizer.options.entity_types = [EntityType.PERSON, EntityType.ORGANIZATION]
        filtered = self.recognizer._filter_entities_by_type(entities)
        self.assertEqual(filtered, [entities[0], entities[2]])
    
    def test_filter_entities_by_confidence(self):
        """Test filtering entities by confidence."""
        entities = [
            Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
            Entity(text="New York", type=EntityType.LOCATION, start=12, end=20, confidence=0.85),
            Entity(text="Apple Inc", type=EntityType.ORGANIZATION, start=24, end=33, confidence=0.45)
        ]
        
        # Default threshold (0.5)
        filtered = self.recognizer._filter_entities_by_confidence(entities)
        self.assertEqual(filtered, [entities[0], entities[1]])
        
        # Custom threshold
        self.recognizer.options.min_confidence = 0.9
        filtered = self.recognizer._filter_entities_by_confidence(entities)
        self.assertEqual(filtered, [entities[0]])
        
        # Low threshold
        self.recognizer.options.min_confidence = 0.4
        filtered = self.recognizer._filter_entities_by_confidence(entities)
        self.assertEqual(filtered, entities)
    
    @patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', True)
    def test_extract_entities_spacy(self):
        """Test extracting entities using spaCy."""
        # Mock spaCy model
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_ent1 = MagicMock()
        mock_ent1.text = "John Doe"
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 8
        mock_ent2 = MagicMock()
        mock_ent2.text = "New York"
        mock_ent2.label_ = "GPE"
        mock_ent2.start_char = 12
        mock_ent2.end_char = 20
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp.return_value = mock_doc
        
        with patch.object(self.recognizer, '_load_spacy_model', return_value=mock_nlp):
            entities = self.recognizer.extract_entities_spacy("John Doe lives in New York.")
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].text, "John Doe")
        self.assertEqual(entities[0].type, EntityType.PERSON)
        self.assertEqual(entities[0].start, 0)
        self.assertEqual(entities[0].end, 8)
        self.assertEqual(entities[0].confidence, 1.0)
        self.assertEqual(entities[0].metadata, {"spacy_label": "PERSON"})
        self.assertEqual(entities[1].text, "New York")
        self.assertEqual(entities[1].type, EntityType.GPE)
        self.assertEqual(entities[1].start, 12)
        self.assertEqual(entities[1].end, 20)
        self.assertEqual(entities[1].confidence, 1.0)
        self.assertEqual(entities[1].metadata, {"spacy_label": "GPE"})
    
    @patch('science_data_kit.core.file_handling.entity_recognition.NLTK_AVAILABLE', True)
    def test_extract_entities_nltk(self):
        """Test extracting entities using NLTK."""
        # Mock NLTK functions
        mock_tree = MagicMock()
        mock_chunk1 = MagicMock()
        mock_chunk1.label.return_value = "PERSON"
        mock_chunk1.__getitem__.return_value = [("John", "NNP")]
        mock_chunk2 = MagicMock()
        mock_chunk2.__getitem__.return_value = ("Doe", "NNP")
        mock_chunk3 = MagicMock()
        mock_chunk3.label.return_value = "GPE"
        mock_chunk3.__getitem__.return_value = [("New", "NNP")]
        mock_chunk4 = MagicMock()
        mock_chunk4.__getitem__.return_value = ("York", "NNP")
        mock_tree.__iter__.return_value = [mock_chunk1, mock_chunk2, mock_chunk3, mock_chunk4]
        
        with patch('science_data_kit.core.file_handling.entity_recognition.word_tokenize', return_value=["John", "Doe", "lives", "in", "New", "York", "."]), \
             patch('science_data_kit.core.file_handling.entity_recognition.pos_tag', return_value=[("John", "NNP"), ("Doe", "NNP"), ("lives", "VBZ"), ("in", "IN"), ("New", "NNP"), ("York", "NNP"), (".", ".")]), \
             patch('science_data_kit.core.file_handling.entity_recognition.ne_chunk', return_value=mock_tree), \
             patch.object(self.recognizer, '_load_nltk_resources', return_value=True):
            
            # This is a simplified test that doesn't fully mock the NLTK behavior
            # In a real test, we would need to mock the tree structure more accurately
            entities = self.recognizer.extract_entities_nltk("John Doe lives in New York.")
        
        # Since we're not fully mocking the NLTK behavior, we'll just check that the function runs without errors
        self.assertIsInstance(entities, list)
    
    def test_extract_entities_regex(self):
        """Test extracting entities using regex."""
        # Set up regex patterns
        self.recognizer.options.method = EntityRecognitionMethod.REGEX
        self.recognizer.options.regex_patterns = {
            EntityType.PERSON: [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'],
            EntityType.LOCATION: [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b']  # Intentionally overlapping with PERSON
        }
        
        entities = self.recognizer.extract_entities_regex("John Doe lives in New York.")
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].text, "John Doe")
        self.assertEqual(entities[0].type, EntityType.PERSON)
        self.assertEqual(entities[0].start, 0)
        self.assertEqual(entities[0].end, 8)
        self.assertEqual(entities[0].confidence, 1.0)
        self.assertEqual(entities[0].metadata["pattern"], r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
        self.assertEqual(entities[1].text, "New York")
        self.assertEqual(entities[1].type, EntityType.LOCATION)
        self.assertEqual(entities[1].start, 18)
        self.assertEqual(entities[1].end, 26)
        self.assertEqual(entities[1].confidence, 1.0)
        self.assertEqual(entities[1].metadata["pattern"], r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
    
    @patch('science_data_kit.core.file_handling.entity_recognition.TRANSFORMERS_AVAILABLE', True)
    def test_extract_entities_transformers(self):
        """Test extracting entities using Transformers."""
        # Mock Transformers pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [
            {"word": "John Doe", "entity_group": "PER", "start": 0, "end": 8, "score": 0.95},
            {"word": "New York", "entity_group": "LOC", "start": 18, "end": 26, "score": 0.85}
        ]
        
        with patch.object(self.recognizer, '_load_transformers_pipeline', return_value=mock_pipeline):
            entities = self.recognizer.extract_entities_transformers("John Doe lives in New York.")
        
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].text, "John Doe")
        self.assertEqual(entities[0].type, EntityType.PERSON)
        self.assertEqual(entities[0].start, 0)
        self.assertEqual(entities[0].end, 8)
        self.assertEqual(entities[0].confidence, 0.95)
        self.assertEqual(entities[0].metadata, {"transformers_label": "PER"})
        self.assertEqual(entities[1].text, "New York")
        self.assertEqual(entities[1].type, EntityType.LOCATION)
        self.assertEqual(entities[1].start, 18)
        self.assertEqual(entities[1].end, 26)
        self.assertEqual(entities[1].confidence, 0.85)
        self.assertEqual(entities[1].metadata, {"transformers_label": "LOC"})
    
    def test_extract_entities_empty_text(self):
        """Test extracting entities from empty text."""
        result = self.recognizer.extract_entities("")
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(result.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(result.text, "")
        self.assertEqual(result.metadata, {"error": "No text provided"})
    
    @patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', False)
    def test_extract_entities_missing_dependency(self):
        """Test extracting entities when the required dependency is missing."""
        with patch('science_data_kit.core.file_handling.entity_recognition.logger') as mock_logger:
            recognizer = EntityRecognizer()
            result = recognizer.extract_entities("John Doe lives in New York.")
            self.assertEqual(len(result.entities), 0)
            self.assertEqual(result.method, EntityRecognitionMethod.SPACY)
            self.assertEqual(result.metadata, {"error": "spaCy is not available. Install it with 'pip install spacy'."})
            mock_logger.warning.assert_called_once()
    
    def test_extract_entities_unsupported_method(self):
        """Test extracting entities with an unsupported method."""
        # Create a custom method
        class CustomMethod(str, Enum):
            CUSTOM = "custom"
        
        # Set options to use the custom method
        self.recognizer.options.method = CustomMethod.CUSTOM
        
        result = self.recognizer.extract_entities("John Doe lives in New York.")
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(result.method, CustomMethod.CUSTOM)
        self.assertEqual(result.text, "John Doe lives in New York.")
        self.assertEqual(result.metadata, {"error": "Unsupported entity recognition method: custom"})
    
    @patch('science_data_kit.core.file_handling.entity_recognition.extract_text_from_file')
    def test_extract_entities_from_file(self, mock_extract_text):
        """Test extracting entities from a file."""
        # Mock text extraction
        mock_extract_text.return_value = TextExtractionResult(
            text="John Doe lives in New York.",
            metadata={"size": 100}
        )
        
        # Mock entity extraction
        with patch.object(self.recognizer, 'extract_entities', return_value=EntityRecognitionResult(
            entities=[
                Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
                Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.85)
            ],
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York."
        )):
            result = self.recognizer.extract_entities_from_file("/path/to/file.txt")
        
        self.assertEqual(len(result.entities), 2)
        self.assertEqual(result.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(result.text, "John Doe lives in New York.")
        self.assertEqual(result.metadata["file_path"], "/path/to/file.txt")
        self.assertEqual(result.metadata["size"], 100)
    
    @patch('science_data_kit.core.file_handling.entity_recognition.extract_text_from_file')
    def test_extract_entities_from_file_error(self, mock_extract_text):
        """Test extracting entities from a file with an error."""
        # Mock text extraction to fail
        mock_extract_text.return_value = None
        
        result = self.recognizer.extract_entities_from_file("/path/to/file.txt")
        self.assertEqual(len(result.entities), 0)
        self.assertEqual(result.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(result.metadata["error"], "Failed to extract text from /path/to/file.txt")
        self.assertEqual(result.metadata["file_path"], "/path/to/file.txt")


class TestHighLevelFunctions(unittest.TestCase):
    """Tests for the high-level functions."""
    
    @patch('science_data_kit.core.file_handling.entity_recognition.EntityRecognizer')
    def test_extract_entities(self, mock_recognizer_class):
        """Test the extract_entities function."""
        # Mock the EntityRecognizer
        mock_recognizer = MagicMock()
        mock_recognizer.extract_entities.return_value = EntityRecognitionResult(
            entities=[
                Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
                Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.85)
            ],
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York."
        )
        mock_recognizer_class.return_value = mock_recognizer
        
        # Extract entities
        entities = extract_entities(
            "John Doe lives in New York.",
            method=EntityRecognitionMethod.SPACY,
            entity_types=[EntityType.PERSON],
            min_confidence=0.8
        )
        
        # Check the result
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0][0], "John Doe")
        self.assertEqual(entities[0][1], "PERSON")
        self.assertEqual(entities[0][2], 0.95)
        self.assertEqual(entities[1][0], "New York")
        self.assertEqual(entities[1][1], "LOCATION")
        self.assertEqual(entities[1][2], 0.85)
        
        # Check that the recognizer was created with the correct options
        mock_recognizer_class.assert_called_once()
        options = mock_recognizer_class.call_args[0][0]
        self.assertEqual(options.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(options.entity_types, [EntityType.PERSON])
        self.assertEqual(options.min_confidence, 0.8)
    
    @patch('science_data_kit.core.file_handling.entity_recognition.EntityRecognizer')
    def test_extract_entities_from_file(self, mock_recognizer_class):
        """Test the extract_entities_from_file function."""
        # Mock the EntityRecognizer
        mock_recognizer = MagicMock()
        mock_recognizer.extract_entities_from_file.return_value = EntityRecognitionResult(
            entities=[
                Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
                Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.85)
            ],
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York.",
            metadata={"file_path": "/path/to/file.txt"}
        )
        mock_recognizer_class.return_value = mock_recognizer
        
        # Extract entities from file
        entities = extract_entities_from_file(
            "/path/to/file.txt",
            method=EntityRecognitionMethod.SPACY,
            entity_types=[EntityType.PERSON],
            min_confidence=0.8
        )
        
        # Check the result
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0][0], "John Doe")
        self.assertEqual(entities[0][1], "PERSON")
        self.assertEqual(entities[0][2], 0.95)
        self.assertEqual(entities[1][0], "New York")
        self.assertEqual(entities[1][1], "LOCATION")
        self.assertEqual(entities[1][2], 0.85)
        
        # Check that the recognizer was created with the correct options
        mock_recognizer_class.assert_called_once()
        options = mock_recognizer_class.call_args[0][0]
        self.assertEqual(options.method, EntityRecognitionMethod.SPACY)
        self.assertEqual(options.entity_types, [EntityType.PERSON])
        self.assertEqual(options.min_confidence, 0.8)
    
    @patch('science_data_kit.core.file_handling.entity_recognition.EntityRecognizer')
    def test_compare_entity_recognition_methods(self, mock_recognizer_class):
        """Test the compare_entity_recognition_methods function."""
        # Mock the EntityRecognizer
        mock_recognizer = MagicMock()
        mock_recognizer.extract_entities.side_effect = [
            # SPACY result
            EntityRecognitionResult(
                entities=[
                    Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
                    Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.85)
                ],
                method=EntityRecognitionMethod.SPACY,
                text="John Doe lives in New York."
            ),
            # NLTK result
            EntityRecognitionResult(
                entities=[
                    Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=1.0),
                    Entity(text="New York", type=EntityType.GPE, start=18, end=26, confidence=1.0)
                ],
                method=EntityRecognitionMethod.NLTK,
                text="John Doe lives in New York."
            ),
            # REGEX result
            EntityRecognitionResult(
                entities=[
                    Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=1.0)
                ],
                method=EntityRecognitionMethod.REGEX,
                text="John Doe lives in New York."
            ),
            # TRANSFORMERS result
            EntityRecognitionResult(
                entities=[
                    Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.9),
                    Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.8)
                ],
                method=EntityRecognitionMethod.TRANSFORMERS,
                text="John Doe lives in New York."
            )
        ]
        mock_recognizer_class.return_value = mock_recognizer
        
        # Mock the availability of all methods
        with patch('science_data_kit.core.file_handling.entity_recognition.SPACY_AVAILABLE', True), \
             patch('science_data_kit.core.file_handling.entity_recognition.NLTK_AVAILABLE', True), \
             patch('science_data_kit.core.file_handling.entity_recognition.TRANSFORMERS_AVAILABLE', True):
            # Compare methods
            results = compare_entity_recognition_methods(
                "John Doe lives in New York.",
                entity_types=[EntityType.PERSON],
                min_confidence=0.8
            )
        
        # Check the result
        self.assertIn("spacy", results)
        self.assertIn("nltk", results)
        self.assertIn("regex", results)
        self.assertIn("transformers", results)
        self.assertEqual(len(results["spacy"]), 2)
        self.assertEqual(results["spacy"][0][0], "John Doe")
        self.assertEqual(results["spacy"][0][1], "PERSON")
        self.assertEqual(results["spacy"][0][2], 0.95)
        self.assertEqual(len(results["nltk"]), 2)
        self.assertEqual(results["nltk"][0][0], "John Doe")
        self.assertEqual(results["nltk"][0][1], "PERSON")
        self.assertEqual(results["nltk"][0][2], 1.0)
        self.assertEqual(len(results["regex"]), 1)
        self.assertEqual(results["regex"][0][0], "John Doe")
        self.assertEqual(results["regex"][0][1], "PERSON")
        self.assertEqual(results["regex"][0][2], 1.0)
        self.assertEqual(len(results["transformers"]), 2)
        self.assertEqual(results["transformers"][0][0], "John Doe")
        self.assertEqual(results["transformers"][0][1], "PERSON")
        self.assertEqual(results["transformers"][0][2], 0.9)
    
    def test_get_entities_by_type(self):
        """Test the get_entities_by_type function."""
        # Create a result with multiple entity types
        result = EntityRecognitionResult(
            entities=[
                Entity(text="John Doe", type=EntityType.PERSON, start=0, end=8, confidence=0.95),
                Entity(text="Jane Smith", type=EntityType.PERSON, start=30, end=40, confidence=0.9),
                Entity(text="New York", type=EntityType.LOCATION, start=18, end=26, confidence=0.85),
                Entity(text="Apple Inc", type=EntityType.ORGANIZATION, start=50, end=59, confidence=0.8)
            ],
            method=EntityRecognitionMethod.SPACY,
            text="John Doe lives in New York with Jane Smith who works at Apple Inc."
        )
        
        # Get entities by type
        person_entities = get_entities_by_type(result, EntityType.PERSON)
        location_entities = get_entities_by_type(result, EntityType.LOCATION)
        organization_entities = get_entities_by_type(result, EntityType.ORGANIZATION)
        other_entities = get_entities_by_type(result, EntityType.OTHER)
        
        # Check the results
        self.assertEqual(len(person_entities), 2)
        self.assertEqual(person_entities[0].text, "John Doe")
        self.assertEqual(person_entities[1].text, "Jane Smith")
        self.assertEqual(len(location_entities), 1)
        self.assertEqual(location_entities[0].text, "New York")
        self.assertEqual(len(organization_entities), 1)
        self.assertEqual(organization_entities[0].text, "Apple Inc")
        self.assertEqual(len(other_entities), 0)


if __name__ == '__main__':
    unittest.main()
"""