"""
Google Cloud Natural Language AI Service Integration for Science Data Kit

This module provides integration with Google Cloud Natural Language API for text analysis,
enabling advanced text processing capabilities within the Science Data Kit.

The module includes:
1. A plugin implementation for Google Cloud Natural Language API
2. Text analysis capabilities using Natural Language API features
3. Utility functions for working with Natural Language API results

This integration allows researchers to analyze text using Google's powerful
natural language processing capabilities directly within the Science Data Kit.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

try:
    from google.cloud import language_v1
    from google.oauth2 import service_account
    GOOGLE_LANGUAGE_AVAILABLE = True
except ImportError:
    GOOGLE_LANGUAGE_AVAILABLE = False

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, AIServicePlugin, TextAnalysisCapability,
    TextAnalysisResult
)
from science_data_kit.core.integrations.plugin_architecture import (
    PluginCategory, PluginMetadata, register_plugin
)

# Set up logging
logger = logging.getLogger(__name__)


@register_plugin
class GoogleLanguageService(AIServicePlugin, TextAnalysisCapability):
    """
    Google Cloud Natural Language API integration for text analysis.

    This plugin provides integration with Google Cloud Natural Language API for text analysis,
    enabling advanced text processing capabilities such as entity recognition, sentiment analysis,
    content classification, and syntax analysis.
    """

    def __init__(self):
        """Initialize the Google Natural Language service plugin."""
        self._client = None
        self._credentials_path = None
        self._authenticated = False

    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="google_language",
            version="1.0.0",
            description="Google Cloud Natural Language API integration for text analysis",
            author="Science Data Kit Team",
            category=PluginCategory.OTHER,
            dependencies=[],
            website="https://cloud.google.com/natural-language",
            tags=["ai", "text", "analysis", "nlp", "google"],
            enabled=GOOGLE_LANGUAGE_AVAILABLE,
            capabilities=[
                AIServiceCapability.TEXT_ANALYSIS.value,
                AIServiceCapability.ENTITY_RECOGNITION.value,
                AIServiceCapability.SENTIMENT_ANALYSIS.value,
                AIServiceCapability.LANGUAGE_DETECTION.value,
                AIServiceCapability.CONTENT_SUMMARIZATION.value
            ],
            priority=10  # High priority
        )

    @property
    def service_type(self) -> str:
        """Get the type of AI service."""
        return "text_analysis"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if not GOOGLE_LANGUAGE_AVAILABLE:
            logger.warning("Google Cloud Natural Language API is not available. Install google-cloud-language package.")
            return False

        # Check for credentials in environment variable
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            try:
                self._credentials_path = credentials_path
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Google Natural Language service: {str(e)}")
                return False
        else:
            logger.warning("Google Cloud Natural Language API credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
            return True  # Return True to allow initialization without credentials

    def shutdown(self) -> bool:
        """
        Shut down the plugin and release any resources.

        Returns:
            True if shutdown was successful, False otherwise.
        """
        self._client = None
        self._authenticated = False
        return True

    def authenticate(self, credentials_path: Optional[str] = None, **kwargs) -> bool:
        """
        Authenticate with the Google Cloud Natural Language API.

        Args:
            credentials_path: Path to the Google Cloud service account credentials JSON file.
                             If None, uses the path from GOOGLE_APPLICATION_CREDENTIALS environment variable.
            **kwargs: Additional authentication parameters.

        Returns:
            True if authentication was successful, False otherwise.
        """
        if not GOOGLE_LANGUAGE_AVAILABLE:
            logger.error("Google Cloud Natural Language API is not available. Install google-cloud-language package.")
            return False

        try:
            # Use provided credentials path or fall back to environment variable
            if credentials_path:
                self._credentials_path = credentials_path
            elif not self._credentials_path:
                self._credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if not self._credentials_path or not os.path.exists(self._credentials_path):
                logger.error("Google Cloud Natural Language API credentials not found.")
                return False

            # Create credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )

            # Create client with credentials
            self._client = language_v1.LanguageServiceClient(credentials=credentials)
            self._authenticated = True
            logger.info("Successfully authenticated with Google Cloud Natural Language API")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Cloud Natural Language API: {str(e)}")
            self._authenticated = False
            return False

    def is_authenticated(self) -> bool:
        """
        Check if the plugin is currently authenticated with the AI service.

        Returns:
            True if authenticated, False otherwise.
        """
        return self._authenticated and self._client is not None

    def get_capabilities(self) -> List[AIServiceCapability]:
        """
        Get a list of capabilities provided by this AI service.

        Returns:
            List of AIServiceCapability values.
        """
        return [
            AIServiceCapability.TEXT_ANALYSIS,
            AIServiceCapability.ENTITY_RECOGNITION,
            AIServiceCapability.SENTIMENT_ANALYSIS,
            AIServiceCapability.LANGUAGE_DETECTION,
            AIServiceCapability.CONTENT_SUMMARIZATION
        ]

    def get_supported_languages(self) -> List[str]:
        """
        Get a list of languages supported by this service.

        Returns:
            List of supported language codes.
        """
        return [
            'en', 'zh', 'zh-Hant', 'zh-Hans', 'ja', 'ko', 'es', 'pt', 'fr', 'de',
            'it', 'nl', 'ru', 'ar', 'hi', 'id', 'th', 'vi', 'pl', 'uk', 'tr'
        ]

    def get_supported_text_features(self) -> List[str]:
        """
        Get a list of text analysis features supported by this service.

        Returns:
            List of supported features.
        """
        return [
            'entities', 'sentiment', 'syntax', 'categories', 'language'
        ]

    def analyze_text(self, text: str, features: List[str] = None, **kwargs) -> TextAnalysisResult:
        """
        Analyze text using the Google Cloud Natural Language API.

        Args:
            text: The text to analyze.
            features: List of specific features to analyze (e.g., 'entities', 'sentiment', 'syntax').
                     If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            TextAnalysisResult containing the analysis results.
        """
        if not self.is_authenticated():
            if not self.authenticate():
                return TextAnalysisResult(
                    success=False,
                    service_name=self.metadata.name,
                    error_message="Not authenticated with Google Cloud Natural Language API"
                )

        try:
            # Determine which features to analyze
            if features is None:
                features = ['entities', 'sentiment', 'syntax', 'categories', 'language']

            # Get language from kwargs or detect it
            language = kwargs.get('language')

            # Create document object
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT,
                language=language
            )

            # Initialize result
            result = TextAnalysisResult(
                success=True,
                service_name=self.metadata.name
            )

            # Analyze entities
            if 'entities' in features:
                try:
                    entity_response = self._client.analyze_entities(
                        document=document,
                        encoding_type=language_v1.EncodingType.UTF8
                    )
                    result.entities = [
                        {
                            'name': entity.name,
                            'type': self._entity_type_to_string(entity.type_),
                            'salience': entity.salience,
                            'mentions': [
                                {
                                    'text': mention.text.content,
                                    'type': self._mention_type_to_string(mention.type_),
                                    'start': mention.text.begin_offset
                                }
                                for mention in entity.mentions
                            ],
                            'metadata': dict(entity.metadata)
                        }
                        for entity in entity_response.entities
                    ]
                except Exception as e:
                    logger.warning(f"Error analyzing entities: {str(e)}")

            # Analyze sentiment
            if 'sentiment' in features:
                try:
                    sentiment_response = self._client.analyze_sentiment(
                        document=document,
                        encoding_type=language_v1.EncodingType.UTF8
                    )
                    result.sentiment = {
                        'score': sentiment_response.document_sentiment.score,
                        'magnitude': sentiment_response.document_sentiment.magnitude,
                        'sentences': [
                            {
                                'text': sentence.text.content,
                                'score': sentence.sentiment.score,
                                'magnitude': sentence.sentiment.magnitude,
                                'start': sentence.text.begin_offset
                            }
                            for sentence in sentiment_response.sentences
                        ]
                    }
                except Exception as e:
                    logger.warning(f"Error analyzing sentiment: {str(e)}")

            # Analyze syntax
            if 'syntax' in features:
                try:
                    syntax_response = self._client.analyze_syntax(
                        document=document,
                        encoding_type=language_v1.EncodingType.UTF8
                    )
                    result.syntax = {
                        'tokens': [
                            {
                                'text': token.text.content,
                                'part_of_speech': self._pos_tag_to_string(token.part_of_speech.tag),
                                'dependency_edge': {
                                    'head_token_index': token.dependency_edge.head_token_index,
                                    'label': self._dependency_label_to_string(token.dependency_edge.label)
                                },
                                'lemma': token.lemma,
                                'start': token.text.begin_offset
                            }
                            for token in syntax_response.tokens
                        ]
                    }
                except Exception as e:
                    logger.warning(f"Error analyzing syntax: {str(e)}")

            # Analyze categories
            if 'categories' in features:
                try:
                    category_response = self._client.classify_text(document=document)
                    result.categories = [
                        {
                            'name': category.name,
                            'confidence': category.confidence
                        }
                        for category in category_response.categories
                    ]
                except Exception as e:
                    logger.warning(f"Error analyzing categories: {str(e)}")

            # Detect language
            if 'language' in features and not language:
                try:
                    language_response = self._client.analyze_sentiment(
                        document=document,
                        encoding_type=language_v1.EncodingType.UTF8
                    )
                    result.language = {
                        'language_code': language_response.language,
                        'confidence': 1.0  # Google doesn't provide confidence for language detection
                    }
                except Exception as e:
                    logger.warning(f"Error detecting language: {str(e)}")

            # Generate summary (using a simple extractive approach)
            if 'summary' in features:
                try:
                    # Use sentiment analysis to identify important sentences
                    if result.sentiment and result.sentiment.get('sentences'):
                        # Sort sentences by sentiment magnitude * score (absolute)
                        sentences = sorted(
                            result.sentiment['sentences'],
                            key=lambda s: abs(s['score']) * s['magnitude'],
                            reverse=True
                        )
                        
                        # Take top 3 sentences or fewer if there are less than 3
                        top_sentences = sentences[:min(3, len(sentences))]
                        
                        # Sort by position in the original text
                        top_sentences.sort(key=lambda s: s['start'])
                        
                        # Join sentences to form summary
                        result.summary = ' '.join(s['text'] for s in top_sentences)
                except Exception as e:
                    logger.warning(f"Error generating summary: {str(e)}")

            # Extract keywords (using entities as a proxy)
            if 'keywords' in features:
                try:
                    if result.entities:
                        # Use entities with high salience as keywords
                        result.keywords = [
                            {
                                'text': entity['name'],
                                'score': entity['salience'],
                                'type': entity['type']
                            }
                            for entity in result.entities
                            if entity['salience'] > 0.1  # Only include significant entities
                        ]
                        
                        # Sort by salience (descending)
                        result.keywords.sort(key=lambda k: k['score'], reverse=True)
                except Exception as e:
                    logger.warning(f"Error extracting keywords: {str(e)}")

            # Add metadata
            result.metadata = {
                'text_length': len(text),
                'features_analyzed': features,
                'service': 'Google Cloud Natural Language API'
            }

            return result

        except Exception as e:
            logger.error(f"Error analyzing text with Google Cloud Natural Language API: {str(e)}")
            return TextAnalysisResult(
                success=False,
                service_name=self.metadata.name,
                error_message=f"Error analyzing text: {str(e)}"
            )

    def _entity_type_to_string(self, entity_type: int) -> str:
        """
        Convert a Google Cloud Natural Language entity type enum to a string.

        Args:
            entity_type: Google Cloud Natural Language entity type enum value.

        Returns:
            String representation of the entity type.
        """
        entity_types = {
            language_v1.Entity.Type.UNKNOWN: "UNKNOWN",
            language_v1.Entity.Type.PERSON: "PERSON",
            language_v1.Entity.Type.LOCATION: "LOCATION",
            language_v1.Entity.Type.ORGANIZATION: "ORGANIZATION",
            language_v1.Entity.Type.EVENT: "EVENT",
            language_v1.Entity.Type.WORK_OF_ART: "WORK_OF_ART",
            language_v1.Entity.Type.CONSUMER_GOOD: "CONSUMER_GOOD",
            language_v1.Entity.Type.OTHER: "OTHER",
            language_v1.Entity.Type.PHONE_NUMBER: "PHONE_NUMBER",
            language_v1.Entity.Type.ADDRESS: "ADDRESS",
            language_v1.Entity.Type.DATE: "DATE",
            language_v1.Entity.Type.NUMBER: "NUMBER",
            language_v1.Entity.Type.PRICE: "PRICE"
        }
        return entity_types.get(entity_type, "UNKNOWN")

    def _mention_type_to_string(self, mention_type: int) -> str:
        """
        Convert a Google Cloud Natural Language mention type enum to a string.

        Args:
            mention_type: Google Cloud Natural Language mention type enum value.

        Returns:
            String representation of the mention type.
        """
        mention_types = {
            language_v1.EntityMention.Type.TYPE_UNKNOWN: "UNKNOWN",
            language_v1.EntityMention.Type.PROPER: "PROPER",
            language_v1.EntityMention.Type.COMMON: "COMMON"
        }
        return mention_types.get(mention_type, "UNKNOWN")

    def _pos_tag_to_string(self, pos_tag: int) -> str:
        """
        Convert a Google Cloud Natural Language part-of-speech tag enum to a string.

        Args:
            pos_tag: Google Cloud Natural Language part-of-speech tag enum value.

        Returns:
            String representation of the part-of-speech tag.
        """
        pos_tags = {
            language_v1.PartOfSpeech.Tag.UNKNOWN: "UNKNOWN",
            language_v1.PartOfSpeech.Tag.ADJ: "ADJ",
            language_v1.PartOfSpeech.Tag.ADP: "ADP",
            language_v1.PartOfSpeech.Tag.ADV: "ADV",
            language_v1.PartOfSpeech.Tag.CONJ: "CONJ",
            language_v1.PartOfSpeech.Tag.DET: "DET",
            language_v1.PartOfSpeech.Tag.NOUN: "NOUN",
            language_v1.PartOfSpeech.Tag.NUM: "NUM",
            language_v1.PartOfSpeech.Tag.PRON: "PRON",
            language_v1.PartOfSpeech.Tag.PRT: "PRT",
            language_v1.PartOfSpeech.Tag.PUNCT: "PUNCT",
            language_v1.PartOfSpeech.Tag.VERB: "VERB",
            language_v1.PartOfSpeech.Tag.X: "X",
            language_v1.PartOfSpeech.Tag.AFFIX: "AFFIX"
        }
        return pos_tags.get(pos_tag, "UNKNOWN")

    def _dependency_label_to_string(self, dependency_label: int) -> str:
        """
        Convert a Google Cloud Natural Language dependency label enum to a string.

        Args:
            dependency_label: Google Cloud Natural Language dependency label enum value.

        Returns:
            String representation of the dependency label.
        """
        dependency_labels = {
            language_v1.DependencyEdge.Label.UNKNOWN: "UNKNOWN",
            language_v1.DependencyEdge.Label.ABBREV: "ABBREV",
            language_v1.DependencyEdge.Label.ACOMP: "ACOMP",
            language_v1.DependencyEdge.Label.ADVCL: "ADVCL",
            language_v1.DependencyEdge.Label.ADVMOD: "ADVMOD",
            language_v1.DependencyEdge.Label.AMOD: "AMOD",
            language_v1.DependencyEdge.Label.APPOS: "APPOS",
            language_v1.DependencyEdge.Label.ATTR: "ATTR",
            language_v1.DependencyEdge.Label.AUX: "AUX",
            language_v1.DependencyEdge.Label.AUXPASS: "AUXPASS",
            language_v1.DependencyEdge.Label.CC: "CC",
            language_v1.DependencyEdge.Label.CCOMP: "CCOMP",
            language_v1.DependencyEdge.Label.CONJ: "CONJ",
            language_v1.DependencyEdge.Label.CSUBJ: "CSUBJ",
            language_v1.DependencyEdge.Label.CSUBJPASS: "CSUBJPASS",
            language_v1.DependencyEdge.Label.DEP: "DEP",
            language_v1.DependencyEdge.Label.DET: "DET",
            language_v1.DependencyEdge.Label.DISCOURSE: "DISCOURSE",
            language_v1.DependencyEdge.Label.DOBJ: "DOBJ",
            language_v1.DependencyEdge.Label.EXPL: "EXPL",
            language_v1.DependencyEdge.Label.GOESWITH: "GOESWITH",
            language_v1.DependencyEdge.Label.IOBJ: "IOBJ",
            language_v1.DependencyEdge.Label.MARK: "MARK",
            language_v1.DependencyEdge.Label.MWE: "MWE",
            language_v1.DependencyEdge.Label.MWV: "MWV",
            language_v1.DependencyEdge.Label.NEG: "NEG",
            language_v1.DependencyEdge.Label.NN: "NN",
            language_v1.DependencyEdge.Label.NPADVMOD: "NPADVMOD",
            language_v1.DependencyEdge.Label.NSUBJ: "NSUBJ",
            language_v1.DependencyEdge.Label.NSUBJPASS: "NSUBJPASS",
            language_v1.DependencyEdge.Label.NUM: "NUM",
            language_v1.DependencyEdge.Label.NUMBER: "NUMBER",
            language_v1.DependencyEdge.Label.P: "P",
            language_v1.DependencyEdge.Label.PARATAXIS: "PARATAXIS",
            language_v1.DependencyEdge.Label.PARTMOD: "PARTMOD",
            language_v1.DependencyEdge.Label.PCOMP: "PCOMP",
            language_v1.DependencyEdge.Label.POBJ: "POBJ",
            language_v1.DependencyEdge.Label.POSS: "POSS",
            language_v1.DependencyEdge.Label.POSTNEG: "POSTNEG",
            language_v1.DependencyEdge.Label.PRECOMP: "PRECOMP",
            language_v1.DependencyEdge.Label.PRECONJ: "PRECONJ",
            language_v1.DependencyEdge.Label.PREDET: "PREDET",
            language_v1.DependencyEdge.Label.PREF: "PREF",
            language_v1.DependencyEdge.Label.PREP: "PREP",
            language_v1.DependencyEdge.Label.PRONL: "PRONL",
            language_v1.DependencyEdge.Label.PRT: "PRT",
            language_v1.DependencyEdge.Label.PS: "PS",
            language_v1.DependencyEdge.Label.QUANTMOD: "QUANTMOD",
            language_v1.DependencyEdge.Label.RCMOD: "RCMOD",
            language_v1.DependencyEdge.Label.RCMODREL: "RCMODREL",
            language_v1.DependencyEdge.Label.RDROP: "RDROP",
            language_v1.DependencyEdge.Label.REF: "REF",
            language_v1.DependencyEdge.Label.REMNANT: "REMNANT",
            language_v1.DependencyEdge.Label.REPARANDUM: "REPARANDUM",
            language_v1.DependencyEdge.Label.ROOT: "ROOT",
            language_v1.DependencyEdge.Label.SNUM: "SNUM",
            language_v1.DependencyEdge.Label.SUFF: "SUFF",
            language_v1.DependencyEdge.Label.TMOD: "TMOD",
            language_v1.DependencyEdge.Label.TOPIC: "TOPIC",
            language_v1.DependencyEdge.Label.VMOD: "VMOD",
            language_v1.DependencyEdge.Label.VOCATIVE: "VOCATIVE",
            language_v1.DependencyEdge.Label.XCOMP: "XCOMP",
            language_v1.DependencyEdge.Label.SUFFIX: "SUFFIX",
            language_v1.DependencyEdge.Label.TITLE: "TITLE",
            language_v1.DependencyEdge.Label.ADVPHMOD: "ADVPHMOD",
            language_v1.DependencyEdge.Label.AUXCAUS: "AUXCAUS",
            language_v1.DependencyEdge.Label.AUXVV: "AUXVV",
            language_v1.DependencyEdge.Label.DTMOD: "DTMOD",
            language_v1.DependencyEdge.Label.FOREIGN: "FOREIGN",
            language_v1.DependencyEdge.Label.KW: "KW",
            language_v1.DependencyEdge.Label.LIST: "LIST",
            language_v1.DependencyEdge.Label.NOMC: "NOMC",
            language_v1.DependencyEdge.Label.NOMCSUBJ: "NOMCSUBJ",
            language_v1.DependencyEdge.Label.NOMCSUBJPASS: "NOMCSUBJPASS",
            language_v1.DependencyEdge.Label.NUMC: "NUMC",
            language_v1.DependencyEdge.Label.COP: "COP",
            language_v1.DependencyEdge.Label.DISLOCATED: "DISLOCATED",
            language_v1.DependencyEdge.Label.ASP: "ASP",
            language_v1.DependencyEdge.Label.GMOD: "GMOD",
            language_v1.DependencyEdge.Label.GOBJ: "GOBJ",
            language_v1.DependencyEdge.Label.INFMOD: "INFMOD",
            language_v1.DependencyEdge.Label.MES: "MES",
            language_v1.DependencyEdge.Label.NCOMP: "NCOMP"
        }
        return dependency_labels.get(dependency_label, "UNKNOWN")
"""