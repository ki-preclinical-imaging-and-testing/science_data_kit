"""
Science Data Kit - Checkpoint Verification Script

This script verifies the progress of users going through the 30-minute preclinical research
challenge tutorial. It checks if each step of the tutorial has been completed correctly.

Usage:
    python checkpoint_verification.py [checkpoint_number]

    If checkpoint_number is not provided, the script will check all checkpoints.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple, Union

# Import Science Data Kit components
from science_data_kit.core.database import get_database_connection
from science_data_kit.data.samples.load_preclinical_dataset import ensure_dataset_exists

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_result(checkpoint, status, message=""):
    """Print a formatted checkpoint result."""
    status_str = "✅ PASSED" if status else "❌ FAILED"
    print(f"Checkpoint {checkpoint}: {status_str}")
    if message:
        print(f"  {message}")

def run_query(query, params=None):
    """Run a Cypher query and return the results."""
    connection = get_database_connection()
    results = connection.run_query(query, params)
    return results

def check_dataset_loaded() -> bool:
    """Check if the preclinical research dataset is loaded."""
    try:
        # Check if the dataset files exist
        if not ensure_dataset_exists():
            return False
        
        # Check if the dataset is loaded in Neo4j
        query = """
        MATCH (e:Experiment {dataset: 'preclinical_research'})
        RETURN count(e) as count
        """
        result = run_query(query)
        
        if not result or result[0]["count"] == 0:
            return False
        
        # Check if all node types are present
        query = """
        MATCH (n)
        WHERE n.dataset = 'preclinical_research'
        RETURN labels(n)[0] as NodeType, count(n) as Count
        """
        results = run_query(query)
        
        # Convert results to a dictionary
        node_counts = {record["NodeType"]: record["Count"] for record in results}
        
        # Check if all required node types are present with reasonable counts
        required_nodes = ["Experiment", "Animal", "Treatment", "Imaging", "Outcome"]
        for node_type in required_nodes:
            if node_type not in node_counts or node_counts[node_type] < 1:
                return False
        
        return True
    except Exception as e:
        print(f"Error checking dataset: {e}")
        return False

def check_animal_distribution() -> bool:
    """Check if animal distribution analysis has been performed."""
    try:
        # Check if animal distribution query returns expected results
        query = """
        MATCH (a:Animal)-[:PART_OF]->(e:Experiment)
        WHERE a.dataset = 'preclinical_research'
        RETURN e.experiment_id as Experiment, a.group as Group, count(a) as Count
        ORDER BY Experiment, Group
        """
        results = run_query(query)
        
        # Check if we have results for all experiments and groups
        experiments = ["EXP001", "EXP002", "EXP003"]
        groups = ["Control", "Treatment"]
        
        # Create a set of expected (experiment, group) pairs
        expected_pairs = {(exp, group) for exp in experiments for group in groups}
        
        # Create a set of actual (experiment, group) pairs from results
        actual_pairs = {(record["Experiment"], record["Group"]) for record in results}
        
        # Check if all expected pairs are in the actual pairs
        if not expected_pairs.issubset(actual_pairs):
            return False
        
        # Check if treatment types query returns expected results
        query = """
        MATCH (t:Treatment)-[:PART_OF]->(e:Experiment)
        WHERE t.dataset = 'preclinical_research'
        RETURN e.experiment_id as Experiment, t.treatment_type as TreatmentType, 
               count(t) as Count
        ORDER BY Experiment, TreatmentType
        """
        results = run_query(query)
        
        # Check if we have results for all experiments
        if len(set(record["Experiment"] for record in results)) < 3:
            return False
        
        return True
    except Exception as e:
        print(f"Error checking animal distribution: {e}")
        return False

def check_tumor_growth_analysis() -> bool:
    """Check if tumor growth analysis has been performed."""
    try:
        # Check if tumor volume query returns expected results
        query = """
        MATCH (i:Imaging)-[:PERFORMED_ON]->(a:Animal)-[:PART_OF]->(e:Experiment)
        WHERE i.dataset = 'preclinical_research'
        RETURN e.experiment_id as Experiment, a.group as Group, i.timepoint as Timepoint,
               avg(i.tumor_volume_mm3) as AvgTumorVolume
        ORDER BY Experiment, Group, i.timepoint
        """
        results = run_query(query)
        
        # Check if we have results for all experiments, groups, and timepoints
        experiments = ["EXP001", "EXP002", "EXP003"]
        groups = ["Control", "Treatment"]
        timepoints = ["Baseline", "2 Weeks", "4 Weeks", "6 Weeks"]
        
        # Create a set of expected (experiment, group, timepoint) tuples
        expected_tuples = {
            (exp, group, timepoint) 
            for exp in experiments 
            for group in groups 
            for timepoint in timepoints
        }
        
        # Create a set of actual tuples from results
        actual_tuples = {
            (record["Experiment"], record["Group"], record["Timepoint"]) 
            for record in results
        }
        
        # Check if all expected tuples are in the actual tuples
        if not expected_tuples.issubset(actual_tuples):
            return False
        
        # Check if tumor volumes are reasonable (positive numbers)
        for record in results:
            if record["AvgTumorVolume"] <= 0:
                return False
        
        return True
    except Exception as e:
        print(f"Error checking tumor growth analysis: {e}")
        return False

def check_survival_analysis() -> bool:
    """Check if survival analysis has been performed."""
    try:
        # Check if survival data query returns expected results
        query = """
        MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
        WHERE o.dataset = 'preclinical_research'
        RETURN e.experiment_id as Experiment, a.group as Group, a.animal_id as AnimalID,
               o.survival_days as SurvivalDays, o.status as Status
        ORDER BY Experiment, Group, SurvivalDays
        """
        results = run_query(query)
        
        # Check if we have results for all experiments and groups
        experiments = ["EXP001", "EXP002", "EXP003"]
        groups = ["Control", "Treatment"]
        
        # Create a set of expected (experiment, group) pairs
        expected_pairs = {(exp, group) for exp in experiments for group in groups}
        
        # Create a set of actual (experiment, group) pairs from results
        actual_pairs = {(record["Experiment"], record["Group"]) for record in results}
        
        # Check if all expected pairs are in the actual pairs
        if not expected_pairs.issubset(actual_pairs):
            return False
        
        # Check if tumor response query returns expected results
        query = """
        MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
        WHERE o.dataset = 'preclinical_research'
        RETURN e.experiment_id as Experiment, a.group as Group, o.tumor_response as Response,
               count(o) as Count
        ORDER BY Experiment, Group, Response
        """
        results = run_query(query)
        
        # Check if we have results for all experiments and groups
        if len(set((record["Experiment"], record["Group"]) for record in results)) < 6:
            return False
        
        return True
    except Exception as e:
        print(f"Error checking survival analysis: {e}")
        return False

def check_research_questions() -> bool:
    """Check if research questions have been answered."""
    try:
        # Check if efficacy data query returns expected results
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
             count(DISTINCT CASE WHEN o.tumor_response = 'Partial Response' THEN a END) as PartialResponses
        RETURN e.experiment_id as Experiment, Group, AvgSurvival, FinalTumorVolume,
               AnimalCount, CompleteResponses, PartialResponses
        ORDER BY Experiment, Group
        """
        results = run_query(query)
        
        # Check if we have results for all experiments and groups
        experiments = ["EXP001", "EXP002", "EXP003"]
        groups = ["Control", "Treatment"]
        
        # Create a set of expected (experiment, group) pairs
        expected_pairs = {(exp, group) for exp in experiments for group in groups}
        
        # Create a set of actual (experiment, group) pairs from results
        actual_pairs = {(record["Experiment"], record["Group"]) for record in results}
        
        # Check if all expected pairs are in the actual pairs
        if not expected_pairs.issubset(actual_pairs):
            return False
        
        # Check if toxicity data query returns expected results
        query = """
        MATCH (o:Outcome)-[:RESULT_FOR]->(a:Animal)-[:PART_OF]->(e:Experiment)
        WHERE o.dataset = 'preclinical_research' AND a.group = 'Treatment'
        RETURN e.experiment_id as Experiment, avg(o.toxicity_grade) as AvgToxicityGrade
        ORDER BY Experiment
        """
        results = run_query(query)
        
        # Check if we have results for all experiments
        if len(results) < 3:
            return False
        
        return True
    except Exception as e:
        print(f"Error checking research questions: {e}")
        return False

def check_checkpoint(checkpoint: int) -> bool:
    """Check a specific checkpoint."""
    if checkpoint == 1:
        return check_dataset_loaded()
    elif checkpoint == 2:
        return check_animal_distribution()
    elif checkpoint == 3:
        return check_tumor_growth_analysis()
    elif checkpoint == 4:
        return check_survival_analysis()
    elif checkpoint == 5:
        return check_research_questions()
    else:
        print(f"Invalid checkpoint number: {checkpoint}")
        return False

def main():
    """Main function to run the checkpoint verification."""
    print_section("CHECKPOINT VERIFICATION")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            checkpoint = int(sys.argv[1])
            result = check_checkpoint(checkpoint)
            print_result(checkpoint, result)
            return 0 if result else 1
        except ValueError:
            print(f"Invalid checkpoint number: {sys.argv[1]}")
            return 1
    
    # Check all checkpoints
    all_passed = True
    
    # Checkpoint 1: Dataset loaded
    result = check_checkpoint(1)
    print_result(1, result, "Dataset loading and exploration")
    all_passed = all_passed and result
    
    # Checkpoint 2: Animal distribution
    result = check_checkpoint(2)
    print_result(2, result, "Analyzing experiments and animal groups")
    all_passed = all_passed and result
    
    # Checkpoint 3: Tumor growth analysis
    result = check_checkpoint(3)
    print_result(3, result, "Tumor growth analysis")
    all_passed = all_passed and result
    
    # Checkpoint 4: Survival analysis
    result = check_checkpoint(4)
    print_result(4, result, "Survival analysis")
    all_passed = all_passed and result
    
    # Checkpoint 5: Research questions
    result = check_checkpoint(5)
    print_result(5, result, "Answering research questions")
    all_passed = all_passed and result
    
    # Print overall result
    print("\nOverall result:", "✅ ALL CHECKPOINTS PASSED" if all_passed else "❌ SOME CHECKPOINTS FAILED")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())