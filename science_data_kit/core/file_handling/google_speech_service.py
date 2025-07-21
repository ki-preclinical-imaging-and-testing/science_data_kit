"""
Google Cloud Speech-to-Text AI Service Integration for Science Data Kit

This module provides integration with Google Cloud Speech-to-Text API for speech recognition,
enabling advanced audio processing capabilities within the Science Data Kit.

The module includes:
1. A plugin implementation for Google Cloud Speech-to-Text API
2. Speech recognition capabilities using Speech-to-Text API features
3. Utility functions for working with Speech-to-Text API results

This integration allows researchers to transcribe speech from audio files using Google's powerful
speech recognition capabilities directly within the Science Data Kit.
"""

import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

try:
    from google.cloud import speech
    from google.oauth2 import service_account
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, AIServicePlugin, SpeechRecognitionCapability,
    SpeechRecognitionResult
)
from science_data_kit.core.integrations.plugin_architecture import (
    PluginCategory, PluginMetadata, register_plugin
)

# Set up logging
logger = logging.getLogger(__name__)


@register_plugin
class GoogleSpeechService(AIServicePlugin, SpeechRecognitionCapability):
    """
    Google Cloud Speech-to-Text API integration for speech recognition.

    This plugin provides integration with Google Cloud Speech-to-Text API for speech recognition,
    enabling advanced audio processing capabilities such as transcription, speaker diarization,
    and word-level timestamps.
    """

    def __init__(self):
        """Initialize the Google Speech-to-Text service plugin."""
        self._client = None
        self._credentials_path = None
        self._authenticated = False

    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="google_speech",
            version="1.0.0",
            description="Google Cloud Speech-to-Text API integration for speech recognition",
            author="Science Data Kit Team",
            category=PluginCategory.OTHER,
            dependencies=[],
            website="https://cloud.google.com/speech-to-text",
            tags=["ai", "audio", "speech", "recognition", "transcription", "google"],
            enabled=GOOGLE_SPEECH_AVAILABLE,
            capabilities=[
                AIServiceCapability.SPEECH_RECOGNITION.value
            ],
            priority=10  # High priority
        )

    @property
    def service_type(self) -> str:
        """Get the type of AI service."""
        return "speech_recognition"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if not GOOGLE_SPEECH_AVAILABLE:
            logger.warning("Google Cloud Speech-to-Text API is not available. Install google-cloud-speech package.")
            return False

        # Check for credentials in environment variable
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            try:
                self._credentials_path = credentials_path
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Google Speech-to-Text service: {str(e)}")
                return False
        else:
            logger.warning("Google Cloud Speech-to-Text API credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
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
        Authenticate with the Google Cloud Speech-to-Text API.

        Args:
            credentials_path: Path to the Google Cloud service account credentials JSON file.
                             If None, uses the path from GOOGLE_APPLICATION_CREDENTIALS environment variable.
            **kwargs: Additional authentication parameters.

        Returns:
            True if authentication was successful, False otherwise.
        """
        if not GOOGLE_SPEECH_AVAILABLE:
            logger.error("Google Cloud Speech-to-Text API is not available. Install google-cloud-speech package.")
            return False

        try:
            # Use provided credentials path or fall back to environment variable
            if credentials_path:
                self._credentials_path = credentials_path
            elif not self._credentials_path:
                self._credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if not self._credentials_path or not os.path.exists(self._credentials_path):
                logger.error("Google Cloud Speech-to-Text API credentials not found.")
                return False

            # Create credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )

            # Create client with credentials
            self._client = speech.SpeechClient(credentials=credentials)
            self._authenticated = True
            logger.info("Successfully authenticated with Google Cloud Speech-to-Text API")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Cloud Speech-to-Text API: {str(e)}")
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
            AIServiceCapability.SPEECH_RECOGNITION
        ]

    def get_supported_audio_formats(self) -> List[str]:
        """
        Get a list of audio formats supported by this service.

        Returns:
            List of supported audio formats.
        """
        return ['flac', 'wav', 'mp3', 'ogg', 'amr', 'awb', 'm4a']

    def get_supported_speech_languages(self) -> List[str]:
        """
        Get a list of languages supported by this service for speech recognition.

        Returns:
            List of supported language codes.
        """
        return [
            'en-US', 'en-GB', 'en-AU', 'en-CA', 'en-IN', 'en-IE', 'en-NZ', 'en-ZA',
            'fr-FR', 'fr-CA', 'es-ES', 'es-US', 'de-DE', 'it-IT', 'ja-JP', 'ko-KR',
            'pt-BR', 'pt-PT', 'ru-RU', 'zh-CN', 'zh-TW', 'nl-NL', 'hi-IN', 'ar-SA'
        ]

    def recognize_speech(self, audio_path: str, language: str = 'en-US', **kwargs) -> SpeechRecognitionResult:
        """
        Recognize speech in an audio file using the Google Cloud Speech-to-Text API.

        Args:
            audio_path: Path to the audio file to analyze.
            language: Language code for the speech (default: 'en-US').
            **kwargs: Additional parameters for the recognition, including:
                      - enable_word_time_offsets: Enable word-level timestamps (default: False)
                      - enable_speaker_diarization: Enable speaker diarization (default: False)
                      - diarization_speaker_count: Number of speakers for diarization (default: 2)
                      - model: Speech recognition model to use (default: 'default')
                      - enhanced: Use enhanced model (default: False)
                      - use_punctuation: Enable automatic punctuation (default: True)
                      - audio_channel_count: Number of audio channels (default: 1)

        Returns:
            SpeechRecognitionResult containing the recognition results.
        """
        if not self.is_authenticated():
            if not self.authenticate():
                return SpeechRecognitionResult(
                    success=False,
                    service_name=self.metadata.name,
                    error_message="Not authenticated with Google Cloud Speech-to-Text API"
                )

        try:
            # Get additional parameters
            enable_word_time_offsets = kwargs.get('enable_word_time_offsets', False)
            enable_speaker_diarization = kwargs.get('enable_speaker_diarization', False)
            diarization_speaker_count = kwargs.get('diarization_speaker_count', 2)
            model = kwargs.get('model', 'default')
            enhanced = kwargs.get('enhanced', False)
            use_punctuation = kwargs.get('use_punctuation', True)
            audio_channel_count = kwargs.get('audio_channel_count', 1)

            # Read the audio file
            with open(audio_path, 'rb') as audio_file:
                content = audio_file.read()

            # Create audio object
            audio = speech.RecognitionAudio(content=content)

            # Configure recognition settings
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,  # Default, will be auto-detected for most formats
                language_code=language,
                enable_word_time_offsets=enable_word_time_offsets,
                enable_automatic_punctuation=use_punctuation,
                model=model,
                use_enhanced=enhanced,
                audio_channel_count=audio_channel_count
            )

            # Add speaker diarization if requested
            if enable_speaker_diarization:
                diarization_config = speech.SpeakerDiarizationConfig(
                    enable_speaker_diarization=True,
                    min_speaker_count=1,
                    max_speaker_count=diarization_speaker_count
                )
                config.diarization_config = diarization_config

            # Send request to Google Cloud Speech-to-Text API
            response = self._client.recognize(config=config, audio=audio)

            # Process response
            result = SpeechRecognitionResult(
                success=True,
                service_name=self.metadata.name,
                raw_response=response
            )

            # Extract transcript and confidence
            if response.results:
                result.transcript = ' '.join([result.alternatives[0].transcript for result in response.results])
                result.confidence = response.results[0].alternatives[0].confidence if response.results[0].alternatives else 0.0

                # Extract alternatives
                result.alternatives = []
                for res in response.results:
                    for alt in res.alternatives:
                        result.alternatives.append({
                            'transcript': alt.transcript,
                            'confidence': alt.confidence
                        })

                # Extract word timings if available
                if enable_word_time_offsets:
                    result.word_timings = []
                    for res in response.results:
                        for alt in res.alternatives:
                            for word in alt.words:
                                result.word_timings.append({
                                    'word': word.word,
                                    'start_time': word.start_time.total_seconds(),
                                    'end_time': word.end_time.total_seconds()
                                })

                # Extract speaker labels if available
                if enable_speaker_diarization:
                    result.speaker_labels = []
                    for res in response.results:
                        for alt in res.alternatives:
                            for word in alt.words:
                                result.speaker_labels.append({
                                    'word': word.word,
                                    'speaker_tag': word.speaker_tag
                                })

            # Add metadata
            result.metadata = {
                'audio_path': audio_path,
                'language': language,
                'model': model,
                'enhanced': enhanced,
                'enable_word_time_offsets': enable_word_time_offsets,
                'enable_speaker_diarization': enable_speaker_diarization,
                'service': 'Google Cloud Speech-to-Text API'
            }

            return result

        except Exception as e:
            logger.error(f"Error recognizing speech with Google Cloud Speech-to-Text API: {str(e)}")
            return SpeechRecognitionResult(
                success=False,
                service_name=self.metadata.name,
                error_message=f"Error recognizing speech: {str(e)}"
            )
"""