# Science Data Kit (SDK) Hands-On Exercises

This document contains detailed hands-on exercises for the Science Data Kit workshop. These exercises are designed to help users learn how to use the SDK effectively through practical, step-by-step instructions.

## Prerequisites

Before starting these exercises, ensure you have:

1. Science Data Kit installed (`pip install science-data-kit`)
2. Basic knowledge of Python
3. Sample datasets downloaded (available in the `science_data_kit/data/samples/` directory)

## Exercise 1: Data Import and Exploration

### Objective
Learn how to import data from various sources, explore its structure, and perform basic preprocessing.

### Steps

#### 1.1 Import a Dataset

```python
import science_data_kit as sdk
import pandas as pd

# Import from CSV
data_csv = sdk.load_dataset("preclinical_sample.csv")

# Import from Excel
data_excel = sdk.load_dataset("clinical_trial_data.xlsx")

# Import from database
connection_string = "sqlite:///sample_database.db"
data_db = sdk.load_from_database(connection_string, "patient_records")

# Print basic information
print(f"CSV data shape: {data_csv.shape}")
print(f"Excel data shape: {data_excel.shape}")
print(f"Database data shape: {data_db.shape}")
```

#### 1.2 Explore Data Structure

```python
# Basic statistics
print(data_csv.describe())

# Column information
print(data_csv.info())

# Check for missing values
print(f"Missing values:\n{data_csv.isnull().sum()}")

# View first few rows
print(data_csv.head())

# Use SDK's data explorer
sdk.explore(data_csv)
```

#### 1.3 Clean and Preprocess Data

```python
# Handle missing values
data_clean = sdk.preprocess.handle_missing(data_csv, method="mean")

# Remove outliers
data_clean = sdk.preprocess.remove_outliers(data_clean, method="iqr")

# Normalize numerical features
data_clean = sdk.preprocess.normalize(data_clean, columns=["age", "weight", "dosage"])

# Encode categorical variables
data_clean = sdk.preprocess.encode_categorical(data_clean, columns=["gender", "treatment_group"])

# Verify changes
print(f"Original data shape: {data_csv.shape}")
print(f"Cleaned data shape: {data_clean.shape}")
print(data_clean.head())
```

#### 1.4 Save Processed Dataset

```python
# Save to CSV
sdk.save_dataset(data_clean, "processed_preclinical_data.csv")

# Save to Excel
sdk.save_dataset(data_clean, "processed_preclinical_data.xlsx")

# Save to database
sdk.save_to_database(data_clean, connection_string, "processed_patient_records")
```

### Exercise 1 Challenge
Import a dataset of your choice, identify and handle at least three data quality issues, and save the processed dataset in two different formats.

## Exercise 2: Data Analysis

### Objective
Learn how to perform statistical analysis and apply machine learning algorithms to scientific data.

### Steps

#### 2.1 Basic Statistical Analysis

```python
import science_data_kit as sdk

# Load processed data
data = sdk.load_dataset("processed_preclinical_data.csv")

# Descriptive statistics
stats = sdk.analyze.descriptive_stats(data)
print(stats)

# Correlation analysis
corr = sdk.analyze.correlation(data, method="pearson")
sdk.visualize.heatmap(corr, title="Feature Correlation")

# Group comparison
group_stats = sdk.analyze.group_comparison(
    data, 
    group_column="treatment_group", 
    value_column="response"
)
print(group_stats)

# Hypothesis testing
t_test = sdk.analyze.t_test(
    data, 
    group_column="treatment_group", 
    value_column="response"
)
print(f"T-test results: p-value = {t_test.pvalue:.4f}")
```

#### 2.2 Machine Learning Analysis

```python
# Prepare data for machine learning
X, y = sdk.ml.prepare_data(
    data, 
    target="response", 
    features=["age", "weight", "dosage", "gender_encoded", "treatment_group_encoded"]
)

# Split data
X_train, X_test, y_train, y_test = sdk.ml.train_test_split(X, y, test_size=0.2)

# Train a model
model = sdk.ml.train_model(X_train, y_train, model_type="random_forest")

# Evaluate the model
evaluation = sdk.ml.evaluate_model(model, X_test, y_test)
print(f"Model accuracy: {evaluation['accuracy']:.2f}")
print(f"Model F1 score: {evaluation['f1_score']:.2f}")

# Feature importance
importance = sdk.ml.feature_importance(model, X.columns)
sdk.visualize.bar_chart(
    importance, 
    x_label="Feature", 
    y_label="Importance", 
    title="Feature Importance"
)
```

#### 2.3 Time Series Analysis

```python
# Load time series data
time_data = sdk.load_dataset("time_series_sample.csv")

# Decompose time series
decomposition = sdk.analyze.time_series_decomposition(
    time_data, 
    date_column="date", 
    value_column="measurement"
)
sdk.visualize.time_series_components(decomposition)

# Trend analysis
trend = sdk.analyze.trend_analysis(
    time_data, 
    date_column="date", 
    value_column="measurement"
)
print(f"Trend coefficient: {trend['coefficient']:.4f}")
print(f"p-value: {trend['p_value']:.4f}")

# Forecasting
forecast = sdk.analyze.forecast(
    time_data, 
    date_column="date", 
    value_column="measurement", 
    periods=30
)
sdk.visualize.time_series_forecast(
    time_data, 
    forecast, 
    date_column="date", 
    value_column="measurement"
)
```

### Exercise 2 Challenge
Perform a complete analysis workflow on a dataset: descriptive statistics, correlation analysis, at least one hypothesis test, and train a machine learning model with at least 75% accuracy.

## Exercise 3: Data Visualization

### Objective
Learn how to create effective visualizations for scientific data using the SDK's visualization capabilities.

### Steps

#### 3.1 Basic Charts

```python
import science_data_kit as sdk

# Load data
data = sdk.load_dataset("processed_preclinical_data.csv")

# Bar chart
sdk.visualize.bar_chart(
    data, 
    x="treatment_group", 
    y="response", 
    title="Response by Treatment Group"
)

# Line chart
time_data = sdk.load_dataset("time_series_sample.csv")
sdk.visualize.line_chart(
    time_data, 
    x="date", 
    y="measurement", 
    title="Measurements Over Time"
)

# Scatter plot
sdk.visualize.scatter_plot(
    data, 
    x="dosage", 
    y="response", 
    color="treatment_group", 
    title="Response vs. Dosage by Treatment Group"
)

# Box plot
sdk.visualize.box_plot(
    data, 
    x="treatment_group", 
    y="response", 
    title="Response Distribution by Treatment Group"
)
```

#### 3.2 Interactive Dashboards

```python
# Create a dashboard
dashboard = sdk.visualize.create_dashboard(title="Preclinical Data Analysis")

# Add charts to dashboard
dashboard.add_chart(
    sdk.visualize.bar_chart(
        data, 
        x="treatment_group", 
        y="response", 
        title="Response by Treatment Group"
    )
)

dashboard.add_chart(
    sdk.visualize.scatter_plot(
        data, 
        x="dosage", 
        y="response", 
        color="treatment_group", 
        title="Response vs. Dosage"
    )
)

dashboard.add_chart(
    sdk.visualize.box_plot(
        data, 
        x="treatment_group", 
        y="response", 
        title="Response Distribution"
    )
)

# Add filters
dashboard.add_filter("treatment_group")
dashboard.add_filter("gender")

# Display dashboard
dashboard.display()
```

#### 3.3 Customizing Visualizations

```python
# Custom color scheme
colors = sdk.visualize.ColorScheme(
    primary="#1f77b4",
    secondary="#ff7f0e",
    accent="#2ca02c",
    background="#f5f5f5"
)

# Custom chart with advanced options
sdk.visualize.scatter_plot(
    data,
    x="dosage",
    y="response",
    color="treatment_group",
    size="weight",
    title="Response vs. Dosage by Treatment Group",
    x_label="Dosage (mg)",
    y_label="Treatment Response",
    color_scheme=colors,
    legend_title="Treatment Group",
    trend_line=True,
    annotations=[
        {"x": 25, "y": 75, "text": "Optimal Dosage Range"},
        {"x": 50, "y": 30, "text": "Diminishing Returns"}
    ]
)

# Custom theme
theme = sdk.visualize.Theme(
    font_family="Arial",
    title_font_size=18,
    axis_font_size=12,
    background_color="#ffffff",
    grid_style="dashed"
)

# Apply theme to visualization
sdk.visualize.set_theme(theme)
sdk.visualize.bar_chart(
    data, 
    x="treatment_group", 
    y="response", 
    title="Response by Treatment Group with Custom Theme"
)
```

#### 3.4 Exporting Visualizations

```python
# Create a visualization
chart = sdk.visualize.scatter_plot(
    data, 
    x="dosage", 
    y="response", 
    color="treatment_group", 
    title="Response vs. Dosage by Treatment Group"
)

# Export as PNG
sdk.visualize.export(chart, "dosage_response_chart.png")

# Export as SVG
sdk.visualize.export(chart, "dosage_response_chart.svg")

# Export as interactive HTML
sdk.visualize.export(chart, "dosage_response_chart.html", interactive=True)

# Export dashboard
sdk.visualize.export(dashboard, "preclinical_dashboard.html")
```

### Exercise 3 Challenge
Create a comprehensive dashboard with at least four different visualization types, custom styling, interactive filters, and export it in two different formats.

## Exercise 4: End-to-End Workflow

### Objective
Apply all the skills learned in previous exercises to complete an end-to-end data analysis workflow.

### Steps

#### 4.1 Import and Prepare Data

```python
import science_data_kit as sdk

# Import data
clinical_data = sdk.load_dataset("clinical_trial_full.csv")

# Explore data
sdk.explore(clinical_data)

# Preprocess data
clinical_clean = sdk.preprocess.handle_missing(clinical_data)
clinical_clean = sdk.preprocess.normalize(clinical_clean, numerical_columns=True)
clinical_clean = sdk.preprocess.encode_categorical(clinical_clean, categorical_columns=True)

# Split data for analysis
patient_data = clinical_clean[clinical_clean["visit_number"] == 1]
longitudinal_data = clinical_clean.sort_values(["patient_id", "visit_date"])
```

#### 4.2 Perform Analysis

```python
# Descriptive statistics by treatment group
group_stats = sdk.analyze.group_statistics(
    patient_data, 
    group_column="treatment_arm", 
    value_columns=["age", "weight", "baseline_measurement"]
)

# Efficacy analysis
efficacy = sdk.analyze.treatment_efficacy(
    longitudinal_data, 
    patient_id_column="patient_id",
    treatment_column="treatment_arm",
    outcome_column="primary_outcome",
    visit_column="visit_number"
)

# Safety analysis
safety = sdk.analyze.adverse_events(
    longitudinal_data,
    patient_id_column="patient_id",
    treatment_column="treatment_arm",
    adverse_event_column="adverse_events"
)

# Predictive modeling
X, y = sdk.ml.prepare_data(
    patient_data,
    target="response_at_week_12",
    exclude=["patient_id", "visit_date", "visit_number"]
)
model = sdk.ml.train_model(X, y, model_type="gradient_boosting")
importance = sdk.ml.feature_importance(model, X.columns)
```

#### 4.3 Create Visualizations

```python
# Create dashboard
clinical_dashboard = sdk.visualize.create_dashboard(title="Clinical Trial Analysis")

# Demographics visualization
clinical_dashboard.add_chart(
    sdk.visualize.demographic_summary(
        patient_data,
        group_column="treatment_arm"
    )
)

# Efficacy visualization
clinical_dashboard.add_chart(
    sdk.visualize.outcome_by_visit(
        longitudinal_data,
        outcome_column="primary_outcome",
        visit_column="visit_number",
        group_column="treatment_arm"
    )
)

# Safety visualization
clinical_dashboard.add_chart(
    sdk.visualize.adverse_event_summary(safety)
)

# Predictors visualization
clinical_dashboard.add_chart(
    sdk.visualize.bar_chart(
        importance,
        x_label="Feature",
        y_label="Importance",
        title="Predictors of 12-Week Response"
    )
)

# Display dashboard
clinical_dashboard.display()
```

#### 4.4 Generate Report

```python
# Create report
report = sdk.reporting.create_report(title="Clinical Trial Analysis Report")

# Add sections
report.add_section("Introduction", "Analysis of clinical trial data for Drug X.")
report.add_section("Methods", "Data was processed and analyzed using Science Data Kit.")

# Add results
report.add_section("Results", "Key findings from the analysis:")
report.add_subsection("Demographics", group_stats)
report.add_subsection("Efficacy", efficacy)
report.add_subsection("Safety", safety)
report.add_subsection("Predictive Factors", importance)

# Add visualizations
report.add_visualization(
    sdk.visualize.outcome_by_visit(
        longitudinal_data,
        outcome_column="primary_outcome",
        visit_column="visit_number",
        group_column="treatment_arm"
    ),
    caption="Figure 1: Primary Outcome by Visit and Treatment Arm"
)

# Add conclusion
report.add_section("Conclusion", "Drug X showed significant efficacy compared to placebo with an acceptable safety profile.")

# Generate report
report.generate("clinical_trial_report.html")
report.generate("clinical_trial_report.pdf")
```

### Exercise 4 Challenge
Complete an end-to-end analysis of a complex dataset, including data cleaning, at least three different types of analysis, a comprehensive dashboard with at least five visualizations, and a detailed report with findings and recommendations.

## Additional Resources

- [Science Data Kit Documentation](https://science-data-kit.readthedocs.io/)
- [Sample Datasets Repository](https://github.com/science-data-kit/sample-datasets)
- [Community Forum](https://community.science-data-kit.org/)

## Feedback

After completing these exercises, please fill out the feedback form to help us improve the workshop and the Science Data Kit.