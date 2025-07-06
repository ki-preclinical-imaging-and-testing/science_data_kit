# REDIRECT NOTICE

**This file has been moved to a new location.**

**New Location**: [docs/roadmaps/active/knowledge_graph_examples.md](../docs/roadmaps/active/knowledge_graph_examples.md)

**Redirect Created**: July 6, 2024

**Original File Removal Date**: August 6, 2024 (after 1-month transition period)

---

Please update your bookmarks and references to point to the new location. This redirect will be removed after the transition period.

The Science Data Kit repository structure has been reorganized to improve discoverability, maintainability, and integration with documentation systems. All roadmap files have been moved to the `docs/roadmaps/` directory, with active roadmaps in `docs/roadmaps/active/`, archived roadmaps in `docs/roadmaps/archive/`, and templates in `docs/roadmaps/templates/`.

---

# Knowledge Graph Documentation System - Examples

## Before/After Documentation Examples

### Before: Standard Python Docstring

```python
class Neo4jManager:
    """
    Manages Neo4j database connections and operations for SciDK.

    The Neo4jManager provides a high-level interface for graph database
    operations, including connection management, query execution, and
    transaction handling.

    Args:
        uri (str): The URI of the Neo4j database
        username (str): The username for authentication
        password (str): The password for authentication

    Attributes:
        driver (neo4j.Driver): The Neo4j driver instance
        session_config (dict): Configuration for Neo4j sessions

    Methods:
        execute_query: Executes a Cypher query and returns the results
        begin_transaction: Begins a new transaction
        commit_transaction: Commits an active transaction
        rollback_transaction: Rolls back an active transaction
    """
```

### After: Knowledge Graph Enhanced Docstring

```python
class Neo4jManager:
    """
    Manages Neo4j database connections and operations for SciDK.

    <!-- concept: graph_database, data_storage, connection_management -->
    <!-- pattern: database_manager, singleton_pattern, connection_pooling -->

    The Neo4jManager provides a high-level interface for graph database
    operations, including connection management, query execution, and
    transaction handling.

    Args:
        uri (str): The URI of the Neo4j database
        username (str): The username for authentication
        password (str): The password for authentication

    Attributes:
        driver (neo4j.Driver): The Neo4j driver instance
        session_config (dict): Configuration for Neo4j sessions

    Methods:
        execute_query: Executes a Cypher query and returns the results
        begin_transaction: Begins a new transaction
        commit_transaction: Commits an active transaction
        rollback_transaction: Rolls back an active transaction

    ## Related Components
    - {class}`science_data_kit.core.data.DataPipeline` - Uses this manager for data storage
    - {class}`science_data_kit.core.query.QueryBuilder` - Builds queries executed by this manager
    - {class}`science_data_kit.core.config.DatabaseConfig` - Provides connection configuration

    ## Extension Patterns
    ### Custom Query Methods
    <!-- pattern: domain_specific_extension, query_customization -->
    Add domain-specific query methods by inheriting and adding methods:
    ```python
    class GenomicsNeo4jManager(Neo4jManager):
        def find_gene_pathways(self, gene_id: str) -> List[Pathway]:
            # Custom genomics query logic
    ```

    ### Performance Optimization  
    <!-- pattern: performance_optimization, caching_strategy -->
    Override query execution for specialized performance requirements:
    ```python
    def execute_query(self, query: str) -> Result:
        # Add caching, connection pooling, etc.
    ```

    ## Implementation Examples
    - {class}`science_data_kit.specialized.GenomicsNeo4jManager` - Domain-specific extension
    - {class}`science_data_kit.core.testing.MockNeo4jManager` - Testing implementation
    """
```

### Before: Standard Markdown Documentation

```markdown
# Data Analysis Pipelines

## Overview
Data analysis pipelines in SciDK provide a structured way to process scientific data through multiple stages of transformation and analysis.

## Core Architecture
The pipeline system is built around the DataPipeline class, which orchestrates:

- **Data Ingestion**: Through data connectors
- **Validation**: Using validation engines  
- **Transformation**: Via analysis modules
- **Output**: To visualization systems

## Implementation Patterns

### Creating New Pipeline Stages
New analysis stages should inherit from `PipelineStage`:

```python
from science_data_kit.core.data import PipelineStage

class CustomAnalysisStage(PipelineStage):
    def process(self, data: DataFrame) -> DataFrame:
        # Custom analysis logic
        return transformed_data
```

### Domain-Specific Pipeline Configurations
Genomics pipelines can be configured using specialized YAML templates:

```yaml
pipeline_name: "genomics_analysis" 
domain: "bioinformatics"
stages:
  - name: "sequence_validation"
    class: "GenomicsDataValidator"
  - name: "expression_normalization" 
    class: "ExpressionNormalizer"
```

## Related Documentation
- [Data Connectors Guide](./data_connectors.md) - Input data sources
- [Analysis Modules Reference](../api/analysis/) - Available analysis components
- [Domain-Specific Extensions](./domain_extensions.md) - Bioinformatics, imaging, clinical workflows
```

### After: Knowledge Graph Enhanced Markdown

```markdown
# Data Analysis Pipelines

<!-- concept: scientific_workflow, data_analysis, pipeline_architecture -->
<!-- pattern: workflow_orchestration, stage_based_processing -->

## Overview
Data analysis pipelines in SciDK provide a structured way to process scientific data through multiple stages of transformation and analysis.

## Core Architecture
<!-- concept: data_pipeline, component_orchestration -->
The pipeline system is built around the {class}`science_data_kit.core.data.DataPipeline` class, which orchestrates:

- **Data Ingestion**: Through [data connectors](./data_connectors.md)
- **Validation**: Using [validation engines](./validation.md)  
- **Transformation**: Via [analysis modules](./analysis_modules.md)
- **Output**: To [visualization systems](./visualization.md)

## Implementation Patterns

### Creating New Pipeline Stages
<!-- pattern: pipeline_stage, component_extension -->
<!-- concept: extensibility, plugin_architecture -->
New analysis stages should inherit from `PipelineStage`:

```python
from science_data_kit.core.data import PipelineStage

class CustomAnalysisStage(PipelineStage):
    def process(self, data: DataFrame) -> DataFrame:
        # Custom analysis logic
        return transformed_data
```

### Domain-Specific Pipeline Configurations
<!-- pattern: domain_customization, configuration_driven -->
<!-- concept: bioinformatics, genomics_analysis -->
Genomics pipelines can be configured using specialized YAML templates:

```yaml
pipeline_name: "genomics_analysis" 
domain: "bioinformatics"
stages:
  - name: "sequence_validation"
    class: "GenomicsDataValidator"
    concept_tags: ["data_validation", "sequence_analysis"]
  - name: "expression_normalization" 
    class: "ExpressionNormalizer"
    concept_tags: ["data_preprocessing", "statistical_normalization"]
```

## Related Documentation
- [Data Connectors Guide](./data_connectors.md) - Input data sources
- [Analysis Modules Reference](../api/analysis/) - Available analysis components
- [Domain-Specific Extensions](./domain_extensions.md) - Bioinformatics, imaging, clinical workflows

## Examples
See the `examples/pipelines/` directory for complete pipeline implementations:
- [RNA-seq Analysis Pipeline](../../examples/pipelines/rnaseq_pipeline.py) <!-- concept: transcriptomics, rna_seq -->
- [Imaging Data Pipeline](../../examples/pipelines/imaging_pipeline.py) <!-- concept: medical_imaging, image_processing -->
```

## Sample AI Queries and Responses

### Query 1: Finding Extension Points

**User Query:**
"How do I add support for proteomics data?"

**AI Query to Knowledge Graph:**
```python
kg.find_extension_point("proteomics + data_integration")
```

**Knowledge Graph Response:**
```json
{
  "extension_points": [
    {
      "component": "DataConnectorInterface",
      "file_path": "science_data_kit/core/integrations/connector.py",
      "patterns": ["connector_implementation", "data_source_integration"],
      "concepts": ["data_integration", "scientific_data"]
    },
    {
      "component": "DataValidator",
      "file_path": "science_data_kit/core/validation/validator.py",
      "patterns": ["validation_implementation", "schema_validation"],
      "concepts": ["data_validation", "data_quality"]
    },
    {
      "component": "AnalysisInterface",
      "file_path": "science_data_kit/core/analysis/interface.py",
      "patterns": ["analysis_implementation", "pipeline_stage"],
      "concepts": ["data_analysis", "scientific_analysis"]
    }
  ],
  "related_components": [
    {
      "component": "GenomicsDataValidator",
      "file_path": "science_data_kit/specialized/genomics/validation.py",
      "patterns": ["domain_specific_validation"],
      "concepts": ["genomics", "bioinformatics", "data_validation"]
    }
  ],
  "implementation_patterns": [
    {
      "pattern": "domain_specific_connector",
      "examples": ["GenomicsConnector", "ImagingConnector"]
    },
    {
      "pattern": "specialized_validator",
      "examples": ["GenomicsDataValidator", "ClinicalDataValidator"]
    }
  ]
}
```

**AI Response to User:**
"To add support for proteomics data in SciDK, you should implement three key components:

1. **Create a Proteomics Data Connector**:
   - Inherit from `DataConnectorInterface` in `science_data_kit.core.integrations.connector`
   - Implement the required methods for connecting to proteomics data sources
   - Register using the `@connector` decorator

2. **Implement a Proteomics Data Validator**:
   - Inherit from `DataValidator` in `science_data_kit.core.validation.validator`
   - Add validation rules specific to proteomics data formats
   - Follow the pattern established in `GenomicsDataValidator`

3. **Create Proteomics Analysis Components**:
   - Inherit from `AnalysisInterface` in `science_data_kit.core.analysis.interface`
   - Implement specialized analysis methods for proteomics data
   - Register with the `@analysis_method` decorator

Here's a code template for the connector:

```python
from science_data_kit.core.integrations.connector import DataConnectorInterface
from science_data_kit.core.di import connector

@connector('proteomics')
class ProteomicsConnector(DataConnectorInterface):
    """
    Connector for proteomics data sources.

    <!-- concept: data_integration, proteomics, mass_spectrometry -->
    <!-- pattern: domain_specific_connector, data_source_integration -->
    """

    def __init__(self, config):
        super().__init__(config)
        # Initialize proteomics-specific configuration

    def connect(self):
        # Implement connection to proteomics data source
        pass

    def get_data(self, query):
        # Implement data retrieval for proteomics
        pass
```

For examples, look at the existing domain-specific implementations like `GenomicsConnector` and `ImagingConnector`."

### Query 2: Understanding Component Relationships

**User Query:**
"How does the dependency injection system work with data connectors?"

**AI Query to Knowledge Graph:**
```python
kg.find_component("DependencyInjectionContainer")
kg.find_components_by_concept("dependency_injection")
kg.find_related_components("DataConnectorInterface")
```

**Knowledge Graph Response:**
```json
{
  "components": [
    {
      "component": "DependencyInjectionContainer",
      "file_path": "science_data_kit/core/di/container.py",
      "patterns": ["service_locator", "dependency_injection"],
      "concepts": ["dependency_management", "inversion_of_control"]
    },
    {
      "component": "Provider",
      "file_path": "science_data_kit/core/di/provider.py",
      "patterns": ["factory_pattern", "dependency_injection"],
      "concepts": ["dependency_management", "component_creation"]
    },
    {
      "component": "connector",
      "file_path": "science_data_kit/core/di/decorators.py",
      "patterns": ["decorator_pattern", "registration_pattern"],
      "concepts": ["dependency_injection", "component_registration"]
    }
  ],
  "relationships": [
    {
      "source": "DataConnectorInterface",
      "target": "DependencyInjectionContainer",
      "relationship": "REGISTERED_WITH",
      "pattern": "component_registration"
    },
    {
      "source": "connector",
      "target": "DataConnectorInterface",
      "relationship": "REGISTERS",
      "pattern": "decorator_registration"
    },
    {
      "source": "DataConnectorRegistry",
      "target": "DependencyInjectionContainer",
      "relationship": "USES",
      "pattern": "registry_pattern"
    }
  ],
  "examples": [
    {
      "component": "MongoDBConnector",
      "file_path": "science_data_kit/core/integrations/mongodb_connector.py",
      "registration": "@connector('mongodb')",
      "usage": "container.get('connector', 'mongodb')"
    }
  ]
}
```

**AI Response to User:**
"The dependency injection system in SciDK works with data connectors through a registration and retrieval pattern:

1. **Registration Process**:
   - Data connectors inherit from `DataConnectorInterface`
   - They're registered using the `@connector` decorator from `science_data_kit.core.di.decorators`
   - The decorator registers the connector with the `DependencyInjectionContainer`
   - Each connector is registered with a unique name (e.g., 'mongodb', 'neo4j')

2. **Container Management**:
   - The `DependencyInjectionContainer` maintains a registry of all connectors
   - It uses the `Provider` class to create instances when requested
   - Connectors are lazy-loaded only when needed

3. **Retrieval Process**:
   - Components request connectors from the container using:
     ```python
     connector = container.get('connector', 'mongodb')
     ```
   - The container returns the appropriate connector instance
   - If the connector hasn't been created yet, it's instantiated

Here's an example of defining and using a connector:

```python
# Defining a connector
from science_data_kit.core.integrations.connector import DataConnectorInterface
from science_data_kit.core.di import connector

@connector('proteomics')
class ProteomicsConnector(DataConnectorInterface):
    def connect(self):
        # Implementation
        pass

# Using a connector
from science_data_kit.core.di import container

def analyze_proteomics_data():
    # Get the proteomics connector
    proteomics = container.get('connector', 'proteomics')

    # Use the connector
    proteomics.connect()
    data = proteomics.get_data(query)

    # Process data
    return processed_data
```

This pattern ensures loose coupling between components and allows for easy substitution of different connector implementations."

## Cross-Reference and Tagging Examples

### Component Cross-References

```python
class DataPipeline:
    """
    Orchestrates data processing through multiple stages.

    <!-- concept: data_pipeline, workflow_orchestration -->
    <!-- pattern: pipeline_pattern, composite_pattern -->

    ## Related Components
    - {class}`science_data_kit.core.data.PipelineStage` - Individual processing stages
    - {class}`science_data_kit.core.data.DataSource` - Input data sources
    - {class}`science_data_kit.core.data.DataSink` - Output destinations

    ## Used By
    - {class}`science_data_kit.analysis.GenomicsWorkflow` - Genomics analysis pipeline
    - {class}`science_data_kit.analysis.ProteomicsWorkflow` - Proteomics analysis pipeline
    """
```

### Hierarchical Concept Tagging

```markdown
# Scientific Data Analysis

<!-- concept: scientific_analysis -->

## Statistical Analysis

<!-- concept: scientific_analysis.statistical_analysis -->

### Regression Analysis

<!-- concept: scientific_analysis.statistical_analysis.regression -->

### Classification

<!-- concept: scientific_analysis.statistical_analysis.classification -->

## Machine Learning

<!-- concept: scientific_analysis.machine_learning -->

### Supervised Learning

<!-- concept: scientific_analysis.machine_learning.supervised_learning -->

### Clustering

<!-- concept: scientific_analysis.machine_learning.clustering -->
```

### Pattern Documentation with Examples

```markdown
# Implementation Patterns

<!-- concept: design_patterns, implementation_patterns -->

## Connector Pattern

<!-- pattern: connector_pattern -->
<!-- concept: data_integration, external_systems -->

The Connector Pattern provides a standardized interface for connecting to external data sources.

### Implementation

```python
from abc import ABC, abstractmethod

class ConnectorInterface(ABC):
    @abstractmethod
    def connect(self):
        """Establish connection to the data source"""
        pass

    @abstractmethod
    def get_data(self, query):
        """Retrieve data from the source"""
        pass

    @abstractmethod
    def close(self):
        """Close the connection"""
        pass
```

### Examples

- {class}`science_data_kit.connectors.MongoDBConnector` - MongoDB implementation
- {class}`science_data_kit.connectors.Neo4jConnector` - Neo4j implementation
- {class}`science_data_kit.connectors.RESTConnector` - REST API implementation

### When to Use

Use this pattern when:
- You need to abstract away the details of connecting to external systems
- You want to provide a consistent interface for different data sources
- You need to support multiple backend systems interchangeably
```

## Integration with Existing SciDK Components

### Integration with Dependency Injection System

```python
from science_data_kit.core.di import container, provider
from science_data_kit.knowledge_graph.query import KnowledgeGraphQuery

# Register the knowledge graph query component
@provider('knowledge_graph')
def provide_knowledge_graph():
    """
    Provides a KnowledgeGraphQuery instance.

    <!-- concept: dependency_injection, knowledge_graph -->
    <!-- pattern: provider_pattern, factory_pattern -->
    """
    neo4j_uri = container.get('config').get('neo4j_uri')
    neo4j_user = container.get('config').get('neo4j_user')
    neo4j_password = container.get('config').get('neo4j_password')

    return KnowledgeGraphQuery(neo4j_uri, neo4j_user, neo4j_password)

# Usage in other components
def get_component_documentation(component_name):
    """
    Get documentation for a component from the knowledge graph.

    <!-- concept: documentation_retrieval, knowledge_graph -->
    <!-- pattern: service_usage, dependency_injection -->
    """
    kg = container.get('knowledge_graph')
    return kg.find_component(component_name)
```

### Integration with Sphinx Documentation

```python
# In conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'science_data_kit.knowledge_graph.sphinx_extension'
]

# Knowledge graph configuration
knowledge_graph_enabled = True
knowledge_graph_neo4j_uri = 'bolt://localhost:7687'
knowledge_graph_neo4j_user = 'neo4j'
knowledge_graph_neo4j_password = 'password'
```

### Integration with Workshop Materials

```markdown
# SciDK Workshop: Extending the Platform

<!-- concept: workshop, extension_points -->
<!-- pattern: tutorial, hands_on_exercise -->

## Exercise 1: Creating a Custom Connector

In this exercise, we'll create a custom connector for a specialized data source.

### Step 1: Identify the Extension Point

Use the knowledge graph to find the appropriate extension point:

```python
from science_data_kit.knowledge_graph import query

# Find extension points for connectors
extension_points = query.find_extension_point("connector + data_integration")

# View the results
for point in extension_points:
    print(f"Component: {point.component}")
    print(f"File: {point.file_path}")
    print(f"Patterns: {', '.join(point.patterns)}")
    print(f"Concepts: {', '.join(point.concepts)}")
    print()
```

### Step 2: Implement the Connector

Based on the extension point information, create your connector:

```python
from science_data_kit.core.integrations.connector import DataConnectorInterface
from science_data_kit.core.di import connector

@connector('custom')
class CustomConnector(DataConnectorInterface):
    """
    Custom connector for specialized data source.

    <!-- concept: data_integration, custom_data_source -->
    <!-- pattern: connector_implementation, data_source_integration -->
    """

    def __init__(self, config):
        super().__init__(config)
        # Initialize custom configuration

    def connect(self):
        # Implement connection logic
        pass

    def get_data(self, query):
        # Implement data retrieval
        pass
```
```
