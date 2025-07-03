"""
PostgreSQL Manager for Science Data Kit

This module provides a unified interface for interacting with PostgreSQL databases.
It provides functionality for connecting to PostgreSQL databases, executing queries,
and managing connections.
"""

import os
import yaml
import socket
import docker
import pandas as pd
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


class DatabaseError(Exception):
    """Base exception class for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Exception raised for connection-related errors."""
    pass


class QueryError(DatabaseError):
    """Exception raised for query-related errors."""
    pass


class ConfigError(DatabaseError):
    """Exception raised for configuration-related errors."""
    pass


def load_db_config(fn: str = 'postgres_config.yaml') -> Dict[str, Any]:
    """
    Loads the database configuration from a YAML file.

    Args:
        fn: Path to the YAML configuration file.

    Returns:
        Dictionary containing the database configuration.

    Raises:
        ConfigError: If the configuration file cannot be loaded.
    """
    # If the file is .postgres_config_auto.yaml, try to load it from the app directory first
    if fn == '.postgres_config_auto.yaml':
        try:
            with open(f"app/{fn}", 'r') as file:
                return yaml.safe_load(file)
        except Exception:
            # Fall back to the original location
            pass

    try:
        with open(fn, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise ConfigError(f"Could not load {fn}: {e}")


def update_db_config_auto(hostname: str, port: str, username: Optional[str] = None,
                         password: Optional[str] = None, database: Optional[str] = None) -> None:
    """
    Updates the auto-generated database configuration file.

    Args:
        hostname: The hostname of the PostgreSQL server.
        port: The port of the PostgreSQL server.
        username: The username for authentication.
        password: The password for authentication.
        database: The name of the database to connect to.

    Raises:
        ConfigError: If the configuration file cannot be updated.
    """
    config_path = Path("app/.postgres_config_auto.yaml")

    # Create config dictionary
    config = {
        "host": hostname,
        "port": port,
    }

    if username:
        config["user"] = username
    if password:
        config["password"] = password
    if database:
        config["database"] = database

    # Write to file
    try:
        with open(config_path, 'w') as file:
            yaml.dump(config, file)
    except Exception as e:
        raise ConfigError(f"Could not update configuration file: {e}")


def find_free_port(start_port: int = 5432) -> int:
    """
    Finds a free port starting from the given port number.

    Args:
        start_port: The port number to start searching from.

    Returns:
        A free port number.
    """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1


class PostgreSQLManager:
    """
    A unified manager for PostgreSQL database operations.

    This class provides methods for:
    - Managing multiple PostgreSQL connections
    - Starting and stopping PostgreSQL containers
    - Executing queries and processing results
    - Importing and exporting data
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(PostgreSQLManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                config_file: Optional[str] = None,
                use_session_state: bool = False,
                connect_on_init: bool = False):
        """
        Initialize the PostgreSQLManager instance.

        Args:
            config: Dictionary with database connection details.
            config_file: Path to a YAML file with database connection details.
            use_session_state: If True, use the connection from Streamlit session_state if available.
            connect_on_init: If True, attempt to connect during initialization.

        Raises:
            ConnectionError: If connect_on_init is True and the connection details are invalid or the connection fails.
        """
        # Skip initialization if already initialized (singleton pattern)
        if self._initialized:
            return

        # Dictionary to store multiple connections
        # Format: {connection_name: {
        #     "connection": PostgreSQL connection object,
        #     "host": hostname string,
        #     "port": port string,
        #     "user": username string,
        #     "password": password string,
        #     "database": database name string
        # }}
        self._connections = {}

        # Current active connection name
        self._active_connection = None

        # Default connection parameters (used for backward compatibility)
        self._connection = None
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.database = None

        # Container configuration
        self.container_name = "postgres-instance"
        self.port = 5432
        self._connection_error = None

        # Try to use session_state connection if requested
        if use_session_state:
            try:
                import streamlit as st
                if hasattr(st, 'session_state') and 'postgres_connected' in st.session_state and st.session_state.postgres_connected:
                    self._connection = st.session_state.postgres_connection
                    self.host = st.session_state.postgres_host
                    self.port = st.session_state.postgres_port
                    self.user = st.session_state.postgres_user
                    self.password = st.session_state.postgres_password
                    self.database = st.session_state.postgres_database
                    self._initialized = True
                    return
            except (ImportError, AttributeError):
                # Fall back to config if session_state is not available or not connected
                pass

        # Use config if session_state is not available or not requested
        if config is None:
            try:
                if config_file:
                    config = load_db_config(config_file)
                else:
                    # Try to load from default locations
                    try:
                        config = load_db_config('.postgres_config_auto.yaml')
                    except ConfigError:
                        pass

                    if not config:
                        try:
                            config = load_db_config('.postgres_config.yaml')
                        except ConfigError:
                            pass

                    if not config:
                        try:
                            config = load_db_config('postgres_config.yaml')
                        except ConfigError:
                            pass
            except Exception as e:
                self._connection_error = f"Error loading configuration: {e}"
                self._initialized = True
                return

        if not config:
            self._connection_error = "No configuration provided and no default configuration found."
            self._initialized = True
            return

        required_keys = {"host", "port", "user", "password"}
        if not all(key in config for key in required_keys):
            self._connection_error = f"Missing required keys in config. Expected keys: {required_keys}"
            self._initialized = True
            return

        self.host = config["host"]
        self.port = config["port"]
        self.user = config["user"]
        self.password = config["password"]
        self.database = config.get("database", "postgres")

        # Only connect if requested
        if connect_on_init:
            try:
                self._connect()
            except ConnectionError as e:
                self._connection_error = str(e)

        self._initialized = True

    def _connect(self, connection_name: Optional[str] = None) -> bool:
        """
        Establishes a connection to the PostgreSQL database.

        Args:
            connection_name: Optional name for the connection. If not provided,
                             uses the current connection parameters.

        Returns:
            True if connection was successful, False otherwise.

        Raises:
            ConnectionError: If the connection fails and raise_error is True.
        """
        # If connection_name is provided, use it to create a new named connection
        if connection_name:
            host = self.host
            port = self.port
            user = self.user
            password = self.password
            database = self.database
        else:
            # Use current connection parameters
            if not self.host or not self.port or not self.user or not self.password:
                self._connection_error = "Missing connection details (host, port, user, or password)"
                return False
            host = self.host
            port = self.port
            user = self.user
            password = self.password
            database = self.database or "postgres"
            # Use a default connection name if none provided
            connection_name = "default"

        # Check if we already have a connection with the same host, port, and database
        # If so, only close it if it's been manually disconnected or is inactive
        names_to_remove = []
        for name, conn in self._connections.items():
            # Only consider connections with the same host, port, and database
            if conn["host"] == host and conn["port"] == port and conn["database"] == database and name != connection_name:
                # Check if the connection is active
                try:
                    cursor = conn["connection"].cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    # Connection is active, keep it
                except Exception:
                    # Connection is inactive or has been manually disconnected, mark for removal
                    names_to_remove.append(name)

        # Remove inactive or manually disconnected duplicate connections
        for name in names_to_remove:
            conn = self._connections[name]
            # Close the duplicate connection
            if conn["connection"]:
                conn["connection"].close()
            # Remove it from connections
            del self._connections[name]

        try:
            # Create a new connection
            connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )

            # Test the connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()

            # Store the connection
            self._connections[connection_name] = {
                "connection": connection,
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database
            }

            # Set as active connection
            self._active_connection = connection_name

            # Update the default connection parameters for backward compatibility
            self._connection = connection
            self.host = host
            self.port = port
            self.user = user
            self.password = password
            self.database = database

            self._connection_error = None
            return True
        except Exception as e:
            self._connection_error = f"Failed to connect to PostgreSQL: {e}"
            return False

    def close(self, connection_name: Optional[str] = None) -> None:
        """
        Closes a PostgreSQL connection.

        Args:
            connection_name: Optional name of the connection to close.
                            If None, closes the active connection.
        """
        if connection_name is None:
            # Close the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                return

        # Close the specified connection
        if connection_name in self._connections:
            conn = self._connections[connection_name]
            if conn["connection"]:
                conn["connection"].close()

            # Remove from connections
            del self._connections[connection_name]

            # If this was the active connection, clear it
            if self._active_connection == connection_name:
                self._active_connection = None
                self._connection = None

                # If there are other connections, set one as active
                if self._connections:
                    # Get the first connection name
                    new_active = next(iter(self._connections))
                    self.set_active_connection(new_active)

        # For backward compatibility
        if self._connection and (not self._connections or not self._active_connection):
            self._connection.close()
            self._connection = None

    def is_connected(self, connection_name: Optional[str] = None) -> bool:
        """
        Checks if the manager is connected to a PostgreSQL database.

        Args:
            connection_name: Optional name of the connection to check.
                            If None, checks the active connection.

        Returns:
            True if connected, False otherwise.
        """
        if connection_name is None:
            # Check the active connection
            if self._active_connection:
                connection_name = self._active_connection
            else:
                # For backward compatibility
                if not self._connection:
                    return False
                try:
                    cursor = self._connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    return True
                except Exception:
                    return False

        # Check the specified connection
        if connection_name in self._connections:
            conn = self._connections[connection_name]
            try:
                cursor = conn["connection"].cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            except Exception:
                return False

        return False

    def set_active_connection(self, connection_name: str) -> bool:
        """
        Sets the active connection.

        Args:
            connection_name: Name of the connection to set as active.

        Returns:
            True if successful, False if the connection doesn't exist.
        """
        if connection_name in self._connections:
            self._active_connection = connection_name
            conn = self._connections[connection_name]

            # Update default connection parameters for backward compatibility
            self._connection = conn["connection"]
            self.host = conn["host"]
            self.port = conn["port"]
            self.user = conn["user"]
            self.password = conn["password"]
            self.database = conn["database"]

            return True
        return False

    def get_connection_names(self) -> List[str]:
        """
        Gets the names of all connections.

        Returns:
            List of connection names.
        """
        return list(self._connections.keys())

    def get_active_connection_name(self) -> Optional[str]:
        """
        Gets the name of the active connection.

        Returns:
            Name of the active connection, or None if no active connection.
        """
        return self._active_connection

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, 
                      connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes a SQL query and returns the results.

        Args:
            query: The SQL query to execute.
            parameters: Optional dictionary of parameters to include in the query.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            List of dictionaries containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        # If connection_name is provided, use that specific connection
        if connection_name:
            if connection_name not in self._connections:
                raise ConnectionError(f"Connection '{connection_name}' does not exist")

            conn = self._connections[connection_name]
            connection = conn["connection"]
        else:
            # Use the active connection
            if self._active_connection:
                conn = self._connections[self._active_connection]
                connection = conn["connection"]
            else:
                # Try to connect if not already connected (backward compatibility)
                if not self._connection:
                    if not self._connect():
                        raise ConnectionError(f"Cannot run query. No active connection to PostgreSQL. {self._connection_error}")
                connection = self._connection

        parameters = parameters or {}

        try:
            # Use RealDictCursor to get results as dictionaries
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, parameters)
                
                # Check if the query returns results
                if cursor.description:
                    results = cursor.fetchall()
                    # Convert to list of dictionaries
                    return [dict(row) for row in results]
                else:
                    # For queries that don't return results (e.g., INSERT, UPDATE, DELETE)
                    connection.commit()
                    return []
        except Exception as e:
            connection.rollback()
            raise QueryError(f"Query execution failed: {e}")

    def query_to_dataframe(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                          connection_name: Optional[str] = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns the results as a Pandas DataFrame.

        Args:
            query: The SQL query to execute.
            parameters: Optional dictionary of parameters.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A Pandas DataFrame containing the query results.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters, connection_name)
        return pd.DataFrame(results)

    def query_to_value(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                      connection_name: Optional[str] = None) -> Any:
        """
        Executes a SQL query and returns a single value.

        Args:
            query: The SQL query to execute.
            parameters: Optional dictionary of parameters.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            A single value if one result is returned, or a list of values if multiple rows are returned.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        results = self.execute_query(query, parameters, connection_name)
        if not results:
            return None

        values = []
        for record in results:
            record_values = list(record.values())
            if record_values:
                values.append(record_values[0])

        return values[0] if len(values) == 1 else values

    def get_container_status(self) -> str:
        """
        Gets the status of the PostgreSQL container.

        Returns:
            The status of the container ("running", "stopped", or "not found").
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True, filters={"name": self.container_name})
            if containers:
                return containers[0].status
            return "not found"
        except Exception:
            return "not found"

    def get_hostname(self) -> str:
        """
        Gets the hostname for connecting to the PostgreSQL container.

        Returns:
            The hostname (either "localhost" or the container's IP address).
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(filters={"name": self.container_name})
            if containers:
                container = containers[0]
                ip_address = container.attrs["NetworkSettings"]["IPAddress"]
                if ip_address:
                    return ip_address
            return "localhost"
        except Exception:
            return "localhost"

    def start_container(self, version: str = "latest") -> bool:
        """
        Starts the PostgreSQL container.

        Args:
            version: The PostgreSQL version to use.

        Returns:
            True if the container was started successfully, False otherwise.

        Raises:
            ConnectionError: If the container cannot be started.
        """
        try:
            client = docker.from_env()

            # Check if container already exists
            existing_containers = client.containers.list(all=True, filters={"name": self.container_name})
            if existing_containers:
                container = existing_containers[0]
                if container.status != "running":
                    container.start()
                return True

            # Find available port
            self.port = find_free_port(5432)

            # Create and start container
            container = client.containers.run(
                f"postgres:{version}",
                name=self.container_name,
                detach=True,
                ports={
                    '5432/tcp': self.port
                },
                environment={
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_PASSWORD": "postgres",
                    "POSTGRES_DB": "postgres"
                },
                volumes={
                    f"{self.container_name}-data": {"bind": "/var/lib/postgresql/data", "mode": "rw"}
                }
            )

            # Update connection details
            self.host = "localhost"
            self.port = self.port
            self.user = "postgres"
            self.password = "postgres"
            self.database = "postgres"

            # Update config file
            update_db_config_auto(self.host, str(self.port), self.user, self.password, self.database)

            return True
        except Exception as e:
            raise ConnectionError(f"Failed to start PostgreSQL container: {e}")

    def stop_container(self) -> bool:
        """
        Stops the PostgreSQL container.

        Returns:
            True if the container was stopped successfully, False otherwise.
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(filters={"name": self.container_name})
            if containers:
                containers[0].stop()
                return True
            return False
        except Exception:
            return False

    def list_databases(self, connection_name: Optional[str] = None) -> List[str]:
        """
        Lists all databases in the PostgreSQL server.

        Args:
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            List of database names.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
        results = self.execute_query(query, connection_name=connection_name)
        return [result["datname"] for result in results]

    def list_schemas(self, connection_name: Optional[str] = None) -> List[str]:
        """
        Lists all schemas in the current database.

        Args:
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            List of schema names.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name"
        results = self.execute_query(query, connection_name=connection_name)
        return [result["schema_name"] for result in results]

    def list_tables(self, schema: str = "public", connection_name: Optional[str] = None) -> List[str]:
        """
        Lists all tables in the specified schema.

        Args:
            schema: The schema to list tables from.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            List of table names.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s 
        ORDER BY table_name
        """
        results = self.execute_query(query, {"schema": schema}, connection_name=connection_name)
        return [result["table_name"] for result in results]

    def get_table_schema(self, table_name: str, schema: str = "public", 
                        connection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Gets the schema of a table.

        Args:
            table_name: The name of the table.
            schema: The schema the table belongs to.
            connection_name: Optional name of the connection to use.
                            If None, uses the active connection.

        Returns:
            List of dictionaries containing column information.

        Raises:
            ConnectionError: If there is no active connection.
            QueryError: If the query execution fails.
        """
        query = """
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM 
            information_schema.columns
        WHERE 
            table_schema = %s
            AND table_name = %s
        ORDER BY 
            ordinal_position
        """
        return self.execute_query(query, {"schema": schema, "table_name": table_name}, connection_name=connection_name)


# Singleton instance - don't connect on initialization to avoid startup errors
postgres_manager = PostgreSQLManager(connect_on_init=False)