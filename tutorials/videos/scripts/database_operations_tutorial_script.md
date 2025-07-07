# Database Operations Tutorial Script

## Introduction (0:00-0:30)
Hello and welcome to this video tutorial on database operations in the Science Data Kit. In this tutorial, we'll explore how to use the database operations functionality to work with Neo4j databases efficiently. We'll cover basic operations, query caching, parameterized query templates, performance metrics, and pagination.

## Prerequisites (0:30-1:00)
Before we begin, make sure you have:
- The Science Data Kit installed
- A Neo4j database running
- Basic knowledge of the Cypher query language

If you need help setting these up, please refer to our installation guide in the documentation.

## Basic Database Operations (1:00-3:30)

### Creating a Connection (1:00-1:30)
First, let's import the necessary modules and create a connection to our Neo4j database:

```python
from science_data_kit.core.db.db_manager import Neo4jManager

# Create a Neo4jManager
db_manager = Neo4jManager()

# Check if connected
if db_manager.is_connected():
    print("Connected to Neo4j.")
else:
    print("Not connected to Neo4j. Please check your connection settings.")
```

### Creating and Querying Data (1:30-2:30)
Now, let's create a test node and query it:

```python
# Create a test node
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

# Query the node
query = "MATCH (n:TestNode {id: $id}) RETURN n.name AS name, n.created AS created"
result = db_manager.execute_query(query, {"id": 1})

for record in result:
    print(f"Name: {record['name']}")
    print(f"Created: {record['created']}")
```

### Working with Results (2:30-3:30)
The SDK provides convenient methods for working with query results:

```python
# Convert query result to DataFrame
df = db_manager.query_to_dataframe(query, {"id": 1})
print("DataFrame Result:")
print(df)

# Get a single value
count_query = "MATCH (n:TestNode) RETURN count(n) AS count"
count = db_manager.query_to_value(count_query)
print(f"Number of TestNode nodes: {count}")
```

## Query Caching (3:30-5:30)

### Understanding Query Caching (3:30-4:00)
Query caching can significantly improve performance for frequently executed queries. Let's see how it works:

```python
# Create some test data
create_query = """
UNWIND range(1, 100) AS id
CREATE (n:CacheTest {
    id: id,
    name: 'Node ' + id,
    value: id * 10
})
"""
db_manager.execute_query(create_query)
```

### Comparing Cached vs. Non-Cached Queries (4:00-5:30)
Let's compare the performance of cached and non-cached queries:

```python
import time

# Define a query to cache
query = """
MATCH (n:CacheTest)
WHERE n.id >= $min_id AND n.id <= $max_id
RETURN n.id AS id, n.name AS name, n.value AS value
ORDER BY n.id
"""

# Execute without caching
start_time = time.time()
result1 = db_manager.execute_query(
    query,
    {"min_id": 1, "max_id": 50},
    enable_cache=False
)
end_time = time.time()
print(f"Execution time without caching: {(end_time - start_time) * 1000:.2f} ms")

# Execute with caching (first run)
start_time = time.time()
result2 = db_manager.execute_query(
    query,
    {"min_id": 1, "max_id": 50},
    enable_cache=True
)
end_time = time.time()
print(f"Execution time with caching (first run): {(end_time - start_time) * 1000:.2f} ms")

# Execute with caching (second run)
start_time = time.time()
result3 = db_manager.execute_query(
    query,
    {"min_id": 1, "max_id": 50},
    enable_cache=True
)
end_time = time.time()
print(f"Execution time with caching (second run): {(end_time - start_time) * 1000:.2f} ms")
```

Notice how the second run with caching is significantly faster!

## Parameterized Query Templates (5:30-8:00)

### Creating Flexible Queries (5:30-6:30)
Parameterized query templates allow you to create reusable and flexible database queries:

```python
# Create some test data
create_query = """
CREATE (alice:Person {name: 'Alice', age: 30, department: 'HR'})
CREATE (bob:Person {name: 'Bob', age: 35, department: 'IT'})
CREATE (charlie:Person {name: 'Charlie', age: 40, department: 'Finance'})
CREATE (david:Person {name: 'David', age: 45, department: 'IT'})
CREATE (eve:Person {name: 'Eve', age: 50, department: 'HR'})
"""
db_manager.execute_query(create_query)

# Define a parameterized query template
find_by_department_template = """
MATCH (p:Person)
WHERE p.department = $department
RETURN p.name AS name, p.age AS age, p.department AS department
ORDER BY p.name
"""

# Use the template with different parameters
hr_people = db_manager.query_to_dataframe(
    find_by_department_template,
    {"department": "HR"}
)
print("HR Department:")
print(hr_people)
```

### Advanced Template Techniques (6:30-8:00)
You can create more complex templates with optional parameters:

```python
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
all_people = find_people()
it_people = find_people(department="IT")
middle_aged = find_people(min_age=35, max_age=45)
hr_over_40 = find_people(department="HR", min_age=40)
```

## Query Metrics (8:00-10:00)

### Tracking Query Performance (8:00-9:00)
The SDK provides tools for tracking and analyzing query performance:

```python
from science_data_kit.core.db.metrics import QueryMetrics

# Create a QueryMetrics instance
metrics = QueryMetrics()

# Define a query to measure
query = """
MATCH (n:MetricsTest)
WHERE n.id >= $min_id AND n.id <= $max_id
RETURN n.id AS id, n.name AS name, n.value AS value
ORDER BY n.id
"""

# Track the first query
with metrics.track("query1"):
    result1 = db_manager.execute_query(
        query,
        {"min_id": 1, "max_id": 100}
    )

# Track the second query
with metrics.track("query2"):
    result2 = db_manager.execute_query(
        query,
        {"min_id": 101, "max_id": 200}
    )
```

### Analyzing Query Metrics (9:00-10:00)
Let's analyze the metrics we've collected:

```python
# Get the metrics
print("Query Metrics:")
for query_name, stats in metrics.get_stats().items():
    print(f"Query: {query_name}")
    print(f"  Execution count: {stats['count']}")
    print(f"  Total time: {stats['total_time']:.4f} seconds")
    print(f"  Average time: {stats['avg_time']:.4f} seconds")
    print(f"  Min time: {stats['min_time']:.4f} seconds")
    print(f"  Max time: {stats['max_time']:.4f} seconds")
```

These metrics can help you identify performance bottlenecks and optimize your queries.

## Pagination (10:00-12:30)

### Handling Large Result Sets (10:00-11:00)
When working with large datasets, pagination is essential for efficient data retrieval:

```python
# Count the total number of nodes
count = db_manager.count_nodes_by_label("PaginationTest")
print(f"Total number of PaginationTest nodes: {count}")

# Fetch nodes with pagination
page_size = 50
total_pages = (count + page_size - 1) // page_size  # Ceiling division

for page in range(1, total_pages + 1):
    result = db_manager.fetch_nodes_paginated(
        label="PaginationTest",
        page=page,
        page_size=page_size,
        order_by="id",
        properties=["id", "name", "value"]
    )
    
    print(f"Page {page} contains {len(result['nodes'])} nodes.")
```

### Paginating Relationships (11:00-12:30)
You can also paginate relationships:

```python
# Count relationships
rel_count = db_manager.count_relationships(
    source_label="PaginationTest",
    relationship_type="RELATES_TO",
    target_label="PaginationTest"
)

# Fetch relationships with pagination
rel_page_size = 25
rel_total_pages = (rel_count + rel_page_size - 1) // rel_page_size

for page in range(1, rel_total_pages + 1):
    result = db_manager.fetch_relationships_paginated(
        source_label="PaginationTest",
        relationship_type="RELATES_TO",
        target_label="PaginationTest",
        page=page,
        page_size=rel_page_size,
        order_by="source.id"
    )
    
    print(f"Page {page} contains {len(result['relationships'])} relationships.")
```

## Conclusion (12:30-13:00)
In this tutorial, we've explored the database operations functionality in the Science Data Kit:

1. Basic database operations for connecting to Neo4j and executing queries
2. Query caching to improve performance for frequently executed queries
3. Parameterized query templates for creating flexible and reusable queries
4. Query metrics for tracking and analyzing performance
5. Pagination for efficiently handling large result sets

These tools will help you work efficiently with Neo4j databases in your Science Data Kit applications.

Thank you for watching this tutorial. For more information, please refer to the documentation and other tutorials in the Science Data Kit.