# Science Data Kit Component API Documentation

This document provides detailed API documentation for the UI components in the Science Data Kit. It is intended for developers who want to use, extend, or customize these components in their applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Common Patterns](#common-patterns)
3. [Progress Indicators](#progress-indicators)
4. [Breadcrumbs](#breadcrumbs)
5. [Error Display](#error-display)
6. [High Contrast Mode](#high-contrast-mode)
7. [Screen Reader Support](#screen-reader-support)
8. [Keyboard Navigation](#keyboard-navigation)
9. [Terminology Standardization](#terminology-standardization)
10. [Data Source Selectors](#data-source-selectors)
11. [Visualization Templates](#visualization-templates)

## Introduction

The Science Data Kit UI components are built on top of Streamlit and provide enhanced functionality for scientific data applications. These components follow consistent patterns and can be easily integrated into your Streamlit applications.

### Component Structure

Most components in the Science Data Kit follow a similar structure:

1. **Core Classes**: Implement the main functionality
2. **Utility Functions**: Provide simplified interfaces for common use cases
3. **Session State Integration**: Functions for persistent state across app reruns
4. **Styling Options**: Customization through style dictionaries

### Import Pattern

Components can be imported directly from the science_data_kit.ui.components module:

```python
from science_data_kit.ui.components.progress_indicators import create_progress_indicator
from science_data_kit.ui.components.breadcrumbs import create_breadcrumb_trail
from science_data_kit.ui.components.error_display import display_error
```

## Common Patterns

### Style Dictionaries

Most components accept style dictionaries for customization:

```python
container_style = {
    "padding": "1rem",
    "margin-bottom": "1.5rem",
    "background-color": "#f5f5f5",
    "border-radius": "8px"
}

create_progress_indicator(
    steps=steps,
    container_style=container_style
)
```

### Session State Integration

Components that need to maintain state across app reruns provide session state integration functions:

```python
# Add to session state
add_progress_to_session(steps, key="my_workflow_progress")

# Update in session state
update_progress_in_session(1, completed=True, current=False, key="my_workflow_progress")

# Render from session state
render_progress_from_session(key="my_workflow_progress")
```

## Progress Indicators

The Progress Indicators component provides standardized progress indicator components for multi-step workflows.

### ProgressIndicatorType Enum

```python
class ProgressIndicatorType(Enum):
    LINEAR = "linear"    # Simple horizontal progress bar
    CIRCULAR = "circular"  # Circular progress indicator
    STEP = "step"        # Numbered steps with labels
    DOT = "dot"          # Dots connected by lines
```

### ProgressStep Class

```python
class ProgressStep:
    def __init__(
        self, 
        label: str, 
        description: Optional[str] = None,
        completed: bool = False,
        current: bool = False,
        icon: Optional[str] = None,
        data: Optional[Any] = None
    ):
        # ...
```

**Parameters:**
- `label` (str): The display label for the step
- `description` (str, optional): A longer description of the step
- `completed` (bool): Whether this step has been completed
- `current` (bool): Whether this is the current active step
- `icon` (str, optional): Icon to display with the step
- `data` (Any, optional): Additional data associated with the step

### ProgressIndicator Class

```python
class ProgressIndicator:
    def __init__(
        self,
        indicator_type: ProgressIndicatorType = ProgressIndicatorType.LINEAR,
        container_style: Optional[Dict] = None,
        step_style: Optional[Dict] = None,
        completed_style: Optional[Dict] = None,
        current_style: Optional[Dict] = None,
        show_labels: bool = True,
        show_descriptions: bool = False,
        show_percentage: bool = True
    ):
        # ...
    
    def add_step(
        self, 
        label: str, 
        description: Optional[str] = None,
        completed: bool = False,
        current: bool = False,
        icon: Optional[str] = None,
        data: Optional[Any] = None
    ) -> None:
        # ...
    
    def update_step(
        self,
        index: int,
        completed: Optional[bool] = None,
        current: Optional[bool] = None
    ) -> None:
        # ...
    
    def clear(self) -> None:
        # ...
    
    def get_completion_percentage(self) -> float:
        # ...
    
    def render(self) -> None:
        # ...
```

**Constructor Parameters:**
- `indicator_type` (ProgressIndicatorType): The type of progress indicator to display
- `container_style` (Dict, optional): CSS styles for the progress indicator container
- `step_style` (Dict, optional): CSS styles for individual steps
- `completed_style` (Dict, optional): CSS styles for completed steps
- `current_style` (Dict, optional): CSS styles for the current step
- `show_labels` (bool): Whether to show step labels
- `show_descriptions` (bool): Whether to show step descriptions
- `show_percentage` (bool): Whether to show percentage completion

**Methods:**
- `add_step()`: Add a step to the progress indicator
- `update_step()`: Update the status of a step
- `clear()`: Clear all steps from the progress indicator
- `get_completion_percentage()`: Calculate the percentage of completed steps
- `render()`: Render the progress indicator in the Streamlit app

### Utility Functions

```python
def create_progress_indicator(
    steps: List[Dict[str, Union[str, bool, Any]]],
    indicator_type: Union[str, ProgressIndicatorType] = ProgressIndicatorType.LINEAR,
    container_style: Optional[Dict] = None,
    step_style: Optional[Dict] = None,
    completed_style: Optional[Dict] = None,
    current_style: Optional[Dict] = None,
    show_labels: bool = True,
    show_descriptions: bool = False,
    show_percentage: bool = True
) -> None:
    # ...

def add_progress_to_session(
    steps: List[Dict[str, Union[str, bool, Any]]],
    key: str = "progress_steps"
) -> None:
    # ...

def get_progress_from_session(key: str = "progress_steps") -> List[Dict]:
    # ...

def update_progress_in_session(
    step_index: int,
    completed: Optional[bool] = None,
    current: Optional[bool] = None,
    key: str = "progress_steps"
) -> None:
    # ...

def render_progress_from_session(
    key: str = "progress_steps",
    indicator_type: Union[str, ProgressIndicatorType] = ProgressIndicatorType.LINEAR,
    container_style: Optional[Dict] = None,
    step_style: Optional[Dict] = None,
    completed_style: Optional[Dict] = None,
    current_style: Optional[Dict] = None,
    show_labels: bool = True,
    show_descriptions: bool = False,
    show_percentage: bool = True
) -> None:
    # ...
```

### Usage Examples

#### Basic Usage

```python
from science_data_kit.ui.components.progress_indicators import create_progress_indicator, ProgressIndicatorType

# Define steps
steps = [
    {"label": "Step 1", "description": "First step", "completed": True, "current": False},
    {"label": "Step 2", "description": "Second step", "completed": False, "current": True},
    {"label": "Step 3", "description": "Third step", "completed": False, "current": False}
]

# Create and render a progress indicator
create_progress_indicator(
    steps=steps,
    indicator_type=ProgressIndicatorType.STEP,
    show_descriptions=True
)
```

#### With Session State

```python
from science_data_kit.ui.components.progress_indicators import (
    add_progress_to_session,
    update_progress_in_session,
    render_progress_from_session,
    ProgressIndicatorType
)

# Define steps
steps = [
    {"label": "Upload", "description": "Upload data", "completed": False, "current": True},
    {"label": "Process", "description": "Process data", "completed": False, "current": False},
    {"label": "Analyze", "description": "Analyze results", "completed": False, "current": False}
]

# Add to session state
add_progress_to_session(steps, key="workflow_progress")

# Later, update a step
if uploaded_file is not None:
    update_progress_in_session(0, completed=True, current=False, key="workflow_progress")
    update_progress_in_session(1, current=True, key="workflow_progress")

# Render from session state
render_progress_from_session(
    key="workflow_progress",
    indicator_type=ProgressIndicatorType.STEP,
    show_descriptions=True
)
```

## Breadcrumbs

The Breadcrumbs component provides a standardized breadcrumb navigation component for complex workflows.

### Breadcrumb Class

```python
class Breadcrumb:
    def __init__(
        self, 
        label: str, 
        url: Optional[str] = None, 
        callback: Optional[Callable] = None,
        active: bool = False,
        icon: Optional[str] = None
    ):
        # ...
```

**Parameters:**
- `label` (str): The display label for the breadcrumb
- `url` (str, optional): The URL or path for the breadcrumb
- `callback` (callable, optional): Function to call when the breadcrumb is clicked
- `active` (bool): Whether this breadcrumb represents the current page
- `icon` (str, optional): Icon to display with the breadcrumb

### BreadcrumbTrail Class

```python
class BreadcrumbTrail:
    def __init__(
        self,
        separator: str = ">",
        container_style: Optional[Dict] = None,
        breadcrumb_style: Optional[Dict] = None,
        active_style: Optional[Dict] = None
    ):
        # ...
    
    def add_breadcrumb(
        self, 
        label: str, 
        url: Optional[str] = None, 
        callback: Optional[Callable] = None,
        active: bool = False,
        icon: Optional[str] = None
    ) -> None:
        # ...
    
    def clear(self) -> None:
        # ...
    
    def render(self) -> None:
        # ...
```

**Constructor Parameters:**
- `separator` (str): The separator to display between breadcrumbs
- `container_style` (Dict, optional): CSS styles for the breadcrumb container
- `breadcrumb_style` (Dict, optional): CSS styles for individual breadcrumbs
- `active_style` (Dict, optional): CSS styles for the active breadcrumb

**Methods:**
- `add_breadcrumb()`: Add a breadcrumb to the trail
- `clear()`: Clear all breadcrumbs from the trail
- `render()`: Render the breadcrumb trail in the Streamlit app

### Utility Functions

```python
def create_breadcrumb_trail(
    paths: List[Dict[str, Union[str, bool, Callable, None]]],
    separator: str = ">",
    container_style: Optional[Dict] = None,
    breadcrumb_style: Optional[Dict] = None,
    active_style: Optional[Dict] = None
) -> None:
    # ...

def add_breadcrumbs_to_session(
    paths: List[Dict[str, Union[str, bool, Callable, None]]],
    key: str = "breadcrumbs"
) -> None:
    # ...

def get_breadcrumbs_from_session(key: str = "breadcrumbs") -> List[Dict]:
    # ...

def render_breadcrumbs_from_session(
    key: str = "breadcrumbs",
    separator: str = ">",
    container_style: Optional[Dict] = None,
    breadcrumb_style: Optional[Dict] = None,
    active_style: Optional[Dict] = None
) -> None:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.breadcrumbs import create_breadcrumb_trail

# Define breadcrumb paths
paths = [
    {"label": "Home", "url": "/"},
    {"label": "Data", "url": "/data"},
    {"label": "Analysis", "active": True}
]

# Create and render breadcrumb trail
create_breadcrumb_trail(paths)
```

## Error Display

The Error Display component provides standardized error messages and recovery options.

### ErrorDisplay Class

```python
class ErrorDisplay:
    def __init__(
        self,
        container_style: Optional[Dict] = None,
        error_style: Optional[Dict] = None,
        warning_style: Optional[Dict] = None,
        info_style: Optional[Dict] = None,
        success_style: Optional[Dict] = None
    ):
        # ...
    
    def display_error(
        self,
        message: str,
        error_type: str = "error",
        details: Optional[str] = None,
        recovery_options: Optional[List[Dict[str, Union[str, Callable]]]] = None,
        icon: Optional[str] = None,
        dismissible: bool = True
    ) -> None:
        # ...
```

**Constructor Parameters:**
- `container_style` (Dict, optional): CSS styles for the error container
- `error_style` (Dict, optional): CSS styles for error messages
- `warning_style` (Dict, optional): CSS styles for warning messages
- `info_style` (Dict, optional): CSS styles for info messages
- `success_style` (Dict, optional): CSS styles for success messages

**Methods:**
- `display_error()`: Display an error message with optional details and recovery options

### Utility Functions

```python
def display_error(
    message: str,
    error_type: str = "error",
    details: Optional[str] = None,
    recovery_options: Optional[List[Dict[str, Union[str, Callable]]]] = None,
    icon: Optional[str] = None,
    dismissible: bool = True,
    container_style: Optional[Dict] = None,
    error_style: Optional[Dict] = None,
    warning_style: Optional[Dict] = None,
    info_style: Optional[Dict] = None,
    success_style: Optional[Dict] = None
) -> None:
    # ...

def add_error_to_session(
    message: str,
    error_type: str = "error",
    details: Optional[str] = None,
    recovery_options: Optional[List[Dict[str, Union[str, Callable]]]] = None,
    icon: Optional[str] = None,
    dismissible: bool = True,
    key: str = "errors"
) -> None:
    # ...

def get_errors_from_session(key: str = "errors") -> List[Dict]:
    # ...

def display_errors_from_session(
    key: str = "errors",
    container_style: Optional[Dict] = None,
    error_style: Optional[Dict] = None,
    warning_style: Optional[Dict] = None,
    info_style: Optional[Dict] = None,
    success_style: Optional[Dict] = None
) -> None:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.error_display import display_error

# Display a simple error
display_error("Failed to load data")

# Display an error with details and recovery options
display_error(
    message="Database connection failed",
    error_type="error",
    details="Could not connect to the database server. The server might be down or the connection parameters might be incorrect.",
    recovery_options=[
        {"label": "Retry Connection", "callback": retry_connection},
        {"label": "Edit Connection Settings", "callback": edit_settings}
    ]
)
```

## High Contrast Mode

The High Contrast Mode component provides enhanced visibility for users with visual impairments.

### HighContrastMode Class

```python
class HighContrastMode:
    def __init__(
        self,
        dark_scheme: Optional[Dict[str, str]] = None,
        light_scheme: Optional[Dict[str, str]] = None
    ):
        # ...
    
    def apply_high_contrast(self, mode: str = "dark") -> None:
        # ...
    
    def get_color(self, color_key: str) -> str:
        # ...
```

**Constructor Parameters:**
- `dark_scheme` (Dict, optional): Custom dark high contrast color scheme
- `light_scheme` (Dict, optional): Custom light high contrast color scheme

**Methods:**
- `apply_high_contrast()`: Apply high contrast mode to the application
- `get_color()`: Get a color from the current color scheme

### Utility Functions

```python
def toggle_high_contrast_mode(mode: Optional[str] = None) -> None:
    # ...

def get_high_contrast_color(color_key: str) -> str:
    # ...

def is_high_contrast_enabled() -> bool:
    # ...

def apply_high_contrast_to_chart(fig, mode: Optional[str] = None) -> None:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.high_contrast import toggle_high_contrast_mode, get_high_contrast_color

# Add a toggle button
if st.button("Toggle High Contrast Mode"):
    toggle_high_contrast_mode()

# Use high contrast colors in custom elements
color = get_high_contrast_color("primary")
st.markdown(f"<div style='color: {color}'>High contrast text</div>", unsafe_allow_html=True)
```

## Screen Reader Support

The Screen Reader Support component enhances accessibility for users of screen readers and other assistive technologies.

### Utility Functions

```python
def add_screen_reader_text(text: str) -> None:
    # ...

def add_aria_label(element_id: str, label: str) -> None:
    # ...

def create_live_region(region_id: str, aria_live: str = "polite") -> None:
    # ...

def update_live_region(region_id: str, content: str) -> None:
    # ...

def add_skip_link(target_id: str, label: str = "Skip to main content") -> None:
    # ...

def make_table_accessible(table_html: str) -> str:
    # ...

def initialize_screen_reader_support() -> None:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.screen_reader import add_aria_label, create_live_region, update_live_region

# Initialize a live region for dynamic updates
create_live_region("status_region", "polite")

# Update the live region when something changes
if st.button("Process Data"):
    # Process data...
    update_live_region("status_region", "Data processing complete")
```

## Keyboard Navigation

The Keyboard Navigation component enhances accessibility by ensuring all functionality is available from a keyboard.

### KeyboardNavigation Class

```python
class KeyboardNavigation:
    def __init__(self):
        # ...
    
    def add_shortcut(self, key: str, action: Callable, description: str) -> None:
        # ...
    
    def remove_shortcut(self, key: str) -> None:
        # ...
    
    def enable(self) -> None:
        # ...
    
    def disable(self) -> None:
        # ...
    
    def show_help(self) -> None:
        # ...
```

**Methods:**
- `add_shortcut()`: Add a keyboard shortcut
- `remove_shortcut()`: Remove a keyboard shortcut
- `enable()`: Enable keyboard navigation
- `disable()`: Disable keyboard navigation
- `show_help()`: Show a help dialog with available shortcuts

### Utility Functions

```python
def initialize_keyboard_navigation() -> None:
    # ...

def add_keyboard_shortcut(key: str, action: Callable, description: str) -> None:
    # ...

def remove_keyboard_shortcut(key: str) -> None:
    # ...

def show_keyboard_shortcuts() -> None:
    # ...

def make_element_focusable(element_id: str, tab_index: int = 0) -> None:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.keyboard_navigation import initialize_keyboard_navigation, add_keyboard_shortcut

# Initialize keyboard navigation
initialize_keyboard_navigation()

# Add a custom shortcut
def save_data():
    # Save data logic
    st.success("Data saved")

add_keyboard_shortcut("ctrl+s", save_data, "Save data")
```

## Terminology Standardization

The Terminology Standardization component ensures consistent naming across the interface.

### Utility Functions

```python
def get_term(category: str, term_key: str, default: Optional[str] = None) -> str:
    # ...

def get_all_terms(category: Optional[str] = None) -> Dict[str, str]:
    # ...

def add_custom_term(category: str, term_key: str, term_value: str) -> None:
    # ...

def get_term_categories() -> List[str]:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.terminology import get_term

# Use standardized terminology
st.button(get_term("ACTION_TERMINOLOGY", "Save"))
st.header(get_term("DATA_TERMINOLOGY", "Dataset"))
```

## Data Source Selectors

The Data Source Selectors provide interfaces for connecting to various data sources.

### DataSourceSelector Class

```python
class DataSourceSelector:
    def __init__(self):
        # ...
    
    def render(self) -> None:
        # ...
    
    def get_selected_source(self) -> str:
        # ...
    
    def get_source_component(self) -> Any:
        # ...
```

### Specific Data Source Components

#### DropboxSelector

```python
class DropboxSelector:
    def __init__(self, api_key: Optional[str] = None):
        # ...
    
    def authenticate(self) -> bool:
        # ...
    
    def list_files(self, folder_path: str = "/") -> List[Dict]:
        # ...
    
    def select_file(self) -> Optional[str]:
        # ...
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        # ...
    
    def render(self) -> Optional[pd.DataFrame]:
        # ...
```

#### GoogleSheetsSelector

```python
class GoogleSheetsSelector:
    def __init__(self, credentials_path: Optional[str] = None):
        # ...
    
    def authenticate(self) -> bool:
        # ...
    
    def list_spreadsheets(self) -> List[Dict]:
        # ...
    
    def list_worksheets(self, spreadsheet_id: str) -> List[Dict]:
        # ...
    
    def get_worksheet_data(self, spreadsheet_id: str, worksheet_name: str) -> Optional[pd.DataFrame]:
        # ...
    
    def render(self) -> Optional[pd.DataFrame]:
        # ...
```

### Usage Example

```python
from science_data_kit.ui.components.data_source_selector import DataSourceSelector

# Create and render a data source selector
selector = DataSourceSelector()
selector.render()

# Get the selected data source
source_name = selector.get_selected_source()

# Get the source-specific component
source_component = selector.get_source_component()

# Use the component to get data
if source_name == "dropbox":
    data = source_component.download_file("/path/to/file.csv")
elif source_name == "google_sheets":
    data = source_component.get_worksheet_data(spreadsheet_id, worksheet_name)
```

## Visualization Templates

The Visualization Templates provide standardized chart creation and styling.

### VisualizationTemplate Class

```python
class VisualizationTemplate:
    def __init__(
        self,
        template_name: str,
        chart_type: str,
        default_options: Optional[Dict] = None
    ):
        # ...
    
    def apply(self, data: pd.DataFrame, options: Optional[Dict] = None) -> Any:
        # ...
    
    def render(self, data: pd.DataFrame, options: Optional[Dict] = None) -> None:
        # ...
```

### Utility Functions

```python
def get_available_templates() -> List[str]:
    # ...

def create_visualization(
    data: pd.DataFrame,
    template_name: str,
    options: Optional[Dict] = None
) -> None:
    # ...

def customize_template(
    template_name: str,
    custom_options: Dict
) -> str:
    # ...
```

### Usage Example

```python
from science_data_kit.ui.components.visualization_templates import create_visualization

# Create a visualization using a template
create_visualization(
    data=df,
    template_name="scatter_plot",
    options={
        "x_column": "temperature",
        "y_column": "sales",
        "color_column": "region",
        "title": "Temperature vs. Sales by Region"
    }
)
```

---

This API documentation will be regularly updated as components are added or modified. For the latest information, please refer to the inline documentation in the source code.