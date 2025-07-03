"""
Ontology queries for Science Data Kit.

This module provides helper functions for common ontology queries in Neo4j.
"""

from typing import Optional, List, Dict, Any, Union
import pandas as pd

from science_data_kit.core.db.db_manager import Neo4jManager
from science_data_kit.core.ontology.models import OntologySource, OntologyAnnotation


def get_ontology_terms(db_manager: Neo4jManager, label: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all ontology terms from the database.
    
    Args:
        db_manager: The Neo4j database manager.
        label: Optional label to filter the terms. If None, returns all terms.
        
    Returns:
        A list of dictionaries containing the ontology terms.
    """
    if label:
        query = """
        MATCH (t:OntologyTerm)
        WHERE t.term CONTAINS $label
        RETURN t.term AS term, t.term_accession AS term_accession
        ORDER BY t.term
        """
        parameters = {"label": label}
    else:
        query = """
        MATCH (t:OntologyTerm)
        RETURN t.term AS term, t.term_accession AS term_accession
        ORDER BY t.term
        """
        parameters = {}
    
    return db_manager.execute_query(query, parameters)


def get_ontology_sources(db_manager: Neo4jManager) -> List[Dict[str, Any]]:
    """
    Get all ontology sources from the database.
    
    Args:
        db_manager: The Neo4j database manager.
        
    Returns:
        A list of dictionaries containing the ontology sources.
    """
    query = """
    MATCH (s:OntologySource)
    RETURN s.name AS name, s.file AS file, s.version AS version, s.description AS description
    ORDER BY s.name
    """
    
    return db_manager.execute_query(query)


def get_ontology_relationships(db_manager: Neo4jManager, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all ontology relationships from the database.
    
    Args:
        db_manager: The Neo4j database manager.
        source_name: Optional name of the ontology source to filter by.
        
    Returns:
        A list of dictionaries containing the ontology relationships.
    """
    if source_name:
        query = """
        MATCH (s:OntologySource {name: $source_name})-[r]->(t:OntologyTerm)
        RETURN s.name AS source_name, t.term AS term, t.term_accession AS term_accession, type(r) AS relationship_type
        ORDER BY s.name, t.term
        """
        parameters = {"source_name": source_name}
    else:
        query = """
        MATCH (s:OntologySource)-[r]->(t:OntologyTerm)
        RETURN s.name AS source_name, t.term AS term, t.term_accession AS term_accession, type(r) AS relationship_type
        ORDER BY s.name, t.term
        """
        parameters = {}
    
    return db_manager.execute_query(query, parameters)


def get_ontology_hierarchy(db_manager: Neo4jManager, term: str) -> List[Dict[str, Any]]:
    """
    Get the hierarchy for a specific ontology term.
    
    Args:
        db_manager: The Neo4j database manager.
        term: The term to get the hierarchy for.
        
    Returns:
        A list of dictionaries containing the ontology hierarchy.
    """
    query = """
    MATCH (t:OntologyTerm {term: $term})
    OPTIONAL MATCH path = (t)-[:SUBCLASS_OF*]->(parent:OntologyTerm)
    WITH t, path, parent
    RETURN t.term AS term, 
           t.term_accession AS term_accession,
           COLLECT(DISTINCT parent.term) AS parent_terms,
           COLLECT(DISTINCT parent.term_accession) AS parent_accessions,
           LENGTH(path) AS distance
    ORDER BY distance
    """
    parameters = {"term": term}
    
    return db_manager.execute_query(query, parameters)


def search_ontology_terms(db_manager: Neo4jManager, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for ontology terms in the database.
    
    Args:
        db_manager: The Neo4j database manager.
        search_term: The term to search for.
        
    Returns:
        A list of dictionaries containing the matching ontology terms.
    """
    query = """
    MATCH (t:OntologyTerm)
    WHERE t.term CONTAINS $search_term OR t.term_accession CONTAINS $search_term
    RETURN t.term AS term, t.term_accession AS term_accession
    ORDER BY t.term
    """
    parameters = {"search_term": search_term}
    
    return db_manager.execute_query(query, parameters)


def get_ontology_statistics(db_manager: Neo4jManager) -> Dict[str, Any]:
    """
    Get statistics about the ontologies in the database.
    
    Args:
        db_manager: The Neo4j database manager.
        
    Returns:
        A dictionary containing statistics about the ontologies.
    """
    query = """
    MATCH (t:OntologyTerm)
    WITH COUNT(t) AS term_count
    MATCH (s:OntologySource)
    WITH term_count, COUNT(s) AS source_count
    MATCH (s:OntologySource)-[r]->(t:OntologyTerm)
    RETURN term_count, source_count, COUNT(r) AS relationship_count
    """
    
    result = db_manager.execute_query(query)
    if result:
        return result[0]
    else:
        return {"term_count": 0, "source_count": 0, "relationship_count": 0}


def ontology_terms_to_dataframe(db_manager: Neo4jManager, label: Optional[str] = None) -> pd.DataFrame:
    """
    Get all ontology terms from the database as a pandas DataFrame.
    
    Args:
        db_manager: The Neo4j database manager.
        label: Optional label to filter the terms. If None, returns all terms.
        
    Returns:
        A pandas DataFrame containing the ontology terms.
    """
    terms = get_ontology_terms(db_manager, label)
    return pd.DataFrame(terms)


def ontology_sources_to_dataframe(db_manager: Neo4jManager) -> pd.DataFrame:
    """
    Get all ontology sources from the database as a pandas DataFrame.
    
    Args:
        db_manager: The Neo4j database manager.
        
    Returns:
        A pandas DataFrame containing the ontology sources.
    """
    sources = get_ontology_sources(db_manager)
    return pd.DataFrame(sources)


def ontology_relationships_to_dataframe(db_manager: Neo4jManager, source_name: Optional[str] = None) -> pd.DataFrame:
    """
    Get all ontology relationships from the database as a pandas DataFrame.
    
    Args:
        db_manager: The Neo4j database manager.
        source_name: Optional name of the ontology source to filter by.
        
    Returns:
        A pandas DataFrame containing the ontology relationships.
    """
    relationships = get_ontology_relationships(db_manager, source_name)
    return pd.DataFrame(relationships)