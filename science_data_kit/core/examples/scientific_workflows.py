"""
Scientific Workflow Examples for Science Data Kit

This module provides examples of real-world scientific data analysis workflows
using the Science Data Kit. It demonstrates how to use multiple components of the SDK
together to solve common scientific data analysis tasks.

Examples include:
1. Genomic data analysis workflow
2. Clinical trial data analysis workflow
3. Environmental monitoring data analysis workflow
4. Preclinical research data analysis workflow
5. Materials science data analysis workflow
6. Pharmaceutical data analysis workflow
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple, Optional, Union

from science_data_kit.core.db.db_manager import DBManager
from science_data_kit.core.utils.model_training import train_model, SklearnModelTrainer
from science_data_kit.core.analysis.sklearn_integration import (
    prepare_data,
    evaluate_model,
    save_model,
    load_model,
    cross_validate
)
from science_data_kit.core.session.session import create_session, load_session
from science_data_kit.core.models.entity_schemas import Dataset, Entity, Relationship


def genomic_data_analysis_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for genomic data analysis.

    This workflow demonstrates:
    1. Loading genomic expression data
    2. Preprocessing and normalization
    3. Differential expression analysis
    4. Pathway enrichment analysis
    5. Visualization of results
    6. Storing results in Neo4j

    Args:
        data_path: Path to the genomic data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting genomic data analysis workflow...")

    # 1. Load genomic expression data
    print("Loading genomic data...")
    expression_data = pd.read_csv(data_path)

    # Create a session to track the analysis
    session = create_session(
        name="Genomic Analysis",
        description="Analysis of gene expression data"
    )

    # 2. Preprocessing and normalization
    print("Preprocessing and normalizing data...")
    # Log2 transform the data (common in genomic analysis)
    expression_data_log = np.log2(expression_data.select_dtypes(include=[np.number]) + 1)

    # Add back non-numeric columns
    for col in expression_data.select_dtypes(exclude=[np.number]).columns:
        expression_data_log[col] = expression_data[col]

    # 3. Differential expression analysis
    print("Performing differential expression analysis...")
    # For this example, we'll simulate differential expression analysis
    # In a real workflow, you would use libraries like limma, DESeq2, or edgeR

    # Assume we have two groups: control and treatment
    control_samples = expression_data_log.filter(regex='control').columns
    treatment_samples = expression_data_log.filter(regex='treatment').columns

    # Calculate mean expression for each group
    control_mean = expression_data_log[control_samples].mean(axis=1)
    treatment_mean = expression_data_log[treatment_samples].mean(axis=1)

    # Calculate log fold change
    log_fold_change = treatment_mean - control_mean

    # Simulate p-values
    np.random.seed(42)
    p_values = np.random.beta(0.3, 1, size=len(log_fold_change))

    # Create differential expression results
    diff_expr_results = pd.DataFrame({
        'gene_id': expression_data_log.index if expression_data_log.index.name == 'gene_id' else range(len(log_fold_change)),
        'log_fold_change': log_fold_change,
        'p_value': p_values,
        'adj_p_value': p_values * 1.5  # Simplified adjustment
    })

    # Filter for significantly differentially expressed genes
    significant_genes = diff_expr_results[diff_expr_results['adj_p_value'] < 0.05]

    # 4. Pathway enrichment analysis (simulated)
    print("Performing pathway enrichment analysis...")
    # In a real workflow, you would use libraries like clusterProfiler, enrichR, or GSEA

    # Simulate pathway enrichment results
    pathways = [
        {'pathway_id': 'GO:0006915', 'pathway_name': 'apoptotic process', 'p_value': 0.001, 'genes': ['CASP3', 'BAX', 'BCL2']},
        {'pathway_id': 'GO:0007165', 'pathway_name': 'signal transduction', 'p_value': 0.003, 'genes': ['MAPK1', 'MAPK3', 'AKT1']},
        {'pathway_id': 'GO:0006281', 'pathway_name': 'DNA repair', 'p_value': 0.008, 'genes': ['BRCA1', 'BRCA2', 'ATM']},
        {'pathway_id': 'GO:0006954', 'pathway_name': 'inflammatory response', 'p_value': 0.012, 'genes': ['IL6', 'TNF', 'IL1B']},
        {'pathway_id': 'GO:0007049', 'pathway_name': 'cell cycle', 'p_value': 0.015, 'genes': ['CDK1', 'CCNB1', 'CCND1']}
    ]

    # 5. Visualization of results
    print("Generating visualizations...")

    # Create a volcano plot (log fold change vs -log10 p-value)
    plt.figure(figsize=(10, 8))
    plt.scatter(
        diff_expr_results['log_fold_change'],
        -np.log10(diff_expr_results['p_value']),
        alpha=0.5
    )

    # Highlight significant genes
    plt.scatter(
        significant_genes['log_fold_change'],
        -np.log10(significant_genes['p_value']),
        color='red',
        alpha=0.7
    )

    plt.axhline(-np.log10(0.05), color='gray', linestyle='--')
    plt.axvline(-1, color='gray', linestyle='--')
    plt.axvline(1, color='gray', linestyle='--')

    plt.xlabel('Log2 Fold Change')
    plt.ylabel('-Log10 P-value')
    plt.title('Volcano Plot of Differential Expression')

    # Save the plot
    volcano_plot_path = os.path.join(os.path.dirname(data_path), 'volcano_plot.png')
    plt.savefig(volcano_plot_path)

    # 6. Store results in Neo4j
    print("Storing results in Neo4j...")
    db_manager = DBManager()

    # Create a transaction
    with db_manager.transaction() as tx:
        # Create nodes for significant genes
        for _, gene in significant_genes.iterrows():
            gene_id = gene['gene_id']
            query = """
            MERGE (g:Gene {id: $gene_id})
            SET g.log_fold_change = $log_fold_change,
                g.p_value = $p_value,
                g.adj_p_value = $adj_p_value
            RETURN g
            """
            params = {
                'gene_id': str(gene_id),
                'log_fold_change': float(gene['log_fold_change']),
                'p_value': float(gene['p_value']),
                'adj_p_value': float(gene['adj_p_value'])
            }
            tx.run(query, params)

        # Create nodes for pathways and relationships to genes
        for pathway in pathways:
            query = """
            MERGE (p:Pathway {id: $pathway_id})
            SET p.name = $pathway_name,
                p.p_value = $p_value
            RETURN p
            """
            params = {
                'pathway_id': pathway['pathway_id'],
                'pathway_name': pathway['pathway_name'],
                'p_value': pathway['p_value']
            }
            tx.run(query, params)

            # Create relationships between pathways and genes
            for gene in pathway['genes']:
                query = """
                MATCH (g:Gene {id: $gene_id})
                MATCH (p:Pathway {id: $pathway_id})
                MERGE (g)-[r:BELONGS_TO]->(p)
                RETURN r
                """
                params = {
                    'gene_id': gene,
                    'pathway_id': pathway['pathway_id']
                }
                tx.run(query, params)

    # Save analysis results to the session
    session.add_metadata({
        'num_genes': len(expression_data),
        'num_significant_genes': len(significant_genes),
        'num_pathways': len(pathways),
        'volcano_plot_path': volcano_plot_path
    })

    # Save the session
    session.save()

    print("Genomic data analysis workflow completed.")

    return {
        'expression_data': expression_data.head(),
        'diff_expr_results': diff_expr_results.head(10),
        'significant_genes': len(significant_genes),
        'enriched_pathways': pathways,
        'volcano_plot_path': volcano_plot_path,
        'session_id': session.session_id
    }


def clinical_trial_data_analysis_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for clinical trial data analysis.

    This workflow demonstrates:
    1. Loading clinical trial data
    2. Data cleaning and preprocessing
    3. Exploratory data analysis
    4. Statistical analysis (survival analysis, efficacy endpoints)
    5. Predictive modeling for patient outcomes
    6. Visualization of results

    Args:
        data_path: Path to the clinical trial data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting clinical trial data analysis workflow...")

    # 1. Load clinical trial data
    print("Loading clinical trial data...")
    clinical_data = pd.read_csv(data_path)

    # Create a session to track the analysis
    session = create_session(
        name="Clinical Trial Analysis",
        description="Analysis of clinical trial data for drug efficacy and safety"
    )

    # 2. Data cleaning and preprocessing
    print("Cleaning and preprocessing data...")

    # Handle missing values
    clinical_data['age'].fillna(clinical_data['age'].median(), inplace=True)
    clinical_data['bmi'].fillna(clinical_data['bmi'].median(), inplace=True)

    # Convert categorical variables to dummy variables
    if 'treatment_group' in clinical_data.columns:
        clinical_data = pd.get_dummies(clinical_data, columns=['treatment_group'], drop_first=True)

    if 'sex' in clinical_data.columns:
        clinical_data['sex'] = clinical_data['sex'].map({'M': 1, 'F': 0})

    # 3. Exploratory data analysis
    print("Performing exploratory data analysis...")

    # Basic statistics
    summary_stats = clinical_data.describe()

    # Check for correlations
    correlation_matrix = clinical_data.select_dtypes(include=[np.number]).corr()

    # 4. Statistical analysis
    print("Performing statistical analysis...")

    # Simulate survival analysis
    # In a real workflow, you would use libraries like lifelines or survival

    # Assume we have survival data with time and event columns
    if 'survival_time' in clinical_data.columns and 'event' in clinical_data.columns:
        from sklearn.preprocessing import StandardScaler

        # Prepare data for Cox proportional hazards model
        features = clinical_data.drop(['patient_id', 'survival_time', 'event'], axis=1, errors='ignore')
        features = StandardScaler().fit_transform(features)

        # Simulate Cox model results
        cox_results = {
            'concordance_index': 0.75,
            'log_likelihood': -156.78,
            'hazard_ratios': {
                'age': 1.02,
                'bmi': 0.98,
                'treatment_group_B': 0.65  # Treatment B reduces hazard by 35%
            }
        }
    else:
        # If no survival data, create placeholder
        cox_results = {'note': 'No survival data available'}

    # 5. Predictive modeling for patient outcomes
    print("Building predictive model for patient outcomes...")

    # Assume we want to predict a binary outcome (e.g., response to treatment)
    if 'response' in clinical_data.columns:
        # Prepare data
        X = clinical_data.drop(['patient_id', 'response', 'survival_time', 'event'], axis=1, errors='ignore')
        y = clinical_data['response']

        # Split data
        X_train, X_test, y_train, y_test = prepare_data(
            pd.DataFrame(X), 'response', test_size=0.3, random_state=42
        )

        # Train a random forest model
        from sklearn.ensemble import RandomForestClassifier

        model, results = train_model(
            RandomForestClassifier(n_estimators=100, random_state=42),
            X_train,
            y_train,
            model_type='sklearn',
            cross_validate=True,
            cv=5,
            scoring=['accuracy', 'precision', 'recall', 'f1']
        )

        # Evaluate on test set
        test_metrics = evaluate_model(model, X_test, y_test)

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        # Save the model
        model_path = os.path.join(os.path.dirname(data_path), 'clinical_response_model.pkl')
        save_model(model, model_path)

        model_results = {
            'cross_validation': results,
            'test_metrics': test_metrics,
            'feature_importance': feature_importance.to_dict(),
            'model_path': model_path
        }
    else:
        # If no response data, create placeholder
        model_results = {'note': 'No response data available'}

    # 6. Visualization of results
    print("Generating visualizations...")

    # Create Kaplan-Meier curves (simulated)
    if 'survival_time' in clinical_data.columns and 'event' in clinical_data.columns:
        plt.figure(figsize=(10, 6))

        # Simulate Kaplan-Meier curves for two treatment groups
        times = np.linspace(0, 60, 100)  # 60 months

        # Treatment A survival curve
        survival_A = np.exp(-0.02 * times)
        plt.step(times, survival_A, where='post', label='Treatment A')

        # Treatment B survival curve
        survival_B = np.exp(-0.01 * times)  # Better survival
        plt.step(times, survival_B, where='post', label='Treatment B')

        plt.xlabel('Time (months)')
        plt.ylabel('Survival Probability')
        plt.title('Kaplan-Meier Survival Curves by Treatment Group')
        plt.ylim(0, 1)
        plt.grid(alpha=0.3)
        plt.legend()

        # Save the plot
        km_plot_path = os.path.join(os.path.dirname(data_path), 'kaplan_meier_plot.png')
        plt.savefig(km_plot_path)
    else:
        km_plot_path = None

    # If we have a model, plot feature importance
    if 'feature_importance' in model_results:
        plt.figure(figsize=(10, 6))

        # Get top 10 features
        top_features = pd.DataFrame(model_results['feature_importance']).sort_values('importance', ascending=False).head(10)

        plt.barh(top_features['feature'], top_features['importance'])
        plt.xlabel('Importance')
        plt.ylabel('Feature')
        plt.title('Top 10 Features for Predicting Treatment Response')
        plt.tight_layout()

        # Save the plot
        importance_plot_path = os.path.join(os.path.dirname(data_path), 'feature_importance_plot.png')
        plt.savefig(importance_plot_path)
    else:
        importance_plot_path = None

    # Save analysis results to the session
    session.add_metadata({
        'num_patients': len(clinical_data),
        'cox_concordance': cox_results.get('concordance_index', None),
        'model_accuracy': test_metrics.get('accuracy', None) if 'test_metrics' in model_results else None,
        'km_plot_path': km_plot_path,
        'importance_plot_path': importance_plot_path
    })

    # Save the session
    session.save()

    print("Clinical trial data analysis workflow completed.")

    return {
        'clinical_data': clinical_data.head(),
        'summary_stats': summary_stats,
        'cox_results': cox_results,
        'model_results': model_results,
        'km_plot_path': km_plot_path,
        'importance_plot_path': importance_plot_path,
        'session_id': session.session_id
    }


def environmental_monitoring_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for environmental monitoring data analysis.

    This workflow demonstrates:
    1. Loading environmental sensor data
    2. Data cleaning and preprocessing
    3. Time series analysis
    4. Anomaly detection
    5. Predictive modeling for environmental parameters
    6. Visualization of results

    Args:
        data_path: Path to the environmental data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting environmental monitoring data analysis workflow...")

    # 1. Load environmental sensor data
    print("Loading environmental sensor data...")
    env_data = pd.read_csv(data_path)

    # Convert timestamp to datetime if it exists
    if 'timestamp' in env_data.columns:
        env_data['timestamp'] = pd.to_datetime(env_data['timestamp'])
        env_data.set_index('timestamp', inplace=True)

    # Create a session to track the analysis
    session = create_session(
        name="Environmental Monitoring Analysis",
        description="Analysis of environmental sensor data for monitoring and prediction"
    )

    # 2. Data cleaning and preprocessing
    print("Cleaning and preprocessing data...")

    # Handle missing values using forward fill (common for time series)
    env_data = env_data.ffill()

    # Remove outliers using IQR method
    for column in env_data.select_dtypes(include=[np.number]).columns:
        Q1 = env_data[column].quantile(0.25)
        Q3 = env_data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        env_data[column] = env_data[column].clip(lower_bound, upper_bound)

    # 3. Time series analysis
    print("Performing time series analysis...")

    # Resample to daily frequency if data is time-indexed
    if isinstance(env_data.index, pd.DatetimeIndex):
        daily_data = env_data.resample('D').mean()

        # Calculate rolling averages
        rolling_avg = daily_data.rolling(window=7).mean()

        # Decompose time series (simulated)
        # In a real workflow, you would use libraries like statsmodels

        # Simulate seasonal decomposition for a key parameter (e.g., temperature)
        if 'temperature' in daily_data.columns:
            # Create simulated components
            trend = np.linspace(20, 25, len(daily_data))
            seasonal = 5 * np.sin(np.linspace(0, 12*np.pi, len(daily_data)))
            residual = np.random.normal(0, 1, len(daily_data))

            decomposition = {
                'trend': trend,
                'seasonal': seasonal,
                'residual': residual,
                'observed': trend + seasonal + residual
            }
        else:
            decomposition = None
    else:
        daily_data = None
        rolling_avg = None
        decomposition = None

    # 4. Anomaly detection
    print("Detecting anomalies in environmental data...")

    # Simple anomaly detection using Z-scores
    z_scores = {}
    anomalies = {}

    for column in env_data.select_dtypes(include=[np.number]).columns:
        # Calculate Z-scores
        mean = env_data[column].mean()
        std = env_data[column].std()
        z_scores[column] = (env_data[column] - mean) / std

        # Identify anomalies (|Z| > 3)
        anomalies[column] = env_data[z_scores[column].abs() > 3]

    # Count anomalies per parameter
    anomaly_counts = {col: len(anomalies[col]) for col in anomalies}

    # 5. Predictive modeling for environmental parameters
    print("Building predictive model for environmental parameters...")

    # Choose a parameter to predict (e.g., temperature, air quality)
    target_param = 'temperature' if 'temperature' in env_data.columns else env_data.columns[0]

    # Prepare features (use lag features for time series prediction)
    if isinstance(env_data.index, pd.DatetimeIndex):
        # Create lag features
        features_df = env_data.copy()

        # Add lags of the target parameter
        for lag in [1, 2, 3, 7]:
            features_df[f'{target_param}_lag_{lag}'] = features_df[target_param].shift(lag)

        # Add rolling statistics
        features_df[f'{target_param}_rolling_mean_7'] = features_df[target_param].rolling(window=7).mean()
        features_df[f'{target_param}_rolling_std_7'] = features_df[target_param].rolling(window=7).std()

        # Drop rows with NaN values
        features_df = features_df.dropna()

        # Prepare data for modeling
        X = features_df.drop(target_param, axis=1)
        y = features_df[target_param]

        # Split data chronologically
        train_size = int(len(X) * 0.7)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

        # Train a model
        from sklearn.ensemble import GradientBoostingRegressor

        model, results = train_model(
            GradientBoostingRegressor(n_estimators=100, random_state=42),
            X_train,
            y_train,
            model_type='sklearn'
        )

        # Evaluate on test set
        test_metrics = evaluate_model(model, X_test, y_test, is_classifier=False)

        # Make predictions
        y_pred = model.predict(X_test)

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        # Save the model
        model_path = os.path.join(os.path.dirname(data_path), f'{target_param}_prediction_model.pkl')
        save_model(model, model_path)

        model_results = {
            'target_parameter': target_param,
            'test_metrics': test_metrics,
            'feature_importance': feature_importance.to_dict(),
            'model_path': model_path
        }
    else:
        model_results = {'note': 'Time series prediction requires datetime-indexed data'}
        y_pred = None

    # 6. Visualization of results
    print("Generating visualizations...")

    # Time series plot with anomalies
    if isinstance(env_data.index, pd.DatetimeIndex) and target_param in env_data.columns:
        plt.figure(figsize=(12, 6))

        # Plot the time series
        plt.plot(env_data.index, env_data[target_param], label=target_param, alpha=0.7)

        # Plot anomalies
        if target_param in anomalies and len(anomalies[target_param]) > 0:
            plt.scatter(
                anomalies[target_param].index,
                anomalies[target_param][target_param],
                color='red',
                label='Anomalies',
                zorder=5
            )

        plt.xlabel('Time')
        plt.ylabel(target_param)
        plt.title(f'{target_param} Time Series with Anomalies')
        plt.legend()
        plt.grid(alpha=0.3)

        # Save the plot
        timeseries_plot_path = os.path.join(os.path.dirname(data_path), f'{target_param}_timeseries_plot.png')
        plt.savefig(timeseries_plot_path)
    else:
        timeseries_plot_path = None

    # Prediction performance plot
    if y_pred is not None:
        plt.figure(figsize=(12, 6))

        # Plot actual vs predicted values
        plt.plot(X_test.index, y_test, label='Actual', alpha=0.7)
        plt.plot(X_test.index, y_pred, label='Predicted', alpha=0.7)

        plt.xlabel('Time')
        plt.ylabel(target_param)
        plt.title(f'Actual vs Predicted {target_param}')
        plt.legend()
        plt.grid(alpha=0.3)

        # Save the plot
        prediction_plot_path = os.path.join(os.path.dirname(data_path), f'{target_param}_prediction_plot.png')
        plt.savefig(prediction_plot_path)
    else:
        prediction_plot_path = None

    # Save analysis results to the session
    session.add_metadata({
        'data_timespan': f"{env_data.index.min()} to {env_data.index.max()}" if isinstance(env_data.index, pd.DatetimeIndex) else None,
        'num_anomalies': sum(anomaly_counts.values()),
        'model_rmse': test_metrics.get('rmse', None) if 'test_metrics' in model_results else None,
        'timeseries_plot_path': timeseries_plot_path,
        'prediction_plot_path': prediction_plot_path
    })

    # Save the session
    session.save()

    print("Environmental monitoring data analysis workflow completed.")

    return {
        'env_data': env_data.head(),
        'daily_data': daily_data.head() if daily_data is not None else None,
        'anomaly_counts': anomaly_counts,
        'model_results': model_results,
        'timeseries_plot_path': timeseries_plot_path,
        'prediction_plot_path': prediction_plot_path,
        'session_id': session.session_id
    }


def preclinical_research_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for preclinical research data analysis.

    This workflow demonstrates:
    1. Loading preclinical research data (animal studies)
    2. Data integration and preprocessing
    3. Statistical analysis of treatment effects
    4. Dose-response modeling
    5. Visualization of results
    6. Storing results in Neo4j with ontology annotations

    Args:
        data_path: Path to the preclinical data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting preclinical research data analysis workflow...")

    # 1. Load preclinical research data
    print("Loading preclinical research data...")
    preclinical_data = pd.read_csv(data_path)

    # Create a session to track the analysis
    session = create_session(
        name="Preclinical Research Analysis",
        description="Analysis of preclinical animal study data for drug development"
    )

    # 2. Data integration and preprocessing
    print("Integrating and preprocessing data...")

    # Handle missing values
    for col in preclinical_data.select_dtypes(include=[np.number]).columns:
        preclinical_data[col].fillna(preclinical_data[col].median(), inplace=True)

    # Convert categorical variables
    if 'treatment_group' in preclinical_data.columns:
        preclinical_data = pd.get_dummies(preclinical_data, columns=['treatment_group'], drop_first=False)

    if 'sex' in preclinical_data.columns:
        preclinical_data['sex'] = preclinical_data['sex'].map({'M': 1, 'F': 0})

    # 3. Statistical analysis of treatment effects
    print("Analyzing treatment effects...")

    # Assume we have a primary endpoint column
    if 'primary_endpoint' in preclinical_data.columns:
        # Group by treatment and calculate statistics
        treatment_stats = preclinical_data.groupby('treatment').agg({
            'primary_endpoint': ['mean', 'std', 'count']
        })

        # Perform ANOVA to test for differences between treatment groups
        from scipy import stats

        # Get unique treatment groups
        treatments = preclinical_data['treatment'].unique()

        # Collect data for each treatment group
        treatment_data = [preclinical_data[preclinical_data['treatment'] == t]['primary_endpoint'].values for t in treatments]

        # Perform one-way ANOVA
        f_stat, p_value = stats.f_oneway(*treatment_data)

        # Perform post-hoc tests if ANOVA is significant
        if p_value < 0.05:
            # Perform Tukey's HSD test
            from statsmodels.stats.multicomp import pairwise_tukeyhsd

            # Prepare data for Tukey's test
            endog = preclinical_data['primary_endpoint']
            groups = preclinical_data['treatment']

            # Perform Tukey's test
            tukey_results = pairwise_tukeyhsd(endog, groups, alpha=0.05)

            # Convert results to a more usable format
            tukey_summary = pd.DataFrame(data=tukey_results._results_table.data[1:], 
                                        columns=tukey_results._results_table.data[0])
        else:
            tukey_summary = None

        anova_results = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'post_hoc': tukey_summary.to_dict() if tukey_summary is not None else None
        }
    else:
        treatment_stats = None
        anova_results = None

    # 4. Dose-response modeling
    print("Performing dose-response modeling...")

    # Check if we have dose and response columns
    if 'dose' in preclinical_data.columns and 'response' in preclinical_data.columns:
        # Group by dose and calculate mean response
        dose_response = preclinical_data.groupby('dose')['response'].mean().reset_index()

        # Fit a sigmoid dose-response curve (4-parameter logistic)
        from scipy.optimize import curve_fit

        def sigmoid(x, bottom, top, ec50, hill):
            """4-parameter logistic function"""
            return bottom + (top - bottom) / (1 + (ec50 / x) ** hill)

        # Initial parameter guesses
        p0 = [min(dose_response['response']), max(dose_response['response']), 
              np.median(dose_response['dose']), 1.0]

        # Fit the curve
        try:
            params, pcov = curve_fit(sigmoid, dose_response['dose'], dose_response['response'], p0=p0)

            # Generate points for the fitted curve
            dose_range = np.linspace(min(dose_response['dose']), max(dose_response['dose']), 100)
            response_fitted = sigmoid(dose_range, *params)

            # Calculate EC50
            ec50 = params[2]

            dose_response_results = {
                'model': 'sigmoid',
                'parameters': {
                    'bottom': params[0],
                    'top': params[1],
                    'ec50': params[2],
                    'hill': params[3]
                },
                'ec50': ec50,
                'dose_range': dose_range.tolist(),
                'response_fitted': response_fitted.tolist()
            }
        except:
            dose_response_results = {'error': 'Failed to fit dose-response curve'}
    else:
        dose_response = None
        dose_response_results = None

    # 5. Visualization of results
    print("Generating visualizations...")

    # Treatment effect plot
    if treatment_stats is not None:
        plt.figure(figsize=(10, 6))

        # Extract data
        treatments = treatment_stats.index
        means = treatment_stats['primary_endpoint']['mean']
        stds = treatment_stats['primary_endpoint']['std']

        # Create bar plot
        plt.bar(range(len(treatments)), means, yerr=stds, capsize=10, alpha=0.7)
        plt.xticks(range(len(treatments)), treatments)

        plt.xlabel('Treatment')
        plt.ylabel('Primary Endpoint')
        plt.title('Treatment Effects on Primary Endpoint')
        plt.grid(axis='y', alpha=0.3)

        # Add p-value annotation
        if anova_results is not None:
            plt.annotate(f"ANOVA p-value: {anova_results['p_value']:.4f}",
                        xy=(0.5, 0.95), xycoords='axes fraction',
                        ha='center', va='center',
                        bbox=dict(boxstyle='round', fc='white', alpha=0.8))

        # Save the plot
        treatment_plot_path = os.path.join(os.path.dirname(data_path), 'treatment_effects_plot.png')
        plt.savefig(treatment_plot_path)
    else:
        treatment_plot_path = None

    # Dose-response plot
    if dose_response is not None and dose_response_results is not None and 'error' not in dose_response_results:
        plt.figure(figsize=(10, 6))

        # Plot observed data points
        plt.scatter(dose_response['dose'], dose_response['response'], 
                   label='Observed', color='blue', s=50)

        # Plot fitted curve
        plt.plot(dose_response_results['dose_range'], dose_response_results['response_fitted'],
                label='Fitted curve', color='red')

        # Mark EC50
        ec50 = dose_response_results['ec50']
        half_max = (dose_response_results['parameters']['bottom'] + dose_response_results['parameters']['top']) / 2
        plt.scatter([ec50], [half_max], color='green', s=100, zorder=5, label=f'EC50 = {ec50:.2f}')
        plt.axvline(x=ec50, color='green', linestyle='--', alpha=0.5)
        plt.axhline(y=half_max, color='green', linestyle='--', alpha=0.5)

        plt.xlabel('Dose')
        plt.ylabel('Response')
        plt.title('Dose-Response Relationship')
        plt.legend()
        plt.grid(alpha=0.3)

        # Save the plot
        dose_response_plot_path = os.path.join(os.path.dirname(data_path), 'dose_response_plot.png')
        plt.savefig(dose_response_plot_path)
    else:
        dose_response_plot_path = None

    # 6. Store results in Neo4j with ontology annotations
    print("Storing results in Neo4j with ontology annotations...")
    db_manager = DBManager()

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

        # Create treatment nodes with ontology annotations
        if 'treatment' in preclinical_data.columns:
            for treatment in preclinical_data['treatment'].unique():
                # Create treatment node
                treatment_query = """
                MERGE (t:Treatment {name: $treatment_name})
                RETURN t
                """
                treatment_params = {
                    'treatment_name': treatment
                }
                tx.run(treatment_query, treatment_params)

                # Link treatment to study
                link_query = """
                MATCH (s:Study {id: $study_id})
                MATCH (t:Treatment {name: $treatment_name})
                MERGE (s)-[r:INCLUDES_TREATMENT]->(t)
                RETURN r
                """
                link_params = {
                    'study_id': f"STUDY_{session.session_id}",
                    'treatment_name': treatment
                }
                tx.run(link_query, link_params)

                # Add ontology annotation (simulated)
                # In a real workflow, you would use actual ontology terms
                ontology_query = """
                MATCH (t:Treatment {name: $treatment_name})
                MERGE (o:OntologyTerm {id: $term_id})
                ON CREATE SET o.name = $term_name, o.source = $term_source
                MERGE (t)-[r:HAS_ONTOLOGY_ANNOTATION]->(o)
                RETURN r
                """

                # Simulate ontology terms based on treatment name
                if 'control' in treatment.lower():
                    term_id = 'NCIT:C28143'
                    term_name = 'Control Group'
                    term_source = 'NCIT'
                elif 'vehicle' in treatment.lower():
                    term_id = 'NCIT:C28254'
                    term_name = 'Vehicle Control'
                    term_source = 'NCIT'
                else:
                    term_id = 'NCIT:C49236'
                    term_name = 'Treatment Group'
                    term_source = 'NCIT'

                ontology_params = {
                    'treatment_name': treatment,
                    'term_id': term_id,
                    'term_name': term_name,
                    'term_source': term_source
                }
                tx.run(ontology_query, ontology_params)

        # Store analysis results
        if anova_results is not None:
            analysis_query = """
            MATCH (s:Study {id: $study_id})
            CREATE (a:Analysis {type: 'ANOVA', f_statistic: $f_stat, p_value: $p_value, significant: $significant})
            CREATE (s)-[r:HAS_ANALYSIS]->(a)
            RETURN a
            """
            analysis_params = {
                'study_id': f"STUDY_{session.session_id}",
                'f_stat': float(anova_results['f_statistic']),
                'p_value': float(anova_results['p_value']),
                'significant': anova_results['significant']
            }
            tx.run(analysis_query, analysis_params)

        if dose_response_results is not None and 'error' not in dose_response_results:
            dr_query = """
            MATCH (s:Study {id: $study_id})
            CREATE (dr:Analysis {
                type: 'DoseResponse',
                model: $model,
                ec50: $ec50,
                bottom: $bottom,
                top: $top,
                hill: $hill
            })
            CREATE (s)-[r:HAS_ANALYSIS]->(dr)
            RETURN dr
            """
            dr_params = {
                'study_id': f"STUDY_{session.session_id}",
                'model': dose_response_results['model'],
                'ec50': float(dose_response_results['ec50']),
                'bottom': float(dose_response_results['parameters']['bottom']),
                'top': float(dose_response_results['parameters']['top']),
                'hill': float(dose_response_results['parameters']['hill'])
            }
            tx.run(dr_query, dr_params)

    # Save analysis results to the session
    session.add_metadata({
        'num_animals': len(preclinical_data),
        'num_treatments': len(preclinical_data['treatment'].unique()) if 'treatment' in preclinical_data.columns else 0,
        'anova_p_value': anova_results['p_value'] if anova_results is not None else None,
        'ec50': dose_response_results['ec50'] if dose_response_results is not None and 'error' not in dose_response_results else None,
        'treatment_plot_path': treatment_plot_path,
        'dose_response_plot_path': dose_response_plot_path
    })

    # Save the session
    session.save()

    print("Preclinical research data analysis workflow completed.")

    return {
        'preclinical_data': preclinical_data.head(),
        'treatment_stats': treatment_stats.to_dict() if treatment_stats is not None else None,
        'anova_results': anova_results,
        'dose_response_results': dose_response_results,
        'treatment_plot_path': treatment_plot_path,
        'dose_response_plot_path': dose_response_plot_path,
        'session_id': session.session_id
    }


def materials_science_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for materials science data analysis.

    This workflow demonstrates:
    1. Loading materials characterization data
    2. Data preprocessing and feature extraction
    3. Structure-property relationship analysis
    4. Predictive modeling of material properties
    5. Visualization of results
    6. Storing results in Neo4j with material ontology

    Args:
        data_path: Path to the materials data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting materials science data analysis workflow...")

    # 1. Load materials characterization data
    print("Loading materials characterization data...")
    materials_data = pd.read_csv(data_path)

    # Create a session to track the analysis
    session = create_session(
        name="Materials Science Analysis",
        description="Analysis of materials characterization data for property prediction"
    )

    # 2. Data preprocessing and feature extraction
    print("Preprocessing data and extracting features...")

    # Handle missing values
    for col in materials_data.select_dtypes(include=[np.number]).columns:
        materials_data[col].fillna(materials_data[col].median(), inplace=True)

    # Normalize numerical features
    from sklearn.preprocessing import StandardScaler

    # Identify numerical columns
    numerical_cols = materials_data.select_dtypes(include=[np.number]).columns.tolist()

    # Remove target properties from features
    target_properties = ['tensile_strength', 'youngs_modulus', 'thermal_conductivity']
    feature_cols = [col for col in numerical_cols if col not in target_properties and col in materials_data.columns]

    # Standardize features
    if feature_cols:
        scaler = StandardScaler()
        materials_data[feature_cols] = scaler.fit_transform(materials_data[feature_cols])

    # 3. Structure-property relationship analysis
    print("Analyzing structure-property relationships...")

    # Calculate correlation matrix
    correlation_matrix = materials_data[numerical_cols].corr()

    # Find top correlations with target properties
    top_correlations = {}

    for target in target_properties:
        if target in correlation_matrix.columns:
            # Get correlations with the target property
            correlations = correlation_matrix[target].drop(target_properties)

            # Sort by absolute correlation
            sorted_correlations = correlations.abs().sort_values(ascending=False)

            # Get top 5 correlations
            top_correlations[target] = {
                'features': sorted_correlations.index[:5].tolist(),
                'values': sorted_correlations.values[:5].tolist()
            }

    # 4. Predictive modeling of material properties
    print("Building predictive models for material properties...")

    model_results = {}

    for target in target_properties:
        if target in materials_data.columns and len(materials_data) > 20:  # Ensure enough data
            print(f"Modeling {target}...")

            # Prepare data
            X = materials_data[feature_cols]
            y = materials_data[target]

            # Split data
            X_train, X_test, y_train, y_test = prepare_data(
                pd.DataFrame(X), target, test_size=0.3, random_state=42
            )

            # Train a gradient boosting model
            from sklearn.ensemble import GradientBoostingRegressor

            model, results = train_model(
                GradientBoostingRegressor(n_estimators=100, random_state=42),
                X_train,
                y_train,
                model_type='sklearn',
                cross_validate=True,
                cv=5,
                scoring=['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
            )

            # Evaluate on test set
            test_metrics = evaluate_model(model, X_test, y_test, is_classifier=False)

            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)

            # Save the model
            model_path = os.path.join(os.path.dirname(data_path), f'{target}_prediction_model.pkl')
            save_model(model, model_path)

            # Make predictions
            y_pred = model.predict(X_test)

            model_results[target] = {
                'cross_validation': results,
                'test_metrics': test_metrics,
                'feature_importance': feature_importance.to_dict(),
                'model_path': model_path,
                'y_test': y_test.values.tolist(),
                'y_pred': y_pred.tolist()
            }

    # 5. Visualization of results
    print("Generating visualizations...")

    # Correlation heatmap
    plt.figure(figsize=(12, 10))
    plt.imshow(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1)

    # Add labels
    plt.colorbar(label='Correlation Coefficient')
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=90)
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)

    # Add correlation values
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}",
                    ha='center', va='center', color='white' if abs(correlation_matrix.iloc[i, j]) > 0.5 else 'black')

    plt.title('Correlation Matrix of Material Properties and Features')
    plt.tight_layout()

    # Save the plot
    correlation_plot_path = os.path.join(os.path.dirname(data_path), 'correlation_heatmap.png')
    plt.savefig(correlation_plot_path)

    # Parity plots for model predictions
    parity_plot_paths = {}

    for target in model_results:
        plt.figure(figsize=(8, 8))

        # Get actual and predicted values
        y_test = model_results[target]['y_test']
        y_pred = model_results[target]['y_pred']

        # Create parity plot
        plt.scatter(y_test, y_pred, alpha=0.7)

        # Add parity line
        min_val = min(min(y_test), min(y_pred))
        max_val = max(max(y_test), max(y_pred))
        plt.plot([min_val, max_val], [min_val, max_val], 'k--')

        # Add R² value
        r2 = model_results[target]['test_metrics']['r2']
        plt.annotate(f"R² = {r2:.3f}", xy=(0.05, 0.95), xycoords='axes fraction',
                    ha='left', va='top', bbox=dict(boxstyle='round', fc='white', alpha=0.8))

        plt.xlabel(f'Actual {target.replace("_", " ").title()}')
        plt.ylabel(f'Predicted {target.replace("_", " ").title()}')
        plt.title(f'Parity Plot for {target.replace("_", " ").title()} Prediction')
        plt.grid(alpha=0.3)
        plt.axis('equal')

        # Save the plot
        parity_plot_path = os.path.join(os.path.dirname(data_path), f'{target}_parity_plot.png')
        plt.savefig(parity_plot_path)

        parity_plot_paths[target] = parity_plot_path

    # 6. Store results in Neo4j with material ontology
    print("Storing results in Neo4j with material ontology...")
    db_manager = DBManager()

    # Create a transaction
    with db_manager.transaction() as tx:
        # Create a study node
        study_query = """
        CREATE (s:MaterialsStudy {id: $study_id, name: $study_name, description: $study_description})
        RETURN s
        """
        study_params = {
            'study_id': f"MATSTUDY_{session.session_id}",
            'study_name': session.config.name,
            'study_description': session.config.description
        }
        tx.run(study_query, study_params)

        # Create material nodes
        if 'material_id' in materials_data.columns and 'material_type' in materials_data.columns:
            for _, material in materials_data[['material_id', 'material_type']].drop_duplicates().iterrows():
                # Create material node
                material_query = """
                MERGE (m:Material {id: $material_id})
                SET m.type = $material_type
                RETURN m
                """
                material_params = {
                    'material_id': material['material_id'],
                    'material_type': material['material_type']
                }
                tx.run(material_query, material_params)

                # Link material to study
                link_query = """
                MATCH (s:MaterialsStudy {id: $study_id})
                MATCH (m:Material {id: $material_id})
                MERGE (s)-[r:INCLUDES_MATERIAL]->(m)
                RETURN r
                """
                link_params = {
                    'study_id': f"MATSTUDY_{session.session_id}",
                    'material_id': material['material_id']
                }
                tx.run(link_query, link_params)

                # Add ontology annotation (simulated)
                # In a real workflow, you would use actual material ontology terms
                ontology_query = """
                MATCH (m:Material {id: $material_id})
                MERGE (o:OntologyTerm {id: $term_id})
                ON CREATE SET o.name = $term_name, o.source = $term_source
                MERGE (m)-[r:HAS_ONTOLOGY_ANNOTATION]->(o)
                RETURN r
                """

                # Simulate ontology terms based on material type
                material_type = material['material_type'].lower()
                if 'metal' in material_type:
                    term_id = 'EMMO:00000113'
                    term_name = 'Metal'
                    term_source = 'EMMO'
                elif 'polymer' in material_type:
                    term_id = 'EMMO:00000114'
                    term_name = 'Polymer'
                    term_source = 'EMMO'
                elif 'ceramic' in material_type:
                    term_id = 'EMMO:00000115'
                    term_name = 'Ceramic'
                    term_source = 'EMMO'
                else:
                    term_id = 'EMMO:00000116'
                    term_name = 'Composite'
                    term_source = 'EMMO'

                ontology_params = {
                    'material_id': material['material_id'],
                    'term_id': term_id,
                    'term_name': term_name,
                    'term_source': term_source
                }
                tx.run(ontology_query, ontology_params)

        # Store model results
        for target, result in model_results.items():
            model_query = """
            MATCH (s:MaterialsStudy {id: $study_id})
            CREATE (m:Model {
                property: $property,
                r2_score: $r2_score,
                rmse: $rmse,
                model_path: $model_path
            })
            CREATE (s)-[r:HAS_MODEL]->(m)
            RETURN m
            """
            model_params = {
                'study_id': f"MATSTUDY_{session.session_id}",
                'property': target,
                'r2_score': float(result['test_metrics']['r2']),
                'rmse': float(result['test_metrics'].get('rmse', 0)),
                'model_path': result['model_path']
            }
            tx.run(model_query, model_params)

            # Store top features for the model
            feature_importance = pd.DataFrame(result['feature_importance'])
            top_features = feature_importance.sort_values('importance', ascending=False).head(5)

            for _, feature in top_features.iterrows():
                feature_query = """
                MATCH (m:Model {property: $property})
                CREATE (f:Feature {name: $feature_name, importance: $importance})
                CREATE (m)-[r:HAS_IMPORTANT_FEATURE]->(f)
                RETURN f
                """
                feature_params = {
                    'property': target,
                    'feature_name': feature['feature'],
                    'importance': float(feature['importance'])
                }
                tx.run(feature_query, feature_params)

    # Save analysis results to the session
    session.add_metadata({
        'num_materials': len(materials_data),
        'correlation_plot_path': correlation_plot_path,
        'parity_plot_paths': parity_plot_paths,
        'model_performance': {target: result['test_metrics']['r2'] for target, result in model_results.items()}
    })

    # Save the session
    session.save()

    print("Materials science data analysis workflow completed.")

    return {
        'materials_data': materials_data.head(),
        'correlation_matrix': correlation_matrix.to_dict(),
        'top_correlations': top_correlations,
        'model_results': {target: {
            'test_metrics': result['test_metrics'],
            'top_features': pd.DataFrame(result['feature_importance']).sort_values('importance', ascending=False).head(5).to_dict()
        } for target, result in model_results.items()},
        'correlation_plot_path': correlation_plot_path,
        'parity_plot_paths': parity_plot_paths,
        'session_id': session.session_id
    }


def pharmaceutical_data_analysis_workflow(data_path: str) -> Dict[str, Any]:
    """
    Example workflow for pharmaceutical data analysis.

    This workflow demonstrates:
    1. Loading pharmaceutical compound data
    2. Data preprocessing and feature extraction
    3. QSAR (Quantitative Structure-Activity Relationship) modeling
    4. Drug-target interaction prediction
    5. Pharmacokinetic property prediction
    6. Visualization of results
    7. Storing results in Neo4j with pharmaceutical ontology

    Args:
        data_path: Path to the pharmaceutical data file (CSV format)

    Returns:
        Dictionary with analysis results
    """
    print("Starting pharmaceutical data analysis workflow...")

    # 1. Load pharmaceutical compound data
    print("Loading pharmaceutical compound data...")
    pharma_data = pd.read_csv(data_path)

    # Create a session to track the analysis
    session = create_session(
        name="Pharmaceutical Data Analysis",
        description="Analysis of pharmaceutical compounds for drug discovery"
    )

    # 2. Data preprocessing and feature extraction
    print("Preprocessing data and extracting features...")

    # Handle missing values
    for col in pharma_data.select_dtypes(include=[np.number]).columns:
        pharma_data[col].fillna(pharma_data[col].median(), inplace=True)

    # Assume we have molecular descriptors and fingerprints
    # In a real workflow, you would calculate these using libraries like RDKit
    descriptor_cols = [col for col in pharma_data.columns if col.startswith('desc_')]
    fingerprint_cols = [col for col in pharma_data.columns if col.startswith('fp_')]

    # Normalize descriptors
    from sklearn.preprocessing import StandardScaler

    if descriptor_cols:
        scaler = StandardScaler()
        pharma_data[descriptor_cols] = scaler.fit_transform(pharma_data[descriptor_cols])

    # 3. QSAR modeling
    print("Building QSAR models...")

    # Assume we have activity data (e.g., IC50, Ki, EC50)
    activity_cols = [col for col in pharma_data.columns if col in ['IC50', 'Ki', 'EC50', 'activity']]

    qsar_results = {}

    if activity_cols and (descriptor_cols or fingerprint_cols):
        for activity in activity_cols:
            if activity in pharma_data.columns:
                print(f"Modeling {activity}...")

                # Prepare features (combine descriptors and fingerprints)
                feature_cols = descriptor_cols + fingerprint_cols

                # Log-transform activity values if needed
                if pharma_data[activity].min() > 0:  # Can't log-transform zero or negative values
                    pharma_data[f'{activity}_log'] = -np.log10(pharma_data[activity])
                    target = f'{activity}_log'
                else:
                    target = activity

                # Prepare data for modeling
                X = pharma_data[feature_cols]
                y = pharma_data[target]

                # Split data
                X_train, X_test, y_train, y_test = prepare_data(
                    pd.DataFrame(X), target, test_size=0.2, random_state=42
                )

                # Train a random forest model
                from sklearn.ensemble import RandomForestRegressor

                model, results = train_model(
                    RandomForestRegressor(n_estimators=100, random_state=42),
                    X_train,
                    y_train,
                    model_type='sklearn',
                    cross_validate=True,
                    cv=5,
                    scoring=['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
                )

                # Evaluate on test set
                test_metrics = evaluate_model(model, X_test, y_test, is_classifier=False)

                # Feature importance
                feature_importance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)

                # Save the model
                model_path = os.path.join(os.path.dirname(data_path), f'{activity}_qsar_model.pkl')
                save_model(model, model_path)

                # Make predictions
                y_pred = model.predict(X_test)

                qsar_results[activity] = {
                    'target': target,
                    'test_metrics': test_metrics,
                    'feature_importance': feature_importance.to_dict(),
                    'model_path': model_path,
                    'y_test': y_test.values.tolist(),
                    'y_pred': y_pred.tolist()
                }

    # 4. Drug-target interaction prediction
    print("Predicting drug-target interactions...")

    # Assume we have target data
    target_cols = [col for col in pharma_data.columns if col.startswith('target_')]

    dti_results = {}

    if target_cols and (descriptor_cols or fingerprint_cols):
        for target in target_cols:
            if target in pharma_data.columns:
                print(f"Modeling interaction with {target}...")

                # Prepare features
                feature_cols = descriptor_cols + fingerprint_cols

                # Prepare data for modeling
                X = pharma_data[feature_cols]
                y = pharma_data[target]

                # Split data
                X_train, X_test, y_train, y_test = prepare_data(
                    pd.DataFrame(X), target, test_size=0.2, random_state=42
                )

                # Train a random forest classifier
                from sklearn.ensemble import RandomForestClassifier

                model, results = train_model(
                    RandomForestClassifier(n_estimators=100, random_state=42),
                    X_train,
                    y_train,
                    model_type='sklearn',
                    cross_validate=True,
                    cv=5,
                    scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
                )

                # Evaluate on test set
                test_metrics = evaluate_model(model, X_test, y_test)

                # Feature importance
                feature_importance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)

                # Save the model
                model_path = os.path.join(os.path.dirname(data_path), f'{target}_dti_model.pkl')
                save_model(model, model_path)

                dti_results[target] = {
                    'test_metrics': test_metrics,
                    'feature_importance': feature_importance.to_dict(),
                    'model_path': model_path
                }

    # 5. Pharmacokinetic property prediction
    print("Predicting pharmacokinetic properties...")

    # Assume we have ADMET data (Absorption, Distribution, Metabolism, Excretion, Toxicity)
    admet_cols = [col for col in pharma_data.columns if col in ['LogP', 'LogS', 'HIA', 'BBB', 'CYP', 'Clearance', 'Toxicity']]

    admet_results = {}

    if admet_cols and (descriptor_cols or fingerprint_cols):
        for admet in admet_cols:
            if admet in pharma_data.columns:
                print(f"Modeling {admet}...")

                # Prepare features
                feature_cols = descriptor_cols + fingerprint_cols

                # Prepare data for modeling
                X = pharma_data[feature_cols]
                y = pharma_data[admet]

                # Determine if classification or regression
                is_categorical = len(y.unique()) < 10 or y.dtype == bool

                # Split data
                X_train, X_test, y_train, y_test = prepare_data(
                    pd.DataFrame(X), admet, test_size=0.2, random_state=42
                )

                if is_categorical:
                    # Train a random forest classifier
                    from sklearn.ensemble import RandomForestClassifier

                    model, results = train_model(
                        RandomForestClassifier(n_estimators=100, random_state=42),
                        X_train,
                        y_train,
                        model_type='sklearn',
                        cross_validate=True,
                        cv=5,
                        scoring=['accuracy', 'precision', 'recall', 'f1']
                    )

                    # Evaluate on test set
                    test_metrics = evaluate_model(model, X_test, y_test)
                else:
                    # Train a random forest regressor
                    from sklearn.ensemble import RandomForestRegressor

                    model, results = train_model(
                        RandomForestRegressor(n_estimators=100, random_state=42),
                        X_train,
                        y_train,
                        model_type='sklearn',
                        cross_validate=True,
                        cv=5,
                        scoring=['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
                    )

                    # Evaluate on test set
                    test_metrics = evaluate_model(model, X_test, y_test, is_classifier=False)

                # Feature importance
                feature_importance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)

                # Save the model
                model_path = os.path.join(os.path.dirname(data_path), f'{admet}_admet_model.pkl')
                save_model(model, model_path)

                admet_results[admet] = {
                    'is_categorical': is_categorical,
                    'test_metrics': test_metrics,
                    'feature_importance': feature_importance.to_dict(),
                    'model_path': model_path
                }

    # 6. Visualization of results
    print("Generating visualizations...")

    # QSAR model performance visualization
    qsar_plot_paths = {}

    for activity, result in qsar_results.items():
        plt.figure(figsize=(8, 8))

        # Get actual and predicted values
        y_test = result['y_test']
        y_pred = result['y_pred']

        # Create scatter plot
        plt.scatter(y_test, y_pred, alpha=0.7)

        # Add parity line
        min_val = min(min(y_test), min(y_pred))
        max_val = max(max(y_test), max(y_pred))
        plt.plot([min_val, max_val], [min_val, max_val], 'k--')

        # Add R² value
        r2 = result['test_metrics']['r2']
        plt.annotate(f"R² = {r2:.3f}", xy=(0.05, 0.95), xycoords='axes fraction',
                    ha='left', va='top', bbox=dict(boxstyle='round', fc='white', alpha=0.8))

        plt.xlabel(f'Actual {activity}')
        plt.ylabel(f'Predicted {activity}')
        plt.title(f'QSAR Model Performance for {activity}')
        plt.grid(alpha=0.3)

        # Save the plot
        qsar_plot_path = os.path.join(os.path.dirname(data_path), f'{activity}_qsar_plot.png')
        plt.savefig(qsar_plot_path)

        qsar_plot_paths[activity] = qsar_plot_path

    # Feature importance visualization
    importance_plot_paths = {}

    # Combine all models
    all_models = {**qsar_results, **dti_results, **admet_results}

    for model_name, result in all_models.items():
        plt.figure(figsize=(10, 6))

        # Get top 10 features
        feature_importance = pd.DataFrame(result['feature_importance'])
        top_features = feature_importance.sort_values('importance', ascending=False).head(10)

        # Create bar plot
        plt.barh(top_features['feature'], top_features['importance'])
        plt.xlabel('Importance')
        plt.ylabel('Feature')
        plt.title(f'Top 10 Features for {model_name}')
        plt.tight_layout()

        # Save the plot
        importance_plot_path = os.path.join(os.path.dirname(data_path), f'{model_name}_importance_plot.png')
        plt.savefig(importance_plot_path)

        importance_plot_paths[model_name] = importance_plot_path

    # 7. Store results in Neo4j with pharmaceutical ontology
    print("Storing results in Neo4j with pharmaceutical ontology...")
    db_manager = DBManager()

    # Create a transaction
    with db_manager.transaction() as tx:
        # Create a study node
        study_query = """
        CREATE (s:PharmaceuticalStudy {id: $study_id, name: $study_name, description: $study_description})
        RETURN s
        """
        study_params = {
            'study_id': f"PHARMA_STUDY_{session.session_id}",
            'study_name': session.config.name,
            'study_description': session.config.description
        }
        tx.run(study_query, study_params)

        # Create compound nodes
        if 'compound_id' in pharma_data.columns:
            for _, compound in pharma_data[['compound_id']].drop_duplicates().iterrows():
                # Create compound node
                compound_query = """
                MERGE (c:Compound {id: $compound_id})
                RETURN c
                """
                compound_params = {
                    'compound_id': compound['compound_id']
                }
                tx.run(compound_query, compound_params)

                # Link compound to study
                link_query = """
                MATCH (s:PharmaceuticalStudy {id: $study_id})
                MATCH (c:Compound {id: $compound_id})
                MERGE (s)-[r:INCLUDES_COMPOUND]->(c)
                RETURN r
                """
                link_params = {
                    'study_id': f"PHARMA_STUDY_{session.session_id}",
                    'compound_id': compound['compound_id']
                }
                tx.run(link_query, link_params)

        # Store model results
        for model_type, results_dict in [('QSAR', qsar_results), ('DTI', dti_results), ('ADMET', admet_results)]:
            for target, result in results_dict.items():
                # Create model node
                model_query = """
                MATCH (s:PharmaceuticalStudy {id: $study_id})
                CREATE (m:Model {
                    type: $model_type,
                    target: $target,
                    performance: $performance,
                    model_path: $model_path
                })
                CREATE (s)-[r:HAS_MODEL]->(m)
                RETURN m
                """

                # Get performance metric based on model type
                if model_type == 'QSAR' or (model_type == 'ADMET' and not result.get('is_categorical', False)):
                    performance = result['test_metrics'].get('r2', 0)
                else:
                    performance = result['test_metrics'].get('accuracy', 0)

                model_params = {
                    'study_id': f"PHARMA_STUDY_{session.session_id}",
                    'model_type': model_type,
                    'target': target,
                    'performance': float(performance),
                    'model_path': result['model_path']
                }
                tx.run(model_query, model_params)

                # Store top features for the model
                feature_importance = pd.DataFrame(result['feature_importance'])
                top_features = feature_importance.sort_values('importance', ascending=False).head(5)

                for _, feature in top_features.iterrows():
                    feature_query = """
                    MATCH (m:Model {type: $model_type, target: $target})
                    CREATE (f:Feature {name: $feature_name, importance: $importance})
                    CREATE (m)-[r:HAS_IMPORTANT_FEATURE]->(f)
                    RETURN f
                    """
                    feature_params = {
                        'model_type': model_type,
                        'target': target,
                        'feature_name': feature['feature'],
                        'importance': float(feature['importance'])
                    }
                    tx.run(feature_query, feature_params)

    # Save analysis results to the session
    session.add_metadata({
        'num_compounds': len(pharma_data),
        'qsar_models': list(qsar_results.keys()),
        'dti_models': list(dti_results.keys()),
        'admet_models': list(admet_results.keys()),
        'qsar_plot_paths': qsar_plot_paths,
        'importance_plot_paths': importance_plot_paths
    })

    # Save the session
    session.save()

    print("Pharmaceutical data analysis workflow completed.")

    return {
        'pharma_data': pharma_data.head(),
        'qsar_results': {k: {'test_metrics': v['test_metrics']} for k, v in qsar_results.items()},
        'dti_results': {k: {'test_metrics': v['test_metrics']} for k, v in dti_results.items()},
        'admet_results': {k: {'test_metrics': v['test_metrics']} for k, v in admet_results.items()},
        'qsar_plot_paths': qsar_plot_paths,
        'importance_plot_paths': importance_plot_paths,
        'session_id': session.session_id
    }


def run_examples():
    """Run all examples."""
    print("Science Data Kit - Scientific Workflow Examples")
    print("==============================================")
    print("This module provides examples of real-world scientific data analysis workflows.")
    print("To run an example, call one of the following functions:")
    print("1. genomic_data_analysis_workflow(data_path)")
    print("2. clinical_trial_data_analysis_workflow(data_path)")
    print("3. environmental_monitoring_workflow(data_path)")
    print("4. preclinical_research_workflow(data_path)")
    print("5. materials_science_workflow(data_path)")
    print("6. pharmaceutical_data_analysis_workflow(data_path)")
    print("\nEach function takes a path to a data file and returns a dictionary with analysis results.")
    print("For example:")
    print("  results = genomic_data_analysis_workflow('path/to/genomic_data.csv')")
    print("  print(results['significant_genes'])")


if __name__ == "__main__":
    run_examples()
