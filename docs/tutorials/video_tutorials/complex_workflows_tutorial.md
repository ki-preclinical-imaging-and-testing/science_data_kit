# Science Data Kit: Complex Workflows Video Tutorial Script

## Introduction

Welcome to this video tutorial on using the Science Data Kit (SDK) for complex scientific data analysis workflows. In this tutorial, we'll demonstrate how to use multiple components of the SDK together to solve real-world scientific data analysis problems.

## Prerequisites

Before starting this tutorial, make sure you have:

1. Installed the Science Data Kit (see INSTALL.md for instructions)
2. Set up a Neo4j database (either locally or using Docker)
3. Basic familiarity with Python and data analysis concepts

## Tutorial Overview

This tutorial will cover:

1. Setting up a scientific data analysis project
2. Loading and preprocessing data
3. Exploratory data analysis
4. Building predictive models
5. Visualizing results
6. Storing results in Neo4j
7. Creating reproducible workflows

## Part 1: Setting Up a Project (0:00 - 5:00)

### Creating a Session

First, let's create a session to track our analysis:

```python
from science_data_kit.core.session.session import create_session

# Create a session
session = create_session(
    name="Clinical Trial Analysis",
    description="Analysis of clinical trial data for drug efficacy and safety"
)

# Print session information
print(f"Session ID: {session.session_id}")
print(f"Session name: {session.config.name}")
print(f"Session description: {session.config.description}")
```

### Connecting to Neo4j

Next, let's connect to our Neo4j database:

```python
from science_data_kit.core.db.db_manager import DBManager

# Create a database manager
db_manager = DBManager()

# Check if connected
if db_manager.is_connected():
    print("Connected to Neo4j database")
else:
    print("Not connected to Neo4j database")
```

## Part 2: Loading and Preprocessing Data (5:00 - 10:00)

### Loading Data

Let's load our clinical trial data:

```python
import pandas as pd

# Load data
data_path = "path/to/clinical_trial_data.csv"
clinical_data = pd.read_csv(data_path)

# Display the first few rows
print(clinical_data.head())

# Get basic information about the dataset
print(clinical_data.info())
print(clinical_data.describe())
```

### Preprocessing Data

Now, let's preprocess the data:

```python
# Handle missing values
clinical_data['age'].fillna(clinical_data['age'].median(), inplace=True)
clinical_data['bmi'].fillna(clinical_data['bmi'].median(), inplace=True)

# Convert categorical variables to dummy variables
if 'treatment_group' in clinical_data.columns:
    clinical_data = pd.get_dummies(clinical_data, columns=['treatment_group'], drop_first=True)

if 'sex' in clinical_data.columns:
    clinical_data['sex'] = clinical_data['sex'].map({'M': 1, 'F': 0})

# Display the preprocessed data
print(clinical_data.head())
```

## Part 3: Exploratory Data Analysis (10:00 - 15:00)

### Basic Statistics

Let's calculate some basic statistics:

```python
# Basic statistics
summary_stats = clinical_data.describe()
print(summary_stats)

# Check for correlations
correlation_matrix = clinical_data.select_dtypes(include=[np.number]).corr()
print(correlation_matrix)
```

### Visualizing Data

Let's create some visualizations:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the figure
plt.figure(figsize=(12, 10))

# Create a heatmap of the correlation matrix
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()

# Create a boxplot of a key variable by treatment group
if 'treatment_group_B' in clinical_data.columns and 'primary_endpoint' in clinical_data.columns:
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='treatment_group_B', y='primary_endpoint', data=clinical_data)
    plt.title('Primary Endpoint by Treatment Group')
    plt.xlabel('Treatment Group B')
    plt.ylabel('Primary Endpoint')
    plt.show()
```

## Part 4: Building Predictive Models (15:00 - 25:00)

### Preparing Data for Modeling

Let's prepare our data for modeling:

```python
from science_data_kit.core.analysis.sklearn_integration import prepare_data

# Assume we want to predict a binary outcome (e.g., response to treatment)
if 'response' in clinical_data.columns:
    # Prepare data
    X = clinical_data.drop(['patient_id', 'response', 'survival_time', 'event'], axis=1, errors='ignore')
    y = clinical_data['response']
    
    # Split data
    X_train, X_test, y_train, y_test = prepare_data(
        pd.DataFrame(X), 'response', test_size=0.3, random_state=42
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Testing set size: {len(X_test)}")
```

### Training a Model

Now, let's train a model:

```python
from science_data_kit.core.utils.model_training import train_model
from sklearn.ensemble import RandomForestClassifier

# Train a random forest model
model, results = train_model(
    RandomForestClassifier(n_estimators=100, random_state=42),
    X_train,
    y_train,
    model_type='sklearn',
    cross_validate=True,
    cv=5,
    scoring=['accuracy', 'precision', 'recall', 'f1']
)

# Print cross-validation results
print("Cross-validation results:")
for metric, values in results.items():
    if isinstance(values, list):
        print(f"{metric}: {sum(values)/len(values):.3f}")
```

### Evaluating the Model

Let's evaluate our model on the test set:

```python
from science_data_kit.core.analysis.sklearn_integration import evaluate_model

# Evaluate on test set
test_metrics = evaluate_model(model, X_test, y_test)

# Print test metrics
print("Test metrics:")
for metric, value in test_metrics.items():
    print(f"{metric}: {value:.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 features:")
print(feature_importance.head(10))
```

### Saving the Model

Let's save our model:

```python
from science_data_kit.core.analysis.sklearn_integration import save_model
import os

# Save the model
model_path = os.path.join(os.path.dirname(data_path), 'clinical_response_model.pkl')
success, message = save_model(model, model_path)

if success:
    print(f"Model saved successfully: {message}")
else:
    print(f"Failed to save model: {message}")
```

## Part 5: Visualizing Results (25:00 - 30:00)

### Creating Visualizations

Let's create some visualizations of our results:

```python
# Plot feature importance
plt.figure(figsize=(10, 6))

# Get top 10 features
top_features = feature_importance.head(10)

plt.barh(top_features['feature'], top_features['importance'])
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Top 10 Features for Predicting Treatment Response')
plt.tight_layout()
plt.show()

# Create a confusion matrix
from sklearn.metrics import confusion_matrix
import numpy as np

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()
```

## Part 6: Storing Results in Neo4j (30:00 - 35:00)

### Storing Model Results

Let's store our model results in Neo4j:

```python
# Create a transaction
with db_manager.transaction() as tx:
    # Create a study node
    study_query = """
    CREATE (s:Study {id: $study_id, name: $study_name, description: $study_description})
    RETURN s
    """
    study_params = {
        'study_id': f"STUDY_{session.session_id}",
        'study_name': session.config.name,
        'study_description': session.config.description
    }
    tx.run(study_query, study_params)
    
    # Create a model node
    model_query = """
    MATCH (s:Study {id: $study_id})
    CREATE (m:Model {
        type: $model_type,
        accuracy: $accuracy,
        precision: $precision,
        recall: $recall,
        f1: $f1,
        model_path: $model_path
    })
    CREATE (s)-[r:HAS_MODEL]->(m)
    RETURN m
    """
    model_params = {
        'study_id': f"STUDY_{session.session_id}",
        'model_type': 'RandomForest',
        'accuracy': float(test_metrics.get('accuracy', 0)),
        'precision': float(test_metrics.get('precision', 0)),
        'recall': float(test_metrics.get('recall', 0)),
        'f1': float(test_metrics.get('f1', 0)),
        'model_path': model_path
    }
    tx.run(model_query, model_params)
    
    # Store top features
    for _, feature in top_features.iterrows():
        feature_query = """
        MATCH (m:Model)
        WHERE m.model_path = $model_path
        CREATE (f:Feature {name: $feature_name, importance: $importance})
        CREATE (m)-[r:HAS_IMPORTANT_FEATURE]->(f)
        RETURN f
        """
        feature_params = {
            'model_path': model_path,
            'feature_name': feature['feature'],
            'importance': float(feature['importance'])
        }
        tx.run(feature_query, feature_params)
```

### Saving Session Metadata

Let's save our analysis results to the session:

```python
# Save analysis results to the session
session.add_metadata({
    'num_patients': len(clinical_data),
    'model_accuracy': test_metrics.get('accuracy', None),
    'model_path': model_path,
    'top_features': top_features['feature'].tolist()
})

# Save the session
session.save()

print(f"Session saved with ID: {session.session_id}")
```

## Part 7: Creating Reproducible Workflows (35:00 - 40:00)

### Loading a Session

Let's see how to load a session:

```python
from science_data_kit.core.session.session import load_session

# Load the session
loaded_session = load_session(session.session_file)

# Print session information
print(f"Loaded session ID: {loaded_session.session_id}")
print(f"Loaded session name: {loaded_session.config.name}")
print(f"Loaded session metadata: {loaded_session.metadata}")
```

### Loading a Model

Let's see how to load a model:

```python
from science_data_kit.core.analysis.sklearn_integration import load_model

# Load the model
success, loaded_model = load_model(model_path)

if success:
    print("Model loaded successfully")
    
    # Make predictions with the loaded model
    new_predictions = loaded_model.predict(X_test[:5])
    print(f"Predictions for first 5 test samples: {new_predictions}")
else:
    print(f"Failed to load model: {loaded_model}")
```

## Conclusion (40:00 - 45:00)

In this tutorial, we've demonstrated how to use the Science Data Kit for complex scientific data analysis workflows. We've covered:

1. Setting up a project with sessions and database connections
2. Loading and preprocessing data
3. Exploratory data analysis
4. Building and evaluating predictive models
5. Visualizing results
6. Storing results in Neo4j
7. Creating reproducible workflows

The Science Data Kit provides a comprehensive framework for scientific data analysis, making it easier to create reproducible, well-documented workflows for your research.

## Next Steps

To learn more about the Science Data Kit, check out:

1. The documentation at [docs/index.md](../../index.md)
2. Example workflows in [science_data_kit/core/examples/scientific_workflows.py](../../../science_data_kit/core/examples/scientific_workflows.py)
3. Additional tutorials in the [docs/tutorials](../../tutorials) directory

Thank you for watching this tutorial!