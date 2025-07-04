"""
Database Operations Tutorial for Science Data Kit

This tutorial demonstrates how to use the database operations functionality
in the Science Data Kit, including query caching, parameterized query templates,
query logging and performance metrics, and pagination for large result sets.
"""

import os
import pandas as pd
import numpy as np
import time
from pathlib import Path
import tempfile

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.db.cache import cached_query
from science_data_kit.core.db.metrics import QueryMetrics


def example_basic_operations():
    """
    Example of basic database operations.
    
    This function demonstrates how to connect to a Neo4j database,
    execute queries, and work with the results.
    """
    print("\n=== Basic Database Operations Example ===\n")
    
    # Create a Neo4jManager
    try:
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping basic operations example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Get connection information
        print("Connection Information:")
        print(f"Active connection: {db_manager.get_active_connection_name()}")
        print(f"Available connections: {db_manager.get_connection_names()}")
        print()
        
        # Create a test node
        print("Creating a test node...")
        query = """
        CREATE (n:TestNode {
            id: $id,
            name: $name,
            created: datetime()
        })
        RETURN n
        """
        
        result = db_manager.execute_query(
            query,
            {
                "id": 1,
                "name": "Test Node"
            }
        )
        
        print("Query executed successfully.")
        print(f"Result: {result}")
        print()
        
        # Query the node
        print("Querying the test node...")
        query = "MATCH (n:TestNode {id: $id}) RETURN n.name AS name, n.created AS created"
        result = db_manager.execute_query(query, {"id": 1})
        
        print("Query Result:")
        for record in result:
            print(f"Name: {record['name']}")
            print(f"Created: {record['created']}")
        print()
        
        # Convert query result to DataFrame
        print("Converting query result to DataFrame...")
        df = db_manager.query_to_dataframe(query, {"id": 1})
        
        print("DataFrame Result:")
        print(df)
        print()
        
        # Get a single value
        print("Getting a single value...")
        count_query = "MATCH (n:TestNode) RETURN count(n) AS count"
        count = db_manager.query_to_value(count_query)
        
        print(f"Number of TestNode nodes: {count}")
        print()
        
        # Clean up
        print("Cleaning up test data...")
        db_manager.execute_query("MATCH (n:TestNode) DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in basic operations example: {e}")
        print("Skipping basic operations example.")
    
    return


def example_query_caching():
    """
    Example of query caching.
    
    This function demonstrates how to use the query caching functionality
    to improve performance for frequently executed queries.
    """
    print("\n=== Query Caching Example ===\n")
    
    # Create a Neo4jManager
    try:
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping query caching example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Create some test data
        print("Creating test data...")
        create_query = """
        UNWIND range(1, 100) AS id
        CREATE (n:CacheTest {
            id: id,
            name: 'Node ' + id,
            value: id * 10
        })
        """
        
        db_manager.execute_query(create_query)
        print("Created 100 test nodes.")
        print()
        
        # Define a query to cache
        query = """
        MATCH (n:CacheTest)
        WHERE n.id >= $min_id AND n.id <= $max_id
        RETURN n.id AS id, n.name AS name, n.value AS value
        ORDER BY n.id
        """
        
        # Execute the query without caching
        print("Executing query without caching...")
        start_time = time.time()
        result1 = db_manager.execute_query(
            query,
            {"min_id": 1, "max_id": 50},
            enable_cache=False
        )
        end_time = time.time()
        
        print(f"Query returned {len(result1)} records.")
        print(f"Execution time without caching: {(end_time - start_time) * 1000:.2f} ms")
        print()
        
        # Execute the query with caching
        print("Executing query with caching (first run)...")
        start_time = time.time()
        result2 = db_manager.execute_query(
            query,
            {"min_id": 1, "max_id": 50},
            enable_cache=True
        )
        end_time = time.time()
        
        print(f"Query returned {len(result2)} records.")
        print(f"Execution time with caching (first run): {(end_time - start_time) * 1000:.2f} ms")
        print()
        
        # Execute the cached query again
        print("Executing query with caching (second run)...")
        start_time = time.time()
        result3 = db_manager.execute_query(
            query,
            {"min_id": 1, "max_id": 50},
            enable_cache=True
        )
        end_time = time.time()
        
        print(f"Query returned {len(result3)} records.")
        print(f"Execution time with caching (second run): {(end_time - start_time) * 1000:.2f} ms")
        print("Note: The second run should be significantly faster due to caching.")
        print()
        
        # Execute the query with different parameters
        print("Executing query with different parameters...")
        start_time = time.time()
        result4 = db_manager.execute_query(
            query,
            {"min_id": 51, "max_id": 100},
            enable_cache=True
        )
        end_time = time.time()
        
        print(f"Query returned {len(result4)} records.")
        print(f"Execution time with different parameters: {(end_time - start_time) * 1000:.2f} ms")
        print("Note: This should be slower as it's not in the cache yet.")
        print()
        
        # Clean up
        print("Cleaning up test data...")
        db_manager.execute_query("MATCH (n:CacheTest) DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in query caching example: {e}")
        print("Skipping query caching example.")
    
    return


def example_parameterized_query_templates():
    """
    Example of parameterized query templates.
    
    This function demonstrates how to use parameterized query templates
    to create reusable and flexible database queries.
    """
    print("\n=== Parameterized Query Templates Example ===\n")
    
    # Create a Neo4jManager
    try:
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping parameterized query templates example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Create some test data
        print("Creating test data...")
        create_query = """
        CREATE (alice:Person {name: 'Alice', age: 30, department: 'HR'})
        CREATE (bob:Person {name: 'Bob', age: 35, department: 'IT'})
        CREATE (charlie:Person {name: 'Charlie', age: 40, department: 'Finance'})
        CREATE (david:Person {name: 'David', age: 45, department: 'IT'})
        CREATE (eve:Person {name: 'Eve', age: 50, department: 'HR'})
        
        CREATE (alice)-[:KNOWS {since: 2010}]->(bob)
        CREATE (alice)-[:KNOWS {since: 2012}]->(charlie)
        CREATE (bob)-[:KNOWS {since: 2015}]->(david)
        CREATE (charlie)-[:KNOWS {since: 2018}]->(eve)
        CREATE (david)-[:KNOWS {since: 2020}]->(eve)
        """
        
        db_manager.execute_query(create_query)
        print("Created test data with Person nodes and KNOWS relationships.")
        print()
        
        # Define a parameterized query template for finding people by department
        find_by_department_template = """
        MATCH (p:Person)
        WHERE p.department = $department
        RETURN p.name AS name, p.age AS age, p.department AS department
        ORDER BY p.name
        """
        
        # Use the template with different parameters
        print("Finding people in the HR department...")
        hr_people = db_manager.query_to_dataframe(
            find_by_department_template,
            {"department": "HR"}
        )
        
        print("HR Department:")
        print(hr_people)
        print()
        
        print("Finding people in the IT department...")
        it_people = db_manager.query_to_dataframe(
            find_by_department_template,
            {"department": "IT"}
        )
        
        print("IT Department:")
        print(it_people)
        print()
        
        # Define a more complex parameterized query template
        find_connections_template = """
        MATCH (p:Person {name: $name})-[r:KNOWS]->(friend:Person)
        RETURN friend.name AS friend_name, friend.department AS friend_department, r.since AS knows_since
        ORDER BY r.since
        """
        
        # Use the template with different parameters
        print("Finding Alice's connections...")
        alice_connections = db_manager.query_to_dataframe(
            find_connections_template,
            {"name": "Alice"}
        )
        
        print("Alice's Connections:")
        print(alice_connections)
        print()
        
        print("Finding Bob's connections...")
        bob_connections = db_manager.query_to_dataframe(
            find_connections_template,
            {"name": "Bob"}
        )
        
        print("Bob's Connections:")
        print(bob_connections)
        print()
        
        # Define a template with optional parameters
        find_people_template = """
        MATCH (p:Person)
        WHERE 1=1
        $department_filter
        $age_filter
        RETURN p.name AS name, p.age AS age, p.department AS department
        ORDER BY p.name
        """
        
        # Function to execute the query with optional filters
        def find_people(department=None, min_age=None, max_age=None):
            # Build the query parameters
            params = {}
            
            # Build the department filter
            department_filter = ""
            if department:
                department_filter = "AND p.department = $department"
                params["department"] = department
            
            # Build the age filter
            age_filter = ""
            if min_age is not None and max_age is not None:
                age_filter = "AND p.age >= $min_age AND p.age <= $max_age"
                params["min_age"] = min_age
                params["max_age"] = max_age
            elif min_age is not None:
                age_filter = "AND p.age >= $min_age"
                params["min_age"] = min_age
            elif max_age is not None:
                age_filter = "AND p.age <= $max_age"
                params["max_age"] = max_age
            
            # Replace the placeholders in the template
            query = find_people_template.replace("$department_filter", department_filter)
            query = query.replace("$age_filter", age_filter)
            
            # Execute the query
            return db_manager.query_to_dataframe(query, params)
        
        # Use the function with different combinations of parameters
        print("Finding all people...")
        all_people = find_people()
        print("All People:")
        print(all_people)
        print()
        
        print("Finding people in the IT department...")
        it_people = find_people(department="IT")
        print("IT Department:")
        print(it_people)
        print()
        
        print("Finding people aged 35-45...")
        middle_aged = find_people(min_age=35, max_age=45)
        print("People aged 35-45:")
        print(middle_aged)
        print()
        
        print("Finding people in HR aged over 40...")
        hr_over_40 = find_people(department="HR", min_age=40)
        print("HR Department, Age > 40:")
        print(hr_over_40)
        print()
        
        # Clean up
        print("Cleaning up test data...")
        db_manager.execute_query("MATCH (n:Person) DETACH DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in parameterized query templates example: {e}")
        print("Skipping parameterized query templates example.")
    
    return


def example_query_metrics():
    """
    Example of query logging and performance metrics.
    
    This function demonstrates how to use the query metrics functionality
    to track and analyze query performance.
    """
    print("\n=== Query Metrics Example ===\n")
    
    # Create a Neo4jManager
    try:
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping query metrics example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Create some test data
        print("Creating test data...")
        create_query = """
        UNWIND range(1, 1000) AS id
        CREATE (n:MetricsTest {
            id: id,
            name: 'Node ' + id,
            value: id * 10
        })
        """
        
        db_manager.execute_query(create_query)
        print("Created 1000 test nodes.")
        print()
        
        # Create a QueryMetrics instance
        metrics = QueryMetrics()
        
        # Define a query to measure
        query = """
        MATCH (n:MetricsTest)
        WHERE n.id >= $min_id AND n.id <= $max_id
        RETURN n.id AS id, n.name AS name, n.value AS value
        ORDER BY n.id
        """
        
        # Execute the query with metrics tracking
        print("Executing query with metrics tracking...")
        
        # Track the first query
        with metrics.track("query1"):
            result1 = db_manager.execute_query(
                query,
                {"min_id": 1, "max_id": 100}
            )
        
        print(f"Query 1 returned {len(result1)} records.")
        print()
        
        # Track the second query
        with metrics.track("query2"):
            result2 = db_manager.execute_query(
                query,
                {"min_id": 101, "max_id": 200}
            )
        
        print(f"Query 2 returned {len(result2)} records.")
        print()
        
        # Track the third query (with a larger result set)
        with metrics.track("query3"):
            result3 = db_manager.execute_query(
                query,
                {"min_id": 201, "max_id": 500}
            )
        
        print(f"Query 3 returned {len(result3)} records.")
        print()
        
        # Get the metrics
        print("Query Metrics:")
        for query_name, stats in metrics.get_stats().items():
            print(f"Query: {query_name}")
            print(f"  Execution count: {stats['count']}")
            print(f"  Total time: {stats['total_time']:.4f} seconds")
            print(f"  Average time: {stats['avg_time']:.4f} seconds")
            print(f"  Min time: {stats['min_time']:.4f} seconds")
            print(f"  Max time: {stats['max_time']:.4f} seconds")
            print()
        
        # Execute the first query again to demonstrate multiple executions
        print("Executing query 1 again...")
        
        with metrics.track("query1"):
            result4 = db_manager.execute_query(
                query,
                {"min_id": 1, "max_id": 100}
            )
        
        print(f"Query 1 (second execution) returned {len(result4)} records.")
        print()
        
        # Get the updated metrics
        print("Updated Query Metrics:")
        for query_name, stats in metrics.get_stats().items():
            print(f"Query: {query_name}")
            print(f"  Execution count: {stats['count']}")
            print(f"  Total time: {stats['total_time']:.4f} seconds")
            print(f"  Average time: {stats['avg_time']:.4f} seconds")
            print(f"  Min time: {stats['min_time']:.4f} seconds")
            print(f"  Max time: {stats['max_time']:.4f} seconds")
            print()
        
        # Clean up
        print("Cleaning up test data...")
        db_manager.execute_query("MATCH (n:MetricsTest) DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in query metrics example: {e}")
        print("Skipping query metrics example.")
    
    return


def example_pagination():
    """
    Example of pagination for large result sets.
    
    This function demonstrates how to use pagination to efficiently
    handle large result sets from database queries.
    """
    print("\n=== Pagination Example ===\n")
    
    # Create a Neo4jManager
    try:
        db_manager = Neo4jManager()
        
        # Check if connected
        if not db_manager.is_connected():
            print("Not connected to Neo4j. Trying to connect...")
            try:
                db_manager._connect()
            except Exception as e:
                print(f"Could not connect to Neo4j: {e}")
                print("Skipping pagination example.")
                return
        
        print("Connected to Neo4j.")
        print()
        
        # Create some test data
        print("Creating test data...")
        create_query = """
        UNWIND range(1, 200) AS id
        CREATE (n:PaginationTest {
            id: id,
            name: 'Node ' + id,
            value: id * 10
        })
        """
        
        db_manager.execute_query(create_query)
        print("Created 200 test nodes.")
        print()
        
        # Count the total number of nodes
        count = db_manager.count_nodes_by_label("PaginationTest")
        print(f"Total number of PaginationTest nodes: {count}")
        print()
        
        # Fetch nodes with pagination
        page_size = 50
        total_pages = (count + page_size - 1) // page_size  # Ceiling division
        
        print(f"Fetching nodes with pagination (page size: {page_size}, total pages: {total_pages})...")
        print()
        
        for page in range(1, total_pages + 1):
            print(f"Fetching page {page} of {total_pages}...")
            
            result = db_manager.fetch_nodes_paginated(
                label="PaginationTest",
                page=page,
                page_size=page_size,
                order_by="id",
                properties=["id", "name", "value"]
            )
            
            print(f"Page {page} contains {len(result['nodes'])} nodes.")
            
            # Print the first and last node in the page
            if result['nodes']:
                first_node = result['nodes'][0]
                last_node = result['nodes'][-1]
                
                print(f"  First node: ID={first_node['properties']['id']}, Name={first_node['properties']['name']}")
                print(f"  Last node: ID={last_node['properties']['id']}, Name={last_node['properties']['name']}")
            
            print()
        
        # Demonstrate relationship pagination
        print("Creating test relationships...")
        create_rels_query = """
        MATCH (n:PaginationTest)
        WHERE n.id <= 100
        MATCH (m:PaginationTest)
        WHERE m.id > 100 AND m.id <= 200
        WITH n, m
        WHERE n.id + 100 = m.id
        CREATE (n)-[:RELATES_TO {strength: n.id * 0.1}]->(m)
        """
        
        db_manager.execute_query(create_rels_query)
        print("Created 100 test relationships.")
        print()
        
        # Count relationships
        rel_count = db_manager.count_relationships(
            source_label="PaginationTest",
            relationship_type="RELATES_TO",
            target_label="PaginationTest"
        )
        
        print(f"Total number of RELATES_TO relationships: {rel_count}")
        print()
        
        # Fetch relationships with pagination
        rel_page_size = 25
        rel_total_pages = (rel_count + rel_page_size - 1) // rel_page_size  # Ceiling division
        
        print(f"Fetching relationships with pagination (page size: {rel_page_size}, total pages: {rel_total_pages})...")
        print()
        
        for page in range(1, rel_total_pages + 1):
            print(f"Fetching relationship page {page} of {rel_total_pages}...")
            
            result = db_manager.fetch_relationships_paginated(
                source_label="PaginationTest",
                relationship_type="RELATES_TO",
                target_label="PaginationTest",
                page=page,
                page_size=rel_page_size,
                order_by="source.id"
            )
            
            print(f"Page {page} contains {len(result['relationships'])} relationships.")
            
            # Print the first and last relationship in the page
            if result['relationships']:
                first_rel = result['relationships'][0]
                last_rel = result['relationships'][-1]
                
                print(f"  First relationship: Source ID={first_rel['source_id']}, Target ID={first_rel['target_id']}")
                print(f"  Last relationship: Source ID={last_rel['source_id']}, Target ID={last_rel['target_id']}")
            
            print()
        
        # Clean up
        print("Cleaning up test data...")
        db_manager.execute_query("MATCH (n:PaginationTest) DETACH DELETE n")
        print("Cleanup complete.")
        print()
        
    except Exception as e:
        print(f"Error in pagination example: {e}")
        print("Skipping pagination example.")
    
    return


def run_tutorial():
    """Run all examples in the tutorial."""
    print("=== Database Operations Tutorial ===")
    print("This tutorial demonstrates how to use the database operations functionality")
    print("in the Science Data Kit, including query caching, parameterized query templates,")
    print("query logging and performance metrics, and pagination for large result sets.")
    print()
    
    # Run the examples
    example_basic_operations()
    example_query_caching()
    example_parameterized_query_templates()
    example_query_metrics()
    example_pagination()
    
    print("Tutorial complete!")


if __name__ == "__main__":
    run_tutorial()