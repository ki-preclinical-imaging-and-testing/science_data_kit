"""
ISA Utilities for Science Data Kit

This module is deprecated and will be removed in a future version.
Please use the science_data_kit.core.ontology module instead.

This module previously provided utilities for working with ISA (Investigation, Study, Assay) data models.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Type
import pandas as pd
import json
import os
from pathlib import Path

# Import ontology classes from the new module
from science_data_kit.core.ontology import OntologyAnnotation, OntologySource

# Define placeholder classes for type hints
class Investigation: pass
class Study: pass
class Assay: pass
class Protocol: pass
class Person: pass
class Publication: pass
class Source: pass
class Sample: pass
class Material: pass
class Process: pass
class DataFile: pass
class Comment: pass

# Set ISATOOLS_AVAILABLE to False since we're removing isatools
ISATOOLS_AVAILABLE = False

def get_isa_objects() -> Tuple[Type, Type, Type, Type, Type, Type, Type, Type]:
    """
    Get the ISA model classes.

    Returns:
        A tuple containing the ISA model classes:
        (Investigation, Study, Assay, OntologyAnnotation, OntologySource, Protocol, Person, Publication)
    """
    return (
        Investigation, Study, Assay, OntologyAnnotation, OntologySource,
        Protocol, Person, Publication
    )

def get_isa_material_objects() -> Tuple[Type, Type, Type]:
    """
    Get the ISA material classes.

    Returns:
        A tuple containing the ISA material classes:
        (Source, Sample, Material)
    """
    return (Source, Sample, Material)

def get_isa_process_objects() -> Tuple[Type, Type]:
    """
    Get the ISA process classes.

    Returns:
        A tuple containing the ISA process classes:
        (Process, DataFile)
    """
    return (Process, DataFile)

def is_isatools_available() -> bool:
    """
    Check if isatools is available.

    Returns:
        True if isatools is available, False otherwise.
    """
    return ISATOOLS_AVAILABLE

def create_ontology_annotation(
    term: str,
    term_source: Optional[Union[str, OntologySource]] = None,
    term_accession: Optional[str] = None
) -> OntologyAnnotation:
    """
    Create an OntologyAnnotation object.

    Args:
        term: The term to annotate.
        term_source: The source of the term, either as a string or an OntologySource object.
        term_accession: The accession number of the term.

    Returns:
        An OntologyAnnotation object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    annotation = OntologyAnnotation(term=term)

    if term_source:
        if isinstance(term_source, str):
            source = OntologySource(name=term_source)
            annotation.term_source = source
        else:
            annotation.term_source = term_source

    if term_accession:
        annotation.term_accession = term_accession

    return annotation

def create_investigation(
    identifier: str,
    title: str,
    description: Optional[str] = None,
    submission_date: Optional[str] = None,
    public_release_date: Optional[str] = None
) -> Investigation:
    """
    Create an Investigation object.

    Args:
        identifier: The identifier of the investigation.
        title: The title of the investigation.
        description: The description of the investigation.
        submission_date: The submission date of the investigation.
        public_release_date: The public release date of the investigation.

    Returns:
        An Investigation object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    investigation = Investigation(
        identifier=identifier,
        title=title,
        description=description,
        submission_date=submission_date,
        public_release_date=public_release_date
    )

    return investigation

def create_study(
    identifier: str,
    title: str,
    description: Optional[str] = None,
    submission_date: Optional[str] = None,
    public_release_date: Optional[str] = None,
    filename: Optional[str] = None
) -> Study:
    """
    Create a Study object.

    Args:
        identifier: The identifier of the study.
        title: The title of the study.
        description: The description of the study.
        submission_date: The submission date of the study.
        public_release_date: The public release date of the study.
        filename: The filename of the study.

    Returns:
        A Study object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    study = Study(
        identifier=identifier,
        title=title,
        description=description,
        submission_date=submission_date,
        public_release_date=public_release_date,
        filename=filename
    )

    return study

def create_assay(
    measurement_type: Union[str, OntologyAnnotation],
    technology_type: Union[str, OntologyAnnotation],
    filename: Optional[str] = None
) -> Assay:
    """
    Create an Assay object.

    Args:
        measurement_type: The measurement type of the assay.
        technology_type: The technology type of the assay.
        filename: The filename of the assay.

    Returns:
        An Assay object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    # Convert string to OntologyAnnotation if needed
    if isinstance(measurement_type, str):
        measurement_type = OntologyAnnotation(term=measurement_type)

    if isinstance(technology_type, str):
        technology_type = OntologyAnnotation(term=technology_type)

    assay = Assay(
        measurement_type=measurement_type,
        technology_type=technology_type,
        filename=filename
    )

    return assay

def investigation_to_dict(investigation: Investigation) -> Dict[str, Any]:
    """
    Convert an Investigation object to a dictionary.

    Args:
        investigation: The Investigation object to convert.

    Returns:
        A dictionary representation of the Investigation object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    # Basic investigation attributes
    result = {
        "identifier": investigation.identifier,
        "title": investigation.title,
        "description": investigation.description,
        "submission_date": investigation.submission_date,
        "public_release_date": investigation.public_release_date,
        "studies": []
    }

    # Add studies
    for study in investigation.studies:
        study_dict = {
            "identifier": study.identifier,
            "title": study.title,
            "description": study.description,
            "submission_date": study.submission_date,
            "public_release_date": study.public_release_date,
            "filename": study.filename,
            "assays": []
        }

        # Add assays
        for assay in study.assays:
            assay_dict = {
                "measurement_type": assay.measurement_type.term if assay.measurement_type else None,
                "technology_type": assay.technology_type.term if assay.technology_type else None,
                "filename": assay.filename
            }
            study_dict["assays"].append(assay_dict)

        result["studies"].append(study_dict)

    return result

def dict_to_investigation(data: Dict[str, Any]) -> Investigation:
    """
    Convert a dictionary to an Investigation object.

    Args:
        data: The dictionary to convert.

    Returns:
        An Investigation object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    # Create investigation
    investigation = Investigation(
        identifier=data.get("identifier", ""),
        title=data.get("title", ""),
        description=data.get("description", ""),
        submission_date=data.get("submission_date", ""),
        public_release_date=data.get("public_release_date", "")
    )

    # Add studies
    for study_data in data.get("studies", []):
        study = Study(
            identifier=study_data.get("identifier", ""),
            title=study_data.get("title", ""),
            description=study_data.get("description", ""),
            submission_date=study_data.get("submission_date", ""),
            public_release_date=study_data.get("public_release_date", ""),
            filename=study_data.get("filename", "")
        )

        # Add assays
        for assay_data in study_data.get("assays", []):
            measurement_type = OntologyAnnotation(term=assay_data.get("measurement_type", ""))
            technology_type = OntologyAnnotation(term=assay_data.get("technology_type", ""))

            assay = Assay(
                measurement_type=measurement_type,
                technology_type=technology_type,
                filename=assay_data.get("filename", "")
            )

            study.assays.append(assay)

        investigation.studies.append(study)

    return investigation

def save_investigation_to_json(
    investigation: Investigation,
    output_path: Union[str, Path]
) -> None:
    """
    Save an Investigation object to a JSON file.

    Args:
        investigation: The Investigation object to save.
        output_path: The path to save the JSON file.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    # Convert to dictionary
    data = investigation_to_dict(investigation)

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_investigation_from_json(
    input_path: Union[str, Path]
) -> Investigation:
    """
    Load an Investigation object from a JSON file.

    Args:
        input_path: The path to the JSON file.

    Returns:
        An Investigation object.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    # Load from JSON
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Convert to Investigation
    return dict_to_investigation(data)

def dataframe_to_sources(
    df: pd.DataFrame,
    name_column: str,
    characteristics_columns: Optional[List[str]] = None
) -> List[Source]:
    """
    Convert a DataFrame to a list of Source objects.

    Args:
        df: The DataFrame to convert.
        name_column: The column containing the source names.
        characteristics_columns: Optional list of columns to use as characteristics.

    Returns:
        A list of Source objects.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    sources = []

    for _, row in df.iterrows():
        source = Source(name=row[name_column])

        # Add characteristics
        if characteristics_columns:
            for col in characteristics_columns:
                if col in row and not pd.isna(row[col]):
                    characteristic = OntologyAnnotation(term=col)
                    source.characteristics[characteristic] = [OntologyAnnotation(term=str(row[col]))]

        sources.append(source)

    return sources

def dataframe_to_samples(
    df: pd.DataFrame,
    name_column: str,
    characteristics_columns: Optional[List[str]] = None
) -> List[Sample]:
    """
    Convert a DataFrame to a list of Sample objects.

    Args:
        df: The DataFrame to convert.
        name_column: The column containing the sample names.
        characteristics_columns: Optional list of columns to use as characteristics.

    Returns:
        A list of Sample objects.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    samples = []

    for _, row in df.iterrows():
        sample = Sample(name=row[name_column])

        # Add characteristics
        if characteristics_columns:
            for col in characteristics_columns:
                if col in row and not pd.isna(row[col]):
                    characteristic = OntologyAnnotation(term=col)
                    sample.characteristics[characteristic] = [OntologyAnnotation(term=str(row[col]))]

        samples.append(sample)

    return samples

def dataframe_to_materials(
    df: pd.DataFrame,
    name_column: str,
    type_column: Optional[str] = None,
    characteristics_columns: Optional[List[str]] = None
) -> List[Material]:
    """
    Convert a DataFrame to a list of Material objects.

    Args:
        df: The DataFrame to convert.
        name_column: The column containing the material names.
        type_column: Optional column containing the material types.
        characteristics_columns: Optional list of columns to use as characteristics.

    Returns:
        A list of Material objects.

    Raises:
        ImportError: If isatools is not available.
    """
    if not ISATOOLS_AVAILABLE:
        raise ImportError("isatools is not available. Please install it first.")

    materials = []

    for _, row in df.iterrows():
        # Create material type if specified
        material_type = None
        if type_column and type_column in row and not pd.isna(row[type_column]):
            material_type = OntologyAnnotation(term=row[type_column])

        material = Material(name=row[name_column], type=material_type)

        # Add characteristics
        if characteristics_columns:
            for col in characteristics_columns:
                if col in row and not pd.isna(row[col]):
                    characteristic = OntologyAnnotation(term=col)
                    material.characteristics[characteristic] = [OntologyAnnotation(term=str(row[col]))]

        materials.append(material)

    return materials
