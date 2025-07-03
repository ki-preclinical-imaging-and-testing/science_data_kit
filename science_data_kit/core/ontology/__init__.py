"""
Ontology module for Science Data Kit.

This module provides classes and functions for working with ontologies in the Science Data Kit.
"""

from science_data_kit.core.ontology.models import OntologySource, OntologyAnnotation
from science_data_kit.core.ontology.importer import OntologyImporter
from science_data_kit.core.ontology.queries import (
    get_ontology_terms, get_ontology_sources, get_ontology_relationships,
    get_ontology_hierarchy, search_ontology_terms, get_ontology_statistics,
    ontology_terms_to_dataframe, ontology_sources_to_dataframe, ontology_relationships_to_dataframe
)
from science_data_kit.core.ontology.browser import OntologyBrowser

__all__ = [
    'OntologySource', 'OntologyAnnotation', 'OntologyImporter', 'OntologyBrowser',
    'get_ontology_terms', 'get_ontology_sources', 'get_ontology_relationships',
    'get_ontology_hierarchy', 'search_ontology_terms', 'get_ontology_statistics',
    'ontology_terms_to_dataframe', 'ontology_sources_to_dataframe', 'ontology_relationships_to_dataframe'
]
