"""
Tests for the Google Cloud Translation AI Service Integration for Science Data Kit.

This module contains unit tests for the Google Translation service implementation,
including authentication, text translation, language detection, and error handling.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from science_data_kit.core.file_handling.google_translate_service import (
    GoogleTranslateService, GOOGLE_TRANSLATE_AVAILABLE
)
from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, TranslationResult
)


@unittest.skipIf(not GOOGLE_TRANSLATE_AVAILABLE, "Google Cloud Translation API not available")
class TestGoogleTranslateService(unittest.TestCase):
    """Tests for the Google Cloud Translation service."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock credentials file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.credentials_file = self.test_dir / "credentials.json"
        
        # Write dummy credentials to file
        with open(self.credentials_file, 'w') as f:
            f.write('{"type": "service_account", "project_id": "test-project"}')
        
        # Create test text file
        self.text_file = self.test_dir / "test_text.txt"
        with open(self.text_file, 'w') as f:
            f.write("This is a test text for translation.")
        
        # Create service instance
        self.service = GoogleTranslateService()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate(self, mock_credentials, mock_translate_client):
        """Test authentication with Google Cloud Translation API."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock get_languages method
        mock_client.get_languages.return_value = [
            {'language': 'en'},
            {'language': 'fr'},
            {'language': 'de'}
        ]
        
        # Test authentication with credentials file
        result = self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Check that authentication was successful
        self.assertTrue(result)
        self.assertTrue(self.service.is_authenticated())
        
        # Check that credentials were created correctly
        mock_credentials.assert_called_once_with(str(self.credentials_file))
        
        # Check that client was created correctly
        mock_translate_client.assert_called_once()
        
        # Check that supported languages were loaded
        mock_client.get_languages.assert_called_once()
        self.assertIn('en', self.service._supported_languages)

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate_with_env_var(self, mock_credentials, mock_translate_client):
        """Test authentication with environment variable."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock get_languages method
        mock_client.get_languages.return_value = [
            {'language': 'en'},
            {'language': 'fr'},
            {'language': 'de'}
        ]
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(self.credentials_file)
        
        # Test authentication without credentials file
        result = self.service.authenticate()
        
        # Check that authentication was successful
        self.assertTrue(result)
        self.assertTrue(self.service.is_authenticated())
        
        # Check that credentials were created correctly
        mock_credentials.assert_called_once_with(str(self.credentials_file))
        
        # Check that client was created correctly
        mock_translate_client.assert_called_once()
        
        # Clean up environment variable
        del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate_failure(self, mock_credentials, mock_translate_client):
        """Test authentication failure."""
        # Set up mocks to raise exception
        mock_credentials.side_effect = Exception("Authentication failed")
        
        # Test authentication with invalid credentials
        result = self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Check that authentication failed
        self.assertFalse(result)
        self.assertFalse(self.service.is_authenticated())

    def test_get_capabilities(self):
        """Test getting capabilities."""
        capabilities = self.service.get_capabilities()
        
        # Check that the service has the translation and language detection capabilities
        self.assertIn(AIServiceCapability.TRANSLATION, capabilities)
        self.assertIn(AIServiceCapability.LANGUAGE_DETECTION, capabilities)
        self.assertEqual(len(capabilities), 2)

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_get_supported_translation_languages(self, mock_credentials, mock_translate_client):
        """Test getting supported translation languages."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock get_languages method
        mock_client.get_languages.return_value = [
            {'language': 'en'},
            {'language': 'fr'},
            {'language': 'de'}
        ]
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test getting supported languages
        languages = self.service.get_supported_translation_languages()
        
        # Check that languages were loaded correctly
        self.assertIn('en', languages)
        self.assertIn('fr', languages)
        self.assertIn('de', languages)
        
        # Check that each language can be translated to all other languages
        self.assertIn('fr', languages['en'])
        self.assertIn('de', languages['en'])
        self.assertIn('en', languages['fr'])
        self.assertIn('de', languages['fr'])
        self.assertIn('en', languages['de'])
        self.assertIn('fr', languages['de'])

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text(self, mock_credentials, mock_translate_client):
        """Test translating text."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock translate method
        mock_client.translate.return_value = {
            'translatedText': 'Ceci est un test de traduction.',
            'detectedSourceLanguage': 'en',
            'input': 'This is a test for translation.'
        }
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text
        result = self.service.translate_text(
            text="This is a test for translation.",
            target_language="fr"
        )
        
        # Check that translation was successful
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "Ceci est un test de traduction.")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "fr")
        self.assertEqual(result.confidence, 1.0)  # Google Translate doesn't provide confidence scores
        
        # Check that the client was called correctly
        mock_client.translate.assert_called_once_with(
            "This is a test for translation.",
            target_language="fr",
            source_language=None,
            format_="text",
            model="nmt"
        )

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text_with_source_language(self, mock_credentials, mock_translate_client):
        """Test translating text with specified source language."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock translate method
        mock_client.translate.return_value = {
            'translatedText': 'Ceci est un test de traduction.',
            'input': 'This is a test for translation.'
        }
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text with source language
        result = self.service.translate_text(
            text="This is a test for translation.",
            target_language="fr",
            source_language="en"
        )
        
        # Check that translation was successful
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "Ceci est un test de traduction.")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "fr")
        
        # Check that the client was called correctly with source language
        mock_client.translate.assert_called_once_with(
            "This is a test for translation.",
            target_language="fr",
            source_language="en",
            format_="text",
            model="nmt"
        )

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text_file(self, mock_credentials, mock_translate_client):
        """Test translating text from a file."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock translate method
        mock_client.translate.return_value = {
            'translatedText': 'Ceci est un test de texte pour la traduction.',
            'detectedSourceLanguage': 'en',
            'input': 'This is a test text for translation.'
        }
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text from file
        result = self.service.translate_text_file(
            file_path=str(self.text_file),
            target_language="fr"
        )
        
        # Check that translation was successful
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "Ceci est un test de texte pour la traduction.")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "fr")
        
        # Check that the client was called correctly
        mock_client.translate.assert_called_once()

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text_with_format_and_model(self, mock_credentials, mock_translate_client):
        """Test translating text with format and model parameters."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock translate method
        mock_client.translate.return_value = {
            'translatedText': '<p>Ceci est un test de <strong>traduction</strong>.</p>',
            'detectedSourceLanguage': 'en',
            'input': '<p>This is a test for <strong>translation</strong>.</p>'
        }
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text with format and model
        result = self.service.translate_text(
            text="<p>This is a test for <strong>translation</strong>.</p>",
            target_language="fr",
            format="html",
            model="base"
        )
        
        # Check that translation was successful
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "<p>Ceci est un test de <strong>traduction</strong>.</p>")
        
        # Check that the client was called correctly with format and model
        mock_client.translate.assert_called_once_with(
            "<p>This is a test for <strong>translation</strong>.</p>",
            target_language="fr",
            source_language=None,
            format_="html",
            model="base"
        )

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text_multiple_results(self, mock_credentials, mock_translate_client):
        """Test translating text with multiple results."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock translate method to return a list of results
        mock_client.translate.return_value = [
            {
                'translatedText': 'Ceci est un test.',
                'detectedSourceLanguage': 'en',
                'input': 'This is a test.'
            },
            {
                'translatedText': 'Ceci est un autre test.',
                'detectedSourceLanguage': 'en',
                'input': 'This is another test.'
            }
        ]
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text with multiple results
        result = self.service.translate_text(
            text=["This is a test.", "This is another test."],
            target_language="fr"
        )
        
        # Check that translation was successful
        self.assertTrue(result.success)
        self.assertEqual(result.translated_text, "Ceci est un test.")  # First result
        self.assertEqual(len(result.alternatives), 2)
        self.assertEqual(result.alternatives[0]['translated_text'], "Ceci est un test.")
        self.assertEqual(result.alternatives[1]['translated_text'], "Ceci est un autre test.")

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_translate_text_error(self, mock_credentials, mock_translate_client):
        """Test error handling in text translation."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock client to raise exception
        mock_client.translate.side_effect = Exception("Translation failed")
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test translating text with error
        result = self.service.translate_text(
            text="This is a test for translation.",
            target_language="fr"
        )
        
        # Check that translation failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Translation failed", result.error_message)

    def test_translate_text_not_authenticated(self):
        """Test translating text without authentication."""
        # Test translating text without authentication
        result = self.service.translate_text(
            text="This is a test for translation.",
            target_language="fr"
        )
        
        # Check that translation failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Not authenticated", result.error_message)

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_detect_language(self, mock_credentials, mock_translate_client):
        """Test detecting language."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock detect_language method
        mock_client.detect_language.return_value = {
            'language': 'en',
            'confidence': 0.98
        }
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test detecting language
        result = self.service.detect_language(
            text="This is a test for language detection."
        )
        
        # Check that detection was successful
        self.assertTrue(result['success'])
        self.assertEqual(result['language'], "en")
        self.assertEqual(result['confidence'], 0.98)
        
        # Check that the client was called correctly
        mock_client.detect_language.assert_called_once_with(
            "This is a test for language detection."
        )

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_detect_language_multiple_results(self, mock_credentials, mock_translate_client):
        """Test detecting language with multiple results."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock detect_language method to return a list of results
        mock_client.detect_language.return_value = [
            {
                'language': 'en',
                'confidence': 0.98
            },
            {
                'language': 'fr',
                'confidence': 0.02
            }
        ]
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test detecting language with multiple results
        result = self.service.detect_language(
            text="This is a test for language detection."
        )
        
        # Check that detection was successful
        self.assertTrue(result['success'])
        self.assertEqual(result['language'], "en")  # First result
        self.assertEqual(result['confidence'], 0.98)
        self.assertEqual(len(result['alternatives']), 2)
        self.assertEqual(result['alternatives'][0]['language'], "en")
        self.assertEqual(result['alternatives'][1]['language'], "fr")

    @patch('google.cloud.translate_v2.Client')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_detect_language_error(self, mock_credentials, mock_translate_client):
        """Test error handling in language detection."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_translate_client.return_value = mock_client
        
        # Mock client to raise exception
        mock_client.detect_language.side_effect = Exception("Detection failed")
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test detecting language with error
        result = self.service.detect_language(
            text="This is a test for language detection."
        )
        
        # Check that detection failed
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error_message'])
        self.assertIn("Detection failed", result['error_message'])

    def test_detect_language_not_authenticated(self):
        """Test detecting language without authentication."""
        # Test detecting language without authentication
        result = self.service.detect_language(
            text="This is a test for language detection."
        )
        
        # Check that detection failed
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error_message'])
        self.assertIn("Not authenticated", result['error_message'])


if __name__ == '__main__':
    unittest.main()
"""