"""
Google Cloud Vision AI Service Integration for Science Data Kit

This module provides integration with Google Cloud Vision API for image analysis,
enabling advanced image processing capabilities within the Science Data Kit.

The module includes:
1. A plugin implementation for Google Cloud Vision API
2. Image analysis capabilities using Vision API features
3. Utility functions for working with Vision API results

This integration allows researchers to analyze images using Google's powerful
computer vision capabilities directly within the Science Data Kit.
"""

import base64
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

try:
    from google.cloud import vision
    from google.cloud.vision import types
    from google.oauth2 import service_account
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

from science_data_kit.core.file_handling.ai_service_integration import (
    AIServiceCapability, AIServicePlugin, ImageAnalysisCapability,
    ImageAnalysisResult
)
from science_data_kit.core.integrations.plugin_architecture import (
    PluginCategory, PluginMetadata, register_plugin
)

# Set up logging
logger = logging.getLogger(__name__)


@register_plugin
class GoogleVisionService(AIServicePlugin, ImageAnalysisCapability):
    """
    Google Cloud Vision API integration for image analysis.

    This plugin provides integration with Google Cloud Vision API for image analysis,
    enabling advanced image processing capabilities such as label detection, object
    detection, face detection, and more.
    """

    def __init__(self):
        """Initialize the Google Vision service plugin."""
        self._client = None
        self._credentials_path = None
        self._authenticated = False

    @property
    def metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            name="google_vision",
            version="1.0.0",
            description="Google Cloud Vision API integration for image analysis",
            author="Science Data Kit Team",
            category=PluginCategory.OTHER,
            dependencies=[],
            website="https://cloud.google.com/vision",
            tags=["ai", "image", "analysis", "vision", "google"],
            enabled=GOOGLE_VISION_AVAILABLE,
            capabilities=[
                AIServiceCapability.IMAGE_ANALYSIS.value,
                AIServiceCapability.OBJECT_DETECTION.value,
                AIServiceCapability.FACE_DETECTION.value,
                AIServiceCapability.OCR.value
            ],
            priority=10  # High priority
        )

    @property
    def service_type(self) -> str:
        """Get the type of AI service."""
        return "image_analysis"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if not GOOGLE_VISION_AVAILABLE:
            logger.warning("Google Cloud Vision API is not available. Install google-cloud-vision package.")
            return False

        # Check for credentials in environment variable
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            try:
                self._credentials_path = credentials_path
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Google Vision service: {str(e)}")
                return False
        else:
            logger.warning("Google Cloud Vision API credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable.")
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
        Authenticate with the Google Cloud Vision API.

        Args:
            credentials_path: Path to the Google Cloud service account credentials JSON file.
                             If None, uses the path from GOOGLE_APPLICATION_CREDENTIALS environment variable.
            **kwargs: Additional authentication parameters.

        Returns:
            True if authentication was successful, False otherwise.
        """
        if not GOOGLE_VISION_AVAILABLE:
            logger.error("Google Cloud Vision API is not available. Install google-cloud-vision package.")
            return False

        try:
            # Use provided credentials path or fall back to environment variable
            if credentials_path:
                self._credentials_path = credentials_path
            elif not self._credentials_path:
                self._credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if not self._credentials_path or not os.path.exists(self._credentials_path):
                logger.error("Google Cloud Vision API credentials not found.")
                return False

            # Create credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                self._credentials_path
            )

            # Create client with credentials
            self._client = vision.ImageAnnotatorClient(credentials=credentials)
            self._authenticated = True
            logger.info("Successfully authenticated with Google Cloud Vision API")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Cloud Vision API: {str(e)}")
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
            AIServiceCapability.IMAGE_ANALYSIS,
            AIServiceCapability.OBJECT_DETECTION,
            AIServiceCapability.FACE_DETECTION,
            AIServiceCapability.OCR
        ]

    def get_supported_image_formats(self) -> List[str]:
        """
        Get a list of image formats supported by this service.

        Returns:
            List of supported image formats.
        """
        return ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'ico', 'tiff', 'tif']

    def get_supported_image_features(self) -> List[str]:
        """
        Get a list of image analysis features supported by this service.

        Returns:
            List of supported features.
        """
        return [
            'labels', 'objects', 'faces', 'landmarks', 'logos', 'text',
            'document_text', 'safe_search', 'properties', 'crop_hints',
            'web', 'product_search'
        ]

    def analyze_image(self, image_path: str, features: List[str] = None, **kwargs) -> ImageAnalysisResult:
        """
        Analyze an image using the Google Cloud Vision API.

        Args:
            image_path: Path to the image file to analyze.
            features: List of specific features to analyze (e.g., 'labels', 'objects', 'faces').
                      If None, all available features will be analyzed.
            **kwargs: Additional parameters for the analysis.

        Returns:
            ImageAnalysisResult containing the analysis results.
        """
        if not self.is_authenticated():
            if not self.authenticate():
                return ImageAnalysisResult(
                    success=False,
                    service_name=self.metadata.name,
                    error_message="Not authenticated with Google Cloud Vision API"
                )

        try:
            # Determine which features to analyze
            if features is None:
                features = ['labels', 'objects', 'faces', 'safe_search', 'properties', 'crop_hints', 'web']

            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Create image object
            image = vision.Image(content=content)

            # Prepare feature requests
            feature_types = []
            if 'labels' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION))
            if 'objects' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION))
            if 'faces' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.FACE_DETECTION))
            if 'landmarks' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.LANDMARK_DETECTION))
            if 'logos' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.LOGO_DETECTION))
            if 'text' in features or 'document_text' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION))
            if 'safe_search' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.SAFE_SEARCH_DETECTION))
            if 'properties' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES))
            if 'crop_hints' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.CROP_HINTS))
            if 'web' in features:
                feature_types.append(vision.Feature(type_=vision.Feature.Type.WEB_DETECTION))

            # Send request to Google Cloud Vision API
            request = vision.AnnotateImageRequest(image=image, features=feature_types)
            response = self._client.annotate_image(request=request)

            # Process response
            result = ImageAnalysisResult(
                success=True,
                service_name=self.metadata.name,
                raw_response=response
            )

            # Extract labels
            if 'labels' in features and response.label_annotations:
                result.labels = [
                    {
                        'description': label.description,
                        'score': label.score,
                        'mid': label.mid,
                        'topicality': label.topicality
                    }
                    for label in response.label_annotations
                ]

            # Extract objects
            if 'objects' in features and response.localized_object_annotations:
                result.objects = [
                    {
                        'name': obj.name,
                        'score': obj.score,
                        'mid': obj.mid,
                        'bounding_poly': [
                            {'x': vertex.x, 'y': vertex.y}
                            for vertex in obj.bounding_poly.normalized_vertices
                        ]
                    }
                    for obj in response.localized_object_annotations
                ]

            # Extract faces
            if 'faces' in features and response.face_annotations:
                result.faces = [
                    {
                        'joy': self._likelihood_to_score(face.joy_likelihood),
                        'sorrow': self._likelihood_to_score(face.sorrow_likelihood),
                        'anger': self._likelihood_to_score(face.anger_likelihood),
                        'surprise': self._likelihood_to_score(face.surprise_likelihood),
                        'detection_confidence': face.detection_confidence,
                        'bounding_poly': [
                            {'x': vertex.x, 'y': vertex.y}
                            for vertex in face.bounding_poly.vertices
                        ]
                    }
                    for face in response.face_annotations
                ]

            # Extract safe search
            if 'safe_search' in features and response.safe_search_annotation:
                result.safe_search = {
                    'adult': self._likelihood_to_score(response.safe_search_annotation.adult),
                    'medical': self._likelihood_to_score(response.safe_search_annotation.medical),
                    'spoof': self._likelihood_to_score(response.safe_search_annotation.spoof),
                    'violence': self._likelihood_to_score(response.safe_search_annotation.violence),
                    'racy': self._likelihood_to_score(response.safe_search_annotation.racy)
                }

            # Extract image properties
            if 'properties' in features and response.image_properties_annotation:
                colors = response.image_properties_annotation.dominant_colors.colors
                result.colors = [
                    {
                        'color': {
                            'red': color.color.red,
                            'green': color.color.green,
                            'blue': color.color.blue,
                            'alpha': color.color.alpha
                        },
                        'score': color.score,
                        'pixel_fraction': color.pixel_fraction
                    }
                    for color in colors
                ]
                result.properties = {
                    'dominant_colors': result.colors
                }

            # Extract crop hints
            if 'crop_hints' in features and response.crop_hints_annotation:
                result.crop_hints = [
                    {
                        'confidence': hint.confidence,
                        'importance_fraction': hint.importance_fraction,
                        'bounding_poly': [
                            {'x': vertex.x, 'y': vertex.y}
                            for vertex in hint.bounding_poly.vertices
                        ]
                    }
                    for hint in response.crop_hints_annotation.crop_hints
                ]

            # Extract web detection
            if 'web' in features and response.web_detection:
                web = response.web_detection
                result.web_detection = {
                    'web_entities': [
                        {
                            'entity_id': entity.entity_id,
                            'score': entity.score,
                            'description': entity.description
                        }
                        for entity in web.web_entities
                    ],
                    'full_matching_images': [
                        {'url': image.url}
                        for image in web.full_matching_images
                    ],
                    'partial_matching_images': [
                        {'url': image.url}
                        for image in web.partial_matching_images
                    ],
                    'visually_similar_images': [
                        {'url': image.url}
                        for image in web.visually_similar_images
                    ],
                    'best_guess_labels': [
                        {'label': label.label}
                        for label in web.best_guess_labels
                    ]
                }

            # Add metadata
            result.metadata = {
                'image_path': image_path,
                'features_analyzed': features,
                'service': 'Google Cloud Vision API'
            }

            return result

        except Exception as e:
            logger.error(f"Error analyzing image with Google Cloud Vision API: {str(e)}")
            return ImageAnalysisResult(
                success=False,
                service_name=self.metadata.name,
                error_message=f"Error analyzing image: {str(e)}"
            )

    def _likelihood_to_score(self, likelihood: int) -> float:
        """
        Convert a Google Cloud Vision likelihood enum to a score between 0 and 1.

        Args:
            likelihood: Google Cloud Vision likelihood enum value.

        Returns:
            Score between 0 and 1.
        """
        # Map likelihood enum values to scores
        likelihood_map = {
            0: 0.0,      # UNKNOWN
            1: 0.0,      # VERY_UNLIKELY
            2: 0.25,     # UNLIKELY
            3: 0.5,      # POSSIBLE
            4: 0.75,     # LIKELY
            5: 1.0       # VERY_LIKELY
        }
        return likelihood_map.get(likelihood, 0.0)
"""