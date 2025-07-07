"""
Clinical Trial Dataset Loader

This module provides functions for generating and loading a simulated clinical trial dataset
for the Science Data Kit. The dataset represents a Phase 3 clinical trial for a Type 2 Diabetes treatment.

The dataset consists of six CSV files:
1. patients.csv - Patient demographic information
2. sites.csv - Clinical trial site information
3. visits.csv - Patient visit information
4. labs.csv - Laboratory measurements
5. treatments.csv - Treatment administration records
6. adverse_events.csv - Adverse event records

Usage:
    from science_data_kit.data.samples.load_clinical_trial_dataset import main
    main()
"""

import os
import pandas as pd
import numpy as np
import datetime
import random
from typing import Dict, List, Tuple, Optional, Union, Any

# Define constants
DATASET_DIR = os.path.join(os.path.dirname(__file__), "datasets", "clinical_trial")
NUM_PATIENTS = 300
NUM_SITES = 15
TREATMENT_RATIO = 2  # 2:1 active:placebo ratio
VISIT_SCHEDULE = {
    "V1": -28,  # Screening (Day -28)
    "V2": 0,    # Baseline (Day 0)
    "V3": 28,   # Week 4
    "V4": 56,   # Week 8
    "V5": 84,   # Week 12
    "V6": 112,  # Week 16
    "V7": 140,  # Week 20
    "V8": 168,  # Week 24 (End of Treatment)
    "V9": 196   # Week 28 (Follow-up)
}
LAB_TESTS = [
    {"name": "HbA1c", "unit": "%", "ref_range": "4.0-5.6", "baseline_mean": 8.2, "baseline_sd": 0.8},
    {"name": "Fasting Plasma Glucose", "unit": "mg/dL", "ref_range": "70-99", "baseline_mean": 160, "baseline_sd": 30},
    {"name": "Total Cholesterol", "unit": "mg/dL", "ref_range": "125-200", "baseline_mean": 190, "baseline_sd": 35},
    {"name": "LDL", "unit": "mg/dL", "ref_range": "0-100", "baseline_mean": 110, "baseline_sd": 30},
    {"name": "HDL", "unit": "mg/dL", "ref_range": "40-60", "baseline_mean": 45, "baseline_sd": 10},
    {"name": "Triglycerides", "unit": "mg/dL", "ref_range": "0-150", "baseline_mean": 180, "baseline_sd": 70},
    {"name": "Serum Creatinine", "unit": "mg/dL", "ref_range": "0.6-1.2", "baseline_mean": 0.9, "baseline_sd": 0.2},
    {"name": "eGFR", "unit": "mL/min/1.73m²", "ref_range": ">60", "baseline_mean": 80, "baseline_sd": 15},
    {"name": "ALT", "unit": "U/L", "ref_range": "7-56", "baseline_mean": 30, "baseline_sd": 15},
    {"name": "AST", "unit": "U/L", "ref_range": "10-40", "baseline_mean": 25, "baseline_sd": 10},
    {"name": "Alkaline Phosphatase", "unit": "U/L", "ref_range": "44-147", "baseline_mean": 80, "baseline_sd": 20},
    {"name": "Total Bilirubin", "unit": "mg/dL", "ref_range": "0.1-1.2", "baseline_mean": 0.6, "baseline_sd": 0.3},
    {"name": "Weight", "unit": "kg", "ref_range": "", "baseline_mean": 90, "baseline_sd": 15},
    {"name": "Systolic BP", "unit": "mmHg", "ref_range": "90-120", "baseline_mean": 130, "baseline_sd": 15},
    {"name": "Diastolic BP", "unit": "mmHg", "ref_range": "60-80", "baseline_mean": 85, "baseline_sd": 10}
]
ADVERSE_EVENTS = [
    {"name": "Nausea", "probability_active": 0.15, "probability_placebo": 0.05, "severity_dist": [0.6, 0.3, 0.1]},
    {"name": "Vomiting", "probability_active": 0.08, "probability_placebo": 0.02, "severity_dist": [0.5, 0.4, 0.1]},
    {"name": "Diarrhea", "probability_active": 0.12, "probability_placebo": 0.04, "severity_dist": [0.7, 0.2, 0.1]},
    {"name": "Headache", "probability_active": 0.10, "probability_placebo": 0.08, "severity_dist": [0.8, 0.15, 0.05]},
    {"name": "Dizziness", "probability_active": 0.07, "probability_placebo": 0.03, "severity_dist": [0.7, 0.25, 0.05]},
    {"name": "Fatigue", "probability_active": 0.09, "probability_placebo": 0.06, "severity_dist": [0.6, 0.35, 0.05]},
    {"name": "Hypoglycemia", "probability_active": 0.05, "probability_placebo": 0.01, "severity_dist": [0.5, 0.4, 0.1]},
    {"name": "Injection Site Reaction", "probability_active": 0.20, "probability_placebo": 0.05, "severity_dist": [0.8, 0.15, 0.05]},
    {"name": "Upper Respiratory Infection", "probability_active": 0.06, "probability_placebo": 0.06, "severity_dist": [0.7, 0.25, 0.05]},
    {"name": "Urinary Tract Infection", "probability_active": 0.04, "probability_placebo": 0.04, "severity_dist": [0.6, 0.3, 0.1]}
]

def generate_sites() -> pd.DataFrame:
    """
    Generate simulated clinical trial sites.
    
    Returns:
        DataFrame containing site information
    """
    sites = []
    
    # List of major US cities for site locations
    cities = [
        "Boston, MA", "New York, NY", "Philadelphia, PA", "Baltimore, MD", "Chicago, IL",
        "Rochester, MN", "Houston, TX", "Los Angeles, CA", "San Francisco, CA", "Seattle, WA",
        "Miami, FL", "Atlanta, GA", "Denver, CO", "Phoenix, AZ", "Nashville, TN"
    ]
    
    # List of fictional principal investigators
    investigators = [
        "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez", "Dr. David Kim",
        "Dr. Lisa Patel", "Dr. Robert Williams", "Dr. Jennifer Lee", "Dr. Thomas Brown",
        "Dr. Maria Garcia", "Dr. James Wilson", "Dr. Susan Miller", "Dr. John Davis",
        "Dr. Karen Taylor", "Dr. Richard Martinez", "Dr. Elizabeth Anderson"
    ]
    
    # Generate site data
    for i in range(NUM_SITES):
        site_id = f"S{i+1:03d}"
        location = cities[i % len(cities)]
        investigator = investigators[i % len(investigators)]
        enrollment_target = random.randint(15, 25)
        
        sites.append({
            "site_id": site_id,
            "location": location,
            "principal_investigator": investigator,
            "enrollment_target": enrollment_target
        })
    
    return pd.DataFrame(sites)

def generate_patients(sites_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate simulated patient data.
    
    Args:
        sites_df: DataFrame containing site information
        
    Returns:
        DataFrame containing patient information
    """
    patients = []
    
    # Assign patients to sites
    site_ids = sites_df["site_id"].tolist()
    
    # Generate patient data
    for i in range(NUM_PATIENTS):
        patient_id = f"P{i+1:03d}"
        site_id = random.choice(site_ids)
        
        # Demographics
        age = random.randint(35, 75)
        sex = random.choice(["Male", "Female"])
        
        # Randomize race with realistic distribution
        race_dist = {
            "White": 0.65,
            "Black or African American": 0.15,
            "Asian": 0.10,
            "American Indian or Alaska Native": 0.02,
            "Native Hawaiian or Other Pacific Islander": 0.01,
            "Other": 0.07
        }
        race = random.choices(list(race_dist.keys()), weights=list(race_dist.values()))[0]
        
        # Randomize ethnicity
        ethnicity = random.choice(["Hispanic or Latino", "Not Hispanic or Latino"])
        
        # Physical characteristics
        if sex == "Male":
            height = round(random.normalvariate(175, 8), 1)  # cm
            weight = round(random.normalvariate(90, 15), 1)  # kg
        else:
            height = round(random.normalvariate(162, 7), 1)  # cm
            weight = round(random.normalvariate(80, 15), 1)  # kg
        
        bmi = round(weight / ((height / 100) ** 2), 1)
        
        # Treatment arm (2:1 ratio)
        treatment_arm = random.choices(["Active", "Placebo"], weights=[TREATMENT_RATIO, 1])[0]
        
        # Enrollment date (staggered over 3 months)
        start_date = datetime.date(2023, 1, 1)
        days_offset = random.randint(0, 90)
        enrollment_date = (start_date + datetime.timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        patients.append({
            "patient_id": patient_id,
            "site_id": site_id,
            "age": age,
            "sex": sex,
            "race": race,
            "ethnicity": ethnicity,
            "height_cm": height,
            "weight_kg": weight,
            "bmi": bmi,
            "treatment_arm": treatment_arm,
            "enrollment_date": enrollment_date
        })
    
    return pd.DataFrame(patients)

def generate_visits(patients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate simulated visit data.
    
    Args:
        patients_df: DataFrame containing patient information
        
    Returns:
        DataFrame containing visit information
    """
    visits = []
    
    # Generate visit data for each patient
    for _, patient in patients_df.iterrows():
        patient_id = patient["patient_id"]
        enrollment_date = datetime.datetime.strptime(patient["enrollment_date"], "%Y-%m-%d").date()
        
        # Generate visits according to schedule
        for visit_id, days_offset in VISIT_SCHEDULE.items():
            scheduled_date = enrollment_date + datetime.timedelta(days=days_offset)
            
            # Add some variability to actual visit dates (±3 days)
            actual_date = scheduled_date + datetime.timedelta(days=random.randint(-3, 3))
            
            # Determine visit status
            # Early visits are all completed
            # Later visits have increasing probability of being missed
            if visit_id in ["V1", "V2", "V3", "V4"]:
                status = "Completed"
            else:
                # Increasing probability of missed visits in later timepoints
                missed_prob = 0.05 * (int(visit_id[1]) - 4)  # V5: 5%, V6: 10%, etc.
                status = random.choices(["Completed", "Missed"], weights=[1 - missed_prob, missed_prob])[0]
            
            visits.append({
                "visit_id": f"{patient_id}_{visit_id}",
                "patient_id": patient_id,
                "visit_type": visit_id,
                "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                "actual_date": actual_date.strftime("%Y-%m-%d") if status == "Completed" else None,
                "status": status
            })
    
    return pd.DataFrame(visits)

def generate_labs(visits_df: pd.DataFrame, patients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate simulated laboratory data.
    
    Args:
        visits_df: DataFrame containing visit information
        patients_df: DataFrame containing patient information
        
    Returns:
        DataFrame containing laboratory measurements
    """
    labs = []
    lab_id_counter = 1
    
    # Get treatment arm for each patient
    patient_treatment = dict(zip(patients_df["patient_id"], patients_df["treatment_arm"]))
    
    # Generate lab data for each completed visit
    completed_visits = visits_df[visits_df["status"] == "Completed"]
    
    for _, visit in completed_visits.iterrows():
        patient_id = visit["patient_id"]
        visit_id = visit["visit_id"]
        visit_type = visit["visit_type"]
        treatment_arm = patient_treatment[patient_id]
        
        # Generate lab values for each test
        for test in LAB_TESTS:
            test_name = test["name"]
            unit = test["unit"]
            ref_range = test["ref_range"]
            
            # Baseline values
            if visit_type == "V2":  # Baseline visit
                value = round(random.normalvariate(test["baseline_mean"], test["baseline_sd"]), 1)
                
                # Store baseline value for this patient and test
                if not hasattr(generate_labs, "baseline_values"):
                    generate_labs.baseline_values = {}
                
                if patient_id not in generate_labs.baseline_values:
                    generate_labs.baseline_values[patient_id] = {}
                
                generate_labs.baseline_values[patient_id][test_name] = value
            
            # Follow-up values
            else:
                # Get baseline value for this patient and test
                if hasattr(generate_labs, "baseline_values") and patient_id in generate_labs.baseline_values and test_name in generate_labs.baseline_values[patient_id]:
                    baseline = generate_labs.baseline_values[patient_id][test_name]
                else:
                    # If no baseline available, use population mean
                    baseline = test["baseline_mean"]
                
                # Calculate expected change based on visit and treatment
                visit_num = int(visit_type[1])
                weeks = (visit_num - 2) * 4  # Weeks since baseline
                
                # Different effects for different tests
                if test_name == "HbA1c":
                    # Active treatment reduces HbA1c more than placebo
                    if treatment_arm == "Active":
                        expected_change = -0.1 * weeks / 4  # About -0.1% per month
                    else:
                        expected_change = -0.02 * weeks / 4  # About -0.02% per month
                
                elif test_name == "Fasting Plasma Glucose":
                    # Active treatment reduces FPG more than placebo
                    if treatment_arm == "Active":
                        expected_change = -2 * weeks / 4  # About -2 mg/dL per month
                    else:
                        expected_change = -0.5 * weeks / 4  # About -0.5 mg/dL per month
                
                elif test_name == "Weight":
                    # Active treatment reduces weight more than placebo
                    if treatment_arm == "Active":
                        expected_change = -0.5 * weeks / 4  # About -0.5 kg per month
                    else:
                        expected_change = 0  # No change with placebo
                
                else:
                    # Other tests have minimal changes
                    expected_change = 0
                
                # Add random variation
                variation = random.normalvariate(0, test["baseline_sd"] * 0.1)
                
                # Calculate final value
                value = round(baseline + expected_change + variation, 1)
            
            # Determine if value is outside reference range
            flag = ""
            if ref_range:
                if "-" in ref_range:
                    low, high = map(float, ref_range.split("-"))
                    if value < low:
                        flag = "L"
                    elif value > high:
                        flag = "H"
                elif ">" in ref_range:
                    threshold = float(ref_range.replace(">", ""))
                    if value <= threshold:
                        flag = "L"
                elif "<" in ref_range:
                    threshold = float(ref_range.replace("<", ""))
                    if value >= threshold:
                        flag = "H"
            
            labs.append({
                "lab_id": f"L{lab_id_counter:06d}",
                "patient_id": patient_id,
                "visit_id": visit_id,
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "reference_range": ref_range,
                "flag": flag
            })
            
            lab_id_counter += 1
    
    return pd.DataFrame(labs)

def generate_treatments(visits_df: pd.DataFrame, patients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate simulated treatment administration data.
    
    Args:
        visits_df: DataFrame containing visit information
        patients_df: DataFrame containing patient information
        
    Returns:
        DataFrame containing treatment administration records
    """
    treatments = []
    treatment_id_counter = 1
    
    # Get treatment arm for each patient
    patient_treatment = dict(zip(patients_df["patient_id"], patients_df["treatment_arm"]))
    
    # Generate treatment data for each completed visit (except screening)
    completed_visits = visits_df[(visits_df["status"] == "Completed") & (visits_df["visit_type"] != "V1")]
    
    for _, visit in completed_visits.iterrows():
        patient_id = visit["patient_id"]
        visit_id = visit["visit_id"]
        visit_type = visit["visit_type"]
        actual_date = visit["actual_date"]
        treatment_arm = patient_treatment[patient_id]
        
        # Determine dose based on treatment arm
        if treatment_arm == "Active":
            dose = "10 mg"
        else:
            dose = "Placebo"
        
        # Calculate compliance (higher in earlier visits, decreases over time)
        visit_num = int(visit_type[1])
        base_compliance = 0.95  # Start with 95% compliance
        decay_rate = 0.01  # Decrease by 1% per visit
        mean_compliance = base_compliance - (decay_rate * (visit_num - 2))
        
        # Add random variation to compliance
        compliance = round(min(1.0, max(0.0, random.normalvariate(mean_compliance, 0.05))), 2)
        
        treatments.append({
            "treatment_id": f"T{treatment_id_counter:06d}",
            "patient_id": patient_id,
            "visit_id": visit_id,
            "treatment_arm": treatment_arm,
            "dose": dose,
            "administration_date": actual_date,
            "compliance": compliance
        })
        
        treatment_id_counter += 1
    
    return pd.DataFrame(treatments)

def generate_adverse_events(patients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate simulated adverse event data.
    
    Args:
        patients_df: DataFrame containing patient information
        
    Returns:
        DataFrame containing adverse event records
    """
    adverse_events = []
    ae_id_counter = 1
    
    # Get treatment arm and enrollment date for each patient
    patient_info = dict(zip(patients_df["patient_id"], zip(patients_df["treatment_arm"], patients_df["enrollment_date"])))
    
    # Generate adverse events for each patient
    for patient_id, (treatment_arm, enrollment_date) in patient_info.items():
        # Convert enrollment date to datetime
        start_date = datetime.datetime.strptime(enrollment_date, "%Y-%m-%d").date()
        
        # Determine number of adverse events for this patient
        if treatment_arm == "Active":
            num_events = random.choices([0, 1, 2, 3, 4], weights=[0.3, 0.3, 0.2, 0.15, 0.05])[0]
        else:
            num_events = random.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
        
        # Generate each adverse event
        for _ in range(num_events):
            # Select an adverse event type
            if treatment_arm == "Active":
                ae_probs = [ae["probability_active"] for ae in ADVERSE_EVENTS]
            else:
                ae_probs = [ae["probability_placebo"] for ae in ADVERSE_EVENTS]
            
            # Normalize probabilities
            total_prob = sum(ae_probs)
            ae_probs = [p / total_prob for p in ae_probs]
            
            ae_index = random.choices(range(len(ADVERSE_EVENTS)), weights=ae_probs)[0]
            ae = ADVERSE_EVENTS[ae_index]
            
            # Determine severity
            severity = random.choices(["Mild", "Moderate", "Severe"], weights=ae["severity_dist"])[0]
            
            # Determine relatedness to treatment
            if treatment_arm == "Active":
                relatedness_probs = [0.2, 0.3, 0.3, 0.2]  # Not, Possibly, Probably, Definitely
            else:
                relatedness_probs = [0.4, 0.3, 0.2, 0.1]  # Not, Possibly, Probably, Definitely
            
            relatedness = random.choices(
                ["Not Related", "Possibly Related", "Probably Related", "Definitely Related"],
                weights=relatedness_probs
            )[0]
            
            # Determine action taken based on severity
            if severity == "Mild":
                action_probs = [0.9, 0.1, 0.0, 0.0]  # None, Reduced, Interrupted, Discontinued
            elif severity == "Moderate":
                action_probs = [0.5, 0.3, 0.2, 0.0]  # None, Reduced, Interrupted, Discontinued
            else:  # Severe
                action_probs = [0.1, 0.2, 0.4, 0.3]  # None, Reduced, Interrupted, Discontinued
            
            action = random.choices(
                ["None", "Dose Reduced", "Treatment Interrupted", "Treatment Discontinued"],
                weights=action_probs
            )[0]
            
            # Determine outcome
            if severity == "Mild":
                outcome_probs = [0.8, 0.15, 0.05, 0.0, 0.0]  # Resolved, Resolving, Not Resolved, Sequelae, Fatal
            elif severity == "Moderate":
                outcome_probs = [0.6, 0.25, 0.1, 0.05, 0.0]  # Resolved, Resolving, Not Resolved, Sequelae, Fatal
            else:  # Severe
                outcome_probs = [0.4, 0.3, 0.15, 0.1, 0.05]  # Resolved, Resolving, Not Resolved, Sequelae, Fatal
            
            outcome = random.choices(
                ["Resolved", "Resolving", "Not Resolved", "Resolved with Sequelae", "Fatal"],
                weights=outcome_probs
            )[0]
            
            # Determine start date (random day during study)
            days_offset = random.randint(1, 168)  # Between day 1 and day 168 (end of treatment)
            ae_start_date = (start_date + datetime.timedelta(days=days_offset)).strftime("%Y-%m-%d")
            
            # Determine end date based on outcome
            if outcome == "Resolved":
                duration_days = random.randint(1, 30)  # 1-30 days
                ae_end_date = (start_date + datetime.timedelta(days=days_offset + duration_days)).strftime("%Y-%m-%d")
            elif outcome == "Resolving":
                duration_days = random.randint(1, 30)  # 1-30 days
                ae_end_date = (start_date + datetime.timedelta(days=days_offset + duration_days)).strftime("%Y-%m-%d")
            elif outcome == "Fatal":
                duration_days = random.randint(1, 10)  # 1-10 days
                ae_end_date = (start_date + datetime.timedelta(days=days_offset + duration_days)).strftime("%Y-%m-%d")
            else:  # Not Resolved or Resolved with Sequelae
                ae_end_date = None
            
            adverse_events.append({
                "event_id": f"AE{ae_id_counter:06d}",
                "patient_id": patient_id,
                "event_name": ae["name"],
                "start_date": ae_start_date,
                "end_date": ae_end_date,
                "severity": severity,
                "relatedness": relatedness,
                "action_taken": action,
                "outcome": outcome
            })
            
            ae_id_counter += 1
    
    return pd.DataFrame(adverse_events)

def create_dataset() -> Dict[str, pd.DataFrame]:
    """
    Create the complete clinical trial dataset.
    
    Returns:
        Dictionary of DataFrames containing the dataset
    """
    print("Generating clinical trial dataset...")
    
    # Generate each component of the dataset
    sites_df = generate_sites()
    print(f"Generated {len(sites_df)} sites")
    
    patients_df = generate_patients(sites_df)
    print(f"Generated {len(patients_df)} patients")
    
    visits_df = generate_visits(patients_df)
    print(f"Generated {len(visits_df)} visits")
    
    labs_df = generate_labs(visits_df, patients_df)
    print(f"Generated {len(labs_df)} lab measurements")
    
    treatments_df = generate_treatments(visits_df, patients_df)
    print(f"Generated {len(treatments_df)} treatment administrations")
    
    adverse_events_df = generate_adverse_events(patients_df)
    print(f"Generated {len(adverse_events_df)} adverse events")
    
    return {
        "sites": sites_df,
        "patients": patients_df,
        "visits": visits_df,
        "labs": labs_df,
        "treatments": treatments_df,
        "adverse_events": adverse_events_df
    }

def save_dataset(dataset: Dict[str, pd.DataFrame]) -> None:
    """
    Save the dataset to CSV files.
    
    Args:
        dataset: Dictionary of DataFrames containing the dataset
    """
    # Create dataset directory if it doesn't exist
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Save each component to a CSV file
    for name, df in dataset.items():
        file_path = os.path.join(DATASET_DIR, f"{name}.csv")
        df.to_csv(file_path, index=False)
        print(f"Saved {name}.csv with {len(df)} rows")

def load_dataset() -> Dict[str, pd.DataFrame]:
    """
    Load the dataset from CSV files.
    
    Returns:
        Dictionary of DataFrames containing the dataset
    """
    dataset = {}
    
    # Check if all files exist
    files_exist = True
    for name in ["sites", "patients", "visits", "labs", "treatments", "adverse_events"]:
        file_path = os.path.join(DATASET_DIR, f"{name}.csv")
        if not os.path.exists(file_path):
            files_exist = False
            break
    
    # If all files exist, load them
    if files_exist:
        for name in ["sites", "patients", "visits", "labs", "treatments", "adverse_events"]:
            file_path = os.path.join(DATASET_DIR, f"{name}.csv")
            dataset[name] = pd.read_csv(file_path)
            print(f"Loaded {name}.csv with {len(dataset[name])} rows")
    # Otherwise, create and save the dataset
    else:
        dataset = create_dataset()
        save_dataset(dataset)
    
    return dataset

def load_to_neo4j(dataset: Dict[str, pd.DataFrame]) -> None:
    """
    Load the dataset into Neo4j.
    
    Args:
        dataset: Dictionary of DataFrames containing the dataset
    """
    try:
        from science_data_kit.data.neo4j_connector import Neo4jConnector
        
        print("Loading dataset into Neo4j...")
        
        # Initialize Neo4j connector
        neo4j = Neo4jConnector()
        
        # Clear existing data for this dataset
        neo4j.run_query("MATCH (n {dataset: 'clinical_trial'}) DETACH DELETE n")
        
        # Load sites
        for _, site in dataset["sites"].iterrows():
            query = """
            CREATE (s:Site {
                site_id: $site_id,
                location: $location,
                principal_investigator: $principal_investigator,
                enrollment_target: $enrollment_target,
                dataset: 'clinical_trial'
            })
            """
            neo4j.run_query(query, dict(site))
        
        # Load patients
        for _, patient in dataset["patients"].iterrows():
            query = """
            MATCH (s:Site {site_id: $site_id, dataset: 'clinical_trial'})
            CREATE (p:Patient {
                patient_id: $patient_id,
                age: $age,
                sex: $sex,
                race: $race,
                ethnicity: $ethnicity,
                height_cm: $height_cm,
                weight_kg: $weight_kg,
                bmi: $bmi,
                treatment_arm: $treatment_arm,
                enrollment_date: $enrollment_date,
                dataset: 'clinical_trial'
            })
            CREATE (p)-[:ENROLLED_AT]->(s)
            """
            neo4j.run_query(query, dict(patient))
        
        # Load visits
        for _, visit in dataset["visits"].iterrows():
            query = """
            MATCH (p:Patient {patient_id: $patient_id, dataset: 'clinical_trial'})
            CREATE (v:Visit {
                visit_id: $visit_id,
                visit_type: $visit_type,
                scheduled_date: $scheduled_date,
                actual_date: $actual_date,
                status: $status,
                dataset: 'clinical_trial'
            })
            CREATE (v)-[:FOR_PATIENT]->(p)
            """
            neo4j.run_query(query, dict(visit))
        
        # Load labs
        for _, lab in dataset["labs"].iterrows():
            query = """
            MATCH (p:Patient {patient_id: $patient_id, dataset: 'clinical_trial'})
            MATCH (v:Visit {visit_id: $visit_id, dataset: 'clinical_trial'})
            CREATE (l:Lab {
                lab_id: $lab_id,
                test_name: $test_name,
                value: $value,
                unit: $unit,
                reference_range: $reference_range,
                flag: $flag,
                dataset: 'clinical_trial'
            })
            CREATE (l)-[:FOR_PATIENT]->(p)
            CREATE (l)-[:COLLECTED_AT]->(v)
            """
            neo4j.run_query(query, dict(lab))
        
        # Load treatments
        for _, treatment in dataset["treatments"].iterrows():
            query = """
            MATCH (p:Patient {patient_id: $patient_id, dataset: 'clinical_trial'})
            MATCH (v:Visit {visit_id: $visit_id, dataset: 'clinical_trial'})
            CREATE (t:Treatment {
                treatment_id: $treatment_id,
                treatment_arm: $treatment_arm,
                dose: $dose,
                administration_date: $administration_date,
                compliance: $compliance,
                dataset: 'clinical_trial'
            })
            CREATE (t)-[:FOR_PATIENT]->(p)
            CREATE (t)-[:ADMINISTERED_AT]->(v)
            """
            neo4j.run_query(query, dict(treatment))
        
        # Load adverse events
        for _, ae in dataset["adverse_events"].iterrows():
            query = """
            MATCH (p:Patient {patient_id: $patient_id, dataset: 'clinical_trial'})
            CREATE (a:AdverseEvent {
                event_id: $event_id,
                event_name: $event_name,
                start_date: $start_date,
                end_date: $end_date,
                severity: $severity,
                relatedness: $relatedness,
                action_taken: $action_taken,
                outcome: $outcome,
                dataset: 'clinical_trial'
            })
            CREATE (a)-[:EXPERIENCED_BY]->(p)
            """
            neo4j.run_query(query, dict(ae))
        
        print("Dataset loaded into Neo4j successfully")
    
    except ImportError:
        print("Neo4j connector not available. Dataset not loaded into Neo4j.")
    except Exception as e:
        print(f"Error loading dataset into Neo4j: {str(e)}")

def main() -> None:
    """
    Main function to load the clinical trial dataset.
    """
    # Load or create the dataset
    dataset = load_dataset()
    
    # Load the dataset into Neo4j
    load_to_neo4j(dataset)
    
    print("Clinical trial dataset loaded successfully")

if __name__ == "__main__":
    main()