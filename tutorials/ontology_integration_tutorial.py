"""
Ontology Integration Tutorial

This tutorial demonstrates how to use the ontology integration features of the Science Data Kit.
It shows how to:
1. Import ontologies from files or URLs
2. Query ontology terms and relationships
3. Visualize ontology hierarchies and relationships
"""

import os
import tempfile
from pathlib import Path

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology import (
    OntologySource, OntologyAnnotation, OntologyImporter, OntologyBrowser,
    get_ontology_terms, get_ontology_sources, get_ontology_relationships,
    search_ontology_terms, get_ontology_statistics
)

# Connect to Neo4j
def connect_to_neo4j():
    """Connect to Neo4j database."""
    # Replace with your Neo4j connection details
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    # Create a Neo4jManager instance
    db_manager = Neo4jManager()
    db_manager.connect(uri=uri, user=user, password=password)
    
    return db_manager

# Example 1: Import an ontology from a URL
def import_ontology_from_url(db_manager):
    """Import an ontology from a URL."""
    print("\n=== Example 1: Import an ontology from a URL ===")
    
    # Create an OntologyImporter instance
    importer = OntologyImporter(db_manager)
    
    # Import an ontology from a URL
    # This is a small ontology for demonstration purposes
    url = "https://raw.githubusercontent.com/oborel/obo-relations/master/ro.owl"
    print(f"Importing ontology from URL: {url}")
    
    # Note: This is a placeholder. The actual implementation will be completed in a future update.
    print("Note: This is a placeholder. The actual implementation will be completed in a future update.")
    
    # For demonstration purposes, let's create some sample ontology data
    create_sample_ontology_data(db_manager)

# Example 2: Import an ontology from a local file
def import_ontology_from_file(db_manager):
    """Import an ontology from a local file."""
    print("\n=== Example 2: Import an ontology from a local file ===")
    
    # Create an OntologyImporter instance
    importer = OntologyImporter(db_manager)
    
    # Create a temporary file with some sample ontology data
    with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as temp_file:
        temp_file.write(b"""
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                 xmlns:owl="http://www.w3.org/2002/07/owl#">
            <owl:Ontology rdf:about="http://example.org/sample-ontology"/>
            <owl:Class rdf:about="http://example.org/sample-ontology#Animal">
                <rdfs:label>Animal</rdfs:label>
            </owl:Class>
            <owl:Class rdf:about="http://example.org/sample-ontology#Mammal">
                <rdfs:label>Mammal</rdfs:label>
                <rdfs:subClassOf rdf:resource="http://example.org/sample-ontology#Animal"/>
            </owl:Class>
            <owl:Class rdf:about="http://example.org/sample-ontology#Dog">
                <rdfs:label>Dog</rdfs:label>
                <rdfs:subClassOf rdf:resource="http://example.org/sample-ontology#Mammal"/>
            </owl:Class>
        </rdf:RDF>
        """)
    
    file_path = temp_file.name
    print(f"Importing ontology from file: {file_path}")
    
    # Note: This is a placeholder. The actual implementation will be completed in a future update.
    print("Note: This is a placeholder. The actual implementation will be completed in a future update.")
    
    # Clean up the temporary file
    os.unlink(file_path)

# Example 3: Query ontology terms and relationships
def query_ontology(db_manager):
    """Query ontology terms and relationships."""
    print("\n=== Example 3: Query ontology terms and relationships ===")
    
    # Get ontology statistics
    stats = get_ontology_statistics(db_manager)
    print(f"Ontology statistics: {stats}")
    
    # Get all ontology terms
    terms = get_ontology_terms(db_manager)
    print(f"Number of ontology terms: {len(terms)}")
    if terms:
        print("Sample terms:")
        for term in terms[:5]:
            print(f"  - {term['term']} ({term.get('term_accession', '')})")
    
    # Get all ontology sources
    sources = get_ontology_sources(db_manager)
    print(f"Number of ontology sources: {len(sources)}")
    if sources:
        print("Sample sources:")
        for source in sources[:5]:
            print(f"  - {source['name']}")
    
    # Search for ontology terms
    search_results = search_ontology_terms(db_manager, "animal")
    print(f"Search results for 'animal': {len(search_results)} terms found")
    if search_results:
        print("Sample results:")
        for result in search_results[:5]:
            print(f"  - {result['term']} ({result.get('term_accession', '')})")

# Example 4: Visualize ontology hierarchies and relationships
def visualize_ontology(db_manager):
    """Visualize ontology hierarchies and relationships."""
    print("\n=== Example 4: Visualize ontology hierarchies and relationships ===")
    
    # Create an OntologyBrowser instance
    browser = OntologyBrowser(db_manager)
    
    # Visualize the hierarchy for a specific term
    term = "Animal"
    print(f"Visualizing hierarchy for term: {term}")
    
    # Note: This would normally create an interactive visualization
    # For this tutorial, we'll just print a message
    print("Note: This would normally create an interactive visualization.")
    print("To visualize the hierarchy in a Jupyter notebook, you would use:")
    print(f"  network = browser.visualize_term_hierarchy('{term}')")
    print("  network.show('term_hierarchy.html')")
    
    # Visualize ontology sources and their relationships
    print("\nVisualizing ontology sources and their relationships")
    print("Note: This would normally create an interactive visualization.")
    print("To visualize the sources in a Jupyter notebook, you would use:")
    print("  network = browser.visualize_ontology_sources()")
    print("  network.show('ontology_sources.html')")

# Helper function to create sample ontology data
def create_sample_ontology_data(db_manager):
    """Create sample ontology data for demonstration purposes."""
    # Create ontology sources
    source_query = """
    MERGE (s:OntologySource {name: $name})
    ON CREATE SET s.created = timestamp()
    SET s.description = $description,
        s.file = $file,
        s.version = $version,
        s.last_updated = timestamp()
    RETURN s
    """
    
    sources = [
        {
            "name": "GO",
            "description": "Gene Ontology",
            "file": "http://purl.obolibrary.org/obo/go.owl",
            "version": "2023-05-01"
        },
        {
            "name": "CHEBI",
            "description": "Chemical Entities of Biological Interest",
            "file": "http://purl.obolibrary.org/obo/chebi.owl",
            "version": "2023-04-01"
        }
    ]
    
    for source in sources:
        db_manager.execute_query(source_query, source)
    
    # Create ontology terms
    term_query = """
    MERGE (t:OntologyTerm {term: $term})
    ON CREATE SET t.created = timestamp()
    SET t.term_accession = $term_accession,
        t.last_updated = timestamp()
    RETURN t
    """
    
    terms = [
        {
            "term": "Animal",
            "term_accession": "GO:0003674"
        },
        {
            "term": "Mammal",
            "term_accession": "GO:0003824"
        },
        {
            "term": "Dog",
            "term_accession": "GO:0016787"
        },
        {
            "term": "Water",
            "term_accession": "CHEBI:15377"
        },
        {
            "term": "Glucose",
            "term_accession": "CHEBI:17234"
        }
    ]
    
    for term in terms:
        db_manager.execute_query(term_query, term)
    
    # Create relationships between sources and terms
    rel_query = """
    MATCH (s:OntologySource {name: $source_name})
    MATCH (t:OntologyTerm {term: $term})
    MERGE (s)-[r:HAS_TERM]->(t)
    ON CREATE SET r.created = timestamp()
    SET r.last_updated = timestamp()
    RETURN r
    """
    
    relationships = [
        {"source_name": "GO", "term": "Animal"},
        {"source_name": "GO", "term": "Mammal"},
        {"source_name": "GO", "term": "Dog"},
        {"source_name": "CHEBI", "term": "Water"},
        {"source_name": "CHEBI", "term": "Glucose"}
    ]
    
    for rel in relationships:
        db_manager.execute_query(rel_query, rel)
    
    # Create hierarchical relationships between terms
    hierarchy_query = """
    MATCH (child:OntologyTerm {term: $child_term})
    MATCH (parent:OntologyTerm {term: $parent_term})
    MERGE (child)-[r:SUBCLASS_OF]->(parent)
    ON CREATE SET r.created = timestamp()
    SET r.last_updated = timestamp()
    RETURN r
    """
    
    hierarchies = [
        {"child_term": "Mammal", "parent_term": "Animal"},
        {"child_term": "Dog", "parent_term": "Mammal"}
    ]
    
    for hierarchy in hierarchies:
        db_manager.execute_query(hierarchy_query, hierarchy)

# Main function to run the tutorial
def main():
    """Run the tutorial."""
    print("=== Ontology Integration Tutorial ===")
    
    # Connect to Neo4j
    try:
        db_manager = connect_to_neo4j()
        print("Connected to Neo4j")
        
        # Run the examples
        import_ontology_from_url(db_manager)
        import_ontology_from_file(db_manager)
        query_ontology(db_manager)
        visualize_ontology(db_manager)
        
        # Disconnect from Neo4j
        db_manager.disconnect()
        print("\nDisconnected from Neo4j")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This tutorial requires a running Neo4j instance.")
        print("You can modify the connection details in the connect_to_neo4j() function.")

if __name__ == "__main__":
    main()