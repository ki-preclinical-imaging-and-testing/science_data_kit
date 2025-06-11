"""
Compatibility layer for isatools to handle Python version differences.
This module provides alternative implementations of isatools classes and functions
for environments where isatools cannot be installed (e.g., Python 3.12+).
"""

class OntologyAnnotation:
    """
    A simplified version of isatools.model.OntologyAnnotation that can be used
    when the original isatools package is not available.
    """
    def __init__(self, term="", term_accession="", term_source=""):
        self.term = term
        self.term_accession = term_accession
        self.term_source = term_source

    def __repr__(self):
        return f"OntologyAnnotation(term='{self.term}', term_accession='{self.term_accession}', term_source='{self.term_source}')"

    def __eq__(self, other):
        if not isinstance(other, OntologyAnnotation):
            return False
        return (self.term == other.term and 
                self.term_accession == other.term_accession and 
                self.term_source == other.term_source)

    def __hash__(self):
        return hash((self.term, self.term_accession, self.term_source))


def get_isa_objects():
    """
    Try to import isatools and return the necessary classes and functions.
    If isatools is not available, return our compatibility versions.

    Returns:
        tuple: (isatab, OntologyAnnotation, Investigation, Study, Assay, Process, Material, DataFile)
    """
    try:
        from isatools import isatab
        from isatools.model import OntologyAnnotation as IsaOntologyAnnotation
        from isatools.model import Investigation, Study, Assay, Process, Material, DataFile

        return (isatab, IsaOntologyAnnotation, Investigation, Study, Assay, Process, Material, DataFile)

    except ImportError:
        # If isatools is not available, return our compatibility versions
        # For now, only OntologyAnnotation is implemented
        # Other classes would need to be implemented as needed

        class DummyIsatab:
            @staticmethod
            def load(file_path):
                raise NotImplementedError(
                    "isatools is required for loading ISA-Tab files. "
                    "Please install Python 3.9 and isatools to use this feature."
                )

        class DummyClass:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError(
                    "isatools is required for this functionality. "
                    "Please install Python 3.9 and isatools to use this feature."
                )

        return (
            DummyIsatab(),
            OntologyAnnotation,
            DummyClass,  # Investigation
            DummyClass,  # Study
            DummyClass,  # Assay
            DummyClass,  # Process
            DummyClass,  # Material
            DummyClass,  # DataFile
        )
