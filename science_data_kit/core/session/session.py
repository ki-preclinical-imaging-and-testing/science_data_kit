"""
Session Management for Science Data Kit

This module provides the main session management functionality,
including creating, loading, and saving sessions, as well as
automatic session recovery in case of crashes or unexpected terminations.
"""

import os
import logging
import signal
import atexit
import time
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from threading import Timer, Lock

from .config import SessionConfig, load_session_config, save_session_config, get_default_session_dir, SessionConfigError
from .registry import ResourceRegistry, Resource

logger = logging.getLogger(__name__)

# Global variables for session recovery
_active_session = None
_recovery_lock = Lock()
_last_autosave_time = 0
_autosave_interval = 300  # 5 minutes in seconds


class Session:
    """
    Class representing a session.

    This class combines the session configuration and resource registry
    to provide a complete session management solution.

    Attributes:
        config: The session configuration.
        registry: The resource registry.
        session_file: The path to the session file.
    """

    def __init__(self, name: str, description: str = "", session_file: Optional[Union[str, Path]] = None):
        """
        Initialize a new session.

        Args:
            name: The name of the session.
            description: A description of the session.
            session_file: The path to the session file. If None, a default path will be used.
        """
        self.config = SessionConfig(name=name, description=description)
        self.registry = ResourceRegistry()

        if session_file is None:
            # Use default session directory
            session_dir = get_default_session_dir()
            session_file = session_dir / f"{name.lower().replace(' ', '_')}.yaml"

        self.session_file = Path(session_file)

    @classmethod
    def load(cls, session_file: Union[str, Path]) -> 'Session':
        """
        Load a session from a file.

        Args:
            session_file: The path to the session file.

        Returns:
            A new Session object.

        Raises:
            SessionConfigError: If there is an error loading the session.
        """
        try:
            # Load the session configuration
            config = load_session_config(session_file)

            # Create a new session
            session = cls(name=config.name, description=config.description, session_file=session_file)
            session.config = config

            # Load resources from the configuration
            for resource_id, resource_config in config.resources.items():
                resource_type = resource_config.get('type')
                if not resource_type:
                    logger.warning(f"Resource '{resource_id}' has no type, skipping")
                    continue

                try:
                    # Create the resource
                    session.registry.create_resource(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        config=resource_config.get('config', {})
                    )
                except Exception as e:
                    logger.error(f"Error creating resource '{resource_id}': {e}")

            # Load connections from the configuration
            # (This would be implemented based on the connection management system)

            return session

        except Exception as e:
            raise SessionConfigError(f"Error loading session: {e}")

    def save(self, session_file: Optional[Union[str, Path]] = None) -> None:
        """
        Save the session to a file.

        Args:
            session_file: The path to the session file. If None, the current session_file will be used.

        Raises:
            SessionConfigError: If there is an error saving the session.
        """
        if session_file is not None:
            self.session_file = Path(session_file)

        try:
            # Update the resources in the configuration
            self.config.resources = {}
            for resource_id, resource in self.registry.resources.items():
                self.config.resources[resource_id] = {
                    "type": resource.resource_type,
                    "config": resource.to_config()
                }

            # Update the connections in the configuration
            # (This would be implemented based on the connection management system)

            # Save the configuration
            save_session_config(self.config, self.session_file)

            logger.info(f"Session saved to {self.session_file}")

        except Exception as e:
            raise SessionConfigError(f"Error saving session: {e}")

    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource to the session.

        Args:
            resource: The resource to add.

        Raises:
            ValueError: If a resource with the same ID is already registered.
        """
        # Register the resource in the registry
        self.registry.register_resource(resource)

        # Add the resource to the configuration
        self.config.add_resource(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            resource_config=resource.to_config()
        )

    def remove_resource(self, resource_id: str) -> None:
        """
        Remove a resource from the session.

        Args:
            resource_id: The ID of the resource to remove.

        Raises:
            KeyError: If the resource is not registered.
        """
        # Unregister the resource from the registry
        self.registry.unregister_resource(resource_id)

        # Remove the resource from the configuration
        self.config.remove_resource(resource_id)

    def get_resource(self, resource_id: str) -> Resource:
        """
        Get a resource from the session.

        Args:
            resource_id: The ID of the resource to get.

        Returns:
            The requested resource.

        Raises:
            KeyError: If the resource is not registered.
        """
        return self.registry.get_resource(resource_id)

    def add_dependency(self, dependent_id: str, dependency_id: str) -> None:
        """
        Add a dependency relationship between two resources.

        Args:
            dependent_id: The ID of the dependent resource.
            dependency_id: The ID of the dependency resource.

        Raises:
            KeyError: If either resource is not registered.
        """
        self.registry.add_dependency(dependent_id, dependency_id)

    def remove_dependency(self, dependent_id: str, dependency_id: str) -> None:
        """
        Remove a dependency relationship between two resources.

        Args:
            dependent_id: The ID of the dependent resource.
            dependency_id: The ID of the dependency resource.

        Raises:
            KeyError: If either resource is not registered.
        """
        self.registry.remove_dependency(dependent_id, dependency_id)

    def get_dependencies(self, resource_id: str) -> List[Resource]:
        """
        Get all dependencies of a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            A list of resources that the specified resource depends on.

        Raises:
            KeyError: If the resource is not registered.
        """
        return self.registry.get_dependencies(resource_id)

    def get_dependents(self, resource_id: str) -> List[Resource]:
        """
        Get all dependents of a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            A list of resources that depend on the specified resource.

        Raises:
            KeyError: If the resource is not registered.
        """
        return self.registry.get_dependents(resource_id)


def create_session(name: str, description: str = "", set_as_active: bool = True) -> Session:
    """
    Create a new session.

    Args:
        name: The name of the session.
        description: A description of the session.
        set_as_active: Whether to set the new session as the active session for automatic recovery.

    Returns:
        A new Session object.
    """
    session = Session(name=name, description=description)

    if set_as_active:
        set_active_session(session)

    return session


def load_session(session_file: Union[str, Path], set_as_active: bool = True) -> Session:
    """
    Load a session from a file.

    Args:
        session_file: The path to the session file.
        set_as_active: Whether to set the loaded session as the active session for automatic recovery.

    Returns:
        A Session object.

    Raises:
        SessionConfigError: If there is an error loading the session.
    """
    session = Session.load(session_file)

    if set_as_active:
        set_active_session(session)

    return session


def list_sessions() -> List[Dict[str, Any]]:
    """
    List all available sessions in the default session directory.

    Returns:
        A list of dictionaries containing session metadata.
    """
    from .config import list_available_sessions
    return list_available_sessions()


def get_session_file_path(name: str) -> Path:
    """
    Get the path to a session file.

    Args:
        name: The name of the session.

    Returns:
        The path to the session file.
    """
    session_dir = get_default_session_dir()
    return session_dir / f"{name.lower().replace(' ', '_')}.yaml"


def set_active_session(session: Session) -> None:
    """
    Set the active session for automatic recovery.

    Args:
        session: The session to set as active.
    """
    global _active_session
    _active_session = session

    # Register the session for automatic saving and recovery
    _register_session_recovery()


def _register_session_recovery() -> None:
    """
    Register the active session for automatic saving and recovery.

    This function sets up signal handlers and exit handlers to ensure
    the session is saved before the application exits.
    """
    if _active_session is None:
        return

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _signal_handler)

    # Register exit handler
    atexit.register(_exit_handler)

    # Start automatic saving
    _schedule_autosave()


def _signal_handler(signum: int, frame) -> None:
    """
    Handle signals (e.g., SIGINT, SIGTERM) by saving the active session.

    Args:
        signum: The signal number.
        frame: The current stack frame.
    """
    logger.info(f"Received signal {signum}, saving session before exit")
    _save_active_session()

    # Re-raise the signal to allow the default handler to run
    signal.default_int_handler(signum, frame)


def _exit_handler() -> None:
    """
    Handle application exit by saving the active session.
    """
    logger.info("Application exiting, saving session")
    _save_active_session()


def _save_active_session() -> None:
    """
    Save the active session if one exists.
    """
    global _last_autosave_time

    with _recovery_lock:
        if _active_session is None:
            return

        try:
            _active_session.save()
            _last_autosave_time = time.time()
            logger.info("Active session saved successfully")
        except Exception as e:
            logger.error(f"Error saving active session: {e}")


def _schedule_autosave() -> None:
    """
    Schedule automatic saving of the active session.
    """
    if _active_session is None:
        return

    def _autosave_task():
        _save_active_session()
        _schedule_autosave()

    # Schedule the next autosave
    Timer(_autosave_interval, _autosave_task).start()


def set_autosave_interval(interval_seconds: int) -> None:
    """
    Set the interval for automatic session saving.

    Args:
        interval_seconds: The interval in seconds between automatic saves.
            Set to 0 to disable automatic saving.

    Raises:
        ValueError: If interval_seconds is negative.
    """
    global _autosave_interval

    if interval_seconds < 0:
        raise ValueError("Autosave interval cannot be negative")

    _autosave_interval = interval_seconds
    logger.info(f"Autosave interval set to {interval_seconds} seconds")

    # If autosave is disabled, don't schedule the next autosave
    if interval_seconds == 0:
        logger.info("Automatic session saving disabled")
        return

    # If there's an active session, reschedule autosave with the new interval
    if _active_session is not None:
        _schedule_autosave()


def get_recovery_session_path() -> Optional[Path]:
    """
    Get the path to the most recently modified session file.

    Returns:
        The path to the most recently modified session file, or None if no session files exist.
    """
    session_dir = get_default_session_dir()
    session_files = list(session_dir.glob("*.yaml"))

    if not session_files:
        return None

    # Sort by modification time (newest first)
    session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return session_files[0]


def recover_last_session() -> Optional[Session]:
    """
    Recover the most recently saved session.

    Returns:
        The recovered session, or None if no session could be recovered.
    """
    recovery_path = get_recovery_session_path()

    if recovery_path is None:
        logger.info("No session files found for recovery")
        return None

    try:
        logger.info(f"Attempting to recover session from {recovery_path}")
        session = load_session(recovery_path)
        set_active_session(session)
        logger.info(f"Successfully recovered session: {session.config.name}")
        return session
    except Exception as e:
        logger.error(f"Error recovering session: {e}")
        return None
