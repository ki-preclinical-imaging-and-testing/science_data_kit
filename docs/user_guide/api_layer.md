# API Layer Guide

## Overview

The Science Data Kit provides a comprehensive API layer that allows you to access SDK functionality through RESTful endpoints, client libraries, and a command-line interface. This guide explains how to use the SDK's API features, including RESTful endpoints, authentication and authorization, API documentation, rate limiting and throttling, client libraries, and the command-line interface.

## Table of Contents

1. [Introduction](#introduction)
2. [RESTful API Endpoints](#restful-api-endpoints)
3. [Authentication and Authorization](#authentication-and-authorization)
4. [API Documentation](#api-documentation)
5. [Rate Limiting and Throttling](#rate-limiting-and-throttling)
6. [Client Libraries](#client-libraries)
7. [Command-Line Interface](#command-line-interface)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

The API layer of the Science Data Kit provides a unified interface for accessing SDK functionality from various platforms and programming languages. It includes:

- **RESTful API Endpoints**: Access SDK functionality through HTTP requests
- **Authentication and Authorization**: Secure your API with token-based authentication and role-based access control
- **API Documentation**: Access comprehensive API documentation using Swagger UI
- **Rate Limiting and Throttling**: Control API usage with configurable rate limiting
- **Client Libraries**: Use Python and JavaScript client libraries for interacting with the SDK API
- **Command-Line Interface**: Access SDK functionality from the command line

These features make it easy to integrate the Science Data Kit with your existing systems and workflows, regardless of the programming language or platform you're using.

## RESTful API Endpoints

The Science Data Kit provides a set of RESTful API endpoints for accessing SDK functionality.

### Base URL

The base URL for the API is:

```
http://<host>:<port>/api/v1
```

Where `<host>` is the hostname or IP address of the server running the SDK, and `<port>` is the port number (default: 8000).

### Available Endpoints

The API provides the following endpoints:

#### Session Management

- `GET /sessions`: Get a list of all sessions
- `GET /sessions/{session_id}`: Get details of a specific session
- `POST /sessions`: Create a new session
- `PUT /sessions/{session_id}`: Update a session
- `DELETE /sessions/{session_id}`: Delete a session

#### Data Sources

- `GET /data_sources`: Get a list of all data sources
- `GET /data_sources/{source_id}`: Get details of a specific data source
- `POST /data_sources`: Create a new data source
- `PUT /data_sources/{source_id}`: Update a data source
- `DELETE /data_sources/{source_id}`: Delete a data source

#### Data Transformation

- `GET /pipelines`: Get a list of all transformation pipelines
- `GET /pipelines/{pipeline_id}`: Get details of a specific pipeline
- `POST /pipelines`: Create a new pipeline
- `PUT /pipelines/{pipeline_id}`: Update a pipeline
- `DELETE /pipelines/{pipeline_id}`: Delete a pipeline
- `POST /pipelines/{pipeline_id}/execute`: Execute a pipeline

#### Database Operations

- `POST /query`: Execute a Cypher query
- `GET /templates`: Get a list of all query templates
- `GET /templates/{template_id}`: Get details of a specific query template
- `POST /templates/{template_id}/execute`: Execute a query template

#### Data Modeling

- `GET /schemas`: Get a list of all entity schemas
- `GET /schemas/{schema_id}`: Get details of a specific schema
- `POST /schemas`: Create a new schema
- `PUT /schemas/{schema_id}`: Update a schema
- `DELETE /schemas/{schema_id}`: Delete a schema

#### Integration

- `GET /integrations`: Get a list of all integration providers
- `GET /integrations/{provider_id}`: Get details of a specific integration provider
- `POST /integrations/{provider_id}/authenticate`: Authenticate with an integration provider
- `GET /integrations/{provider_id}/resources`: Get resources from an integration provider

### Making API Requests

You can make API requests using any HTTP client. Here's an example using `curl`:

```bash
# Get a list of all sessions
curl -X GET "http://localhost:8000/api/v1/sessions" \
     -H "Authorization: Bearer <your_token>"

# Create a new session
curl -X POST "http://localhost:8000/api/v1/sessions" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Session", "description": "A sample session"}'

# Execute a Cypher query
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"query": "MATCH (n:Person) RETURN n.name, n.age", "parameters": {}}'
```

### Response Format

API responses are returned in JSON format. A typical response has the following structure:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

In case of an error, the response will have the following structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  }
}
```

## Authentication and Authorization

The Science Data Kit API uses token-based authentication and role-based access control to secure API endpoints.

### Token-Based Authentication

To access the API, you need to obtain an authentication token:

```bash
# Obtain an authentication token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

The response will include an access token:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "message": "Token generated successfully"
}
```

You can then use this token to authenticate API requests by including it in the `Authorization` header:

```bash
curl -X GET "http://localhost:8000/api/v1/sessions" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Role-Based Access Control

The API uses role-based access control to restrict access to certain endpoints. The following roles are available:

- **Admin**: Full access to all endpoints
- **User**: Access to most endpoints, but cannot create, update, or delete certain resources
- **ReadOnly**: Read-only access to endpoints

You can check your current role:

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
     -H "Authorization: Bearer <your_token>"
```

The response will include your role:

```json
{
  "success": true,
  "data": {
    "username": "your_username",
    "role": "user",
    "permissions": [
      "read:sessions",
      "write:sessions",
      "read:data_sources",
      "write:data_sources",
      // ...
    ]
  },
  "message": "User information retrieved successfully"
}
```

## API Documentation

The Science Data Kit provides comprehensive API documentation using Swagger UI.

### Accessing Swagger UI

You can access the Swagger UI documentation at:

```
http://<host>:<port>/api/docs
```

The Swagger UI provides a user-friendly interface for exploring the API, including:

- A list of all available endpoints
- Request and response schemas
- Example requests and responses
- The ability to try out API endpoints directly from the UI

### OpenAPI Specification

The API documentation is based on the OpenAPI Specification (formerly known as Swagger). You can access the raw OpenAPI specification at:

```
http://<host>:<port>/api/openapi.json
```

This specification can be used with various tools for generating client code, testing API endpoints, and more.

## Rate Limiting and Throttling

The Science Data Kit API includes rate limiting and throttling to prevent abuse and ensure fair usage.

### Rate Limits

The API enforces the following rate limits:

- **Anonymous users**: 10 requests per minute
- **Authenticated users**: 60 requests per minute
- **Admin users**: 120 requests per minute

When you exceed the rate limit, the API will return a `429 Too Many Requests` response with a `Retry-After` header indicating how many seconds to wait before making another request.

### Monitoring Rate Limits

You can monitor your current rate limit status using the headers returned with each API response:

- `X-RateLimit-Limit`: The maximum number of requests you can make per minute
- `X-RateLimit-Remaining`: The number of requests remaining in the current minute
- `X-RateLimit-Reset`: The time at which the rate limit will reset, in Unix epoch seconds

### Throttling Configuration

If you're running your own instance of the Science Data Kit, you can configure rate limiting and throttling in the API settings:

```python
from science_data_kit.core.api import APISettings

# Configure API settings
api_settings = APISettings(
    rate_limit_anonymous=10,
    rate_limit_user=60,
    rate_limit_admin=120,
    enable_throttling=True
)
```

## Client Libraries

The Science Data Kit provides client libraries for Python and JavaScript, making it easy to interact with the API from your applications.

### Python Client Library

The Python client library provides a convenient interface for accessing the API:

```python
from science_data_kit.client import SDKClient

# Create a client
client = SDKClient(
    base_url="http://localhost:8000/api/v1",
    username="your_username",
    password="your_password"
)

# Get a list of all sessions
sessions = client.sessions.list()
print(f"Found {len(sessions)} sessions")

# Create a new session
new_session = client.sessions.create(
    name="My Session",
    description="A sample session"
)
print(f"Created session with ID: {new_session.id}")

# Execute a Cypher query
result = client.query.execute(
    query="MATCH (n:Person) RETURN n.name, n.age",
    parameters={}
)
for record in result:
    print(f"Name: {record['n.name']}, Age: {record['n.age']}")
```

#### Client-Side Caching

The Python client library supports client-side caching to improve performance:

```python
from science_data_kit.client import SDKClient, CacheSettings

# Create a client with caching enabled
client = SDKClient(
    base_url="http://localhost:8000/api/v1",
    username="your_username",
    password="your_password",
    cache_settings=CacheSettings(
        enable_caching=True,
        cache_size=1000,
        cache_ttl=3600
    )
)

# Execute a query (results will be cached)
result1 = client.query.execute(
    query="MATCH (n:Person) RETURN n.name, n.age",
    parameters={}
)

# Execute the same query again (results will be retrieved from cache)
result2 = client.query.execute(
    query="MATCH (n:Person) RETURN n.name, n.age",
    parameters={}
)
```

### JavaScript Client Library

The JavaScript client library provides a similar interface for accessing the API from JavaScript applications:

```javascript
import { SDKClient } from 'science-data-kit-client';

// Create a client
const client = new SDKClient({
  baseUrl: 'http://localhost:8000/api/v1',
  username: 'your_username',
  password: 'your_password'
});

// Get a list of all sessions
client.sessions.list()
  .then(sessions => {
    console.log(`Found ${sessions.length} sessions`);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Create a new session
client.sessions.create({
  name: 'My Session',
  description: 'A sample session'
})
  .then(newSession => {
    console.log(`Created session with ID: ${newSession.id}`);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Execute a Cypher query
client.query.execute({
  query: 'MATCH (n:Person) RETURN n.name, n.age',
  parameters: {}
})
  .then(result => {
    result.forEach(record => {
      console.log(`Name: ${record['n.name']}, Age: ${record['n.age']}`);
    });
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### Client-Side Caching

The JavaScript client library also supports client-side caching:

```javascript
import { SDKClient, CacheSettings } from 'science-data-kit-client';

// Create a client with caching enabled
const client = new SDKClient({
  baseUrl: 'http://localhost:8000/api/v1',
  username: 'your_username',
  password: 'your_password',
  cacheSettings: {
    enableCaching: true,
    cacheSize: 1000,
    cacheTtl: 3600
  }
});
```

## Command-Line Interface

The Science Data Kit provides a command-line interface (CLI) for accessing SDK functionality from the command line.

### Installation

The CLI is included with the Science Data Kit package. You can also install it separately:

```bash
pip install science-data-kit-cli
```

### Configuration

Before using the CLI, you need to configure it with your API credentials:

```bash
sdk config set api.url http://localhost:8000/api/v1
sdk config set auth.username your_username
sdk config set auth.password your_password
```

### Basic Usage

The CLI provides commands for accessing various SDK features:

```bash
# Get a list of all sessions
sdk sessions list

# Create a new session
sdk sessions create --name "My Session" --description "A sample session"

# Execute a Cypher query
sdk query execute "MATCH (n:Person) RETURN n.name, n.age"

# Get a list of all data sources
sdk data-sources list

# Create a new data source
sdk data-sources create --name "My Data Source" --type "csv" --path "/path/to/data.csv"

# Execute a pipeline
sdk pipelines execute --id 123
```

### Output Formats

The CLI supports various output formats:

```bash
# Output as JSON
sdk sessions list --format json

# Output as CSV
sdk query execute "MATCH (n:Person) RETURN n.name, n.age" --format csv

# Output as table
sdk data-sources list --format table
```

### Scripting

You can use the CLI in scripts:

```bash
#!/bin/bash

# Create a session
SESSION_ID=$(sdk sessions create --name "My Session" --description "A sample session" --format json | jq -r '.id')

# Create a data source
DATA_SOURCE_ID=$(sdk data-sources create --name "My Data Source" --type "csv" --path "/path/to/data.csv" --format json | jq -r '.id')

# Create a pipeline
PIPELINE_ID=$(sdk pipelines create --name "My Pipeline" --source-id "$DATA_SOURCE_ID" --format json | jq -r '.id')

# Execute the pipeline
sdk pipelines execute --id "$PIPELINE_ID"

# Execute a query
sdk query execute "MATCH (n:Person) RETURN count(n) AS count" --format json | jq -r '.data[0].count'
```

## Best Practices

Here are some best practices for using the API layer of the Science Data Kit:

1. **Use Authentication**: Always use authentication to secure your API requests.
2. **Handle Rate Limits**: Monitor rate limit headers and implement backoff strategies to handle rate limiting.
3. **Use Client Libraries**: Use the provided client libraries instead of making raw HTTP requests when possible.
4. **Enable Caching**: Enable client-side caching to improve performance for frequently used queries.
5. **Validate Input**: Validate input data before sending it to the API to prevent errors.
6. **Handle Errors**: Implement proper error handling to make your applications more robust.
7. **Use Pagination**: Use pagination for endpoints that return large result sets.
8. **Minimize Requests**: Minimize the number of API requests by batching operations when possible.
9. **Use HTTPS**: Use HTTPS to encrypt API traffic and protect sensitive data.
10. **Keep Tokens Secure**: Store authentication tokens securely and never expose them in client-side code.

## Troubleshooting

Here are some common issues and their solutions:

### Authentication Issues

- **Issue**: Unable to obtain an authentication token.
  - **Solution**: Check that your username and password are correct. Ensure that the API server is running and accessible.

### Rate Limiting Issues

- **Issue**: Receiving `429 Too Many Requests` responses.
  - **Solution**: Implement a backoff strategy to handle rate limiting. Monitor the `X-RateLimit-*` headers to track your rate limit status.

### Connection Issues

- **Issue**: Unable to connect to the API server.
  - **Solution**: Check that the API server is running and accessible. Verify that the base URL is correct.

### Query Execution Issues

- **Issue**: Cypher queries fail to execute.
  - **Solution**: Check that your Cypher syntax is correct. Ensure that the database is running and accessible.

### Client Library Issues

- **Issue**: Client library throws unexpected errors.
  - **Solution**: Check that you're using the latest version of the client library. Verify that your code matches the examples in the documentation.

### CLI Issues

- **Issue**: CLI commands fail to execute.
  - **Solution**: Check that the CLI is properly configured with your API credentials. Ensure that the API server is running and accessible.

If you encounter other issues, please refer to the SDK documentation or contact support.