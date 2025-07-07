# Genomics Dataset

## Overview

This dataset contains simulated genomics data designed for educational and demonstration purposes. It represents a comprehensive collection of data from a multi-omics study investigating genetic factors associated with response to cancer immunotherapy.

The dataset is structured to mimic realistic genomics data collected in a translational research setting. It includes patient clinical data, whole exome sequencing (WES) data, RNA sequencing (RNA-seq) data, and immunotherapy response data.

## Dataset Structure

The dataset consists of five CSV files:

1. **patients.csv**: Contains clinical information about the patients, including patient ID, age, sex, cancer type, cancer stage, prior treatments, and ECOG performance status.
2. **samples.csv**: Contains information about the biological samples collected from each patient, including sample ID, patient ID, sample type, collection date, and quality metrics.
3. **mutations.csv**: Contains somatic mutation data from whole exome sequencing, including mutation ID, sample ID, chromosome, position, reference allele, alternate allele, gene, variant type, and functional impact.
4. **expression.csv**: Contains gene expression data from RNA sequencing, including gene ID, sample ID, gene symbol, transcript ID, and normalized expression values (TPM).
5. **response.csv**: Contains immunotherapy response data, including patient ID, treatment type, response category (RECIST criteria), progression-free survival (days), and overall survival (days).

## Study Design

### Study Overview

This simulated genomics study (Study ID: GEN-IO-001) investigates genetic determinants of response to immune checkpoint inhibitors in patients with advanced solid tumors. The study enrolled 100 patients with various cancer types who received either anti-PD-1 or anti-PD-L1 immunotherapy.

### Cancer Types

The study includes patients with the following cancer types:
- Non-small cell lung cancer (NSCLC)
- Melanoma
- Renal cell carcinoma (RCC)
- Urothelial carcinoma
- Head and neck squamous cell carcinoma (HNSCC)

### Sample Collection

For each patient, the following samples were collected:
- Tumor biopsy (pre-treatment)
- Adjacent normal tissue (when available)
- Peripheral blood

### Genomic Analyses

The following genomic analyses were performed:
- **Whole Exome Sequencing (WES)**: To identify somatic mutations, tumor mutational burden, and specific genetic alterations
- **RNA Sequencing (RNA-seq)**: To measure gene expression profiles and identify gene signatures associated with response

### Response Assessment

Treatment response was assessed using RECIST 1.1 criteria:
- Complete Response (CR)
- Partial Response (PR)
- Stable Disease (SD)
- Progressive Disease (PD)

Survival outcomes were also recorded:
- Progression-free survival (PFS)
- Overall survival (OS)

## Data Collection

### Patient Clinical Data

Patient clinical data includes demographic information (age, sex), disease characteristics (cancer type, stage), and treatment history. All patients had advanced or metastatic disease (stage III or IV) and had received at least one prior line of therapy.

### Mutation Data

Mutation data from whole exome sequencing includes:
- **Genomic Coordinates**: Chromosome, position
- **Variant Information**: Reference allele, alternate allele
- **Annotation**: Gene, variant type (missense, nonsense, frameshift, etc.), functional impact (high, moderate, low, modifier)
- **Metrics**: Variant allele frequency (VAF), coverage depth

Key cancer-related genes were captured, including:
- Tumor suppressor genes (TP53, PTEN, RB1, etc.)
- Oncogenes (KRAS, BRAF, PIK3CA, etc.)
- DNA repair genes (BRCA1, BRCA2, MLH1, etc.)
- Immune-related genes (B2M, JAK1, JAK2, etc.)

### Expression Data

Expression data from RNA sequencing includes:
- **Gene Information**: Gene symbol, Ensembl ID
- **Expression Values**: Transcripts Per Million (TPM)
- **Pathway Enrichment**: Immune-related pathways, cancer-related pathways

Key immune-related gene signatures were captured, including:
- T cell infiltration markers (CD8A, CD4, GZMA, PRF1, etc.)
- Immune checkpoint molecules (PD-1, PD-L1, CTLA-4, etc.)
- Interferon-gamma signaling (IFNG, STAT1, IRF1, etc.)
- Antigen presentation (HLA genes, B2M, TAP1, etc.)

### Response Data

Response data includes:
- **RECIST Assessment**: Best overall response (CR, PR, SD, PD)
- **Response Category**: Responder (CR/PR) vs. Non-responder (SD/PD)
- **Survival Outcomes**: Progression-free survival (days), overall survival (days)
- **Treatment Information**: Immunotherapy type (anti-PD-1 or anti-PD-L1), duration of therapy

## Usage

This dataset can be used for:

1. **Educational purposes**: Teaching students about genomics data analysis and interpretation
2. **Software development**: Testing data analysis and visualization tools for genomics data
3. **Method development**: Developing and testing new methods for analyzing multi-omics data
4. **Workshop demonstrations**: Demonstrating the capabilities of the Science Data Kit for analyzing genomics data

## Loading the Dataset

The dataset can be loaded into the Science Data Kit using the following command:

```python
from science_data_kit.data.samples.load_genomics_dataset import main
main()
```

This will create the dataset files if they don't exist and load the data into the Neo4j database.

## Data Model

The dataset is loaded into Neo4j with the following data model:

- **Nodes**:
  - `Patient`: Represents a patient in the study
  - `Sample`: Represents a biological sample
  - `Mutation`: Represents a somatic mutation
  - `Gene`: Represents a gene
  - `Expression`: Represents gene expression in a sample
  - `Response`: Represents treatment response data

- **Relationships**:
  - `(Sample)-[:COLLECTED_FROM]->(Patient)`: A sample is collected from a patient
  - `(Mutation)-[:FOUND_IN]->(Sample)`: A mutation is found in a sample
  - `(Mutation)-[:AFFECTS]->(Gene)`: A mutation affects a gene
  - `(Expression)-[:MEASURED_IN]->(Sample)`: Gene expression is measured in a sample
  - `(Expression)-[:OF_GENE]->(Gene)`: Expression data is of a specific gene
  - `(Response)-[:FOR_PATIENT]->(Patient)`: Response data is for a patient

## Example Queries

Here are some example Cypher queries that can be used to explore the dataset:

### Get patients with specific mutations

```cypher
MATCH (p:Patient)<-[:COLLECTED_FROM]-(s:Sample)<-[:FOUND_IN]-(m:Mutation)-[:AFFECTS]->(g:Gene)
WHERE g.symbol = 'TP53' AND m.functional_impact = 'HIGH'
RETURN p.patient_id, p.cancer_type, m.variant_type
```

### Compare gene expression between responders and non-responders

```cypher
MATCH (p:Patient)<-[:FOR_PATIENT]-(r:Response),
      (p)<-[:COLLECTED_FROM]-(s:Sample)<-[:MEASURED_IN]-(e:Expression)-[:OF_GENE]->(g:Gene)
WHERE g.symbol = 'CD8A' AND s.sample_type = 'Tumor'
RETURN r.response_category, avg(e.tpm) as avg_expression
```

### Get tumor mutational burden and correlate with response

```cypher
MATCH (p:Patient)<-[:COLLECTED_FROM]-(s:Sample)<-[:FOUND_IN]-(m:Mutation),
      (p)<-[:FOR_PATIENT]-(r:Response)
WHERE s.sample_type = 'Tumor'
WITH p, r, count(m) as mutation_count
RETURN r.response_category, avg(mutation_count) as avg_tmb, count(p) as patient_count
ORDER BY avg_tmb DESC
```

### Find genes with differential expression between responders and non-responders

```cypher
MATCH (p:Patient)<-[:FOR_PATIENT]-(r:Response),
      (p)<-[:COLLECTED_FROM]-(s:Sample)<-[:MEASURED_IN]-(e:Expression)-[:OF_GENE]->(g:Gene)
WHERE s.sample_type = 'Tumor'
WITH g, r.response_category as response, avg(e.tpm) as avg_expr
ORDER BY g.symbol, response
WITH g, collect(response) as responses, collect(avg_expr) as expressions
WHERE size(responses) > 1
RETURN g.symbol, 
       expressions[0] as non_responder_expr, 
       expressions[1] as responder_expr,
       expressions[1] / expressions[0] as fold_change
ORDER BY fold_change DESC
LIMIT 20
```

### Get survival outcomes by mutation status

```cypher
MATCH (p:Patient)<-[:COLLECTED_FROM]-(s:Sample)<-[:FOUND_IN]-(m:Mutation)-[:AFFECTS]->(g:Gene),
      (p)<-[:FOR_PATIENT]-(r:Response)
WHERE g.symbol = 'BRAF' AND m.variant_type = 'missense' AND s.sample_type = 'Tumor'
WITH p, r, count(m) > 0 as has_mutation
RETURN has_mutation, 
       avg(r.progression_free_survival) as avg_pfs,
       avg(r.overall_survival) as avg_os,
       count(p) as patient_count
```

## License

This dataset is provided for educational and demonstration purposes only. It contains simulated data and should not be used for clinical decision-making or research purposes.