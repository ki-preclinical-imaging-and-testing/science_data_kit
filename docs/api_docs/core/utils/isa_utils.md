# isa_utils.py - ISA Utilities

This module provides utilities for working with ISA (Investigation, Study, Assay) data models. It includes functions for importing, exporting, and manipulating ISA data.

## Functions

### get_isa_objects

```python
def get_isa_objects() -> Tuple[Type, Type, Type, Type, Type, Type, Type, Type]
```

Get the ISA model classes.

**Returns:**
- A tuple containing the ISA model classes: (Investigation, Study, Assay, OntologyAnnotation, OntologySource, Protocol, Person, Publication)

### get_isa_material_objects

```python
def get_isa_material_objects() -> Tuple[Type, Type, Type]
```

Get the ISA material classes.

**Returns:**
- A tuple containing the ISA material classes: (Source, Sample, Material)

### get_isa_process_objects

```python
def get_isa_process_objects() -> Tuple[Type, Type]
```

Get the ISA process classes.

**Returns:**
- A tuple containing the ISA process classes: (Process, DataFile)

### is_isatools_available

```python
def is_isatools_available() -> bool
```

Check if isatools is available.

**Returns:**
- True if isatools is available, False otherwise.

### create_ontology_annotation

```python
def create_ontology_annotation(
    term: str,
    term_source: Optional[Union[str, OntologySource]] = None,
    term_accession: Optional[str] = None
) -> OntologyAnnotation
```

Create an OntologyAnnotation object.

**Parameters:**
- `term` (str): The term to annotate.
- `term_source` (str or OntologySource, optional): The source of the term, either as a string or an OntologySource object.
- `term_accession` (str, optional): The accession number of the term.

**Returns:**
- An OntologyAnnotation object.

**Raises:**
- ImportError: If isatools is not available.

### create_investigation

```python
def create_investigation(
    identifier: str,
    title: str,
    description: Optional[str] = None,
    submission_date: Optional[str] = None,
    public_release_date: Optional[str] = None
) -> Investigation
```

Create an Investigation object.

**Parameters:**
- `identifier` (str): The identifier of the investigation.
- `title` (str): The title of the investigation.
- `description` (str, optional): The description of the investigation.
- `submission_date` (str, optional): The submission date of the investigation.
- `public_release_date` (str, optional): The public release date of the investigation.

**Returns:**
- An Investigation object.

**Raises:**
- ImportError: If isatools is not available.

### create_study

```python
def create_study(
    identifier: str,
    title: str,
    description: Optional[str] = None,
    submission_date: Optional[str] = None,
    public_release_date: Optional[str] = None,
    filename: Optional[str] = None
) -> Study
```

Create a Study object.

**Parameters:**
- `identifier` (str): The identifier of the study.
- `title` (str): The title of the study.
- `description` (str, optional): The description of the study.
- `submission_date` (str, optional): The submission date of the study.
- `public_release_date` (str, optional): The public release date of the study.
- `filename` (str, optional): The filename of the study.

**Returns:**
- A Study object.

**Raises:**
- ImportError: If isatools is not available.

### create_assay

```python
def create_assay(
    measurement_type: Union[str, OntologyAnnotation],
    technology_type: Union[str, OntologyAnnotation],
    filename: Optional[str] = None
) -> Assay
```

Create an Assay object.

**Parameters:**
- `measurement_type` (str or OntologyAnnotation): The measurement type of the assay.
- `technology_type` (str or OntologyAnnotation): The technology type of the assay.
- `filename` (str, optional): The filename of the assay.

**Returns:**
- An Assay object.

**Raises:**
- ImportError: If isatools is not available.

### investigation_to_dict

```python
def investigation_to_dict(investigation: Investigation) -> Dict[str, Any]
```

Convert an Investigation object to a dictionary.

**Parameters:**
- `investigation` (Investigation): The Investigation object to convert.

**Returns:**
- A dictionary representation of the Investigation object.

**Raises:**
- ImportError: If isatools is not available.

### dict_to_investigation

```python
def dict_to_investigation(data: Dict[str, Any]) -> Investigation
```

Convert a dictionary to an Investigation object.

**Parameters:**
- `data` (Dict[str, Any]): The dictionary to convert.

**Returns:**
- An Investigation object.

**Raises:**
- ImportError: If isatools is not available.

### save_investigation_to_json

```python
def save_investigation_to_json(
    investigation: Investigation,
    output_path: Union[str, Path]
) -> None
```

Save an Investigation object to a JSON file.

**Parameters:**
- `investigation` (Investigation): The Investigation object to save.
- `output_path` (str or Path): The path to save the JSON file.

**Raises:**
- ImportError: If isatools is not available.

### load_investigation_from_json

```python
def load_investigation_from_json(
    input_path: Union[str, Path]
) -> Investigation
```

Load an Investigation object from a JSON file.

**Parameters:**
- `input_path` (str or Path): The path to the JSON file.

**Returns:**
- An Investigation object.

**Raises:**
- ImportError: If isatools is not available.

### dataframe_to_sources

```python
def dataframe_to_sources(
    df: pd.DataFrame,
    name_column: str,
    characteristics_columns: Optional[List[str]] = None
) -> List[Source]
```

Convert a DataFrame to a list of Source objects.

**Parameters:**
- `df` (pd.DataFrame): The DataFrame to convert.
- `name_column` (str): The column containing the source names.
- `characteristics_columns` (List[str], optional): Optional list of columns to use as characteristics.

**Returns:**
- A list of Source objects.

**Raises:**
- ImportError: If isatools is not available.

### dataframe_to_samples

```python
def dataframe_to_samples(
    df: pd.DataFrame,
    name_column: str,
    characteristics_columns: Optional[List[str]] = None
) -> List[Sample]
```

Convert a DataFrame to a list of Sample objects.

**Parameters:**
- `df` (pd.DataFrame): The DataFrame to convert.
- `name_column` (str): The column containing the sample names.
- `characteristics_columns` (List[str], optional): Optional list of columns to use as characteristics.

**Returns:**
- A list of Sample objects.

**Raises:**
- ImportError: If isatools is not available.

### dataframe_to_materials

```python
def dataframe_to_materials(
    df: pd.DataFrame,
    name_column: str,
    type_column: Optional[str] = None,
    characteristics_columns: Optional[List[str]] = None
) -> List[Material]
```

Convert a DataFrame to a list of Material objects.

**Parameters:**
- `df` (pd.DataFrame): The DataFrame to convert.
- `name_column` (str): The column containing the material names.
- `type_column` (str, optional): Optional column containing the material types.
- `characteristics_columns` (List[str], optional): Optional list of columns to use as characteristics.

**Returns:**
- A list of Material objects.

**Raises:**
- ImportError: If isatools is not available.

## Examples

### Checking ISA Tools Availability

```python
from science_data_kit.core.utils.isa_utils import is_isatools_available

# Check if isatools is available
if is_isatools_available():
    print("ISA Tools is available")
else:
    print("ISA Tools is not available")
```

### Creating ISA Objects

```python
from science_data_kit.core.utils.isa_utils import (
    create_investigation, create_study, create_assay,
    create_ontology_annotation
)

# Create an investigation
investigation = create_investigation(
    identifier="INV-001",
    title="My Investigation",
    description="An example investigation",
    submission_date="2023-01-01",
    public_release_date="2023-06-01"
)

# Create a study
study = create_study(
    identifier="STD-001",
    title="My Study",
    description="An example study",
    submission_date="2023-01-15",
    public_release_date="2023-06-15",
    filename="study.txt"
)

# Add the study to the investigation
investigation.studies.append(study)

# Create an assay
assay = create_assay(
    measurement_type="gene expression profiling",
    technology_type="DNA microarray",
    filename="assay.txt"
)

# Add the assay to the study
study.assays.append(assay)
```

### Converting Between ISA Objects and Dictionaries

```python
from science_data_kit.core.utils.isa_utils import (
    investigation_to_dict, dict_to_investigation,
    save_investigation_to_json, load_investigation_from_json
)

# Convert an investigation to a dictionary
investigation_dict = investigation_to_dict(investigation)

# Convert a dictionary to an investigation
new_investigation = dict_to_investigation(investigation_dict)

# Save an investigation to a JSON file
save_investigation_to_json(investigation, "investigation.json")

# Load an investigation from a JSON file
loaded_investigation = load_investigation_from_json("investigation.json")
```

### Converting DataFrames to ISA Objects

```python
import pandas as pd
from science_data_kit.core.utils.isa_utils import (
    dataframe_to_sources, dataframe_to_samples, dataframe_to_materials
)

# Create a DataFrame with source data
sources_df = pd.DataFrame({
    "name": ["Source1", "Source2", "Source3"],
    "organism": ["Homo sapiens", "Mus musculus", "Rattus norvegicus"],
    "age": [30, 12, 24]
})

# Convert the DataFrame to a list of Source objects
sources = dataframe_to_sources(
    df=sources_df,
    name_column="name",
    characteristics_columns=["organism", "age"]
)

# Create a DataFrame with sample data
samples_df = pd.DataFrame({
    "name": ["Sample1", "Sample2", "Sample3"],
    "tissue": ["blood", "liver", "brain"],
    "treatment": ["control", "drug A", "drug B"]
})

# Convert the DataFrame to a list of Sample objects
samples = dataframe_to_samples(
    df=samples_df,
    name_column="name",
    characteristics_columns=["tissue", "treatment"]
)

# Create a DataFrame with material data
materials_df = pd.DataFrame({
    "name": ["Material1", "Material2", "Material3"],
    "type": ["extract", "extract", "library"],
    "concentration": [10.5, 8.2, 12.7]
})

# Convert the DataFrame to a list of Material objects
materials = dataframe_to_materials(
    df=materials_df,
    name_column="name",
    type_column="type",
    characteristics_columns=["concentration"]
)
```