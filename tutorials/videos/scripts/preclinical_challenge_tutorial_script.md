# Preclinical Challenge Tutorial Script

## Introduction (0:00-0:45)
Hello and welcome to this video tutorial on the Preclinical Research Challenge in the Science Data Kit. In this tutorial, we'll guide you through analyzing a realistic preclinical cancer research dataset. You'll learn how to load data, analyze experimental design, perform tumor growth analysis, conduct survival analysis, and answer research questions using the Science Data Kit.

## Prerequisites (0:45-1:15)
Before we begin, make sure you have:
- The Science Data Kit installed
- A Neo4j database running
- Basic knowledge of Python and data analysis

If you need help setting these up, please refer to our installation guide in the documentation.

## Overview of the Dataset (1:15-2:00)
The preclinical research dataset we'll be working with contains information about three cancer research experiments:
- EXP001: Immunotherapy for breast cancer
- EXP002: Combination therapy for pancreatic cancer
- EXP003: Gene therapy for lung cancer

The dataset includes experimental design, animal records, treatment protocols, imaging data, and outcomes. This realistic dataset will help you understand how to analyze preclinical research data effectively.

## Challenge 1: Loading the Dataset (2:00-4:00)

### Setting Up (2:00-2:30)
First, let's import the necessary libraries and define some helper functions:

```python
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

# Import Science Data Kit components
from science_data_kit.core.database import get_database_connection
from science_data_kit.data.samples.load_preclinical_dataset import main as load_dataset
from science_data_kit.core.visualization import create_visualization
from science_data_kit.core.analysis import perform_statistical_test

# Helper function to run queries
def run_query(query, params=None):
    """Run a Cypher query and return the results as a pandas DataFrame."""
    connection = get_database_connection()
    results = connection.run_query(query, params)
    return pd.DataFrame([dict(record) for record in results])
```

### Loading the Dataset (2:30-3:00)
Now, let's load the preclinical research dataset into the Neo4j database:

```python
# Load the dataset
print("Loading the preclinical research dataset...")
load_dataset()
print("Dataset loaded successfully!")
```

### Exploring the Dataset Structure (3:00-4:00)
Let's explore the structure of the dataset by running some queries:

```python
# Query to get all experiments
print("Querying all experiments...")
query = """
MATCH (e:Experiment {dataset: 'preclinical_research'})
RETURN e.experiment_id as ID, e.title as Title, e.principal_investigator as PI
"""
experiments_df = run_query(query)
display(experiments_df)

# Query to count nodes by type
print("Counting nodes by type...")
query = """
MATCH (n)
WHERE n.dataset = 'preclinical_research'
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC
"""
counts_df = run_query(query)
display(counts_df)
```

As we can see, the dataset consists of five main node types: Experiment, Animal, Treatment, Imaging, and Outcome. This gives us a good understanding of the dataset structure.

## Challenge 2: Analyzing Experiments and Animal Groups (4:00-6:30)

### Animal Distribution Analysis (4:00-5:15)
Let's analyze how animals are distributed across experiments and treatment groups:

```python
# Query to get animal distribution by experiment and group
query = """
MATCH (a:Animal)-[:PART_OF]->(e:Experiment)
WHERE a.dataset = 'preclinical_research'
RETURN e.experiment_id as Experiment, a.group as Group, count(a) as Count
ORDER BY Experiment, Group
"""
animal_distribution_df = run_query(query)
display(animal_distribution_df)

# Create a visualization of animal distribution
plt.figure(figsize=(10, 6))
sns.barplot(x='Experiment', y='Count', hue='Group', data=animal_distribution_df)
plt.title('Animal Distribution by Experiment and Group')
plt.xlabel('Experiment')
plt.ylabel('Number of Animals')
plt.tight_layout()
plt.show()
```

This visualization shows us how many animals are in each treatment group across the three experiments. We can see that each experiment has a control group and several treatment groups, with a balanced number of animals in each group.

### Treatment Protocol Analysis (5:15-6:30)
Now, let's examine the treatment protocols for each experiment:

```python
# Query to get treatment types by experiment
query = """
MATCH (t:Treatment)-[:PART_OF]->(e:Experiment)
WHERE t.dataset = 'preclinical_research'
RETURN e.experiment_id as Experiment, t.treatment_type as TreatmentType, 
       t.agent as Agent, count(t) as Count
ORDER BY Experiment, TreatmentType
"""
treatment_types_df = run_query(query)
display(treatment_types_df)
```

This query shows us the different treatment types and agents used in each experiment. We can see that:
- EXP001 uses immunotherapy agents
- EXP002 uses combination therapy with multiple agents
- EXP003 uses gene therapy approaches

Understanding the treatment protocols is essential for interpreting the results of the experiments.

## Challenge 3: Tumor Growth Analysis (6:30-9:30)

### Retrieving Tumor Volume Data (6:30-7:15)
Let's analyze tumor growth over time for different treatment groups:

```python
# Query to get tumor volume measurements over time
query = """
MATCH (i:Imaging)-[:MEASURED_FROM]->(a:Animal)-[:PART_OF]->(e:Experiment)
WHERE i.dataset = 'preclinical_research' AND i.measurement_type = 'tumor_volume'
RETURN e.experiment_id as Experiment, a.animal_id as AnimalID, a.group as Group,
       i.day as Day, i.value as TumorVolume
ORDER BY Experiment, AnimalID, Day
"""
tumor_volume_df = run_query(query)
display(tumor_volume_df.head(10))

# Calculate average tumor volume by experiment, group, and day
avg_tumor_volume = tumor_volume_df.groupby(['Experiment', 'Group', 'Day'])['TumorVolume'].mean().reset_index()
display(avg_tumor_volume.head(10))
```

### Visualizing Tumor Growth (7:15-8:15)
Now, let's visualize tumor growth over time for each experiment:

```python
# Visualize tumor growth over time for each experiment
for experiment in avg_tumor_volume['Experiment'].unique():
    plt.figure(figsize=(10, 6))
    exp_data = avg_tumor_volume[avg_tumor_volume['Experiment'] == experiment]
    
    for group in exp_data['Group'].unique():
        group_data = exp_data[exp_data['Group'] == group]
        plt.plot(group_data['Day'], group_data['TumorVolume'], marker='o', label=group)
    
    plt.title(f'Tumor Growth Over Time - {experiment}')
    plt.xlabel('Day')
    plt.ylabel('Average Tumor Volume (mm³)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
```

These visualizations show us how tumor volume changes over time for each treatment group in each experiment. We can see clear differences in tumor growth patterns between the control and treatment groups.

### Statistical Analysis of Tumor Growth (8:15-9:30)
Let's perform statistical analysis to determine if there are significant differences in tumor growth between treatment groups:

```python
# Get final tumor volumes (last day of measurement for each animal)
final_volumes = []

for experiment in tumor_volume_df['Experiment'].unique():
    exp_data = tumor_volume_df[tumor_volume_df['Experiment'] == experiment]
    
    for animal in exp_data['AnimalID'].unique():
        animal_data = exp_data[exp_data['AnimalID'] == animal]
        last_day = animal_data['Day'].max()
        last_measurement = animal_data[animal_data['Day'] == last_day].iloc[0]
        
        final_volumes.append({
            'Experiment': experiment,
            'AnimalID': animal,
            'Group': last_measurement['Group'],
            'FinalDay': last_day,
            'FinalVolume': last_measurement['TumorVolume']
        })

final_volumes_df = pd.DataFrame(final_volumes)
display(final_volumes_df.head(10))

# Perform statistical tests to compare treatment groups
for experiment in final_volumes_df['Experiment'].unique():
    print(f"\nStatistical Analysis for {experiment}:")
    exp_data = final_volumes_df[final_volumes_df['Experiment'] == experiment]
    groups = exp_data['Group'].unique()
    
    # Compare treatment groups to control
    control_data = exp_data[exp_data['Group'] == 'Control']['FinalVolume']
    
    for group in groups:
        if group != 'Control':
            treatment_data = exp_data[exp_data['Group'] == group]['FinalVolume']
            result = perform_statistical_test(control_data, treatment_data, test_type='t-test')
            
            print(f"  {group} vs Control: p-value = {result['p_value']:.4f}")
            if result['p_value'] < 0.05:
                print(f"    Significant difference detected (p < 0.05)")
            else:
                print(f"    No significant difference detected (p >= 0.05)")
```

The statistical analysis shows us which treatment groups have significantly different tumor volumes compared to the control group. This helps us identify effective treatments.

## Challenge 4: Survival Analysis (9:30-12:00)

### Retrieving Survival Data (9:30-10:15)
Now, let's analyze survival outcomes for different treatment groups:

```python
# Query to get survival data
query = """
MATCH (o:Outcome)-[:OUTCOME_OF]->(a:Animal)-[:PART_OF]->(e:Experiment)
WHERE o.dataset = 'preclinical_research' AND o.outcome_type = 'survival'
RETURN e.experiment_id as Experiment, a.animal_id as AnimalID, a.group as Group,
       o.day as Day, o.status as Status
ORDER BY Experiment, Group, Day
"""
survival_df = run_query(query)
display(survival_df.head(10))
```

### Kaplan-Meier Survival Analysis (10:15-11:00)
Let's perform Kaplan-Meier survival analysis for each experiment:

```python
# Import survival analysis libraries
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# Perform Kaplan-Meier survival analysis for each experiment
for experiment in survival_df['Experiment'].unique():
    plt.figure(figsize=(10, 6))
    exp_data = survival_df[survival_df['Experiment'] == experiment]
    
    kmf = KaplanMeierFitter()
    
    for group in exp_data['Group'].unique():
        group_data = exp_data[exp_data['Group'] == group]
        T = group_data['Day']
        E = group_data['Status'].map({'alive': 0, 'dead': 1})
        
        kmf.fit(T, event_observed=E, label=group)
        kmf.plot()
    
    plt.title(f'Kaplan-Meier Survival Curves - {experiment}')
    plt.xlabel('Days')
    plt.ylabel('Survival Probability')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
```

These Kaplan-Meier curves show us the probability of survival over time for each treatment group in each experiment. Higher curves indicate better survival outcomes.

### Log-Rank Tests (11:00-12:00)
Let's perform log-rank tests to statistically compare survival curves:

```python
# Perform log-rank tests to compare survival curves
for experiment in survival_df['Experiment'].unique():
    print(f"\nSurvival Analysis for {experiment}:")
    exp_data = survival_df[survival_df['Experiment'] == experiment]
    groups = exp_data['Group'].unique()
    
    # Compare treatment groups to control
    control_data = exp_data[exp_data['Group'] == 'Control']
    T_control = control_data['Day']
    E_control = control_data['Status'].map({'alive': 0, 'dead': 1})
    
    for group in groups:
        if group != 'Control':
            treatment_data = exp_data[exp_data['Group'] == group]
            T_treatment = treatment_data['Day']
            E_treatment = treatment_data['Status'].map({'alive': 0, 'dead': 1})
            
            results = logrank_test(T_treatment, T_control, E_treatment, E_control)
            p_value = results.p_value
            
            print(f"  {group} vs Control: p-value = {p_value:.4f}")
            if p_value < 0.05:
                print(f"    Significant difference detected (p < 0.05)")
            else:
                print(f"    No significant difference detected (p >= 0.05)")
```

The log-rank tests tell us which treatment groups have significantly different survival outcomes compared to the control group. This is another important measure of treatment efficacy.

## Challenge 5: Answering Research Questions (12:00-15:00)

### Question 1: Which treatment showed the most significant reduction in tumor volume? (12:00-13:00)
Let's calculate the percent change in tumor volume from baseline to final measurement for each treatment group:

```python
# Calculate percent change in tumor volume
tumor_changes = []

for experiment in tumor_volume_df['Experiment'].unique():
    exp_data = tumor_volume_df[tumor_volume_df['Experiment'] == experiment]
    
    for animal in exp_data['AnimalID'].unique():
        animal_data = exp_data[exp_data['AnimalID'] == animal]
        
        if len(animal_data) >= 2:  # Ensure we have at least baseline and one follow-up
            baseline = animal_data[animal_data['Day'] == animal_data['Day'].min()]['TumorVolume'].values[0]
            final = animal_data[animal_data['Day'] == animal_data['Day'].max()]['TumorVolume'].values[0]
            
            percent_change = ((final - baseline) / baseline) * 100
            
            tumor_changes.append({
                'Experiment': experiment,
                'AnimalID': animal,
                'Group': animal_data['Group'].values[0],
                'BaselineVolume': baseline,
                'FinalVolume': final,
                'PercentChange': percent_change
            })

tumor_changes_df = pd.DataFrame(tumor_changes)
display(tumor_changes_df.head(10))

# Calculate average percent change by experiment and group
avg_changes = tumor_changes_df.groupby(['Experiment', 'Group'])['PercentChange'].mean().reset_index()
display(avg_changes)

# Visualize average percent change
plt.figure(figsize=(12, 6))
sns.barplot(x='Experiment', y='PercentChange', hue='Group', data=avg_changes)
plt.title('Average Percent Change in Tumor Volume by Treatment Group')
plt.xlabel('Experiment')
plt.ylabel('Percent Change (%)')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
```

This visualization shows us the average percent change in tumor volume for each treatment group. Lower (more negative) values indicate greater tumor reduction, which is desirable.

### Question 2: Which treatment showed the best survival outcomes? (13:00-14:00)
Let's calculate the median survival time for each treatment group:

```python
# Calculate median survival time for each group
median_survival = []

for experiment in survival_df['Experiment'].unique():
    exp_data = survival_df[survival_df['Experiment'] == experiment]
    
    for group in exp_data['Group'].unique():
        group_data = exp_data[exp_data['Group'] == group]
        T = group_data['Day']
        E = group_data['Status'].map({'alive': 0, 'dead': 1})
        
        kmf = KaplanMeierFitter()
        kmf.fit(T, event_observed=E)
        
        try:
            median = kmf.median_survival_time_
        except:
            # If median survival is not reached (>50% survival at end of study)
            median = float('inf')
        
        median_survival.append({
            'Experiment': experiment,
            'Group': group,
            'MedianSurvival': median
        })

median_survival_df = pd.DataFrame(median_survival)
display(median_survival_df)
```

The median survival time tells us how long it takes for 50% of the animals in each group to reach the endpoint. Higher values (or infinity, meaning >50% survived until the end of the study) indicate better survival outcomes.

### Question 3: What is the most effective treatment overall? (14:00-15:00)
Let's create a composite score based on tumor volume reduction and survival improvement:

```python
# Create a composite score
composite_scores = []

for experiment in tumor_changes_df['Experiment'].unique():
    exp_tumor_data = avg_changes[avg_changes['Experiment'] == experiment]
    exp_survival_data = median_survival_df[median_survival_df['Experiment'] == experiment]
    
    # Get control values for normalization
    control_tumor_change = exp_tumor_data[exp_tumor_data['Group'] == 'Control']['PercentChange'].values[0]
    control_survival = exp_survival_data[exp_survival_data['Group'] == 'Control']['MedianSurvival'].values[0]
    
    for group in exp_tumor_data['Group'].unique():
        if group != 'Control':
            tumor_change = exp_tumor_data[exp_tumor_data['Group'] == group]['PercentChange'].values[0]
            survival = exp_survival_data[exp_survival_data['Group'] == group]['MedianSurvival'].values[0]
            
            # Calculate normalized scores (lower is better for tumor change, higher is better for survival)
            tumor_score = (control_tumor_change - tumor_change) / abs(control_tumor_change) if control_tumor_change != 0 else 0
            
            if survival == float('inf') and control_survival == float('inf'):
                survival_score = 0  # Both infinite, no difference
            elif survival == float('inf'):
                survival_score = 1  # Treatment is infinite, control is finite
            elif control_survival == float('inf'):
                survival_score = -1  # Control is infinite, treatment is finite
            else:
                survival_score = (survival - control_survival) / control_survival if control_survival != 0 else 0
            
            # Composite score (equal weight to tumor reduction and survival improvement)
            composite = (tumor_score + survival_score) / 2
            
            composite_scores.append({
                'Experiment': experiment,
                'Group': group,
                'TumorScore': tumor_score,
                'SurvivalScore': survival_score,
                'CompositeScore': composite
            })

composite_scores_df = pd.DataFrame(composite_scores)
display(composite_scores_df)

# Visualize composite scores
plt.figure(figsize=(12, 6))
sns.barplot(x='Experiment', y='CompositeScore', hue='Group', data=composite_scores_df)
plt.title('Composite Treatment Efficacy Score (Higher is Better)')
plt.xlabel('Experiment')
plt.ylabel('Composite Score')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
```

The composite score combines tumor volume reduction and survival improvement into a single metric. Higher values indicate more effective treatments overall. This helps us identify the most promising treatments from each experiment.

## Conclusion (15:00-15:30)
In this tutorial, we've guided you through analyzing a realistic preclinical cancer research dataset using the Science Data Kit. We've covered:

1. Loading and exploring the dataset
2. Analyzing experimental design and animal groups
3. Performing tumor growth analysis
4. Conducting survival analysis
5. Answering research questions using data analysis

These skills can be applied to your own research data to gain insights and make data-driven decisions. The Science Data Kit provides a powerful set of tools for scientific data analysis, making it easier to extract meaningful insights from complex datasets.

Thank you for following this tutorial. For more information, please refer to the documentation and other tutorials in the Science Data Kit.