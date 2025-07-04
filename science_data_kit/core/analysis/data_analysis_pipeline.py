"""
# Data Analysis Pipeline Module for Science Data Kit

This module provides a flexible and extensible data analysis pipeline framework
that allows users to define, configure, and execute multi-step data analysis workflows.
It supports integration with external data sources and various analysis tools.

## Features
- Pipeline definition with multiple stages
- Support for various data sources (internal and external)
- Integration with pandas, NumPy, scikit-learn, and other analysis tools
- Configurable pipeline stages with parameters
- Pipeline execution with progress tracking
- Result caching and persistence
- Error handling and logging

## Usage
```python
from science_data_kit.core.analysis.data_analysis_pipeline import (
    Pipeline,
    DataSource,
    DataTransformation,
    DataAnalysis,
    DataVisualization,
    PipelineExecutor
)

# Create a pipeline
pipeline = Pipeline(name="My Analysis Pipeline")

# Add data source stage
pipeline.add_stage(DataSource(
    name="Neo4j Data",
    source_type="neo4j",
    query="MATCH (n:Person) RETURN n.name, n.age"
))

# Add transformation stage
pipeline.add_stage(DataTransformation(
    name="Age Grouping",
    transformation_type="pandas",
    transformation_func=lambda df: df.assign(
        age_group=pd.cut(df['n.age'], bins=[0, 18, 35, 50, 65, 100], 
                         labels=['0-18', '19-35', '36-50', '51-65', '65+'])
    )
))

# Add analysis stage
pipeline.add_stage(DataAnalysis(
    name="Age Statistics",
    analysis_type="pandas",
    analysis_func=lambda df: df.groupby('age_group').agg({'n.age': ['count', 'mean', 'std']})
))

# Add visualization stage
pipeline.add_stage(DataVisualization(
    name="Age Distribution",
    visualization_type="matplotlib",
    visualization_func=lambda df: df.groupby('age_group').size().plot(kind='bar')
))

# Execute the pipeline
executor = PipelineExecutor()
results = executor.execute(pipeline)

# Access results
age_stats = results.get_stage_result("Age Statistics")
age_plot = results.get_stage_result("Age Distribution")
```
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union, Callable, Type
import logging
import uuid
import os
import json
import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum

from ..db.db_manager import DBManager

# Configure logging
logger = logging.getLogger(__name__)

class PipelineStageType(Enum):
    """Enum for pipeline stage types."""
    DATA_SOURCE = "data_source"
    DATA_TRANSFORMATION = "data_transformation"
    DATA_ANALYSIS = "data_analysis"
    DATA_VISUALIZATION = "data_visualization"
    DATA_EXPORT = "data_export"
    CUSTOM = "custom"

class PipelineStage(ABC):
    """Abstract base class for pipeline stages."""
    
    def __init__(
        self, 
        name: str,
        stage_type: PipelineStageType,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a pipeline stage.
        
        Args:
            name: The name of the stage.
            stage_type: The type of the stage.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.stage_type = stage_type
        self.description = description
        self.enabled = enabled
        self.parameters = parameters or {}
        self.input_data = None
        self.output_data = None
        self.execution_time = None
        self.status = "not_started"
        self.error = None
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the stage.
        
        Args:
            input_data: The input data for the stage.
            
        Returns:
            The output data from the stage.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        return {
            "id": self.id,
            "name": self.name,
            "stage_type": self.stage_type.value,
            "description": self.description,
            "enabled": self.enabled,
            "parameters": self.parameters,
            "status": self.status,
            "execution_time": self.execution_time,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineStage':
        """
        Create a stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A pipeline stage.
        """
        stage_type = PipelineStageType(data["stage_type"])
        
        if stage_type == PipelineStageType.DATA_SOURCE:
            return DataSource.from_dict(data)
        elif stage_type == PipelineStageType.DATA_TRANSFORMATION:
            return DataTransformation.from_dict(data)
        elif stage_type == PipelineStageType.DATA_ANALYSIS:
            return DataAnalysis.from_dict(data)
        elif stage_type == PipelineStageType.DATA_VISUALIZATION:
            return DataVisualization.from_dict(data)
        elif stage_type == PipelineStageType.DATA_EXPORT:
            return DataExport.from_dict(data)
        elif stage_type == PipelineStageType.CUSTOM:
            return CustomStage.from_dict(data)
        else:
            raise ValueError(f"Unknown stage type: {stage_type}")

class DataSource(PipelineStage):
    """Pipeline stage for data sources."""
    
    def __init__(
        self,
        name: str,
        source_type: str,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
        connection_name: Optional[str] = None,
        file_path: Optional[str] = None,
        custom_source_func: Optional[Callable] = None
    ):
        """
        Initialize a data source stage.
        
        Args:
            name: The name of the stage.
            source_type: The type of data source (neo4j, pandas, numpy, csv, excel, json, custom).
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
            query: A query to execute (for database sources).
            connection_name: The name of the database connection to use.
            file_path: The path to a file to load (for file sources).
            custom_source_func: A custom function to use for loading data.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.DATA_SOURCE,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.source_type = source_type
        self.query = query
        self.connection_name = connection_name
        self.file_path = file_path
        self.custom_source_func = custom_source_func
    
    def execute(self, input_data: Any = None) -> Any:
        """
        Execute the data source stage.
        
        Args:
            input_data: Not used for data source stages.
            
        Returns:
            The loaded data.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        
        try:
            if self.source_type == "neo4j":
                if not self.query:
                    raise ValueError("Query is required for Neo4j data source")
                
                db_manager = DBManager()
                success, results = db_manager.query(self.query, {}, self.connection_name)
                
                if success:
                    from .pandas_integration import query_to_dataframe
                    self.output_data = query_to_dataframe(results)
                else:
                    raise ValueError(f"Query failed: {results}")
            
            elif self.source_type == "pandas_csv":
                if not self.file_path:
                    raise ValueError("File path is required for CSV data source")
                
                self.output_data = pd.read_csv(self.file_path, **self.parameters)
            
            elif self.source_type == "pandas_excel":
                if not self.file_path:
                    raise ValueError("File path is required for Excel data source")
                
                self.output_data = pd.read_excel(self.file_path, **self.parameters)
            
            elif self.source_type == "pandas_json":
                if not self.file_path:
                    raise ValueError("File path is required for JSON data source")
                
                self.output_data = pd.read_json(self.file_path, **self.parameters)
            
            elif self.source_type == "numpy":
                if not self.file_path:
                    raise ValueError("File path is required for NumPy data source")
                
                from .numpy_integration import load_array
                self.output_data = load_array(self.file_path, **self.parameters)
            
            elif self.source_type == "custom":
                if not self.custom_source_func:
                    raise ValueError("Custom source function is required for custom data source")
                
                self.output_data = self.custom_source_func(**self.parameters)
            
            else:
                raise ValueError(f"Unsupported source type: {self.source_type}")
            
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing data source stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "source_type": self.source_type,
            "query": self.query,
            "connection_name": self.connection_name,
            "file_path": self.file_path,
            "has_custom_func": self.custom_source_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataSource':
        """
        Create a data source stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A data source stage.
        """
        return cls(
            name=data["name"],
            source_type=data["source_type"],
            description=data["description"],
            enabled=data["enabled"],
            parameters=data["parameters"],
            query=data.get("query"),
            connection_name=data.get("connection_name"),
            file_path=data.get("file_path"),
            custom_source_func=None  # Custom functions cannot be serialized
        )

class DataTransformation(PipelineStage):
    """Pipeline stage for data transformations."""
    
    def __init__(
        self,
        name: str,
        transformation_type: str,
        transformation_func: Optional[Callable] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a data transformation stage.
        
        Args:
            name: The name of the stage.
            transformation_type: The type of transformation (pandas, numpy, sklearn, custom).
            transformation_func: A function to apply to the data.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.DATA_TRANSFORMATION,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.transformation_type = transformation_type
        self.transformation_func = transformation_func
    
    def execute(self, input_data: Any) -> Any:
        """
        Execute the data transformation stage.
        
        Args:
            input_data: The input data to transform.
            
        Returns:
            The transformed data.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        self.input_data = input_data
        
        try:
            if self.transformation_func is not None:
                self.output_data = self.transformation_func(input_data, **self.parameters)
            else:
                # Apply default transformations based on type
                if self.transformation_type == "pandas":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for pandas transformation")
                    
                    # Apply pandas transformations based on parameters
                    df = input_data.copy()
                    
                    if "filter" in self.parameters:
                        df = df.query(self.parameters["filter"])
                    
                    if "select_columns" in self.parameters:
                        df = df[self.parameters["select_columns"]]
                    
                    if "rename_columns" in self.parameters:
                        df = df.rename(columns=self.parameters["rename_columns"])
                    
                    if "sort_by" in self.parameters:
                        ascending = self.parameters.get("ascending", True)
                        df = df.sort_values(by=self.parameters["sort_by"], ascending=ascending)
                    
                    if "group_by" in self.parameters:
                        agg_funcs = self.parameters.get("aggregations", {})
                        df = df.groupby(self.parameters["group_by"]).agg(agg_funcs)
                    
                    self.output_data = df
                
                elif self.transformation_type == "numpy":
                    from .numpy_integration import apply_function
                    
                    if "function" not in self.parameters:
                        raise ValueError("Function parameter is required for NumPy transformation")
                    
                    func_name = self.parameters["function"]
                    axis = self.parameters.get("axis")
                    
                    if func_name == "reshape":
                        if "shape" not in self.parameters:
                            raise ValueError("Shape parameter is required for reshape transformation")
                        
                        from .numpy_integration import reshape_array
                        self.output_data = reshape_array(input_data, self.parameters["shape"])
                    
                    elif func_name == "concatenate":
                        if "arrays" not in self.parameters:
                            raise ValueError("Arrays parameter is required for concatenate transformation")
                        
                        from .numpy_integration import concatenate_arrays
                        self.output_data = concatenate_arrays([input_data] + self.parameters["arrays"], axis=axis)
                    
                    elif func_name == "split":
                        if "indices_or_sections" not in self.parameters:
                            raise ValueError("Indices or sections parameter is required for split transformation")
                        
                        from .numpy_integration import split_array
                        self.output_data = split_array(input_data, self.parameters["indices_or_sections"], axis=axis)
                    
                    else:
                        # Use apply_function for other functions
                        import numpy as np
                        func = getattr(np, func_name)
                        self.output_data = apply_function(input_data, func, axis=axis)
                
                elif self.transformation_type == "sklearn":
                    from .sklearn_integration import prepare_data
                    
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for sklearn transformation")
                    
                    if "target_column" not in self.parameters:
                        raise ValueError("Target column parameter is required for sklearn transformation")
                    
                    feature_columns = self.parameters.get("feature_columns")
                    test_size = self.parameters.get("test_size", 0.2)
                    random_state = self.parameters.get("random_state", 42)
                    stratify = self.parameters.get("stratify", False)
                    
                    self.output_data = prepare_data(
                        input_data,
                        target_column=self.parameters["target_column"],
                        feature_columns=feature_columns,
                        test_size=test_size,
                        random_state=random_state,
                        stratify=stratify
                    )
                
                else:
                    raise ValueError(f"Unsupported transformation type: {self.transformation_type}")
            
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing data transformation stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "transformation_type": self.transformation_type,
            "has_transformation_func": self.transformation_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataTransformation':
        """
        Create a data transformation stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A data transformation stage.
        """
        return cls(
            name=data["name"],
            transformation_type=data["transformation_type"],
            transformation_func=None,  # Functions cannot be serialized
            description=data["description"],
            enabled=data["enabled"],
            parameters=data["parameters"]
        )

class DataAnalysis(PipelineStage):
    """Pipeline stage for data analysis."""
    
    def __init__(
        self,
        name: str,
        analysis_type: str,
        analysis_func: Optional[Callable] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a data analysis stage.
        
        Args:
            name: The name of the stage.
            analysis_type: The type of analysis (pandas, numpy, sklearn, custom).
            analysis_func: A function to apply to the data.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.DATA_ANALYSIS,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.analysis_type = analysis_type
        self.analysis_func = analysis_func
    
    def execute(self, input_data: Any) -> Any:
        """
        Execute the data analysis stage.
        
        Args:
            input_data: The input data to analyze.
            
        Returns:
            The analysis results.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        self.input_data = input_data
        
        try:
            if self.analysis_func is not None:
                self.output_data = self.analysis_func(input_data, **self.parameters)
            else:
                # Apply default analyses based on type
                if self.analysis_type == "pandas":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for pandas analysis")
                    
                    from .pandas_integration import analyze_dataframe
                    self.output_data = analyze_dataframe(input_data)
                
                elif self.analysis_type == "numpy":
                    from .numpy_integration import calculate_statistics
                    
                    axis = self.parameters.get("axis")
                    self.output_data = calculate_statistics(input_data, axis=axis)
                
                elif self.analysis_type == "sklearn":
                    from .sklearn_integration import train_model, evaluate_model
                    
                    if not isinstance(input_data, tuple) or len(input_data) != 4:
                        raise ValueError("Input data must be a tuple of (X_train, X_test, y_train, y_test) for sklearn analysis")
                    
                    X_train, X_test, y_train, y_test = input_data
                    
                    model_type = self.parameters.get("model_type", "random_forest")
                    model_params = self.parameters.get("model_params", {})
                    
                    model = train_model(X_train, y_train, model_type=model_type, model_params=model_params)
                    
                    metrics = self.parameters.get("metrics")
                    is_classifier = self.parameters.get("is_classifier")
                    
                    evaluation = evaluate_model(model, X_test, y_test, metrics=metrics, is_classifier=is_classifier)
                    
                    self.output_data = {
                        "model": model,
                        "evaluation": evaluation
                    }
                
                elif self.analysis_type == "sklearn_cross_validation":
                    from .sklearn_integration import cross_validate
                    
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for sklearn cross-validation")
                    
                    if "target_column" not in self.parameters:
                        raise ValueError("Target column parameter is required for sklearn cross-validation")
                    
                    feature_columns = self.parameters.get("feature_columns")
                    if feature_columns is None:
                        feature_columns = [col for col in input_data.columns if col != self.parameters["target_column"]]
                    
                    X = input_data[feature_columns].values
                    y = input_data[self.parameters["target_column"]].values
                    
                    model_type = self.parameters.get("model_type", "random_forest")
                    model_params = self.parameters.get("model_params", {})
                    cv = self.parameters.get("cv", 5)
                    metrics = self.parameters.get("metrics")
                    is_classifier = self.parameters.get("is_classifier")
                    
                    self.output_data = cross_validate(
                        X, y,
                        model_type=model_type,
                        model_params=model_params,
                        cv=cv,
                        metrics=metrics,
                        is_classifier=is_classifier
                    )
                
                else:
                    raise ValueError(f"Unsupported analysis type: {self.analysis_type}")
            
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing data analysis stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "analysis_type": self.analysis_type,
            "has_analysis_func": self.analysis_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataAnalysis':
        """
        Create a data analysis stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A data analysis stage.
        """
        return cls(
            name=data["name"],
            analysis_type=data["analysis_type"],
            analysis_func=None,  # Functions cannot be serialized
            description=data["description"],
            enabled=data["enabled"],
            parameters=data["parameters"]
        )

class DataVisualization(PipelineStage):
    """Pipeline stage for data visualization."""
    
    def __init__(
        self,
        name: str,
        visualization_type: str,
        visualization_func: Optional[Callable] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a data visualization stage.
        
        Args:
            name: The name of the stage.
            visualization_type: The type of visualization (matplotlib, plotly, d3, custom).
            visualization_func: A function to apply to the data.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.DATA_VISUALIZATION,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.visualization_type = visualization_type
        self.visualization_func = visualization_func
    
    def execute(self, input_data: Any) -> Any:
        """
        Execute the data visualization stage.
        
        Args:
            input_data: The input data to visualize.
            
        Returns:
            The visualization result.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        self.input_data = input_data
        
        try:
            if self.visualization_func is not None:
                self.output_data = self.visualization_func(input_data, **self.parameters)
            else:
                # Apply default visualizations based on type
                if self.visualization_type == "matplotlib":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for matplotlib visualization")
                    
                    from .pandas_integration import visualize_dataframe
                    
                    plot_type = self.parameters.get("plot_type", "bar")
                    x = self.parameters.get("x")
                    y = self.parameters.get("y")
                    
                    self.output_data = visualize_dataframe(input_data, plot_type=plot_type, x=x, y=y, **self.parameters)
                
                elif self.visualization_type == "plotly":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for plotly visualization")
                    
                    try:
                        import plotly.express as px
                    except ImportError:
                        raise ImportError("Plotly is not installed. Please install it with 'pip install plotly'.")
                    
                    plot_type = self.parameters.get("plot_type", "bar")
                    x = self.parameters.get("x")
                    y = self.parameters.get("y")
                    
                    if plot_type == "bar":
                        if x and y:
                            self.output_data = px.bar(input_data, x=x, y=y, **self.parameters)
                        else:
                            self.output_data = px.bar(input_data, **self.parameters)
                    elif plot_type == "line":
                        if x and y:
                            self.output_data = px.line(input_data, x=x, y=y, **self.parameters)
                        else:
                            self.output_data = px.line(input_data, **self.parameters)
                    elif plot_type == "scatter":
                        if x and y:
                            self.output_data = px.scatter(input_data, x=x, y=y, **self.parameters)
                        else:
                            raise ValueError("Scatter plot requires x and y parameters")
                    elif plot_type == "histogram":
                        if x:
                            self.output_data = px.histogram(input_data, x=x, **self.parameters)
                        else:
                            self.output_data = px.histogram(input_data, **self.parameters)
                    elif plot_type == "box":
                        if x:
                            self.output_data = px.box(input_data, x=x, **self.parameters)
                        else:
                            self.output_data = px.box(input_data, **self.parameters)
                    else:
                        raise ValueError(f"Unsupported plot type: {plot_type}")
                
                elif self.visualization_type == "d3":
                    # For D3.js, we prepare the data in a format suitable for D3
                    # The actual visualization would happen in the frontend
                    if isinstance(input_data, pd.DataFrame):
                        self.output_data = {
                            "data": input_data.to_dict(orient="records"),
                            "visualization_type": self.parameters.get("d3_chart_type", "bar"),
                            "options": self.parameters.get("d3_options", {})
                        }
                    else:
                        self.output_data = {
                            "data": input_data,
                            "visualization_type": self.parameters.get("d3_chart_type", "bar"),
                            "options": self.parameters.get("d3_options", {})
                        }
                
                else:
                    raise ValueError(f"Unsupported visualization type: {self.visualization_type}")
            
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing data visualization stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "visualization_type": self.visualization_type,
            "has_visualization_func": self.visualization_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataVisualization':
        """
        Create a data visualization stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A data visualization stage.
        """
        return cls(
            name=data["name"],
            visualization_type=data["visualization_type"],
            visualization_func=None,  # Functions cannot be serialized
            description=data["description"],
            enabled=data["enabled"],
            parameters=data["parameters"]
        )

class DataExport(PipelineStage):
    """Pipeline stage for data export."""
    
    def __init__(
        self,
        name: str,
        export_type: str,
        file_path: Optional[str] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None,
        custom_export_func: Optional[Callable] = None
    ):
        """
        Initialize a data export stage.
        
        Args:
            name: The name of the stage.
            export_type: The type of export (csv, excel, json, numpy, neo4j, custom).
            file_path: The path to save the data to.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
            custom_export_func: A custom function to use for exporting data.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.DATA_EXPORT,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.export_type = export_type
        self.file_path = file_path
        self.custom_export_func = custom_export_func
    
    def execute(self, input_data: Any) -> Any:
        """
        Execute the data export stage.
        
        Args:
            input_data: The input data to export.
            
        Returns:
            Information about the export operation.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        self.input_data = input_data
        
        try:
            if self.custom_export_func is not None:
                self.output_data = self.custom_export_func(input_data, **self.parameters)
            else:
                # Apply default export based on type
                if self.export_type == "csv":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for CSV export")
                    
                    if not self.file_path:
                        raise ValueError("File path is required for CSV export")
                    
                    from .pandas_integration import save_dataframe_to_csv
                    success, message = save_dataframe_to_csv(input_data, self.file_path)
                    
                    self.output_data = {
                        "success": success,
                        "message": message,
                        "file_path": self.file_path
                    }
                
                elif self.export_type == "excel":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for Excel export")
                    
                    if not self.file_path:
                        raise ValueError("File path is required for Excel export")
                    
                    from .pandas_integration import save_dataframe_to_excel
                    success, message = save_dataframe_to_excel(input_data, self.file_path)
                    
                    self.output_data = {
                        "success": success,
                        "message": message,
                        "file_path": self.file_path
                    }
                
                elif self.export_type == "json":
                    if not self.file_path:
                        raise ValueError("File path is required for JSON export")
                    
                    if isinstance(input_data, pd.DataFrame):
                        # Convert DataFrame to JSON
                        orient = self.parameters.get("orient", "records")
                        input_data.to_json(self.file_path, orient=orient)
                        success, message = True, f"DataFrame saved to {self.file_path}"
                    else:
                        # Convert other data to JSON
                        with open(self.file_path, 'w') as f:
                            json.dump(input_data, f)
                        success, message = True, f"Data saved to {self.file_path}"
                    
                    self.output_data = {
                        "success": success,
                        "message": message,
                        "file_path": self.file_path
                    }
                
                elif self.export_type == "numpy":
                    if not isinstance(input_data, np.ndarray):
                        raise ValueError("Input data must be a NumPy array for NumPy export")
                    
                    if not self.file_path:
                        raise ValueError("File path is required for NumPy export")
                    
                    from .numpy_integration import save_array
                    format = self.parameters.get("format", "npy")
                    file_path = save_array(input_data, self.file_path, format=format)
                    
                    self.output_data = {
                        "success": True,
                        "message": f"Array saved to {file_path}",
                        "file_path": file_path
                    }
                
                elif self.export_type == "neo4j":
                    if not isinstance(input_data, pd.DataFrame):
                        raise ValueError("Input data must be a pandas DataFrame for Neo4j export")
                    
                    from .pandas_integration import dataframe_to_neo4j
                    
                    node_label = self.parameters.get("node_label", "Node")
                    id_column = self.parameters.get("id_column")
                    
                    nodes, relationships = dataframe_to_neo4j(input_data, node_label=node_label, id_column=id_column)
                    
                    # Create nodes in Neo4j
                    db_manager = DBManager()
                    
                    # Create nodes
                    for node in nodes:
                        query = f"""
                        CREATE (n:{node['labels'][0]} {{id: $id}})
                        SET n += $properties
                        """
                        
                        params = {
                            "id": node["id"],
                            "properties": node["properties"]
                        }
                        
                        success, result = db_manager.query(query, params, self.parameters.get("connection_name"))
                        
                        if not success:
                            raise ValueError(f"Error creating node: {result}")
                    
                    self.output_data = {
                        "success": True,
                        "message": f"Exported {len(nodes)} nodes to Neo4j",
                        "nodes_created": len(nodes),
                        "relationships_created": len(relationships)
                    }
                
                else:
                    raise ValueError(f"Unsupported export type: {self.export_type}")
            
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing data export stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "export_type": self.export_type,
            "file_path": self.file_path,
            "has_custom_func": self.custom_export_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataExport':
        """
        Create a data export stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A data export stage.
        """
        return cls(
            name=data["name"],
            export_type=data["export_type"],
            file_path=data.get("file_path"),
            description=data["description"],
            enabled=data["enabled"],
            parameters=data["parameters"],
            custom_export_func=None  # Functions cannot be serialized
        )

class CustomStage(PipelineStage):
    """Custom pipeline stage for user-defined operations."""
    
    def __init__(
        self,
        name: str,
        execute_func: Callable,
        description: Optional[str] = None,
        enabled: bool = True,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a custom stage.
        
        Args:
            name: The name of the stage.
            execute_func: A function to execute for this stage.
            description: A description of the stage.
            enabled: Whether the stage is enabled.
            parameters: Additional parameters for the stage.
        """
        super().__init__(
            name=name,
            stage_type=PipelineStageType.CUSTOM,
            description=description,
            enabled=enabled,
            parameters=parameters
        )
        self.execute_func = execute_func
    
    def execute(self, input_data: Any) -> Any:
        """
        Execute the custom stage.
        
        Args:
            input_data: The input data for the stage.
            
        Returns:
            The output data from the stage.
        """
        start_time = datetime.datetime.now()
        self.status = "running"
        self.input_data = input_data
        
        try:
            self.output_data = self.execute_func(input_data, **self.parameters)
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Error executing custom stage '{self.name}': {str(e)}")
            raise
        finally:
            self.execution_time = (datetime.datetime.now() - start_time).total_seconds()
        
        return self.output_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the stage to a dictionary.
        
        Returns:
            A dictionary representation of the stage.
        """
        data = super().to_dict()
        data.update({
            "has_execute_func": self.execute_func is not None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomStage':
        """
        Create a custom stage from a dictionary.
        
        Args:
            data: A dictionary representation of the stage.
            
        Returns:
            A custom stage.
        """
        # Custom stages cannot be fully serialized because they require an execute_func
        raise ValueError("Custom stages cannot be created from a dictionary without an execute_func")

class Pipeline:
    """A data analysis pipeline consisting of multiple stages."""
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        stages: Optional[List[PipelineStage]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a pipeline.
        
        Args:
            name: The name of the pipeline.
            description: A description of the pipeline.
            stages: A list of pipeline stages.
            parameters: Additional parameters for the pipeline.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.stages = stages or []
        self.parameters = parameters or {}
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.status = "not_started"
        self.execution_time = None
        self.error = None
    
    def add_stage(self, stage: PipelineStage) -> None:
        """
        Add a stage to the pipeline.
        
        Args:
            stage: The stage to add.
        """
        self.stages.append(stage)
        self.updated_at = datetime.datetime.now()
    
    def remove_stage(self, stage_id: str) -> bool:
        """
        Remove a stage from the pipeline.
        
        Args:
            stage_id: The ID of the stage to remove.
            
        Returns:
            True if the stage was removed, False otherwise.
        """
        for i, stage in enumerate(self.stages):
            if stage.id == stage_id:
                self.stages.pop(i)
                self.updated_at = datetime.datetime.now()
                return True
        return False
    
    def get_stage(self, stage_id: str) -> Optional[PipelineStage]:
        """
        Get a stage by ID.
        
        Args:
            stage_id: The ID of the stage to get.
            
        Returns:
            The stage with the given ID, or None if not found.
        """
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pipeline to a dictionary.
        
        Returns:
            A dictionary representation of the pipeline.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stages": [stage.to_dict() for stage in self.stages],
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "execution_time": self.execution_time,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipeline':
        """
        Create a pipeline from a dictionary.
        
        Args:
            data: A dictionary representation of the pipeline.
            
        Returns:
            A pipeline.
        """
        pipeline = cls(
            name=data["name"],
            description=data["description"],
            parameters=data["parameters"]
        )
        
        pipeline.id = data["id"]
        pipeline.created_at = datetime.datetime.fromisoformat(data["created_at"])
        pipeline.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        pipeline.status = data["status"]
        pipeline.execution_time = data["execution_time"]
        pipeline.error = data["error"]
        
        # Create stages
        for stage_data in data["stages"]:
            try:
                stage = PipelineStage.from_dict(stage_data)
                pipeline.stages.append(stage)
            except ValueError as e:
                logger.warning(f"Could not create stage from dictionary: {str(e)}")
        
        return pipeline
    
    def save(self, file_path: str) -> Tuple[bool, str]:
        """
        Save the pipeline to a file.
        
        Args:
            file_path: The path to save the pipeline to.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save the pipeline
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            return True, f"Pipeline saved to {file_path}"
        except Exception as e:
            logger.error(f"Error saving pipeline: {str(e)}")
            return False, f"Error saving pipeline: {str(e)}"
    
    @classmethod
    def load(cls, file_path: str) -> Tuple[bool, Union['Pipeline', str]]:
        """
        Load a pipeline from a file.
        
        Args:
            file_path: The path to the pipeline file.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - The loaded pipeline or an error message.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return True, cls.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading pipeline: {str(e)}")
            return False, f"Error loading pipeline: {str(e)}"

class PipelineResults:
    """Results from executing a pipeline."""
    
    def __init__(self, pipeline: Pipeline):
        """
        Initialize pipeline results.
        
        Args:
            pipeline: The pipeline that was executed.
        """
        self.pipeline = pipeline
        self.stage_results = {}
        self.execution_time = None
        self.completed_at = None
        self.status = "not_started"
        self.error = None
    
    def set_stage_result(self, stage_id: str, result: Any) -> None:
        """
        Set the result for a stage.
        
        Args:
            stage_id: The ID of the stage.
            result: The result of the stage.
        """
        self.stage_results[stage_id] = result
    
    def get_stage_result(self, stage_name_or_id: str) -> Any:
        """
        Get the result for a stage by name or ID.
        
        Args:
            stage_name_or_id: The name or ID of the stage.
            
        Returns:
            The result of the stage, or None if not found.
        """
        # Try to get by ID first
        if stage_name_or_id in self.stage_results:
            return self.stage_results[stage_name_or_id]
        
        # Try to get by name
        for stage in self.pipeline.stages:
            if stage.name == stage_name_or_id and stage.id in self.stage_results:
                return self.stage_results[stage.id]
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the results to a dictionary.
        
        Returns:
            A dictionary representation of the results.
        """
        return {
            "pipeline": self.pipeline.to_dict(),
            "stage_results": {k: str(v) for k, v in self.stage_results.items()},  # Convert results to strings
            "execution_time": self.execution_time,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "error": self.error
        }

class PipelineExecutor:
    """Executor for running pipelines."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize a pipeline executor.
        
        Args:
            cache_dir: Directory to use for caching results.
        """
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def execute(self, pipeline: Pipeline) -> PipelineResults:
        """
        Execute a pipeline.
        
        Args:
            pipeline: The pipeline to execute.
            
        Returns:
            The results of the pipeline execution.
        """
        start_time = datetime.datetime.now()
        pipeline.status = "running"
        results = PipelineResults(pipeline)
        results.status = "running"
        
        try:
            # Execute each stage in sequence
            data = None
            
            for stage in pipeline.stages:
                if not stage.enabled:
                    logger.info(f"Skipping disabled stage: {stage.name}")
                    continue
                
                logger.info(f"Executing stage: {stage.name}")
                
                try:
                    # Execute the stage
                    result = stage.execute(data)
                    
                    # Store the result
                    results.set_stage_result(stage.id, result)
                    
                    # Use the result as input for the next stage
                    data = result
                except Exception as e:
                    stage.status = "failed"
                    stage.error = str(e)
                    pipeline.status = "failed"
                    pipeline.error = f"Stage '{stage.name}' failed: {str(e)}"
                    results.status = "failed"
                    results.error = pipeline.error
                    logger.error(f"Error executing stage '{stage.name}': {str(e)}")
                    raise
            
            pipeline.status = "completed"
            results.status = "completed"
        except Exception as e:
            if pipeline.status != "failed":
                pipeline.status = "failed"
                pipeline.error = str(e)
                results.status = "failed"
                results.error = str(e)
            logger.error(f"Error executing pipeline '{pipeline.name}': {str(e)}")
        finally:
            pipeline.execution_time = (datetime.datetime.now() - start_time).total_seconds()
            results.execution_time = pipeline.execution_time
            results.completed_at = datetime.datetime.now()
        
        return results
    
    def execute_async(self, pipeline: Pipeline) -> str:
        """
        Execute a pipeline asynchronously.
        
        Args:
            pipeline: The pipeline to execute.
            
        Returns:
            A job ID for tracking the execution.
        """
        # This is a placeholder for future implementation
        # In a real implementation, this would start a background task
        # and return a job ID for tracking the execution
        job_id = str(uuid.uuid4())
        
        # For now, just execute the pipeline synchronously
        results = self.execute(pipeline)
        
        return job_id
    
    def get_execution_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an asynchronous pipeline execution.
        
        Args:
            job_id: The job ID returned by execute_async.
            
        Returns:
            A dictionary containing the status of the execution.
        """
        # This is a placeholder for future implementation
        # In a real implementation, this would check the status of the background task
        return {
            "job_id": job_id,
            "status": "not_implemented",
            "message": "Asynchronous execution is not yet implemented"
        }
"""