"""
Interactive Demos Component for Science Data Kit

This module provides functionality for displaying interactive demos in the Science Data Kit application.
It includes classes and functions for:
- Loading interactive demo metadata
- Displaying interactive demos
- Providing information about available demos
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
import importlib.util
import sys

class InteractiveDemos:
    """
    Interactive demos class for Science Data Kit.
    
    This class provides methods for loading and displaying interactive demos.
    """
    
    def __init__(self):
        """Initialize the interactive demos component."""
        self.demos = self._load_demos()
    
    def _load_demos(self) -> List[Dict[str, Any]]:
        """
        Load interactive demo metadata from JSON files.
        
        Returns:
            A list of dictionaries containing demo metadata.
        """
        demos = []
        
        # Path to the metadata directory
        metadata_dir = Path(__file__).parent.parent.parent.parent / "interactive_demos" / "metadata"
        
        # Check if the directory exists
        if not metadata_dir.exists():
            # Create the directory structure if it doesn't exist
            metadata_dir.parent.mkdir(parents=True, exist_ok=True)
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a README file
            readme_path = metadata_dir.parent / "README.md"
            with open(readme_path, "w") as f:
                f.write("""# Science Data Kit Interactive Demos

This directory contains interactive demonstrations for the Science Data Kit. These demos provide hands-on experience with key features and workflows in the Science Data Kit.

## Directory Structure

- `metadata/`: Contains metadata files for each interactive demo, including titles, descriptions, and parameters
- `demos/`: Contains the Python modules that implement the interactive demos
- `resources/`: Contains additional resources used in the interactive demos, such as sample data files

## Available Interactive Demos

1. **Data Explorer Demo**: Interactive exploration of scientific datasets
2. **Visualization Builder Demo**: Interactive creation of data visualizations
3. **Query Builder Demo**: Interactive construction of database queries
4. **Analysis Pipeline Demo**: Interactive creation of data analysis pipelines
5. **Dashboard Creator Demo**: Interactive creation of data dashboards

## Usage Guidelines

Interactive demos are designed to be:

1. **Self-contained**: Each demo includes all necessary components and dependencies
2. **User-friendly**: Demos provide clear instructions and feedback
3. **Educational**: Demos teach concepts and skills through hands-on interaction
4. **Progressive**: Demos start simple and gradually introduce more advanced features

## Creating New Interactive Demos

To create a new interactive demo:

1. Create a new Python module in the `demos/` directory
2. Implement the demo using Streamlit components
3. Create a metadata file in the `metadata/` directory
4. Test the demo thoroughly with different inputs and scenarios

## Usage

The interactive demos are accessible through the workshop page and can be used for self-guided exploration or as part of structured workshop activities.
""")
            
            # Create the demos directory
            demos_dir = metadata_dir.parent / "demos"
            demos_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the resources directory
            resources_dir = metadata_dir.parent / "resources"
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            # Create sample demo files
            demo_files = [
                {
                    "id": "data_explorer",
                    "title": "Data Explorer Demo",
                    "filename": "data_explorer_demo.py",
                    "content": """
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_demo(params=None):
    \"\"\"
    Run the Data Explorer interactive demo.
    
    Args:
        params: Optional parameters for the demo.
    \"\"\"
    st.title("Data Explorer Demo")
    
    st.markdown(\"\"\"
    This interactive demo allows you to explore scientific datasets using the Science Data Kit.
    You can load sample datasets, view their structure, generate summary statistics, and create visualizations.
    
    Follow the steps below to explore the data:
    1. Select a dataset
    2. Examine the data structure
    3. Generate summary statistics
    4. Create visualizations
    \"\"\")
    
    # Step 1: Select a dataset
    st.header("Step 1: Select a Dataset")
    
    dataset_option = st.selectbox(
        "Choose a dataset to explore:",
        ["Clinical Trial Data", "Genomics Data", "Preclinical Research Data", "Sample Tabular Data"]
    )
    
    # Load the selected dataset
    if dataset_option == "Sample Tabular Data":
        # Generate a sample dataset
        data = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'] * 10,
            'Values': np.random.randn(50) * 100,
            'Group': ['Group 1', 'Group 2'] * 25,
            'Date': pd.date_range(start='1/1/2020', periods=50),
            'Metric': np.random.randint(1, 100, 50)
        })
    elif dataset_option == "Clinical Trial Data":
        # Simulated clinical trial data
        data = pd.DataFrame({
            'Patient_ID': [f'P{i:03d}' for i in range(1, 51)],
            'Age': np.random.randint(18, 80, 50),
            'Gender': np.random.choice(['Male', 'Female'], 50),
            'Treatment': np.random.choice(['Drug A', 'Drug B', 'Placebo'], 50),
            'Response': np.random.choice(['Improved', 'No Change', 'Worsened'], 50, 
                                        p=[0.5, 0.3, 0.2]),
            'Adverse_Events': np.random.randint(0, 5, 50),
            'Baseline_Value': np.random.normal(100, 15, 50),
            'Final_Value': np.random.normal(85, 20, 50)
        })
    elif dataset_option == "Genomics Data":
        # Simulated genomics data
        genes = [f'Gene_{chr(65+i)}_{j}' for i in range(5) for j in range(10)]
        samples = [f'Sample_{i:02d}' for i in range(20)]
        
        # Create a DataFrame with gene expression values
        data = pd.DataFrame(
            np.random.normal(10, 5, (len(samples), len(genes))),
            columns=genes,
            index=samples
        )
        
        # Add sample metadata
        sample_type = np.random.choice(['Tumor', 'Normal'], len(samples))
        data = data.reset_index().rename(columns={'index': 'Sample_ID'})
        data['Sample_Type'] = sample_type
        data['Batch'] = np.random.choice(['Batch_1', 'Batch_2', 'Batch_3'], len(samples))
    else:  # Preclinical Research Data
        # Simulated preclinical research data
        data = pd.DataFrame({
            'Compound_ID': [f'CMP{i:03d}' for i in range(1, 41)],
            'Target': np.random.choice(['Target_A', 'Target_B', 'Target_C', 'Target_D'], 40),
            'IC50_nM': np.random.lognormal(3, 1, 40),
            'Solubility_uM': np.random.lognormal(2, 1.5, 40),
            'Permeability': np.random.choice(['High', 'Medium', 'Low'], 40),
            'Toxicity': np.random.choice(['None', 'Low', 'Moderate', 'High'], 40),
            'Selectivity': np.random.uniform(1, 100, 40)
        })
    
    # Step 2: Examine the data structure
    st.header("Step 2: Examine the Data Structure")
    
    # Show the first few rows of the dataset
    st.subheader("Data Preview")
    st.dataframe(data.head())
    
    # Show dataset information
    st.subheader("Dataset Information")
    
    # Create two columns for displaying information
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Number of Rows", data.shape[0])
        st.metric("Number of Columns", data.shape[1])
    
    with col2:
        st.write("Column Data Types:")
        st.write(data.dtypes)
    
    # Step 3: Generate summary statistics
    st.header("Step 3: Generate Summary Statistics")
    
    # Select columns for analysis
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if numeric_cols:
        st.subheader("Numeric Columns Summary")
        st.dataframe(data[numeric_cols].describe())
    
    if categorical_cols:
        st.subheader("Categorical Columns Summary")
        for col in categorical_cols:
            st.write(f"**{col}** value counts:")
            st.write(data[col].value_counts())
    
    # Step 4: Create visualizations
    st.header("Step 4: Create Visualizations")
    
    # Select visualization type
    viz_type = st.selectbox(
        "Select visualization type:",
        ["Bar Chart", "Histogram", "Scatter Plot", "Box Plot", "Heatmap"]
    )
    
    if viz_type == "Bar Chart" and categorical_cols:
        # Bar chart settings
        x_col = st.selectbox("Select category column (X-axis):", categorical_cols)
        
        if numeric_cols:
            y_col = st.selectbox("Select value column (Y-axis):", numeric_cols)
            agg_func = st.selectbox("Select aggregation function:", ["mean", "sum", "count", "median", "min", "max"])
            
            # Create the bar chart
            st.subheader(f"Bar Chart: {agg_func.capitalize()} of {y_col} by {x_col}")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            data.groupby(x_col)[y_col].agg(agg_func).plot(kind='bar', ax=ax)
            plt.xlabel(x_col)
            plt.ylabel(f"{agg_func.capitalize()} of {y_col}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            # Simple count bar chart
            st.subheader(f"Bar Chart: Count by {x_col}")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            data[x_col].value_counts().plot(kind='bar', ax=ax)
            plt.xlabel(x_col)
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
    
    elif viz_type == "Histogram" and numeric_cols:
        # Histogram settings
        hist_col = st.selectbox("Select column for histogram:", numeric_cols)
        bins = st.slider("Number of bins:", min_value=5, max_value=50, value=20)
        
        # Create the histogram
        st.subheader(f"Histogram: Distribution of {hist_col}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        data[hist_col].plot(kind='hist', bins=bins, ax=ax)
        plt.xlabel(hist_col)
        plt.ylabel("Frequency")
        plt.tight_layout()
        
        st.pyplot(fig)
    
    elif viz_type == "Scatter Plot" and len(numeric_cols) >= 2:
        # Scatter plot settings
        x_col = st.selectbox("Select X-axis column:", numeric_cols)
        y_col = st.selectbox("Select Y-axis column:", [col for col in numeric_cols if col != x_col])
        
        color_col = None
        if categorical_cols:
            use_color = st.checkbox("Color points by category")
            if use_color:
                color_col = st.selectbox("Select column for color:", categorical_cols)
        
        # Create the scatter plot
        st.subheader(f"Scatter Plot: {y_col} vs {x_col}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if color_col:
            for category, group in data.groupby(color_col):
                ax.scatter(group[x_col], group[y_col], label=category, alpha=0.7)
            ax.legend()
        else:
            ax.scatter(data[x_col], data[y_col], alpha=0.7)
        
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.tight_layout()
        
        st.pyplot(fig)
    
    elif viz_type == "Box Plot" and numeric_cols:
        # Box plot settings
        y_col = st.selectbox("Select column for values:", numeric_cols)
        
        if categorical_cols:
            x_col = st.selectbox("Select category column for grouping:", categorical_cols)
            
            # Create the box plot
            st.subheader(f"Box Plot: {y_col} by {x_col}")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(x=x_col, y=y_col, data=data, ax=ax)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.warning("Box plot requires at least one categorical column for grouping.")
    
    elif viz_type == "Heatmap" and len(numeric_cols) >= 2:
        # Heatmap settings
        st.subheader("Correlation Heatmap")
        
        # Select columns for correlation
        selected_cols = st.multiselect(
            "Select columns for correlation analysis:",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
        
        if selected_cols and len(selected_cols) >= 2:
            # Create the correlation heatmap
            corr = data[selected_cols].corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.warning("Please select at least two numeric columns for the correlation heatmap.")
    
    else:
        st.warning("The selected visualization type is not applicable to the current dataset.")
    
    # Conclusion
    st.header("Conclusion")
    st.markdown(\"\"\"
    This interactive demo has shown you how to:
    
    1. Load and examine different types of scientific datasets
    2. Generate summary statistics to understand data distributions
    3. Create various visualizations to explore relationships in the data
    
    These skills are fundamental for data exploration and analysis in scientific research.
    
    To learn more, check out the following resources:
    - [Data Visualization Tutorial](http://localhost:8888/lab/tree/tutorials/data_visualization_tutorial.ipynb)
    - [Data Transformation Tutorial](http://localhost:8888/lab/tree/tutorials/data_transformation_tutorial.ipynb)
    - [Database Operations Tutorial](http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb)
    \"\"\")
    
    # Return any results or state if needed
    return {"status": "completed", "dataset": dataset_option}

if __name__ == "__main__":
    run_demo()
"""
                },
                {
                    "id": "visualization_builder",
                    "title": "Visualization Builder Demo",
                    "filename": "visualization_builder_demo.py",
                    "content": """
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def run_demo(params=None):
    \"\"\"
    Run the Visualization Builder interactive demo.
    
    Args:
        params: Optional parameters for the demo.
    \"\"\"
    st.title("Visualization Builder Demo")
    
    st.markdown(\"\"\"
    This interactive demo allows you to build custom visualizations using the Science Data Kit.
    You can select from various chart types, customize their appearance, and export the results.
    
    Follow the steps below to create your visualization:
    1. Select a dataset
    2. Choose a visualization type
    3. Configure visualization parameters
    4. Customize appearance
    5. Export or share your visualization
    \"\"\")
    
    # Step 1: Select a dataset
    st.header("Step 1: Select a Dataset")
    
    dataset_option = st.selectbox(
        "Choose a dataset:",
        ["Sample Sales Data", "Clinical Trial Results", "Stock Market Data", "Custom Data"]
    )
    
    # Load the selected dataset
    if dataset_option == "Sample Sales Data":
        # Generate a sample sales dataset
        data = pd.DataFrame({
            'Product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'] * 12,
            'Category': ['Electronics', 'Electronics', 'Clothing', 'Home', 'Home'] * 12,
            'Region': np.repeat(['North', 'South', 'East', 'West'], 15),
            'Month': np.tile(pd.date_range(start='1/1/2023', periods=12, freq='M').strftime('%b'), 5),
            'Sales': np.random.randint(1000, 10000, 60),
            'Profit': np.random.randint(100, 2000, 60),
            'Units': np.random.randint(10, 100, 60)
        })
    elif dataset_option == "Clinical Trial Results":
        # Simulated clinical trial data
        treatments = ['Treatment A', 'Treatment B', 'Placebo']
        timepoints = ['Baseline', 'Week 4', 'Week 8', 'Week 12']
        
        # Create patient IDs and randomize treatments
        patients = [f'Patient {i:03d}' for i in range(1, 61)]
        treatment_groups = np.random.choice(treatments, len(patients))
        
        # Create a list to build the DataFrame
        rows = []
        
        for i, patient in enumerate(patients):
            treatment = treatment_groups[i]
            # Baseline value between 90-110
            baseline = np.random.normal(100, 5)
            
            # Effect size depends on treatment
            if treatment == 'Treatment A':
                effect = -20  # Strong effect
            elif treatment == 'Treatment B':
                effect = -10  # Moderate effect
            else:  # Placebo
                effect = -2   # Minimal effect
            
            # Add some random variation
            for timepoint in timepoints:
                if timepoint == 'Baseline':
                    value = baseline
                else:
                    # Progressive effect over time with some random noise
                    week = int(timepoint.split()[1])
                    progress_factor = week / 12
                    value = baseline + (effect * progress_factor) + np.random.normal(0, 3)
                
                rows.append({
                    'Patient': patient,
                    'Treatment': treatment,
                    'Timepoint': timepoint,
                    'Value': value,
                    'Age': np.random.randint(18, 75),
                    'Gender': np.random.choice(['Male', 'Female']),
                    'Responder': value < (baseline - 10)  # Responder if value decreased by more than 10
                })
        
        data = pd.DataFrame(rows)
    elif dataset_option == "Stock Market Data":
        # Simulated stock market data
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        dates = pd.date_range(start='1/1/2023', periods=252, freq='B')  # Business days
        
        # Create a list to build the DataFrame
        rows = []
        
        for stock in stocks:
            # Initial price between 100-500
            price = np.random.uniform(100, 500)
            
            for date in dates:
                # Daily return with some randomness
                daily_return = np.random.normal(0.0005, 0.015)  # Mean 0.05% daily return
                price *= (1 + daily_return)
                
                volume = np.random.randint(1000000, 10000000)
                
                rows.append({
                    'Date': date,
                    'Stock': stock,
                    'Price': price,
                    'Volume': volume,
                    'Return': daily_return,
                    'Sector': np.random.choice(['Technology', 'E-commerce', 'Social Media']),
                    'Market_Cap': price * volume / 1000000  # Simplified market cap calculation
                })
        
        data = pd.DataFrame(rows)
    else:  # Custom Data
        st.info("For custom data, we'll use a sample dataset that you can modify.")
        
        # Create a sample dataset as a starting point
        data = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'] * 4,
            'Group': ['Group 1', 'Group 2'] * 10,
            'Value1': np.random.randint(1, 100, 20),
            'Value2': np.random.randint(1, 100, 20),
            'Value3': np.random.normal(50, 15, 20)
        })
        
        # Allow the user to edit the data
        st.subheader("Edit Custom Data")
        edited_data = st.data_editor(data)
        data = edited_data
    
    # Display a preview of the data
    st.subheader("Data Preview")
    st.dataframe(data.head())
    
    # Step 2: Choose a visualization type
    st.header("Step 2: Choose a Visualization Type")
    
    viz_type = st.selectbox(
        "Select visualization type:",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Heatmap", "Box Plot", "Histogram", "Area Chart", "Bubble Chart"]
    )
    
    # Step 3: Configure visualization parameters
    st.header("Step 3: Configure Visualization Parameters")
    
    # Get column lists by type
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower() or 
                 (hasattr(data[col], 'dt') and hasattr(data[col].dt, 'date'))]
    
    # Configuration based on visualization type
    if viz_type == "Bar Chart":
        st.subheader("Bar Chart Configuration")
        
        x_col = st.selectbox("Select X-axis (categories):", categorical_cols if categorical_cols else data.columns.tolist())
        y_col = st.selectbox("Select Y-axis (values):", numeric_cols if numeric_cols else data.columns.tolist())
        
        orientation = st.radio("Orientation:", ["Vertical", "Horizontal"])
        
        color_by = None
        if len(categorical_cols) > 1:
            use_color = st.checkbox("Color by category")
            if use_color:
                color_options = [col for col in categorical_cols if col != x_col]
                if color_options:
                    color_by = st.selectbox("Select column for color:", color_options)
        
        agg_func = st.selectbox("Aggregation function:", ["sum", "mean", "count", "median", "min", "max"])
        
        # Create the visualization
        st.subheader("Bar Chart Visualization")
        
        if orientation == "Vertical":
            if color_by:
                fig = px.bar(data, x=x_col, y=y_col, color=color_by, barmode='group',
                            title=f"{agg_func.capitalize()} of {y_col} by {x_col}",
                            height=500)
            else:
                fig = px.bar(data, x=x_col, y=y_col,
                            title=f"{agg_func.capitalize()} of {y_col} by {x_col}",
                            height=500)
        else:  # Horizontal
            if color_by:
                fig = px.bar(data, y=x_col, x=y_col, color=color_by, barmode='group',
                            title=f"{agg_func.capitalize()} of {y_col} by {x_col}",
                            height=500, orientation='h')
            else:
                fig = px.bar(data, y=x_col, x=y_col,
                            title=f"{agg_func.capitalize()} of {y_col} by {x_col}",
                            height=500, orientation='h')
    
    elif viz_type == "Line Chart":
        st.subheader("Line Chart Configuration")
        
        # For line charts, we typically need a date/time column or a sequential column
        if date_cols:
            x_col = st.selectbox("Select X-axis (time/sequence):", date_cols)
        else:
            x_col = st.selectbox("Select X-axis (time/sequence):", data.columns.tolist())
        
        y_cols = st.multiselect("Select Y-axis (values):", numeric_cols if numeric_cols else data.columns.tolist())
        
        if not y_cols:
            st.warning("Please select at least one column for Y-axis.")
            return
        
        group_by = None
        if categorical_cols:
            use_groups = st.checkbox("Group by category")
            if use_groups:
                group_by = st.selectbox("Select column for grouping:", categorical_cols)
        
        # Create the visualization
        st.subheader("Line Chart Visualization")
        
        if group_by:
            fig = px.line(data, x=x_col, y=y_cols, color=group_by,
                        title=f"{', '.join(y_cols)} over {x_col} by {group_by}",
                        height=500)
        else:
            fig = px.line(data, x=x_col, y=y_cols,
                        title=f"{', '.join(y_cols)} over {x_col}",
                        height=500)
    
    elif viz_type == "Scatter Plot":
        st.subheader("Scatter Plot Configuration")
        
        x_col = st.selectbox("Select X-axis:", numeric_cols if numeric_cols else data.columns.tolist())
        y_col = st.selectbox("Select Y-axis:", [col for col in numeric_cols if col != x_col] if len(numeric_cols) > 1 else data.columns.tolist())
        
        color_by = None
        if categorical_cols:
            use_color = st.checkbox("Color by category")
            if use_color:
                color_by = st.selectbox("Select column for color:", categorical_cols)
        
        size_by = None
        if len(numeric_cols) > 2:
            use_size = st.checkbox("Size by value")
            if use_size:
                size_options = [col for col in numeric_cols if col != x_col and col != y_col]
                if size_options:
                    size_by = st.selectbox("Select column for point size:", size_options)
        
        # Create the visualization
        st.subheader("Scatter Plot Visualization")
        
        if color_by and size_by:
            fig = px.scatter(data, x=x_col, y=y_col, color=color_by, size=size_by,
                            title=f"{y_col} vs {x_col} (colored by {color_by}, sized by {size_by})",
                            height=500)
        elif color_by:
            fig = px.scatter(data, x=x_col, y=y_col, color=color_by,
                            title=f"{y_col} vs {x_col} (colored by {color_by})",
                            height=500)
        elif size_by:
            fig = px.scatter(data, x=x_col, y=y_col, size=size_by,
                            title=f"{y_col} vs {x_col} (sized by {size_by})",
                            height=500)
        else:
            fig = px.scatter(data, x=x_col, y=y_col,
                            title=f"{y_col} vs {x_col}",
                            height=500)
    
    elif viz_type == "Pie Chart":
        st.subheader("Pie Chart Configuration")
        
        names_col = st.selectbox("Select column for categories:", categorical_cols if categorical_cols else data.columns.tolist())
        values_col = st.selectbox("Select column for values:", numeric_cols if numeric_cols else data.columns.tolist())
        
        # Create the visualization
        st.subheader("Pie Chart Visualization")
        
        fig = px.pie(data, names=names_col, values=values_col,
                    title=f"Distribution of {values_col} by {names_col}",
                    height=500)
    
    elif viz_type == "Heatmap":
        st.subheader("Heatmap Configuration")
        
        # For heatmaps, we need at least two categorical columns and one numeric column
        if len(categorical_cols) >= 2 and numeric_cols:
            x_col = st.selectbox("Select X-axis (categories):", categorical_cols)
            y_col = st.selectbox("Select Y-axis (categories):", [col for col in categorical_cols if col != x_col])
            value_col = st.selectbox("Select values:", numeric_cols)
            
            agg_func = st.selectbox("Aggregation function:", ["mean", "sum", "count", "median", "min", "max"])
            
            # Create a pivot table for the heatmap
            pivot_data = data.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc=agg_func)
            
            # Create the visualization
            st.subheader("Heatmap Visualization")
            
            fig = px.imshow(pivot_data, 
                           title=f"Heatmap of {value_col} ({agg_func}) by {x_col} and {y_col}",
                           height=500)
        else:
            st.warning("Heatmap requires at least two categorical columns and one numeric column.")
            
            # Create a correlation heatmap as an alternative
            if len(numeric_cols) >= 2:
                st.info("Creating a correlation heatmap of numeric columns instead.")
                
                # Select columns for correlation
                selected_cols = st.multiselect(
                    "Select columns for correlation analysis:",
                    numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))]
                )
                
                if selected_cols and len(selected_cols) >= 2:
                    # Create the correlation heatmap
                    corr = data[selected_cols].corr()
                    
                    fig = px.imshow(corr,
                                   title="Correlation Heatmap",
                                   height=500)
                else:
                    st.warning("Please select at least two numeric columns for the correlation heatmap.")
                    return
            else:
                st.error("Not enough appropriate columns for any type of heatmap.")
                return
    
    elif viz_type == "Box Plot":
        st.subheader("Box Plot Configuration")
        
        if categorical_cols and numeric_cols:
            x_col = st.selectbox("Select X-axis (categories):", categorical_cols)
            y_col = st.selectbox("Select Y-axis (values):", numeric_cols)
            
            color_by = None
            if len(categorical_cols) > 1:
                use_color = st.checkbox("Color by category")
                if use_color:
                    color_options = [col for col in categorical_cols if col != x_col]
                    if color_options:
                        color_by = st.selectbox("Select column for color:", color_options)
            
            # Create the visualization
            st.subheader("Box Plot Visualization")
            
            if color_by:
                fig = px.box(data, x=x_col, y=y_col, color=color_by,
                            title=f"Distribution of {y_col} by {x_col} and {color_by}",
                            height=500)
            else:
                fig = px.box(data, x=x_col, y=y_col,
                            title=f"Distribution of {y_col} by {x_col}",
                            height=500)
        else:
            st.warning("Box plot requires at least one categorical column and one numeric column.")
            return
    
    elif viz_type == "Histogram":
        st.subheader("Histogram Configuration")
        
        if numeric_cols:
            value_col = st.selectbox("Select column for histogram:", numeric_cols)
            
            bins = st.slider("Number of bins:", min_value=5, max_value=50, value=20)
            
            color_by = None
            if categorical_cols:
                use_color = st.checkbox("Color by category")
                if use_color:
                    color_by = st.selectbox("Select column for color:", categorical_cols)
            
            # Create the visualization
            st.subheader("Histogram Visualization")
            
            if color_by:
                fig = px.histogram(data, x=value_col, color=color_by, nbins=bins,
                                title=f"Distribution of {value_col} by {color_by}",
                                height=500)
            else:
                fig = px.histogram(data, x=value_col, nbins=bins,
                                title=f"Distribution of {value_col}",
                                height=500)
        else:
            st.warning("Histogram requires at least one numeric column.")
            return
    
    elif viz_type == "Area Chart":
        st.subheader("Area Chart Configuration")
        
        # For area charts, we typically need a date/time column or a sequential column
        if date_cols:
            x_col = st.selectbox("Select X-axis (time/sequence):", date_cols)
        else:
            x_col = st.selectbox("Select X-axis (time/sequence):", data.columns.tolist())
        
        y_col = st.selectbox("Select Y-axis (values):", numeric_cols if numeric_cols else data.columns.tolist())
        
        group_by = None
        if categorical_cols:
            use_groups = st.checkbox("Group by category")
            if use_groups:
                group_by = st.selectbox("Select column for grouping:", categorical_cols)
        
        # Create the visualization
        st.subheader("Area Chart Visualization")
        
        if group_by:
            fig = px.area(data, x=x_col, y=y_col, color=group_by,
                        title=f"{y_col} over {x_col} by {group_by}",
                        height=500)
        else:
            fig = px.area(data, x=x_col, y=y_col,
                        title=f"{y_col} over {x_col}",
                        height=500)
    
    elif viz_type == "Bubble Chart":
        st.subheader("Bubble Chart Configuration")
        
        if len(numeric_cols) >= 3:
            x_col = st.selectbox("Select X-axis:", numeric_cols)
            y_col = st.selectbox("Select Y-axis:", [col for col in numeric_cols if col != x_col])
            size_col = st.selectbox("Select bubble size:", [col for col in numeric_cols if col != x_col and col != y_col])
            
            color_by = None
            if categorical_cols:
                use_color = st.checkbox("Color by category")
                if use_color:
                    color_by = st.selectbox("Select column for color:", categorical_cols)
            
            # Create the visualization
            st.subheader("Bubble Chart Visualization")
            
            if color_by:
                fig = px.scatter(data, x=x_col, y=y_col, size=size_col, color=color_by,
                                title=f"{y_col} vs {x_col} (sized by {size_col}, colored by {color_by})",
                                height=500)
            else:
                fig = px.scatter(data, x=x_col, y=y_col, size=size_col,
                                title=f"{y_col} vs {x_col} (sized by {size_col})",
                                height=500)
        else:
            st.warning("Bubble chart requires at least three numeric columns.")
            return
    
    else:
        st.error(f"Visualization type '{viz_type}' not implemented.")
        return
    
    # Step 4: Customize appearance
    st.header("Step 4: Customize Appearance")
    
    with st.expander("Customize Chart Appearance"):
        # Title and labels
        chart_title = st.text_input("Chart Title:", fig.layout.title.text)
        x_axis_title = st.text_input("X-axis Label:", x_col)
        y_axis_title = st.text_input("Y-axis Label:", y_col if viz_type != "Pie Chart" else "")
        
        # Color scheme
        color_scheme = st.selectbox("Color Scheme:", 
                                   ["default", "Viridis", "Plasma", "Inferno", "Magma", "Cividis", 
                                    "Rainbow", "Blues", "Greens", "Reds", "Purples", "Oranges"])
        
        # Legend position
        legend_pos = st.selectbox("Legend Position:", ["right", "top", "bottom", "left"])
        
        # Apply customizations
        fig.update_layout(
            title=chart_title,
            xaxis_title=x_axis_title,
            yaxis_title=y_axis_title,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) if legend_pos == "top" else
                   dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02) if legend_pos == "right" else
                   dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5) if legend_pos == "bottom" else
                   dict(orientation="v", yanchor="top", y=1, xanchor="right", x=-0.02)
        )
        
        if color_scheme != "default" and viz_type != "Heatmap":
            fig.update_traces(marker=dict(colorscale=color_scheme.lower()))
        elif color_scheme != "default" and viz_type == "Heatmap":
            fig.update_traces(colorscale=color_scheme.lower())
    
    # Display the final visualization
    st.plotly_chart(fig, use_container_width=True)
    
    # Step 5: Export or share
    st.header("Step 5: Export or Share")
    
    export_format = st.selectbox("Export Format:", ["HTML", "PNG", "SVG", "JSON"])
    
    if export_format == "HTML":
        html_str = fig.to_html(include_plotlyjs="cdn")
        st.download_button(
            label="Download HTML",
            data=html_str,
            file_name=f"{viz_type.lower().replace(' ', '_')}_visualization.html",
            mime="text/html"
        )
    elif export_format == "PNG":
        # In a real implementation, this would generate a PNG file
        st.download_button(
            label="Download PNG",
            data="This is a placeholder. In a real implementation, this would generate a PNG file.",
            file_name=f"{viz_type.lower().replace(' ', '_')}_visualization.png",
            mime="image/png"
        )
    elif export_format == "SVG":
        # In a real implementation, this would generate an SVG file
        st.download_button(
            label="Download SVG",
            data="This is a placeholder. In a real implementation, this would generate an SVG file.",
            file_name=f"{viz_type.lower().replace(' ', '_')}_visualization.svg",
            mime="image/svg+xml"
        )
    elif export_format == "JSON":
        json_str = fig.to_json()
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"{viz_type.lower().replace(' ', '_')}_visualization.json",
            mime="application/json"
        )
    
    # Conclusion
    st.header("Conclusion")
    st.markdown(\"\"\"
    This interactive demo has shown you how to:
    
    1. Select and prepare data for visualization
    2. Choose appropriate visualization types for different data
    3. Configure visualization parameters
    4. Customize visualization appearance
    5. Export visualizations in various formats
    
    These skills are essential for effective data communication in scientific research.
    
    To learn more, check out the following resources:
    - [Data Visualization Tutorial](http://localhost:8888/lab/tree/tutorials/data_visualization_tutorial.ipynb)
    - [Plotly Documentation](https://plotly.com/python/)
    - [Visualization Best Practices](https://your-org.github.io/science_data_kit/visualization_best_practices.html)
    \"\"\")
    
    # Return any results or state if needed
    return {"status": "completed", "visualization_type": viz_type}

if __name__ == "__main__":
    run_demo()
"""
                },
                {
                    "id": "query_builder",
                    "title": "Query Builder Demo",
                    "filename": "query_builder_demo.py",
                    "content": """
import streamlit as st
import pandas as pd
import numpy as np
import re

def run_demo(params=None):
    \"\"\"
    Run the Query Builder interactive demo.
    
    Args:
        params: Optional parameters for the demo.
    \"\"\"
    st.title("Query Builder Demo")
    
    st.markdown(\"\"\"
    This interactive demo allows you to build database queries using the Science Data Kit.
    You can construct Cypher queries for Neo4j databases without writing code, visualize the query structure,
    and see the results.
    
    Follow the steps below to build your query:
    1. Define the data model
    2. Select node types and relationships
    3. Add filters and conditions
    4. Specify return values
    5. Execute and visualize results
    \"\"\")
    
    # Step 1: Define the data model
    st.header("Step 1: Define the Data Model")
    
    # Offer predefined data models or custom definition
    data_model_option = st.selectbox(
        "Choose a data model:",
        ["Clinical Trial Data", "Publication Network", "Protein Interaction Network", "Custom Data Model"]
    )
    
    # Define the data model based on selection
    if data_model_option == "Clinical Trial Data":
        nodes = [
            {"label": "Patient", "properties": ["id", "age", "gender", "ethnicity"]},
            {"label": "Treatment", "properties": ["id", "name", "dosage", "frequency"]},
            {"label": "Outcome", "properties": ["id", "measure", "value", "timepoint"]},
            {"label": "AdverseEvent", "properties": ["id", "type", "severity", "onset"]},
            {"label": "Study", "properties": ["id", "title", "phase", "start_date", "end_date"]}
        ]
        
        relationships = [
            {"type": "ENROLLED_IN", "source": "Patient", "target": "Study", "properties": ["enrollment_date"]},
            {"type": "RECEIVED", "source": "Patient", "target": "Treatment", "properties": ["start_date", "end_date"]},
            {"type": "REPORTED", "source": "Patient", "target": "Outcome", "properties": ["report_date"]},
            {"type": "EXPERIENCED", "source": "Patient", "target": "AdverseEvent", "properties": ["report_date"]},
            {"type": "PART_OF", "source": "Treatment", "target": "Study", "properties": []},
            {"type": "MEASURED_IN", "source": "Outcome", "target": "Study", "properties": []}
        ]
        
        # Sample data for demonstration
        sample_data = {
            "Patient": pd.DataFrame({
                "id": ["P001", "P002", "P003", "P004", "P005"],
                "age": [45, 62, 38, 71, 53],
                "gender": ["Male", "Female", "Female", "Male", "Male"],
                "ethnicity": ["Caucasian", "African American", "Hispanic", "Asian", "Caucasian"]
            }),
            "Treatment": pd.DataFrame({
                "id": ["T001", "T002", "T003"],
                "name": ["Drug A", "Drug B", "Placebo"],
                "dosage": ["100mg", "50mg", "0mg"],
                "frequency": ["Daily", "Twice daily", "Daily"]
            }),
            "Study": pd.DataFrame({
                "id": ["S001"],
                "title": ["Phase 3 Trial of Drug A vs Drug B"],
                "phase": ["Phase 3"],
                "start_date": ["2023-01-15"],
                "end_date": ["2023-07-15"]
            })
        }
    
    elif data_model_option == "Publication Network":
        nodes = [
            {"label": "Author", "properties": ["id", "name", "affiliation", "h_index"]},
            {"label": "Paper", "properties": ["id", "title", "journal", "year", "doi", "citations"]},
            {"label": "Topic", "properties": ["id", "name", "field"]},
            {"label": "Institution", "properties": ["id", "name", "country", "type"]},
            {"label": "Journal", "properties": ["id", "name", "impact_factor", "publisher"]}
        ]
        
        relationships = [
            {"type": "AUTHORED", "source": "Author", "target": "Paper", "properties": ["order", "corresponding"]},
            {"type": "CITES", "source": "Paper", "target": "Paper", "properties": ["context"]},
            {"type": "COVERS", "source": "Paper", "target": "Topic", "properties": ["relevance"]},
            {"type": "AFFILIATED_WITH", "source": "Author", "target": "Institution", "properties": ["start_year", "end_year"]},
            {"type": "PUBLISHED_IN", "source": "Paper", "target": "Journal", "properties": ["publication_date"]},
            {"type": "SPECIALIZES_IN", "source": "Author", "target": "Topic", "properties": ["expertise_level"]}
        ]
        
        # Sample data for demonstration
        sample_data = {
            "Author": pd.DataFrame({
                "id": ["A001", "A002", "A003", "A004", "A005"],
                "name": ["John Smith", "Maria Garcia", "David Chen", "Sarah Johnson", "Ahmed Hassan"],
                "affiliation": ["Stanford University", "MIT", "Harvard University", "Oxford University", "Cairo University"],
                "h_index": [25, 18, 32, 15, 10]
            }),
            "Paper": pd.DataFrame({
                "id": ["P001", "P002", "P003"],
                "title": ["Advances in Graph Neural Networks", "Protein Folding Prediction", "Climate Change Effects on Biodiversity"],
                "journal": ["Nature Machine Intelligence", "Science", "Nature Climate Change"],
                "year": [2022, 2021, 2023],
                "citations": [45, 120, 8]
            }),
            "Topic": pd.DataFrame({
                "id": ["T001", "T002", "T003", "T004"],
                "name": ["Machine Learning", "Protein Structure", "Climate Change", "Biodiversity"],
                "field": ["Computer Science", "Biology", "Environmental Science", "Ecology"]
            })
        }
    
    elif data_model_option == "Protein Interaction Network":
        nodes = [
            {"label": "Protein", "properties": ["id", "name", "uniprot_id", "molecular_weight", "organism"]},
            {"label": "Gene", "properties": ["id", "name", "chromosome", "start_position", "end_position"]},
            {"label": "Pathway", "properties": ["id", "name", "category", "source_database"]},
            {"label": "Disease", "properties": ["id", "name", "omim_id", "category"]},
            {"label": "Drug", "properties": ["id", "name", "drugbank_id", "mechanism", "approval_status"]}
        ]
        
        relationships = [
            {"type": "INTERACTS_WITH", "source": "Protein", "target": "Protein", "properties": ["interaction_type", "confidence_score", "detection_method"]},
            {"type": "ENCODED_BY", "source": "Protein", "target": "Gene", "properties": []},
            {"type": "PARTICIPATES_IN", "source": "Protein", "target": "Pathway", "properties": ["role"]},
            {"type": "ASSOCIATED_WITH", "source": "Protein", "target": "Disease", "properties": ["association_type", "evidence_level"]},
            {"type": "TARGETS", "source": "Drug", "target": "Protein", "properties": ["binding_affinity", "action"]},
            {"type": "TREATS", "source": "Drug", "target": "Disease", "properties": ["efficacy", "phase"]}
        ]
        
        # Sample data for demonstration
        sample_data = {
            "Protein": pd.DataFrame({
                "id": ["P001", "P002", "P003", "P004", "P005"],
                "name": ["TP53", "EGFR", "TNF", "BRCA1", "APOE"],
                "uniprot_id": ["P04637", "P00533", "P01375", "P38398", "P02649"],
                "organism": ["Homo sapiens", "Homo sapiens", "Homo sapiens", "Homo sapiens", "Homo sapiens"]
            }),
            "Disease": pd.DataFrame({
                "id": ["D001", "D002", "D003", "D004"],
                "name": ["Lung Cancer", "Alzheimer's Disease", "Breast Cancer", "Diabetes Mellitus"],
                "category": ["Cancer", "Neurodegenerative", "Cancer", "Metabolic"]
            }),
            "Drug": pd.DataFrame({
                "id": ["DR001", "DR002", "DR003"],
                "name": ["Gefitinib", "Donepezil", "Tamoxifen"],
                "mechanism": ["EGFR inhibitor", "Acetylcholinesterase inhibitor", "Estrogen receptor modulator"],
                "approval_status": ["Approved", "Approved", "Approved"]
            })
        }
    
    else:  # Custom Data Model
        st.subheader("Define Custom Data Model")
        
        # Allow users to define their own nodes
        st.write("Define Node Types:")
        custom_nodes = []
        
        num_node_types = st.number_input("Number of node types:", min_value=1, max_value=10, value=2)
        
        for i in range(num_node_types):
            col1, col2 = st.columns(2)
            with col1:
                node_label = st.text_input(f"Node {i+1} Label:", value=f"Node{i+1}")
            
            with col2:
                node_props = st.text_input(f"Node {i+1} Properties (comma-separated):", value="id,name")
                node_properties = [prop.strip() for prop in node_props.split(",")]
            
            custom_nodes.append({"label": node_label, "properties": node_properties})
        
        # Allow users to define their own relationships
        st.write("Define Relationships:")
        custom_relationships = []
        
        num_relationship_types = st.number_input("Number of relationship types:", min_value=0, max_value=10, value=1)
        
        for i in range(num_relationship_types):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rel_type = st.text_input(f"Relationship {i+1} Type:", value=f"RELATES_TO_{i+1}")
            
            with col2:
                source_options = [node["label"] for node in custom_nodes]
                source_node = st.selectbox(f"Source Node {i+1}:", source_options, key=f"source_{i}")
            
            with col3:
                target_options = [node["label"] for node in custom_nodes]
                target_node = st.selectbox(f"Target Node {i+1}:", target_options, key=f"target_{i}")
            
            rel_props = st.text_input(f"Relationship {i+1} Properties (comma-separated):", value="since")
            rel_properties = [prop.strip() for prop in rel_props.split(",") if prop.strip()]
            
            custom_relationships.append({
                "type": rel_type,
                "source": source_node,
                "target": target_node,
                "properties": rel_properties
            })
        
        nodes = custom_nodes
        relationships = custom_relationships
        
        # Create sample data for the custom model
        sample_data = {}
        for node in nodes:
            # Generate sample data for each node type
            num_samples = 3
            sample_df = pd.DataFrame()
            
            for prop in node["properties"]:
                if prop.lower() == "id":
                    sample_df[prop] = [f"{node['label'][0]}{i:03d}" for i in range(1, num_samples+1)]
                elif prop.lower() == "name":
                    sample_df[prop] = [f"{node['label']} {i}" for i in range(1, num_samples+1)]
                else:
                    # Generate random data based on property name
                    if "date" in prop.lower():
                        sample_df[prop] = pd.date_range(start='1/1/2023', periods=num_samples).strftime('%Y-%m-%d')
                    elif any(num_type in prop.lower() for num_type in ["count", "number", "amount", "quantity", "id"]):
                        sample_df[prop] = np.random.randint(1, 100, num_samples)
                    else:
                        sample_df[prop] = [f"{prop.capitalize()} {i}" for i in range(1, num_samples+1)]
            
            sample_data[node["label"]] = sample_df
    
    # Display the data model
    st.subheader("Data Model Visualization")
    
    # Create a simple visualization of the data model
    dot_code = "digraph G {\n"
    dot_code += "  rankdir=LR;\n"
    dot_code += "  node [shape=box, style=filled, fillcolor=lightblue];\n"
    
    # Add nodes
    for node in nodes:
        props_str = "\\n".join(node["properties"])
        dot_code += f'  {node["label"]} [label="{node["label"]}\\n\\n{props_str}"];\n'
    
    # Add relationships
    for rel in relationships:
        dot_code += f'  {rel["source"]} -> {rel["target"]} [label="{rel["type"]}", fontsize=10];\n'
    
    dot_code += "}"
    
    # Display the graph using mermaid
    mermaid_code = "graph LR\n"
    
    # Add nodes
    for node in nodes:
        props_str = "<br>".join(node["properties"])
        mermaid_code += f'  {node["label"]}["{node["label"]}<br><br>{props_str}"]\n'
    
    # Add relationships
    for rel in relationships:
        mermaid_code += f'  {rel["source"]} -- "{rel["type"]}" --> {rel["target"]}\n'
    
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    # Display sample data
    with st.expander("View Sample Data"):
        for node_label, df in sample_data.items():
            st.subheader(f"{node_label} Data")
            st.dataframe(df)
    
    # Step 2: Select node types and relationships
    st.header("Step 2: Select Node Types and Relationships")
    
    # Select starting node
    start_node = st.selectbox("Select starting node type:", [node["label"] for node in nodes])
    
    # Find available relationships for the starting node
    available_rels = [rel for rel in relationships if rel["source"] == start_node]
    
    # Build the query path
    query_path = [{"node": start_node, "alias": "n0"}]
    
    max_path_length = 3
    for i in range(max_path_length):
        if not available_rels:
            break
        
        with st.expander(f"Add relationship {i+1}"):
            # Select relationship
            rel_options = [f"{rel['type']} -> {rel['target']}" for rel in available_rels]
            rel_options.insert(0, "None")
            
            selected_rel = st.selectbox(f"Select relationship {i+1}:", rel_options, key=f"rel_{i}")
            
            if selected_rel != "None":
                rel_type, target = selected_rel.split(" -> ")
                
                # Add to query path
                rel_alias = f"r{i}"
                target_alias = f"n{i+1}"
                
                query_path.append({
                    "relationship": rel_type,
                    "rel_alias": rel_alias,
                    "node": target,
                    "alias": target_alias
                })
                
                # Update available relationships for the next step
                available_rels = [rel for rel in relationships if rel["source"] == target]
            else:
                break
    
    # Step 3: Add filters and conditions
    st.header("Step 3: Add Filters and Conditions")
    
    filters = []
    
    for i, path_item in enumerate(query_path):
        node_label = path_item["node"]
        node_alias = path_item["alias"]
        
        # Find the node definition
        node_def = next((node for node in nodes if node["label"] == node_label), None)
        
        if node_def:
            with st.expander(f"Add filters for {node_label} ({node_alias})"):
                for prop in node_def["properties"]:
                    add_filter = st.checkbox(f"Filter by {prop}", key=f"filter_{node_alias}_{prop}")
                    
                    if add_filter:
                        # Determine appropriate filter UI based on property name
                        if prop.lower() in ["id", "name"]:
                            filter_value = st.text_input(f"Value for {prop}:", key=f"filter_value_{node_alias}_{prop}")
                            operator = "="
                            filters.append({
                                "node_alias": node_alias,
                                "property": prop,
                                "operator": operator,
                                "value": filter_value
                            })
                        elif any(num_type in prop.lower() for num_type in ["age", "count", "number", "amount", "quantity", "index"]):
                            filter_type = st.selectbox(
                                f"Filter type for {prop}:",
                                ["Equal to", "Greater than", "Less than", "Between"],
                                key=f"filter_type_{node_alias}_{prop}"
                            )
                            
                            if filter_type == "Between":
                                min_val = st.number_input(f"Minimum {prop}:", key=f"min_{node_alias}_{prop}")
                                max_val = st.number_input(f"Maximum {prop}:", value=100, key=f"max_{node_alias}_{prop}")
                                
                                filters.append({
                                    "node_alias": node_alias,
                                    "property": prop,
                                    "operator": ">=",
                                    "value": min_val
                                })
                                
                                filters.append({
                                    "node_alias": node_alias,
                                    "property": prop,
                                    "operator": "<=",
                                    "value": max_val
                                })
                            else:
                                operator_map = {
                                    "Equal to": "=",
                                    "Greater than": ">",
                                    "Less than": "<"
                                }
                                
                                filter_value = st.number_input(f"Value for {prop}:", key=f"filter_value_{node_alias}_{prop}")
                                
                                filters.append({
                                    "node_alias": node_alias,
                                    "property": prop,
                                    "operator": operator_map[filter_type],
                                    "value": filter_value
                                })
                        else:
                            filter_value = st.text_input(f"Value for {prop}:", key=f"filter_value_{node_alias}_{prop}")
                            operator = "="
                            filters.append({
                                "node_alias": node_alias,
                                "property": prop,
                                "operator": operator,
                                "value": filter_value
                            })
        
        # Add relationship filters if this is a relationship
        if i > 0 and "relationship" in path_item:
            rel_type = path_item["relationship"]
            rel_alias = path_item["rel_alias"]
            
            # Find the relationship definition
            rel_def = next((rel for rel in relationships if rel["type"] == rel_type), None)
            
            if rel_def and rel_def["properties"]:
                with st.expander(f"Add filters for {rel_type} relationship ({rel_alias})"):
                    for prop in rel_def["properties"]:
                        add_filter = st.checkbox(f"Filter by {prop}", key=f"filter_{rel_alias}_{prop}")
                        
                        if add_filter:
                            filter_value = st.text_input(f"Value for {prop}:", key=f"filter_value_{rel_alias}_{prop}")
                            operator = "="
                            filters.append({
                                "node_alias": rel_alias,
                                "property": prop,
                                "operator": operator,
                                "value": filter_value
                            })
    
    # Step 4: Specify return values
    st.header("Step 4: Specify Return Values")
    
    return_values = []
    
    for path_item in query_path:
        node_label = path_item["node"]
        node_alias = path_item["alias"]
        
        # Find the node definition
        node_def = next((node for node in nodes if node["label"] == node_label), None)
        
        if node_def:
            with st.expander(f"Return values from {node_label} ({node_alias})"):
                return_node = st.checkbox(f"Return entire {node_label} node", key=f"return_{node_alias}")
                
                if return_node:
                    return_values.append({
                        "alias": node_alias,
                        "property": None
                    })
                
                for prop in node_def["properties"]:
                    return_prop = st.checkbox(f"Return {prop}", key=f"return_{node_alias}_{prop}")
                    
                    if return_prop:
                        return_values.append({
                            "alias": node_alias,
                            "property": prop
                        })
        
        # Add relationship return options if this is a relationship
        if "relationship" in path_item:
            rel_type = path_item["relationship"]
            rel_alias = path_item["rel_alias"]
            
            # Find the relationship definition
            rel_def = next((rel for rel in relationships if rel["type"] == rel_type), None)
            
            if rel_def:
                with st.expander(f"Return values from {rel_type} relationship ({rel_alias})"):
                    return_rel = st.checkbox(f"Return entire {rel_type} relationship", key=f"return_{rel_alias}")
                    
                    if return_rel:
                        return_values.append({
                            "alias": rel_alias,
                            "property": None
                        })
                    
                    for prop in rel_def["properties"]:
                        return_prop = st.checkbox(f"Return {prop}", key=f"return_{rel_alias}_{prop}")
                        
                        if return_prop:
                            return_values.append({
                                "alias": rel_alias,
                                "property": prop
                            })
    
    # Step 5: Execute and visualize results
    st.header("Step 5: Execute and Visualize Results")
    
    # Build the Cypher query
    cypher_query = "MATCH "
    
    # Add path pattern
    for i, path_item in enumerate(query_path):
        if i == 0:
            # First node
            cypher_query += f"({path_item['alias']}:{path_item['node']})"
        else:
            # Relationship and target node
            cypher_query += f"-[{path_item['rel_alias']}:{path_item['relationship']}]->({path_item['alias']}:{path_item['node']})"
    
    # Add WHERE clause if there are filters
    if filters:
        cypher_query += " WHERE "
        filter_conditions = []
        
        for i, filter_item in enumerate(filters):
            if isinstance(filter_item["value"], str) and not filter_item["value"].isdigit():
                # String value needs quotes
                filter_conditions.append(f"{filter_item['node_alias']}.{filter_item['property']} {filter_item['operator']} '{filter_item['value']}'")
            else:
                # Numeric value doesn't need quotes
                filter_conditions.append(f"{filter_item['node_alias']}.{filter_item['property']} {filter_item['operator']} {filter_item['value']}")
        
        cypher_query += " AND ".join(filter_conditions)
    
    # Add RETURN clause
    if return_values:
        cypher_query += " RETURN "
        return_items = []
        
        for return_item in return_values:
            if return_item["property"] is None:
                # Return entire node/relationship
                return_items.append(return_item["alias"])
            else:
                # Return specific property
                return_items.append(f"{return_item['alias']}.{return_item['property']}")
        
        cypher_query += ", ".join(return_items)
    else:
        # Default return if nothing selected
        cypher_query += f" RETURN {query_path[0]['alias']}"
    
    # Display the Cypher query
    st.subheader("Generated Cypher Query")
    st.code(cypher_query, language="cypher")
    
    # Execute button
    execute_query = st.button("Execute Query")
    
    if execute_query:
        st.subheader("Query Results")
        
        # In a real implementation, this would execute the query against Neo4j
        # For this demo, we'll simulate results based on the sample data
        
        # Simple query execution simulation
        try:
            # Extract the first node label and any filters on it
            start_node_label = query_path[0]["node"]
            start_node_alias = query_path[0]["alias"]
            
            # Get the sample data for this node
            if start_node_label in sample_data:
                result_df = sample_data[start_node_label].copy()
                
                # Apply filters
                for filter_item in filters:
                    if filter_item["node_alias"] == start_node_alias:
                        prop = filter_item["property"]
                        op = filter_item["operator"]
                        val = filter_item["value"]
                        
                        if op == "=":
                            if isinstance(val, str) and not val.isdigit():
                                result_df = result_df[result_df[prop] == val]
                            else:
                                result_df = result_df[result_df[prop] == float(val)]
                        elif op == ">":
                            result_df = result_df[result_df[prop] > float(val)]
                        elif op == "<":
                            result_df = result_df[result_df[prop] < float(val)]
                        elif op == ">=":
                            result_df = result_df[result_df[prop] >= float(val)]
                        elif op == "<=":
                            result_df = result_df[result_df[prop] <= float(val)]
                
                # If there are relationships in the query, we need to join with other node data
                if len(query_path) > 1:
                    st.info("This demo simulates query execution on a single node type only. In a real Neo4j database, the query would traverse the graph according to the specified relationships.")
                
                # Select only the requested return columns
                if return_values:
                    # Extract property names for the start node
                    return_props = [item["property"] for item in return_values 
                                   if item["alias"] == start_node_alias and item["property"] is not None]
                    
                    if return_props:
                        result_df = result_df[return_props]
                
                # Display results
                st.dataframe(result_df)
                st.success(f"Query returned {len(result_df)} results.")
            else:
                st.error(f"No sample data available for node type {start_node_label}.")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    # Conclusion
    st.header("Conclusion")
    st.markdown(\"\"\"
    This interactive demo has shown you how to:
    
    1. Define and visualize a graph data model
    2. Build a Cypher query using a visual interface
    3. Add filters and conditions to your query
    4. Specify which data to return
    5. Execute the query and view results
    
    These skills are essential for working with graph databases in scientific research.
    
    To learn more, check out the following resources:
    - [Database Operations Tutorial](http://localhost:8888/lab/tree/tutorials/database_operations_tutorial.ipynb)
    - [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
    - [Neo4j Browser](http://localhost:7474)
    \"\"\")
    
    # Return any results or state if needed
    return {"status": "completed", "query": cypher_query}

if __name__ == "__main__":
    run_demo()
"""
                },
                {
                    "id": "analysis_pipeline",
                    "title": "Analysis Pipeline Demo",
                    "filename": "analysis_pipeline_demo.py",
                    "content": "# Placeholder for Analysis Pipeline Demo"
                },
                {
                    "id": "dashboard_creator",
                    "title": "Dashboard Creator Demo",
                    "filename": "dashboard_creator_demo.py",
                    "content": "# Placeholder for Dashboard Creator Demo"
                }
            ]
            
            # Create the demo files
            for demo in demo_files:
                demo_path = demos_dir / demo["filename"]
                with open(demo_path, "w") as f:
                    f.write(demo["content"])
                
                # Create metadata file
                metadata = {
                    "title": demo["title"],
                    "description": f"Interactive demo for {demo['title'].lower().replace(' demo', '')} in the Science Data Kit.",
                    "id": demo["id"],
                    "categories": ["interactive", "demo", demo["id"].replace("_", " ")],
                    "difficulty": "Intermediate",
                    "estimated_time": "15-20 minutes",
                    "requirements": ["streamlit", "pandas", "matplotlib", "seaborn"],
                    "author": "Science Data Kit Team",
                    "version": "1.0.0",
                    "last_updated": "2023-07-24",
                    "status": "Active"
                }
                
                metadata_path = metadata_dir / f"{demo['id']}_metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
            
            # Return the sample metadata
            demos = []
            for demo in demo_files:
                demos.append({
                    "demo_id": demo["id"],
                    "title": demo["title"],
                    "description": f"Interactive demo for {demo['title'].lower().replace(' demo', '')} in the Science Data Kit.",
                    "categories": ["interactive", "demo", demo["id"].replace("_", " ")],
                    "difficulty": "Intermediate",
                    "estimated_time": "15-20 minutes",
                    "status": "Active"
                })
            
            return demos
        
        # Load metadata files
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    
                    # Add the filename (without extension) as the demo_id if not present
                    if "demo_id" not in metadata:
                        metadata["demo_id"] = metadata_file.stem.replace("_metadata", "")
                    
                    demos.append(metadata)
            except Exception as e:
                st.warning(f"Error loading demo metadata from {metadata_file}: {e}")
        
        # Sort demos by title
        demos.sort(key=lambda x: x.get("title", ""))
        
        return demos
    
    def get_all_demos(self) -> List[Dict[str, Any]]:
        """
        Get all available interactive demos.
        
        Returns:
            A list of dictionaries containing demo metadata.
        """
        return self.demos
    
    def get_demo_by_id(self, demo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific demo by ID.
        
        Args:
            demo_id: The ID of the demo to retrieve.
            
        Returns:
            A dictionary containing the demo metadata, or None if not found.
        """
        for demo in self.demos:
            if demo.get("demo_id") == demo_id:
                return demo
        return None
    
    def get_demos_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get demos by category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            A list of dictionaries containing demo metadata for the specified category.
        """
        return [demo for demo in self.demos if category in demo.get("categories", [])]
    
    def get_demo_module(self, demo_id: str) -> Optional[Any]:
        """
        Get the Python module for a specific demo.
        
        Args:
            demo_id: The ID of the demo to retrieve.
            
        Returns:
            The demo module, or None if not found.
        """
        demo = self.get_demo_by_id(demo_id)
        if not demo:
            return None
        
        # Path to the demo file
        demo_file = Path(__file__).parent.parent.parent.parent / "interactive_demos" / "demos" / f"{demo_id}_demo.py"
        
        if not demo_file.exists():
            return None
        
        try:
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(f"{demo_id}_demo", demo_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            st.error(f"Error loading demo module: {e}")
            return None

# Create a singleton instance of the interactive demos
_interactive_demos = None

def get_interactive_demos() -> InteractiveDemos:
    """
    Get the singleton instance of the interactive demos.
    
    Returns:
        The InteractiveDemos instance.
    """
    global _interactive_demos
    if _interactive_demos is None:
        _interactive_demos = InteractiveDemos()
    return _interactive_demos

def run_interactive_demo(demo_id: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Run a specific interactive demo.
    
    Args:
        demo_id: The ID of the demo to run.
        params: Optional parameters for the demo.
        
    Returns:
        The result of running the demo, or None if the demo could not be run.
    """
    demos = get_interactive_demos()
    demo = demos.get_demo_by_id(demo_id)
    
    if not demo:
        st.warning(f"Demo not found: {demo_id}")
        return None
    
    module = demos.get_demo_module(demo_id)
    if not module:
        st.error(f"Could not load demo module for {demo_id}")
        return None
    
    try:
        # Run the demo
        if hasattr(module, "run_demo"):
            return module.run_demo(params)
        else:
            st.error(f"Demo module {demo_id} does not have a run_demo function")
            return None
    except Exception as e:
        st.error(f"Error running demo: {e}")
        return None

def display_interactive_demo_info(demo_id: str) -> None:
    """
    Display information about a specific interactive demo.
    
    Args:
        demo_id: The ID of the demo to display.
    """
    demos = get_interactive_demos()
    demo = demos.get_demo_by_id(demo_id)
    
    if not demo:
        st.warning(f"Demo not found: {demo_id}")
        return
    
    st.header(demo.get("title", "Untitled Demo"))
    
    # Display demo description
    st.markdown(demo.get("description", "No description available."))
    
    # Display demo metadata
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Difficulty:** {demo.get('difficulty', 'Not specified')}")
        st.markdown(f"**Categories:** {', '.join(demo.get('categories', []))}")
    
    with col2:
        st.markdown(f"**Estimated Time:** {demo.get('estimated_time', 'Not specified')}")
        st.markdown(f"**Status:** {demo.get('status', 'Not specified')}")
    
    # Display demo requirements if available
    if "requirements" in demo:
        st.markdown("**Requirements:**")
        for req in demo["requirements"]:
            st.markdown(f"- {req}")
    
    # Run demo button
    if st.button("Run This Demo", key=f"run_demo_{demo_id}"):
        st.session_state[f"running_demo_{demo_id}"] = True
    
    # If the demo is running, display it
    if st.session_state.get(f"running_demo_{demo_id}", False):
        st.markdown("---")
        run_interactive_demo(demo_id)

def display_interactive_demos_section() -> None:
    """
    Display the interactive demos section on the workshop page.
    
    This function creates a Streamlit UI for browsing and running interactive demos.
    """
    st.header("Interactive Demos")
    
    demos = get_interactive_demos()
    all_demos = demos.get_all_demos()
    
    if not all_demos:
        st.info("No interactive demos available yet. Check back soon!")
        return
    
    st.markdown("""
    These interactive demos provide hands-on experience with key features and workflows in the Science Data Kit.
    Select a demo from the list below to learn more and try it out.
    """)
    
    # Create a selectbox for choosing a demo
    demo_options = [demo.get("title", "Untitled Demo") for demo in all_demos]
    selected_demo_title = st.selectbox("Select a Demo", demo_options, key="interactive_demo_selectbox")
    
    # Find the selected demo
    selected_demo = next((demo for demo in all_demos 
                         if demo.get("title") == selected_demo_title), None)
    
    if selected_demo:
        # Display the selected demo
        display_interactive_demo_info(selected_demo.get("demo_id"))