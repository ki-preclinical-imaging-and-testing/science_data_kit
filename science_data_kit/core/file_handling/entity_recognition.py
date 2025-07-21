"""
Entity recognition module for extracting named entities from documents.

This module provides functionality for extracting named entities from documents using
various entity recognition algorithms, including rule-based approaches and machine learning models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
import re

try:
    import spacy
    from spacy.language import Language
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from science_data_kit.core.file_handling.text_extraction import (
    TextExtractionOptions, extract_text_from_file, TextExtractionResult
)

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Enum for entity types."""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    FACILITY = "FACILITY"
    GPE = "GPE"  # Geopolitical Entity
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    NORP = "NORP"  # Nationalities, religious or political groups
    CARDINAL = "CARDINAL"  # Numerals that don't fall under another type
    ORDINAL = "ORDINAL"  # "first", "second", etc.
    QUANTITY = "QUANTITY"  # Measurements
    OTHER = "OTHER"  # Catch-all for other entity types


class EntityRecognitionMethod(str, Enum):
    """Enum for entity recognition methods."""
    SPACY = "spacy"  # spaCy NER
    NLTK = "nltk"  # NLTK NER
    REGEX = "regex"  # Regular expression-based NER
    TRANSFORMERS = "transformers"  # Hugging Face Transformers NER


@dataclass
class EntityRecognitionOptions:
    """Options for entity recognition."""
    method: EntityRecognitionMethod = EntityRecognitionMethod.SPACY
    entity_types: Optional[List[EntityType]] = None
    min_confidence: float = 0.5
    case_sensitive: bool = False
    
    # spaCy specific options
    spacy_model: str = "en_core_web_sm"
    
    # NLTK specific options
    nltk_download_resources: bool = True
    
    # Regex specific options
    regex_patterns: Optional[Dict[EntityType, List[str]]] = None
    
    # Transformers specific options
    transformers_model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    transformers_aggregation_strategy: str = "simple"
    
    # Text extraction options
    text_extraction_options: Optional[TextExtractionOptions] = None


@dataclass
class Entity:
    """Class representing a named entity."""
    text: str
    type: EntityType
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the entity."""
        return f"{self.text} ({self.type.value}, {self.confidence:.4f})"


@dataclass
class EntityRecognitionResult:
    """Result of entity recognition."""
    entities: List[Entity]
    method: EntityRecognitionMethod
    text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a string representation of the entity recognition result."""
        entities_by_type = {}
        for entity in self.entities:
            if entity.type not in entities_by_type:
                entities_by_type[entity.type] = []
            entities_by_type[entity.type].append(entity)
        
        result_str = [f"Method: {self.method.value}"]
        result_str.append(f"Total entities: {len(self.entities)}")
        
        for entity_type, entities in sorted(entities_by_type.items(), key=lambda x: x[0].value):
            entity_texts = [f"{entity.text} ({entity.confidence:.4f})" for entity in entities]
            result_str.append(f"{entity_type.value}: {', '.join(entity_texts)}")
        
        return "\n".join(result_str)


class EntityRecognizer:
    """Class for entity recognition."""
    
    def __init__(self, options: Optional[EntityRecognitionOptions] = None):
        """Initialize the entity recognizer.
        
        Args:
            options: Options for entity recognition.
        """
        self.options = options or EntityRecognitionOptions()
        self._spacy_nlp = None
        self._transformers_pipeline = None
        
        if self.options.method == EntityRecognitionMethod.SPACY and not SPACY_AVAILABLE:
            logger.warning(
                "spaCy is not available. Cannot use spaCy for entity recognition. "
                "Install spaCy with 'pip install spacy' and download the model with "
                f"'python -m spacy download {self.options.spacy_model}'."
            )
        
        if self.options.method == EntityRecognitionMethod.NLTK and not NLTK_AVAILABLE:
            logger.warning(
                "NLTK is not available. Cannot use NLTK for entity recognition. "
                "Install NLTK with 'pip install nltk'."
            )
        
        if self.options.method == EntityRecognitionMethod.TRANSFORMERS and not TRANSFORMERS_AVAILABLE:
            logger.warning(
                "Transformers is not available. Cannot use Transformers for entity recognition. "
                "Install Transformers with 'pip install transformers'."
            )
        
        # Initialize regex patterns if not provided
        if self.options.method == EntityRecognitionMethod.REGEX and not self.options.regex_patterns:
            self.options.regex_patterns = self._get_default_regex_patterns()
    
    def _get_default_regex_patterns(self) -> Dict[EntityType, List[str]]:
        """Get default regex patterns for entity recognition.
        
        Returns:
            Dict[EntityType, List[str]]: Dictionary mapping entity types to regex patterns.
        """
        return {
            EntityType.PERSON: [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Simple name pattern (e.g., John Doe)
                r'\bDr\. [A-Z][a-z]+\b',  # Dr. Name
                r'\bMr\. [A-Z][a-z]+\b',  # Mr. Name
                r'\bMrs\. [A-Z][a-z]+\b',  # Mrs. Name
                r'\bMs\. [A-Z][a-z]+\b',  # Ms. Name
                r'\bProf\. [A-Z][a-z]+\b',  # Prof. Name
            ],
            EntityType.ORGANIZATION: [
                r'\b[A-Z][a-z]+ (Inc|Corp|Corporation|Company|Co|Ltd)\b',  # Company names
                r'\b[A-Z][A-Za-z]+ (University|College|School|Institute)\b',  # Educational institutions
                r'\b[A-Z]{2,}\b',  # Acronyms (e.g., IBM, NASA)
            ],
            EntityType.LOCATION: [
                r'\b[A-Z][a-z]+ (Street|Avenue|Road|Boulevard|Lane|Drive|Place|Court)\b',  # Street addresses
                r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, State
            ],
            EntityType.DATE: [
                r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
                r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY or DD-MM-YYYY
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b',  # Month DD, YYYY
                r'\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b',  # DD Month YYYY
            ],
            EntityType.TIME: [
                r'\b\d{1,2}:\d{2}(:\d{2})? ?([AP]M)?\b',  # HH:MM:SS AM/PM or HH:MM AM/PM
            ],
            EntityType.MONEY: [
                r'\$\d+(\.\d{2})?\b',  # $X or $X.XX
                r'\b\d+ dollars\b',  # X dollars
                r'\b\d+(\.\d{2})? (USD|EUR|GBP|JPY|CAD|AUD|CHF)\b',  # X.XX Currency
            ],
            EntityType.PERCENT: [
                r'\b\d+(\.\d+)?%\b',  # X% or X.X%
                r'\b\d+(\.\d+)? percent\b',  # X percent or X.X percent
            ],
        }
    
    def _load_spacy_model(self) -> Optional[Language]:
        """Load the spaCy model.
        
        Returns:
            Optional[Language]: Loaded spaCy model or None if spaCy is not available.
        """
        if not SPACY_AVAILABLE:
            return None
        
        if self._spacy_nlp is None:
            try:
                self._spacy_nlp = spacy.load(self.options.spacy_model)
            except OSError:
                logger.error(
                    f"Could not load spaCy model '{self.options.spacy_model}'. "
                    f"Download it with 'python -m spacy download {self.options.spacy_model}'."
                )
                return None
        
        return self._spacy_nlp
    
    def _load_nltk_resources(self) -> bool:
        """Load NLTK resources.
        
        Returns:
            bool: True if resources were loaded successfully, False otherwise.
        """
        if not NLTK_AVAILABLE:
            return False
        
        if self.options.nltk_download_resources:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('maxent_ne_chunker', quiet=True)
                nltk.download('words', quiet=True)
                return True
            except Exception as e:
                logger.error(f"Error downloading NLTK resources: {e}")
                return False
        
        return True
    
    def _load_transformers_pipeline(self) -> Optional[Any]:
        """Load the Transformers pipeline.
        
        Returns:
            Optional[Any]: Loaded Transformers pipeline or None if Transformers is not available.
        """
        if not TRANSFORMERS_AVAILABLE:
            return None
        
        if self._transformers_pipeline is None:
            try:
                self._transformers_pipeline = pipeline(
                    "ner",
                    model=self.options.transformers_model,
                    aggregation_strategy=self.options.transformers_aggregation_strategy
                )
            except Exception as e:
                logger.error(f"Error loading Transformers pipeline: {e}")
                return None
        
        return self._transformers_pipeline
    
    def _map_spacy_entity_type(self, spacy_type: str) -> EntityType:
        """Map spaCy entity type to EntityType.
        
        Args:
            spacy_type: spaCy entity type.
            
        Returns:
            EntityType: Mapped entity type.
        """
        mapping = {
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.GPE,
            "LOC": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "TIME": EntityType.TIME,
            "MONEY": EntityType.MONEY,
            "PERCENT": EntityType.PERCENT,
            "FAC": EntityType.FACILITY,
            "PRODUCT": EntityType.PRODUCT,
            "EVENT": EntityType.EVENT,
            "WORK_OF_ART": EntityType.WORK_OF_ART,
            "LAW": EntityType.LAW,
            "LANGUAGE": EntityType.LANGUAGE,
            "NORP": EntityType.NORP,
            "CARDINAL": EntityType.CARDINAL,
            "ORDINAL": EntityType.ORDINAL,
            "QUANTITY": EntityType.QUANTITY,
        }
        
        return mapping.get(spacy_type, EntityType.OTHER)
    
    def _map_nltk_entity_type(self, nltk_type: str) -> EntityType:
        """Map NLTK entity type to EntityType.
        
        Args:
            nltk_type: NLTK entity type.
            
        Returns:
            EntityType: Mapped entity type.
        """
        mapping = {
            "PERSON": EntityType.PERSON,
            "ORGANIZATION": EntityType.ORGANIZATION,
            "GPE": EntityType.GPE,
            "LOCATION": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "TIME": EntityType.TIME,
            "MONEY": EntityType.MONEY,
            "PERCENT": EntityType.PERCENT,
            "FACILITY": EntityType.FACILITY,
        }
        
        return mapping.get(nltk_type, EntityType.OTHER)
    
    def _map_transformers_entity_type(self, transformers_type: str) -> EntityType:
        """Map Transformers entity type to EntityType.
        
        Args:
            transformers_type: Transformers entity type.
            
        Returns:
            EntityType: Mapped entity type.
        """
        mapping = {
            "PER": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "MISC": EntityType.OTHER,
            "B-PER": EntityType.PERSON,
            "I-PER": EntityType.PERSON,
            "B-ORG": EntityType.ORGANIZATION,
            "I-ORG": EntityType.ORGANIZATION,
            "B-LOC": EntityType.LOCATION,
            "I-LOC": EntityType.LOCATION,
            "B-MISC": EntityType.OTHER,
            "I-MISC": EntityType.OTHER,
        }
        
        return mapping.get(transformers_type, EntityType.OTHER)
    
    def _filter_entities_by_type(self, entities: List[Entity]) -> List[Entity]:
        """Filter entities by type.
        
        Args:
            entities: List of entities.
            
        Returns:
            List[Entity]: Filtered list of entities.
        """
        if not self.options.entity_types:
            return entities
        
        return [entity for entity in entities if entity.type in self.options.entity_types]
    
    def _filter_entities_by_confidence(self, entities: List[Entity]) -> List[Entity]:
        """Filter entities by confidence.
        
        Args:
            entities: List of entities.
            
        Returns:
            List[Entity]: Filtered list of entities.
        """
        return [entity for entity in entities if entity.confidence >= self.options.min_confidence]
    
    def extract_entities_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            List[Entity]: List of extracted entities.
        """
        nlp = self._load_spacy_model()
        if not nlp:
            return []
        
        doc = nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity_type = self._map_spacy_entity_type(ent.label_)
            entities.append(Entity(
                text=ent.text,
                type=entity_type,
                start=ent.start_char,
                end=ent.end_char,
                confidence=1.0,  # spaCy doesn't provide confidence scores
                metadata={"spacy_label": ent.label_}
            ))
        
        return entities
    
    def extract_entities_nltk(self, text: str) -> List[Entity]:
        """Extract entities using NLTK.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            List[Entity]: List of extracted entities.
        """
        if not NLTK_AVAILABLE or not self._load_nltk_resources():
            return []
        
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        ne_tree = ne_chunk(pos_tags)
        
        entities = []
        current_entity = None
        current_entity_type = None
        current_start = 0
        
        for i, chunk in enumerate(ne_tree):
            if hasattr(chunk, 'label'):
                # Start of a named entity
                if current_entity is None:
                    current_entity = [chunk[0][0]]
                    current_entity_type = chunk.label()
                    # Calculate start position in original text
                    if i > 0:
                        current_start = text.find(chunk[0][0], current_start)
                    else:
                        current_start = text.find(chunk[0][0])
                else:
                    # Continue current entity
                    current_entity.append(chunk[0][0])
            elif current_entity is not None:
                # End of a named entity
                entity_text = " ".join(current_entity)
                entity_type = self._map_nltk_entity_type(current_entity_type)
                end = current_start + len(entity_text)
                
                entities.append(Entity(
                    text=entity_text,
                    type=entity_type,
                    start=current_start,
                    end=end,
                    confidence=1.0,  # NLTK doesn't provide confidence scores
                    metadata={"nltk_label": current_entity_type}
                ))
                
                current_entity = None
                current_entity_type = None
        
        # Handle case where the last token is part of a named entity
        if current_entity is not None:
            entity_text = " ".join(current_entity)
            entity_type = self._map_nltk_entity_type(current_entity_type)
            end = current_start + len(entity_text)
            
            entities.append(Entity(
                text=entity_text,
                type=entity_type,
                start=current_start,
                end=end,
                confidence=1.0,  # NLTK doesn't provide confidence scores
                metadata={"nltk_label": current_entity_type}
            ))
        
        return entities
    
    def extract_entities_regex(self, text: str) -> List[Entity]:
        """Extract entities using regular expressions.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            List[Entity]: List of extracted entities.
        """
        if not self.options.regex_patterns:
            return []
        
        entities = []
        
        for entity_type, patterns in self.options.regex_patterns.items():
            for pattern in patterns:
                flags = 0 if self.options.case_sensitive else re.IGNORECASE
                for match in re.finditer(pattern, text, flags=flags):
                    entities.append(Entity(
                        text=match.group(0),
                        type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=1.0,  # Regex doesn't provide confidence scores
                        metadata={"pattern": pattern}
                    ))
        
        return entities
    
    def extract_entities_transformers(self, text: str) -> List[Entity]:
        """Extract entities using Transformers.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            List[Entity]: List of extracted entities.
        """
        pipeline = self._load_transformers_pipeline()
        if not pipeline:
            return []
        
        try:
            results = pipeline(text)
            entities = []
            
            for result in results:
                entity_type = self._map_transformers_entity_type(result["entity_group"])
                entities.append(Entity(
                    text=result["word"],
                    type=entity_type,
                    start=result["start"],
                    end=result["end"],
                    confidence=result["score"],
                    metadata={"transformers_label": result["entity_group"]}
                ))
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities with Transformers: {e}")
            return []
    
    def extract_entities(self, text: str) -> EntityRecognitionResult:
        """Extract entities from text.
        
        Args:
            text: Text to extract entities from.
            
        Returns:
            EntityRecognitionResult: Result of entity recognition.
        """
        if not text:
            return EntityRecognitionResult(
                entities=[],
                method=self.options.method,
                text=text,
                metadata={"error": "No text provided"}
            )
        
        if self.options.method == EntityRecognitionMethod.SPACY:
            if not SPACY_AVAILABLE:
                return self._handle_missing_dependency("spaCy")
            entities = self.extract_entities_spacy(text)
        
        elif self.options.method == EntityRecognitionMethod.NLTK:
            if not NLTK_AVAILABLE:
                return self._handle_missing_dependency("NLTK")
            entities = self.extract_entities_nltk(text)
        
        elif self.options.method == EntityRecognitionMethod.REGEX:
            entities = self.extract_entities_regex(text)
        
        elif self.options.method == EntityRecognitionMethod.TRANSFORMERS:
            if not TRANSFORMERS_AVAILABLE:
                return self._handle_missing_dependency("Transformers")
            entities = self.extract_entities_transformers(text)
        
        else:
            return EntityRecognitionResult(
                entities=[],
                method=self.options.method,
                text=text,
                metadata={"error": f"Unsupported entity recognition method: {self.options.method.value}"}
            )
        
        # Filter entities by type and confidence
        entities = self._filter_entities_by_type(entities)
        entities = self._filter_entities_by_confidence(entities)
        
        return EntityRecognitionResult(
            entities=entities,
            method=self.options.method,
            text=text
        )
    
    def _handle_missing_dependency(self, dependency: str) -> EntityRecognitionResult:
        """Handle missing dependency.
        
        Args:
            dependency: Name of the missing dependency.
            
        Returns:
            EntityRecognitionResult: Result with error message.
        """
        return EntityRecognitionResult(
            entities=[],
            method=self.options.method,
            metadata={"error": f"{dependency} is not available. Install it with 'pip install {dependency.lower()}'."}
        )
    
    def extract_entities_from_file(self, file_path: str) -> EntityRecognitionResult:
        """Extract entities from a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            EntityRecognitionResult: Result of entity recognition.
        """
        # Extract text from file
        result = extract_text_from_file(
            file_path, options=self.options.text_extraction_options
        )
        
        if not result:
            return EntityRecognitionResult(
                entities=[],
                method=self.options.method,
                metadata={"error": f"Failed to extract text from {file_path}", "file_path": file_path}
            )
        
        # Extract entities from text
        entity_result = self.extract_entities(result.text)
        
        # Add file metadata
        entity_result.metadata.update({
            "file_path": file_path,
            **result.metadata
        })
        
        return entity_result


def extract_entities(
    text: str,
    method: EntityRecognitionMethod = EntityRecognitionMethod.SPACY,
    entity_types: Optional[List[EntityType]] = None,
    min_confidence: float = 0.5,
    **kwargs
) -> List[Tuple[str, str, float]]:
    """Extract entities from text.
    
    Args:
        text: Text to extract entities from.
        method: Entity recognition method.
        entity_types: List of entity types to extract.
        min_confidence: Minimum confidence score for entities.
        **kwargs: Additional options for entity recognition.
        
    Returns:
        List[Tuple[str, str, float]]: List of (entity_text, entity_type, confidence) tuples.
    """
    options = EntityRecognitionOptions(
        method=method,
        entity_types=entity_types,
        min_confidence=min_confidence,
        **kwargs
    )
    
    recognizer = EntityRecognizer(options)
    result = recognizer.extract_entities(text)
    
    return [(entity.text, entity.type.value, entity.confidence) for entity in result.entities]


def extract_entities_from_file(
    file_path: str,
    method: EntityRecognitionMethod = EntityRecognitionMethod.SPACY,
    entity_types: Optional[List[EntityType]] = None,
    min_confidence: float = 0.5,
    **kwargs
) -> List[Tuple[str, str, float]]:
    """Extract entities from a file.
    
    Args:
        file_path: Path to the file.
        method: Entity recognition method.
        entity_types: List of entity types to extract.
        min_confidence: Minimum confidence score for entities.
        **kwargs: Additional options for entity recognition.
        
    Returns:
        List[Tuple[str, str, float]]: List of (entity_text, entity_type, confidence) tuples.
    """
    options = EntityRecognitionOptions(
        method=method,
        entity_types=entity_types,
        min_confidence=min_confidence,
        **kwargs
    )
    
    recognizer = EntityRecognizer(options)
    result = recognizer.extract_entities_from_file(file_path)
    
    return [(entity.text, entity.type.value, entity.confidence) for entity in result.entities]


def compare_entity_recognition_methods(
    text: str,
    entity_types: Optional[List[EntityType]] = None,
    min_confidence: float = 0.5,
    **kwargs
) -> Dict[str, List[Tuple[str, str, float]]]:
    """Compare different entity recognition methods on the same text.
    
    Args:
        text: Text to extract entities from.
        entity_types: List of entity types to extract.
        min_confidence: Minimum confidence score for entities.
        **kwargs: Additional options for entity recognition.
        
    Returns:
        Dict[str, List[Tuple[str, str, float]]]: Dictionary mapping method names to lists of entities.
    """
    results = {}
    
    for method in EntityRecognitionMethod:
        try:
            if method == EntityRecognitionMethod.SPACY and not SPACY_AVAILABLE:
                logger.warning(f"Skipping {method.value} as spaCy is not available")
                continue
            
            if method == EntityRecognitionMethod.NLTK and not NLTK_AVAILABLE:
                logger.warning(f"Skipping {method.value} as NLTK is not available")
                continue
            
            if method == EntityRecognitionMethod.TRANSFORMERS and not TRANSFORMERS_AVAILABLE:
                logger.warning(f"Skipping {method.value} as Transformers is not available")
                continue
            
            options = EntityRecognitionOptions(
                method=method,
                entity_types=entity_types,
                min_confidence=min_confidence,
                **kwargs
            )
            
            recognizer = EntityRecognizer(options)
            result = recognizer.extract_entities(text)
            
            results[method.value] = [(entity.text, entity.type.value, entity.confidence) for entity in result.entities]
        except Exception as e:
            logger.error(f"Error extracting entities with {method.value}: {e}")
            results[method.value] = []
    
    return results


def get_entities_by_type(
    result: EntityRecognitionResult,
    entity_type: EntityType
) -> List[Entity]:
    """Get entities of a specific type from an entity recognition result.
    
    Args:
        result: Entity recognition result.
        entity_type: Entity type to filter by.
        
    Returns:
        List[Entity]: List of entities of the specified type.
    """
    return [entity for entity in result.entities if entity.type == entity_type]
"""