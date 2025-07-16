"""
Flask State Adapter for Science Data Kit

This module provides a state adapter for Flask that uses Flask's session object
for state management, with fallbacks to other storage mechanisms for different scopes.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from science_data_kit.core.state.adapters.base_adapter import StateAdapter
from science_data_kit.core.state.state_types import StateValue

class FlaskStateAdapter(StateAdapter):
    """
    A state adapter for Flask that uses Flask's session object for state management.
    
    This adapter uses different storage mechanisms for different scopes:
    - SESSION: Flask's session object
    - GLOBAL: A file in the app's data directory
    - USER: A file in the user's home directory (if user is authenticated)
    - REQUEST: Flask's g object (resets on each request)
    - COMPONENT: In-memory dictionary with component-specific keys
    """
    
    def __init__(self, app=None, data_dir: Optional[str] = None):
        """
        Initialize the Flask state adapter.
        
        Args:
            app: The Flask application instance. If None, the adapter will attempt to use the current app.
            data_dir: The directory to use for global state storage. If None, uses ~/.science_data_kit/state.
        """
        try:
            from flask import session, g, current_app, has_request_context, has_app_context
            self._session = session
            self._g = g
            self._current_app = current_app
            self._has_request_context = has_request_context
            self._has_app_context = has_app_context
        except ImportError:
            raise ImportError("Flask is not installed. Please install it with 'pip install flask'.")
        
        self._app = app
        
        # Set up storage for different scopes
        self._component_state: Dict[str, Dict[str, StateValue]] = {}
        
        # Set up data directory for global state
        if data_dir is None:
            self._data_dir = Path.home() / ".science_data_kit" / "state"
        else:
            self._data_dir = Path(data_dir)
        
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize global state file if it doesn't exist
        self._global_state_file = self._data_dir / "global_state.json"
        if not self._global_state_file.exists():
            with open(self._global_state_file, 'w') as f:
                json.dump({}, f)
    
    def get(self, key: str, default: Any = None, scope: str = "session") -> StateValue:
        """
        Get a value from the state.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            scope: The scope for the state variable.
            
        Returns:
            The value associated with the key, or the default value if the key doesn't exist.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            return self._session.get(key, default)
        elif scope == "global":
            return self._get_from_file(self._global_state_file, key, default)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                return self._get_from_file(user_state_file, key, default)
            return default
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            return getattr(self._g, key, default)
        elif scope == "component":
            component_id, component_key = self._parse_component_key(key)
            return self._component_state.get(component_id, {}).get(component_key, default)
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def set(self, key: str, value: StateValue, scope: str = "session") -> None:
        """
        Set a value in the state.
        
        Args:
            key: The key to set.
            value: The value to set.
            scope: The scope for the state variable.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            self._session[key] = value
        elif scope == "global":
            self._set_in_file(self._global_state_file, key, value)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                self._set_in_file(user_state_file, key, value)
            else:
                raise ValueError("Cannot set user state without an authenticated user")
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            setattr(self._g, key, value)
        elif scope == "component":
            component_id, component_key = self._parse_component_key(key)
            if component_id not in self._component_state:
                self._component_state[component_id] = {}
            self._component_state[component_id][component_key] = value
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def delete(self, key: str, scope: str = "session") -> None:
        """
        Delete a value from the state.
        
        Args:
            key: The key to delete.
            scope: The scope for the state variable.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            if key in self._session:
                del self._session[key]
        elif scope == "global":
            self._delete_from_file(self._global_state_file, key)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                self._delete_from_file(user_state_file, key)
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            if hasattr(self._g, key):
                delattr(self._g, key)
        elif scope == "component":
            component_id, component_key = self._parse_component_key(key)
            if component_id in self._component_state and component_key in self._component_state[component_id]:
                del self._component_state[component_id][component_key]
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def has(self, key: str, scope: str = "session") -> bool:
        """
        Check if a key exists in the state.
        
        Args:
            key: The key to check.
            scope: The scope for the state variable.
            
        Returns:
            True if the key exists, False otherwise.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            return key in self._session
        elif scope == "global":
            return self._has_in_file(self._global_state_file, key)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                return self._has_in_file(user_state_file, key)
            return False
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            return hasattr(self._g, key)
        elif scope == "component":
            component_id, component_key = self._parse_component_key(key)
            return component_id in self._component_state and component_key in self._component_state[component_id]
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def clear(self, scope: str = "session") -> None:
        """
        Clear all values in the state.
        
        Args:
            scope: The scope for the state variables.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            self._session.clear()
        elif scope == "global":
            with open(self._global_state_file, 'w') as f:
                json.dump({}, f)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                with open(user_state_file, 'w') as f:
                    json.dump({}, f)
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            # Flask doesn't provide a way to clear all attributes of g,
            # so we'll just clear the ones we know about
            for key in dir(self._g):
                if not key.startswith('_'):
                    delattr(self._g, key)
        elif scope == "component":
            self._component_state = {}
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def keys(self, scope: str = "session") -> List[str]:
        """
        Get all keys in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A list of all keys in the state.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            return list(self._session.keys())
        elif scope == "global":
            return list(self._get_file_contents(self._global_state_file).keys())
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                return list(self._get_file_contents(user_state_file).keys())
            return []
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            return [key for key in dir(self._g) if not key.startswith('_')]
        elif scope == "component":
            keys = []
            for component_id, component_state in self._component_state.items():
                for component_key in component_state.keys():
                    keys.append(f"{component_id}:{component_key}")
            return keys
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def items(self, scope: str = "session") -> Dict[str, StateValue]:
        """
        Get all key-value pairs in the state.
        
        Args:
            scope: The scope for the state variables.
            
        Returns:
            A dictionary of all key-value pairs in the state.
        """
        if scope == "session":
            if not self._has_request_context():
                raise RuntimeError("Cannot access session state outside of a request context")
            return dict(self._session)
        elif scope == "global":
            return self._get_file_contents(self._global_state_file)
        elif scope == "user":
            user_id = self._get_user_id()
            if user_id:
                user_state_file = self._get_user_state_file(user_id)
                return self._get_file_contents(user_state_file)
            return {}
        elif scope == "request":
            if not self._has_request_context():
                raise RuntimeError("Cannot access request state outside of a request context")
            return {key: getattr(self._g, key) for key in dir(self._g) if not key.startswith('_')}
        elif scope == "component":
            items = {}
            for component_id, component_state in self._component_state.items():
                for component_key, value in component_state.items():
                    items[f"{component_id}:{component_key}"] = value
            return items
        else:
            raise ValueError(f"Invalid scope: {scope}")
    
    def _get_file_contents(self, file_path: Path) -> Dict[str, StateValue]:
        """Get the contents of a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _get_from_file(self, file_path: Path, key: str, default: Any = None) -> StateValue:
        """Get a value from a JSON file."""
        contents = self._get_file_contents(file_path)
        return contents.get(key, default)
    
    def _set_in_file(self, file_path: Path, key: str, value: StateValue) -> None:
        """Set a value in a JSON file."""
        contents = self._get_file_contents(file_path)
        contents[key] = value
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(contents, f, indent=2)
    
    def _delete_from_file(self, file_path: Path, key: str) -> None:
        """Delete a value from a JSON file."""
        contents = self._get_file_contents(file_path)
        if key in contents:
            del contents[key]
            with open(file_path, 'w') as f:
                json.dump(contents, f, indent=2)
    
    def _has_in_file(self, file_path: Path, key: str) -> bool:
        """Check if a key exists in a JSON file."""
        contents = self._get_file_contents(file_path)
        return key in contents
    
    def _parse_component_key(self, key: str) -> tuple:
        """Parse a component key into component ID and component key."""
        if ":" not in key:
            raise ValueError(f"Invalid component key format: {key}. Expected format: 'component_id:key'")
        return key.split(":", 1)
    
    def _get_user_id(self) -> Optional[str]:
        """Get the current user ID."""
        if not self._has_request_context():
            return None
        
        # Try to get the user ID from the session
        user_id = self._session.get('user_id')
        if user_id:
            return str(user_id)
        
        # Try to get the user ID from Flask-Login's current_user
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                return str(current_user.get_id())
        except ImportError:
            pass
        
        return None
    
    def _get_user_state_file(self, user_id: str) -> Path:
        """Get the path to the user state file."""
        return self._data_dir / "users" / f"{user_id}.json"