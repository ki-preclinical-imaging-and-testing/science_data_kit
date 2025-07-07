"""
Terminology Standardization for Science Data Kit

This module provides standardized terminology for use across the application
to ensure consistent naming and labeling in the user interface.
"""

# Data-related terminology
DATA_TERMINOLOGY = {
    # Data sources
    "DATA_SOURCE": "Data Source",
    "FILE_UPLOAD": "File Upload",
    "DATABASE": "Database",
    "API": "API",
    "CLOUD_STORAGE": "Cloud Storage",
    
    # Data operations
    "IMPORT": "Import",
    "EXPORT": "Export",
    "LOAD": "Load",
    "SAVE": "Save",
    "DOWNLOAD": "Download",
    "UPLOAD": "Upload",
    
    # Data formats
    "CSV": "CSV",
    "EXCEL": "Excel",
    "JSON": "JSON",
    "XML": "XML",
    "SQL": "SQL",
    
    # Data structures
    "DATASET": "Dataset",
    "TABLE": "Table",
    "DATAFRAME": "DataFrame",
    "ROW": "Row",
    "COLUMN": "Column",
    "CELL": "Cell",
}

# Analysis-related terminology
ANALYSIS_TERMINOLOGY = {
    # Analysis types
    "STATISTICAL_ANALYSIS": "Statistical Analysis",
    "MACHINE_LEARNING": "Machine Learning",
    "DATA_MINING": "Data Mining",
    "EXPLORATORY_ANALYSIS": "Exploratory Analysis",
    "PREDICTIVE_ANALYSIS": "Predictive Analysis",
    
    # Statistical terms
    "MEAN": "Mean",
    "MEDIAN": "Median",
    "MODE": "Mode",
    "STANDARD_DEVIATION": "Standard Deviation",
    "VARIANCE": "Variance",
    "CORRELATION": "Correlation",
    "REGRESSION": "Regression",
    
    # Machine learning terms
    "MODEL": "Model",
    "TRAINING": "Training",
    "TESTING": "Testing",
    "VALIDATION": "Validation",
    "ACCURACY": "Accuracy",
    "PRECISION": "Precision",
    "RECALL": "Recall",
}

# Visualization-related terminology
VISUALIZATION_TERMINOLOGY = {
    # Chart types
    "BAR_CHART": "Bar Chart",
    "LINE_CHART": "Line Chart",
    "PIE_CHART": "Pie Chart",
    "SCATTER_PLOT": "Scatter Plot",
    "HISTOGRAM": "Histogram",
    "HEATMAP": "Heatmap",
    "BOX_PLOT": "Box Plot",
    
    # Chart elements
    "AXIS": "Axis",
    "LEGEND": "Legend",
    "TITLE": "Title",
    "LABEL": "Label",
    "TOOLTIP": "Tooltip",
    "GRID": "Grid",
    
    # Visualization actions
    "ZOOM": "Zoom",
    "PAN": "Pan",
    "FILTER": "Filter",
    "SORT": "Sort",
    "GROUP": "Group",
}

# UI element terminology
UI_TERMINOLOGY = {
    # Navigation elements
    "SIDEBAR": "Sidebar",
    "MENU": "Menu",
    "NAVIGATION": "Navigation",
    "BREADCRUMB": "Breadcrumb",
    "TAB": "Tab",
    "PAGE": "Page",
    
    # Interactive elements
    "BUTTON": "Button",
    "CHECKBOX": "Checkbox",
    "RADIO_BUTTON": "Radio Button",
    "DROPDOWN": "Dropdown",
    "SLIDER": "Slider",
    "TEXT_INPUT": "Text Input",
    "TEXT_AREA": "Text Area",
    
    # Feedback elements
    "ERROR": "Error",
    "WARNING": "Warning",
    "INFO": "Information",
    "SUCCESS": "Success",
    "LOADING": "Loading",
    
    # Layout elements
    "CONTAINER": "Container",
    "PANEL": "Panel",
    "CARD": "Card",
    "MODAL": "Modal",
    "DIALOG": "Dialog",
    "TOOLTIP": "Tooltip",
}

# Action terminology
ACTION_TERMINOLOGY = {
    # File actions
    "OPEN": "Open",
    "CLOSE": "Close",
    "CREATE": "Create",
    "DELETE": "Delete",
    "RENAME": "Rename",
    
    # Edit actions
    "EDIT": "Edit",
    "COPY": "Copy",
    "PASTE": "Paste",
    "CUT": "Cut",
    "UNDO": "Undo",
    "REDO": "Redo",
    
    # Data actions
    "FILTER": "Filter",
    "SORT": "Sort",
    "GROUP": "Group",
    "AGGREGATE": "Aggregate",
    "TRANSFORM": "Transform",
    
    # Application actions
    "LOGIN": "Login",
    "LOGOUT": "Logout",
    "REGISTER": "Register",
    "SETTINGS": "Settings",
    "HELP": "Help",
}

# Combine all terminology dictionaries for easy access
TERMINOLOGY = {
    **DATA_TERMINOLOGY,
    **ANALYSIS_TERMINOLOGY,
    **VISUALIZATION_TERMINOLOGY,
    **UI_TERMINOLOGY,
    **ACTION_TERMINOLOGY,
}

def get_term(key):
    """
    Get the standardized term for a given key.
    
    Args:
        key (str): The terminology key to look up
        
    Returns:
        str: The standardized term, or the key itself if not found
    """
    return TERMINOLOGY.get(key, key)

def get_all_terms():
    """
    Get all standardized terms.
    
    Returns:
        dict: A dictionary of all standardized terms
    """
    return TERMINOLOGY

def get_category_terms(category):
    """
    Get all terms for a specific category.
    
    Args:
        category (str): The category to get terms for (e.g., 'DATA', 'ANALYSIS')
        
    Returns:
        dict: A dictionary of terms for the specified category
    """
    if category == 'DATA':
        return DATA_TERMINOLOGY
    elif category == 'ANALYSIS':
        return ANALYSIS_TERMINOLOGY
    elif category == 'VISUALIZATION':
        return VISUALIZATION_TERMINOLOGY
    elif category == 'UI':
        return UI_TERMINOLOGY
    elif category == 'ACTION':
        return ACTION_TERMINOLOGY
    else:
        return {}