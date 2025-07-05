"""
Science Data Kit - 30-Minute Preclinical Research Challenge Tutorial

This tutorial is designed as a guided 30-minute challenge for workshop attendees
to learn how to use the Science Data Kit with a realistic preclinical cancer research dataset.

The challenge is structured in progressive steps, each building on the previous one,
to help users understand how to:
1. Load and explore the preclinical research dataset
2. Perform basic data analysis and visualization
3. Answer research questions using the dataset

Prerequisites:
- Science Data Kit installed
- Neo4j database running
- Basic understanding of Python

To verify your progress, run the checkpoint_verification.py script after completing each step.
"""

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

# Set up plotting style
plt.style.use('seaborn-whitegrid')
sns.set_palette("colorblind")

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_step(step_number, description):
    """Print a formatted step."""
    print(f"\n--- Step {step_number}: {description} ---\n")

def print_checkpoint(checkpoint_number):
    """Print a checkpoint message."""
    print(f"\n>>> Checkpoint {checkpoint_number}: Run checkpoint_verification.py to verify your progress <<<\n")

def run_query(query, params=None):
    """Run a Cypher query and return the results as a pandas DataFrame."""
    connection = get_database_connection()
    results = connection.run_query(query, params)
    return pd.DataFrame([dict(record) for record in results])

def challenge_1_load_data():
    """Challenge 1: Load the preclinical research dataset."""
    print_section("CHALLENGE 1: LOADING THE DATASET")
    
    print_step(1, "Load the preclinical research dataset")
    print("""
    The first step is to load the preclinical research dataset into the Neo4j database.
    This dataset contains information about three cancer research experiments:
    - EXP001: Immunotherapy for breast cancer
    - EXP002: Combination therapy for pancreatic cancer
    - EXP003: Gene therapy for lung cancer
    
    The dataset includes experimental design, animal records, treatment protocols,
    imaging data, and outcomes.
    
    Run the following code to load the dataset:
    """)
    
    # Load the dataset
    print("Loading the preclinical research dataset...")
    load_dataset()
    
    print("\nDataset loaded successfully!")
    
    print_step(2, "Explore the dataset structure")
    print("""
    Now that the dataset is loaded, let's explore its structure.
    The dataset consists of five main node types:
    - Experiment: Information about the experimental design
    - Animal: Information about the experimental animals
    - Treatment: Information about the treatments administered
    - Imaging: Information about the imaging data collected
    - Outcome: Information about the experimental outcomes
    
    Let's run some queries to explore the dataset:
    """)
    
    # Query to get all experiments
    print("Querying all experiments...")
    query = """
    MATCH (e:Experiment {dataset: 'preclinical_research'})
    RETURN e.experiment_id as ID, e.title as Title, e.principal_investigator as PI
    """
    experiments_df = run_query(query)
    display(experiments_df)
    
    # Query to count nodes by type
    print("\nCounting nodes by type...")
    query = """
    MATCH (n)
    WHERE n.dataset = 'preclinical_research'
    RETURN labels(n)[0] as NodeType, count(n) as Count
    ORDER BY Count DESC
    """
    counts_df = run_query(query)
    display(counts_df)
    
    print_checkpoint(1)
    
    return experiments_df, counts_df

def challenge_2_analyze_experiments():
    """Challenge 2: Analyze the experiments and animal groups."""
    print_section("CHALLENGE 2: ANALYZING EXPERIMENTS AND ANIMAL GROUPS")
    
    print_step(3, "Analyze animal distribution across experiments")
    print("""
    Let's analyze how animals are distributed across experiments and treatment groups.
    This will help us understand the experimental design and balance.
    """)
    
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
    print("\nVisualizing animal distribution...")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Experiment', y='Count', hue='Group', data=animal_distribution_df)
    plt.title('Animal Distribution by Experiment and Group')
    plt.xlabel('Experiment')
    plt.ylabel('Number of Animals')
    plt.tight_layout()
    plt.show()
    
    print_step(4, "Analyze treatment protocols")
    print("""
    Now let's examine the treatment protocols for each experiment.
    This will help us understand what treatments were administered and how they differ.
    """)
    
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
    
    print_checkpoint(2)
    
    return animal_distribution_df, treatment_types_df

def challenge_3_tumor_growth_analysis():
    """Challenge 3: Analyze tumor growth over time."""
    print_section("CHALLENGE 3: TUMOR GROWTH ANALYSIS")
    
    print_step(5, "Analyze tumor growth over time")
    print("""
    One of the key metrics in preclinical cancer research is tumor volume.
    Let's analyze how tumor volume changes over time for different experiments and groups.
    """)
    
    # Query to get tumor volumes by experiment, group, and timepoint
    query = """
    MATCH (i:Imaging)-[:PERFORMED_ON]->(a:Animal)-[:PART_OF]->(e:Experiment)
    WHERE i.dataset = 'preclinical_research'
    RETURN e.experiment_id as Experiment, a.group as Group, i.timepoint as Timepoint,
           avg(i.tumor_volume_mm3) as AvgTumorVolume
    ORDER BY Experiment, Group, CASE i.timepoint
        WHEN 'Baseline' THEN 0
        WHEN '2 Weeks' THEN 1
        WHEN '4 Weeks' THEN 2
        WHEN '6 Weeks' THEN 3
        ELSE 4
    END
    """
    tumor_volume_df = run_query(query)
    display(tumor_volume_df)
    
    # Create a visualization of tumor growth
    print("\nVisualizing tumor growth over time...")
    plt.figure(figsize=(15, 10))
    
    # Create subplots for each experiment
    experiments = tumor_volume_df['Experiment'].unique()
    for i, exp in enumerate(experiments, 1):
        plt.subplot(2, 2, i)
        exp_data = tumor_volume_df[tumor_volume_df['Experiment'] == exp]
        
        # Create line plot
        sns.lineplot(x='Timepoint', y='AvgTumorVolume', hue='Group', 
                    data=exp_data, markers=True, dashes=False)
        
        plt.title(f'Tumor Growth - {exp}')
        plt.xlabel('Timepoint')
        plt.ylabel('Average Tumor Volume (mm³)')
        plt.xticks(rotation=45)
        plt.legend(title='Group')
        plt.tight_layout()
    
    plt.tight_layout()
    plt.show()
    
    print_step(6, "Calculate tumor growth inhibition")
    print("""
    Tumor Growth Inhibition (TGI) is a common metric used to evaluate treatment efficacy.
    It compares the tumor growth in the treatment group to the control group.
    
    TGI = (1 - (T_final - T_initial) / (C_final - C_initial)) * 100
    
    Where:
    - T_final: Final tumor volume in treatment group
    - T_initial: Initial tumor volume in treatment group
    - C_final: Final tumor volume in control group
    - C_initial: Initial tumor volume in control group
    
    Let's calculate TGI for each experiment:
    """)
    
    # Calculate TGI for each experiment
    tgi_results = []
    
    for exp in experiments:
        exp_data = tumor_volume_df[tumor_volume_df['Experiment'] == exp]
        
        # Get baseline and final timepoints for control and treatment groups
        control_baseline = exp_data[(exp_data['Group'] == 'Control') & 
                                   (exp_data['Timepoint'] == 'Baseline')]['AvgTumorVolume'].values[0]
        control_final = exp_data[(exp_data['Group'] == 'Control') & 
                                (exp_data['Timepoint'] == '6 Weeks')]['AvgTumorVolume'].values[0]
        
        treatment_baseline = exp_data[(exp_data['Group'] == 'Treatment') & 
                                     (exp_data['Timepoint'] == 'Baseline')]['AvgTumorVolume'].values[0]
        treatment_final = exp_data[(exp_data['Group'] == 'Treatment') & 
                                  (exp_data['Timepoint'] == '6 Weeks')]['AvgTumorVolume'].values[0]
        
        # Calculate TGI
        control_growth = control_final - control_baseline
        treatment_growth = treatment_final - treatment_baseline
        tgi = (1 - (treatment_growth / control_growth)) * 100
        
        tgi_results.append({
            'Experiment': exp,
            'Control_Growth': control_growth,
            'Treatment_Growth': treatment_growth,
            'TGI_Percent': tgi
        })
    
    tgi_df = pd.DataFrame(tgi_results)
    display(tgi_df)
    
    # Visualize TGI
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Experiment', y='TGI_Percent', data=tgi_df)
    plt.title('Tumor Growth Inhibition (TGI) by Experiment')
    plt.xlabel('Experiment')
    plt.ylabel('TGI (%)')
    plt.axhline(y=0, color='r', linestyle='-')
    plt.tight_layout()
    plt.show()
    
    print_checkpoint(3)
    
    return tumor_volume_df, tgi_df

def challenge_4_survival_analysis():
    """Challenge 4: Perform survival analysis."""
    print_section("CHALLENGE 4: SURVIVAL ANALYSIS")
    
    print_step(7, "Analyze survival outcomes")
    print("""
    Survival analysis is a critical component of preclinical cancer research.
    Let's analyze the survival outcomes for different experiments and groups.
    """)
    
    # Query to get survival data by experiment and group
    query = """
    MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
    WHERE o.dataset = 'preclinical_research'
    RETURN e.experiment_id as Experiment, a.group as Group, a.animal_id as AnimalID,
           o.survival_days as SurvivalDays, o.status as Status
    ORDER BY Experiment, Group, SurvivalDays
    """
    survival_df = run_query(query)
    display(survival_df)
    
    # Calculate median survival by experiment and group
    median_survival = survival_df.groupby(['Experiment', 'Group'])['SurvivalDays'].median().reset_index()
    median_survival.columns = ['Experiment', 'Group', 'MedianSurvival']
    
    print("\nMedian Survival by Experiment and Group:")
    display(median_survival)
    
    # Visualize median survival
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Experiment', y='MedianSurvival', hue='Group', data=median_survival)
    plt.title('Median Survival by Experiment and Group')
    plt.xlabel('Experiment')
    plt.ylabel('Median Survival (days)')
    plt.tight_layout()
    plt.show()
    
    print_step(8, "Analyze tumor response")
    print("""
    Tumor response is another important metric in cancer research.
    Let's analyze the distribution of tumor responses for different experiments and groups.
    """)
    
    # Query to get tumor response by experiment and group
    query = """
    MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
    WHERE o.dataset = 'preclinical_research'
    RETURN e.experiment_id as Experiment, a.group as Group, o.tumor_response as Response,
           count(o) as Count
    ORDER BY Experiment, Group, Response
    """
    response_df = run_query(query)
    display(response_df)
    
    # Visualize tumor response
    plt.figure(figsize=(15, 10))
    
    # Create subplots for each experiment
    experiments = response_df['Experiment'].unique()
    for i, exp in enumerate(experiments, 1):
        plt.subplot(2, 2, i)
        exp_data = response_df[response_df['Experiment'] == exp]
        
        # Create grouped bar plot
        sns.barplot(x='Response', y='Count', hue='Group', data=exp_data)
        
        plt.title(f'Tumor Response - {exp}')
        plt.xlabel('Response')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Group')
        plt.tight_layout()
    
    plt.tight_layout()
    plt.show()
    
    print_checkpoint(4)
    
    return survival_df, response_df

def challenge_5_research_questions():
    """Challenge 5: Answer research questions."""
    print_section("CHALLENGE 5: ANSWERING RESEARCH QUESTIONS")
    
    print_step(9, "Identify the most effective treatment")
    print("""
    Based on the analyses we've performed, let's identify the most effective treatment
    across the three experiments. We'll consider multiple metrics:
    - Tumor Growth Inhibition (TGI)
    - Median Survival
    - Tumor Response
    """)
    
    # Query to get comprehensive treatment efficacy data
    query = """
    MATCH (e:Experiment {dataset: 'preclinical_research'})
    OPTIONAL MATCH (a:Animal)-[:PART_OF]->(e)
    OPTIONAL MATCH (o:Outcome)-[:RESULT_FOR]->(a)
    OPTIONAL MATCH (i:Imaging)-[:PERFORMED_ON]->(a)
    WHERE i.timepoint = '6 Weeks'
    WITH e, a.group as Group, 
         avg(o.survival_days) as AvgSurvival,
         avg(i.tumor_volume_mm3) as FinalTumorVolume,
         count(DISTINCT a) as AnimalCount,
         count(DISTINCT CASE WHEN o.tumor_response = 'Complete Response' THEN a END) as CompleteResponses,
         count(DISTINCT CASE WHEN o.tumor_response = 'Partial Response' THEN a END) as PartialResponses,
         count(DISTINCT CASE WHEN o.tumor_response = 'Stable Disease' THEN a END) as StableDisease,
         count(DISTINCT CASE WHEN o.tumor_response = 'Progressive Disease' THEN a END) as ProgressiveDisease
    RETURN e.experiment_id as Experiment, e.title as ExperimentTitle, Group,
           AvgSurvival, FinalTumorVolume, AnimalCount,
           CompleteResponses, PartialResponses, StableDisease, ProgressiveDisease
    ORDER BY Experiment, Group
    """
    efficacy_df = run_query(query)
    display(efficacy_df)
    
    # Calculate response rates
    efficacy_df['ResponseRate'] = (efficacy_df['CompleteResponses'] + efficacy_df['PartialResponses']) / efficacy_df['AnimalCount'] * 100
    
    # Display treatment groups only
    treatment_efficacy = efficacy_df[efficacy_df['Group'] == 'Treatment']
    print("\nEfficacy Metrics for Treatment Groups:")
    display(treatment_efficacy[['Experiment', 'ExperimentTitle', 'AvgSurvival', 'FinalTumorVolume', 'ResponseRate']])
    
    # Visualize multiple efficacy metrics
    metrics = ['AvgSurvival', 'ResponseRate']
    fig, axes = plt.subplots(1, len(metrics), figsize=(15, 6))
    
    for i, metric in enumerate(metrics):
        sns.barplot(x='Experiment', y=metric, data=treatment_efficacy, ax=axes[i])
        axes[i].set_title(f'{metric} by Experiment')
        axes[i].set_xlabel('Experiment')
        axes[i].set_ylabel(metric)
        axes[i].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    # Determine the most effective treatment
    best_survival = treatment_efficacy.loc[treatment_efficacy['AvgSurvival'].idxmax()]
    best_response = treatment_efficacy.loc[treatment_efficacy['ResponseRate'].idxmax()]
    
    print(f"\nTreatment with highest average survival: {best_survival['Experiment']} - {best_survival['ExperimentTitle']}")
    print(f"Average survival: {best_survival['AvgSurvival']:.2f} days")
    
    print(f"\nTreatment with highest response rate: {best_response['Experiment']} - {best_response['ExperimentTitle']}")
    print(f"Response rate: {best_response['ResponseRate']:.2f}%")
    
    print_step(10, "Investigate treatment toxicity")
    print("""
    Treatment efficacy must be balanced with toxicity.
    Let's analyze the toxicity profiles of the different treatments.
    """)
    
    # Query to get toxicity data
    query = """
    MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
    WHERE o.dataset = 'preclinical_research' AND a.group = 'Treatment'
    RETURN e.experiment_id as Experiment, e.title as ExperimentTitle,
           avg(o.toxicity_grade) as AvgToxicityGrade,
           count(DISTINCT CASE WHEN o.toxicity_grade = 0 THEN a END) as Grade0,
           count(DISTINCT CASE WHEN o.toxicity_grade = 1 THEN a END) as Grade1,
           count(DISTINCT CASE WHEN o.toxicity_grade = 2 THEN a END) as Grade2,
           count(DISTINCT a) as TotalAnimals
    ORDER BY Experiment
    """
    toxicity_df = run_query(query)
    
    # Calculate percentages
    for grade in range(3):
        toxicity_df[f'Grade{grade}Percent'] = toxicity_df[f'Grade{grade}'] / toxicity_df['TotalAnimals'] * 100
    
    display(toxicity_df)
    
    # Visualize toxicity grades
    plt.figure(figsize=(12, 6))
    
    # Prepare data for stacked bar chart
    toxicity_data = []
    for _, row in toxicity_df.iterrows():
        for grade in range(3):
            toxicity_data.append({
                'Experiment': row['Experiment'],
                'ExperimentTitle': row['ExperimentTitle'],
                'ToxicityGrade': f'Grade {grade}',
                'Percentage': row[f'Grade{grade}Percent']
            })
    
    toxicity_plot_df = pd.DataFrame(toxicity_data)
    
    # Create stacked bar chart
    toxicity_pivot = toxicity_plot_df.pivot(index='Experiment', columns='ToxicityGrade', values='Percentage')
    toxicity_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title('Toxicity Grade Distribution by Experiment')
    plt.xlabel('Experiment')
    plt.ylabel('Percentage of Animals')
    plt.xticks(rotation=45)
    plt.legend(title='Toxicity Grade')
    plt.tight_layout()
    plt.show()
    
    # Calculate therapeutic index (efficacy/toxicity ratio)
    therapeutic_index = pd.merge(
        treatment_efficacy[['Experiment', 'ResponseRate']], 
        toxicity_df[['Experiment', 'AvgToxicityGrade']], 
        on='Experiment'
    )
    
    # Avoid division by zero
    therapeutic_index['AvgToxicityGrade'] = therapeutic_index['AvgToxicityGrade'].apply(lambda x: max(0.1, x))
    therapeutic_index['TherapeuticIndex'] = therapeutic_index['ResponseRate'] / therapeutic_index['AvgToxicityGrade']
    
    print("\nTherapeutic Index (Efficacy/Toxicity Ratio):")
    display(therapeutic_index)
    
    # Visualize therapeutic index
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Experiment', y='TherapeuticIndex', data=therapeutic_index)
    plt.title('Therapeutic Index by Experiment')
    plt.xlabel('Experiment')
    plt.ylabel('Therapeutic Index (Response Rate / Avg Toxicity)')
    plt.tight_layout()
    plt.show()
    
    print_checkpoint(5)
    
    return efficacy_df, toxicity_df, therapeutic_index

def main():
    """Main function to run the tutorial."""
    print_section("SCIENCE DATA KIT - 30-MINUTE PRECLINICAL RESEARCH CHALLENGE")
    
    print("""
    Welcome to the Science Data Kit 30-Minute Preclinical Research Challenge!
    
    In this tutorial, you will learn how to use the Science Data Kit to analyze
    a realistic preclinical cancer research dataset. The challenge is structured
    in progressive steps, each building on the previous one.
    
    By the end of this tutorial, you will be able to:
    1. Load and explore a preclinical research dataset
    2. Analyze experimental design and animal groups
    3. Perform tumor growth analysis
    4. Conduct survival analysis
    5. Answer research questions using the dataset
    
    Let's get started!
    """)
    
    # Run the challenges
    experiments_df, counts_df = challenge_1_load_data()
    animal_distribution_df, treatment_types_df = challenge_2_analyze_experiments()
    tumor_volume_df, tgi_df = challenge_3_tumor_growth_analysis()
    survival_df, response_df = challenge_4_survival_analysis()
    efficacy_df, toxicity_df, therapeutic_index = challenge_5_research_questions()
    
    print_section("CHALLENGE COMPLETED!")
    
    print("""
    Congratulations! You have completed the 30-Minute Preclinical Research Challenge.
    
    You have successfully:
    1. Loaded and explored the preclinical research dataset
    2. Analyzed experimental design and animal groups
    3. Performed tumor growth analysis and calculated TGI
    4. Conducted survival analysis and examined tumor responses
    5. Identified the most effective treatment and analyzed toxicity profiles
    
    Next steps:
    - Try modifying the queries to explore different aspects of the data
    - Create your own visualizations to highlight key findings
    - Apply these techniques to your own research data
    
    For more information and resources, check out the Science Data Kit documentation.
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())