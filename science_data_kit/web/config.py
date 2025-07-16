"""
Configuration for the Flask Application

This module provides configuration classes for the Flask application.
"""

import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration class for the Flask application."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = False
    TESTING = False
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR') or '/tmp/flask_session'
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    
    # API configuration
    API_PREFIX = '/api/v1'
    
    # Authentication configuration
    AUTH_REQUIRED = True
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp/uploads'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/tmp/science_data_kit.log'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    """Production configuration."""
    # Production-specific settings
    pass