# Science Data Kit (SDK) Research Use Cases Guide

## Overview

This guide provides examples of how the Science Data Kit (SDK) can be applied to different research scenarios. It demonstrates the versatility and power of the SDK for various scientific domains and data analysis tasks.

## Use Case 1: Preclinical Cancer Research

### Scenario
A cancer research lab is conducting preclinical studies to evaluate the efficacy of novel drug compounds on patient-derived xenograft (PDX) models.

### Data Types
- Animal metadata (strain, age, sex)
- Treatment data (drug, dose, schedule)
- Tumor measurements (volume, weight)
- Imaging data (histology, fluorescence)
- Gene expression data
- Survival data

### SDK Application
```python
# Connect to database
from science_data_kit.core.database import DatabaseManager
db_manager = DatabaseManager()
db_manager.connect_to_neo4j(uri="bolt://localhost:7687", username="neo4j", password="password")

# Query for all animals treated with compound X
query = """
MATCH (a:Animal)-[:RECEIVED]->(t:Treatment {compound: 'Compound X'})
MATCH (a)-[:HAS_MEASUREMENT]->(m:TumorMeasurement)
RETURN a.id, a.strain, a.sex, t.dose, m.day, m.volume
ORDER BY a.id, m.day
"""
results = db_manager.query(query)

# Analyze tumor growth rates
import pandas as pd
import matplotlib.pyplot as plt
from science_data_kit.analysis.growth_models import fit_exponential_growth

df = pd.DataFrame(results)
animals = df['a.id'].unique()

plt.figure(figsize=(10, 6))
for animal in animals:
    animal_data = df[df['a.id'] == animal]
    days = animal_data['m.day'].values
    volumes = animal_data['m.volume'].values
    
    # Fit growth model
    params, fitted_curve = fit_exponential_growth(days, volumes)
    
    # Plot data and fitted curve
    plt.scatter(days, volumes, label=f"Animal {animal} (data)")
    plt.plot(days, fitted_curve, '--', label=f"Animal {animal} (model)")

plt.xlabel('Day')
plt.ylabel('Tumor Volume (mm³)')
plt.title('Tumor Growth Curves for Animals Treated with Compound X')
plt.legend()
plt.grid(True)
plt.show()

# Export results
from science_data_kit.export.data_export import export_to_csv
export_to_csv(results, "compound_x_tumor_growth.csv")
```

### Benefits
- Integrated analysis of heterogeneous data types
- Automated growth curve fitting
- Easy visualization of treatment effects
- Streamlined data export for publication

## Use Case 2: Multi-omics Integration

### Scenario
A systems biology lab is integrating transcriptomics, proteomics, and metabolomics data to understand cellular responses to environmental stressors.

### Data Types
- RNA-seq data (gene expression)
- Proteomics data (protein abundance)
- Metabolomics data (metabolite levels)
- Experimental conditions (stressor type, duration, concentration)

### SDK Application
```python
# Load multi-omics data
from science_data_kit.data_integration.omics_loader import load_omics_data

transcriptomics = load_omics_data("transcriptomics.csv", data_type="transcriptomics")
proteomics = load_omics_data("proteomics.csv", data_type="proteomics")
metabolomics = load_omics_data("metabolomics.csv", data_type="metabolomics")

# Perform integrated analysis
from science_data_kit.analysis.multi_omics import integrate_omics_data, pathway_enrichment

# Integrate data
integrated_data = integrate_omics_data([transcriptomics, proteomics, metabolomics])

# Identify enriched pathways
enriched_pathways = pathway_enrichment(integrated_data, pathway_database="KEGG")

# Visualize results
from science_data_kit.visualization.network_viz import create_pathway_network

# Create interactive network visualization
network = create_pathway_network(enriched_pathways, threshold=0.05)
network.show()

# Export results for publication
from science_data_kit.export.report_generator import generate_multi_omics_report
generate_multi_omics_report(integrated_data, enriched_pathways, "multi_omics_analysis_report.html")
```

### Benefits
- Seamless integration of multiple omics data types
- Automated pathway enrichment analysis
- Interactive network visualization
- Comprehensive report generation

## Use Case 3: Clinical Trial Data Analysis

### Scenario
A clinical research team is analyzing data from a multi-center clinical trial testing a new therapy for autoimmune disease.

### Data Types
- Patient demographics
- Medical history
- Treatment assignments
- Longitudinal clinical measurements
- Adverse events
- Biomarker data

### SDK Application
```python
# Connect to clinical trial database
from science_data_kit.core.database import DatabaseManager
db_manager = DatabaseManager()
db_manager.connect_to_sql(connection_string="postgresql://username:password@localhost:5432/clinical_trial_db")

# Load patient data
from science_data_kit.data_integration.clinical_data import load_clinical_data
patient_data = load_clinical_data(db_manager, study_id="CT-2023-001")

# Perform survival analysis
from science_data_kit.analysis.survival import kaplan_meier, cox_proportional_hazards
from science_data_kit.visualization.survival_plots import plot_survival_curves

# Create treatment groups
treatment_group = patient_data[patient_data['arm'] == 'Treatment']
control_group = patient_data[patient_data['arm'] == 'Placebo']

# Perform Kaplan-Meier analysis
km_results = kaplan_meier([treatment_group, control_group], 
                         time_column='days_to_event', 
                         event_column='event_occurred',
                         group_labels=['Treatment', 'Placebo'])

# Plot survival curves
plot_survival_curves(km_results, title="Treatment vs. Placebo Survival Curves")

# Perform Cox proportional hazards analysis
covariates = ['age', 'sex', 'baseline_severity', 'arm']
cox_results = cox_proportional_hazards(patient_data, 
                                      time_column='days_to_event', 
                                      event_column='event_occurred',
                                      covariates=covariates)

# Print hazard ratios and p-values
print(cox_results.summary())

# Generate statistical report
from science_data_kit.export.clinical_reports import generate_clinical_trial_report
generate_clinical_trial_report(patient_data, km_results, cox_results, "clinical_trial_report.pdf")
```

### Benefits
- Standardized clinical data loading
- Advanced statistical analysis
- Publication-quality survival curves
- Comprehensive clinical trial reporting

## Use Case 4: Environmental Monitoring and Modeling

### Scenario
An environmental science team is analyzing water quality data from multiple monitoring stations to assess pollution trends and predict future conditions.

### Data Types
- Water quality measurements (pH, dissolved oxygen, temperature, contaminants)
- Weather data
- Geographic information
- Time series data from monitoring stations

### SDK Application
```python
# Load environmental monitoring data
from science_data_kit.data_integration.environmental_data import load_monitoring_data
monitoring_data = load_monitoring_data("monitoring_stations.csv", "measurements.csv")

# Perform time series analysis
from science_data_kit.analysis.time_series import detect_anomalies, trend_analysis
from science_data_kit.visualization.geo_viz import create_pollution_map

# Detect anomalies in dissolved oxygen levels
anomalies = detect_anomalies(monitoring_data, 
                            parameter="dissolved_oxygen",
                            method="isolation_forest")

# Analyze trends in contaminant levels
trends = trend_analysis(monitoring_data, 
                       parameter="lead_concentration",
                       period="monthly")

# Create interactive map of pollution levels
pollution_map = create_pollution_map(monitoring_data, 
                                    parameter="lead_concentration",
                                    time_point="2023-06-01")
pollution_map.save("pollution_map.html")

# Train predictive model
from science_data_kit.ml.environmental_models import train_water_quality_model
model = train_water_quality_model(monitoring_data, 
                                 target="dissolved_oxygen",
                                 features=["temperature", "rainfall", "pH"])

# Make predictions
future_conditions = model.predict(new_data)

# Generate comprehensive report
from science_data_kit.export.environmental_reports import generate_monitoring_report
generate_monitoring_report(monitoring_data, anomalies, trends, model, "water_quality_report.pdf")
```

### Benefits
- Integrated analysis of spatial and temporal data
- Automated anomaly detection
- Interactive geospatial visualization
- Predictive modeling capabilities

## Use Case 5: Genomics Research

### Scenario
A genomics lab is analyzing whole genome sequencing data to identify variants associated with a rare genetic disorder.

### Data Types
- Whole genome sequencing data
- Patient phenotype data
- Family pedigree information
- Population frequency data

### SDK Application
```python
# Load genomic data
from science_data_kit.data_integration.genomics import load_vcf_data, load_phenotype_data
variant_data = load_vcf_data("samples.vcf")
phenotype_data = load_phenotype_data("patient_phenotypes.csv")

# Filter variants
from science_data_kit.analysis.variant_analysis import filter_variants, annotate_variants
filtered_variants = filter_variants(variant_data,
                                  min_quality=30,
                                  max_population_freq=0.01)

# Annotate variants with functional information
annotated_variants = annotate_variants(filtered_variants, 
                                     annotation_db="ensembl")

# Perform association analysis
from science_data_kit.analysis.association import variant_phenotype_association
associations = variant_phenotype_association(annotated_variants,
                                           phenotype_data,
                                           phenotype="disease_status")

# Visualize results
from science_data_kit.visualization.genomic_viz import manhattan_plot, gene_network
manhattan_plot(associations, title="Variant-Disease Associations")

# Create gene interaction network for top hits
top_genes = associations[associations['p_value'] < 1e-5]['gene'].unique()
network = gene_network(top_genes, interaction_db="string")
network.show()

# Export results
from science_data_kit.export.genomic_reports import generate_variant_report
generate_variant_report(associations, annotated_variants, "variant_analysis_report.html")
```

### Benefits
- Streamlined genomic data processing
- Integrated variant annotation
- Statistical association testing
- Interactive visualization of genomic data

## Conclusion

The Science Data Kit provides powerful tools for a wide range of research scenarios across different scientific domains. By integrating data management, analysis, visualization, and reporting capabilities, the SDK enables researchers to focus on scientific questions rather than technical implementation details.

For more information on how to apply the SDK to your specific research needs, please refer to the [Next Steps Guide](next_steps.md) and the [SDK Documentation](https://science-data-kit.readthedocs.io/).