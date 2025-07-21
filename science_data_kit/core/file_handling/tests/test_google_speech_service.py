"""
Tests for the Google Cloud Speech-to-Text AI Service Integration for Science Data Kit.

This module contains unit tests for the Google Speech-to-Text service implementation,
including authentication, speech recognition, and error handling.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from science_data_kit.core.file_handling.google_speech_service import (
    GoogleSpeechService, GOOGLE_SPEECH_AVAILABLE
)
from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, SpeechRecognitionResult
)


@unittest.skipIf(not GOOGLE_SPEECH_AVAILABLE, "Google Cloud Speech-to-Text API not available")
class TestGoogleSpeechService(unittest.TestCase):
    """Tests for the Google Cloud Speech-to-Text service."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock credentials file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.credentials_file = self.test_dir / "credentials.json"
        
        # Write dummy credentials to file
        with open(self.credentials_file, 'w') as f:
            f.write('{"type": "service_account", "project_id": "test-project"}')
        
        # Create test audio file
        self.audio_file = self.test_dir / "test_audio.wav"
        with open(self.audio_file, 'wb') as f:
            # Write a minimal WAV file header
            f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        
        # Create service instance
        self.service = GoogleSpeechService()

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate(self, mock_credentials, mock_speech_client):
        """Test authentication with Google Cloud Speech-to-Text API."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_speech_client.return_value = MagicMock()
        
        # Test authentication with credentials file
        result = self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Check that authentication was successful
        self.assertTrue(result)
        self.assertTrue(self.service.is_authenticated())
        
        # Check that credentials were created correctly
        mock_credentials.assert_called_once_with(str(self.credentials_file))
        
        # Check that client was created correctly
        mock_speech_client.assert_called_once()

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate_with_env_var(self, mock_credentials, mock_speech_client):
        """Test authentication with environment variable."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_speech_client.return_value = MagicMock()
        
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
        mock_speech_client.assert_called_once()
        
        # Clean up environment variable
        del os.environ['GOOGLE_APPLICATION_CREDENTIALS']

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_authenticate_failure(self, mock_credentials, mock_speech_client):
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
        
        # Check that the service has the speech recognition capability
        self.assertIn(AIServiceCapability.SPEECH_RECOGNITION, capabilities)
        self.assertEqual(len(capabilities), 1)

    def test_get_supported_audio_formats(self):
        """Test getting supported audio formats."""
        formats = self.service.get_supported_audio_formats()
        
        # Check that common audio formats are supported
        self.assertIn('wav', formats)
        self.assertIn('mp3', formats)
        self.assertIn('flac', formats)

    def test_get_supported_speech_languages(self):
        """Test getting supported speech languages."""
        languages = self.service.get_supported_speech_languages()
        
        # Check that common languages are supported
        self.assertIn('en-US', languages)
        self.assertIn('fr-FR', languages)
        self.assertIn('de-DE', languages)

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_recognize_speech(self, mock_credentials, mock_speech_client):
        """Test recognizing speech."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_speech_client.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_alternative = MagicMock()
        mock_alternative.transcript = "This is a test transcript."
        mock_alternative.confidence = 0.95
        mock_result.alternatives = [mock_alternative]
        mock_response.results = [mock_result]
        mock_client.recognize.return_value = mock_response
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test recognizing speech
        result = self.service.recognize_speech(
            audio_path=str(self.audio_file),
            language='en-US'
        )
        
        # Check that recognition was successful
        self.assertTrue(result.success)
        self.assertEqual(result.transcript, "This is a test transcript.")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(len(result.alternatives), 1)
        self.assertEqual(result.alternatives[0]['transcript'], "This is a test transcript.")
        self.assertEqual(result.alternatives[0]['confidence'], 0.95)
        
        # Check that the client was called correctly
        mock_client.recognize.assert_called_once()

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_recognize_speech_with_word_timings(self, mock_credentials, mock_speech_client):
        """Test recognizing speech with word timings."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_speech_client.return_value = mock_client
        
        # Mock response with word timings
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_alternative = MagicMock()
        mock_alternative.transcript = "This is a test transcript."
        mock_alternative.confidence = 0.95
        
        # Create mock words with timing information
        mock_word1 = MagicMock()
        mock_word1.word = "This"
        mock_word1.start_time.total_seconds.return_value = 0.0
        mock_word1.end_time.total_seconds.return_value = 0.5
        
        mock_word2 = MagicMock()
        mock_word2.word = "is"
        mock_word2.start_time.total_seconds.return_value = 0.5
        mock_word2.end_time.total_seconds.return_value = 0.7
        
        mock_alternative.words = [mock_word1, mock_word2]
        mock_result.alternatives = [mock_alternative]
        mock_response.results = [mock_result]
        mock_client.recognize.return_value = mock_response
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test recognizing speech with word timings
        result = self.service.recognize_speech(
            audio_path=str(self.audio_file),
            language='en-US',
            enable_word_time_offsets=True
        )
        
        # Check that recognition was successful
        self.assertTrue(result.success)
        self.assertEqual(result.transcript, "This is a test transcript.")
        self.assertEqual(result.confidence, 0.95)
        
        # Check word timings
        self.assertEqual(len(result.word_timings), 2)
        self.assertEqual(result.word_timings[0]['word'], "This")
        self.assertEqual(result.word_timings[0]['start_time'], 0.0)
        self.assertEqual(result.word_timings[0]['end_time'], 0.5)
        self.assertEqual(result.word_timings[1]['word'], "is")
        self.assertEqual(result.word_timings[1]['start_time'], 0.5)
        self.assertEqual(result.word_timings[1]['end_time'], 0.7)
        
        # Check that the client was called correctly with word time offsets enabled
        config = mock_client.recognize.call_args[1]['config']
        self.assertTrue(config.enable_word_time_offsets)

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_recognize_speech_with_speaker_diarization(self, mock_credentials, mock_speech_client):
        """Test recognizing speech with speaker diarization."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_speech_client.return_value = mock_client
        
        # Mock response with speaker diarization
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_alternative = MagicMock()
        mock_alternative.transcript = "This is a test transcript."
        mock_alternative.confidence = 0.95
        
        # Create mock words with speaker tags
        mock_word1 = MagicMock()
        mock_word1.word = "This"
        mock_word1.speaker_tag = 1
        
        mock_word2 = MagicMock()
        mock_word2.word = "is"
        mock_word2.speaker_tag = 2
        
        mock_alternative.words = [mock_word1, mock_word2]
        mock_result.alternatives = [mock_alternative]
        mock_response.results = [mock_result]
        mock_client.recognize.return_value = mock_response
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test recognizing speech with speaker diarization
        result = self.service.recognize_speech(
            audio_path=str(self.audio_file),
            language='en-US',
            enable_speaker_diarization=True,
            diarization_speaker_count=2
        )
        
        # Check that recognition was successful
        self.assertTrue(result.success)
        self.assertEqual(result.transcript, "This is a test transcript.")
        self.assertEqual(result.confidence, 0.95)
        
        # Check speaker labels
        self.assertEqual(len(result.speaker_labels), 2)
        self.assertEqual(result.speaker_labels[0]['word'], "This")
        self.assertEqual(result.speaker_labels[0]['speaker_tag'], 1)
        self.assertEqual(result.speaker_labels[1]['word'], "is")
        self.assertEqual(result.speaker_labels[1]['speaker_tag'], 2)
        
        # Check that the client was called correctly with speaker diarization enabled
        config = mock_client.recognize.call_args[1]['config']
        self.assertTrue(hasattr(config, 'diarization_config'))
        self.assertTrue(config.diarization_config.enable_speaker_diarization)
        self.assertEqual(config.diarization_config.max_speaker_count, 2)

    @patch('google.cloud.speech.SpeechClient')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_recognize_speech_error(self, mock_credentials, mock_speech_client):
        """Test error handling in speech recognition."""
        # Set up mocks
        mock_credentials.return_value = MagicMock()
        mock_client = MagicMock()
        mock_speech_client.return_value = mock_client
        
        # Mock client to raise exception
        mock_client.recognize.side_effect = Exception("Recognition failed")
        
        # Authenticate
        self.service.authenticate(credentials_path=str(self.credentials_file))
        
        # Test recognizing speech with error
        result = self.service.recognize_speech(
            audio_path=str(self.audio_file),
            language='en-US'
        )
        
        # Check that recognition failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Recognition failed", result.error_message)

    def test_recognize_speech_not_authenticated(self):
        """Test recognizing speech without authentication."""
        # Test recognizing speech without authentication
        result = self.service.recognize_speech(
            audio_path=str(self.audio_file),
            language='en-US'
        )
        
        # Check that recognition failed
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Not authenticated", result.error_message)


if __name__ == '__main__':
    unittest.main()
"""