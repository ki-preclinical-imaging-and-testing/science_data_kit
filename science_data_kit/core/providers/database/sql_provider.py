"""
SQL Database Provider for Science Data Kit

This module provides a provider for connecting to SQL databases, allowing
the Science Data Kit to interact with various SQL database systems.
"""

import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Any, Union, Tuple

from ...providers.registry import BaseProvider, ProviderType


class SQLDatabaseProvider(BaseProvider):
    """
    Provider for SQL database connections.

    This class provides functionality for connecting to various SQL database systems
    (MySQL, PostgreSQL, SQLite, etc.) and executing queries against them.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the SQL database provider.

        Args:
            config: Configuration dictionary containing connection details
                   Required keys depend on the database type:
                   - db_type: Type of database (mysql, postgresql, sqlite, etc.)
                   - connection_string: SQLAlchemy connection string (optional, alternative to individual params)
                   
                   For MySQL/PostgreSQL:
                   - host: Database host
                   - port: Database port
                   - database: Database name
                   - username: Database username
                   - password: Database password
                   
                   For SQLite:
                   - database_path: Path to SQLite database file
                   
                   Optional:
                   - pool_size: Connection pool size
                   - max_overflow: Maximum overflow connections
                   - pool_timeout: Connection pool timeout
                   - pool_recycle: Connection pool recycle time
                   - echo: Echo SQL queries (for debugging)
        """
        super().__init__(config)
        self.engine = None
        self.inspector = None
        self.db_type = config.get('db_type', '').lower()
        self.connection_string = config.get('connection_string')
        
    async def initialize(self) -> bool:
        """
        Initialize the SQL database connection.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # If connection string is provided, use it directly
            if self.connection_string:
                connection_url = self.connection_string
            else:
                # Otherwise, build connection string based on database type
                if self.db_type == 'sqlite':
                    database_path = self.config.get('database_path')
                    if not database_path:
                        print("Database path not provided for SQLite")
                        return False
                    
                    # Ensure path is absolute
                    database_path = os.path.abspath(os.path.expanduser(database_path))
                    connection_url = f"sqlite:///{database_path}"
                
                elif self.db_type in ['mysql', 'mariadb']:
                    host = self.config.get('host', 'localhost')
                    port = self.config.get('port', 3306)
                    database = self.config.get('database')
                    username = self.config.get('username')
                    password = self.config.get('password')
                    
                    if not all([database, username, password]):
                        print("Missing required MySQL connection parameters")
                        return False
                    
                    connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                
                elif self.db_type in ['postgresql', 'postgres']:
                    host = self.config.get('host', 'localhost')
                    port = self.config.get('port', 5432)
                    database = self.config.get('database')
                    username = self.config.get('username')
                    password = self.config.get('password')
                    
                    if not all([database, username, password]):
                        print("Missing required PostgreSQL connection parameters")
                        return False
                    
                    connection_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                
                elif self.db_type == 'mssql':
                    host = self.config.get('host', 'localhost')
                    port = self.config.get('port', 1433)
                    database = self.config.get('database')
                    username = self.config.get('username')
                    password = self.config.get('password')
                    
                    if not all([database, username, password]):
                        print("Missing required MSSQL connection parameters")
                        return False
                    
                    connection_url = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
                
                elif self.db_type == 'oracle':
                    host = self.config.get('host', 'localhost')
                    port = self.config.get('port', 1521)
                    service_name = self.config.get('service_name')
                    username = self.config.get('username')
                    password = self.config.get('password')
                    
                    if not all([service_name, username, password]):
                        print("Missing required Oracle connection parameters")
                        return False
                    
                    connection_url = f"oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"
                
                else:
                    print(f"Unsupported database type: {self.db_type}")
                    return False
            
            # Create engine with optional connection pool settings
            pool_size = self.config.get('pool_size', 5)
            max_overflow = self.config.get('max_overflow', 10)
            pool_timeout = self.config.get('pool_timeout', 30)
            pool_recycle = self.config.get('pool_recycle', 3600)
            echo = self.config.get('echo', False)
            
            self.engine = create_engine(
                connection_url,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                echo=echo
            )
            
            # Create inspector for schema introspection
            self.inspector = inspect(self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing SQL database provider: {str(e)}")
            self.is_initialized = False
            return False
    
    async def health_check(self) -> bool:
        """
        Check if the database connection is healthy.
        
        Returns:
            True if the connection is healthy, False otherwise
        """
        if not self.is_initialized or not self.engine:
            return False
        
        try:
            # Test connection by executing a simple query
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database health check failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the provider.
        
        Returns:
            Dictionary of provider capabilities
        """
        capabilities = {
            "type": ProviderType.DATABASE.value,
            "name": "sql",
            "database_type": self.db_type,
            "features": [
                "query",
                "schema_introspection",
                "data_export",
                "transaction_support"
            ],
            "supported_databases": [
                "sqlite",
                "mysql",
                "mariadb",
                "postgresql",
                "mssql",
                "oracle"
            ]
        }
        
        # Add database-specific capabilities
        if self.db_type == 'sqlite':
            capabilities["features"].extend([
                "file_based",
                "portable"
            ])
        elif self.db_type in ['mysql', 'mariadb', 'postgresql', 'mssql', 'oracle']:
            capabilities["features"].extend([
                "server_based",
                "multi_user",
                "connection_pooling"
            ])
        
        return capabilities
    
    async def list_tables(self) -> List[Dict[str, Any]]:
        """
        List tables in the database.
        
        Returns:
            List of table metadata dictionaries
        """
        if not self.is_initialized or not self.engine or not self.inspector:
            raise Exception("SQL database provider not initialized")
        
        try:
            tables = []
            
            # Get all table names
            table_names = self.inspector.get_table_names()
            
            # Get metadata for each table
            for table_name in table_names:
                # Get primary key columns
                pk_columns = self.inspector.get_pk_constraint(table_name).get('constrained_columns', [])
                
                # Get column information
                columns = self.inspector.get_columns(table_name)
                column_info = [
                    {
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column.get("nullable", True),
                        "default": str(column.get("default", "")),
                        "is_primary_key": column["name"] in pk_columns
                    }
                    for column in columns
                ]
                
                # Add table to the list
                tables.append({
                    "name": table_name,
                    "columns": column_info,
                    "primary_keys": pk_columns,
                    "schema": self.inspector.default_schema_name
                })
            
            return tables
        
        except Exception as e:
            print(f"Error listing tables: {str(e)}")
            raise
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a DataFrame.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query (optional)
            
        Returns:
            Pandas DataFrame containing the query results
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Execute query and return results as DataFrame
            if params:
                return pd.read_sql(text(query), self.engine, params=params)
            else:
                return pd.read_sql(text(query), self.engine)
        
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise
    
    async def execute_statement(self, statement: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE) and return affected rows.
        
        Args:
            statement: SQL statement to execute
            params: Parameters for the statement (optional)
            
        Returns:
            Number of affected rows
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Execute statement and return number of affected rows
            with self.engine.connect() as conn:
                with conn.begin():  # Start a transaction
                    if params:
                        result = conn.execute(text(statement), params)
                    else:
                        result = conn.execute(text(statement))
                    return result.rowcount
        
        except Exception as e:
            print(f"Error executing statement: {str(e)}")
            raise
    
    async def get_table_data(self, table_name: str, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """
        Get data from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            Pandas DataFrame containing the table data
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Build query with limit and offset
            query = f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"
            
            # Execute query and return results as DataFrame
            return pd.read_sql(text(query), self.engine)
        
        except Exception as e:
            print(f"Error getting table data: {str(e)}")
            raise
    
    async def get_table_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Build count query
            query = f"SELECT COUNT(*) AS count FROM {table_name}"
            
            # Execute query and return count
            df = pd.read_sql(text(query), self.engine)
            return df.iloc[0]['count']
        
        except Exception as e:
            print(f"Error getting table count: {str(e)}")
            raise
    
    async def export_table_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        Export a table to a pandas DataFrame.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Pandas DataFrame containing the table data
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Build query
            query = f"SELECT * FROM {table_name}"
            
            # Execute query and return results as DataFrame
            return pd.read_sql(text(query), self.engine)
        
        except Exception as e:
            print(f"Error exporting table to DataFrame: {str(e)}")
            raise
    
    async def import_dataframe_to_table(self, df: pd.DataFrame, table_name: str, 
                                       if_exists: str = 'fail', index: bool = False) -> bool:
        """
        Import a pandas DataFrame to a database table.
        
        Args:
            df: Pandas DataFrame to import
            table_name: Name of the target table
            if_exists: Action if table exists ('fail', 'replace', or 'append')
            index: Whether to include DataFrame index as a column
            
        Returns:
            True if import was successful, False otherwise
        """
        if not self.is_initialized or not self.engine:
            raise Exception("SQL database provider not initialized")
        
        try:
            # Import DataFrame to table
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=index)
            return True
        
        except Exception as e:
            print(f"Error importing DataFrame to table: {str(e)}")
            return False