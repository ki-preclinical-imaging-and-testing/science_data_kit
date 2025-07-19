"""
User Preferences Page Module for Science Data Kit

This module provides the core functionality for the User preferences page,
allowing users to customize their preferences for the application.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import os
import json

from science_data_kit.core.pages.base import BasePage

class PreferencesPage(BasePage):
    """
    Core functionality for the User preferences page.

    This class provides the backend functionality for managing user preferences,
    including saving and loading preferences, and applying them to the application.
    """

    def __init__(self):
        """Initialize the User preferences page."""
        super().__init__(title="User Preferences", icon="⚙️")

        # Initialize default preferences
        self.default_preferences = {
            "theme": "light",
            "font_size": "medium",
            "sidebar_collapsed": False,
            "show_tooltips": True,
            "data_table_rows": 10,
            "auto_save": True,
            "language": "en",
            "high_contrast": False,
            "screen_reader": False,
            "reduced_motion": False,
            "focus_indicators": False,
            "text_spacing": False,
            "custom_colors": {
                "background": "#ffffff",
                "text": "#31333F",
                "widget_background": "#f0f2f6",
                "widget_border": "#cccccc",
                "accent": "#1E88E5",
                "container_background": "rgba(240, 242, 246, 0.5)"
            }
        }

        # Initialize user preferences with defaults
        self.user_preferences = self.default_preferences.copy()

    def get_preferences_path(self) -> Path:
        """
        Get the path to the user preferences file.

        Returns:
            Path to the user preferences file.
        """
        # Create preferences directory in user's home directory
        preferences_dir = Path.home() / ".science_data_kit"
        preferences_dir.mkdir(parents=True, exist_ok=True)
        return preferences_dir / "user_preferences.yaml"

    def save_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save user preferences to a file.

        Args:
            preferences: The preferences to save.

        Returns:
            A dictionary with the result of the operation.
        """
        preferences_path = self.get_preferences_path()

        try:
            # Save preferences to file
            with open(preferences_path, 'w') as file:
                yaml.dump({"user_preferences": preferences}, file)

            # Update instance preferences
            self.user_preferences = preferences

            return {"success": True, "message": "Preferences saved successfully!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences from a file.

        Returns:
            A dictionary with the loaded preferences or the result of the operation.
        """
        preferences_path = self.get_preferences_path()

        if not preferences_path.exists():
            return {"success": True, "preferences": self.default_preferences, "message": "Using default preferences."}

        try:
            with open(preferences_path, 'r') as file:
                data = yaml.safe_load(file)

            if data and "user_preferences" in data:
                self.user_preferences = data["user_preferences"]
                return {"success": True, "preferences": self.user_preferences, "message": "Preferences loaded successfully!"}
            else:
                return {"success": False, "error": "Invalid preferences file format."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reset_preferences(self) -> Dict[str, Any]:
        """
        Reset preferences to defaults.

        Returns:
            A dictionary with the result of the operation.
        """
        try:
            self.user_preferences = self.default_preferences.copy()
            return {"success": True, "preferences": self.user_preferences, "message": "Preferences reset to defaults!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_preference(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Update a specific preference.

        Args:
            key: The preference key to update.
            value: The new value for the preference.

        Returns:
            A dictionary with the result of the operation.
        """
        try:
            # Handle nested preferences (e.g., custom_colors.background)
            if '.' in key:
                parts = key.split('.')
                parent_key = parts[0]
                child_key = parts[1]

                if parent_key in self.user_preferences and isinstance(self.user_preferences[parent_key], dict):
                    self.user_preferences[parent_key][child_key] = value
                else:
                    return {"success": False, "error": f"Invalid preference key: {key}"}
            else:
                self.user_preferences[key] = value

            # Auto-save if enabled
            if self.user_preferences.get("auto_save", True):
                return self.save_preferences(self.user_preferences)

            return {"success": True, "message": f"Preference {key} updated."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_preferences(self) -> Dict[str, Any]:
        """
        Get the current user preferences.

        Returns:
            A dictionary with the current user preferences.
        """
        return {"success": True, "preferences": self.user_preferences}

    def get_theme_colors(self) -> Dict[str, Any]:
        """
        Get the color palette for the current theme.

        Returns:
            A dictionary with the color palette for the current theme.
        """
        theme = self.user_preferences.get("theme", "light")

        # Define theme color palettes
        theme_colors = {
            "light": {
                "background": "#ffffff",
                "text": "#31333F",
                "widget_background": "#f0f2f6",
                "widget_border": "#cccccc",
                "accent": "#1E88E5",
                "container_background": "rgba(240, 242, 246, 0.5)"
            },
            "dark": {
                "background": "#0e1117",
                "text": "#fafafa",
                "widget_background": "#262730",
                "widget_border": "#4d4d4d",
                "accent": "#4CAF50",
                "container_background": "rgba(38, 39, 48, 0.5)"
            },
            "blue": {
                "background": "#E3F2FD",
                "text": "#0D47A1",
                "widget_background": "#BBDEFB",
                "widget_border": "#64B5F6",
                "accent": "#1976D2",
                "container_background": "rgba(187, 222, 251, 0.5)"
            },
            "green": {
                "background": "#E8F5E9",
                "text": "#1B5E20",
                "widget_background": "#C8E6C9",
                "widget_border": "#81C784",
                "accent": "#388E3C",
                "container_background": "rgba(200, 230, 201, 0.5)"
            },
            "purple": {
                "background": "#F3E5F5",
                "text": "#4A148C",
                "widget_background": "#E1BEE7",
                "widget_border": "#BA68C8",
                "accent": "#7B1FA2",
                "container_background": "rgba(225, 190, 231, 0.5)"
            }
        }

        # Get colors for the selected theme or use custom colors
        if theme == "custom" and "custom_colors" in self.user_preferences:
            colors = self.user_preferences["custom_colors"]
        else:
            colors = theme_colors.get(theme, theme_colors["light"])

        return {"success": True, "colors": colors}

    def get_font_sizes(self) -> Dict[str, Any]:
        """
        Get the font sizes for the current font size preference.

        Returns:
            A dictionary with the font sizes for the current font size preference.
        """
        font_size = self.user_preferences.get("font_size", "medium")

        font_sizes = {
            "small": {
                "base": "0.8rem",
                "h1": "1.5rem",
                "h2": "1.3rem",
                "h3": "1.1rem"
            },
            "medium": {
                "base": "1rem",
                "h1": "1.8rem",
                "h2": "1.5rem",
                "h3": "1.3rem"
            },
            "large": {
                "base": "1.2rem",
                "h1": "2.1rem",
                "h2": "1.8rem",
                "h3": "1.5rem"
            }
        }

        sizes = font_sizes.get(font_size, font_sizes["medium"])

        return {"success": True, "sizes": sizes}

    def get_language_names(self) -> Dict[str, Any]:
        """
        Get the names of available languages.

        Returns:
            A dictionary with the names of available languages.
        """
        language_names = {
            "en": "English",
            "es": "Español (Spanish)",
            "fr": "Français (French)",
            "de": "Deutsch (German)",
            "zh": "中文 (Chinese)"
        }

        return {"success": True, "language_names": language_names}
