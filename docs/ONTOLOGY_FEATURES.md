# Ontology Features in Science Data Kit

This document provides detailed information about the ontology-related features in the Science Data Kit.

## Overview

The Science Data Kit provides several features for working with ontologies:

1. **Summarizing Ontology Terms**: Analyze and summarize ontology terms used across different node labels in Neo4j
2. **Loading Ontology Relationships**: Load ontology terms and their relationships into Neo4j in a standardized way
3. **Loading Ontology Terms**: Load ontology terms directly from OntologyTerm objects or dictionaries

These features help you build and maintain ontology-based knowledge graphs, making your data more interoperable and semantically rich.

## Summarizing Ontology Terms

The `summarize_ontology_terms` method in the `Neo4jManager` class provides a standardized way to analyze and summarize ontology terms used across different node labels in Neo4j.

### Usage

```python
from science_data_kit.core.db.db_manager import Neo4jManager

# Create a Neo4jManager instance
db_manager = Neo4jManager()

# Get a summary of all ontology terms in the database
summary = db_manager.summarize_ontology_terms()

# Get a summary for a specific label
person_summary = db_manager.summarize_ontology_terms(label="Person")

# Get a compact summary
compact_summary = db_manager.summarize_ontology_terms(format_type="compact")

# Get a detailed summary
detailed_summary = db_manager.summarize_ontology_terms(format_type="detailed")
```

### Output Formats

The method supports three output formats:

1. **Standard Format** (default): Provides detailed property information
   ```python
   {
     "labels": {
       "LabelName": {
         "properties": {
           "propertyName": {
             "count": int,
             "unique_values": int,
             "sample_values": list,
             "has_uri_pattern": bool,
             "is_likely_ontology": bool
           }
         },
         "total_ontology_properties": int
       }
     },
     "total_labels": int,
     "total_ontology_properties": int,
     "metadata": {
       "generated_at": "timestamp",
       "format": "standard"
     }
   }
   ```

2. **Compact Format**: Provides a simplified view with just label names and likely ontology properties
   ```python
   {
     "LabelName": ["property1", "property2", ...],
     ...
   }
   ```

3. **Detailed Format**: Extends the standard format with additional statistics
   ```python
   # Same as standard format, plus:
   "propertyName": {
     # ... standard fields
     "all_values": list,
     "value_types": list,
     "average_string_length": float
   }
   ```

## Loading Ontology Relationships

The `load_ontology_relationships` method provides a flexible and standardized approach to loading ontology terms and their relationships into Neo4j from OntologyAnnotation objects.

### Usage

```python
from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology import OntologyAnnotation, OntologySource

# Create a Neo4jManager instance
db_manager = Neo4jManager()

# Create OntologyAnnotation objects
annotations = [
    OntologyAnnotation(
        term="Metabolomics",
        term_accession="http://purl.obolibrary.org/obo/NCIT_C16974",
        term_source=OntologySource(
            name="NCIT",
            version="4.0",
            description="National Cancer Institute Thesaurus"
        )
    ),
    OntologyAnnotation(
        term="Proteomics",
        term_accession="http://purl.obolibrary.org/obo/NCIT_C20085",
        term_source=OntologySource(
            name="NCIT",
            version="4.0",
            description="National Cancer Institute Thesaurus"
        )
    )
]

# Load ontology relationships into Neo4j
result = db_manager.load_ontology_relationships(
    annotations,
    create_source_nodes=True,
    relationship_type="HAS_TERM",
    batch_size=100,
    additional_term_properties={"term_accession": "uri"},
    additional_source_properties={"version": "ontology_version"}
)

print(f"Loaded {result['terms_created']} new terms and {result['sources_created']} new sources.")
print(f"Created {result['relationships_created']} relationships between sources and terms.")
```

### Parameters

- **ontology_annotations**: List of OntologyAnnotation objects to load
- **create_source_nodes**: Whether to create nodes for ontology sources (default: True)
- **relationship_type**: The type of relationship to create between source and term nodes (default: "HAS_TERM")
- **batch_size**: Number of terms to process in each batch for better performance (default: 100)
- **additional_term_properties**: Dictionary mapping from OntologyAnnotation attribute names to property names to be set on OntologyTerm nodes
- **additional_source_properties**: Dictionary mapping from OntologySource attribute names to property names to be set on OntologySource nodes

### Return Value

The method returns a dictionary with statistics about the operation:

```python
{
    "terms_created": int,  # Number of term nodes created
    "terms_updated": int,  # Number of term nodes updated
    "sources_created": int,  # Number of source nodes created
    "sources_updated": int,  # Number of source nodes updated
    "relationships_created": int,  # Number of relationships created
    "total_processed": int  # Total number of annotations processed
}
```

## Loading Ontology Terms

The `load_ontology_terms` method provides a standard way to load ontology terms and their relationships directly from OntologyTerm objects or dictionaries with the same structure.

### Usage

```python
from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.models.entity_schemas import OntologyTerm

# Create a Neo4jManager instance
db_manager = Neo4jManager()

# Create OntologyTerm objects
terms = [
    OntologyTerm(
        id="term-001",
        term="Glucose",
        term_accession="http://purl.obolibrary.org/obo/CHEBI_17234",
        term_source="CHEBI",
        definition="A monosaccharide that has a role as a human metabolite."
    ),
    OntologyTerm(
        id="term-002",
        term="Fructose",
        term_accession="http://purl.obolibrary.org/obo/CHEBI_28645",
        term_source="CHEBI",
        definition="A ketohexose that is the 2-ketose of glucose."
    )
]

# Load ontology terms into Neo4j
result = db_manager.load_ontology_terms(
    terms,
    relationship_type="RELATED_TO",
    batch_size=100
)

print(f"Loaded {result['terms_created']} new terms and updated {result['terms_updated']} existing terms.")
print(f"Created {result['relationships_created']} relationships between terms.")
```

### Parameters

- **ontology_terms**: List of OntologyTerm objects or dictionaries with the same structure
- **relationship_type**: The type of relationship to create between related terms (default: "RELATED_TO")
- **batch_size**: Number of terms to process in each batch for better performance (default: 100)

### Return Value

The method returns a dictionary with statistics about the operation:

```python
{
    "terms_created": int,  # Number of term nodes created
    "terms_updated": int,  # Number of term nodes updated
    "relationships_created": int,  # Number of relationships created
    "total_processed": int  # Total number of terms processed
}
```

## Example: Complete Ontology Workflow

Here's a complete example that demonstrates how to use all the ontology-related features:

```python
from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.models.entity_schemas import OntologyTerm
from science_data_kit.core.utils.isa_compatibility import OntologyAnnotation

# Create a Neo4jManager instance
db_manager = Neo4jManager()

# 1. Create and load ontology terms
terms = [
    OntologyTerm(
        id="term-001",
        term="Glucose",
        term_accession="http://purl.obolibrary.org/obo/CHEBI_17234",
        term_source="CHEBI",
        definition="A monosaccharide that has a role as a human metabolite."
    ),
    OntologyTerm(
        id="term-002",
        term="Fructose",
        term_accession="http://purl.obolibrary.org/obo/CHEBI_28645",
        term_source="CHEBI",
        definition="A ketohexose that is the 2-ketose of glucose."
    )
]

result1 = db_manager.load_ontology_terms(terms)
print(f"Loaded {result1['terms_created']} new terms and updated {result1['terms_updated']} existing terms.")

# 2. Create and load ontology annotations
class OntologySource:
    def __init__(self, name, version=None, description=None):
        self.name = name
        self.version = version
        self.description = description

annotations = [
    OntologyAnnotation(
        term="Metabolomics",
        term_accession="http://purl.obolibrary.org/obo/NCIT_C16974",
        term_source=OntologySource(
            name="NCIT",
            version="4.0",
            description="National Cancer Institute Thesaurus"
        )
    )
]

result2 = db_manager.load_ontology_relationships(annotations)
print(f"Loaded {result2['terms_created']} new terms from annotations.")

# 3. Summarize ontology terms in the database
summary = db_manager.summarize_ontology_terms()
print(f"Found {summary['total_ontology_properties']} ontology properties across {summary['total_labels']} labels.")

# Print a compact summary
compact_summary = db_manager.summarize_ontology_terms(format_type="compact")
for label, properties in compact_summary.items():
    print(f"Label '{label}' has {len(properties)} ontology properties: {', '.join(properties)}")
```

## Integration with Neo4j Graph Data Science

The ontology features can be combined with Neo4j Graph Data Science (GDS) for advanced analytics:

1. **Similarity Analysis**: Find similar terms based on their relationships
2. **Centrality Algorithms**: Identify key terms in your ontology
3. **Community Detection**: Discover clusters of related terms

Example with GDS:

```python
# Assuming you have loaded ontology terms and relationships

# Run a similarity algorithm
similarity_query = """
CALL gds.nodeSimilarity.stream('ontology-graph')
YIELD node1, node2, similarity
RETURN gds.util.asNode(node1).term AS term1, 
       gds.util.asNode(node2).term AS term2, 
       similarity
ORDER BY similarity DESCENDING, term1, term2
LIMIT 10
"""

results = db_manager.execute_query(similarity_query)
for result in results:
    print(f"{result['term1']} and {result['term2']} have similarity {result['similarity']}")
```

## Importing Ontologies

The Science Data Kit provides the `OntologyImporter` class for importing ontologies from various sources (local files, URLs) and in various formats (OWL, Turtle, RDF/XML, JSON-LD) into Neo4j.

### Usage

```python
from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology import OntologyImporter

# Create a Neo4jManager instance
db_manager = Neo4jManager()
db_manager.connect(uri="bolt://localhost:7687", user="neo4j", password="password")

# Create an OntologyImporter instance
importer = OntologyImporter(db_manager)

# Import an ontology from a local file
importer.load_ontology("path/to/ontology.owl")

# Import an ontology from a URL
importer.load_ontology("https://example.org/ontology.ttl")
```

### Features

The `OntologyImporter` class provides the following features:

1. **Support for Various Formats**: Import ontologies in OWL, Turtle (.ttl), RDF/XML, JSON-LD formats
2. **URL Support**: Import ontologies directly from URLs
3. **Neo4j Integration**: Uses Neo4j's neosemantics (n10s) plugin for efficient ontology import
4. **Fallback Implementation**: Uses rdflib when the neosemantics plugin is not available
5. **Class Hierarchy Preservation**: Preserves class hierarchies as relationships in Neo4j
6. **Error Handling**: Provides robust error handling and logging

## Browsing and Visualizing Ontologies

The Science Data Kit provides the `OntologyBrowser` class for browsing and visualizing ontologies stored in Neo4j.

### Usage

```python
from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology import OntologyBrowser

# Create a Neo4jManager instance
db_manager = Neo4jManager()
db_manager.connect(uri="bolt://localhost:7687", user="neo4j", password="password")

# Create an OntologyBrowser instance
browser = OntologyBrowser(db_manager)

# Get statistics about the ontologies in the database
stats = browser.get_statistics()
print(f"Number of ontology terms: {stats['term_count']}")
print(f"Number of ontology sources: {stats['source_count']}")
print(f"Number of relationships: {stats['relationship_count']}")

# Search for ontology terms
results = browser.search_terms("metabolomics")
print(f"Found {len(results)} terms matching 'metabolomics'")

# Get the hierarchy for a specific term
hierarchy = browser.get_term_hierarchy("Metabolomics")
print(f"Hierarchy for 'Metabolomics': {hierarchy}")

# Visualize the hierarchy for a specific term
network = browser.visualize_term_hierarchy("Metabolomics")
network.show("metabolomics_hierarchy.html")

# Visualize ontology sources and their relationships
network = browser.visualize_ontology_sources()
network.show("ontology_sources.html")
```

### Features

The `OntologyBrowser` class provides the following features:

1. **Term Search**: Search for ontology terms in the database
2. **Hierarchy Visualization**: Visualize the hierarchy for a specific ontology term
3. **Source Visualization**: Visualize ontology sources and their relationships
4. **Statistics**: Get statistics about the ontologies in the database
5. **Interactive Visualizations**: Create interactive visualizations using pyvis

## Best Practices

1. **Use URIs for term_accession**: Always use proper URIs for term_accession values to ensure interoperability
2. **Include source information**: Provide complete source information for ontology terms
3. **Batch processing**: Use batch processing for large ontologies
4. **Relationship types**: Choose meaningful relationship types that reflect the semantic meaning
5. **Regular updates**: Periodically update your ontology terms to stay current with the latest versions
6. **Use neosemantics plugin**: Install the Neo4j neosemantics (n10s) plugin for efficient ontology import
7. **Visualize hierarchies**: Use the visualization capabilities to understand the structure of your ontologies
