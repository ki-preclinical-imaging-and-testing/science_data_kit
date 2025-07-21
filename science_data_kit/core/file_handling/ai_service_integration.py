"""
AI Service Integration Framework for Science Data Kit

This module provides a framework for integrating AI services with the Science Data Kit,
enabling file interpreters and other components to leverage AI capabilities for
advanced analysis, content extraction, and metadata generation.

The framework includes:
1. Base classes and interfaces for AI service integrations
2. Capability mixins for different AI service types
3. Integration with the existing plugin architecture
4. Standardized error handling and result processing

This framework allows for a more extensible and maintainable AI integration system,
making it easier to add new AI services and use them with different file types.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

from science_data_kit.core.integrations.plugin_architecture import (
    PluginBase, PluginCategory, PluginMetadata, register_plugin
)

# Set up logging
logger = logging.getLogger(__name__)


class AIServiceCapability(Enum):
    """Capabilities that can be provided by AI service plugins."""
    IMAGE_ANALYSIS = "image_analysis"
    TEXT_ANALYSIS = "text_analysis"
    SPEECH_RECOGNITION = "speech_recognition"
    TRANSLATION = "translation"
    CONTENT_SUMMARIZATION = "content_summarization"
    ENTITY_RECOGNITION = "entity_recognition"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    LANGUAGE_DETECTION = "language_detection"
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    OCR = "ocr"
    DOCUMENT_ANALYSIS = "document_analysis"


@dataclass
class AIServiceResult:
    """Base class for AI service results."""
    success: bool
    service_name: str
    error_message: Optional[str] = None
    raw_response: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageAnalysisResult(AIServiceResult):
    """Result from image analysis services."""
    labels: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    colors: List[Dict[str, Any]] = field(default_factory=list)
    safe_search: Optional[Dict[str, Any]] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    crop_hints: List[Dict[str, Any]] = field(default_factory=list)
    web_detection: Optional[Dict[str, Any]] = None


@dataclass
class TextAnalysisResult(AIServiceResult):
    """Result from text analysis services."""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: Optional[Dict[str, Any]] = None
    categories: List[Dict[str, Any]] = field(default_factory=list)
    language: Optional[Dict[str, Any]] = None
    syntax: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SpeechRecognitionResult(AIServiceResult):
    """Result from speech recognition services."""
    transcript: str = ""
    confidence: float = 0.0
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    word_timings: List[Dict[str, Any]] = field(default_factory=list)
    speaker_labels: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TranslationResult(AIServiceResult):
    """Result from translation services."""
    translated_text: str = ""
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    confidence: float = 0.0
    alternatives: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DocumentAnalysisResult(AIServiceResult):
    """Result from document analysis services."""
    text: str = ""
    pages: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    key_value_pairs: List[Dict[str, Any]] = field(default_factory=list)


class AIServicePlugin(PluginBase):
    """
    Base class for AI service integration plugins.

    AI service plugins provide integration with external AI services like
    Google Cloud Vision, Azure Cognitive Services, AWS Rekognition, etc.
    """

    @property
    @abstractmethod
    def service_type(self) -> str:
        """Get the type of AI service (e.g., 'image_analysis', 'text_analysis')."""
        pass

    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with the AI service.

        Args:
            **kwargs: Authentication parameters specific to the service.

        Returns:
            True if authentication was successful, False otherwise.
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the plugin is currently authenticated with the AI service.

        Returns:
            True if authenticated, False otherwise.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AIServiceCapability]:
        """
        Get a list of capabilities provided by this AI service.

        Returns:
            List of AIServiceCapability values.
        """
        pass

    def has_capability(self, capability: AIServiceCapability) -> bool:
        """
        Check if this AI service has a specific capability.

        Args:
            capability: The capability to check for.

        Returns:
            True if the service has the capability, False otherwise.
        """
        return capability in self.get_capabilities()


# Capability Mixins for AI Services

class ImageAnalysisCapability:
    """
    Mixin for AI services that can analyze images.

    This capability allows plugins to analyze images and extract information
    such as labels, objects, faces, and other visual features.
    """

    def analyze_image(self, image_path: str, features: List[str] = None, **kwargs) -> ImageAnalysisResult:
        """
        Analyze an image using the AI service.

        Args:
            image_path: Path to the image file to analyze.
            features: List of specific features to analyze (e.g., 'labels', 'objects', 'faces').
                      If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            ImageAnalysisResult containing the analysis results.
        """
        raise NotImplementedError("Image analysis not implemented")

    def get_supported_image_formats(self) -> List[str]:
        """
        Get a list of image formats supported by this service.

        Returns:
            List of supported image formats (e.g., ['jpeg', 'png', 'gif']).
        """
        return []

    def get_supported_image_features(self) -> List[str]:
        """
        Get a list of image analysis features supported by this service.

        Returns:
            List of supported features (e.g., ['labels', 'objects', 'faces']).
        """
        return []


class TextAnalysisCapability:
    """
    Mixin for AI services that can analyze text.

    This capability allows plugins to analyze text and extract information
    such as entities, sentiment, categories, and other linguistic features.
    """

    def analyze_text(self, text: str, features: List[str] = None, **kwargs) -> TextAnalysisResult:
        """
        Analyze text using the AI service.

        Args:
            text: The text to analyze.
            features: List of specific features to analyze (e.g., 'entities', 'sentiment', 'categories').
                     If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            TextAnalysisResult containing the analysis results.
        """
        raise NotImplementedError("Text analysis not implemented")

    def analyze_text_file(self, file_path: str, features: List[str] = None, **kwargs) -> TextAnalysisResult:
        """
        Analyze text from a file using the AI service.

        Args:
            file_path: Path to the text file to analyze.
            features: List of specific features to analyze.
                     If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            TextAnalysisResult containing the analysis results.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.analyze_text(text, features, **kwargs)
        except Exception as e:
            logger.error(f"Failed to analyze text file {file_path}: {str(e)}")
            return TextAnalysisResult(
                success=False,
                service_name=getattr(self, 'metadata', PluginMetadata('unknown', '0.0', '', '', PluginCategory.OTHER)).name,
                error_message=f"Failed to analyze text file: {str(e)}"
            )

    def get_supported_languages(self) -> List[str]:
        """
        Get a list of languages supported by this service.

        Returns:
            List of supported language codes (e.g., ['en', 'fr', 'de']).
        """
        return []

    def get_supported_text_features(self) -> List[str]:
        """
        Get a list of text analysis features supported by this service.

        Returns:
            List of supported features (e.g., ['entities', 'sentiment', 'categories']).
        """
        return []


class SpeechRecognitionCapability:
    """
    Mixin for AI services that can recognize speech in audio files.

    This capability allows plugins to transcribe speech from audio files
    and extract additional information such as speaker identification.
    """

    def recognize_speech(self, audio_path: str, language: str = 'en-US', **kwargs) -> SpeechRecognitionResult:
        """
        Recognize speech in an audio file using the AI service.

        Args:
            audio_path: Path to the audio file to analyze.
            language: Language code for the speech (default: 'en-US').
            **kwargs: Additional parameters for the recognition.

        Returns:
            SpeechRecognitionResult containing the recognition results.
        """
        raise NotImplementedError("Speech recognition not implemented")

    def get_supported_audio_formats(self) -> List[str]:
        """
        Get a list of audio formats supported by this service.

        Returns:
            List of supported audio formats (e.g., ['mp3', 'wav', 'flac']).
        """
        return []

    def get_supported_speech_languages(self) -> List[str]:
        """
        Get a list of languages supported by this service for speech recognition.

        Returns:
            List of supported language codes (e.g., ['en-US', 'fr-FR', 'de-DE']).
        """
        return []


class TranslationCapability:
    """
    Mixin for AI services that can translate text.

    This capability allows plugins to translate text between different languages.
    """

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None, **kwargs) -> TranslationResult:
        """
        Translate text using the AI service.

        Args:
            text: The text to translate.
            target_language: The language code to translate to.
            source_language: The language code to translate from (if None, auto-detect).
            **kwargs: Additional parameters for the translation.

        Returns:
            TranslationResult containing the translation results.
        """
        raise NotImplementedError("Translation not implemented")

    def translate_text_file(self, file_path: str, target_language: str, source_language: Optional[str] = None, **kwargs) -> TranslationResult:
        """
        Translate text from a file using the AI service.

        Args:
            file_path: Path to the text file to translate.
            target_language: The language code to translate to.
            source_language: The language code to translate from (if None, auto-detect).
            **kwargs: Additional parameters for the translation.

        Returns:
            TranslationResult containing the translation results.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.translate_text(text, target_language, source_language, **kwargs)
        except Exception as e:
            logger.error(f"Failed to translate text file {file_path}: {str(e)}")
            return TranslationResult(
                success=False,
                service_name=getattr(self, 'metadata', PluginMetadata('unknown', '0.0', '', '', PluginCategory.OTHER)).name,
                error_message=f"Failed to translate text file: {str(e)}"
            )

    def get_supported_translation_languages(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of supported source and target languages for translation.

        Returns:
            Dictionary mapping source language codes to lists of target language codes.
        """
        return {}


class DocumentAnalysisCapability:
    """
    Mixin for AI services that can analyze documents.

    This capability allows plugins to analyze documents and extract structured
    information such as text, tables, forms, and key-value pairs.
    """

    def analyze_document(self, document_path: str, features: List[str] = None, **kwargs) -> DocumentAnalysisResult:
        """
        Analyze a document using the AI service.

        Args:
            document_path: Path to the document file to analyze.
            features: List of specific features to analyze (e.g., 'text', 'tables', 'forms').
                     If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            DocumentAnalysisResult containing the analysis results.
        """
        raise NotImplementedError("Document analysis not implemented")

    def get_supported_document_formats(self) -> List[str]:
        """
        Get a list of document formats supported by this service.

        Returns:
            List of supported document formats (e.g., ['pdf', 'docx', 'tiff']).
        """
        return []

    def get_supported_document_features(self) -> List[str]:
        """
        Get a list of document analysis features supported by this service.

        Returns:
            List of supported features (e.g., ['text', 'tables', 'forms']).
        """
        return []


# AI Service Registry Functions

def get_ai_service_for_capability(capability: AIServiceCapability) -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides the specified capability.

    If multiple services provide the capability, returns the one with the highest priority.

    Args:
        capability: The capability to find a service for.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    from science_data_kit.core.integrations.plugin_architecture import plugin_registry, PluginCategory

    # Get all AI service plugins
    plugin_names = plugin_registry.get_plugins_by_category(PluginCategory.OTHER)
    
    # Filter to those with the requested capability
    capable_plugins = []
    for name in plugin_names:
        plugin = plugin_registry.get_plugin_instance(name)
        if (plugin and isinstance(plugin, AIServicePlugin) and 
            plugin.has_capability(capability)):
            metadata = plugin_registry.get_plugin_metadata(name)
            if metadata:
                capable_plugins.append((name, metadata.priority))
    
    # Sort by priority (descending)
    capable_plugins.sort(key=lambda x: x[1], reverse=True)
    
    # Return the highest priority plugin that has the capability
    for name, _ in capable_plugins:
        plugin = plugin_registry.get_plugin_instance(name)
        if plugin:
            return cast(AIServicePlugin, plugin)
    
    logger.warning(f"No AI service found with capability: {capability.value}")
    return None


def get_image_analysis_service() -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides image analysis capabilities.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    return get_ai_service_for_capability(AIServiceCapability.IMAGE_ANALYSIS)


def get_text_analysis_service() -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides text analysis capabilities.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    return get_ai_service_for_capability(AIServiceCapability.TEXT_ANALYSIS)


def get_speech_recognition_service() -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides speech recognition capabilities.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    return get_ai_service_for_capability(AIServiceCapability.SPEECH_RECOGNITION)


def get_translation_service() -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides translation capabilities.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    return get_ai_service_for_capability(AIServiceCapability.TRANSLATION)


def get_document_analysis_service() -> Optional[AIServicePlugin]:
    """
    Get an AI service plugin instance that provides document analysis capabilities.

    Returns:
        An AI service plugin instance, or None if no suitable service is found.
    """
    return get_ai_service_for_capability(AIServiceCapability.DOCUMENT_ANALYSIS)


# Convenience Functions for AI Service Integration

def analyze_image(image_path: str, features: List[str] = None, **kwargs) -> ImageAnalysisResult:
    """
    Analyze an image using the best available AI service.

    Args:
        image_path: Path to the image file to analyze.
        features: List of specific features to analyze.
        **kwargs: Additional parameters for the analysis.

    Returns:
        ImageAnalysisResult containing the analysis results.
    """
    service = get_image_analysis_service()
    if not service or not isinstance(service, ImageAnalysisCapability):
        return ImageAnalysisResult(
            success=False,
            service_name="none",
            error_message="No image analysis service available"
        )
    
    try:
        return service.analyze_image(image_path, features, **kwargs)
    except Exception as e:
        logger.error(f"Error analyzing image {image_path}: {str(e)}")
        return ImageAnalysisResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error analyzing image: {str(e)}"
        )


def analyze_text(text: str, features: List[str] = None, **kwargs) -> TextAnalysisResult:
    """
    Analyze text using the best available AI service.

    Args:
        text: The text to analyze.
        features: List of specific features to analyze.
        **kwargs: Additional parameters for the analysis.

    Returns:
        TextAnalysisResult containing the analysis results.
    """
    service = get_text_analysis_service()
    if not service or not isinstance(service, TextAnalysisCapability):
        return TextAnalysisResult(
            success=False,
            service_name="none",
            error_message="No text analysis service available"
        )
    
    try:
        return service.analyze_text(text, features, **kwargs)
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return TextAnalysisResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error analyzing text: {str(e)}"
        )


def analyze_text_file(file_path: str, features: List[str] = None, **kwargs) -> TextAnalysisResult:
    """
    Analyze text from a file using the best available AI service.

    Args:
        file_path: Path to the text file to analyze.
        features: List of specific features to analyze.
        **kwargs: Additional parameters for the analysis.

    Returns:
        TextAnalysisResult containing the analysis results.
    """
    service = get_text_analysis_service()
    if not service or not isinstance(service, TextAnalysisCapability):
        return TextAnalysisResult(
            success=False,
            service_name="none",
            error_message="No text analysis service available"
        )
    
    try:
        return service.analyze_text_file(file_path, features, **kwargs)
    except Exception as e:
        logger.error(f"Error analyzing text file {file_path}: {str(e)}")
        return TextAnalysisResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error analyzing text file: {str(e)}"
        )


def recognize_speech(audio_path: str, language: str = 'en-US', **kwargs) -> SpeechRecognitionResult:
    """
    Recognize speech in an audio file using the best available AI service.

    Args:
        audio_path: Path to the audio file to analyze.
        language: Language code for the speech (default: 'en-US').
        **kwargs: Additional parameters for the recognition.

    Returns:
        SpeechRecognitionResult containing the recognition results.
    """
    service = get_speech_recognition_service()
    if not service or not isinstance(service, SpeechRecognitionCapability):
        return SpeechRecognitionResult(
            success=False,
            service_name="none",
            error_message="No speech recognition service available"
        )
    
    try:
        return service.recognize_speech(audio_path, language, **kwargs)
    except Exception as e:
        logger.error(f"Error recognizing speech in {audio_path}: {str(e)}")
        return SpeechRecognitionResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error recognizing speech: {str(e)}"
        )


def translate_text(text: str, target_language: str, source_language: Optional[str] = None, **kwargs) -> TranslationResult:
    """
    Translate text using the best available AI service.

    Args:
        text: The text to translate.
        target_language: The language code to translate to.
        source_language: The language code to translate from (if None, auto-detect).
        **kwargs: Additional parameters for the translation.

    Returns:
        TranslationResult containing the translation results.
    """
    service = get_translation_service()
    if not service or not isinstance(service, TranslationCapability):
        return TranslationResult(
            success=False,
            service_name="none",
            error_message="No translation service available"
        )
    
    try:
        return service.translate_text(text, target_language, source_language, **kwargs)
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        return TranslationResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error translating text: {str(e)}"
        )


def analyze_document(document_path: str, features: List[str] = None, **kwargs) -> DocumentAnalysisResult:
    """
    Analyze a document using the best available AI service.

    Args:
        document_path: Path to the document file to analyze.
        features: List of specific features to analyze.
        **kwargs: Additional parameters for the analysis.

    Returns:
        DocumentAnalysisResult containing the analysis results.
    """
    service = get_document_analysis_service()
    if not service or not isinstance(service, DocumentAnalysisCapability):
        return DocumentAnalysisResult(
            success=False,
            service_name="none",
            error_message="No document analysis service available"
        )
    
    try:
        return service.analyze_document(document_path, features, **kwargs)
    except Exception as e:
        logger.error(f"Error analyzing document {document_path}: {str(e)}")
        return DocumentAnalysisResult(
            success=False,
            service_name=service.metadata.name,
            error_message=f"Error analyzing document: {str(e)}"
        )
"""