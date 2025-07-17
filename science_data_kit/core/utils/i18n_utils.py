"""
Internationalization utilities for Science Data Kit.

This module provides utilities for internationalization (i18n) and localization (l10n)
of the Science Data Kit, including translation functions and language management.
"""

import gettext
import os
import threading
from typing import Dict, List, Optional

# Thread-local storage for current language
_thread_local = threading.local()
_thread_local.current_language = "en"  # Default language is English

# Available languages
AVAILABLE_LANGUAGES = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "ja": "日本語"
}

# Path to translations directory
_translations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "translations")

# Cache for translation objects
_translations_cache: Dict[str, gettext.GNUTranslations] = {}


def _get_translation(language: str) -> gettext.NullTranslations:
    """
    Get the translation object for the specified language.
    
    Args:
        language: The language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        A translation object for the specified language
    """
    if language in _translations_cache:
        return _translations_cache[language]
    
    try:
        translation = gettext.translation(
            "messages",
            localedir=_translations_dir,
            languages=[language]
        )
    except (FileNotFoundError, OSError):
        # Fall back to NullTranslations if the translation file is not found
        translation = gettext.NullTranslations()
    
    _translations_cache[language] = translation
    return translation


def get_current_language() -> str:
    """
    Get the current language code.
    
    Returns:
        The current language code (e.g., 'en', 'es', 'fr')
    """
    return getattr(_thread_local, "current_language", "en")


def set_current_language(language: str) -> None:
    """
    Set the current language.
    
    Args:
        language: The language code (e.g., 'en', 'es', 'fr')
    """
    if language not in AVAILABLE_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    
    _thread_local.current_language = language


def get_available_languages() -> Dict[str, str]:
    """
    Get the list of available languages.
    
    Returns:
        A dictionary mapping language codes to language names
    """
    return AVAILABLE_LANGUAGES


def translate(text: str, language: Optional[str] = None) -> str:
    """
    Translate the given text to the specified language.
    
    Args:
        text: The text to translate
        language: The language code (e.g., 'en', 'es', 'fr'). If None, uses the current language.
        
    Returns:
        The translated text
    """
    if language is None:
        language = get_current_language()
    
    translation = _get_translation(language)
    return translation.gettext(text)


# Alias for translate function (similar to gettext)
_ = translate


class TranslationManager:
    """
    Manager for handling translations in the application.
    
    This class provides methods for managing translations and language settings.
    It is designed to be used as a singleton instance.
    """
    
    def __init__(self):
        """Initialize the TranslationManager."""
        self._default_language = "en"
    
    def get_default_language(self) -> str:
        """
        Get the default language.
        
        Returns:
            The default language code
        """
        return self._default_language
    
    def set_default_language(self, language: str) -> None:
        """
        Set the default language.
        
        Args:
            language: The language code (e.g., 'en', 'es', 'fr')
        """
        if language not in AVAILABLE_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        self._default_language = language
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the name of the language for the given language code.
        
        Args:
            language_code: The language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            The name of the language
        """
        return AVAILABLE_LANGUAGES.get(language_code, language_code)
    
    def translate(self, text: str, language: Optional[str] = None) -> str:
        """
        Translate the given text to the specified language.
        
        Args:
            text: The text to translate
            language: The language code (e.g., 'en', 'es', 'fr'). If None, uses the current language.
            
        Returns:
            The translated text
        """
        return translate(text, language)


# Singleton instance of TranslationManager
translation_manager = TranslationManager()