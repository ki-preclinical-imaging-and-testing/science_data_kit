"""
Ontology models for Science Data Kit.

This module provides classes for representing ontology sources and annotations.
"""

from typing import Optional, List, Dict, Any, Union


class OntologySource:
    """
    A class representing an ontology source.
    
    Attributes:
        name: The name of the ontology source.
        file: The file path or URL of the ontology source.
        version: The version of the ontology source.
        description: A description of the ontology source.
        comments: A list of comments about the ontology source.
    """
    def __init__(self, name: str = "", file: str = "", version: str = "", description: str = ""):
        self.name = name
        self.file = file
        self.version = version
        self.description = description
        self.comments: List[Dict[str, str]] = []

    def __repr__(self) -> str:
        return f"OntologySource(name='{self.name}', file='{self.file}', version='{self.version}', description='{self.description}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OntologySource):
            return False
        return (self.name == other.name and
                self.file == other.file and
                self.version == other.version and
                self.description == other.description)

    def __hash__(self) -> int:
        return hash((self.name, self.file, self.version, self.description))


class OntologyAnnotation:
    """
    A class representing an ontology annotation.
    
    Attributes:
        term: The term of the annotation.
        term_accession: The accession number of the term.
        term_source: The source of the term, either as a string or an OntologySource object.
    """
    def __init__(self, term: str = "", term_accession: str = "", term_source: Optional[Union[str, OntologySource]] = None):
        self.term = term
        self.term_accession = term_accession
        self.term_source = term_source

    def __repr__(self) -> str:
        return f"OntologyAnnotation(term='{self.term}', term_accession='{self.term_accession}', term_source='{self.term_source}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OntologyAnnotation):
            return False
        return (self.term == other.term and
                self.term_accession == other.term_accession and
                self.term_source == other.term_source)

    def __hash__(self) -> int:
        return hash((self.term, self.term_accession, self.term_source))