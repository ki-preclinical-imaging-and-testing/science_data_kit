# Database Operations Guide

## Overview

The Science Data Kit provides advanced database operations capabilities that allow you to efficiently work with Neo4j databases. This guide explains how to use the SDK's database features, including query caching, parameterized query templates, query logging and performance metrics, and pagination for large result sets.

## Table of Contents

1. [Introduction](#introduction)
2. [Database Connection](#database-connection)
3. [Query Caching](#query-caching)
4. [Parameterized Query Templates](#parameterized-query-templates)
5. [Query Logging and Performance Metrics](#query-logging-and-performance-metrics)
6. [Pagination for Large Result Sets](#pagination-for-large-result-sets)
7. [Advanced Query Techniques](#advanced-query-techniques)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

Efficient database operations are crucial for working with graph databases like Neo4j. The Science Data Kit provides several features to improve the performance, reliability, and usability of database operations:

- **Query Caching**: Cache database queries for improved performance
- **Parameterized Query Templates**: Define reusable query templates with named parameters, validation, and documentation
- **Query Logging and Performance Metrics**: Track and analyze query execution times, cache hits/misses, and other performance data
- **Pagination for Large Result Sets**: Retrieve large sets of nodes and relationships with pagination support

These features help you work more efficiently with Neo4j databases, especially when dealing with large datasets or complex queries.

## Database Connection

Before you can perform database operations, you need to establish a connection to the Neo4j database.

### Basic Connection

Here's an example of establishing a basic connection to a Neo4j database:

```python
from science_data_kit.core.db import Neo4jManager

# Create a database manager
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Test the connection
if db_manager.test_connection():
    print("Connected to Neo4j database")
else:
    print("Failed to connect to Neo4j database")
```

### Connection Pool

For better performance, you can use a connection pool:

```python
from science_data_kit.core.db import Neo4jConnectionPool

# Create a connection pool
connection_pool = Neo4jConnectionPool(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j",
    max_connections=10,
    connection_timeout=30
)

# Get a connection from the pool
with connection_pool.get_connection() as db_manager:
    # Use the connection
    result = db_manager.run_query("MATCH (n) RETURN count(n) AS count")
    print(f"Node count: {result[0]['count']}")
```

## Query Caching

Query caching can significantly improve performance by storing the results of queries and returning them directly when the same query is executed again.

### Enabling Query Caching

Query caching is enabled by default in the Neo4jManager. You can configure it when creating the manager:

```python
from science_data_kit.core.db import Neo4jManager

# Create a database manager with caching enabled
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j",
    enable_caching=True,
    cache_size=1000,  # Maximum number of cached queries
    cache_ttl=3600    # Time-to-live in seconds (1 hour)
)
```

### Using the Cache

When you execute a query, the results are automatically cached:

```python
# Execute a query (results will be cached)
result1 = db_manager.run_query(
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age",
    parameters={"min_age": 30}
)

# Execute the same query again (results will be retrieved from cache)
result2 = db_manager.run_query(
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age",
    parameters={"min_age": 30}
)
```

### Cache Control

You can control the caching behavior for individual queries:

```python
# Execute a query without caching
result = db_manager.run_query(
    "MATCH (p:Person) RETURN p.name, p.age",
    use_cache=False
)

# Clear the entire cache
db_manager.clear_cache()

# Clear a specific query from the cache
db_manager.clear_cache_entry(
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age",
    parameters={"min_age": 30}
)
```

### Cache Statistics

You can get statistics about the cache:

```python
# Get cache statistics
stats = db_manager.get_cache_stats()
print(f"Cache size: {stats['size']}")
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Hit ratio: {stats['hit_ratio']:.2f}")
```

## Parameterized Query Templates

Parameterized query templates allow you to define reusable Cypher queries with named parameters, validation, and documentation.

### Creating a Query Template

Here's an example of creating a query template:

```python
from science_data_kit.core.db import QueryTemplate, ParameterDefinition

# Create a query template
person_query_template = QueryTemplate(
    name="get_persons_by_age",
    description="Get persons with age greater than or equal to the specified minimum age",
    query="MATCH (p:Person) WHERE p.age >= $min_age RETURN p.name, p.age ORDER BY p.age",
    parameters=[
        ParameterDefinition(
            name="min_age",
            description="Minimum age",
            type="int",
            required=True,
            default=18,
            validation={"min": 0, "max": 120}
        )
    ],
    result_description="Returns a list of person names and ages"
)

# Register the template with the database manager
db_manager.register_query_template(person_query_template)
```

### Using a Query Template

Once a template is registered, you can use it to execute queries:

```python
# Execute a query using a template
result = db_manager.run_query_template(
    "get_persons_by_age",
    parameters={"min_age": 30}
)

# Print the results
for record in result:
    print(f"Name: {record['p.name']}, Age: {record['p.age']}")
```

### Template Validation

The template automatically validates the parameters:

```python
try:
    # This will raise an exception because min_age is outside the valid range
    result = db_manager.run_query_template(
        "get_persons_by_age",
        parameters={"min_age": 150}
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Template Documentation

You can get documentation for a template:

```python
# Get documentation for a template
doc = db_manager.get_template_documentation("get_persons_by_age")
print(doc)
```

## Query Logging and Performance Metrics

Query logging and performance metrics help you track and analyze query execution times, cache hits/misses, and other performance data.

### Enabling Query Logging

Query logging is enabled by default in the Neo4jManager. You can configure it when creating the manager:

```python
from science_data_kit.core.db import Neo4jManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a database manager with logging enabled
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j",
    enable_logging=True,
    log_level=logging.INFO
)
```

### Query Execution Metrics

You can get metrics for query execution:

```python
# Execute a query
result = db_manager.run_query(
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age",
    parameters={"min_age": 30}
)

# Get metrics for the last query
metrics = db_manager.get_last_query_metrics()
print(f"Query: {metrics['query']}")
print(f"Parameters: {metrics['parameters']}")
print(f"Execution time: {metrics['execution_time']:.2f} ms")
print(f"Result count: {metrics['result_count']}")
print(f"Cached: {metrics['cached']}")
```

### Query History

You can get the history of executed queries:

```python
# Get query history
history = db_manager.get_query_history()
print(f"Query history ({len(history)} entries):")
for entry in history:
    print(f"Query: {entry['query']}")
    print(f"Execution time: {entry['execution_time']:.2f} ms")
    print(f"Timestamp: {entry['timestamp']}")
    print()
```

### Performance Analysis

You can analyze query performance:

```python
# Get performance analysis
analysis = db_manager.analyze_query_performance()
print("Top 5 slowest queries:")
for query, metrics in analysis['slowest_queries'][:5]:
    print(f"Query: {query}")
    print(f"Average execution time: {metrics['avg_execution_time']:.2f} ms")
    print(f"Execution count: {metrics['execution_count']}")
    print()

print("Cache performance:")
print(f"Hit ratio: {analysis['cache_hit_ratio']:.2f}")
print(f"Average execution time with cache: {analysis['avg_execution_time_with_cache']:.2f} ms")
print(f"Average execution time without cache: {analysis['avg_execution_time_without_cache']:.2f} ms")
```

## Pagination for Large Result Sets

Pagination allows you to retrieve large sets of nodes and relationships in smaller chunks, which is more efficient and prevents memory issues.

### Basic Pagination

Here's an example of using pagination:

```python
from science_data_kit.core.db import Paginator

# Create a paginator
paginator = Paginator(
    db_manager=db_manager,
    query="MATCH (p:Person) RETURN p.name, p.age ORDER BY p.age",
    page_size=10
)

# Get the first page
page1 = paginator.get_page(1)
print(f"Page 1 ({len(page1)} records):")
for record in page1:
    print(f"Name: {record['p.name']}, Age: {record['p.age']}")

# Get the second page
page2 = paginator.get_page(2)
print(f"\nPage 2 ({len(page2)} records):")
for record in page2:
    print(f"Name: {record['p.name']}, Age: {record['p.age']}")
```

### Pagination with Parameters

You can use parameters with pagination:

```python
# Create a paginator with parameters
paginator = Paginator(
    db_manager=db_manager,
    query="MATCH (p:Person) WHERE p.age > $min_age RETURN p.name, p.age ORDER BY p.age",
    parameters={"min_age": 30},
    page_size=10
)

# Get the first page
page1 = paginator.get_page(1)
print(f"Page 1 ({len(page1)} records):")
for record in page1:
    print(f"Name: {record['p.name']}, Age: {record['p.age']}")
```

### Pagination Information

You can get information about the pagination:

```python
# Get pagination information
info = paginator.get_pagination_info()
print(f"Total records: {info['total_records']}")
print(f"Total pages: {info['total_pages']}")
print(f"Current page: {info['current_page']}")
print(f"Page size: {info['page_size']}")
print(f"Has next page: {info['has_next_page']}")
print(f"Has previous page: {info['has_previous_page']}")
```

### Iterating Through All Pages

You can iterate through all pages:

```python
# Iterate through all pages
for page_number, page in paginator.iter_pages():
    print(f"Page {page_number} ({len(page)} records):")
    for record in page:
        print(f"Name: {record['p.name']}, Age: {record['p.age']}")
    print()
```

## Advanced Query Techniques

The Science Data Kit supports advanced query techniques for working with Neo4j databases.

### Transactions

You can use transactions to ensure data consistency:

```python
# Start a transaction
with db_manager.transaction() as tx:
    # Execute multiple queries in a transaction
    tx.run("CREATE (p:Person {name: 'Alice', age: 30})")
    tx.run("CREATE (p:Person {name: 'Bob', age: 25})")
    tx.run("CREATE (p:Person {name: 'Charlie', age: 35})")
    
    # If any query fails, the entire transaction is rolled back
    # If all queries succeed, the transaction is committed
```

### Batch Operations

You can use batch operations for better performance:

```python
# Create a batch of nodes
batch_data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

# Execute a batch operation
db_manager.batch_create_nodes(
    label="Person",
    data=batch_data,
    batch_size=100
)
```

### Graph Algorithms

You can use Neo4j's graph algorithms:

```python
# Run a graph algorithm (requires Neo4j Graph Data Science library)
result = db_manager.run_query("""
    CALL gds.pageRank.stream('myGraph')
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).name AS name, score
    ORDER BY score DESC
    LIMIT 10
""")

# Print the results
for record in result:
    print(f"Name: {record['name']}, PageRank Score: {record['score']:.4f}")
```

## Best Practices

Here are some best practices for using the database operations capabilities of the Science Data Kit:

1. **Use Parameterized Queries**: Always use parameterized queries to prevent Cypher injection attacks and improve performance.
2. **Enable Query Caching**: Enable query caching for frequently executed queries to improve performance.
3. **Use Pagination**: Use pagination for large result sets to prevent memory issues and improve performance.
4. **Monitor Query Performance**: Use query logging and performance metrics to identify slow queries and optimize them.
5. **Use Transactions**: Use transactions for operations that need to be atomic.
6. **Optimize Queries**: Write efficient Cypher queries by using appropriate indexes and avoiding unnecessary operations.
7. **Use Batch Operations**: Use batch operations for creating or updating large numbers of nodes or relationships.
8. **Close Connections**: Always close database connections when you're done with them, especially when using connection pools.

## Troubleshooting

Here are some common issues and their solutions:

### Connection Issues

- **Issue**: Unable to connect to the Neo4j database.
  - **Solution**: Check that the Neo4j server is running and that the connection parameters (URI, username, password) are correct. Ensure that the Neo4j server is accessible from your application.

### Query Execution Issues

- **Issue**: Queries are slow or time out.
  - **Solution**: Optimize your queries by adding appropriate indexes, using parameterized queries, and avoiding unnecessary operations. Use query logging and performance metrics to identify slow queries.

### Memory Issues

- **Issue**: Out of memory errors when retrieving large result sets.
  - **Solution**: Use pagination to retrieve large result sets in smaller chunks. Consider using streaming queries for very large result sets.

### Cache Issues

- **Issue**: Cache is not improving performance.
  - **Solution**: Ensure that query caching is enabled and that the cache size and TTL are appropriate for your workload. Use cache statistics to monitor cache performance.

### Transaction Issues

- **Issue**: Transactions are not being committed or rolled back properly.
  - **Solution**: Use the `with` statement with the transaction object to ensure proper handling of transactions. Check for exceptions that might be causing transactions to roll back.

If you encounter other issues, please refer to the SDK documentation or contact support.