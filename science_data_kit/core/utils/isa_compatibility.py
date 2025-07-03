"""
Compatibility layer for ontology classes.

This module is deprecated and will be removed in a future version.
Please use the science_data_kit.core.ontology module instead.
"""

from science_data_kit.core.ontology import OntologySource, OntologyAnnotation


def get_isa_objects():
    """
    Return the necessary classes and functions for compatibility with existing code.

    This function is deprecated and will be removed in a future version.
    Please use the science_data_kit.core.ontology module directly instead.

    Returns:
        tuple: (isatab, OntologyAnnotation, Investigation, Study, Assay, Process, Material, DataFile)
        Note: OntologySource is also available but not included in the return tuple.
    """
    # Create dummy classes for compatibility
    class DummyIsatab:
        @staticmethod
        def load(file_path):
            raise NotImplementedError(
                "isatools functionality has been removed. "
                "Please use the science_data_kit.core.ontology module instead."
            )

    class DummyClass:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "isatools functionality has been removed. "
                "Please use the science_data_kit.core.ontology module instead."
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
