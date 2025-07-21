"""
Tests for the AI Service Integration Framework

This module contains tests for the AI service integration framework, including
base classes, capability mixins, and utility functions.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, AIServicePlugin, AIServiceResult,
    ImageAnalysisCapability, TextAnalysisCapability, SpeechRecognitionCapability,
    TranslationCapability, DocumentAnalysisCapability,
    ImageAnalysisResult, TextAnalysisResult, SpeechRecognitionResult,
    TranslationResult, DocumentAnalysisResult,
    get_ai_service_for_capability, get_image_analysis_service, get_text_analysis_service,
    get_speech_recognition_service, get_translation_service, get_document_analysis_service,
    analyze_image, analyze_text, analyze_text_file, recognize_speech, translate_text, analyze_document
)
from science_data_kit.core.integrations.plugin_architecture import (
    PluginCategory, PluginMetadata
)


class TestAIServiceResult(unittest.TestCase):
    """Tests for the AIServiceResult class and its subclasses."""

    def test_ai_service_result_init(self):
        """Test initialization of AIServiceResult."""
        result = AIServiceResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.raw_response)
        self.assertEqual(result.metadata, {})

    def test_image_analysis_result_init(self):
        """Test initialization of ImageAnalysisResult."""
        result = ImageAnalysisResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertEqual(result.labels, [])
        self.assertEqual(result.objects, [])
        self.assertEqual(result.faces, [])
        self.assertEqual(result.colors, [])
        self.assertIsNone(result.safe_search)
        self.assertEqual(result.properties, {})
        self.assertEqual(result.crop_hints, [])
        self.assertIsNone(result.web_detection)

    def test_text_analysis_result_init(self):
        """Test initialization of TextAnalysisResult."""
        result = TextAnalysisResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertEqual(result.entities, [])
        self.assertIsNone(result.sentiment)
        self.assertEqual(result.categories, [])
        self.assertIsNone(result.language)
        self.assertIsNone(result.syntax)
        self.assertIsNone(result.summary)
        self.assertEqual(result.keywords, [])

    def test_speech_recognition_result_init(self):
        """Test initialization of SpeechRecognitionResult."""
        result = SpeechRecognitionResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertEqual(result.transcript, "")
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.alternatives, [])
        self.assertEqual(result.word_timings, [])
        self.assertEqual(result.speaker_labels, [])

    def test_translation_result_init(self):
        """Test initialization of TranslationResult."""
        result = TranslationResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertEqual(result.translated_text, "")
        self.assertIsNone(result.source_language)
        self.assertIsNone(result.target_language)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.alternatives, [])

    def test_document_analysis_result_init(self):
        """Test initialization of DocumentAnalysisResult."""
        result = DocumentAnalysisResult(success=True, service_name="test_service")
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, "test_service")
        self.assertEqual(result.text, "")
        self.assertEqual(result.pages, [])
        self.assertEqual(result.tables, [])
        self.assertEqual(result.forms, [])
        self.assertEqual(result.entities, [])
        self.assertEqual(result.key_value_pairs, [])


class MockAIServicePlugin(AIServicePlugin):
    """Mock AI service plugin for testing."""

    def __init__(self, service_type="test", capabilities=None):
        self._service_type = service_type
        self._capabilities = capabilities or []
        self._authenticated = False

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_service",
            version="1.0.0",
            description="Mock AI service for testing",
            author="Test",
            category=PluginCategory.OTHER,
            capabilities=[cap.value for cap in self._capabilities],
            priority=5
        )

    @property
    def service_type(self) -> str:
        return self._service_type

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def authenticate(self, **kwargs) -> bool:
        self._authenticated = True
        return True

    def is_authenticated(self) -> bool:
        return self._authenticated

    def get_capabilities(self) -> list:
        return self._capabilities


class MockImageAnalysisService(MockAIServicePlugin, ImageAnalysisCapability):
    """Mock image analysis service for testing."""

    def __init__(self):
        super().__init__(
            service_type="image_analysis",
            capabilities=[AIServiceCapability.IMAGE_ANALYSIS]
        )

    def analyze_image(self, image_path, features=None, **kwargs):
        return ImageAnalysisResult(
            success=True,
            service_name=self.metadata.name,
            labels=[{"description": "test", "score": 0.9}]
        )

    def get_supported_image_formats(self):
        return ["jpeg", "png"]

    def get_supported_image_features(self):
        return ["labels", "objects"]


class MockTextAnalysisService(MockAIServicePlugin, TextAnalysisCapability):
    """Mock text analysis service for testing."""

    def __init__(self):
        super().__init__(
            service_type="text_analysis",
            capabilities=[AIServiceCapability.TEXT_ANALYSIS]
        )

    def analyze_text(self, text, features=None, **kwargs):
        return TextAnalysisResult(
            success=True,
            service_name=self.metadata.name,
            entities=[{"name": "test", "type": "PERSON", "salience": 0.9}]
        )

    def get_supported_languages(self):
        return ["en", "fr"]

    def get_supported_text_features(self):
        return ["entities", "sentiment"]


class TestAIServicePlugin(unittest.TestCase):
    """Tests for the AIServicePlugin base class."""

    def test_has_capability(self):
        """Test the has_capability method."""
        service = MockAIServicePlugin(
            capabilities=[AIServiceCapability.IMAGE_ANALYSIS, AIServiceCapability.TEXT_ANALYSIS]
        )
        self.assertTrue(service.has_capability(AIServiceCapability.IMAGE_ANALYSIS))
        self.assertTrue(service.has_capability(AIServiceCapability.TEXT_ANALYSIS))
        self.assertFalse(service.has_capability(AIServiceCapability.SPEECH_RECOGNITION))


class TestImageAnalysisCapability(unittest.TestCase):
    """Tests for the ImageAnalysisCapability mixin."""

    def test_analyze_image_not_implemented(self):
        """Test that analyze_image raises NotImplementedError by default."""
        class TestService(MockAIServicePlugin, ImageAnalysisCapability):
            pass

        service = TestService()
        with self.assertRaises(NotImplementedError):
            service.analyze_image("test.jpg")

    def test_get_supported_image_formats_default(self):
        """Test that get_supported_image_formats returns an empty list by default."""
        class TestService(MockAIServicePlugin, ImageAnalysisCapability):
            pass

        service = TestService()
        self.assertEqual(service.get_supported_image_formats(), [])

    def test_get_supported_image_features_default(self):
        """Test that get_supported_image_features returns an empty list by default."""
        class TestService(MockAIServicePlugin, ImageAnalysisCapability):
            pass

        service = TestService()
        self.assertEqual(service.get_supported_image_features(), [])


class TestTextAnalysisCapability(unittest.TestCase):
    """Tests for the TextAnalysisCapability mixin."""

    def test_analyze_text_not_implemented(self):
        """Test that analyze_text raises NotImplementedError by default."""
        class TestService(MockAIServicePlugin, TextAnalysisCapability):
            pass

        service = TestService()
        with self.assertRaises(NotImplementedError):
            service.analyze_text("test text")

    def test_analyze_text_file(self):
        """Test analyze_text_file method."""
        class TestService(MockAIServicePlugin, TextAnalysisCapability):
            def analyze_text(self, text, features=None, **kwargs):
                return TextAnalysisResult(
                    success=True,
                    service_name=self.metadata.name,
                    entities=[{"name": text, "type": "TEST"}]
                )

        service = TestService()
        
        # Create a temporary test file
        test_file = "test_text_file.txt"
        test_content = "This is a test file."
        try:
            with open(test_file, "w") as f:
                f.write(test_content)
            
            result = service.analyze_text_file(test_file)
            self.assertTrue(result.success)
            self.assertEqual(result.entities[0]["name"], test_content)
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_analyze_text_file_error(self):
        """Test analyze_text_file method with a non-existent file."""
        class TestService(MockAIServicePlugin, TextAnalysisCapability):
            def analyze_text(self, text, features=None, **kwargs):
                return TextAnalysisResult(
                    success=True,
                    service_name=self.metadata.name
                )

        service = TestService()
        result = service.analyze_text_file("non_existent_file.txt")
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

    def test_get_supported_languages_default(self):
        """Test that get_supported_languages returns an empty list by default."""
        class TestService(MockAIServicePlugin, TextAnalysisCapability):
            pass

        service = TestService()
        self.assertEqual(service.get_supported_languages(), [])

    def test_get_supported_text_features_default(self):
        """Test that get_supported_text_features returns an empty list by default."""
        class TestService(MockAIServicePlugin, TextAnalysisCapability):
            pass

        service = TestService()
        self.assertEqual(service.get_supported_text_features(), [])


class TestAIServiceRegistryFunctions(unittest.TestCase):
    """Tests for the AI service registry functions."""

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_ai_service_for_capability')
    def test_get_image_analysis_service(self, mock_get_service):
        """Test get_image_analysis_service function."""
        mock_service = MockImageAnalysisService()
        mock_get_service.return_value = mock_service
        
        service = get_image_analysis_service()
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with(AIServiceCapability.IMAGE_ANALYSIS)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_ai_service_for_capability')
    def test_get_text_analysis_service(self, mock_get_service):
        """Test get_text_analysis_service function."""
        mock_service = MockTextAnalysisService()
        mock_get_service.return_value = mock_service
        
        service = get_text_analysis_service()
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with(AIServiceCapability.TEXT_ANALYSIS)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_ai_service_for_capability')
    def test_get_speech_recognition_service(self, mock_get_service):
        """Test get_speech_recognition_service function."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        service = get_speech_recognition_service()
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with(AIServiceCapability.SPEECH_RECOGNITION)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_ai_service_for_capability')
    def test_get_translation_service(self, mock_get_service):
        """Test get_translation_service function."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        service = get_translation_service()
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with(AIServiceCapability.TRANSLATION)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_ai_service_for_capability')
    def test_get_document_analysis_service(self, mock_get_service):
        """Test get_document_analysis_service function."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        service = get_document_analysis_service()
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with(AIServiceCapability.DOCUMENT_ANALYSIS)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for the convenience functions."""

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_image_analysis_service')
    def test_analyze_image(self, mock_get_service):
        """Test analyze_image function."""
        # Test with a valid service
        mock_service = MockImageAnalysisService()
        mock_get_service.return_value = mock_service
        
        result = analyze_image("test.jpg", ["labels"])
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, mock_service.metadata.name)
        self.assertEqual(result.labels, [{"description": "test", "score": 0.9}])
        
        # Test with no service available
        mock_get_service.return_value = None
        result = analyze_image("test.jpg")
        self.assertFalse(result.success)
        self.assertEqual(result.service_name, "none")
        self.assertIn("No image analysis service available", result.error_message)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_text_analysis_service')
    def test_analyze_text(self, mock_get_service):
        """Test analyze_text function."""
        # Test with a valid service
        mock_service = MockTextAnalysisService()
        mock_get_service.return_value = mock_service
        
        result = analyze_text("test text", ["entities"])
        self.assertTrue(result.success)
        self.assertEqual(result.service_name, mock_service.metadata.name)
        self.assertEqual(result.entities, [{"name": "test", "type": "PERSON", "salience": 0.9}])
        
        # Test with no service available
        mock_get_service.return_value = None
        result = analyze_text("test text")
        self.assertFalse(result.success)
        self.assertEqual(result.service_name, "none")
        self.assertIn("No text analysis service available", result.error_message)

    @patch('science_data_kit.core.file_handling.ai_service_integration.get_text_analysis_service')
    def test_analyze_text_file(self, mock_get_service):
        """Test analyze_text_file function."""
        # Test with a valid service
        mock_service = MockTextAnalysisService()
        mock_get_service.return_value = mock_service
        
        # Create a temporary test file
        test_file = "test_text_file.txt"
        try:
            with open(test_file, "w") as f:
                f.write("This is a test file.")
            
            result = analyze_text_file(test_file, ["entities"])
            self.assertTrue(result.success)
            self.assertEqual(result.service_name, mock_service.metadata.name)
            self.assertEqual(result.entities, [{"name": "test", "type": "PERSON", "salience": 0.9}])
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
        
        # Test with no service available
        mock_get_service.return_value = None
        result = analyze_text_file("test_file.txt")
        self.assertFalse(result.success)
        self.assertEqual(result.service_name, "none")
        self.assertIn("No text analysis service available", result.error_message)


if __name__ == '__main__':
    unittest.main()
"""