# SQL Database Integration Guide

## Overview

The Science Data Kit (SDK) provides a SQL database connector that allows you to connect to various SQL database systems, including SQLite, MySQL, PostgreSQL, Microsoft SQL Server, and Oracle. This guide explains how to configure and use the SQL database connector to interact with SQL databases.

## Configuration

To use the SQL database connector, you need to create a configuration dictionary with the necessary connection parameters. The required parameters depend on the type of database you want to connect to.

### Common Configuration Parameters

- `db_type`: Type of database (sqlite, mysql, postgresql, mssql, oracle)
- `connection_string`: SQLAlchemy connection string (optional, alternative to individual params)
- `pool_size`: Connection pool size (default: 5)
- `max_overflow`: Maximum overflow connections (default: 10)
- `pool_timeout`: Connection pool timeout in seconds (default: 30)
- `pool_recycle`: Connection pool recycle time in seconds (default: 3600)
- `echo`: Echo SQL queries for debugging (default: False)

### SQLite Configuration

For SQLite databases, you need to provide the path to the database file:

```python
config = {
    'db_type': 'sqlite',
    'database_path': '/path/to/database.db'
}
```

### MySQL/MariaDB Configuration

For MySQL or MariaDB databases, you need to provide the host, port, database name, username, and password:

```python
config = {
    'db_type': 'mysql',  # or 'mariadb'
    'host': 'localhost',
    'port': 3306,
    'database': 'mydatabase',
    'username': 'myuser',
    'password': 'mypassword'
}
```

### PostgreSQL Configuration

For PostgreSQL databases, you need to provide the host, port, database name, username, and password:

```python
config = {
    'db_type': 'postgresql',  # or 'postgres'
    'host': 'localhost',
    'port': 5432,
    'database': 'mydatabase',
    'username': 'myuser',
    'password': 'mypassword'
}
```

### Microsoft SQL Server Configuration

For Microsoft SQL Server databases, you need to provide the host, port, database name, username, and password:

```python
config = {
    'db_type': 'mssql',
    'host': 'localhost',
    'port': 1433,
    'database': 'mydatabase',
    'username': 'myuser',
    'password': 'mypassword'
}
```

### Oracle Configuration

For Oracle databases, you need to provide the host, port, service name, username, and password:

```python
config = {
    'db_type': 'oracle',
    'host': 'localhost',
    'port': 1521,
    'service_name': 'myservice',
    'username': 'myuser',
    'password': 'mypassword'
}
```

### Using a Connection String

Alternatively, you can provide a SQLAlchemy connection string directly:

```python
config = {
    'db_type': 'postgresql',
    'connection_string': 'postgresql://myuser:mypassword@localhost:5432/mydatabase'
}
```

## Usage

### Creating a SQL Database Provider

To create a SQL database provider, you need to use the provider registry:

```python
from science_data_kit.core.providers.registry import registry, ProviderType

# Create the provider
sql_provider = registry.create_provider(
    provider_type=ProviderType.DATABASE,
    name='sql',
    config=config
)

# Initialize the provider
await sql_provider.initialize()
```

### Listing Tables

To list all tables in the database:

```python
tables = await sql_provider.list_tables()
for table in tables:
    print(f"Table: {table['name']}")
    print(f"Columns: {len(table['columns'])}")
    print(f"Primary keys: {table['primary_keys']}")
```

### Executing Queries

To execute a SQL query and get the results as a pandas DataFrame:

```python
# Simple query
df = await sql_provider.execute_query("SELECT * FROM users WHERE age > 18")

# Query with parameters
df = await sql_provider.execute_query(
    "SELECT * FROM users WHERE age > :min_age",
    params={'min_age': 18}
)
```

### Executing Statements

To execute a SQL statement (INSERT, UPDATE, DELETE) and get the number of affected rows:

```python
# Insert statement
affected_rows = await sql_provider.execute_statement(
    "INSERT INTO users (name, age) VALUES (:name, :age)",
    params={'name': 'John Doe', 'age': 30}
)

# Update statement
affected_rows = await sql_provider.execute_statement(
    "UPDATE users SET age = :age WHERE name = :name",
    params={'name': 'John Doe', 'age': 31}
)

# Delete statement
affected_rows = await sql_provider.execute_statement(
    "DELETE FROM users WHERE name = :name",
    params={'name': 'John Doe'}
)
```

### Getting Table Data

To get data from a table with pagination:

```python
# Get first 1000 rows
df = await sql_provider.get_table_data('users')

# Get rows 1001-2000
df = await sql_provider.get_table_data('users', limit=1000, offset=1000)
```

### Getting Table Row Count

To get the number of rows in a table:

```python
count = await sql_provider.get_table_count('users')
print(f"The users table has {count} rows")
```

### Exporting Table to DataFrame

To export an entire table to a pandas DataFrame:

```python
df = await sql_provider.export_table_to_dataframe('users')
```

### Importing DataFrame to Table

To import a pandas DataFrame to a database table:

```python
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({
    'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
    'age': [30, 25, 40]
})

# Import to a new table
success = await sql_provider.import_dataframe_to_table(
    df=df,
    table_name='new_users',
    if_exists='replace',  # 'fail', 'replace', or 'append'
    index=False
)
```

## Error Handling

The SQL database provider methods raise exceptions when errors occur. You should wrap your code in try-except blocks to handle these exceptions:

```python
try:
    df = await sql_provider.execute_query("SELECT * FROM non_existent_table")
except Exception as e:
    print(f"An error occurred: {str(e)}")
```

## Best Practices

1. **Connection Pooling**: The SQL database provider uses connection pooling by default. You can adjust the pool size and other parameters in the configuration.

2. **Parameterized Queries**: Always use parameterized queries with the `params` argument to prevent SQL injection attacks.

3. **Resource Cleanup**: When you're done with the provider, close it to release resources:

   ```python
   # Close the provider when done
   await sql_provider.close()
   ```

4. **Transaction Management**: For operations that need to be atomic, use the `execute_statement` method with multiple statements in a single call, as it wraps the execution in a transaction.

5. **Large Result Sets**: For large result sets, use pagination with `get_table_data` to avoid memory issues.

## Supported Database Types

The SQL database provider supports the following database types:

- SQLite
- MySQL
- MariaDB
- PostgreSQL
- Microsoft SQL Server
- Oracle

## Dependencies

The SQL database provider requires the following dependencies:

- SQLAlchemy
- Pandas
- Database-specific drivers:
  - SQLite: Built-in
  - MySQL: pymysql
  - PostgreSQL: psycopg2
  - Microsoft SQL Server: pyodbc
  - Oracle: cx_Oracle

Make sure to install the appropriate driver for your database type.