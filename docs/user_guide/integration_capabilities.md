# Integration Capabilities Guide

## Overview

The Science Data Kit provides integration capabilities with various external platforms, allowing you to access and analyze data from these sources within the SDK environment. This guide focuses on the integration with NExtSEEK and FAIRDOM-Hub platforms.

## Table of Contents

1. [Introduction](#introduction)
2. [NExtSEEK Integration](#nextsee-integration)
3. [FAIRDOM-Hub Integration](#fairdom-hub-integration)
4. [Using Integration Providers](#using-integration-providers)
5. [Importing Data into Neo4j](#importing-data-into-neo4j)
6. [Querying Integrated Data](#querying-integrated-data)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

Integration capabilities allow the Science Data Kit to connect with external platforms and services, providing a unified interface for accessing and analyzing data from these sources. The SDK uses a provider-based architecture for integrations, where each provider implements a common interface for interacting with a specific platform.

Currently, the SDK supports integration with the following platforms:

- **NExtSEEK**: A platform for managing and analyzing scientific data.
- **FAIRDOM-Hub**: A platform for managing and sharing scientific research assets.

## NExtSEEK Integration

The NExtSEEK integration allows you to access and analyze data from the NExtSEEK platform within the Science Data Kit environment.

### Features

- **Authentication**: Authenticate with NExtSEEK using username and password or API key.
- **Data Retrieval**: Retrieve projects, experiments, and samples from NExtSEEK.
- **Search**: Search for resources in NExtSEEK.
- **Data Import**: Import NExtSEEK data into Neo4j for analysis.

### Getting Started

To use the NExtSEEK integration, you first need to initialize the NExtSEEK provider:

```python
from science_data_kit.core.integrations import get_provider

# Initialize the NExtSEEK provider
nextsee_provider = get_provider("nextsee")(
    base_url="https://nextsee.org/api/v1",
    api_key=None  # Replace with your API key if available
)
```

If you don't have an API key, you can authenticate with your username and password:

```python
# Authenticate with NExtSEEK
success, message = nextsee_provider.authenticate("your_username", "your_password")
print(f"Authentication result: {success}, {message}")
```

### Retrieving Data

Once authenticated, you can retrieve data from NExtSEEK:

```python
# Get projects
success, projects = nextsee_provider.get_projects()
if success:
    print(f"Retrieved {len(projects)} projects")
else:
    print(f"Failed to retrieve projects: {projects}")

# Get experiments for a specific project
project_id = "your_project_id"
success, experiments = nextsee_provider.get_experiments(project_id)
if success:
    print(f"Retrieved {len(experiments)} experiments for project {project_id}")
else:
    print(f"Failed to retrieve experiments: {experiments}")

# Get samples for a specific experiment
experiment_id = "your_experiment_id"
success, samples = nextsee_provider.get_samples(experiment_id)
if success:
    print(f"Retrieved {len(samples)} samples for experiment {experiment_id}")
else:
    print(f"Failed to retrieve samples: {samples}")
```

### Searching

You can search for resources in NExtSEEK:

```python
# Search for resources
query = "your_search_query"
success, results = nextsee_provider.search(query)
if success:
    print(f"Found {len(results)} results for query '{query}'")
else:
    print(f"Failed to search: {results}")
```

### Importing Data into Neo4j

You can import NExtSEEK data into Neo4j for analysis:

```python
# Import data into Neo4j
from science_data_kit.core.db import Neo4jManager

# Connect to Neo4j
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Import data
data = {
    "projects": projects,
    "experiments": experiments,
    "samples": samples
}
success, message = nextsee_provider.import_to_neo4j(data, db_manager)
print(f"Import result: {success}, {message}")
```

## FAIRDOM-Hub Integration

The FAIRDOM-Hub integration allows you to access and analyze data from the FAIRDOM-Hub platform within the Science Data Kit environment.

### Features

- **Authentication**: Authenticate with FAIRDOM-Hub using username and password or API key.
- **Data Retrieval**: Retrieve investigations, studies, assays, and data files from FAIRDOM-Hub.
- **Data Download**: Download data files from FAIRDOM-Hub.
- **Data Import**: Import FAIRDOM-Hub data into Neo4j for analysis.

### Getting Started

To use the FAIRDOM-Hub integration, you first need to initialize the FAIRDOM-Hub provider:

```python
from science_data_kit.core.integrations import get_provider

# Initialize the FAIRDOM-Hub provider
fairdom_provider = get_provider("fairdom")(
    base_url="https://fairdomhub.org/api",
    api_key=None  # Replace with your API key if available
)
```

If you don't have an API key, you can authenticate with your username and password:

```python
# Authenticate with FAIRDOM-Hub
success, message = fairdom_provider.authenticate("your_username", "your_password")
print(f"Authentication result: {success}, {message}")
```

### Retrieving Data

Once authenticated, you can retrieve data from FAIRDOM-Hub:

```python
# Get investigations
success, investigations = fairdom_provider.get_investigations()
if success:
    print(f"Retrieved {len(investigations)} investigations")
else:
    print(f"Failed to retrieve investigations: {investigations}")

# Get studies for a specific investigation
investigation_id = "your_investigation_id"
success, studies = fairdom_provider.get_studies(investigation_id)
if success:
    print(f"Retrieved {len(studies)} studies for investigation {investigation_id}")
else:
    print(f"Failed to retrieve studies: {studies}")

# Get assays for a specific study
study_id = "your_study_id"
success, assays = fairdom_provider.get_assays(study_id)
if success:
    print(f"Retrieved {len(assays)} assays for study {study_id}")
else:
    print(f"Failed to retrieve assays: {assays}")

# Get data files for a specific assay
assay_id = "your_assay_id"
success, data_files = fairdom_provider.get_data_files(assay_id)
if success:
    print(f"Retrieved {len(data_files)} data files for assay {assay_id}")
else:
    print(f"Failed to retrieve data files: {data_files}")
```

### Downloading Data Files

You can download data files from FAIRDOM-Hub:

```python
# Download a data file
data_file_id = "your_data_file_id"
destination = "path/to/save/file.csv"
success, message = fairdom_provider.download_data_file(data_file_id, destination)
print(f"Download result: {success}, {message}")
```

### Importing Data into Neo4j

You can import FAIRDOM-Hub data into Neo4j for analysis:

```python
# Import data into Neo4j
from science_data_kit.core.db import Neo4jManager

# Connect to Neo4j
db_manager = Neo4jManager(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Import data
data = {
    "investigations": investigations,
    "studies": studies,
    "assays": assays,
    "data_files": data_files
}
success, message = fairdom_provider.import_to_neo4j(data, db_manager)
print(f"Import result: {success}, {message}")
```

## Using Integration Providers

The Science Data Kit provides a unified interface for working with integration providers. You can list all available providers and get a specific provider using the following code:

```python
from science_data_kit.core.integrations import list_providers, get_provider

# List available providers
providers = list_providers()
print("Available integration providers:")
for provider in providers:
    print(f"- {provider}")

# Get a specific provider
provider_name = "nextsee"  # or "fairdom"
provider_class = get_provider(provider_name)
if provider_class:
    provider = provider_class()
    print(f"Successfully initialized {provider_name} provider")
else:
    print(f"Provider {provider_name} not found")
```

## Importing Data into Neo4j

Both the NExtSEEK and FAIRDOM-Hub providers include methods for importing data into Neo4j. These methods create nodes and relationships in Neo4j based on the data from the respective platforms.

### NExtSEEK Data Model

The NExtSEEK provider creates the following nodes and relationships in Neo4j:

- **Nodes**:
  - `Project:NExtSEEK`: Represents a project in NExtSEEK.
  - `Experiment:NExtSEEK`: Represents an experiment in NExtSEEK.
  - `Sample:NExtSEEK`: Represents a sample in NExtSEEK.
- **Relationships**:
  - `(Project)-[:CONTAINS]->(Experiment)`: Indicates that a project contains an experiment.
  - `(Experiment)-[:CONTAINS]->(Sample)`: Indicates that an experiment contains a sample.

### FAIRDOM-Hub Data Model

The FAIRDOM-Hub provider creates the following nodes and relationships in Neo4j:

- **Nodes**:
  - `Investigation:FAIRDOM`: Represents an investigation in FAIRDOM-Hub.
  - `Study:FAIRDOM`: Represents a study in FAIRDOM-Hub.
  - `Assay:FAIRDOM`: Represents an assay in FAIRDOM-Hub.
  - `DataFile:FAIRDOM`: Represents a data file in FAIRDOM-Hub.
- **Relationships**:
  - `(Investigation)-[:CONTAINS]->(Study)`: Indicates that an investigation contains a study.
  - `(Study)-[:CONTAINS]->(Assay)`: Indicates that a study contains an assay.
  - `(Assay)-[:CONTAINS]->(DataFile)`: Indicates that an assay contains a data file.

## Querying Integrated Data

Once you've imported data into Neo4j, you can query it using Cypher, Neo4j's query language. Here are some example queries:

### Querying NExtSEEK Data

```cypher
// Get all projects
MATCH (p:Project:NExtSEEK)
RETURN p

// Get all experiments for a specific project
MATCH (p:Project:NExtSEEK {id: "your_project_id"})-[:CONTAINS]->(e:Experiment:NExtSEEK)
RETURN e

// Get all samples for a specific experiment
MATCH (e:Experiment:NExtSEEK {id: "your_experiment_id"})-[:CONTAINS]->(s:Sample:NExtSEEK)
RETURN s

// Get the complete hierarchy
MATCH (p:Project:NExtSEEK)-[:CONTAINS]->(e:Experiment:NExtSEEK)-[:CONTAINS]->(s:Sample:NExtSEEK)
RETURN p.name AS project, e.name AS experiment, s.name AS sample
```

### Querying FAIRDOM-Hub Data

```cypher
// Get all investigations
MATCH (i:Investigation:FAIRDOM)
RETURN i

// Get all studies for a specific investigation
MATCH (i:Investigation:FAIRDOM {id: "your_investigation_id"})-[:CONTAINS]->(s:Study:FAIRDOM)
RETURN s

// Get all assays for a specific study
MATCH (s:Study:FAIRDOM {id: "your_study_id"})-[:CONTAINS]->(a:Assay:FAIRDOM)
RETURN a

// Get all data files for a specific assay
MATCH (a:Assay:FAIRDOM {id: "your_assay_id"})-[:CONTAINS]->(d:DataFile:FAIRDOM)
RETURN d

// Get the complete hierarchy
MATCH (i:Investigation:FAIRDOM)-[:CONTAINS]->(s:Study:FAIRDOM)-[:CONTAINS]->(a:Assay:FAIRDOM)-[:CONTAINS]->(d:DataFile:FAIRDOM)
RETURN i.title AS investigation, s.title AS study, a.title AS assay, d.title AS data_file
```

## Best Practices

Here are some best practices for using the integration capabilities of the Science Data Kit:

1. **Use API Keys**: When possible, use API keys instead of username/password authentication for better security.
2. **Cache Results**: If you're making multiple requests to the same endpoint, consider caching the results to reduce API calls.
3. **Handle Errors**: Always check the success flag returned by provider methods and handle errors appropriately.
4. **Limit Data**: When importing data into Neo4j, consider limiting the amount of data to avoid performance issues.
5. **Use Transactions**: When making multiple changes to Neo4j, use transactions to ensure data consistency.
6. **Clean Up**: Remove any temporary files or data when you're done with them.

## Troubleshooting

Here are some common issues and their solutions:

### Authentication Issues

- **Issue**: Authentication fails with "No token received" error.
  - **Solution**: Check that your username and password are correct. If using an API key, ensure it's valid and has the necessary permissions.

### Connection Issues

- **Issue**: Unable to connect to the platform.
  - **Solution**: Check your internet connection and ensure the platform is accessible. Verify that the base URL is correct.

### Import Issues

- **Issue**: Data import fails with Neo4j errors.
  - **Solution**: Check that your Neo4j connection is valid and that you have the necessary permissions to write to the database. Ensure that the data structure matches what the import method expects.

### Query Issues

- **Issue**: Cypher queries return no results.
  - **Solution**: Verify that the data was imported correctly and that your query is targeting the correct nodes and relationships. Check for typos in node labels, relationship types, and property names.

If you encounter other issues, please refer to the platform-specific documentation or contact support.