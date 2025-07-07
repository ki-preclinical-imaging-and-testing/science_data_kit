# Clinical Trial Dataset

## Overview

This dataset contains simulated clinical trial data designed for educational and demonstration purposes. It represents a comprehensive collection of data from a randomized, double-blind, placebo-controlled Phase 3 clinical trial evaluating the efficacy and safety of a novel treatment for Type 2 Diabetes Mellitus.

The dataset is structured to mimic realistic clinical trial data collected during a multi-center study. It includes patient demographics, medical history, laboratory measurements, treatment administration, adverse events, and efficacy outcomes.

## Dataset Structure

The dataset consists of six CSV files:

1. **patients.csv**: Contains demographic information about the trial participants, including patient ID, site ID, age, sex, race, ethnicity, height, weight, BMI, and enrollment date.
2. **sites.csv**: Contains information about the clinical trial sites, including site ID, location, principal investigator, and enrollment target.
3. **visits.csv**: Contains information about patient visits, including visit ID, patient ID, visit type, date, and status.
4. **labs.csv**: Contains laboratory measurements for each patient at each visit, including lab ID, patient ID, visit ID, test name, value, unit, reference range, and flags.
5. **treatments.csv**: Contains information about treatment administration, including treatment ID, patient ID, visit ID, treatment arm, dose, administration date, and compliance.
6. **adverse_events.csv**: Contains information about adverse events, including event ID, patient ID, start date, end date, severity, relatedness to treatment, action taken, and outcome.

## Study Design

### Study Overview

This simulated clinical trial (Study ID: CT-DM-001) is a Phase 3, randomized, double-blind, placebo-controlled study evaluating the efficacy and safety of a novel GLP-1 receptor agonist (GLP-1-RA) in patients with Type 2 Diabetes Mellitus. The study enrolled 300 patients across 15 clinical sites in the United States.

### Treatment Arms

Patients were randomized in a 2:1 ratio to receive either:
- **Active Treatment**: Novel GLP-1 receptor agonist (10 mg once daily)
- **Placebo**: Matching placebo (once daily)

### Study Duration

The study duration was 24 weeks, with a 4-week screening period and a 4-week follow-up period.

### Visit Schedule

- **Screening Visit (V1)**: Week -4
- **Baseline Visit (V2)**: Week 0 (Randomization)
- **Treatment Visits**: Weeks 4 (V3), 8 (V4), 12 (V5), 16 (V6), 20 (V7)
- **End of Treatment Visit (V8)**: Week 24
- **Follow-up Visit (V9)**: Week 28

### Primary Endpoint

The primary endpoint was the change from baseline in HbA1c at Week 24.

### Secondary Endpoints

- Change from baseline in fasting plasma glucose at Week 24
- Proportion of patients achieving HbA1c < 7.0% at Week 24
- Change from baseline in body weight at Week 24
- Incidence of treatment-emergent adverse events

## Data Collection

### Patient Demographics

Patient demographics include age, sex, race, ethnicity, height, weight, and BMI. The study enrolled adult patients (age 18-75) with Type 2 Diabetes Mellitus and HbA1c between 7.0% and 10.0%.

### Laboratory Measurements

Laboratory measurements were collected at each visit and include:
- **Glycemic Parameters**: HbA1c, fasting plasma glucose
- **Lipid Panel**: Total cholesterol, LDL, HDL, triglycerides
- **Renal Function**: Serum creatinine, eGFR, urine albumin-to-creatinine ratio
- **Liver Function**: ALT, AST, alkaline phosphatase, total bilirubin
- **Other**: Complete blood count, electrolytes, vital signs

### Treatment Administration

Treatment administration records include the treatment arm, dose, administration date, and compliance. Compliance was calculated as the percentage of prescribed doses taken between visits.

### Adverse Events

Adverse events were recorded throughout the study and include the start date, end date, severity (mild, moderate, severe), relatedness to treatment (not related, possibly related, probably related, definitely related), action taken (none, dose reduced, treatment interrupted, treatment discontinued), and outcome (resolved, resolving, not resolved, resolved with sequelae, fatal).

## Usage

This dataset can be used for:

1. **Educational purposes**: Teaching students about clinical trial data and analysis
2. **Software development**: Testing data analysis and visualization tools for clinical trial data
3. **Method development**: Developing and testing new methods for analyzing clinical trial data
4. **Workshop demonstrations**: Demonstrating the capabilities of the Science Data Kit for analyzing clinical trial data

## Loading the Dataset

The dataset can be loaded into the Science Data Kit using the following command:

```python
from science_data_kit.data.samples.load_clinical_trial_dataset import main
main()
```

This will create the dataset files if they don't exist and load the data into the Neo4j database.

## Data Model

The dataset is loaded into Neo4j with the following data model:

- **Nodes**:
  - `Patient`: Represents a clinical trial participant
  - `Site`: Represents a clinical trial site
  - `Visit`: Represents a patient visit
  - `Lab`: Represents a laboratory measurement
  - `Treatment`: Represents a treatment administration
  - `AdverseEvent`: Represents an adverse event

- **Relationships**:
  - `(Patient)-[:ENROLLED_AT]->(Site)`: A patient is enrolled at a site
  - `(Visit)-[:FOR_PATIENT]->(Patient)`: A visit is for a patient
  - `(Lab)-[:COLLECTED_AT]->(Visit)`: A lab measurement is collected at a visit
  - `(Lab)-[:FOR_PATIENT]->(Patient)`: A lab measurement is for a patient
  - `(Treatment)-[:ADMINISTERED_AT]->(Visit)`: A treatment is administered at a visit
  - `(Treatment)-[:FOR_PATIENT]->(Patient)`: A treatment is for a patient
  - `(AdverseEvent)-[:EXPERIENCED_BY]->(Patient)`: An adverse event is experienced by a patient

## Example Queries

Here are some example Cypher queries that can be used to explore the dataset:

### Get all patients in the active treatment arm

```cypher
MATCH (p:Patient {dataset: 'clinical_trial'})
WHERE p.treatment_arm = 'Active'
RETURN p
```

### Get HbA1c measurements over time for a specific patient

```cypher
MATCH (l:Lab)-[:FOR_PATIENT]->(p:Patient {patient_id: 'P001'})
WHERE l.test_name = 'HbA1c'
RETURN l.visit_id, l.value
ORDER BY l.visit_id
```

### Compare mean HbA1c change from baseline between treatment arms

```cypher
MATCH (baseline:Lab)-[:FOR_PATIENT]->(p:Patient),
      (endpoint:Lab)-[:FOR_PATIENT]->(p)
WHERE baseline.test_name = 'HbA1c' AND baseline.visit_id = 'V2'
  AND endpoint.test_name = 'HbA1c' AND endpoint.visit_id = 'V8'
RETURN p.treatment_arm, 
       avg(endpoint.value - baseline.value) as mean_change,
       count(p) as n
```

### Get adverse events by severity and treatment arm

```cypher
MATCH (ae:AdverseEvent)-[:EXPERIENCED_BY]->(p:Patient)
RETURN p.treatment_arm, ae.severity, count(ae) as count
ORDER BY p.treatment_arm, ae.severity
```

### Get treatment compliance by visit and treatment arm

```cypher
MATCH (t:Treatment)-[:FOR_PATIENT]->(p:Patient)
RETURN p.treatment_arm, t.visit_id, avg(t.compliance) as mean_compliance
ORDER BY p.treatment_arm, t.visit_id
```

## License

This dataset is provided for educational and demonstration purposes only. It contains simulated data and should not be used for clinical decision-making or research purposes.