"""
Google Cloud Translation AI Service Integration for Science Data Kit

This module provides integration with Google Cloud Translation API for text translation,
enabling advanced language processing capabilities within the Science Data Kit.

The module includes:
1. A plugin implementation for Google Cloud Translation API
2. Translation capabilities using Translation API features
3. Utility functions for working with Translation API results

This integration allows researchers to translate text between different languages using Google's powerful
translation capabilities directly within the Science Data Kit.
"""

import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

try:
    from google.cloud import translate_v2 as translate
    from google.oauth2 import service_account
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, AIServicePlugin, TranslationCapability,
    TranslationResult
)
from science_data_kit.core.integrations.plugin_architecture import (
    PluginCategory, PluginMetadata, register_plugin
)

# Set up logging
logger = logging.getLogger(__name__)


@register_plugin
class GoogleTranslateService(AIServicePlugin, TranslationCapability):
    """
    Google Cloud Translation API integration for text translation.

    This plugin provides integration with Google Cloud Translation API for text translation,
    enabling advanced language processing capabilities such as language detection and
    translation between multiple languages.
    """

    def __init__(self):
        """Initialize the Google Translation service plugin."""
        self._client = None
        self._credentials_path = None
        self._authenticated = False
        self._supported_languages = {}

    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="google_translate",
            version="1.0.0",
            description="Google Cloud Translation API integration for text translation",
            author="Science Data Kit Team",
            category=PluginCategory.OTHER,
            dependencies=[],
            website="https://cloud.google.com/translate",
            tags=["ai", "text", "translation", "language", "google"],
            enabled=GOOGLE_TRANSLATE_AVAILABLE,
            capabilities=[
                AIServiceCapability.TRANSLATION.value,
                AIServiceCapability.LANGUAGE_DETECTION.value
            ],
            priority=10  # High priority
        )

    @property
    def service_type(self) -> str:
        """Get the type of AI service."""
        return "translation"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if not GOOGLE_TRANSLATE_AVAILABLE:
            logger.warning("Google Cloud Translation API is not available. Install google-cloud-translate package.")
            return False

        # Check for credentials in environment variable
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            try:
                self._credentials_path = credentials_path
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Google Translation service: {str(e)}")
                return False
        else:
            logger.warning("Google Cloud Translation API credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
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
        Authenticate with the Google Cloud Translation API.

        Args:
            credentials_path: Path to the Google Cloud service account credentials JSON file.
                             If None, uses the path from GOOGLE_APPLICATION_CREDENTIALS environment variable.
            **kwargs: Additional authentication parameters.

        Returns:
            True if authentication was successful, False otherwise.
        """
        if not GOOGLE_TRANSLATE_AVAILABLE:
            logger.error("Google Cloud Translation API is not available. Install google-cloud-translate package.")
            return False

        try:
            # Use provided credentials path or fall back to environment variable
            if credentials_path:
                self._credentials_path = credentials_path
            elif not self._credentials_path:
                self._credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if not self._credentials_path or not os.path.exists(self._credentials_path):
                logger.error("Google Cloud Translation API credentials not found.")
                return False

            # Create credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )

            # Create client with credentials
            self._client = translate.Client(credentials=credentials)
            self._authenticated = True
            
            # Cache supported languages
            self._load_supported_languages()
            
            logger.info("Successfully authenticated with Google Cloud Translation API")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Cloud Translation API: {str(e)}")
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
            AIServiceCapability.TRANSLATION,
            AIServiceCapability.LANGUAGE_DETECTION
        ]

    def _load_supported_languages(self) -> None:
        """
        Load the list of supported languages from the Google Cloud Translation API.
        """
        if not self.is_authenticated():
            return
            
        try:
            # Get supported languages
            languages = self._client.get_languages()
            
            # Create a mapping of language codes to target languages
            self._supported_languages = {}
            for language in languages:
                self._supported_languages[language['language']] = [l['language'] for l in languages]
                
            logger.info(f"Loaded {len(languages)} supported languages from Google Cloud Translation API")
        except Exception as e:
            logger.error(f"Failed to load supported languages: {str(e)}")
            self._supported_languages = {}

    def get_supported_translation_languages(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of supported source and target languages for translation.

        Returns:
            Dictionary mapping source language codes to lists of target language codes.
        """
        if not self._supported_languages and self.is_authenticated():
            self._load_supported_languages()
            
        return self._supported_languages

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None, **kwargs) -> TranslationResult:
        """
        Translate text using the Google Cloud Translation API.

        Args:
            text: The text to translate.
            target_language: The language code to translate to.
            source_language: The language code to translate from (if None, auto-detect).
            **kwargs: Additional parameters for the translation, including:
                      - format: The format of the text (html or text, default: text)
                      - model: The translation model to use (default: nmt)

        Returns:
            TranslationResult containing the translation results.
        """
        if not self.is_authenticated():
            if not self.authenticate():
                return TranslationResult(
                    success=False,
                    service_name=self.metadata.name,
                    error_message="Not authenticated with Google Cloud Translation API"
                )

        try:
            # Get additional parameters
            format_type = kwargs.get('format', 'text')
            model = kwargs.get('model', 'nmt')

            # Send request to Google Cloud Translation API
            response = self._client.translate(
                text,
                target_language=target_language,
                source_language=source_language,
                format_=format_type,
                model=model
            )

            # Process response
            if isinstance(response, list):
                # Multiple translations
                translations = response
            else:
                # Single translation
                translations = [response]

            # Create result
            result = TranslationResult(
                success=True,
                service_name=self.metadata.name,
                raw_response=response
            )

            # Extract translation and metadata
            if translations:
                result.translated_text = translations[0]['translatedText']
                result.source_language = translations[0]['detectedSourceLanguage'] if source_language is None else source_language
                result.target_language = target_language
                result.confidence = 1.0  # Google Translate doesn't provide confidence scores
                
                # Extract alternatives (if multiple translations were requested)
                result.alternatives = [
                    {
                        'translated_text': t['translatedText'],
                        'source_language': t['detectedSourceLanguage'] if source_language is None else source_language,
                        'target_language': target_language
                    }
                    for t in translations
                ]

            # Add metadata
            result.metadata = {
                'format': format_type,
                'model': model,
                'service': 'Google Cloud Translation API'
            }

            return result

        except Exception as e:
            logger.error(f"Error translating text with Google Cloud Translation API: {str(e)}")
            return TranslationResult(
                success=False,
                service_name=self.metadata.name,
                error_message=f"Error translating text: {str(e)}"
            )

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of a text using the Google Cloud Translation API.

        Args:
            text: The text to detect the language of.

        Returns:
            Dictionary containing the detected language and confidence.
        """
        if not self.is_authenticated():
            if not self.authenticate():
                return {
                    'success': False,
                    'error_message': "Not authenticated with Google Cloud Translation API"
                }

        try:
            # Send request to Google Cloud Translation API
            response = self._client.detect_language(text)

            # Process response
            if isinstance(response, list):
                # Multiple detections
                detections = response
            else:
                # Single detection
                detections = [response]

            # Extract detection results
            if detections:
                return {
                    'success': True,
                    'language': detections[0]['language'],
                    'confidence': detections[0]['confidence'],
                    'alternatives': [
                        {
                            'language': d['language'],
                            'confidence': d['confidence']
                        }
                        for d in detections
                    ]
                }
            else:
                return {
                    'success': False,
                    'error_message': "No language detected"
                }

        except Exception as e:
            logger.error(f"Error detecting language with Google Cloud Translation API: {str(e)}")
            return {
                'success': False,
                'error_message': f"Error detecting language: {str(e)}"
            }
"""