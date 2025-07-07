"""
Clinical Trial Dataset Demo Script

This script demonstrates how to use the Science Data Kit with the clinical trial dataset.
It shows how to load the dataset, perform analysis, and create visualizations.

Usage:
    python -m science_data_kit.data.samples.demo_clinical_trial
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union, Any
import os
import sys

# Add the parent directory to the path to allow importing the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the Science Data Kit
from science_data_kit.data.samples.load_clinical_trial_dataset import load_dataset
from science_data_kit.visualization import plotting
from science_data_kit.analysis import statistics

def load_data() -> Dict[str, pd.DataFrame]:
    """
    Load the clinical trial dataset.
    
    Returns:
        Dictionary of DataFrames containing the dataset
    """
    print("Loading clinical trial dataset...")
    dataset = load_dataset()
    return dataset

def explore_data(dataset: Dict[str, pd.DataFrame]) -> None:
    """
    Explore the clinical trial dataset.
    
    Args:
        dataset: Dictionary of DataFrames containing the dataset
    """
    print("\n=== Dataset Exploration ===")
    
    # Print basic information about each component
    for name, df in dataset.items():
        print(f"\n{name.capitalize()} DataFrame:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {', '.join(df.columns)}")
        print(f"  Sample data:")
        print(df.head(3))
    
    # Print some summary statistics
    patients_df = dataset["patients"]
    print("\nPatient Demographics:")
    print(f"  Total patients: {len(patients_df)}")
    print(f"  Age range: {patients_df['age'].min()} - {patients_df['age'].max()} years")
    print(f"  Sex distribution: {patients_df['sex'].value_counts().to_dict()}")
    print(f"  Treatment arms: {patients_df['treatment_arm'].value_counts().to_dict()}")
    
    # Print visit completion rates
    visits_df = dataset["visits"]
    visit_completion = visits_df.groupby("visit_type")["status"].value_counts().unstack().fillna(0)
    completion_rate = (visit_completion["Completed"] / visit_completion.sum(axis=1) * 100).round(1)
    
    print("\nVisit Completion Rates:")
    for visit_type, rate in completion_rate.items():
        print(f"  {visit_type}: {rate}%")

def analyze_efficacy(dataset: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Analyze the efficacy of the treatment.
    
    Args:
        dataset: Dictionary of DataFrames containing the dataset
        
    Returns:
        DataFrame containing efficacy analysis results
    """
    print("\n=== Efficacy Analysis ===")
    
    # Get HbA1c data
    labs_df = dataset["labs"]
    hba1c_data = labs_df[labs_df["test_name"] == "HbA1c"].copy()
    
    # Merge with visits and patients data to get visit type and treatment arm
    visits_df = dataset["visits"]
    patients_df = dataset["patients"]
    
    hba1c_data = hba1c_data.merge(
        visits_df[["visit_id", "visit_type", "patient_id"]],
        on=["visit_id", "patient_id"]
    )
    
    hba1c_data = hba1c_data.merge(
        patients_df[["patient_id", "treatment_arm"]],
        on="patient_id"
    )
    
    # Filter for baseline (V2) and end of treatment (V8) visits
    baseline_data = hba1c_data[hba1c_data["visit_type"] == "V2"]
    endpoint_data = hba1c_data[hba1c_data["visit_type"] == "V8"]
    
    # Calculate change from baseline
    baseline_values = baseline_data.set_index("patient_id")["value"]
    endpoint_values = endpoint_data.set_index("patient_id")["value"]
    
    # Get patients with both baseline and endpoint values
    common_patients = set(baseline_values.index) & set(endpoint_values.index)
    
    # Calculate change for these patients
    changes = pd.DataFrame({
        "patient_id": list(common_patients),
        "baseline": baseline_values.loc[common_patients].values,
        "endpoint": endpoint_values.loc[common_patients].values
    })
    
    changes["change"] = changes["endpoint"] - changes["baseline"]
    
    # Merge with treatment arm information
    changes = changes.merge(
        patients_df[["patient_id", "treatment_arm"]],
        on="patient_id"
    )
    
    # Calculate summary statistics by treatment arm
    efficacy_summary = changes.groupby("treatment_arm").agg({
        "baseline": ["count", "mean", "std"],
        "endpoint": ["mean", "std"],
        "change": ["mean", "std"]
    })
    
    # Flatten the column names
    efficacy_summary.columns = [f"{col[0]}_{col[1]}" for col in efficacy_summary.columns]
    
    # Reset index for easier display
    efficacy_summary = efficacy_summary.reset_index()
    
    # Calculate responder rate (HbA1c < 7.0%)
    responders = changes[changes["endpoint"] < 7.0].groupby("treatment_arm").size()
    total = changes.groupby("treatment_arm").size()
    responder_rate = (responders / total * 100).round(1)
    
    efficacy_summary["responder_rate"] = efficacy_summary["treatment_arm"].map(responder_rate)
    
    # Print summary
    print("\nHbA1c Change from Baseline to Week 24:")
    print(efficacy_summary[["treatment_arm", "baseline_count", "baseline_mean", "endpoint_mean", "change_mean", "responder_rate"]])
    
    # Perform t-test between treatment arms
    active_changes = changes[changes["treatment_arm"] == "Active"]["change"]
    placebo_changes = changes[changes["treatment_arm"] == "Placebo"]["change"]
    
    t_stat, p_value = statistics.t_test(active_changes, placebo_changes)
    
    print(f"\nT-test for difference between treatment arms:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  Statistically significant: {p_value < 0.05}")
    
    return changes

def analyze_safety(dataset: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Analyze the safety of the treatment.
    
    Args:
        dataset: Dictionary of DataFrames containing the dataset
        
    Returns:
        DataFrame containing safety analysis results
    """
    print("\n=== Safety Analysis ===")
    
    # Get adverse events data
    ae_df = dataset["adverse_events"]
    patients_df = dataset["patients"]
    
    # Merge with patient data to get treatment arm
    ae_with_treatment = ae_df.merge(
        patients_df[["patient_id", "treatment_arm"]],
        on="patient_id"
    )
    
    # Calculate adverse event rates by treatment arm
    total_patients = patients_df["treatment_arm"].value_counts()
    patients_with_ae = ae_with_treatment.groupby("treatment_arm")["patient_id"].nunique()
    ae_rate = (patients_with_ae / total_patients * 100).round(1)
    
    print("\nAdverse Event Rates:")
    for arm, rate in ae_rate.items():
        print(f"  {arm}: {rate}% of patients experienced at least one adverse event")
    
    # Calculate adverse event counts by type and treatment arm
    ae_counts = ae_with_treatment.groupby(["treatment_arm", "event_name"]).size().unstack(fill_value=0)
    
    # Calculate percentages
    ae_percentages = ae_counts.div(total_patients, axis=0) * 100
    
    # Sort by difference between active and placebo
    if "Active" in ae_percentages.index and "Placebo" in ae_percentages.index:
        ae_diff = ae_percentages.loc["Active"] - ae_percentages.loc["Placebo"]
        ae_percentages = ae_percentages[ae_diff.sort_values(ascending=False).index]
    
    print("\nAdverse Events by Type (% of patients):")
    print(ae_percentages.round(1))
    
    # Calculate adverse event counts by severity and treatment arm
    severity_counts = ae_with_treatment.groupby(["treatment_arm", "severity"]).size().unstack(fill_value=0)
    
    # Calculate percentages
    severity_percentages = severity_counts.div(severity_counts.sum(axis=1), axis=0) * 100
    
    print("\nAdverse Events by Severity (% of events):")
    print(severity_percentages.round(1))
    
    return ae_with_treatment

def visualize_efficacy(changes_df: pd.DataFrame, output_dir: str = "figures") -> None:
    """
    Create visualizations for efficacy analysis.
    
    Args:
        changes_df: DataFrame containing efficacy analysis results
        output_dir: Directory to save figures
    """
    print("\n=== Efficacy Visualizations ===")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set the style
    sns.set(style="whitegrid")
    
    # Figure 1: HbA1c Change from Baseline
    plt.figure(figsize=(10, 6))
    
    # Box plot
    sns.boxplot(x="treatment_arm", y="change", data=changes_df)
    
    # Add individual points
    sns.stripplot(x="treatment_arm", y="change", data=changes_df, 
                 size=4, color=".3", alpha=0.6)
    
    # Customize the plot
    plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
    plt.title("HbA1c Change from Baseline to Week 24", fontsize=14)
    plt.xlabel("Treatment Arm", fontsize=12)
    plt.ylabel("Change in HbA1c (%)", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "hba1c_change.png"), dpi=300)
    print(f"Saved figure to {os.path.join(output_dir, 'hba1c_change.png')}")
    
    # Figure 2: HbA1c Over Time
    # This requires additional data processing to get all timepoints
    
    # Figure 3: Responder Analysis
    plt.figure(figsize=(8, 6))
    
    # Calculate responder counts
    responder_data = changes_df.copy()
    responder_data["responder"] = responder_data["endpoint"] < 7.0
    responder_counts = responder_data.groupby(["treatment_arm", "responder"]).size().unstack()
    
    # Calculate percentages
    responder_pct = responder_counts[True] / responder_counts.sum(axis=1) * 100
    non_responder_pct = 100 - responder_pct
    
    # Create stacked bar chart
    bar_width = 0.6
    bars = plt.bar(responder_pct.index, responder_pct, bar_width, label="HbA1c < 7.0%")
    plt.bar(non_responder_pct.index, non_responder_pct, bar_width, bottom=responder_pct, label="HbA1c ≥ 7.0%")
    
    # Add percentage labels
    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, 
                f"{responder_pct.iloc[i]:.1f}%", 
                ha='center', va='center', color='white', fontweight='bold')
    
    # Customize the plot
    plt.title("Percentage of Patients Achieving HbA1c < 7.0% at Week 24", fontsize=14)
    plt.xlabel("Treatment Arm", fontsize=12)
    plt.ylabel("Percentage of Patients", fontsize=12)
    plt.ylim(0, 100)
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "responder_analysis.png"), dpi=300)
    print(f"Saved figure to {os.path.join(output_dir, 'responder_analysis.png')}")

def visualize_safety(ae_df: pd.DataFrame, output_dir: str = "figures") -> None:
    """
    Create visualizations for safety analysis.
    
    Args:
        ae_df: DataFrame containing adverse event data with treatment arm
        output_dir: Directory to save figures
    """
    print("\n=== Safety Visualizations ===")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set the style
    sns.set(style="whitegrid")
    
    # Figure 1: Adverse Event Rates by Type
    plt.figure(figsize=(12, 8))
    
    # Calculate event counts by type and treatment arm
    event_counts = ae_df.groupby(["treatment_arm", "event_name"]).size().unstack(fill_value=0)
    
    # Calculate percentages based on number of patients in each arm
    patient_counts = ae_df.groupby("treatment_arm")["patient_id"].nunique()
    event_pct = event_counts.div(patient_counts, axis=0) * 100
    
    # Sort by frequency in the active arm
    if "Active" in event_pct.index:
        event_pct = event_pct[event_pct.loc["Active"].sort_values(ascending=False).index]
    
    # Plot
    event_pct.plot(kind="bar", figsize=(12, 8))
    
    # Customize the plot
    plt.title("Adverse Event Rates by Type", fontsize=14)
    plt.xlabel("Treatment Arm", fontsize=12)
    plt.ylabel("Percentage of Patients", fontsize=12)
    plt.legend(title="Adverse Event", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ae_rates_by_type.png"), dpi=300)
    print(f"Saved figure to {os.path.join(output_dir, 'ae_rates_by_type.png')}")
    
    # Figure 2: Adverse Event Severity
    plt.figure(figsize=(10, 6))
    
    # Calculate event counts by severity and treatment arm
    severity_counts = ae_df.groupby(["treatment_arm", "severity"]).size().unstack(fill_value=0)
    
    # Ensure all severity levels are present
    for severity in ["Mild", "Moderate", "Severe"]:
        if severity not in severity_counts.columns:
            severity_counts[severity] = 0
    
    # Sort columns by severity
    severity_counts = severity_counts[["Mild", "Moderate", "Severe"]]
    
    # Calculate percentages
    severity_pct = severity_counts.div(severity_counts.sum(axis=1), axis=0) * 100
    
    # Create stacked bar chart
    severity_pct.plot(kind="bar", stacked=True, figsize=(10, 6), 
                     color=["#66c2a5", "#fc8d62", "#8da0cb"])
    
    # Customize the plot
    plt.title("Adverse Event Severity Distribution", fontsize=14)
    plt.xlabel("Treatment Arm", fontsize=12)
    plt.ylabel("Percentage of Events", fontsize=12)
    plt.legend(title="Severity")
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ae_severity.png"), dpi=300)
    print(f"Saved figure to {os.path.join(output_dir, 'ae_severity.png')}")

def main() -> None:
    """
    Main function to demonstrate the clinical trial dataset.
    """
    # Load the dataset
    dataset = load_data()
    
    # Explore the dataset
    explore_data(dataset)
    
    # Analyze efficacy
    changes_df = analyze_efficacy(dataset)
    
    # Analyze safety
    ae_df = analyze_safety(dataset)
    
    # Create visualizations
    visualize_efficacy(changes_df)
    visualize_safety(ae_df)
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()